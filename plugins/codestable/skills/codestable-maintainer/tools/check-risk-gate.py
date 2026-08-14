#!/usr/bin/env python3
"""Verify the fast lanes carry a real risk-escalation gate.

The three fast lanes (`cs-feat-ff`, `cs-refactor-ff`, `cs-issue-fix`) gate on
volume/scope. Volume is not a risk proxy, so each lane must also carry a risk
gate wired to `assurance.md`.

This checks *structure*: the gate section is sliced by its own heading and ends
at the next structural boundary, and every required element must appear inside
that slice. A whole-file substring probe passes on a decoy comment carrying the
keywords and fails on a harmless rewording — both error directions at once.

Two rules keep the slice honest:

- **Never fail open.** If the terminator cannot be located the section is
  reported missing, not widened to the rest of the file. A silently widened
  slice degrades into exactly the whole-file probe this replaces.
- **Boundaries are structural, not literal.** The slice ends at the next heading
  or the next ordered-list item outside a fenced block, so ordinary edits
  (renumbering a list, adding a fenced example) cannot move it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]

# One keyword per risk row in assurance.md, in row order. Membership proves the
# categories survive; order proves the lane still mirrors the canon row-for-row,
# which is what each lane's 逐行对应 claim asserts.
RISK_KEYWORDS = ("取舍", "契约", "权限", "schema", "并发", "副作用", "性能", "传播")

BOUNDARY = re.compile(r"^(?:#{2,4}\s|\s*\d+\.\s|---\s*$)")
FENCE = re.compile(r"^\s*```")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

LANES = {
    "cs-feat-ff": ("cs-feat-ff/SKILL.md", "### 风险升级"),
    "cs-refactor-ff": ("cs-refactor-ff/SKILL.md", "### 第 4 条：风险核对"),
    "cs-issue-fix": ("cs-issue-fix/SKILL.md", "**风险核对（静默）**"),
}

# "Stay in the lane" is only safe while a scale signal still forces fallback.
# That carve-out lives in the fallback section, not the gate, so requiring the
# bare 不切回 token inside the gate would accept the rule without its bound.
SCOPE_SECTIONS = {
    "cs-feat-ff": ("## 什么时候跳出 fastforward", ("规模", "风险")),
    "cs-refactor-ff": ("## 什么时候跳出 fastforward", ("规模信号", "以规模信号为准")),
}

# cs-feat-ff also carries economy.md's counterweight; losing it leaves the lane
# telling the agent to write less with nothing saying what must never be cut.
COUNTERWEIGHT_HEADING = "### 默认写最少的代码"
COUNTERWEIGHT_ELEMENTS = (
    "用户明确要求",
    "信任边界",
    "权限",
    "数据丢失",
    "可访问性",
    "护栏",
    "验证证据",
    "economy.md",
)


def slice_section(text: str, heading: str) -> str | None:
    """Text from `heading` to the next structural boundary, or None if unslicable.

    Returns None when the heading is absent, appears more than once (an ambiguous
    slice), or has no following boundary — never a widened fallback.
    """
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if heading in ln]
    if len(starts) != 1:
        return None
    start = starts[0]

    in_fence = False
    for i in range(start + 1, len(lines)):
        if FENCE.match(lines[i]):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if BOUNDARY.match(lines[i]):
            body = "\n".join(lines[start:i])
            # Commented-out text is not instruction the agent reads, so it must
            # not satisfy any requirement. Without this a decoy comment carrying
            # every token passes every token check.
            return HTML_COMMENT.sub(" ", body)
    return None


ENUMERATION_ANCHOR = "逐行对应"


def enumeration(section: str) -> str:
    """The category list itself, excluding the narrative lead-in.

    The lead-in legitimately mentions 权限 / 并发 as examples, so measuring
    membership or order across the whole section would grade prose rather than
    the list. All three lanes anchor the list on the 逐行对应 claim.
    """
    i = section.find(ENUMERATION_ANCHOR)
    return section[i:] if i >= 0 else ""


def ordered(text: str, keywords: tuple[str, ...]) -> bool:
    positions = [text.find(k) for k in keywords]
    return all(p >= 0 for p in positions) and positions == sorted(positions)


def scope_ok(skills_root: Path, lane: str) -> bool:
    """Lanes that may stay in-lane on a risk hit must still let scale force fallback."""
    spec = SCOPE_SECTIONS.get(lane)
    if spec is None:
        return True
    heading, tokens = spec
    section = slice_section((skills_root / LANES[lane][0]).read_text(encoding="utf-8"), heading)
    return section is not None and all(tok in section for tok in tokens)


def check_lane(skills_root: Path, lane: str) -> dict[str, object]:
    relpath, heading = LANES[lane]
    path = skills_root / relpath
    base = {
        "missing_categories": list(RISK_KEYWORDS),
        "categories_present": 0,
        "categories_expected": len(RISK_KEYWORDS),
        "categories_in_canon_order": False,
        "cites_assurance": False,
        "takes_full_row": False,
        "clarifies_jiashen": False,
        "stays_in_lane": False,
        "records_miss": False,
        "scopes_stay_in_lane": False,
        "ok": False,
    }
    if not path.is_file():
        return {**base, "reason": f"missing {relpath}"}

    section = slice_section(path.read_text(encoding="utf-8"), heading)
    if section is None:
        return {**base, "reason": f"gate section under {heading!r} is missing, duplicated, or unbounded"}

    listing = enumeration(section)
    if not listing:
        return {**base, "reason": f"gate section has no {ENUMERATION_ANCHOR!r} category list"}

    missing = [kw for kw in RISK_KEYWORDS if kw not in listing]
    result = {
        **base,
        "missing_categories": missing,
        "categories_present": len(RISK_KEYWORDS) - len(missing),
        "categories_in_canon_order": ordered(listing, RISK_KEYWORDS),
        "cites_assurance": "assurance.md" in section,
        # Structural marker for "take the whole compound cell", not one phrasing.
        "takes_full_row": bool(re.search(r"每一?项都要做", section)),
        # The floor review must not be able to absorb 加审.
        "clarifies_jiashen": "加审" in section and "之外" in section,
        "stays_in_lane": "不切回" in section or "不因此升级回标准路径" in section,
        # A silent check with no output is skippable; the miss marker makes it observable.
        "records_miss": "无命中" in section,
        "scopes_stay_in_lane": scope_ok(skills_root, lane),
    }
    result["ok"] = (
        not missing
        and result["categories_in_canon_order"]
        and result["cites_assurance"]
        and result["takes_full_row"]
        and result["clarifies_jiashen"]
        and result["stays_in_lane"]
        and result["records_miss"]
        and result["scopes_stay_in_lane"]
    )
    if not result["ok"]:
        result["reason"] = "gate present but incomplete"
    return result


def check_counterweight(skills_root: Path) -> dict[str, object]:
    path = skills_root / LANES["cs-feat-ff"][0]
    if not path.is_file():
        return {"ok": False, "reason": "missing cs-feat-ff/SKILL.md", "missing": list(COUNTERWEIGHT_ELEMENTS)}
    section = slice_section(path.read_text(encoding="utf-8"), COUNTERWEIGHT_HEADING)
    if section is None:
        return {"ok": False, "reason": "counterweight section missing or unbounded", "missing": list(COUNTERWEIGHT_ELEMENTS)}
    missing = [e for e in COUNTERWEIGHT_ELEMENTS if e not in section]
    return {"ok": not missing, "missing": missing}


def check(skills_root: Path) -> dict[str, object]:
    lanes = {lane: check_lane(skills_root, lane) for lane in LANES}
    counterweight = check_counterweight(skills_root)
    return {
        "ok": all(v["ok"] for v in lanes.values()) and counterweight["ok"],
        "lanes": lanes,
        "counterweight": counterweight,
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
        for lane, result in sorted(payload["lanes"].items()):
            print(f"{lane}: {'ok' if result['ok'] else 'FAIL ' + str(result.get('reason', ''))}")
        cw = payload["counterweight"]
        print(f"counterweight: {'ok' if cw['ok'] else 'FAIL ' + str(cw.get('missing'))}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
