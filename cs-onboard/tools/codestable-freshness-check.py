#!/usr/bin/env python3
"""Check whether installed CodeStable skills match the latest source."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


KNOWN_SKILL_DIRS = {
    "browser-bridge",
    "codestable-maintainer",
    "cs",
    "cs-arch",
    "cs-audit",
    "cs-brainstorm",
    "cs-decide",
    "cs-explore",
    "cs-feat",
    "cs-feat-accept",
    "cs-feat-design",
    "cs-feat-ff",
    "cs-feat-impl",
    "cs-goal",
    "cs-guide",
    "cs-issue",
    "cs-issue-analyze",
    "cs-issue-fix",
    "cs-issue-report",
    "cs-learn",
    "cs-libdoc",
    "cs-note",
    "cs-onboard",
    "cs-refactor",
    "cs-refactor-ff",
    "cs-req",
    "cs-roadmap",
    "cs-trick",
    "using-codestable",
}

IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
IGNORED_NAMES = {".DS_Store"}


def run_text(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def run_bytes(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git_text(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_text(["git", *args], root)


def git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return run_bytes(["git", *args], root)


def is_source_repo(root: Path) -> bool:
    return (root / "cs-onboard/SKILL.md").exists() and (root / "using-codestable/SKILL.md").exists()


def source_candidates(cwd: Path) -> list[Path]:
    candidates: list[Path] = []
    env = os.environ.get("CODESTABLE_SOURCE_ROOT")
    if env:
        candidates.append(Path(env))
    candidates.extend([cwd, *cwd.parents])
    candidates.extend(
        [
            Path.home() / "Code/Github/CodeStable",
            Path.home() / "Code/CodeStable",
            Path.home() / "CodeStable",
        ]
    )
    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def locate_source_root(explicit: str | None, cwd: Path) -> Path | None:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        return root if is_source_repo(root) else None
    for candidate in source_candidates(cwd):
        if is_source_repo(candidate):
            return candidate
    return None


def default_installed_roots() -> list[Path]:
    roots = [Path.home() / ".agents/skills", Path.home() / ".codex/skills"]
    return [root for root in roots if root.exists()]


def ref_head(root: Path, ref: str) -> str | None:
    result = git_text(root, "rev-parse", "--verify", ref)
    return result.stdout.strip() if result.returncode == 0 else None


def resolve_latest_ref(root: Path, remote: str, branch: str, explicit_ref: str | None, fetch: bool) -> tuple[str | None, str | None]:
    if explicit_ref:
        return (explicit_ref, ref_head(root, explicit_ref))
    if fetch:
        git_text(root, "fetch", remote, branch)
    for ref in (f"refs/remotes/{remote}/{branch}", f"{remote}/{branch}", branch, "HEAD"):
        head = ref_head(root, ref)
        if head:
            return (ref, head)
    return (None, None)


def is_ignored(path: Path) -> bool:
    return path.name in IGNORED_NAMES or any(part in IGNORED_PARTS for part in path.parts)


def source_files(root: Path, ref: str, skill: str) -> set[str]:
    result = git_text(root, "ls-tree", "-r", "--name-only", ref, "--", skill)
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip() and not is_ignored(Path(line.strip()))}


def show_file(root: Path, ref: str, path: str) -> bytes | None:
    result = git_bytes(root, "show", f"{ref}:{path}")
    return result.stdout if result.returncode == 0 else None


def installed_files(root: Path, skill: str) -> set[str]:
    skill_root = root / skill
    if not skill_root.exists():
        return set()
    files: set[str] = set()
    for path in skill_root.rglob("*"):
        if path.is_file():
            relative = Path(skill) / path.relative_to(skill_root)
            if not is_ignored(relative):
                files.add(relative.as_posix())
    return files


def compare_installed_root(source: Path, ref: str, installed_root: Path) -> dict[str, object]:
    if not installed_root.exists():
        return {"path": installed_root.as_posix(), "status": "missing", "findings": []}

    findings: list[dict[str, str]] = []
    compared_skills: list[str] = []
    installed_skills = sorted(path.name for path in installed_root.iterdir() if path.is_dir() and path.name in KNOWN_SKILL_DIRS)
    if not installed_skills:
        return {"path": installed_root.as_posix(), "status": "unknown", "findings": [{"path": "", "message": "No installed CodeStable skill directories found."}]}

    for skill in installed_skills:
        repo_files = source_files(source, ref, skill)
        if not repo_files:
            findings.append({"path": skill, "message": "Installed skill is not present in the source reference."})
            continue
        compared_skills.append(skill)
        local_files = installed_files(installed_root, skill)
        for path in sorted(repo_files):
            expected = show_file(source, ref, path)
            local_path = installed_root / path
            if expected is None:
                continue
            if not local_path.exists():
                findings.append({"path": path, "message": "Installed file is missing."})
            elif local_path.read_bytes() != expected:
                findings.append({"path": path, "message": "Installed file differs from latest CodeStable source."})
        for path in sorted(local_files - repo_files):
            findings.append({"path": path, "message": "Installed file no longer exists in latest CodeStable source."})

    return {
        "path": installed_root.as_posix(),
        "status": "stale" if findings else "current",
        "compared_skills": compared_skills,
        "findings": findings,
    }


def check_freshness(
    source_root: str | None = None,
    installed_roots: list[str] | None = None,
    remote: str = "origin",
    branch: str = "main",
    explicit_ref: str | None = None,
    fetch: bool = True,
    cwd: Path | None = None,
) -> dict[str, object]:
    cwd = (cwd or Path.cwd()).resolve()
    source = locate_source_root(source_root, cwd)
    if source is None:
        return {
            "ok": True,
            "status": "unknown",
            "should_prompt_update": False,
            "summary": "CodeStable source checkout was not found; freshness could not be verified.",
            "source_root": None,
            "installed_roots": [],
        }

    ref, head = resolve_latest_ref(source, remote, branch, explicit_ref, fetch)
    if not ref or not head:
        return {
            "ok": True,
            "status": "unknown",
            "should_prompt_update": False,
            "summary": f"Could not resolve latest CodeStable source ref {remote}/{branch}.",
            "source_root": source.as_posix(),
            "installed_roots": [],
        }

    roots = [Path(value).expanduser().resolve() for value in installed_roots] if installed_roots else default_installed_roots()
    if not roots:
        return {
            "ok": True,
            "status": "unknown",
            "should_prompt_update": False,
            "summary": "No installed CodeStable skill roots were found.",
            "source_root": source.as_posix(),
            "source_ref": ref,
            "source_head": head,
            "installed_roots": [],
        }

    root_results = [compare_installed_root(source, ref, root) for root in roots]
    stale = [item for item in root_results if item.get("status") == "stale"]
    unknown = [item for item in root_results if item.get("status") == "unknown"]
    if stale:
        status = "stale"
        summary = "Installed CodeStable skill copies differ from latest source."
    elif unknown and len(unknown) == len(root_results):
        status = "unknown"
        summary = "Installed CodeStable skill roots could not be compared."
    else:
        status = "current"
        summary = "Installed CodeStable skill copies match latest source."

    update_commands = [
        (
            "python3 codestable-maintainer/tools/verify.py "
            f"--repo {source.as_posix()} --branch {branch} --remote {remote} "
            f"--installed-root {item['path']} --sync-installed --json"
        )
        for item in stale
    ]
    return {
        "ok": status != "stale",
        "status": status,
        "should_prompt_update": status == "stale",
        "summary": summary,
        "source_root": source.as_posix(),
        "source_ref": ref,
        "source_head": head,
        "installed_roots": root_results,
        "update_commands": update_commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default=None, help="CodeStable source checkout. Defaults to CODESTABLE_SOURCE_ROOT or common paths.")
    parser.add_argument("--installed-root", action="append", help="Installed skills root. Repeatable. Defaults to ~/.agents/skills and ~/.codex/skills if present.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--ref", default=None, help="Compare against an explicit local git ref instead of remote/branch.")
    parser.add_argument("--no-fetch", action="store_true", help="Do not fetch remote/branch before comparing.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = check_freshness(
        source_root=args.source_root,
        installed_roots=args.installed_root,
        remote=args.remote,
        branch=args.branch,
        explicit_ref=args.ref,
        fetch=not args.no_fetch,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"CodeStable freshness: {payload['status']}")
        print(payload["summary"])
        if payload.get("should_prompt_update"):
            print("Update recommended before continuing:")
            for command in payload.get("update_commands", []):
                print(f"- {command}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
