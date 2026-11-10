#!/usr/bin/env python3
"""Shared helpers for CodeStable repository state tools."""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


# Version of the CodeStable skill package these tools were copied from.
# `.codestable/tools/` and `.codestable/reference/` are copied together, so a
# mismatch against `.codestable/reference/MANIFEST.json` means the project
# refreshed one half of the shared runtime but not the other.
# Kept in sync with the repository VERSION file by tests/test_package_contract.py.
PACKAGE_VERSION = "3.0.1"

REFERENCE_MANIFEST_RELPATH = ".codestable/reference/MANIFEST.json"


def reference_drift(root: Path) -> dict[str, object]:
    """Report whether the project's shared reference copy is complete and current.

    Returns a report with ``state``:

    - ``ok``: manifest present, version matches, every listed file exists;
    - ``unversioned``: no manifest — the copy predates manifest tracking and has
      never been refreshed since;
    - ``version-mismatch``: reference and tools came from different package
      versions;
    - ``incomplete``: the copy is missing files its own manifest lists;
    - ``unreadable``: the manifest cannot be parsed or has the wrong shape;
    - ``absent``: there is no ``.codestable/reference/`` at all. ``has_codestable``
      distinguishes a project that never onboarded from one whose reference
      directory went missing — the latter dangles every skill's reference pointer.

    Note this verifies presence, not content: files are not hashed, so a locally
    edited reference file at the right version still reports ``ok``.
    """
    reference_dir = root / ".codestable" / "reference"
    if not reference_dir.is_dir():
        return {
            "state": "absent",
            "expected_version": PACKAGE_VERSION,
            "has_codestable": (root / ".codestable").is_dir(),
        }

    manifest_path = root / REFERENCE_MANIFEST_RELPATH
    if not manifest_path.is_file():
        return {
            "state": "unversioned",
            "expected_version": PACKAGE_VERSION,
            "reference_dir": reference_dir.as_posix(),
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "state": "unreadable",
            "expected_version": PACKAGE_VERSION,
            "error": f"unreadable manifest: {error}",
        }

    # A truncated or hand-edited manifest is exactly what this check exists to
    # catch, so validate its shape instead of letting it raise out of diagnose().
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or not all(isinstance(name, str) for name in files):
        return {
            "state": "unreadable",
            "expected_version": PACKAGE_VERSION,
            "error": "malformed manifest: expected an object with a list of file names",
        }

    found_version = str(manifest.get("version", ""))
    missing = sorted(name for name in files if not (reference_dir / name).is_file())

    if missing:
        return {
            "state": "incomplete",
            "expected_version": PACKAGE_VERSION,
            "found_version": found_version,
            "missing": missing,
        }
    if found_version != PACKAGE_VERSION:
        return {
            "state": "version-mismatch",
            "expected_version": PACKAGE_VERSION,
            "found_version": found_version,
        }
    return {"state": "ok", "expected_version": PACKAGE_VERSION, "found_version": found_version}


IMPLEMENTATION_PREFIXES = (
    "app/",
    "backend/",
    "client/",
    "frontend/",
    "lib/",
    "packages/",
    "scripts/",
    "server/",
    "src/",
    "supabase/migrations/",
    "test/",
    "tests/",
)

IMPLEMENTATION_SUFFIXES = (
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
)

UNIT_ROOTS = ("features", "issues", "refactors")
IMPLEMENTATION_UNIT_ROOTS = frozenset(UNIT_ROOTS)
KNOWN_SKILL_DIRS = {
    "browser-bridge",
    "codestable-maintainer",
    "cs",
    "cs-audit",
    "cs-brainstorm",
    "cs-explore",
    "cs-feat",
    "cs-goal",
    "cs-guide",
    "cs-issue",
    "cs-keep",
    "cs-onboard",
    "cs-refactor",
    "cs-roadmap",
    "using-codestable",
}


@dataclass(frozen=True)
class ChangedFile:
    status: str
    path: str


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class BacklogItem:
    kind: str
    path: str
    line: int
    text: str


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_output(root: Path, *args: str) -> str:
    result = run_git(root, *args)
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()


def git_status(root: Path, *extra_args: str) -> list[ChangedFile]:
    result = run_git(root, "status", "--porcelain", "-uall", *extra_args)
    if result.returncode != 0:
        return []

    changed: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        changed.append(ChangedFile(status=status, path=raw_path.strip('"')))
    return changed


def staged_files(root: Path) -> list[ChangedFile]:
    result = run_git(root, "diff", "--cached", "--name-status")
    if result.returncode != 0:
        return []
    changed: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status, _, path = line.partition("\t")
        if "\t" in path:
            path = path.rsplit("\t", 1)[-1]
        changed.append(ChangedFile(status=status, path=path))
    return changed


def current_branch(root: Path) -> str | None:
    result = run_git(root, "branch", "--show-current")
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def ref_exists(root: Path, ref: str) -> bool:
    return run_git(root, "rev-parse", "--verify", "--quiet", ref).returncode == 0


def ref_head(root: Path, ref: str) -> str | None:
    result = run_git(root, "rev-parse", "--verify", ref)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def default_branch(root: Path) -> str | None:
    origin_head = run_git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if origin_head.returncode == 0:
        value = origin_head.stdout.strip()
        if value.startswith("origin/"):
            return value.split("/", 1)[1]
    for candidate in ("main", "master"):
        if ref_exists(root, candidate) or ref_exists(root, f"refs/heads/{candidate}"):
            return candidate
    # No remote and no main/master: the main checkout (first `git worktree list` entry)
    # is the best guess, not whatever feature branch this linked worktree is on.
    listing = run_git(root, "worktree", "list", "--porcelain")
    if listing.returncode == 0:
        for line in listing.stdout.split("\n\n", 1)[0].splitlines():
            if line.startswith("branch "):
                return line.removeprefix("branch ").removeprefix("refs/heads/")
    return current_branch(root)


def is_linked_worktree(root: Path) -> bool:
    superproject = run_git(root, "rev-parse", "--show-superproject-working-tree")
    in_submodule = superproject.returncode == 0 and bool(superproject.stdout.strip())

    git_dir = run_git(root, "rev-parse", "--path-format=absolute", "--git-dir")
    common_dir = run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if git_dir.returncode == 0 and common_dir.returncode == 0:
        git_dir_path = Path(git_dir.stdout.strip()).resolve()
        common_dir_path = Path(common_dir.stdout.strip()).resolve()
        if git_dir_path != common_dir_path and not in_submodule:
            return True

    return False


def is_implementation_path(path: str) -> bool:
    if path.startswith(".codestable/"):
        return False
    return path.startswith(IMPLEMENTATION_PREFIXES) or path.endswith(IMPLEMENTATION_SUFFIXES)


def path_bucket(path: str) -> str:
    if path.startswith(".codestable/"):
        return "codestable"
    first = Path(path).parts[0] if Path(path).parts else ""
    if first in KNOWN_SKILL_DIRS:
        return "installed_skill"
    if path.startswith("supabase/migrations/"):
        return "migrations"
    if path.startswith("docs/database/"):
        return "database_docs"
    if path.startswith(("data/input/", "data/output/")):
        return "data"
    if path.endswith((".log", ".jsonl")) or "/logs/" in path or path.startswith("logs/"):
        return "logs"
    if path.startswith(("docs/", "doc/")) or path.endswith(".md"):
        return "docs"
    if path.startswith("tests/") or path.startswith("test/"):
        return "tests"
    if is_implementation_path(path):
        return "code"
    return "unknown"


def is_secret_like_path(path: str) -> bool:
    lower = path.lower()
    name = Path(lower).name
    return name.startswith(".env") or "secret" in lower or "token" in lower or "credential" in lower


SECRET_QUOTED_VALUE_RE = re.compile(
    r"(?i)(token|api[_-]?key|secret|password|credential)(\s*[:=]\s*)(['\"])([^'\"\n]+)(['\"])"
)
SECRET_VALUE_RE = re.compile(
    r"(?i)(token|api[_-]?key|secret|password|credential)(\s*[:=]\s*)([^\s'\"`]+)"
)


def redact_text(text: str) -> str:
    text = SECRET_QUOTED_VALUE_RE.sub(r"\1\2\3[REDACTED]\5", text)
    text = SECRET_VALUE_RE.sub(r"\1\2[REDACTED]", text)
    text = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/=-]{12,}", r"\1[REDACTED]", text)
    text = re.sub(r"eyJ[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]{12,}", "[REDACTED_JWT]", text)
    return text


def bucket_paths(paths: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for path in paths:
        buckets.setdefault(path_bucket(path), []).append(path)
    return {bucket: sorted(values) for bucket, values in sorted(buckets.items())}


def unit_dir_for(path: str) -> Path | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != ".codestable" or parts[1] not in UNIT_ROOTS:
        return None
    return Path(*parts[:3])


def unit_slug(unit_dir: Path) -> str:
    return unit_dir.name.split("-", 3)[-1]


def review_file_for(unit_dir: Path) -> Path:
    return unit_dir / f"{unit_slug(unit_dir)}-implementation-review.md"


def unit_files(unit_root: Path, suffix: str) -> list[Path]:
    """`*-<suffix>` (slug-prefixed names) plus the bare `<suffix>` that older units used."""
    bare = unit_root / suffix
    return [*sorted(unit_root.glob(f"*-{suffix}")), *([bare] if bare.is_file() else [])]


def existing_review_file(root: Path, unit_dir: Path) -> Path:
    """The unit's implementation review file, slug-prefixed or bare; the canonical path when neither exists."""
    for candidate in (review_file_for(unit_dir), unit_dir / "implementation-review.md"):
        if (root / candidate).exists():
            return candidate
    return review_file_for(unit_dir)


def all_checklist_steps_done(path: Path) -> bool:
    if not path.exists():
        return False

    in_steps = False
    saw_step = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == "steps:":
            in_steps = True
            continue
        if in_steps and stripped and not raw_line.startswith((" ", "-")):
            break
        if not in_steps:
            continue
        if stripped.startswith("- "):
            saw_step = True
        if stripped.startswith("status:"):
            _, _, value = stripped.partition(":")
            if value.strip() != "done":
                return False
    return saw_step


def unit_needs_review(root: Path, unit_dir: Path) -> bool:
    unit_root = root / unit_dir
    if not unit_root.exists():
        return False
    unit_type = unit_dir.parts[1]

    if unit_type == "features":
        return bool(unit_files(unit_root, "ff-note.md")) or any(
            all_checklist_steps_done(path) for path in unit_files(unit_root, "checklist.yaml")
        )

    if unit_type == "issues":
        return bool(unit_files(unit_root, "fix-note.md"))

    if unit_type == "refactors":
        return bool(unit_files(unit_root, "apply-notes.md")) or any(
            all_checklist_steps_done(path) for path in unit_files(unit_root, "checklist.yaml")
        )

    return False


def find_touched_units(changed: list[ChangedFile]) -> set[Path]:
    units: set[Path] = set()
    for item in changed:
        unit_dir = unit_dir_for(item.path)
        if unit_dir is not None:
            units.add(unit_dir)
    return units


def iter_units(root: Path) -> list[Path]:
    units: list[Path] = []
    codestable = root / ".codestable"
    for unit_root in UNIT_ROOTS:
        parent = codestable / unit_root
        if not parent.exists():
            continue
        units.extend(path.relative_to(root) for path in parent.iterdir() if path.is_dir())
    return sorted(units, key=lambda path: path.as_posix())


def unit_completion_marker(root: Path, unit_dir: Path) -> str | None:
    """Why a unit is past its working phase, by the repo's own predicates, or None.

    "canceled": a lifecycle file says canceled/abandoned. "complete": a goal's
    `state.yaml` is terminal. "implementation-done": `unit_needs_review` (ff-note,
    fix-note, apply-notes or every checklist step done). In the 3.0.0 flow all of
    these precede review, graduation and deletion, so a marker alone does not
    mean the unit is closed.
    """
    if unit_has_canceled_lifecycle_status(root, unit_dir.as_posix()):
        return "canceled"
    if unit_dir.parts[1] == "goals":
        try:
            lines = (root / unit_dir / "state.yaml").read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return None
        for line in lines:
            key, sep, value = line.partition(":")
            if sep and key.strip() == "status":
                return "complete" if value.strip().strip("\"'").lower() in GOAL_TERMINAL_STATUSES else None
        return None
    return "implementation-done" if unit_needs_review(root, unit_dir) else None


def review_has_subagent_evidence(path: Path) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() == "reviewer" and value.strip().lower() == "subagent":
            return True
    return False


def missing_review_findings(root: Path, units: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for unit_dir in units:
        if not unit_needs_review(root, unit_dir):
            continue
        review_path = existing_review_file(root, unit_dir)
        full_review_path = root / review_path
        if not full_review_path.exists():
            findings.append(
                Finding(
                    severity="P1",
                    message="Completed CodeStable implementation unit is missing implementation review evidence.",
                    path=review_path.as_posix(),
                )
            )
        elif not review_has_subagent_evidence(full_review_path):
            findings.append(
                Finding(
                    severity="P1",
                    message="CodeStable implementation review must use a subagent reviewer.",
                    path=review_path.as_posix(),
                )
            )
    return findings


def unit_was_removed(root: Path, unit_dir: Path) -> bool:
    """True when a unit directory is gone from the working tree because it was closed.

    Closing a unit deletes its work directory (shared-conventions.md, section 3),
    so a missing directory that git still knows about is a finished unit, not a
    typo. The deletion may be uncommitted (HEAD still has the files) or committed.
    """
    if (root / unit_dir).exists():
        return False
    path = unit_dir.as_posix()
    tracked = run_git(root, "ls-tree", "-r", "--name-only", "HEAD", "--", path)
    if tracked.returncode == 0 and tracked.stdout.strip():
        return True
    deleted = run_git(root, "log", "-1", "--diff-filter=D", "--format=%H", "--", path)
    return deleted.returncode == 0 and bool(deleted.stdout.strip())


def looks_like_unit_path(candidate: Path) -> bool:
    parts = candidate.parts
    return len(parts) == 3 and parts[0] == ".codestable" and parts[1] in (*UNIT_ROOTS, "goals")


GOAL_TERMINAL_STATUSES = {"complete", "canceled", "cancelled", "abandoned"}


def head_files(root: Path, directory: Path) -> list[str]:
    """Paths of tracked files under `directory` in HEAD (empty when HEAD has none)."""
    listing = run_git(root, "ls-tree", "-r", "--name-only", "HEAD", "--", directory.as_posix())
    if listing.returncode != 0:
        return []
    return [line for line in listing.stdout.splitlines() if line]


def head_text(root: Path, path: str) -> str | None:
    shown = run_git(root, "show", f"HEAD:{path}")
    return shown.stdout if shown.returncode == 0 else None


def checklist_steps_done_text(text: str) -> bool:
    in_steps = False
    saw_step = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped == "steps:":
            in_steps = True
            continue
        if in_steps and stripped and not raw_line.startswith((" ", "-")):
            break
        if not in_steps:
            continue
        if stripped.startswith("- "):
            saw_step = True
        if stripped.startswith("status:"):
            _, _, value = stripped.partition(":")
            if value.strip() != "done":
                return False
    return saw_step


def head_unit_needs_review(root: Path, unit_dir: Path) -> bool:
    """`unit_needs_review`, decided from the unit's content in HEAD."""
    names = head_files(root, unit_dir)
    base = {Path(n).name for n in names}
    unit_type = unit_dir.parts[1]

    def done_checklist() -> bool:
        return any(
            checklist_steps_done_text(head_text(root, n) or "")
            for n in names
            if Path(n).name.endswith("-checklist.yaml")
        )

    if unit_type == "features":
        return any(n.endswith("-ff-note.md") for n in base) or done_checklist()
    if unit_type == "issues":
        return any(n.endswith("-fix-note.md") for n in base)
    if unit_type == "refactors":
        return any(n.endswith("-apply-notes.md") for n in base) or done_checklist()
    return False


def head_unit_canceled(root: Path, unit_dir: Path) -> bool:
    slug = unit_slug(unit_dir)
    for suffix in ("acceptance", "ff-note", "fix-note", "apply-notes"):
        text = head_text(root, f"{unit_dir.as_posix()}/{slug}-{suffix}.md")
        if text and any(
            (m := STATUS_RE.match(line)) and m.group(1).lower() in CANCELED_UNIT_STATUSES
            for line in text.splitlines()
        ):
            return True
    return False


def deleted_unit_dirs(root: Path, paths: list[str]) -> set[Path]:
    """Work directories (feature / issue / refactor / goal) that this change removes
    entirely: some path sits under them, the directory is gone, and HEAD has it."""
    units: set[Path] = set()
    for path in paths:
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != ".codestable" or parts[1] not in (*UNIT_ROOTS, "goals"):
            continue
        unit = Path(*parts[:3])
        if unit in units or (root / unit).exists():
            continue
        if head_files(root, unit):
            units.add(unit)
    return units


def unit_deletion_findings(root: Path, paths: list[str], allow_self_review: bool = False) -> list[Finding]:
    """Guard the closing deletion of a work directory.

    A deleted directory no longer shows what it was, so the decision uses HEAD:
    a unit that needed implementation review there must already carry subagent
    review evidence there; an unfinished goal must not be deleted; and the
    deletion must not ride along with implementation changes (delete the
    directory in its own commit).
    """
    units = deleted_unit_dirs(root, paths)
    if not units:
        return []
    findings: list[Finding] = []
    for unit in sorted(units):
        if unit.parts[1] == "goals":
            state = head_text(root, f"{unit.as_posix()}/state.yaml") or ""
            status = ""
            for line in state.splitlines():
                key, sep, value = line.partition(":")
                if sep and key.strip() == "status":
                    status = value.strip().strip("\"'").lower()
                    break
            if status and status not in GOAL_TERMINAL_STATUSES:
                findings.append(
                    Finding(
                        severity="P1",
                        message=(
                            f"Goal directory is being deleted while its state.yaml in HEAD says status: {status}. "
                            "An active or blocked goal's directory is its recovery record."
                        ),
                        path=unit.as_posix(),
                    )
                )
            continue
        if not head_unit_needs_review(root, unit) or head_unit_canceled(root, unit):
            continue
        review_path = review_file_for(unit)
        review = head_text(root, review_path.as_posix())
        if review is None:
            findings.append(
                Finding(
                    severity="P1",
                    message=(
                        "Work directory is being deleted but HEAD holds no implementation review evidence for it. "
                        "Commit the review evidence first, then delete the directory in its own commit."
                    ),
                    path=review_path.as_posix(),
                )
            )
        elif not allow_self_review and not any(
            (parts := line.partition(":"))[1]
            and parts[0].strip().lower() == "reviewer"
            and parts[2].strip().lower() == "subagent"
            for line in review.splitlines()
        ):
            findings.append(
                Finding(
                    severity="P1",
                    message="Implementation review evidence in HEAD does not show reviewer: subagent.",
                    path=review_path.as_posix(),
                )
            )
    implementation = [path for path in paths if is_implementation_path(path)]
    if implementation:
        findings.append(
            Finding(
                severity="P1",
                message=(
                    "A change that deletes a work directory must not also carry implementation changes; "
                    "commit the code and review evidence first, then delete the directory in its own commit."
                ),
                path=", ".join(implementation),
            )
        )
    return findings


def resolve_unit(root: Path, value: str, allow_removed: bool = False) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve().relative_to(root.resolve())
    if (root / candidate).exists():
        return candidate
    matches = [unit for unit in iter_units(root) if value in unit.name or value == unit_slug(unit)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        if looks_like_unit_path(candidate) and unit_was_removed(root, candidate):
            if allow_removed:
                return candidate
            raise ValueError(
                f"unit was closed and its work directory deleted (see git history): {value}"
            )
        raise ValueError(f"unit not found: {value}")
    raise ValueError(f"unit is ambiguous: {value}")


def is_implementation_unit(unit_dir: Path) -> bool:
    parts = unit_dir.parts
    return len(parts) >= 3 and parts[0] == ".codestable" and parts[1] in IMPLEMENTATION_UNIT_ROOTS


def override_file_for(root: Path, unit_dir: Path) -> Path:
    return root / unit_dir / "worktree-override.md"


def has_human_approved_override(root: Path, unit_dir: Path) -> bool:
    path = override_file_for(root, unit_dir)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return "reason" in text and "scope" in text and ("approved" in text or "approval" in text)


def baseline_id(unit_dir: Path) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", unit_dir.as_posix()).strip("_")


def baseline_path(root: Path, unit_dir: Path) -> Path:
    result = run_git(root, "rev-parse", "--git-path", f"codestable/worktree-gate/{baseline_id(unit_dir)}.json")
    if result.returncode == 0 and result.stdout.strip():
        return (root / result.stdout.strip()).resolve()
    return root / ".git" / "codestable" / "worktree-gate" / f"{baseline_id(unit_dir)}.json"


def write_baseline(root: Path, unit_dir: Path) -> dict[str, object]:
    branch = current_branch(root)
    default = default_branch(root)
    default_ref = default or branch or "HEAD"
    baseline = {
        "unit": unit_dir.as_posix(),
        "default_branch": default,
        "default_head": ref_head(root, default_ref),
        "current_branch": branch,
        "worktree": root.resolve().as_posix(),
        "linked_worktree": is_linked_worktree(root),
        "timestamp": int(time.time()),
    }
    path = baseline_path(root, unit_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return baseline


def read_baseline(root: Path, unit_dir: Path) -> dict[str, object] | None:
    path = baseline_path(root, unit_dir)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def iter_baselines(root: Path) -> list[dict[str, object]]:
    git_path = run_git(root, "rev-parse", "--git-path", "codestable/worktree-gate")
    if git_path.returncode != 0 or not git_path.stdout.strip():
        return []
    baseline_root = (root / git_path.stdout.strip()).resolve()
    if not baseline_root.exists():
        return []
    baselines: list[dict[str, object]] = []
    for path in sorted(baseline_root.glob("*.json")):
        try:
            baselines.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return baselines


def changed_paths_between(root: Path, base_ref: str, head_ref: str) -> list[str]:
    diff = run_git(root, "diff", "--name-only", f"{base_ref}..{head_ref}")
    if diff.returncode != 0:
        return []
    return [line.strip() for line in diff.stdout.splitlines() if line.strip()]


def changed_status_between(root: Path, base_ref: str, head_ref: str) -> list[tuple[str, str]]:
    diff = run_git(root, "diff", "--name-status", f"{base_ref}..{head_ref}")
    if diff.returncode != 0:
        return []
    changes: list[tuple[str, str]] = []
    for line in diff.stdout.splitlines():
        status, _, rest = line.partition("\t")
        if status and rest:
            changes.append((status, rest.split("\t")[-1]))
    return changes


def post_baseline_implementation_changes(root: Path, baseline: dict[str, object]) -> list[str]:
    default = baseline.get("default_branch")
    default_head = baseline.get("default_head")
    if not default or not default_head:
        return []
    head = ref_head(root, str(default))
    if not head or head == default_head:
        return []
    return [
        path
        for path in changed_paths_between(root, str(default_head), str(default))
        if is_implementation_path(path)
    ]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_common_dir(root: Path) -> Path:
    result = run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return (root / ".git").resolve()


def inbox_dir(root: Path) -> Path:
    return git_common_dir(root) / "codestable" / "worktree-inbox"


def inbox_record_id(branch: str | None, unit_dir: Path | str | None) -> str:
    source = branch or (unit_dir.as_posix() if isinstance(unit_dir, Path) else str(unit_dir or "detached"))
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", source).strip("_") or "detached"


def inbox_record_path(root: Path, branch: str | None, unit_dir: Path | str | None) -> Path:
    return inbox_dir(root) / f"{inbox_record_id(branch, unit_dir)}.json"


def write_inbox_record(root: Path, record: dict[str, object]) -> Path:
    path = inbox_record_path(root, str(record.get("branch") or ""), str(record.get("unit") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def iter_inbox_records(root: Path) -> list[dict[str, object]]:
    directory = inbox_dir(root)
    if not directory.exists():
        return []
    records: list[dict[str, object]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            record["_record_path"] = path.as_posix()
            records.append(record)
    return records


def branch_head(root: Path, branch: str) -> str | None:
    return ref_head(root, branch) or ref_head(root, f"refs/heads/{branch}")


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return run_git(root, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def worktree_map(root: Path) -> dict[str, dict[str, object]]:
    result = run_git(root, "worktree", "list", "--porcelain")
    if result.returncode != 0:
        return {}
    entries: dict[str, dict[str, object]] = {}
    current: dict[str, object] = {}
    for line in result.stdout.splitlines():
        if not line:
            if current.get("path"):
                entries[str(current["path"])] = current
            current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = str(Path(value).resolve())
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            current["detached"] = True
    if current.get("path"):
        entries[str(current["path"])] = current
    return entries


BACKLOG_PATTERNS = (
    ("needs-human-review", re.compile(r"needs-human-review", re.IGNORECASE)),
    ("human-review", re.compile(r"human review required", re.IGNORECASE)),
    ("accepted-p2", re.compile(r"accepted.{0,40}P2|P2.{0,40}accepted", re.IGNORECASE)),
    ("deferred-p2", re.compile(r"deferred.{0,40}P2|P2.{0,40}deferred", re.IGNORECASE)),
    ("follow-up", re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+)?follow[- ]ups?(?:\s*:|\b)", re.IGNORECASE)),
)
BILINGUAL_POLICY_KIND = "bilingual-report-policy"
ATTENTION_CANDIDATES_HEADING_RE = re.compile(r"attention\.md.{0,40}candidates?|candidates?.{0,40}attention\.md", re.IGNORECASE)
MARKDOWN_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+)")
FOLLOW_UP_SECTION_HEADING_RE = re.compile(r"^\s*#{1,6}\s+follow[- ]ups?\s*$", re.IGNORECASE)
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CHINESE_TEXT_RE = re.compile(r"[\u3400-\u9fff]")
ASCII_WORD_RE = re.compile(r"[A-Za-z]")
BACKLOG_SCAN_EXCLUDED_SUFFIXES = ("-review-packet.md",)
BACKLOG_SCAN_EXCLUDED_PREFIXES = (".codestable/reference/",)
# Only files written for the owner are held to the bilingual policy. Work-directory
# files (design, checklist, acceptance, iterations, ...) are read by agents and use
# one language (shared-conventions.md, report language policy).
BILINGUAL_REPORT_FILENAMES = {"approval-report.md"}
FOLLOW_UP_BLOCKING_TEXT_MARKERS = (
    "before merge",
    "before publish",
    "before release",
    "before ship",
    "before completion",
    "blocking",
    "must",
    "required",
)
RESOLVED_FOLLOW_UP_RE = re.compile(
    r"(?:subagent review )?follow[- ]up(?:s)?(?:\s+(?:fix(?:es)?|review|evidence|implementation)|$)|"
    r"follow[- ]up(?:s)?.{0,40}(?:backlog|fixed;|passed after|was added before|has been fixed)|"
    r"passed after.{0,40}follow[- ]up|"
    r"after follow[- ]up fixes|"
    r"follow[- ]up.{0,80}(?:no (?:new )?(?:remaining )?p0|no (?:new )?(?:remaining )?p1|"
    r"no (?:new )?(?:remaining )?p2|closed|fixed|resolved|已修|无 p0|无 p1|无阻塞)",
    re.IGNORECASE,
)
CANCELED_UNIT_STATUSES = {"canceled", "cancelled", "abandoned"}
STATUS_RE = re.compile(r"^\s*status:\s*['\"]?([a-z0-9_-]+)['\"]?\s*$", re.IGNORECASE)


def should_scan_backlog_file(rel_path: str) -> bool:
    return not (
        rel_path.startswith(BACKLOG_SCAN_EXCLUDED_PREFIXES)
        or rel_path.endswith(BACKLOG_SCAN_EXCLUDED_SUFFIXES)
    )


def attention_requires_english_first_chinese(root: Path) -> bool:
    path = root / ".codestable/attention.md"
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    lowered = text.lower()
    return (
        ("english first" in lowered and "chinese" in lowered)
        or ("英文" in text and "中文" in text and ("先英文" in text or "英文在前" in text))
    )


def is_bilingual_report_target(rel_path: str) -> bool:
    if not rel_path.startswith(".codestable/"):
        return False
    if not should_scan_backlog_file(rel_path):
        return False
    return Path(rel_path).name in BILINGUAL_REPORT_FILENAMES


def content_start_line(lines: list[str]) -> int:
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return index + 1
    return 0


def section_body_text(lines: list[str], headings: list[tuple[int, str, str]], section_line: int, section_level: int) -> str:
    next_peer_line = len(lines) + 1
    for later_line, level, _ in headings:
        later_level = len(level)
        if later_line > section_line and later_level <= section_level:
            next_peer_line = later_line
            break
    body_lines = lines[section_line : next_peer_line - 1]
    return "\n".join(line for line in body_lines if not MARKDOWN_HEADING_RE.match(line.strip()))


def body_text_until(lines: list[str], start_line: int, end_line: int) -> str:
    body_lines = lines[start_line : max(start_line, end_line - 1)]
    return "\n".join(line for line in body_lines if not MARKDOWN_HEADING_RE.match(line.strip()))


def bilingual_policy_violation(lines: list[str]) -> tuple[int, str] | None:
    headings: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines[content_start_line(lines) :], start=content_start_line(lines) + 1):
        match = MARKDOWN_HEADING_RE.match(line.strip())
        if match:
            headings.append((index, match.group(1), match.group(2).strip()))

    explicit_english_sections = [
        (line_no, len(level), title)
        for line_no, level, title in headings
        if title.strip().lower() == "english"
    ]
    top_english_sections = [
        (line_no, len(level), title)
        for line_no, level, title in headings
        if len(level) == 1 and ASCII_WORD_RE.search(title) and not CHINESE_TEXT_RE.search(title)
    ]
    explicit_chinese_sections = [
        (line_no, len(level), title)
        for line_no, level, title in headings
        if CHINESE_TEXT_RE.search(title)
        and "摘要" not in title
        and (title.strip() in {"中文", "中文版"} or "中文版本" in title)
    ]
    top_chinese_sections = [
        (line_no, len(level), title)
        for line_no, level, title in headings
        if len(level) == 1 and CHINESE_TEXT_RE.search(title) and "摘要" not in title
    ]
    english_sections = explicit_english_sections or top_english_sections
    chinese_sections = sorted({*explicit_chinese_sections, *top_chinese_sections})

    if not english_sections:
        return (
            1,
            "Bilingual report policy requires an English top-level section before the Chinese section.",
        )
    if not chinese_sections:
        return (
            english_sections[0][0],
            "Bilingual report policy requires a full Chinese top-level section after the English section; summary-only Chinese subsections are not enough.",
        )
    if chinese_sections[0][0] < english_sections[0][0]:
        return (
            chinese_sections[0][0],
            "Bilingual report policy requires English first, then Chinese.",
        )
    english_line, english_level, _ = english_sections[0]
    chinese_sections_after_english = [section for section in chinese_sections if section[0] > english_line]
    if not chinese_sections_after_english:
        return (
            chinese_sections[0][0],
            "Bilingual report policy requires English first, then Chinese.",
        )
    chinese_line, chinese_level, _ = chinese_sections_after_english[0]
    english_body = body_text_until(lines, english_line, chinese_line)
    if not ASCII_WORD_RE.search(english_body):
        return (
            english_line,
            "Bilingual report policy requires English body content after the English section heading.",
        )
    chinese_body = section_body_text(lines, headings, chinese_line, chinese_level)
    if not CHINESE_TEXT_RE.search(chinese_body):
        return (
            chinese_line,
            "Bilingual report policy requires translated Chinese body content after the Chinese section heading.",
        )
    return None


def is_blocking_follow_up_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in FOLLOW_UP_BLOCKING_TEXT_MARKERS)


def is_blocking_backlog_item(kind: str, text: str) -> bool:
    if kind in {"needs-human-review", "human-review", BILINGUAL_POLICY_KIND}:
        return True
    if kind != "follow-up":
        return False
    return is_blocking_follow_up_text(text)


def is_resolved_backlog_match(kind: str, text: str) -> bool:
    if kind != "follow-up":
        return False
    if is_blocking_follow_up_text(text):
        return False
    return bool(RESOLVED_FOLLOW_UP_RE.search(text))


def unit_lifecycle_status_files(root: Path, unit_dir: Path) -> list[Path]:
    unit_root = root / unit_dir
    slug = unit_slug(unit_dir)
    names = [
        name
        for suffix in ("acceptance.md", "ff-note.md", "fix-note.md", "apply-notes.md")
        for name in (f"{slug}-{suffix}", suffix)  # slug-prefixed, then the bare name older units used
    ]
    return [unit_root / name for name in names if (unit_root / name).exists()]


def file_has_canceled_status(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False
    for line in lines:
        match = STATUS_RE.match(line)
        if match and match.group(1).lower() in CANCELED_UNIT_STATUSES:
            return True
    return False


def unit_has_canceled_lifecycle_status(root: Path, rel_path: str) -> bool:
    unit_dir = unit_dir_for(rel_path)
    if unit_dir is None:
        return False
    return any(file_has_canceled_status(path) for path in unit_lifecycle_status_files(root, unit_dir))


def is_answered_review_authorization(path: Path, lines: list[str]) -> bool:
    """Only completed approval metadata can contextualize a conditional review policy."""
    if path.name != "approval-report.md" or not lines or lines[0].strip() != "---":
        return False
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return False
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip("\"'")
    return (
        fields.get("status") == "approved"
        and fields.get("reason") == "review-authorization"
        and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields.get("answered_at", "")))
    )


def is_conditional_review_policy(text: str) -> bool:
    matches = list(re.finditer(r"human review required", text, re.IGNORECASE))
    return bool(matches) and all(
        re.match(r"\s+only\s+(?:for|if|when)\b", text[match.end():], re.IGNORECASE)
        for match in matches
    )


def scan_backlog(root: Path) -> list[BacklogItem]:
    codestable = root / ".codestable"
    if not codestable.exists():
        return []
    items: list[BacklogItem] = []
    bilingual_required = attention_requires_english_first_chinese(root)
    for path in sorted(codestable.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel_path = path.relative_to(root).as_posix()
        if not should_scan_backlog_file(rel_path):
            continue
        if unit_has_canceled_lifecycle_status(root, rel_path):
            continue
        if bilingual_required and is_bilingual_report_target(rel_path):
            violation = bilingual_policy_violation(lines)
            if violation:
                line_no, text = violation
                items.append(BacklogItem(kind=BILINGUAL_POLICY_KIND, path=rel_path, line=line_no, text=text))
        answered_review_policy = is_answered_review_authorization(path, lines)
        in_attention_candidates = False
        in_follow_up_section = False
        section_heading = ""
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            heading = MARKDOWN_HEADING_RE.match(stripped)
            if heading:
                section_heading = heading.group(2).lower()
                in_attention_candidates = False
                in_follow_up_section = False
            if ATTENTION_CANDIDATES_HEADING_RE.search(stripped):
                in_attention_candidates = True
                continue
            if FOLLOW_UP_SECTION_HEADING_RE.search(stripped):
                in_follow_up_section = True
                continue
            if in_attention_candidates:
                if stripped.startswith("#"):
                    in_attention_candidates = False
                elif not stripped:
                    continue
                else:
                    bullet = MARKDOWN_BULLET_RE.match(line)
                    if bullet and not re.match(r"\[[xX]\]\s", bullet.group(1)):
                        items.append(
                            BacklogItem(
                                kind="attention-candidate",
                                path=rel_path,
                                line=line_no,
                                text=bullet.group(1).strip(),
                            )
                        )
                    continue
            if in_follow_up_section:
                if stripped.startswith("#"):
                    in_follow_up_section = False
                else:
                    bullet = MARKDOWN_BULLET_RE.match(line)
                    if bullet:
                        text = bullet.group(1).strip()
                        if re.match(r"\[[xX]\]\s", text):
                            continue
                        items.append(
                            BacklogItem(
                                kind="follow-up",
                                path=rel_path,
                                line=line_no,
                                text=text,
                            )
                        )
                        continue
            for kind, pattern in BACKLOG_PATTERNS:
                if pattern.search(line):
                    if (
                        kind == "human-review"
                        and answered_review_policy
                        and section_heading == "decision needed"
                        and is_conditional_review_policy(stripped)
                    ):
                        continue
                    if kind == "follow-up" and re.fullmatch(
                        r"(?:[-*]\s+)?follow[- ]ups?\s+applied\s*:", stripped, re.IGNORECASE
                    ):
                        continue
                    if is_resolved_backlog_match(kind, stripped):
                        continue
                    items.append(BacklogItem(kind=kind, path=rel_path, line=line_no, text=stripped))
                    break
    return items


def unit_for_path(path: str) -> str | None:
    unit_dir = unit_dir_for(path)
    return unit_dir.as_posix() if unit_dir is not None else None


def has_secret_like_untracked(root: Path) -> list[str]:
    secret_paths: list[str] = []
    for item in git_status(root):
        if item.status != "??":
            continue
        lower = item.path.lower()
        name = Path(lower).name
        if name.startswith(".env") or "secret" in lower or "token" in lower:
            secret_paths.append(item.path)
    return sorted(secret_paths)


def tracked_ignored_paths(root: Path) -> list[str]:
    result = run_git(root, "ls-files", "-ci", "--exclude-standard")
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
