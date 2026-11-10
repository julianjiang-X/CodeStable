#!/usr/bin/env python3
"""Read-only progress snapshot: in progress, waiting, recently done, next.

Nothing is stored; the answer is derived from work directories (main checkout
and every linked worktree), branches and dirty trees, the worktree inbox,
undecided approval reports and the default branch history. No network and no
`git fetch`; `--prs` additionally asks `gh` for open PRs, and anything that
could not be checked is listed under `not_checked` instead of failing.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from codestable_common import (
    UNIT_ROOTS,
    default_branch,
    review_file_for,
    review_has_subagent_evidence,
    run_git,
    unit_completion_marker,
    worktree_map,
)

WORK_ROOTS = (*UNIT_ROOTS, "goals")
# Latest stage first: the first suffix found names the stage, its position the rank.
STAGES = {
    "features": (("-acceptance.md", "acceptance"), ("-ff-note.md", "fast-forward"),
                 ("-implementation-review.md", "implementation review"), ("-checklist.yaml", "implementation"),
                 ("-design.md", "design"), ("-brainstorm.md", "brainstorm")),
    "issues": (("-fix-note.md", "fix"), ("-implementation-review.md", "fix review"),
               ("-analysis.md", "analysis"), ("-report.md", "report")),
    "refactors": (("-apply-notes.md", "apply"), ("-refactor-note.md", "refactor note"),
                  ("-implementation-review.md", "implementation review"), ("-checklist.yaml", "implementation"),
                  ("-refactor-design.md", "design"), ("-scan.md", "scan")),
    "goals": (("functional-acceptance.md", "functional acceptance"), ("goal.md", "iterating")),
}
CLOSING = {"implementation-done": "implementation done, review/closure pending",
           "canceled": "canceled, deletion pending", "complete": "goal complete, deletion pending"}
OPEN_INBOX = {"ready-to-merge", "stale-report", "blocked"}


def load_inbox_tool():
    path = Path(__file__).resolve().with_name("codestable-worktree-inbox.py")
    spec = importlib.util.spec_from_file_location("codestable_worktree_inbox_for_status", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def front_value(path: Path, key: str) -> str:
    try:
        match = re.search(rf"^{key}:\s*['\"]?([^'\"\n]+)", path.read_text(encoding="utf-8"), re.MULTILINE)
    except (OSError, UnicodeDecodeError):
        return ""
    return match.group(1).strip() if match else ""


def git_lines(root: Path | str, *args: str) -> list[str]:
    result = run_git(Path(root), *args)
    return [line for line in result.stdout.splitlines() if line] if result.returncode == 0 else []


def changed_units(wt: Path, base: str | None) -> set[str] | None:
    """Units this worktree changed since it forked from the default branch (committed, uncommitted, untracked).

    None when the comparison cannot be made (no default branch, no merge-base): the caller then
    treats every unit as current work rather than hide it.
    """
    fork = git_lines(wt, "merge-base", base, "HEAD") if base else []
    if not fork:
        return None
    paths = git_lines(wt, "diff", "--name-only", fork[0], "--", ".codestable")
    paths += git_lines(wt, "ls-files", "--others", "--exclude-standard", "--", ".codestable")
    return {"/".join(p.split("/")[:3]) for p in paths if p.startswith(".codestable/")}


def checklist_progress(unit: Path) -> tuple[int, str]:
    """(steps done, first pending step) over the unit's checklists."""
    done, step = 0, ""
    for checklist in sorted(unit.glob("*-checklist.yaml")):
        text = checklist.read_text(encoding="utf-8", errors="replace")
        steps = re.search(r"(?ms)^steps:\s*\n(.*?)(?=^\S|\Z)", text)
        for block in re.split(r"(?m)^\s*-\s+", steps.group(1))[1:] if steps else []:
            if re.search(r"^\s*status:\s*pending", block, re.MULTILINE):
                action = re.match(r"(?:action|id|name):\s*[\"']?(.+?)[\"']?\s*$", block.splitlines()[0])
                step = step or (action.group(1) if action else block.splitlines()[0])[:80]
            elif re.search(r"^\s*status:\s*done", block, re.MULTILINE):
                done += 1
    return done, step


def classify_unit(wt: Path, kind: str, unit: Path, changed: set[str] | None) -> dict[str, object]:
    """Three-way split of one copy of a unit.

    legacy: has a completion/cancel marker (`unit_completion_marker`) and this worktree has not
      changed the unit since it forked from the default branch: a record from before 3.0.0.
    closing: has a marker and this worktree changed the unit: 3.0.0 writes these files before
      review, graduation and deletion, so the work is not closed.
    live: no marker.
    """
    rel = unit.relative_to(wt)
    marker = unit_completion_marker(wt, rel)
    own = changed is None or rel.as_posix() in changed  # no comparison possible: never hide work
    names = {p.name for p in unit.iterdir() if p.is_file()}
    stages = STAGES[kind]
    hit = next(((i, label) for i, (suffix, label) in enumerate(stages) if any(n.endswith(suffix) for n in names)), None)
    stage, rank = (hit[1], len(stages) - hit[0]) if hit else ("started", 0)
    done, step = checklist_progress(unit)
    if marker:
        stage = f"closing: {CLOSING[marker]}"
        if marker == "implementation-done":
            evidence = review_has_subagent_evidence(wt / review_file_for(rel))
            stage += f"; subagent review evidence {'present' if evidence else 'absent'}"
    elif kind == "goals" and (status := front_value(unit / "state.yaml", "status")):
        stage += f" ({status})"
    legacy = bool(marker) and not own
    if step and not legacy:
        stage += f", next step: {step}"
    return {"legacy": legacy, "own": own, "stage": stage, "next_step": step, "rank": (not legacy, bool(marker), rank, done)}


def collect_units(worktrees: list[dict], base: str | None, not_checked: list[str]) -> tuple[list[dict], list[dict], list[str], set[str]]:
    """One entry per (kind, unit) across worktrees, from its furthest-along copy.

    Tie-break: higher stage, then more done steps, then the earlier worktree in
    `git worktree list` order (main checkout first). Legacy units are only counted.
    """
    copies: dict[tuple[str, str], list[dict]] = {}
    reports: dict[str, dict] = {}
    for wt in worktrees:
        wt_path = Path(wt["path"])
        base_dir = wt_path / ".codestable"
        changed = changed_units(wt_path, base)
        if changed is None:
            not_checked.append(f"unit changes in {wt_path.as_posix()}: no fork point with the default branch "
                               f"({base}), so its units are treated as current work")
        for kind in WORK_ROOTS:
            parent = base_dir / kind
            for unit in sorted(p for p in parent.iterdir() if p.is_dir()) if parent.is_dir() else []:
                if not any(f.is_file() and not f.name.startswith(".") for f in unit.rglob("*")):
                    continue  # nothing but hidden files such as .DS_Store
                copies.setdefault((kind, unit.name), []).append(
                    {"kind": kind.rstrip("s"), "unit": unit.name, "branch": wt.get("branch"), "wt": wt["path"],
                     "pointer": unit.as_posix(), "parent": f".codestable/{kind}",
                     **classify_unit(wt_path, kind, unit, changed)})
        for report in sorted(base_dir.rglob("approval-report.md")) if base_dir.is_dir() else []:
            item = reports.setdefault(report.relative_to(wt_path).as_posix(), {"status": set(), "copies": []})
            item["status"].add(front_value(report, "status"))
            item["copies"].append((wt.get("branch"), report.as_posix(), front_value(report, "reason")))
    in_progress: list[dict] = []
    legacy: dict[str, int] = {}
    owned: set[str] = set()
    for group in copies.values():
        best = max(group, key=lambda c: c["rank"])  # max() keeps the first of equal copies
        if best["legacy"]:
            legacy[best["parent"]] = legacy.get(best["parent"], 0) + 1
            continue
        owned.update(c["wt"] for c in group if c["own"])
        entry = {k: best[k] for k in ("kind", "unit", "stage", "next_step", "pointer")}
        entry["branches"] = sorted({str(c["branch"]) for c in group if c["branch"]})
        entry["pointers"] = [c["pointer"] for c in group]
        in_progress.append(entry)
    # An approval report only moves forward: decided in any copy means decided.
    waiting = [{"kind": "approval-report", "detail": item["copies"][0][2] or "pending decision",
                "branches": sorted({str(b) for b, _p, _r in item["copies"] if b}), "pointer": item["copies"][0][1]}
               for item in reports.values()
               if "pending" in item["status"] and not any(s and s != "pending" for s in item["status"])]
    notes = []
    if legacy:
        notes.append(
            f"{sum(legacy.values())} finished or canceled work directories, unchanged since this branch forked from "
            f"{base} (records from before 3.0.0), are not listed: " + ", ".join(f"{p} ({n})" for p, n in sorted(legacy.items()))
            + "; review gaps in such old records are reported by codestable-doctor.py, not here")
    return in_progress, waiting, notes, owned


def branch_entries(worktrees: list[dict], base: str | None, owned: set[str], notes: list[str]) -> list[dict]:
    """Work with no directory: a worktree ahead of the default branch or with a dirty tree."""
    entries = []
    for wt in worktrees:
        ahead = int((git_lines(wt["path"], "rev-list", "--count", f"{base}..HEAD") or ["0"])[0]) if base else 0
        dirty = bool(git_lines(wt["path"], "status", "--porcelain"))
        if (ahead or dirty) and wt["path"] not in owned:
            label = wt.get("branch") or "(detached)"
            entries.append({"kind": "branch", "unit": label, "ahead": ahead, "dirty": dirty, "branches": [label],
                            "stage": f"{ahead} commits ahead of {base}" + (", uncommitted changes" if dirty else ""),
                            "next_step": "", "pointer": f"{label} @ {wt['path']}"})
    checked_out = {wt.get("branch") for wt in worktrees}
    loose = [b for b in git_lines(worktrees[0]["path"], "for-each-ref", f"--no-merged={base}", "--format=%(refname:short)",
                                  "refs/heads") if b not in checked_out] if base else []
    if loose:
        notes.append(f"{len(loose)} local branches are ahead of {base} and have no worktree")
    return entries


def open_prs(root: Path, not_checked: list[str]) -> list[dict]:
    if shutil.which("gh") is None:
        not_checked.append("open PRs: gh is not installed")
        return []
    result = subprocess.run(["gh", "pr", "list", "--state", "open", "--json", "number,title,headRefName,url"],
                            cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        not_checked.append("open PRs: gh failed (" + (result.stderr.strip().splitlines() or ["no output"])[0] + ")")
        return []
    try:
        prs = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        not_checked.append("open PRs: gh output was not JSON")
        return []
    return [{"kind": "open-pr", "detail": f"#{pr['number']} {pr['title']}", "branches": [pr.get("headRefName")],
             "pointer": pr["url"]} for pr in prs]


def yaml_scalar(value: str) -> str:
    value = re.sub(r"\s+#.*$", "", value.strip())
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"" else value


def roadmap_items(text: str) -> list[dict[str, str]]:
    """Items of an items.yaml split by list indentation; only item-level keys are read."""
    items: list[dict[str, str]] = []
    dash_col, key_col = None, 0
    for line in text.splitlines():
        dash = re.match(r"^(\s*)-(\s+)(?=\w[\w-]*:)", line)
        if dash and (dash_col is None or len(dash.group(1)) == dash_col):
            dash_col, key_col = len(dash.group(1)), dash.end()
            items.append({})
            line = " " * key_col + line[key_col:]
        elif not items:
            continue
        if len(line) - len(line.lstrip()) == key_col:
            key, sep, value = line.strip().partition(":")
            if sep and re.fullmatch(r"\w[\w-]*", key):
                items[-1].setdefault(key, yaml_scalar(value))
    return items


def roadmap_next(root: Path) -> list[dict]:
    found = []
    for path in sorted((root / ".codestable/roadmap").glob("*/*-items.yaml")):
        for item in roadmap_items(path.read_text(encoding="utf-8", errors="replace")):
            if item.get("slug") and item.get("status") in {"in-progress", "planned"}:
                found.append({"roadmap": path.parent.name, "slug": item["slug"], "status": item["status"],
                              "pointer": path.as_posix()})
    return found


def recent_commits(root: Path, branch: str | None, not_checked: list[str]) -> list[dict]:
    result = run_git(root, "log", branch, "-n", "10", "--format=%h%x09%s") if branch else None
    if result is None or result.returncode != 0:
        not_checked.append("recent commits: default branch could not be read")
        return []
    return [{"commit": h, "subject": s, "pointer": h}
            for h, _, s in (line.partition("\t") for line in result.stdout.splitlines())]


def status(root: Path, with_prs: bool = False) -> dict[str, object]:
    root = root.resolve()
    not_checked = ["remote state: nothing was fetched, so origin may be ahead of what is shown"]
    payload: dict[str, object] = {"root": root.as_posix(), "default_branch": None, "in_progress": [], "waiting": [],
                                  "recent": [], "next": [], "not_checked": not_checked, "notes": []}
    if not (root / ".codestable").is_dir():
        payload["notes"] = [".codestable/ not found: answer from git (worktree list, branches, log)"]
        return payload
    worktrees = [{"path": p, **info} for p, info in worktree_map(root).items() if Path(p).is_dir()]
    worktrees = worktrees or [{"path": root.as_posix(), "branch": None}]
    base = default_branch(root)
    payload["default_branch"] = base
    in_progress, waiting, notes, owned = collect_units(worktrees, base, not_checked)
    in_progress += branch_entries(worktrees, base, owned, notes)
    inbox_tool = load_inbox_tool()
    if inbox_tool is not None:
        for item in inbox_tool.inbox(root)["items"]:
            if item.get("status") in OPEN_INBOX and not item.get("snoozed"):
                waiting.append({"kind": "unmerged-worktree", "detail": f"{item['status']}: {'; '.join(item['reasons'])}".rstrip(": "),
                                "branches": [item.get("branch")], "pointer": str(item.get("worktree") or item.get("branch"))})
    if with_prs:
        waiting.extend(open_prs(root, not_checked))
    else:
        not_checked.append("open PRs: not queried (pass --prs to ask gh)")
    nxt = roadmap_next(root) or [
        {"kind": "unit-step", "unit": u["unit"], "step": u["next_step"], "pointer": u["pointer"]}
        for u in in_progress if u["next_step"]
    ]
    if not nxt:
        notes.append("no next step is recorded (no roadmap items, no pending checklist step)")
    payload.update(in_progress=in_progress, waiting=waiting, next=nxt, notes=notes,
                   recent=recent_commits(root, base, not_checked))
    return payload


def emit(payload: dict[str, object]) -> None:
    print(f"Progress snapshot ({payload['root']}, default branch: {payload['default_branch']})")
    for section in ("in_progress", "waiting", "recent", "next"):
        print(f"\n{section}:")
        for entry in payload[section]:
            skip = {"pointer", "pointers", "next_step", "ahead", "dirty"} | ({"branches"} if entry.get("kind") == "branch" else set())
            fields = [", ".join(v) if isinstance(v, list) else str(v) for k, v in entry.items() if k not in skip and v]
            print(f"- {' | '.join(fields)} -> {entry['pointer']}")
        if not payload[section]:
            print("- (none)")
    for label in ("not_checked", "notes"):
        for line in payload[label]:
            print(f"[{label}] {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    parser.add_argument("--prs", action="store_true", help="Also list open PRs through gh (network)")
    args = parser.parse_args()
    payload = status(Path(args.root), args.prs)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        emit(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
