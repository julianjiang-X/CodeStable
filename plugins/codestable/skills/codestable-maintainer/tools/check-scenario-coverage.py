#!/usr/bin/env python3
"""Report which scenarios carry CI-effective coverage of their own.

Under the scripted actors used in CI, `run_scripted_actor` replays the scenario's
own `say` strings, so `transcript` and `trajectory` are graded against text the
same file authored. Only `commands`, `artifacts` and `git` observe the repository.

That creates a specific blind spot: a scenario can look substantial, pass, and
still assert nothing its siblings do not already assert — so deleting the thing
it is named for stays green. This happened: `fast-path-minimization-keeps-guards`
was rewritten to call a shared checker with the same assertions as two sibling
scenarios, and deleting the entire economy counterweight left all three passing.

A scenario has **unique CI coverage** when at least one of its command assertions
(keyed by fixture, since the same assertion under a different repo state is a
genuinely different test) is asserted by no other scenario.

Scenarios without it are not necessarily wrong — they are behavioral
specifications for `--actor live-codex`, which is their real job. But they must
not be mistaken for CI regression coverage, and a *new* scenario that lands in
this state is almost always an authoring mistake.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = "codestable-maintainer/scenarios/critical"
DEFAULT_FIXTURE = "clean-onboarded-repo"

# Scenarios that predate this check and duplicate a sibling's CI assertions.
# They remain valid live-codex specifications. This list is a ratchet: it may
# shrink, never grow. A new name here means a new scenario shipped without CI
# coverage of its own.
LEGACY_WITHOUT_UNIQUE_COVERAGE = frozenset(
    {
        "accept-analyze-spec-drift",
        "compacted-worktree-start-gate",
        "cs-route-brief-minimal",
        "feat-design-clarify",
        "finish-inbox-cross-branch-report",
        "finish-inbox-ready",
        "global-interview-mode-routes-lightly",
        "long-context-noise-routing",
        "realistic-spec-no-free-rewrite",
        "spec-no-free-rewrite",
        "worktree-start-gate-main-stop",
    }
)


def assertion_signatures(scenario: dict[str, object]) -> set[tuple[str, ...]]:
    fixture = str(scenario.get("fixture") or DEFAULT_FIXTURE)
    expect = scenario.get("expect") or {}
    signatures: set[tuple[str, ...]] = set()

    for command in expect.get("commands", []) or []:
        cmd = " ".join(command.get("cmd", []))
        # exit_code is an assertion in its own right: two scenarios asserting
        # opposite exit codes on one command are not duplicates.
        if "exit_code" in command:
            signatures.add((fixture, cmd, "exit_code", json.dumps(command["exit_code"])))
        for check in command.get("json", []) or []:
            # Serialise the whole check, not just `equals`; contains_item and
            # friends otherwise all collapse to the same "null" signature.
            predicate = json.dumps(
                {k: v for k, v in check.items() if k != "path"}, sort_keys=True, ensure_ascii=False
            )
            signatures.add((fixture, cmd, str(check.get("path")), predicate))

    artifacts = expect.get("artifacts") or {}
    for key in ("must_create", "must_not_create", "must_exist", "must_not_exist"):
        for path in artifacts.get(key, []) or []:
            signatures.add((fixture, "artifact", key, str(path)))
    for item in artifacts.get("contains", []) or []:
        signatures.add((fixture, "artifact", "contains", f"{item.get('path')}::{item.get('text')}"))

    # git assertions observe the repo too, so they count as CI-effective.
    for key, paths in (expect.get("git") or {}).items():
        for path in paths or []:
            signatures.add((fixture, "git", str(key), str(path)))

    return signatures


def check(skills_root: Path) -> dict[str, object]:
    directory = skills_root / SCENARIO_DIR
    if not directory.is_dir():
        return {"ok": False, "reason": f"missing {SCENARIO_DIR}", "scenarios": {}}

    signatures = {}
    for path in sorted(directory.glob("*.yaml")):
        signatures[path.stem] = assertion_signatures(json.loads(path.read_text(encoding="utf-8")))

    owners: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for name, sigs in signatures.items():
        for sig in sigs:
            owners[sig].append(name)

    scenarios: dict[str, object] = {}
    for name, sigs in sorted(signatures.items()):
        unique = [s for s in sigs if len(owners[s]) == 1]
        scenarios[name] = {
            "assertions": len(sigs),
            "unique": len(unique),
            "has_unique_ci_coverage": bool(unique),
            "grandfathered": name in LEGACY_WITHOUT_UNIQUE_COVERAGE,
        }

    regressions = sorted(
        name
        for name, r in scenarios.items()
        if not r["has_unique_ci_coverage"] and not r["grandfathered"]
    )
    # A name that gained coverage should leave the list rather than sit there stale.
    stale = sorted(
        name
        for name, r in scenarios.items()
        if r["has_unique_ci_coverage"] and r["grandfathered"]
    )

    return {
        "ok": not regressions and not stale,
        "regressions": regressions,
        "stale_allowlist_entries": stale,
        "scenarios": scenarios,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", default=str(SKILLS_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = check(Path(args.skills_root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        total = len(payload["scenarios"])
        covered = sum(1 for r in payload["scenarios"].values() if r["has_unique_ci_coverage"])
        print(f"{covered}/{total} scenarios carry unique CI coverage")
        for name in payload["regressions"]:
            print(f"  REGRESSION {name}: no CI assertion of its own")
        for name in payload["stale_allowlist_entries"]:
            print(f"  STALE ALLOWLIST {name}: now has unique coverage; remove it from the list")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
