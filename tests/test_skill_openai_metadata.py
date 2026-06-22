from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def frontmatter_name(skill_dir: Path) -> str:
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert match, f"{skill_dir}/SKILL.md has no frontmatter"

    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        if key == "name":
            return value.strip().strip('"')

    raise AssertionError(f"{skill_dir}/SKILL.md has no name")


def read_openai_interface(skill_dir: Path) -> dict[str, str]:
    path = skill_dir / "agents/openai.yaml"
    assert path.exists(), f"{skill_dir.name} is missing agents/openai.yaml"

    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r'^  ([a-z_]+): "(.*)"$', line)
        if match:
            fields[match.group(1)] = match.group(2).replace('\\"', '"')
    return fields


def test_every_skill_has_consistent_openai_metadata() -> None:
    skill_dirs = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))

    assert skill_dirs, "expected at least one skill"
    for skill_dir in skill_dirs:
        name = frontmatter_name(skill_dir)
        interface = read_openai_interface(skill_dir)

        assert interface.get("display_name"), f"{name} has no display_name"
        assert interface["display_name"] != name, f"{name} should not expose the raw skill id"
        assert not interface["display_name"].startswith("Cs "), f"{name} should use CodeStable, not Cs"

        short_description = interface.get("short_description", "")
        assert 25 <= len(short_description) <= 64, f"{name} has invalid short_description length"

        default_prompt = interface.get("default_prompt", "")
        assert f"${name}" in default_prompt, f"{name} default_prompt must mention ${name}"

        if name == "browser-bridge":
            assert interface["display_name"] == "Browser Bridge"
        elif name == "using-codestable":
            assert interface["display_name"] == "Using CodeStable"
        else:
            assert interface["display_name"].startswith("CodeStable"), f"{name} display is off-brand"
