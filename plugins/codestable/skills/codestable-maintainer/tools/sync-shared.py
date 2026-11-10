#!/usr/bin/env python3
"""Keep each skill's own copies of shared references and tools in sync.

Skills are independent install units and cannot read each other's files, and
since package 3.0.0 nothing is copied into the project either. So every skill
carries the shared documents it cites under ``<skill>/shared/`` and the tools
its stages call under ``<skill>/tools/``. The sources stay in one place:
``cs-onboard/reference/`` and ``cs-onboard/tools/``.

``--check`` (default) reports missing, stale and unused copies and exits 1 on
any of them. ``--write`` rewrites the copies from the sources.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SOURCE_SKILL = "cs-onboard"
# These skills keep their own tool directories and are not sync targets for tools.
OWN_TOOLS = {"cs-onboard", "codestable-maintainer", "browser-bridge"}
# Execution skills run the gates described in the shared conventions, so they
# carry every tool those documents name. Other skills carry only the tools
# their own text calls; the shared documents tell them to skip the rest.
EXECUTION_SKILLS = {"cs-feat", "cs-issue", "cs-refactor", "cs-goal"}
SHARED_CITE = re.compile(r"(?<![\w/-])shared/([A-Za-z0-9_.-]+\.md)")
TOOL_CITE = re.compile(r"\{SKILL_DIR\}/tools/([A-Za-z0-9_.-]+)")
# A tool that loads a sibling at runtime needs that sibling shipped with it.
TOOL_SIBLINGS = {"codestable-doctor.py": ("codestable-worktree-inbox.py",)}


def default_skills_root() -> Path:
    return Path(__file__).resolve().parents[2]


def own_markdown(skill: Path) -> list[Path]:
    skip = {"shared"} | ({"reference"} if skill.name == SOURCE_SKILL else set())
    return [p for p in sorted(skill.rglob("*.md")) if not (set(p.relative_to(skill).parts[:-1]) & skip)]


def shared_closure(names: set[str], reference: Path, unknown: list[str] | None = None) -> set[str]:
    seen: set[str] = set()
    todo = list(names)
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        if not (reference / name).is_file():
            if unknown is not None and name not in unknown:
                unknown.append(name)
            continue
        seen.add(name)
        if name == "tools.md":
            todo += [p.name for p in reference.glob("tools-part*.md")]
        todo += SHARED_CITE.findall((reference / name).read_text(encoding="utf-8"))
    return seen


def plan(skills_root: Path) -> dict[str, dict[str, object]]:
    reference = skills_root / SOURCE_SKILL / "reference"
    tools = skills_root / SOURCE_SKILL / "tools"
    result: dict[str, dict[str, object]] = {}
    for skill in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        text = "\n".join(p.read_text(encoding="utf-8") for p in own_markdown(skill))
        cited_shared = set(SHARED_CITE.findall(text))
        cited_tools = set(TOOL_CITE.findall(text))
        unknown: list[str] = []
        closure = shared_closure(cited_shared, reference, unknown)
        want_shared = set() if skill.name == SOURCE_SKILL else closure
        if skill.name in EXECUTION_SKILLS:
            for name in closure:
                cited_tools.update(TOOL_CITE.findall((reference / name).read_text(encoding="utf-8")))
        want_tools: set[str] = set()
        if skill.name not in OWN_TOOLS:
            for name in cited_tools:
                source = tools / name
                if not source.is_file():
                    unknown.append(f"tools/{name}")
                    continue
                want_tools.add(name)
                want_tools.update(TOOL_SIBLINGS.get(name, ()))
                if "codestable_common" in source.read_text(encoding="utf-8"):
                    want_tools.add("codestable_common.py")
            if any(
                "codestable_common" in (tools / n).read_text(encoding="utf-8")
                for n in want_tools
                if (tools / n).is_file()
            ):
                want_tools.add("codestable_common.py")
        elif skill.name == SOURCE_SKILL:
            unknown += sorted(f"tools/{n}" for n in cited_tools if not (tools / n).is_file())
        result[skill.name] = {"shared": sorted(want_shared), "tools": sorted(want_tools), "unknown": sorted(unknown)}
    return result


def compare(skill: Path, sub: str, want: list[str], source: Path) -> dict[str, list[str]]:
    have_dir = skill / sub
    have = sorted(p.name for p in have_dir.iterdir() if p.is_file()) if have_dir.is_dir() else []
    return {
        "missing": [n for n in want if n not in have],
        "stale": [n for n in want if n in have and (have_dir / n).read_bytes() != (source / n).read_bytes()],
        "unused": [n for n in have if n not in want],
    }


def check(skills_root: Path) -> dict[str, object]:
    reference = skills_root / SOURCE_SKILL / "reference"
    tools = skills_root / SOURCE_SKILL / "tools"
    problems: dict[str, object] = {}
    for name, want in plan(skills_root).items():
        skill = skills_root / name
        entry: dict[str, object] = {}
        if want["unknown"]:
            entry["unknown"] = want["unknown"]
        if name != SOURCE_SKILL:
            diff = compare(skill, "shared", want["shared"], reference)
            if any(diff.values()):
                entry["shared"] = diff
        if name not in OWN_TOOLS:
            diff = compare(skill, "tools", want["tools"], tools)
            if any(diff.values()):
                entry["tools"] = diff
        if entry:
            problems[name] = entry
    return {"ok": not problems, "problems": problems}


def write(skills_root: Path) -> None:
    reference = skills_root / SOURCE_SKILL / "reference"
    tools = skills_root / SOURCE_SKILL / "tools"
    for name, want in plan(skills_root).items():
        skill = skills_root / name
        targets = []
        if name != SOURCE_SKILL:
            targets.append(("shared", want["shared"], reference))
        if name not in OWN_TOOLS:
            targets.append(("tools", want["tools"], tools))
        for sub, names, source in targets:
            target = skill / sub
            if target.is_dir():
                for path in target.iterdir():
                    if path.is_file() and path.name not in names:
                        path.unlink()
            if names:
                target.mkdir(exist_ok=True)
                for item in names:
                    shutil.copyfile(source / item, target / item)
            elif target.is_dir() and not any(target.iterdir()):
                target.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skills-root", type=Path, default=default_skills_root())
    parser.add_argument("--write", action="store_true", help="rewrite the copies from the sources")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.write:
        write(args.skills_root)
    payload = check(args.skills_root)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    elif not payload["ok"]:
        print(json.dumps(payload["problems"], indent=2, ensure_ascii=False, sort_keys=True), file=sys.stderr)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
