#!/usr/bin/env python3
"""Verify the fast lanes carry a real risk-escalation gate.

The three fast lanes (`cs-feat-ff`, `cs-refactor-ff`, `cs-issue-fix`) gate on
volume/scope. Volume is not a risk proxy, so each lane must also carry a risk
gate wired to `assurance.md`.

This checks *structure*, not phrasing: the gate section must exist, must name
every risk category from the canon, and must state that the whole matching row
of safeguards applies. A substring probe over the whole file would pass on a
decoy comment and fail on a harmless rewording; scoping to the section and
requiring the full category set avoids both.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]

# One keyword per risk row in assurance.md. Each must appear inside the gate
# section, so deleting the category list fails even if the heading survives.
RISK_KEYWORDS = ("取舍", "契约", "权限", "schema", "并发", "副作用", "性能", "传播")

# lane -> (relative SKILL.md, gate heading, section terminator)
LANES = {
    "cs-feat-ff": ("cs-feat-ff/SKILL.md", "### 风险升级", "\n---"),
    "cs-refactor-ff": ("cs-refactor-ff/SKILL.md", "### 第 4 条：风险核对", "\n---"),
    "cs-issue-fix": ("cs-issue-fix/SKILL.md", "**风险核对（静默）**", "\n6."),
}


def gate_section(text: str, heading: str, stop: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    end = text.find(stop, start + len(heading))
    return text[start : end if end > 0 else len(text)]


def check_lane(skills_root: Path, lane: str) -> dict[str, object]:
    relpath, heading, stop = LANES[lane]
    path = skills_root / relpath
    if not path.is_file():
        return {"ok": False, "reason": f"missing {relpath}"}

    section = gate_section(path.read_text(encoding="utf-8"), heading, stop)
    if not section:
        return {"ok": False, "reason": f"no gate section under {heading!r}"}

    missing = [kw for kw in RISK_KEYWORDS if kw not in section]
    result = {
        "categories_present": len(RISK_KEYWORDS) - len(missing),
        "categories_expected": len(RISK_KEYWORDS),
        "missing_categories": missing,
        # The gate must point at the canon rather than restate safeguards.
        "cites_assurance": "assurance.md" in section,
        # It must take the whole matching row, not one item from a compound cell.
        "takes_full_row": "全部保障" in section,
        # And it must stay in the lane rather than fall back to the full flow.
        "stays_in_lane": "不切回" in section or "不因此升级回标准路径" in section,
    }
    result["ok"] = (
        not missing
        and result["cites_assurance"]
        and result["takes_full_row"]
        and result["stays_in_lane"]
    )
    if not result["ok"] and "reason" not in result:
        result["reason"] = "gate present but incomplete"
    return result


def check(skills_root: Path) -> dict[str, object]:
    lanes = {lane: check_lane(skills_root, lane) for lane in LANES}
    return {"ok": all(v["ok"] for v in lanes.values()), "lanes": lanes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", default=str(SKILLS_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = check(Path(args.skills_root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        for lane, result in sorted(payload["lanes"].items()):
            status = "ok" if result["ok"] else f"FAIL ({result.get('reason', '')})"
            print(f"{lane}: {status}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
