"""Shared markdown section slicing for the maintainer checkers.

Every checker that verifies "this rule still lives in this section" needs the
same parsing, and getting it wrong fails silently in the direction of passing.
This module exists because that already happened: `check-risk-gate.py` was
hardened across two rounds of adversarial review, and a sibling checker written
the same week reimplemented the naive version and inherited the fail-open it had
just removed.

The policies differ per checker. The parsing must not.

Invariants:

- **Never fail open.** An absent, duplicated, or unterminated heading returns
  `None`. A silently widened slice degrades into a whole-file substring probe,
  which passes on a decoy comment carrying the keywords and fails on a harmless
  rewording — both error directions at once.
- **Boundaries are structural.** The slice ends at the next heading, ordered-list
  item, or horizontal rule outside a fenced block, so renumbering a list or
  adding a fenced example cannot move it.
- **Commented-out text does not count.** An agent does not act on `<!-- ... -->`,
  so it must not satisfy a requirement either.
"""

from __future__ import annotations

import re


BOUNDARY = re.compile(r"^(?:#{1,6}\s|(?:---|\*\*\*|___)\s*$)")
# Only a boundary for sections that live *inside* a numbered list, where the
# next item ends them. Applying it everywhere truncates any section that
# legitimately contains a numbered list of its own.
LIST_ITEM = re.compile(r"^\s*\d+\.\s")
FENCE = re.compile(r"^\s*(?:```|~~~)")
# A heading may be the first content of a list item. Stripping the marker keeps
# the start-of-line anchor (so a mid-sentence cross-reference still cannot match)
# while allowing a nested heading.
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


class SectionError(Exception):
    """Why a section could not be sliced, for reporting rather than widening."""


def _heads(line: str, heading: str) -> bool:
    """True when `line` begins with `heading`, ignoring an enclosing list marker."""
    stripped = line.lstrip()
    return stripped.startswith(heading) or LIST_MARKER.sub("", line, count=1).startswith(heading)


def slice_section(
    text: str,
    heading: str,
    *,
    strip_comments: bool = True,
    stop_at_list_item: bool = False,
) -> str | None:
    """Return the body under `heading`, or None when it cannot be sliced safely.

    `heading` is matched at the start of a line so that cross-references to a
    section elsewhere in the document do not make the slice ambiguous.

    Set `stop_at_list_item` for a section nested inside a numbered list, where
    the next item is its real end.
    """
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if _heads(line, heading)]
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
        if BOUNDARY.match(lines[i]) or (stop_at_list_item and LIST_ITEM.match(lines[i])):
            body = "\n".join(lines[start:i])
            return HTML_COMMENT.sub(" ", body) if strip_comments else body
    return None


def describe_failure(text: str, heading: str) -> str:
    """Distinguish missing / duplicated / unterminated so the report is actionable."""
    occurrences = sum(1 for line in text.split("\n") if _heads(line, heading))
    if occurrences == 0:
        return f"section {heading!r} is missing"
    if occurrences > 1:
        return f"section {heading!r} appears {occurrences} times, so the slice is ambiguous"
    return f"section {heading!r} has no following boundary, so it cannot be bounded"
