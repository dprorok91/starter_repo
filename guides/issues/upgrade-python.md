Upgrade the application in `examples/python310/` from Python 3.10 to Python 3.12.
Keep its directory name and the independent tooling runtime unchanged.

Acceptance criteria:

- Change the application's `.python-version` to `3.12` and `requires-python` to `>=3.12`.
- Regenerate `uv.lock` using uv; a locked install must succeed and Python 3.10 must no longer satisfy the project.
- Preserve greeting behavior and existing tests. Add or adjust meaningful tests only where needed.
- Update the application's README and `acceptance.python.runtime` description in `docs/specs.json`.
- Run `python tools/starter.py verify`, including starter tests, Python tests under a real 3.12 interpreter,
  JavaScript regression tests, code scanning, reference checks, and documentation generation.
- Report the actual interpreter version and test results. Do not skip checks or weaken acceptance to pass.
- Open the linked PR through the configured workflow; automatic merge is outside this task.
