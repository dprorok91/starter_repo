---
name: implement-spec
description: Implement reviewed acceptance criteria in a configured Python or JavaScript project, including runtime and dependency migrations.
---

Read the affected specification and project's runtime pins, manifests, and existing tests.
Implement the smallest change satisfying the criteria and relevant failure cases.
For Python runtime migrations update `.python-version`, `requires-python`, and `uv.lock`
together; use `uv lock` in the project directory and test the actual requested interpreter.
Do not change the independent orchestration runtime unless that is part of the request.
Run `python tools/starter.py verify`; resolve relevant failures within three repair attempts.
Keep symbol/test references resolvable and fold accepted behavior into `docs/specs.json`.
Remove completed temporary change packets. Record durable rationale under `docs/decisions/`.
Output changed behavior, exact checks and versions, and any blocker or remaining limitation.
