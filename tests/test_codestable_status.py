"""codestable-status.py answers progress by looking: nothing is stored."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import ONBOARD_TOOLS as TOOLS_DIR  # noqa: E402
from test_codestable_closed_units import UNIT, _ready_branch, init_repo, run  # noqa: E402

sys.path.insert(0, str(TOOLS_DIR))
import codestable_common as common  # noqa: E402
SPEC = importlib.util.spec_from_file_location("codestable_status_for_tests", TOOLS_DIR / "codestable-status.py")
assert SPEC and SPEC.loader
status_tool = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = status_tool
SPEC.loader.exec_module(status_tool)

CHECKLIST = "steps:\n  - action: first slice\n    status: done\n  - action: second slice\n    status: pending\n"
ITEMS = (
    "items:\n  - slug: alpha\n    status: done\n  - slug: beta\n    status: in-progress\n"
    "  - slug: gamma\n    status: planned\n"
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_unit(base: Path, rel: str = "features/2026-07-01-alpha", checklist: bool = True) -> Path:
    unit = base / ".codestable" / rel
    write(unit / "alpha-design.md", "design\n")
    if checklist:
        write(unit / "alpha-checklist.yaml", CHECKLIST)
    return unit


def commit_all(repo: Path, message: str = "commit") -> None:
    run(repo, "add", "-A")
    run(repo, "commit", "-q", "-m", message)


def add_worktree(repo: Path, tmp_path: Path, branch: str, name: str = "wt") -> Path:
    worktree = tmp_path / name
    run(repo, "worktree", "add", "-b", branch, worktree.as_posix())
    return worktree


def test_repo_without_codestable_gives_empty_sections_and_a_note(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)

    result = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "codestable-status.py"), "--root", str(repo), "--json"],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["in_progress"] == payload["waiting"] == payload["recent"] == payload["next"] == []
    assert ".codestable/ not found" in payload["notes"][0]


def test_units_in_main_checkout_and_linked_worktree_are_in_progress(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_unit(repo)
    worktree = add_worktree(repo, tmp_path, "codex/beta")
    other = make_unit(worktree, "issues/2026-07-02-beta", checklist=False)
    write(other / "beta-report.md", "report\n")

    payload = status_tool.status(repo)

    by_unit = {e["unit"]: e for e in payload["in_progress"]}
    assert set(by_unit) == {"2026-07-01-alpha", "2026-07-02-beta"}
    assert by_unit["2026-07-01-alpha"]["pointer"] == (repo.resolve() / ".codestable/features/2026-07-01-alpha").as_posix()
    assert "implementation" in by_unit["2026-07-01-alpha"]["stage"]
    assert by_unit["2026-07-01-alpha"]["branches"] == ["main"]
    assert by_unit["2026-07-02-beta"]["branches"] == ["codex/beta"]
    assert by_unit["2026-07-02-beta"]["pointer"].startswith(worktree.resolve().as_posix())
    assert by_unit["2026-07-02-beta"]["stage"] == "report"
    assert unit.exists()  # read-only: nothing was written or deleted


def test_next_comes_from_roadmap_then_checklist_then_nothing(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()
    payload = status_tool.status(repo)
    assert payload["next"] == [] and "no next step" in payload["notes"][-1]

    make_unit(repo)
    fallback = status_tool.status(repo)["next"]
    assert [e["kind"] for e in fallback] == ["unit-step"] and fallback[0]["step"] == "second slice"

    write(repo / ".codestable/roadmap/demo/demo-items.yaml", ITEMS)
    with_roadmap = status_tool.status(repo)["next"]
    assert [(e["slug"], e["status"]) for e in with_roadmap] == [("beta", "in-progress"), ("gamma", "planned")]
    assert with_roadmap[0]["pointer"].endswith("demo-items.yaml")


def test_roadmap_items_survive_key_order_quotes_comments_and_notes_blocks() -> None:
    text = (
        "roadmap: demo\nitems:\n"
        "  - description: key order differs\n    slug: first\n    status: planned\n"
        "  - slug: second\n    status: \"planned\"   # quoted, with a comment\n"
        "  - slug: third\n    status: done\n    notes: |\n      status: planned\n      - slug: fake\n        status: planned\n"
        "  - slug: fourth\n    depends_on: [first]\n    status: 'in-progress'\n"
    )

    items = status_tool.roadmap_items(text)

    assert [(i["slug"], i["status"]) for i in items] == [
        ("first", "planned"), ("second", "planned"), ("third", "done"), ("fourth", "in-progress")]


def test_roadmap_template_in_cs_roadmap_reference_parses(tmp_path: Path) -> None:
    reference = (TOOLS_DIR.parent.parent / "cs-roadmap/reference.md").read_text(encoding="utf-8")
    block = reference.split("## 2. items.yaml 格式", 1)[1].split("```yaml", 1)[1].split("```", 1)[0]

    items = status_tool.roadmap_items(block)

    assert [(i["slug"], i["status"]) for i in items] == [
        ("permission-rbac-core", "planned"), ("permission-admin-ui", "planned")]


def test_only_undecided_approval_reports_are_waiting(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_unit(repo)
    write(unit / "approval-report.md", "---\ndoc_type: approval-report\nstatus: pending\nreason: route-choice\n---\n")
    decided = make_unit(repo, "issues/2026-07-02-done")
    write(decided / "approval-report.md", "---\ndoc_type: approval-report\nstatus: approved\n---\n")

    waiting = status_tool.status(repo)["waiting"]

    assert [(e["kind"], e["detail"]) for e in waiting] == [("approval-report", "route-choice")]
    assert waiting[0]["pointer"].endswith("2026-07-01-alpha/approval-report.md")


def test_the_same_approval_report_is_one_entry_and_decided_anywhere_means_decided(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_unit(repo)
    report = unit / "approval-report.md"
    write(report, "---\nstatus: pending\nreason: merge\n---\n")
    commit_all(repo)
    worktree = add_worktree(repo, tmp_path, "codex/alpha")

    waiting = status_tool.status(repo)["waiting"]
    assert len(waiting) == 1 and waiting[0]["branches"] == ["codex/alpha", "main"]

    wt_report = worktree / ".codestable/features/2026-07-01-alpha/approval-report.md"
    wt_report.write_text("---\nstatus: approved\nreason: merge\n---\n", encoding="utf-8")
    assert status_tool.status(repo)["waiting"] == []


def test_finished_but_unmerged_worktree_is_waiting_and_its_deleted_unit_is_not_in_progress(tmp_path: Path) -> None:
    repo, worktree, _payload = _ready_branch(tmp_path)
    run(worktree, "rm", "-r", "-q", UNIT)
    run(worktree, "commit", "-m", "close demo: delete work directory")

    payload = status_tool.status(repo)

    unmerged = [e for e in payload["waiting"] if e["kind"] == "unmerged-worktree"]
    assert [e["branches"] for e in unmerged] == [["codex/demo"]]
    assert "ready-to-merge" in unmerged[0]["detail"]
    assert [e for e in payload["in_progress"] if e["kind"] != "branch"] == []  # the deleted directory means closed


def test_recent_commits_follow_a_default_branch_that_is_not_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "trunk")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / ".codestable").mkdir()
    for i in range(12):
        (repo / "f.txt").write_text(str(i), encoding="utf-8")
        run(repo, "add", "f.txt")
        run(repo, "commit", "-m", f"change {i}")

    payload = status_tool.status(repo)

    assert payload["default_branch"] == "trunk"
    assert len(payload["recent"]) == 10
    assert payload["recent"][0]["subject"] == "change 11"
    assert payload["recent"][0]["pointer"] == payload["recent"][0]["commit"]


def test_default_branch_from_a_linked_worktree_is_the_main_checkouts_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "trunk")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / ".codestable").mkdir()
    (repo / "f.txt").write_text("base", encoding="utf-8")
    run(repo, "add", "f.txt")
    run(repo, "commit", "-m", "base commit")
    worktree = add_worktree(repo, tmp_path, "feat/q")
    (worktree / "f.txt").write_text("feature work", encoding="utf-8")
    run(worktree, "commit", "-a", "-m", "feature-only commit")
    (worktree / ".codestable").mkdir(exist_ok=True)

    assert status_tool.default_branch(worktree) == "trunk"
    payload = status_tool.status(worktree)

    assert payload["default_branch"] == "trunk"
    assert [c["subject"] for c in payload["recent"]] == ["base commit"]


def test_open_prs_are_opt_in_and_a_missing_gh_is_reported_not_raised(tmp_path: Path, monkeypatch) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()

    without = status_tool.status(repo)
    assert any("not queried" in line for line in without["not_checked"])

    monkeypatch.setattr(status_tool.shutil, "which", lambda _name: None)
    with_prs = status_tool.status(repo, with_prs=True)
    assert any("gh is not installed" in line for line in with_prs["not_checked"])
    assert with_prs["waiting"] == []


def test_open_prs_come_from_gh_when_asked(tmp_path: Path, monkeypatch) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "#!/bin/sh\necho '[{\"number\": 7, \"title\": \"Add x\", \"headRefName\": \"codex/x\", "
        "\"url\": \"https://example.test/pr/7\"}]'\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin:/bin")

    waiting = status_tool.status(repo, with_prs=True)["waiting"]

    assert [(e["kind"], e["pointer"]) for e in waiting] == [("open-pr", "https://example.test/pr/7")]


def _legacy_project(repo: Path) -> None:
    """Units a project onboarded before 3.0.0 still carries: finished or canceled, never deleted."""
    cs = repo / ".codestable"
    done_list = "steps:\n  - action: a\n    status: done\nchecks:\n  - item: b\n    status: passed\n"
    for i in range(3):
        write(cs / f"features/2026-01-0{i + 1}-old{i}/old{i}-acceptance.md", "accepted\n")
        write(cs / f"features/2026-01-0{i + 1}-old{i}/old{i}-checklist.yaml", done_list)
        write(cs / f"issues/2026-02-0{i + 1}-fixed{i}/fixed{i}-fix-note.md", "fixed\n")
    write(cs / "features/2026-03-01-ff/ff-ff-note.md", "ff done\n")
    write(cs / "refactors/2026-03-02-applied/applied-apply-notes.md", "applied\n")
    write(cs / "refactors/2026-03-03-dropped/dropped-apply-notes.md", "---\nstatus: canceled\n---\n")
    write(cs / "features/2026-03-04-dropped/dropped-acceptance.md", "---\nstatus: abandoned\n---\n")
    write(cs / "goals/2026-04-01-finished/state.yaml", "status: complete\n")
    write(cs / "goals/2026-04-02-gone/state.yaml", "status: canceled\n")


def test_legacy_records_unchanged_since_the_fork_are_counted_not_listed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _legacy_project(repo)
    commit_all(repo, "legacy records")
    make_unit(repo)  # the one live unit, not committed

    payload = status_tool.status(repo)

    assert [e["unit"] for e in payload["in_progress"]] == ["2026-07-01-alpha"]
    note = payload["notes"][0]
    assert note.startswith("12 finished or canceled work directories, unchanged since this branch forked from main")
    assert ".codestable/features (5)" in note and ".codestable/issues (3)" in note
    assert ".codestable/refactors (2)" in note and ".codestable/goals (2)" in note
    assert "codestable-doctor.py" in note
    assert "old0" not in note  # no per-unit listing


def test_the_same_legacy_feature_modified_in_a_worktree_is_listed_as_closing(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _legacy_project(repo)
    commit_all(repo, "legacy records")
    worktree = add_worktree(repo, tmp_path, "codex/old0")
    assert status_tool.status(repo)["in_progress"] == []  # unchanged everywhere: counted only

    write(worktree / ".codestable/features/2026-01-01-old0/old0-implementation-review.md", "reviewer: subagent\n")

    entries = status_tool.status(repo)["in_progress"]

    assert [e["unit"] for e in entries] == ["2026-01-01-old0"]
    assert entries[0]["stage"].startswith("closing: implementation done, review/closure pending")
    assert "subagent review evidence present" in entries[0]["stage"]
    assert entries[0]["branches"] == ["codex/old0", "main"]


def test_units_with_a_completion_marker_that_the_branch_created_are_closing_not_finished(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    cs = repo / ".codestable"
    write(cs / "features/2026-08-01-ffonly/ffonly-ff-note.md", "done\n")
    write(cs / "refactors/2026-08-02-human/human-apply-notes.md", "applied\n")
    write(cs / "refactors/2026-08-02-human/human-checklist.yaml",
          "steps:\n  - action: a\n    status: done\nchecks:\n  - item: human check\n    status: pending\n")
    write(cs / "refactors/2026-08-03-midway/midway-apply-notes.md", "step 1\n")
    write(cs / "refactors/2026-08-03-midway/midway-checklist.yaml",
          "steps:\n  - action: a\n    status: in_progress\n")

    entries = {e["unit"]: e for e in status_tool.status(repo)["in_progress"]}

    assert set(entries) == {"2026-08-01-ffonly", "2026-08-02-human", "2026-08-03-midway"}
    for entry in entries.values():
        assert entry["stage"].startswith("closing: implementation done, review/closure pending")
        assert "subagent review evidence absent" in entry["stage"]
    assert all("finished or canceled" not in n for n in status_tool.status(repo)["notes"])


def test_a_unit_seen_from_two_worktrees_is_one_entry_taken_from_the_furthest_copy(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_unit(repo)
    commit_all(repo, "add unit")
    worktree = add_worktree(repo, tmp_path, "codex/alpha")

    same = status_tool.status(repo)["in_progress"]
    assert len(same) == 1 and same[0]["branches"] == ["codex/alpha", "main"]
    assert same[0]["pointer"].startswith(repo.resolve().as_posix())  # tie: main checkout, listed first

    write(worktree / ".codestable/features/2026-07-01-alpha/alpha-implementation-review.md", "review\n")
    ahead = status_tool.status(repo)["in_progress"]

    assert len(ahead) == 1
    assert ahead[0]["branches"] == ["codex/alpha", "main"]
    assert ahead[0]["stage"].startswith("implementation review")
    assert ahead[0]["pointer"].startswith(worktree.resolve().as_posix())
    assert len(ahead[0]["pointers"]) == 2


def test_blocked_goals_say_so_in_the_stage(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    cs = repo / ".codestable"
    write(cs / "goals/2026-06-03-halted/state.yaml", "status: blocked\n")
    write(cs / "goals/2026-06-03-halted/goal.md", "goal\n")
    write(cs / "features/2026-06-04-fine/fine-design.md", "design\n")

    stages = {e["unit"]: e["stage"] for e in status_tool.status(repo)["in_progress"]}

    assert stages["2026-06-03-halted"] == "iterating (blocked)"
    assert stages["2026-06-04-fine"] == "design"


def test_directories_with_only_hidden_files_are_ignored(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo / ".codestable/features/2026-09-01-ghost/.DS_Store", "x")
    make_unit(repo)

    assert [e["unit"] for e in status_tool.status(repo)["in_progress"]] == ["2026-07-01-alpha"]


def test_work_without_a_directory_shows_up_as_branch_entries(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()
    ahead = add_worktree(repo, tmp_path, "codex/ahead", "wt-ahead")
    (ahead / "a.txt").write_text("a", encoding="utf-8")
    commit_all(ahead, "work without a directory")
    dirty = add_worktree(repo, tmp_path, "codex/dirty", "wt-dirty")
    (dirty / "README.md").write_text("edited\n", encoding="utf-8")
    run(repo, "branch", "codex/loose", "codex/ahead")  # a branch ahead of main with no worktree
    withunit = add_worktree(repo, tmp_path, "codex/unit", "wt-unit")
    make_unit(withunit)

    payload = status_tool.status(repo)

    branches = {e["unit"]: e for e in payload["in_progress"] if e["kind"] == "branch"}
    assert set(branches) == {"codex/ahead", "codex/dirty"}  # codex/unit is represented by its unit entry
    assert branches["codex/ahead"]["ahead"] == 1 and branches["codex/ahead"]["dirty"] is False
    assert branches["codex/dirty"]["ahead"] == 0 and branches["codex/dirty"]["dirty"] is True
    assert branches["codex/ahead"]["pointer"] == f"codex/ahead @ {ahead.resolve().as_posix()}"
    assert any(n == "1 local branches are ahead of main and have no worktree" for n in payload["notes"])
    assert [e["unit"] for e in payload["in_progress"] if e["kind"] == "feature"] == ["2026-07-01-alpha"]


def test_three_hundred_legacy_units_stay_fast(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    for i in range(300):
        write(repo / f".codestable/issues/2026-01-01-bug{i}/bug{i}-fix-note.md", "fixed\n")
    commit_all(repo, "legacy")
    add_worktree(repo, tmp_path, "codex/other")
    make_unit(repo)

    started = time.monotonic()
    payload = status_tool.status(repo)

    assert time.monotonic() - started < 10
    assert [e["unit"] for e in payload["in_progress"]] == ["2026-07-01-alpha"]
    assert payload["notes"][0].startswith("300 finished or canceled")


def test_plain_text_output_renders_every_section(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_unit(repo)
    dirty = add_worktree(repo, tmp_path, "codex/dirty")
    (dirty / "README.md").write_text("edited\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TOOLS_DIR / "codestable-status.py"), "--root", str(repo)],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    for heading in ("in_progress:", "waiting:", "recent:", "next:"):
        assert heading in result.stdout
    assert "2026-07-01-alpha" in result.stdout and "uncommitted changes" in result.stdout
    assert "init" in result.stdout  # a recent commit line (no `kind` field)


def test_a_branch_behind_the_default_still_counts_deleted_legacy_units_as_legacy(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    cs = repo / ".codestable"
    done_list = "steps:\n  - action: a\n    status: done\nchecks:\n  - item: b\n    status: passed\n"
    write(cs / "attention.md", "notes\n")
    write(cs / "features/2026-01-01-old/old-checklist.yaml", done_list)
    write(cs / "features/2026-01-01-old/old-acceptance.md", "accepted\n")
    write(cs / "issues/2026-02-01-bug/bug-fix-note.md", "fixed\n")
    commit_all(repo, "legacy records")
    behind = add_worktree(repo, tmp_path, "codex/behind")
    run(repo, "rm", "-r", "-q", ".codestable/features", ".codestable/issues")
    run(repo, "commit", "-q", "-m", "clean up legacy records on main")

    for root in (repo, behind):
        payload = status_tool.status(root)
        assert [e for e in payload["in_progress"] if e["kind"] != "branch"] == []
        assert payload["notes"][0].startswith("2 finished or canceled work directories")


def test_a_unit_created_on_a_branch_is_its_own_work_even_when_the_branch_is_behind(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / ".codestable").mkdir()
    worktree = add_worktree(repo, tmp_path, "codex/new")
    write(worktree / ".codestable/features/2026-10-01-fresh/fresh-ff-note.md", "done\n")
    commit_all(worktree, "ff done")
    (repo / "later.txt").write_text("moves main ahead\n", encoding="utf-8")
    commit_all(repo, "main moves on")

    entries = [e for e in status_tool.status(repo)["in_progress"] if e["kind"] == "feature"]

    assert [e["unit"] for e in entries] == ["2026-10-01-fresh"]
    assert entries[0]["stage"].startswith("closing: implementation done")


def test_without_a_fork_point_units_are_listed_and_the_reason_is_reported(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo / ".codestable/issues/2026-02-01-bug/bug-fix-note.md", "fixed\n")
    commit_all(repo, "legacy record")
    run(repo, "checkout", "-q", "--orphan", "solo")  # history unrelated to main: no merge-base
    run(repo, "commit", "-q", "-m", "unrelated root")

    payload = status_tool.status(repo)

    assert [e["unit"] for e in payload["in_progress"] if e["kind"] == "issue"] == ["2026-02-01-bug"]
    assert all("finished or canceled" not in n for n in payload["notes"])
    assert any("no fork point" in line and "main" in line for line in payload["not_checked"])


def test_a_repo_without_commits_lists_units_and_reports_the_missing_comparison(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    write(repo / ".codestable/issues/2026-02-01-bug/bug-fix-note.md", "fixed\n")

    payload = status_tool.status(repo)

    assert [e["unit"] for e in payload["in_progress"]] == ["2026-02-01-bug"]
    assert any("no fork point" in line for line in payload["not_checked"])


def _mononoke_shaped_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Submodule-like checkout: detached HEAD, a stale orphan local `main`, `origin/main` from a local bare
    remote, unprefixed legacy unit files, and one linked worktree on a branch."""
    bare = tmp_path / "origin.git"
    run(tmp_path, "init", "-q", "--bare", "-b", "main", bare.as_posix())
    seed = tmp_path / "seed"
    seed.mkdir()
    run(seed, "init", "-q", "-b", "main")
    run(seed, "config", "user.email", "test@example.com")
    run(seed, "config", "user.name", "Test User")
    cs = seed / ".codestable"
    done = "steps:\n  - action: a\n    status: done\nchecks:\n  - item: b\n    status: passed\n"
    write(cs / "features/2026-10-26-m1-save-catalog/checklist.yaml", done)
    write(cs / "features/2026-10-26-m1-save-catalog/acceptance.md", "accepted\n")
    write(cs / "features/2026-10-26-m1-save-catalog/implementation-review.md", "reviewer: subagent\n")
    write(cs / "issues/2026-10-27-old-bug/fix-note.md", "fixed\n")
    write(cs / "features/2026-10-18-design-only/design.md", "design\n")
    write(cs / "features/2026-10-16-pending/design.md", "design\n")
    write(cs / "features/2026-10-16-pending/checklist.yaml", CHECKLIST)
    commit_all(seed, "current work")
    (seed / "later.txt").write_text("x", encoding="utf-8")
    commit_all(seed, "newest on origin")
    run(seed, "push", "-q", bare.as_posix(), "main")
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-q", "-b", "main")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / "stale.txt").write_text("stale", encoding="utf-8")
    commit_all(repo, "stale local main, unrelated history")
    run(repo, "remote", "add", "origin", bare.as_posix())
    run(repo, "fetch", "-q", "origin")
    run(repo, "remote", "set-head", "origin", "main")
    run(repo, "checkout", "-q", "--detach", "origin/main")
    worktree = tmp_path / "wt"
    run(repo, "worktree", "add", "-q", "-b", "feat/x", worktree.as_posix(), "origin/main")
    (worktree / "x.txt").write_text("x", encoding="utf-8")
    commit_all(worktree, "feature commit")
    return repo, worktree, bare


def test_remote_tracking_default_is_used_when_local_main_is_stale_and_unrelated(tmp_path: Path) -> None:
    repo, worktree, _bare = _mononoke_shaped_repo(tmp_path)

    payload = status_tool.status(repo)

    assert payload["default_branch"] == "origin/main"
    assert "no fork point with HEAD" in payload["default_ref_note"]
    assert not any("no fork point" in line for line in payload["not_checked"])  # the comparison worked
    assert [c["subject"] for c in payload["recent"]][:2] == ["newest on origin", "current work"]
    listed = {e["unit"]: e for e in payload["in_progress"] if e["kind"] == "feature"}
    assert set(listed) == {"2026-10-18-design-only", "2026-10-16-pending"}
    assert listed["2026-10-18-design-only"]["stage"] == "design"
    assert "next step: second slice" in listed["2026-10-16-pending"]["stage"]
    assert payload["notes"][0].startswith("2 finished or canceled work directories, unchanged since this branch forked from origin/main")
    branches = [e for e in payload["in_progress"] if e["kind"] == "branch"]
    assert [(e["unit"], e["ahead"]) for e in branches] == [("feat/x", 1)]
    assert "(detached)" in listed["2026-10-18-design-only"]["branches"]


def test_header_names_the_ref_that_was_used(tmp_path: Path) -> None:
    repo, _worktree, _bare = _mononoke_shaped_repo(tmp_path)

    result = subprocess.run([sys.executable, str(TOOLS_DIR / "codestable-status.py"), "--root", str(repo)],
                            capture_output=True, text=True, check=False)

    assert result.stdout.splitlines()[0].endswith(
        "default branch: origin/main - remote-tracking default; local main has no fork point with HEAD)")


def test_default_ref_prefers_local_only_when_it_is_not_behind_the_remote_tracking_one(tmp_path: Path) -> None:
    repo, _worktree, _bare = _mononoke_shaped_repo(tmp_path)
    run(repo, "branch", "-f", "main", "origin/main~1")  # related, but behind origin/main
    assert status_tool.default_ref(repo)[0] == "origin/main"
    assert "is behind it" in status_tool.default_ref(repo)[1]

    run(repo, "branch", "-f", "main", "origin/main")  # level with origin/main
    assert status_tool.default_ref(repo)[0] == "main"

    run(repo, "branch", "-D", "main")  # no local branch at all
    assert status_tool.default_ref(repo)[0] == "origin/main"
    assert "no local branch main" in status_tool.default_ref(repo)[1]


def test_unprefixed_legacy_file_names_are_recognized_by_the_shared_predicates(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = Path(".codestable/features/2026-10-26-m1-save-catalog")
    write(repo / unit / "checklist.yaml", "steps:\n  - action: a\n    status: done\n")

    assert common.unit_needs_review(repo, unit) is True
    assert common.unit_completion_marker(repo, unit) == "implementation-done"
    assert common.existing_review_file(repo, unit) == unit / "m1-save-catalog-implementation-review.md"  # canonical when none
    write(repo / unit / "implementation-review.md", "reviewer: subagent\n")
    assert common.existing_review_file(repo, unit) == unit / "implementation-review.md"
    assert common.missing_review_findings(repo, [unit]) == []
    write(repo / unit / "acceptance.md", "---\nstatus: canceled\n---\n")
    assert common.unit_completion_marker(repo, unit) == "canceled"
