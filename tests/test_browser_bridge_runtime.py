from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "browser-bridge"
ENTRYPOINTS = (
    BRIDGE / "scripts/browser.py",
    BRIDGE / "scripts/browser_master.py",
)
EXPECTED_DEPENDENCIES = {
    "beautifulsoup4",
    "bottle",
    "requests",
    "simple-websocket-server",
}


def read_script_metadata(path: Path) -> tuple[str, set[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index("# /// script") + 1
    end = lines.index("# ///", start)
    metadata = "\n".join(line.removeprefix("# ") for line in lines[start:end])
    requires_python = re.search(r'^requires-python = "([^"]+)"$', metadata, re.MULTILINE)
    dependencies = re.search(r"dependencies = \[(.*?)\]", metadata, re.DOTALL)

    assert requires_python
    assert dependencies
    return requires_python.group(1), set(re.findall(r'"([^"]+)"', dependencies.group(1)))


def test_browser_bridge_entrypoints_own_their_uv_runtime() -> None:
    for entrypoint in ENTRYPOINTS:
        content = entrypoint.read_text(encoding="utf-8")
        requires_python, dependencies = read_script_metadata(entrypoint)

        assert content.startswith("#!/usr/bin/env -S uv run --script\n")
        if os.name != "nt":
            assert os.access(entrypoint, os.X_OK)
        assert requires_python == ">=3.10"
        assert dependencies == EXPECTED_DEPENDENCIES


def test_browser_bridge_entrypoint_locks_are_consistent() -> None:
    locks = [path.with_suffix(".py.lock").read_text(encoding="utf-8") for path in ENTRYPOINTS]

    assert locks[0] == locks[1]
    assert 'requires-python = ">=3.10"' in locks[0]
    manifest = locks[0].split("[manifest]", 1)[1].split("[[package]]", 1)[0]
    assert set(re.findall(r'\{ name = "([^"]+)" \}', manifest)) == EXPECTED_DEPENDENCIES


def test_browser_bridge_guidance_never_bypasses_the_uv_runtime() -> None:
    guidance_paths = sorted(
        path
        for path in BRIDGE.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py"}
    )

    for path in guidance_paths:
        content = path.read_text(encoding="utf-8")
        assert "pip install bs4" not in content
        assert "请叫Agent安装BeautifulSoup4" not in content
        assert not re.search(r"(?m)^\s*python3?\s+.*browser(?:_master)?\.py", content)
