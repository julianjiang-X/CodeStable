"""Regression coverage for resolved records without silencing fresh blockers."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/codestable/skills/cs-onboard/tools"))
from codestable_common import scan_backlog


def write_record(root, text, name="approval-report.md"):
    path = root / ".codestable/features/2026-07-06-demo" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


METADATA = "---\nstatus: approved\nreason: review-authorization\nanswered_at: 2026-07-06\n---\n"
POLICY = "## Decision Needed\nThe owner authorized subagent review, with human review required only for serious issues.\n"


def test_answered_policy_keeps_actual_new_blockers(tmp_path):
    write_record(tmp_path, METADATA + POLICY + "Human review required for the newly discovered defect.\nFollow-up: must fix before merge.\nstatus: needs-human-review\n")
    assert [x.kind for x in scan_backlog(tmp_path)] == ["human-review", "follow-up", "needs-human-review"]


@pytest.mark.parametrize("metadata", ["", METADATA.replace("approved", "pending"), METADATA.replace("answered_at: 2026-07-06\n", ""), METADATA.replace("review-authorization", "design-approval"), METADATA.replace("2026-07-06", "null")])
def test_unanswered_or_other_approval_does_not_suppress_review(tmp_path, metadata):
    write_record(tmp_path, metadata + POLICY)
    assert [x.kind for x in scan_backlog(tmp_path)] == ["human-review"]


def test_body_fields_cannot_impersonate_answered_frontmatter(tmp_path):
    write_record(tmp_path, METADATA.strip("-\n") + "\n" + POLICY)
    assert [x.kind for x in scan_backlog(tmp_path)] == ["human-review"]


def test_other_files_and_same_line_unconditional_review_are_not_hidden(tmp_path):
    write_record(tmp_path, METADATA + POLICY, "demo-review.md")
    write_record(tmp_path, METADATA + POLICY.rstrip() + " Human review required now.\n")
    assert [x.kind for x in scan_backlog(tmp_path)] == ["human-review", "human-review"]


def test_applied_heading_keeps_following_open_work(tmp_path):
    write_record(tmp_path, "Follow-up applied:\n- The test was narrowed.\nFollow-up: must review the remaining defect.\nFollow-up applied: must still verify before merge.\n", "demo-review.md")
    items = scan_backlog(tmp_path)
    assert len(items) == 2
    assert all("must" in x.text for x in items)


def test_checked_candidates_and_followups_are_resolved(tmp_path):
    write_record(tmp_path, "## attention.md candidates\n- [x] Recorded policy.\n- [X] Recorded command.\n- [ ] Decide remaining policy.\n- Unchecked candidate.\n## Follow-Ups\n- [x] Must fix before merge.\n- [ ] Must review before merge.\n- Optional next step.\n", "demo-acceptance.md")
    items = scan_backlog(tmp_path)
    assert [(x.kind, x.text) for x in items] == [
        ("attention-candidate", "[ ] Decide remaining policy."),
        ("attention-candidate", "Unchecked candidate."),
        ("follow-up", "[ ] Must review before merge."),
        ("follow-up", "Optional next step."),
    ]


def test_conditional_policy_outside_historical_section_is_visible(tmp_path):
    write_record(tmp_path, METADATA + POLICY + "## Current issue\nHuman review required only for this defect.\n")
    assert [x.kind for x in scan_backlog(tmp_path)] == ["human-review"]
