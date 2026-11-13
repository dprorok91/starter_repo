#!/usr/bin/env python3
"""Language-neutral documentation and verification orchestration (Python 3.12+)."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
import sys

from adapters import ADAPTERS

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build', '.cache'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def inside(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes repository: {relative}')
    return path


def config(root):
    data = read_json(root / 'starter.json')
    if data.get('schema_version') != 1 or not data.get('projects'):
        raise ValueError('starter.json requires schema_version=1 and nonempty projects')
    ids, roots = set(), []
    for project in data['projects']:
        if project['id'] in ids or project['language'] not in ADAPTERS:
            raise ValueError(f'Invalid/duplicate project: {project["id"]}')
        ids.add(project['id'])
        directory = inside(root, project['root'])
        if not directory.is_dir():
            raise ValueError(f'Missing project root: {directory}')
        if any(directory.resolve().is_relative_to(other) or other.is_relative_to(directory.resolve()) for other in roots):
            raise ValueError('Project roots must not overlap')
        roots.append(directory.resolve())
        if not project.get('checks') or any(not isinstance(cmd, list) or not cmd or not all(isinstance(arg, str) for arg in cmd) for cmd in project['checks']):
            raise ValueError('Each project needs nonempty argument-array checks')
    return data


def discover(root, project):
    directory = inside(root, project['root'])
    # Git is authoritative for ignore rules; include new, not-yet-committed code too.
    result = subprocess.run(['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], capture_output=True, check=False)
    if result.returncode == 0:
        candidates = [root / os.fsdecode(name) for name in result.stdout.split(b'\0') if name]
    else:
        candidates = directory.rglob('*')
    files = set()
    for path in candidates:
        if not path.is_file() or not path.is_relative_to(directory):
            continue
        relative = path.relative_to(directory)
        if any(part in IGNORED for part in relative.parts) or path.suffix not in ADAPTERS[project['language']].extensions:
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Source symlink is not supported: {path}')
        files.add(path.relative_to(root).as_posix())
    if not files:
        raise ValueError(f'No source files found for {project["id"]}')
    return sorted(files)


def scan(root):
    projects = config(root)['projects']
    files = []
    for project in projects:
        names = discover(root, project)
        rows = ADAPTERS[project['language']].scan(root, names)
        for row in rows:
            row.update(language=project['language'], project=project['id'], sha256=hashlib.sha256((root / row['path']).read_bytes()).hexdigest())
            files.append(row)
    revision = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return {'schema_version': 1, 'git_commit': revision.stdout.strip() if revision.returncode == 0 else None, 'files': sorted(files, key=lambda row: row['path'])}


def validate_specs(root, facts):
    specs = read_json(root / 'docs' / 'specs.json')
    if specs.get('schema_version') != 1 or not isinstance(specs.get('features'), list) or not specs['features']:
        raise ValueError('Invalid specification envelope')
    symbols = {symbol['id'] for row in facts['files'] for symbol in row['symbols']}
    tests = {test for row in facts['files'] for test in row['tests']}
    ids = set()
    for feature in specs['features']:
        entries = [feature, *feature.get('acceptance', [])]
        if not feature.get('acceptance'):
            raise ValueError(f'Feature has no acceptance criteria: {feature["id"]}')
        for entry in entries:
            if not entry.get('id') or entry['id'] in ids:
                raise ValueError('Specification IDs must be present and unique')
            ids.add(entry['id'])
        for criterion in feature['acceptance']:
            if not criterion.get('description') or not criterion.get('tests') or not criterion.get('symbols'):
                raise ValueError(f'Acceptance needs description, tests and symbols: {criterion["id"]}')
            for reference in criterion['tests']:
                if reference not in tests:
                    raise ValueError(f'Unresolved test: {reference}')
            for reference in criterion['symbols']:
                if reference not in symbols:
                    raise ValueError(f'Unresolved symbol: {reference}')
    return specs


def generate(root):
    facts = scan(root)
    specs = validate_specs(root, facts)
    output = root / 'docs' / 'generated'
    write_json(output / 'facts.json', facts)
    escaped = html.escape(json.dumps({'specifications': specs, 'implementation': facts}, indent=2))
    (output / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Project documentation</title><h1>Specifications and implementation evidence</h1><p>Links show static evidence. Check verification.json and CI logs for executed checks.</p><pre>' + escaped + '</pre></html>\n', encoding='utf-8')
    return facts


def run_command(argv, cwd):
    print(f'[{cwd}] {argv}', flush=True)
    subprocess.run(argv, cwd=cwd, check=True)


def verify(root, selected=None, self_tests=True):
    # Remove stale success evidence before attempting a new run.
    evidence = root / 'docs' / 'generated' / 'verification.json'
    evidence.unlink(missing_ok=True)
    if self_tests:
        run_command([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'], ROOT)
    projects = config(root)['projects']
    if selected and selected not in {project['id'] for project in projects}:
        raise ValueError(f'Unknown project: {selected}')
    records = []
    for project in projects:
        if selected and selected != project['id']:
            continue
        directory = inside(root, project['root'])
        ADAPTERS[project['language']].prepare(directory)
        actual = ADAPTERS[project['language']].runtime(directory)
        for argv in project['checks']:
            run_command(argv, directory)
            records.append({'project': project['id'], 'command': argv, 'runtime': actual, 'status': 'passed'})
    facts = generate(root)
    write_json(evidence, {'schema_version': 1, 'checks': records, 'scope': selected or 'all', 'facts_sha256': hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()})
    print('Verification passed. Documentation: docs/generated/index.html')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['scan', 'docs', 'verify', 'context'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--project')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == 'verify':
        verify(root, args.project)
    elif args.command == 'scan':
        print(json.dumps(scan(root), indent=2))
    elif args.command == 'docs':
        generate(root)
    else:
        facts = generate(root)
        print('# Change context\n\n' + json.dumps({'specifications': read_json(root / 'docs' / 'specs.json'), 'implementation': facts}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
