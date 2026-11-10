"""Tools must cope with closed units.

Since 3.0.0 a finished task graduates its content and then deletes its work
directory (shared-conventions.md, section 3). The gates, doctor, backlog and inbox
must not mistake the deleted directory for missing work.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import ONBOARD_TOOLS as TOOLS_DIR  # noqa: E402

sys.path.insert(0, str(TOOLS_DIR))


def load_tool(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, TOOLS_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


common = load_tool("codestable_common_for_closed_units", "codestable_common.py")
gate = load_tool("codestable_worktree_gate_for_closed_units", "codestable-worktree-gate.py")
doctor = load_tool("codestable_doctor_for_closed_units", "codestable-doctor.py")
finish_gate = load_tool("codestable_finish_for_closed_units", "codestable-finish-worktree.py")
inbox_tool = load_tool("codestable_inbox_for_closed_units", "codestable-worktree-inbox.py")
backlog_tool = load_tool("codestable_backlog_for_closed_units", "codestable-backlog.py")
review_gate = load_tool("validate_review_for_closed_units", "validate-implementation-review.py")

UNIT = ".codestable/features/2026-06-03-demo"


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    run(repo, "add", "README.md")
    run(repo, "commit", "-m", "init")
    return repo


def commit_unit(repo: Path, with_review: bool, finished: bool = True) -> Path:
    """A committed unit: finished (all steps done) or still a plain design,
    with or without review evidence."""
    unit = repo / UNIT
    unit.mkdir(parents=True)
    (unit / "demo-design.md").write_text("design\n", encoding="utf-8")
    if finished:
        (unit / "demo-checklist.yaml").write_text("steps:\n  - id: one\n    status: done\n", encoding="utf-8")
    if with_review:
        (unit / "demo-implementation-review.md").write_text(
            "reviewer: subagent\nfindings: none\n", encoding="utf-8"
        )
    (unit / "worktree-override.md").write_text("reason: test\nscope: demo\napproval: approved\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "add unit")
    return unit


def close_unit(repo: Path, commit: bool) -> None:
    run(repo, "rm", "-r", "-q", UNIT)
    if commit:
        run(repo, "commit", "-m", "close demo: delete work directory")


def test_unit_was_removed_distinguishes_closed_from_never_existed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    unit = Path(UNIT)

    assert common.unit_was_removed(repo, unit) is False  # still on disk

    close_unit(repo, commit=False)  # deletion staged only: HEAD still has the files
    assert common.unit_was_removed(repo, unit) is True

    run(repo, "commit", "-m", "close")  # deletion committed: found in history
    assert common.unit_was_removed(repo, unit) is True
    assert common.unit_was_removed(repo, Path(".codestable/features/2026-01-01-never")) is False


def test_doctor_does_not_judge_a_deletion_that_is_already_history(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    assert doctor.diagnose(repo)["status"] == "blocked"  # control: the live unit lacks review

    close_unit(repo, commit=True)  # the gates, not the doctor, judge a deletion
    report = doctor.diagnose(repo)

    assert report["status"] != "blocked", report["findings"]
    assert report["active_units"] == []
    assert report["findings"] == []


def test_doctor_blocks_a_pending_deletion_of_an_unreviewed_unit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    close_unit(repo, commit=False)

    report = doctor.diagnose(repo)

    assert report["status"] == "blocked"
    assert any("no implementation review evidence" in f["message"] for f in report["findings"])


def test_doctor_accepts_a_pending_deletion_of_a_reviewed_unit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    close_unit(repo, commit=False)

    report = doctor.diagnose(repo)

    assert report["status"] != "blocked", report["findings"]
    assert report["findings"] == []


def test_doctor_ignores_the_baseline_of_a_closed_unit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    assert gate.start_gate(repo, UNIT)["ok"]
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")
    run(repo, "commit", "-m", "implement on main")
    assert doctor.diagnose(repo)["status"] == "blocked"  # control: baseline guard fires

    close_unit(repo, commit=True)
    report = doctor.diagnose(repo)

    assert report["post_baseline_blocks"] == []
    assert report["status"] == "idle"


def test_commit_gate_passes_for_a_closed_unit_and_still_checks_the_branch(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    close_unit(repo, commit=False)

    payload = gate.commit_gate(repo, UNIT)

    assert payload["ok"], payload["findings"]
    assert payload["unit_removed"] is True
    assert payload["required_review"] is None

    # Closing does not switch the branch guard off.
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")
    blocked = gate.commit_gate(repo, UNIT)
    assert not blocked["ok"]
    assert "default branch" in blocked["findings"][0]["message"]


def test_commit_gate_still_rejects_a_unit_that_never_existed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()

    with pytest.raises(ValueError, match="unit not found"):
        gate.commit_gate(repo, ".codestable/features/2026-01-01-never")


def test_start_and_finish_refuse_a_closed_unit_with_a_clear_message(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    close_unit(repo, commit=True)

    with pytest.raises(ValueError, match="closed and its work directory deleted"):
        gate.start_gate(repo, UNIT)
    with pytest.raises(ValueError, match="closed and its work directory deleted"):
        finish_gate.finish(repo, UNIT, ["pytest -> passed"])


def _validate_deletion(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CODESTABLE_ALLOW_MAIN_CHECKOUT_IMPLEMENTATION", "1")
    return review_gate.validate(repo)


def test_deleting_a_unit_with_review_evidence_in_head_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    close_unit(repo, commit=False)

    ok, findings, meta = _validate_deletion(repo, monkeypatch)

    assert ok, findings
    assert UNIT in meta["touched_units"]


def test_deleting_an_unreviewed_finished_unit_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    close_unit(repo, commit=False)

    ok, findings, _meta = _validate_deletion(repo, monkeypatch)

    assert not ok
    assert "no implementation review evidence" in findings[0].message
    assert findings[0].path.endswith("demo-implementation-review.md")


def test_deleting_a_unit_whose_review_is_not_a_subagent_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    (repo / UNIT / "demo-implementation-review.md").write_text("reviewer: self\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "self review")
    close_unit(repo, commit=False)

    ok, findings, _meta = _validate_deletion(repo, monkeypatch)

    assert not ok
    assert "reviewer: subagent" in findings[0].message


def test_deleting_a_unit_together_with_code_fails_even_with_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    close_unit(repo, commit=False)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")

    ok, findings, _meta = _validate_deletion(repo, monkeypatch)

    assert not ok
    assert any("own commit" in f.message and f.path == "src/app.py" for f in findings)


def test_deleting_a_unit_that_needed_no_review_is_free(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False, finished=False)  # a design that never reached implementation
    close_unit(repo, commit=False)

    ok, findings, _meta = _validate_deletion(repo, monkeypatch)

    assert ok, findings


def test_deleting_a_canceled_unit_needs_no_review(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    (repo / UNIT / "demo-acceptance.md").write_text("status: canceled\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "cancel")
    close_unit(repo, commit=False)

    ok, findings, _meta = _validate_deletion(repo, monkeypatch)

    assert ok, findings


def test_commit_gate_applies_the_same_deletion_rules(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=False)
    close_unit(repo, commit=False)
    missing = gate.commit_gate(repo, UNIT)
    assert not missing["ok"]
    assert any("no implementation review evidence" in f["message"] for f in missing["findings"])

    run(repo, "reset", "-q", "--hard", "HEAD")
    (repo / UNIT / "demo-implementation-review.md").write_text("reviewer: subagent\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "review")
    run(repo, "switch", "-c", "codex/demo")
    close_unit(repo, commit=False)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")
    mixed = gate.commit_gate(repo, UNIT)
    assert not mixed["ok"]
    assert any("own commit" in f["message"] for f in mixed["findings"])

    run(repo, "rm", "-q", "--cached", "src/app.py")
    clean = gate.commit_gate(repo, UNIT)
    assert clean["ok"], clean["findings"]


def _commit_goal(repo: Path, status: str) -> str:
    goal = ".codestable/goals/2026-06-03-demo"
    (repo / goal).mkdir(parents=True)
    (repo / goal / "state.yaml").write_text(f"schema_version: 1\ngoal: demo\nstatus: {status}\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "goal")
    run(repo, "rm", "-r", "-q", goal)
    return goal


@pytest.mark.parametrize("status", ["active", "blocked"])
def test_deleting_an_unfinished_goal_directory_is_rejected(tmp_path: Path, status: str) -> None:
    repo = init_repo(tmp_path)
    goal = _commit_goal(repo, status)

    payload = gate.commit_gate(repo, goal)

    assert not payload["ok"]
    assert any(f"status: {status}" in f["message"] for f in payload["findings"])


def test_deleting_a_completed_goal_directory_passes(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    goal = _commit_goal(repo, "complete")

    payload = gate.commit_gate(repo, goal)

    assert payload["ok"], payload["findings"]


def _ready_branch(tmp_path: Path) -> tuple[Path, Path, dict[str, object]]:
    repo = init_repo(tmp_path)
    commit_unit(repo, with_review=True)
    worktree = tmp_path / "repo-worktree"
    run(repo, "worktree", "add", "-b", "codex/demo", worktree.as_posix())
    (worktree / "src").mkdir()
    (worktree / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(worktree, "add", "src/app.py")
    run(worktree, "commit", "-m", "implement demo")
    payload = finish_gate.finish(worktree, UNIT, ["pytest -> passed"])
    assert payload["ok"], payload
    run(worktree, "add", payload["learning_report"], payload["context_check"], payload["merge_readiness"])
    run(worktree, "commit", "-m", "add finish artifacts")
    return repo, worktree, payload


def test_inbox_keeps_a_finished_branch_ready_after_the_closing_deletion(tmp_path: Path) -> None:
    repo, worktree, _payload = _ready_branch(tmp_path)
    run(worktree, "rm", "-r", "-q", UNIT)
    run(worktree, "commit", "-m", "close demo: delete work directory")

    inbox = inbox_tool.inbox(repo)

    assert inbox["stale_reports"] == []
    assert inbox["ready_to_merge"][0]["branch"] == "codex/demo"
    assert "non-implementation .codestable changes" in inbox["ready_to_merge"][0]["reasons"][0]


def test_inbox_still_flags_other_changes_made_alongside_the_closing_deletion(tmp_path: Path) -> None:
    repo, worktree, _payload = _ready_branch(tmp_path)
    run(worktree, "rm", "-r", "-q", UNIT)
    (worktree / "src/app.py").write_text("print('changed after the report')\n", encoding="utf-8")
    run(worktree, "add", "src/app.py")
    run(worktree, "commit", "-m", "close demo and sneak in a change")

    inbox = inbox_tool.inbox(repo)

    assert inbox["stale_reports"][0]["status"] == "stale-report"


def test_inbox_accepts_graduated_docs_edited_with_the_closing_deletion(tmp_path: Path) -> None:
    repo, worktree, _payload = _ready_branch(tmp_path)
    (worktree / ".codestable/requirements").mkdir(parents=True)
    (worktree / ".codestable/requirements/x.md").write_text("graduated capability\n", encoding="utf-8")
    (worktree / ".codestable/attention.md").write_text("- a graduated constraint\n", encoding="utf-8")
    run(worktree, "add", ".codestable/requirements/x.md", ".codestable/attention.md")
    run(worktree, "rm", "-r", "-q", UNIT)
    run(worktree, "commit", "-m", "close demo: graduate and delete")

    inbox = inbox_tool.inbox(repo)

    assert inbox["stale_reports"] == []
    assert inbox["ready_to_merge"][0]["branch"] == "codex/demo"
