"""Application-language adapters; shared orchestration does not parse source syntax."""
import ast
import json
from pathlib import Path
import subprocess
import tomllib


class PythonAdapter:
    extensions = {'.py'}

    def prepare(self, directory):
        subprocess.run(['uv', 'sync', '--locked'], cwd=directory, check=True)

    def scan(self, root, filenames):
        return [self.file_facts(root / name, name) for name in filenames]

    def file_facts(self, path, filename):
        tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=filename)
        symbols, imports, tests = [], [], []

        def visit(node, parents=()):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = '.'.join((*parents, child.name))
                    symbols.append({'id': f'{filename}::{name}', 'name': name, 'line': child.lineno, 'kind': 'class' if isinstance(child, ast.ClassDef) else 'function', 'documentation': ast.get_docstring(child) or ''})
                    if not isinstance(child, ast.ClassDef) and child.name.startswith('test_'):
                        tests.append(f'{filename}::{name}')
                    visit(child, (*parents, child.name))
                else:
                    if isinstance(child, ast.Import):
                        imports.extend(alias.name for alias in child.names)
                    elif isinstance(child, ast.ImportFrom):
                        imports.append('.' * child.level + (child.module or ''))
                    visit(child, parents)
        visit(tree)
        return {'path': filename, 'symbols': symbols, 'imports': sorted(set(imports)), 'tests': sorted(tests)}

    def runtime(self, directory):
        expected = (directory / '.python-version').read_text().strip()
        metadata = tomllib.loads((directory / 'pyproject.toml').read_text())
        if 'requires-python' not in metadata['project']:
            raise ValueError('Python projects must declare requires-python')
        result = subprocess.run(['uv', 'run', '--locked', 'python', '-c', 'import platform; print(platform.python_version())'], cwd=directory, capture_output=True, text=True, check=True)
        actual = result.stdout.strip()
        if '.'.join(actual.split('.')[:2]) != expected:
            raise ValueError(f'Python runtime mismatch: requested {expected}, ran {actual}')
        return actual


class JavaScriptAdapter:
    extensions = {'.js', '.jsx', '.mjs', '.cjs'}

    def prepare(self, directory):
        subprocess.run(['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=directory, check=True)

    def scan(self, root, filenames):
        script = Path(__file__).resolve().parent / 'javascript' / 'scan.mjs'
        result = subprocess.run(['node', str(script)], input=json.dumps({'root': str(root), 'files': filenames}), text=True, capture_output=True)
        if result.returncode:
            raise ValueError(f'JavaScript adapter failed (install with npm ci --prefix tools/javascript):\n{result.stderr}')
        return json.loads(result.stdout)

    def runtime(self, directory):
        actual = subprocess.check_output(['node', '--version'], text=True).strip()
        expected = (directory / '.node-version').read_text().strip()
        if actual.lstrip('v').split('.')[0] != expected:
            raise ValueError(f'Node runtime mismatch: requested {expected}, ran {actual}')
        return actual


ADAPTERS = {'python': PythonAdapter(), 'javascript': JavaScriptAdapter()}
