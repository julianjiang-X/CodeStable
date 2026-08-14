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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sections import describe_failure, slice_section  # noqa: E402


SKILLS_ROOT = Path(__file__).resolve().parents[2]

# One keyword per risk row in assurance.md. Membership proves the categories
# survive; row-count parity against assurance.md (check_canon_parity) proves the
# set is still complete. Order is deliberately not checked — a permutation has no
# instructional consequence, so asserting it only produces false positives.
RISK_KEYWORDS = ("取舍", "契约", "权限", "schema", "并发", "副作用", "性能", "传播")

LANES = {
    "cs-feat-ff": ("cs-feat-ff/SKILL.md", "### 风险升级", False),
    "cs-refactor-ff": ("cs-refactor-ff/SKILL.md", "### 第 4 条：风险核对", False),
    # This gate is nested inside the fast-path numbered list.
    "cs-issue-fix": ("cs-issue-fix/SKILL.md", "**风险核对（静默）**", True),
}

# "Stay in the lane" is only safe while a scale signal still forces fallback.
# That carve-out lives in the fallback section, not the gate, so requiring the
# bare 不切回 token inside the gate would accept the rule without its bound.
SCOPE_SECTIONS = {
    # Must reach the trigger list itself. Pointing at the parent heading sliced
    # only the framing sentence, which names both tokens while the rule it
    # announces could be deleted wholesale.
    "cs-feat-ff": ("### 规模跳出", ("3 个以上子系统", "cs-feat-design")),
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


# N12: anchoring on a phrase like 逐行对应 just swaps one magic phrase for another —
# a descriptive connective is exactly what a prose cleanup rewrites. Anchor on the
# enumeration's own shape: the bullet run, or the `·`-separated run used inline.
BULLET = re.compile(r"^\s*[-*]\s+\S", re.MULTILINE)


def enumeration(section: str) -> str:
    """The category list itself, excluding the narrative lead-in.

    The lead-in legitimately names 权限 / 并发 as examples, so measuring membership
    or order across the whole section would grade prose rather than the list.
    """
    bullets = BULLET.findall(section)
    if len(bullets) >= 4:
        first = BULLET.search(section)
        return section[first.start():]
    # Inline form: the longest `·`-separated run, starting at the colon that
    # introduces it — the lead-in shares the line and legitimately names
    # 权限 / 并发 as examples.
    runs = [ln for ln in section.split("\n") if ln.count("·") >= 3]
    if not runs:
        return ""
    line = max(runs, key=len)
    head = line.rfind("：", 0, line.find("·"))
    return line[head + 1:] if head >= 0 else line


def scope_ok(skills_root: Path, lane: str) -> bool:
    """Lanes that may stay in-lane on a risk hit must still let scale force fallback.

    The carve-out lives in the fallback section, not the gate, so requiring the bare
    不切回 token inside the gate would accept the rule without its bound.
    """
    spec = SCOPE_SECTIONS.get(lane)
    if spec is None:
        return True
    heading, tokens = spec
    text = (skills_root / LANES[lane][0]).read_text(encoding="utf-8")
    section = slice_section(text, heading)
    return section is not None and all(tok in section for tok in tokens)


def check_lane(skills_root: Path, lane: str) -> dict[str, object]:
    relpath, heading, nested = LANES[lane]
    path = skills_root / relpath
    base = {
        "missing_categories": list(RISK_KEYWORDS),
        "categories_present": 0,
        "categories_expected": len(RISK_KEYWORDS),
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

    text = path.read_text(encoding="utf-8")
    section = slice_section(text, heading, stop_at_list_item=nested)
    if section is None:
        return {**base, "reason": describe_failure(text, heading)}

    listing = enumeration(section)
    if not listing:
        return {**base, "reason": "gate section has no recognisable category enumeration"}

    missing = [kw for kw in RISK_KEYWORDS if kw not in listing]
    result = {
        **base,
        "missing_categories": missing,
        "categories_present": len(RISK_KEYWORDS) - len(missing),
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


ASSURANCE = "cs-onboard/reference/assurance.md"
ASSURANCE_ROW = re.compile(r"^\| (?!风险事实|---)[^|]+\|[^|]+\|\s*$", re.MULTILINE)


def check_canon_parity(skills_root: Path) -> dict[str, object]:
    """The lanes claim to mirror assurance.md row for row; verify the count.

    Without this the canon can gain a row while every lane and every checker
    stays green, because RISK_KEYWORDS is a constant baked into this file.
    """
    path = skills_root / ASSURANCE
    if not path.is_file():
        return {"ok": False, "reason": f"missing {ASSURANCE}"}
    rows = len(ASSURANCE_ROW.findall(path.read_text(encoding="utf-8")))
    return {
        "ok": rows == len(RISK_KEYWORDS),
        "canon_rows": rows,
        "keywords": len(RISK_KEYWORDS),
        "reason": "" if rows == len(RISK_KEYWORDS)
        else f"assurance.md has {rows} risk rows but RISK_KEYWORDS has {len(RISK_KEYWORDS)}",
    }


def check(skills_root: Path) -> dict[str, object]:
    lanes = {lane: check_lane(skills_root, lane) for lane in LANES}
    counterweight = check_counterweight(skills_root)
    canon = check_canon_parity(skills_root)
    return {
        "ok": all(v["ok"] for v in lanes.values()) and counterweight["ok"] and canon["ok"],
        "lanes": lanes,
        "counterweight": counterweight,
        "canon_parity": canon,
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
        cp = payload["canon_parity"]
        print(f"canon parity: {'ok' if cp['ok'] else 'FAIL ' + cp.get('reason', '')}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
