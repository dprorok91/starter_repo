#!/usr/bin/env python3
"""Exercise the runtime migration and fresh-checkout verifier without an API call."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from starter import ROOT, verify
from agent import check_patch, reject_staged_symlinks


def command(argv, root, **kwargs):
    return subprocess.run(argv, cwd=root, check=True, **kwargs)


def main():
    with tempfile.TemporaryDirectory(prefix='starter-upgrade-') as directory:
        baseline = Path(directory) / 'baseline'
        shutil.copytree(ROOT / 'tests/fixtures/basic', baseline, ignore=shutil.ignore_patterns('.venv', 'node_modules', '__pycache__'))
        shutil.copy2(ROOT / '.gitignore', baseline / '.gitignore')
        command(['git', 'init', '-q'], baseline)
        command(['git', 'add', '.'], baseline)
        command(['git', '-c', 'user.name=Starter Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'baseline'], baseline)
        verify(baseline, self_tests=False)
        initial = json.loads((baseline / 'docs/generated/verification.json').read_text())
        assert next(row for row in initial['checks'] if row['project'] == 'python-demo')['runtime'].startswith('3.10.')
        candidate = Path(directory) / 'candidate'
        shutil.copytree(baseline, candidate, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', 'generated'))
        project = baseline / 'examples/python310'
        (project / '.python-version').write_text('3.12\n')
        metadata = project / 'pyproject.toml'
        metadata.write_text(metadata.read_text().replace('>=3.10', '>=3.12'))
        readme = project / 'README.md'
        readme.write_text(readme.read_text().replace('3.10', '3.12'))
        specfile = baseline / 'docs/specs.json'
        specs = json.loads(specfile.read_text())
        specs['features'][0]['acceptance'][2]['description'] = 'The Python example requires Python >=3.12 and runs on its selected 3.12 interpreter.'
        specfile.write_text(json.dumps(specs, indent=2) + '\n')
        command(['uv', 'lock'], project)
        patch = Path(directory) / 'upgrade.patch'
        patch.write_bytes(command(['git', 'diff', '--binary', 'HEAD'], baseline, capture_output=True).stdout)
        command(['git', 'init', '-q'], candidate)
        command(['git', 'add', '.'], candidate)
        check_patch(candidate, patch)
        command(['git', 'apply', '--index', str(patch)], candidate)
        reject_staged_symlinks(candidate)
        verify(candidate, self_tests=False)
        evidence = json.loads((candidate / 'docs/generated/verification.json').read_text())
        assert next(row for row in evidence['checks'] if row['project'] == 'python-demo')['runtime'].startswith('3.12.')
        old = subprocess.run(['uv', 'run', '--locked', '--python', '3.10', 'python', '--version'], cwd=candidate / 'examples/python310', capture_output=True)
        assert old.returncode != 0, 'Upgraded project must reject Python 3.10'
        print('Upgrade smoke test passed: real 3.10 baseline -> policy-checked patch -> real 3.12 verification; 3.10 rejected.')


if __name__ == '__main__':
    main()
