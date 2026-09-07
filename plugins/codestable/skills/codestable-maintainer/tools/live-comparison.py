#!/usr/bin/env python3
"""Run a frozen evaluator against two immutable CodeStable package revisions."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
from types import SimpleNamespace

PACKAGE = Path('plugins/codestable/skills')
DISABLED_FEATURES = ('remote_plugin', 'apps', 'hooks', 'shell_snapshot', 'memories',
                     'external_agent_memory_import', 'plugins', 'skill_search',
                     'skill_mcp_dependency_install')


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_snapshot(repo, ref, target):
    sha = subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'], cwd=repo, text=True).strip()
    target.mkdir(parents=True)
    archive = target.parent / (target.name + '.tar')
    subprocess.run(['git', 'archive', '--format=tar', '-o', str(archive), sha], cwd=repo, check=True)
    archive_sha = digest(archive)
    with tarfile.open(archive) as source:
        source.extractall(target, filter='data')
    archive.unlink()
    if not (target / PACKAGE / 'using-codestable/SKILL.md').is_file():
        raise ValueError('revision does not contain a CodeStable package: ' + sha)
    return {'requested_ref': ref, 'commit': sha, 'archive_sha256': archive_sha, 'root': str(target)}


def schedule(scenarios, repeats):
    for repeat in range(1, repeats + 1):
        for index, scenario in enumerate(scenarios):
            order = ['baseline', 'candidate'] if (repeat + index) % 2 else ['candidate', 'baseline']
            for arm in order:
                yield repeat, scenario, arm


def host_skill_paths(host_home, host_codex):
    paths = set()
    for root in [host_home / '.agents/skills', host_home / '.codex/skills', host_codex / 'skills']:
        if root.exists():
            visited = set()
            for directory, children, files in os.walk(root, followlinks=True):
                resolved = Path(directory).resolve()
                if resolved in visited:
                    children[:] = []
                    continue
                visited.add(resolved)
                if 'SKILL.md' in files:
                    path = Path(directory) / 'SKILL.md'
                    paths.update([str(path), str(path.resolve())])
    return sorted(paths)


def isolation_args(paths, model, effort):
    disabled = ','.join('{path=' + json.dumps(path) + ',enabled=false}' for path in paths)
    arguments = ['--ignore-user-config', '-m', model, '-c', 'model_reasoning_effort=' + json.dumps(effort),
                 '-c', 'skills.config=[' + disabled + ']']
    for feature in DISABLED_FEATURES:
        arguments.extend(['-c', 'features.' + feature + '=false'])
    return arguments


@contextmanager
def isolated_home(run_dir, skills, auth_source, codex_bin):
    home = run_dir / 'codex-home'
    home.mkdir(mode=0o700)
    (home / 'skills').mkdir()
    for skill in skills.iterdir():
        if skill.is_dir():
            (home / 'skills' / skill.name).symlink_to(skill, target_is_directory=True)
    auth = home / 'auth.json'
    saved = {key: os.environ.get(key) for key in ['CODEX_HOME', 'CODESTABLE_HARNESS_CODEX_BIN']}
    try:
        if auth_source.is_file():
            shutil.copyfile(auth_source, auth)
            auth.chmod(0o600)
        os.environ['CODEX_HOME'] = str(home)
        os.environ['CODESTABLE_HARNESS_CODEX_BIN'] = codex_bin
        yield home
    finally:
        auth.unlink(missing_ok=True)
        shutil.rmtree(home)
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def classify(result, events):
    if result.get('runtime_status') != 'completed':
        return 'infra_invalid'
    if not any(event.get('type') == 'turn.completed' for event in events):
        return 'infra_invalid'
    return 'pass' if result.get('ok') else 'fail'


def completed_tool_metrics(events):
    known = {'command_execution', 'file_change', 'mcp_tool_call', 'web_search',
             'image_generation', 'collab_tool_call', 'custom_tool_call', 'function_call', 'tool_call'}
    seen = set()
    counts = {}
    missing_ids = 0
    unknown = set()
    for event in events:
        if event.get('type') != 'item.completed' or not isinstance(event.get('item'), dict):
            continue
        item = event['item']
        kind = item.get('type')
        if kind not in known:
            if kind not in {'agent_message', 'reasoning', 'todo_list', 'error'}:
                unknown.add(str(kind))
            continue
        identity = item.get('id')
        if identity:
            if identity in seen:
                continue
            seen.add(identity)
        else:
            missing_ids += 1
        counts[kind] = counts.get(kind, 0) + 1
    return {'tool_call_count': sum(counts.values()), 'completed_tool_counts': counts,
            'tool_count_missing_ids': missing_ids, 'unclassified_completed_item_types': sorted(unknown),
            'tool_count_caveat': ('ID-less completions count individually; unknown item types are excluded.'
                                  if missing_ids or unknown else None)}


def execute(h, scenario, repeat, snapshot, run_dir, args, host_paths, auth_source):
    skills = snapshot / PACKAGE
    h.SKILLS_ROOT = skills
    h.SOURCE_ROOT = snapshot
    h.SCENARIO_ROOT = skills / 'codestable-maintainer/scenarios'
    h.RUNTIME_TOOL_SOURCE = skills / 'cs-onboard/tools'
    h.RUNTIME_REFERENCE_SOURCE = skills / 'cs-onboard/reference'
    original_common = h.write_common_codestable
    original_tempfile = h.tempfile
    original_actor = h.run_actor
    initial_state = {}
    def capture_actor(root, work, scenario, mode):
        initial_state.update(h.repo_snapshot(root))
        return original_actor(root, work, scenario, mode)
    h.run_actor = capture_actor
    def full_common(root):
        original_common(root)
        shutil.copytree(h.RUNTIME_REFERENCE_SOURCE, root / '.codestable/reference', dirs_exist_ok=True)
    h.write_common_codestable = full_common
    h.tempfile = SimpleNamespace(mkdtemp=lambda prefix: tempfile.mkdtemp(prefix=prefix, dir=run_dir))
    scenario = copy.deepcopy(scenario)
    actor = scenario.setdefault('actor', {})
    if actor.get('codex_args') not in (None, [], ['--add-dir', '{work}']):
        raise ValueError('comparison scenarios may only request --add-dir {work}')
    actor['codex_args'] = isolation_args(host_paths, args.model, args.effort) + ['--add-dir', '{work}']
    start = time.monotonic()
    try:
        with isolated_home(run_dir, skills, auth_source, args.codex_bin):
            result = h.run_one(scenario, repeat, 'live-codex', keep=True)
    except Exception as exc:
        result = {'ok': False, 'runtime_status': 'exception', 'error': repr(exc), 'tool_calls': []}
    finally:
        h.write_common_codestable = original_common
        h.tempfile = original_tempfile
        h.run_actor = original_actor
    result['wall_seconds'] = time.monotonic() - start
    result['git_initial'] = initial_state
    outer_call = next((call for call in result.get('tool_calls', []) if 'stdout' in call), {})
    raw = str(outer_call.get('stdout', ''))
    (run_dir / 'events.jsonl').write_text(raw)
    (run_dir / 'stderr.txt').write_text(str(outer_call.get('stderr', '')))
    events = h.jsonl_events(raw)
    result['classification'] = classify(result, events)
    result['usage'] = [event['usage'] for event in events if isinstance(event.get('usage'), dict)]
    result.update(completed_tool_metrics(events))
    if result.get('repo'):
        root = Path(result['repo'])
        result['git_final'] = h.repo_snapshot(root)
        (run_dir / 'changes.patch').write_text(h.git(root, 'diff', 'HEAD').stdout)
    write_json(run_dir / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', action='append', required=True)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--codex-bin', default='codex')
    parser.add_argument('--model', default='gpt-6-astra')
    parser.add_argument('--effort', default='low')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    repo = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    snapshots = {arm: export_snapshot(repo, getattr(args, arm), output / 'snapshots' / arm) for arm in ['baseline', 'candidate']}
    evaluator = output / 'agent-behavior-harness.py'
    shutil.copyfile(Path(__file__).with_name('agent-behavior-harness.py'), evaluator)
    shutil.copyfile(Path(__file__), output / 'live-comparison.py')
    spec = importlib.util.spec_from_file_location('comparison_evaluator', evaluator)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    scenarios = []
    scenario_meta = []
    for index, filename in enumerate(args.scenario):
        source = Path(filename).resolve()
        frozen = output / f'scenario-{index:02d}.yaml'
        shutil.copyfile(source, frozen)
        scenarios.append(h.load_scenario(frozen))
        scenario_meta.append({'source': str(source), 'frozen': str(frozen), 'sha256': digest(frozen)})
    host_codex = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    host_paths = host_skill_paths(Path.home(), host_codex)
    plan = list(schedule(range(len(scenarios)), args.repeats))
    manifest = {'snapshots': snapshots, 'evaluator_sha256': digest(evaluator), 'runner_sha256': digest(Path(__file__)),
                'scenarios': scenario_meta, 'model': args.model, 'effort': args.effort, 'schedule': plan,
                'disabled_host_skills': host_paths, 'disabled_features': list(DISABLED_FEATURES),
                'treatment_skills': {arm: {str(path.relative_to(Path(info['root']) / PACKAGE)): digest(path)
                    for path in sorted((Path(info['root']) / PACKAGE).glob('*/SKILL.md'))}
                    for arm, info in snapshots.items()}, 'prepare_only': args.prepare_only,
                'limitations': ['Small samples do not establish performance improvements.',
                                'Infrastructure-invalid runs are excluded from behavioral pass/fail.',
                                'Host OS and shell remain shared; this isolates Codex config and skill discovery.']}
    executable = shutil.which(args.codex_bin)
    manifest['codex_binary'] = executable or args.codex_bin
    if executable:
        manifest['codex_binary_sha256'] = digest(Path(executable))
        version = subprocess.run([executable, '--version'], text=True, capture_output=True, timeout=15)
        manifest['codex_version'] = version.stdout.strip()
    write_json(output / 'manifest.json', manifest)
    if args.prepare_only:
        print(json.dumps({'prepared': True, 'output': str(output), 'planned_runs': len(plan)}))
        return 0
    results = []
    for ordinal, (repeat, index, arm) in enumerate(plan, 1):
        run_dir = output / f'run-{ordinal:03d}-{arm}'
        run_dir.mkdir()
        result = execute(h, scenarios[index], repeat, Path(snapshots[arm]['root']), run_dir, args, host_paths, host_codex / 'auth.json')
        results.append({'ordinal': ordinal, 'arm': arm, 'scenario': scenarios[index].get('id'), 'repeat': repeat,
                        'classification': result['classification'], 'wall_seconds': result['wall_seconds'],
                        'usage': result['usage'], 'result_path': str(run_dir / 'result.json')})
        write_json(output / 'summary.json', {'results': results})
        print(json.dumps(results[-1]), flush=True)
    return 0 if all(result['classification'] == 'pass' for result in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
