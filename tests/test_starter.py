import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import starter
import agent


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['starter.json', 'docs/specs.json']:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'tests/fixtures/basic' / name, target)
        shutil.copytree(ROOT / 'tests/fixtures/basic/examples', self.root / 'examples', ignore=shutil.ignore_patterns('.venv', '__pycache__', 'node_modules'))

    def git(self, *argv):
        return subprocess.run(['git', *argv], cwd=self.root, capture_output=True, check=True)


class StarterTests(Fixture):
    def test_both_adapters_report_symbols_imports_and_test_names(self):
        facts = starter.scan(self.root)
        specs = starter.validate_specs(self.root, facts)
        self.assertEqual(len(specs['features']), 1)
        rows = {row['path']: row for row in facts['files']}
        self.assertEqual(rows['examples/python310/demo.py']['symbols'][0]['name'], 'greet')
        self.assertIn('node:test', rows['examples/javascript/tests/greet.test.js']['imports'])
        self.assertTrue(rows['examples/javascript/src/greet.js']['symbols'][0]['documentation'])
        self.assertEqual(len(rows['examples/python310/tests/test_demo.py']['tests']), 3)

    def test_python_only_and_javascript_only_need_no_other_adapter(self):
        original = starter.config(self.root)
        for language in ['python', 'javascript']:
            data = copy.deepcopy(original)
            data['projects'] = [p for p in data['projects'] if p['language'] == language]
            starter.write_json(self.root / 'starter.json', data)
            self.assertEqual({row['language'] for row in starter.scan(self.root)['files']}, {language})

    def test_tracked_and_new_files_scanned_but_gitignored_files_excluded(self):
        self.git('init', '-q')
        (self.root / '.gitignore').write_text('ignored.py\n')
        self.git('add', '.')
        directory = self.root / 'examples/python310'
        (directory / 'new.py').write_text('async def added():\n    return 1\n')
        (directory / 'ignored.py').write_text('this is deliberately invalid syntax!')
        rows = {row['path']: row for row in starter.scan(self.root)['files']}
        self.assertIn('examples/python310/new.py', rows)
        self.assertNotIn('examples/python310/ignored.py', rows)

    def test_syntax_errors_fail_in_each_language(self):
        for file, contents in [('examples/python310/broken.py', 'def !'), ('examples/javascript/broken.js', 'export function (')]:
            path = self.root / file
            path.write_text(contents)
            with self.assertRaises((SyntaxError, ValueError)):
                starter.scan(self.root)
            path.unlink()

    def test_runtime_pin_mismatch_is_rejected(self):
        from adapters import JavaScriptAdapter
        directory = self.root / 'examples/javascript'
        (directory / '.node-version').write_text('0\n')
        with self.assertRaisesRegex(ValueError, 'runtime mismatch'):
            JavaScriptAdapter().runtime(directory)

    def test_commonjs_and_mjs_and_class_methods_are_tracked(self):
        (self.root / 'examples/javascript/extra.cjs').write_text("const fs = require('node:fs'); class Repo { save() {} }\n")
        (self.root / 'examples/javascript/extra.mjs').write_text('export const load = async () => 1;\n')
        rows = {r['path']: r for r in starter.scan(self.root)['files']}
        self.assertIn('node:fs', rows['examples/javascript/extra.cjs']['imports'])
        self.assertIn('Repo.save', [s['name'] for s in rows['examples/javascript/extra.cjs']['symbols']])
        self.assertIn('load', [s['name'] for s in rows['examples/javascript/extra.mjs']['symbols']])

    def test_missing_and_duplicate_spec_references_fail(self):
        data = starter.read_json(self.root / 'docs/specs.json')
        data['features'][0]['acceptance'][0]['tests'] = ['missing::test']
        starter.write_json(self.root / 'docs/specs.json', data)
        with self.assertRaisesRegex(ValueError, 'Unresolved test'):
            starter.validate_specs(self.root, starter.scan(self.root))
        data['features'][0]['acceptance'][0]['id'] = data['features'][0]['id']
        starter.write_json(self.root / 'docs/specs.json', data)
        with self.assertRaisesRegex(ValueError, 'unique'):
            starter.validate_specs(self.root, starter.scan(self.root))

    def test_generated_facts_are_deterministic_and_change_with_source(self):
        starter.generate(self.root)
        first = (self.root / 'docs/generated/facts.json').read_bytes()
        starter.generate(self.root)
        self.assertEqual(first, (self.root / 'docs/generated/facts.json').read_bytes())
        with (self.root / 'examples/python310/demo.py').open('a') as file:
            file.write('\n# changed\n')
        starter.generate(self.root)
        self.assertNotEqual(first, (self.root / 'docs/generated/facts.json').read_bytes())

    def test_path_escape_and_overlapping_roots_fail(self):
        with self.assertRaises(ValueError):
            starter.inside(self.root, '../outside')
        data = starter.config(self.root)
        data['projects'][1]['root'] = 'examples/python310/tests'
        starter.write_json(self.root / 'starter.json', data)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            starter.config(self.root)

    def test_failing_project_check_has_nonzero_exit_and_no_success_evidence(self):
        data = starter.config(self.root)
        data['projects'] = [data['projects'][1]]
        data['projects'][0]['checks'] = [[sys.executable, '-c', 'raise SystemExit(9)']]
        starter.write_json(self.root / 'starter.json', data)
        evidence = self.root / 'docs/generated/verification.json'
        starter.write_json(evidence, {'status': 'stale success'})
        with self.assertRaises(subprocess.CalledProcessError):
            starter.verify(self.root, self_tests=False)
        self.assertFalse(evidence.exists())


class AgentTests(Fixture):
    def test_issue_input_is_data_and_requires_eligible_issue(self):
        event = {'issue': {'number': 1, 'state': 'open', 'title': 'Upgrade', 'body': '$(touch /tmp/never-run) `secret`', 'labels': [{'name': 'agent:ready'}]}}
        prompt = agent.issue_prompt(event, 'Trusted instructions')
        self.assertIn('$(touch /tmp/never-run)', prompt)
        event['issue']['labels'] = []
        with self.assertRaises(ValueError):
            agent.issue_prompt(event, '')

    def test_policy_accepts_runtime_upgrade_but_blocks_workflow_and_secret_edits(self):
        self.assertTrue(agent.allowed_path(self.root, 'examples/python310/.python-version'))
        for path in ['.github/workflows/ci.yml', 'tools/starter.py', 'AGENTS.md', 'examples/python310/.env', '../escape']:
            try:
                allowed = agent.allowed_path(self.root, path)
            except ValueError:
                allowed = False
            self.assertFalse(allowed, path)

    def test_real_patch_is_inspected_before_application(self):
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Starter Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'baseline')
        target = self.root / 'examples/python310/.python-version'
        target.write_text('3.12\n')
        patch = self.root / 'upgrade.patch'
        patch.write_bytes(self.git('diff', '--binary', 'HEAD').stdout)
        self.assertEqual(agent.check_patch(self.root, patch), ['examples/python310/.python-version'])
        target.write_text('3.10\n')
        (self.root / 'AGENTS.md').write_text('changed instructions')
        self.git('add', 'AGENTS.md')
        patch.write_bytes(self.git('diff', '--cached', '--binary').stdout)
        with self.assertRaisesRegex(ValueError, 'protected'):
            agent.check_patch(self.root, patch)

    def test_symlink_patch_is_rejected(self):
        self.git('init', '-q')
        (self.root / 'examples/python310/link.py').symlink_to('/tmp/outside.py')
        self.git('add', '.')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            agent.reject_staged_symlinks(self.root)


if __name__ == '__main__':
    unittest.main()
