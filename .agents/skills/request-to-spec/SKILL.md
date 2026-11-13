---
name: request-to-spec
description: Turn a starter repository issue or change request into a scoped specification delta and implementation packet before coding.
---

Read `AGENTS.md`, `starter.json`, and the affected entries in `docs/specs.json`.
Run `python tools/starter.py context` when implementation ownership is unclear.
Identify outcome, scope, invariants, failure cases, and observable acceptance criteria.
Reuse stable IDs. Proposed symbols must remain explicitly proposed until code exists.
Write a proportionate `changes/<id>/request.md`, `plan.md`, and `tasks.md` when useful.
An `agent:ready` issue supplies reviewed intent; proceed if its criteria are sufficient.
Report conflicting requirements or missing decisions before dependent implementation.
Output the spec delta, affected projects, required tests, and unresolved questions.
