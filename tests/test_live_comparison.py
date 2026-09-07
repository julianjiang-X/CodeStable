from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import MAINTAINER_TOOLS

spec = importlib.util.spec_from_file_location('live_comparison_tests', MAINTAINER_TOOLS / 'live-comparison.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_schedule_pairs_and_counterbalances():
    plan = list(runner.schedule([0, 1], 2))
    assert plan == [(1, 0, 'baseline'), (1, 0, 'candidate'), (1, 1, 'candidate'), (1, 1, 'baseline'),
                    (2, 0, 'candidate'), (2, 0, 'baseline'), (2, 1, 'baseline'), (2, 1, 'candidate')]


def test_auth_cleanup_and_environment_restored_on_exception(tmp_path, monkeypatch):
    skills = tmp_path / 'package'
    (skills / 'cs').mkdir(parents=True)
    auth = tmp_path / 'auth.json'
    auth.write_text('private test credential')
    run = tmp_path / 'run'
    run.mkdir()
    monkeypatch.setenv('CODEX_HOME', '/original-codex')
    monkeypatch.delenv('CODESTABLE_HARNESS_CODEX_BIN', raising=False)
    with pytest.raises(RuntimeError):
        with runner.isolated_home(run, skills, auth, '/codex') as home:
            assert (home / 'auth.json').stat().st_mode & 0o777 == 0o600
            assert (home / 'skills/cs').resolve() == skills / 'cs'
            assert os.environ['CODEX_HOME'] == str(home)
            raise RuntimeError('simulated launch failure')
    assert not (run / 'codex-home').exists()
    assert auth.read_text() == 'private test credential'
    assert os.environ['CODEX_HOME'] == '/original-codex'
    assert 'CODESTABLE_HARNESS_CODEX_BIN' not in os.environ


def test_infra_is_separate_from_behavior_and_requires_completion():
    done = [{'type': 'turn.completed'}]
    assert runner.classify({'ok': True, 'runtime_status': 'completed'}, []) == 'infra_invalid'
    assert runner.classify({'ok': True, 'runtime_status': 'process_failed'}, done) == 'infra_invalid'
    assert runner.classify({'ok': False, 'runtime_status': 'completed'}, done) == 'fail'
    assert runner.classify({'ok': True, 'runtime_status': 'completed'}, done) == 'pass'


def test_snapshot_uses_commit_not_dirty_checkout(tmp_path):
    repo = tmp_path / 'source'
    repo.mkdir()
    def git(*args):
        return subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    git('init')
    git('config', 'user.email', 'test@example.com')
    git('config', 'user.name', 'Test')
    skill = repo / runner.PACKAGE / 'using-codestable/SKILL.md'
    skill.parent.mkdir(parents=True)
    skill.write_text('frozen skill')
    runtime = repo / runner.PACKAGE / 'cs-onboard/tools/runtime.py'
    runtime.parent.mkdir(parents=True)
    runtime.write_text('frozen runtime')
    git('add', '.')
    git('commit', '-m', 'fixture')
    sha = git('rev-parse', 'HEAD')
    skill.write_text('uncommitted change')
    target = tmp_path / 'snapshot'
    metadata = runner.export_snapshot(repo, 'HEAD', target)
    assert metadata['commit'] == sha
    assert (target / runner.PACKAGE / 'using-codestable/SKILL.md').read_text() == 'frozen skill'
    assert (target / runner.PACKAGE / 'cs-onboard/tools/runtime.py').read_text() == 'frozen runtime'


def test_skills_config_disables_lexical_and_resolved_paths(tmp_path):
    installed = tmp_path / '.agents/skills'
    installed.mkdir(parents=True)
    real = tmp_path / 'elsewhere'
    real.mkdir()
    (real / 'SKILL.md').write_text('foreign')
    (installed / 'foreign').symlink_to(real, target_is_directory=True)
    # pathlib rglob does not traverse symlink directories: discover explicitly.
    paths = runner.host_skill_paths(tmp_path, tmp_path / '.codex')
    assert str(installed / 'foreign/SKILL.md') in paths
    assert str(real / 'SKILL.md') in paths
    args = runner.isolation_args(paths, 'gpt-6-astra', 'low')
    assert '--ignore-user-config' in args
    assert any('enabled=false' in arg for arg in args)
    for feature in ['remote_plugin', 'apps', 'hooks', 'shell_snapshot', 'memories']:
        assert 'features.' + feature + '=false' in args


def test_counts_completed_tool_types_once_and_reports_unknowns():
    def event(kind, identity=None, state='item.completed'):
        return {'type': state, 'item': {'type': kind, 'id': identity}}
    events = [event('command_execution', 'one', 'item.started'),
              event('command_execution', 'one'), event('command_execution', 'one'),
              event('file_change', 'two'), event('mcp_tool_call', 'three'),
              event('web_search', 'four'), event('agent_message', 'five'),
              event('error', 'six'), event('file_change'), event('new_tool_type', 'seven')]
    metrics = runner.completed_tool_metrics(events)
    assert metrics['tool_call_count'] == 5
    assert metrics['completed_tool_counts']['file_change'] == 2
    assert metrics['tool_count_missing_ids'] == 1
    assert metrics['unclassified_completed_item_types'] == ['new_tool_type']
    assert metrics['tool_count_caveat']
