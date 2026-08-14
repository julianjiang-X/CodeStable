"""Package-level contracts: version/changelog consistency, shared reference wiring,
and the repository's document-size rule.

These guard invariants that are otherwise only stated in prose:

- ``CLAUDE.md`` rule 2: skills are independent install units, so a skill may only
  point at shared docs through the project-level ``.codestable/reference/`` path.
  Every such pointer must resolve to a template that ``cs-onboard`` actually ships.
- ``CLAUDE.md``: no single markdown document may exceed 300 lines.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import (  # noqa: E402
    ONBOARD_REFERENCE as REFERENCE_DIR,
    ONBOARD_TOOLS,
    PLUGIN_ROOT,
    REPO_ROOT as ROOT,
    SKILLS_ROOT,
    skill,
    skill_dirs,
)

MANIFEST_PATH = REFERENCE_DIR / "MANIFEST.json"
MAX_DOC_LINES = 300

sys.path.insert(0, str(ONBOARD_TOOLS))


def load_common():
    # Plain import so this shares one module instance with the other tool tests;
    # exec'ing a second copy breaks dataclass identity checks when both run.
    import codestable_common

    return codestable_common

# Shared references introduced by the upstream v2 absorption (CHANGELOG 1.1.0).
ABSORBED_REFERENCES = (
    "assurance.md",
    "code-design.md",
    "economy.md",
    "evidence-lifecycle.md",
)


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and "asset" not in path.parts
    ]


def test_version_matches_latest_changelog_entry() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    headings = re.findall(r"^## (\d+\.\d+\.\d+)$", changelog, re.MULTILINE)
    assert headings, "CHANGELOG.md has no versioned section"
    assert headings[0] == version, (
        f"VERSION is {version} but the newest CHANGELOG entry is {headings[0]}"
    )


@pytest.mark.parametrize("name", ABSORBED_REFERENCES)
def test_absorbed_reference_is_shipped_and_documented(name: str) -> None:
    assert (REFERENCE_DIR / name).exists(), f"cs-onboard/reference/{name} is missing"

    onboard = (skill("cs-onboard") / "SKILL.md").read_text(encoding="utf-8")
    assert f".codestable/reference/{name}" in onboard, (
        f"{name} is shipped but not listed in cs-onboard/SKILL.md, so onboard will not announce it"
    )


def skill_documents() -> list[Path]:
    """Markdown shipped inside a skill package.

    Scoped to skill directories on purpose: repo-level prose (CLAUDE.md, CHANGELOG.md,
    UPGRADE.md, ADRs) describes the convention using placeholder paths rather than
    consuming it, and must not be read as a real reference pointer.
    """
    return [doc for skill_dir in skill_dirs() for doc in skill_dir.rglob("*.md")]


def test_every_referenced_shared_doc_is_shipped_by_onboard() -> None:
    """A skill pointing at .codestable/reference/X.md is broken unless cs-onboard ships X.md."""
    pattern = re.compile(r"\.codestable/reference/([A-Za-z0-9._-]+\.md)")
    dangling: dict[str, set[str]] = {}

    documents = skill_documents()
    assert documents, "expected to find skill documents"

    for path in documents:
        for name in pattern.findall(path.read_text(encoding="utf-8")):
            if not (REFERENCE_DIR / name).exists():
                dangling.setdefault(name, set()).add(str(path.relative_to(ROOT)))

    assert not dangling, f"references with no cs-onboard template: {dangling}"


def test_reference_manifest_matches_directory_and_version() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    on_disk = sorted(p.name for p in REFERENCE_DIR.iterdir() if p.is_file() and p.suffix == ".md")
    assert manifest["files"] == on_disk, (
        "MANIFEST.json is out of sync with cs-onboard/reference/; regenerate it"
    )
    assert manifest["version"] == version, (
        f"MANIFEST.json version {manifest['version']} != VERSION {version}"
    )


@pytest.mark.parametrize("manifest", [".claude-plugin/plugin.json", ".codex-plugin/plugin.json"])
def test_plugin_manifest_version_matches_version_file(manifest: str) -> None:
    """The version users see in /plugin must not drift from the repo version."""
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    data = json.loads((PLUGIN_ROOT / manifest).read_text(encoding="utf-8"))

    assert data["version"] == version, (
        f"{manifest} version {data['version']} != VERSION {version}"
    )


def test_tools_package_version_matches_version_file() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert load_common().PACKAGE_VERSION == version, (
        "codestable_common.PACKAGE_VERSION must match the VERSION file, "
        "otherwise doctor reports false reference drift"
    )


def test_reference_drift_detects_stale_and_incomplete_copies(tmp_path: Path) -> None:
    common = load_common()
    reference = tmp_path / ".codestable" / "reference"
    reference.mkdir(parents=True)

    assert common.reference_drift(tmp_path)["state"] == "unversioned"

    manifest = reference / "MANIFEST.json"
    manifest.write_text(
        json.dumps({"version": common.PACKAGE_VERSION, "files": ["shared-conventions.md"]}),
        encoding="utf-8",
    )
    assert common.reference_drift(tmp_path)["state"] == "incomplete"

    (reference / "shared-conventions.md").write_text("x", encoding="utf-8")
    assert common.reference_drift(tmp_path)["state"] == "ok"

    manifest.write_text(
        json.dumps({"version": "0.0.1", "files": ["shared-conventions.md"]}), encoding="utf-8"
    )
    drift = common.reference_drift(tmp_path)
    assert drift["state"] == "version-mismatch"
    assert drift["found_version"] == "0.0.1"


def test_reference_drift_reports_absent_directory(tmp_path: Path) -> None:
    drift = load_common().reference_drift(tmp_path)
    assert drift["state"] == "absent"
    assert drift["has_codestable"] is False

    (tmp_path / ".codestable").mkdir()
    onboarded = load_common().reference_drift(tmp_path)
    assert onboarded["state"] == "absent"
    # An onboarded project with no reference/ dangles every skill pointer.
    assert onboarded["has_codestable"] is True


@pytest.mark.parametrize(
    "body",
    ['[]', '"nope"', '{"version": "9.9.9"}', '{"version": "9.9.9", "files": "one.md"}', 'not json'],
)
def test_reference_drift_survives_malformed_manifest(tmp_path: Path, body: str) -> None:
    """A truncated manifest must be reported, not raised out of diagnose()."""
    reference = tmp_path / ".codestable" / "reference"
    reference.mkdir(parents=True)
    (reference / "MANIFEST.json").write_text(body, encoding="utf-8")

    drift = load_common().reference_drift(tmp_path)

    assert drift["state"] == "unreadable"
    assert drift["error"]


def documented_script_paths(doc: Path) -> set[str]:
    """Repo-relative script paths invoked in runnable command examples."""
    text = doc.read_text(encoding="utf-8")
    found: set[str] = set()
    for match in re.finditer(r"python3?\s+([A-Za-z0-9._/-]+\.(?:py|sh))", text):
        candidate = match.group(1)
        # Placeholders and runtime-copy paths are not repo files.
        if candidate.startswith((".codestable/", "<", "$", "/", "~")):
            continue
        found.add(candidate)
    return found


def test_documented_commands_point_at_real_files() -> None:
    """A copy-pasteable `python3 <path>` in docs must reference a file that exists.

    This is the guard for layout moves: renaming a directory silently invalidates
    every command block that names it, and no other test executes those strings.
    """
    docs = [ROOT / "README.md", ROOT / "README.en.md", ROOT / "UPGRADE.md"]
    docs += [doc for skill_dir in skill_dirs() for doc in skill_dir.rglob("*.md")]

    broken: dict[str, set[str]] = {}
    for doc in docs:
        for candidate in documented_script_paths(doc):
            if not (ROOT / candidate).exists():
                broken.setdefault(str(doc.relative_to(ROOT)), set()).add(candidate)

    assert not broken, f"documented commands reference missing files: {broken}"


def test_markdown_documents_stay_within_size_limit() -> None:
    oversized = {
        str(path.relative_to(ROOT)): len(path.read_text(encoding="utf-8").splitlines())
        for path in markdown_files()
    }
    oversized = {name: count for name, count in oversized.items() if count > MAX_DOC_LINES}

    assert not oversized, f"documents over {MAX_DOC_LINES} lines must be split: {oversized}"


def load_risk_gate_checker():
    import importlib.util

    path = skill("codestable-maintainer") / "tools" / "check-risk-gate.py"
    spec = importlib.util.spec_from_file_location("check_risk_gate_for_tests", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fast_lanes_carry_a_complete_risk_gate() -> None:
    """Volume gates are not risk gates; every fast lane must wire to assurance.md."""
    payload = load_risk_gate_checker().check(SKILLS_ROOT)

    assert payload["ok"], payload
    for lane, result in payload["lanes"].items():
        assert not result["missing_categories"], (lane, result)
        assert result["takes_full_row"], lane
        assert result["stays_in_lane"], lane


def _fake_lane_files(root: Path, gate_body: str, tail: str = "") -> Path:
    """Minimal skills tree with the same gate body in every lane."""
    checker = load_risk_gate_checker()
    fake = root / "skills"
    for relpath, heading in checker.LANES.values():
        target = fake / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        scope = checker.SCOPE_SECTIONS.get(_lane_of(relpath))
        scope_block = ""
        if scope:
            scope_heading, tokens = scope
            scope_block = f"\n{scope_heading}\n" + " ".join(tokens) + "\n\n## after\n"
        target.write_text(
            f"# lane\n\n{heading}\n{gate_body}\n\n## next\n{scope_block}{tail}", encoding="utf-8"
        )
    return fake


def _lane_of(relpath: str) -> str:
    return relpath.split("/", 1)[0]


def _well_formed_gate() -> str:
    checker = load_risk_gate_checker()
    listing = " · ".join(checker.RISK_KEYWORDS)
    return (
        f"引子提到权限判断。\n\n八类风险与 `.codestable/reference/assurance.md` 逐行对应：{listing}。\n\n"
        "命中后照搬那一行，`+` 连接的每项都要做；加审指在地板 review 之外再加一轮。\n"
        "只命中风险时不切回；不命中带一句 无命中。"
    )


def test_risk_gate_checker_accepts_a_well_formed_gate(tmp_path: Path) -> None:
    """Positive control: without this, the decoy tests could pass on a broken checker."""
    checker = load_risk_gate_checker()
    fake = _fake_lane_files(tmp_path, _well_formed_gate())

    for lane in checker.LANES:
        result = checker.check_lane(fake, lane)
        assert result["ok"], (lane, result)


def test_risk_gate_checker_rejects_a_gutted_gate(tmp_path: Path) -> None:
    """Heading kept, payload replaced by a comment carrying the keywords."""
    checker = load_risk_gate_checker()
    keywords = " ".join(checker.RISK_KEYWORDS)
    fake = _fake_lane_files(tmp_path, f"<!-- assurance.md 逐行对应 {keywords} 每项都要做 加审 之外 不切回 无命中 -->")

    for lane in checker.LANES:
        result = checker.check_lane(fake, lane)
        assert result["ok"] is False, (lane, result)


def test_risk_gate_checker_rejects_keywords_outside_the_gate_section(tmp_path: Path) -> None:
    """The headline claim: keywords present in the file but outside the gate must fail.

    A whole-file substring probe passes this; only real section scoping fails it.
    """
    checker = load_risk_gate_checker()
    listing = " · ".join(checker.RISK_KEYWORDS)
    gutted = "八类风险与 `assurance.md` 逐行对应：见附录。\n命中后每项都要做；加审在地板之外；不切回；无命中也记一句。"
    appendix = f"\n## 附录\n\n逐行对应：{listing}\n"
    fake = _fake_lane_files(tmp_path, gutted, tail=appendix)

    for lane in checker.LANES:
        result = checker.check_lane(fake, lane)
        assert result["ok"] is False, (lane, result)
        assert result["missing_categories"], (lane, result)


def test_risk_gate_checker_never_fails_open_without_a_terminator(tmp_path: Path) -> None:
    """An unbounded section must report missing, not widen to the rest of the file."""
    checker = load_risk_gate_checker()
    listing = " · ".join(checker.RISK_KEYWORDS)
    fake = tmp_path / "skills"
    for relpath, heading in checker.LANES.values():
        target = fake / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        # Heading present, no following boundary anywhere, keywords far below.
        target.write_text(f"{heading}\nno boundary follows\n逐行对应：{listing}\n", encoding="utf-8")

    for lane in checker.LANES:
        result = checker.check_lane(fake, lane)
        assert result["ok"] is False, (lane, result)
        assert "unbounded" in result.get("reason", ""), (lane, result)


def test_risk_gate_checker_requires_the_counterweight(tmp_path: Path) -> None:
    checker = load_risk_gate_checker()
    fake = _fake_lane_files(tmp_path, _well_formed_gate())

    # Counterweight section absent entirely.
    assert checker.check_counterweight(fake)["ok"] is False


def load_review_protocol_checker():
    import importlib.util

    path = skill("codestable-maintainer") / "tools" / "check-review-protocol.py"
    spec = importlib.util.spec_from_file_location("check_review_protocol_for_tests", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reviewer_protocol_sections_are_intact() -> None:
    payload = load_review_protocol_checker().check(SKILLS_ROOT)

    assert payload["ok"], payload
    for heading, result in payload["sections"].items():
        assert not result["missing"], (heading, result)


def test_review_protocol_checker_rejects_a_decoy_section(tmp_path: Path) -> None:
    """Keywords present but the section gutted must fail, or the guard is theatre."""
    checker = load_review_protocol_checker()
    target = tmp_path / "skills" / checker.CONVENTIONS
    target.parent.mkdir(parents=True, exist_ok=True)
    keywords = " ".join(kw for elems in checker.REQUIRED.values() for kw in elems)
    body = "".join(f"{heading}\n<!-- {keywords} -->\n" for heading in checker.REQUIRED)
    target.write_text(body, encoding="utf-8")

    payload = checker.check(tmp_path / "skills")

    assert payload["ok"] is False
    assert any(not s["ok"] for s in payload["sections"].values())
