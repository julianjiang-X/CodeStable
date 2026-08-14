#!/usr/bin/env python3
"""Verify the reviewer-lineage protocol in execution-conventions.md is intact.

Companion to check-risk-gate.py. Both share sections.py so the parsing is
hardened once; same reason: a substring
search over a whole file passes on a decoy comment carrying the keywords and
fails on a harmless rewording. Each protocol section is sliced by heading and
checked for the elements that section must carry.

The reviewer protocol is load-bearing — it bounds review rounds, forbids the
reviewer from spawning sub-agents, and defines what a re-review must report.
Losing any of it degrades silently, so it gets a mechanical guard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sections import describe_failure, slice_section  # noqa: E402


SKILLS_ROOT = Path(__file__).resolve().parents[2]
CONVENTIONS = "cs-onboard/reference/execution-conventions.md"

# section heading -> elements that section must contain
REQUIRED = {
    "### Freeze The Review Target": (
        "staged diff",
        "SHA-256",
        "void",
    ),
    "### Reviewer Lineage": (
        "fresh reviewer",
        "same session",
        # `resolved` is a substring of `unresolved`, so the three states are
        # matched as the backticked tokens the protocol actually specifies.
        "`resolved`",
        "`unresolved`",
        "`new findings`",
        "complete current candidate",
    ),
    "### Round Budget": (
        "3 rounds",
        "does not reset",
        "escalate to the owner",
    ),
    "### Reviewer Health": (
        "run identity",
        "bounded retry",
    ),
    "### Reviewer Is A Leaf": (
        "must not create, delegate to, or wake any sub-agent",
        "NeedsContext",
    ),
    "### When The Reviewer Returns No Report": (
        "transcript",
        "recovered report is a valid terminal report",
    ),
}

# A section that shrank to almost nothing is a decoy even if keywords survive.
MIN_SECTION_CHARS = 200


def check(skills_root: Path) -> dict[str, object]:
    path = skills_root / CONVENTIONS
    if not path.is_file():
        return {"ok": False, "reason": f"missing {CONVENTIONS}", "sections": {}}

    text = path.read_text(encoding="utf-8")
    sections: dict[str, object] = {}
    for heading, elements in REQUIRED.items():
        body = slice_section(text, heading)
        if body is None:
            sections[heading] = {
                "ok": False,
                "reason": describe_failure(text, heading),
                "missing": list(elements),
            }
            continue
        missing = [e for e in elements if e not in body]
        # Prose, not a stub or a comment that merely mentions the keywords.
        # Comments are already stripped by the shared slicer, so length here
        # measures real prose rather than a padded decoy.
        substantial = len(body) >= MIN_SECTION_CHARS
        sections[heading] = {
            "ok": not missing and substantial,
            "missing": missing,
            "chars": len(body),
            "substantial": substantial,
        }

    return {
        "ok": all(v["ok"] for v in sections.values()),
        "sections": sections,
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
        for heading, result in payload["sections"].items():
            status = "ok" if result["ok"] else f"FAIL {result.get('missing') or result.get('reason')}"
            print(f"{heading}: {status}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
