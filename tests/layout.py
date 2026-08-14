"""Single source of truth for repository layout in tests.

Skills live under ``plugins/codestable/skills/`` in the source tree but install
flat as ``<installed_root>/<skill>``. Tests import from here so a future layout
change is one edit, not one per test module.
"""

from __future__ import annotations

from pathlib import Path


# Repo-relative location of the shipped skill set.
SKILLS_RELPATH = "plugins/codestable/skills"

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "codestable"
SKILLS_ROOT = REPO_ROOT / SKILLS_RELPATH


def source_in(repo: Path, *parts: str) -> Path:
    """Path inside a synthetic source repo's plugin package.

    Use for fixtures that build a fake CodeStable checkout. The installed side
    stays flat (``installed_root / skill``) and must not use this helper.
    """
    return repo.joinpath(SKILLS_RELPATH, *parts)


def skill(name: str) -> Path:
    """Source directory of a shipped skill."""
    return SKILLS_ROOT / name


def skill_dirs() -> list[Path]:
    """Every shipped skill directory, sorted by name."""
    return sorted(path.parent for path in SKILLS_ROOT.glob("*/SKILL.md"))


ONBOARD_TOOLS = skill("cs-onboard") / "tools"
ONBOARD_REFERENCE = skill("cs-onboard") / "reference"
MAINTAINER_TOOLS = skill("codestable-maintainer") / "tools"
MAINTAINER_SCENARIOS = skill("codestable-maintainer") / "scenarios"
