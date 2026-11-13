# Installation: Bash on Linux or macOS

Run these commands inside a clone of this starter. Git, curl, and network access are prerequisites.
The application language is independent of the tooling runtime: Python 3.12+ runs orchestration;
Node 24 runs the optional JavaScript parser. Developing/testing this mixed starter requires both.
Install commands download tools; they do not change the system Python.

## 1. Install the tooling runtimes

Install uv, then both Python versions for the upgrade exercise:

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/starter-uv-install.sh
sh /tmp/starter-uv-install.sh
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.10 3.12
uv --version
uv run --no-project --python 3.12 python --version
```

Install Node 24 using nvm. Skip nvm installation if it is already installed:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh -o /tmp/starter-nvm-install.sh
bash /tmp/starter-nvm-install.sh
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version
npm --version
```

These use the documented [uv installer](https://docs.astral.sh/uv/getting-started/installation/),
[uv-managed Python versions](https://docs.astral.sh/uv/concepts/python-versions/), and
[nvm installation](https://github.com/nvm-sh/nvm/tree/v0.40.3#installing-and-updating).

## 2. Install and verify the starter

```bash
cd /home/lenovo/projects/starter_repo
npm ci --prefix tools/javascript --ignore-scripts
npm ci --prefix examples/javascript --ignore-scripts
uv sync --directory examples/python310 --locked
uv run --no-project --python 3.12 python tools/starter.py verify
uv run --no-project --python 3.12 python tools/smoke_upgrade.py
```

The first command installs the parser from its lockfile. The example applications currently have no third-party
dependencies. `verify` runs starter tests, both application test suites, actual-runtime checks, source parsing,
specification references, and documentation generation. The smoke test uses disposable copies: it upgrades the Python
example, refreshes its lockfile, applies the patch to a fresh baseline, verifies 3.12, and checks that 3.10 is rejected.
It does not invoke a hosted agent or modify your example's 3.10 baseline.

## 3. Track Python code and dependencies

For an existing Python project, preserve its environment manager unless you choose to migrate. This starter's default
Python profile uses uv; other managers require an adapter/runtime check and configured commands.
For a new project alongside the examples, run from the repository root:

```bash
uv init --bare --python 3.12 apps/my-python
uv python pin --directory apps/my-python 3.12
uv add --directory apps/my-python --dev pytest
mkdir -p apps/my-python/tests
```

Add application code and behavioral tests, then add a `python` project to `starter.json`, with its own `root` and checks,
for example `["uv", "run", "--locked", "pytest"]`. Commands run from that project directory. The checked-in examples
show a dependency-free `unittest` alternative. Set `requires-python` in `pyproject.toml` deliberately: the interpreter
pin selects your local runtime; it does not set the supported version range.

```bash
uv lock --directory apps/my-python
uv sync --directory apps/my-python --locked
git add apps/my-python/pyproject.toml apps/my-python/uv.lock apps/my-python/.python-version
git add apps/my-python starter.json docs/specs.json
uv run --no-project --python 3.12 python tools/starter.py verify
```

The Python adapter parses `.py` files with AST and records functions, classes, docstrings, imports, and literal
`test_*` definitions, including unittest methods. The tool runs under 3.12; syntax introduced after 3.12 needs a newer
tooling interpreter. New specification criteria must reference existing `path::qualified.name` IDs.

## 4. Track JavaScript code and dependencies

For a new JavaScript project, run from the repository root:

```bash
mkdir -p apps/my-js/src apps/my-js/tests
cd apps/my-js
npm init -y
npm pkg set type=module 'engines.node=24.x' 'scripts.test=node --test tests/*.test.js'
printf '24\n' > .node-version
npm install --package-lock-only --ignore-scripts
cd ../..
```

Add source and tests, then register a `javascript` project in `starter.json` with `root: apps/my-js` and
`checks: [["npm", "test"]]`. Add its acceptance references to `docs/specs.json`.

```bash
npm ci --prefix apps/my-js
git add apps/my-js starter.json docs/specs.json
uv run --no-project --python 3.12 python tools/starter.py verify
```

The Babel adapter handles `.js`, `.jsx`, `.mjs`, and `.cjs`; it records declarations, imports, and literal `test`/`it`
calls. JSX parsing does not configure a React test/build environment. Configure the project's actual lint, test, and
build commands in `checks`. TypeScript is a future adapter capability, not currently advertised support.

## 5. Check discovery and Git tracking

The scanner includes tracked and new unignored files under configured roots. Add new files to Git before committing.
Virtual environments, dependencies, builds, caches, credentials, and generated docs stay ignored.

```bash
git status --short
git ls-files '*.py' '*.js' '*.jsx' '*.mjs' '*.cjs'
git check-ignore -v examples/python310/demo.py examples/javascript/src/greet.js || true
uv run --no-project --python 3.12 python tools/starter.py scan > /tmp/starter-facts.json
uv run --no-project --python 3.12 python tools/starter.py docs
```

For source files, `git check-ignore` should print nothing. `scan` inventories new unignored files too, so compare its
output with `git status`. Commit manifests, runtime pins, locks, specs, tests, and agent guidance. Review project-specific ignore rules when adapting the starter.

Python-only or JavaScript-only applications use the same model: remove the unused profile and its example-specific
specification references. The shared self-test fixtures remain independent. Python-only scans need no Node runtime;
the starter development suite deliberately exercises both adapters and therefore still requires both toolchains.

Local and CI installs use [locked uv synchronization](https://docs.astral.sh/uv/concepts/projects/sync/) and
[`npm ci`](https://docs.npmjs.com/cli/v11/commands/npm-ci/) to reject stale manifests/lockfiles.
