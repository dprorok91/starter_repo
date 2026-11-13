---
name: review-change
description: Review a starter repository change against its acceptance criteria, test evidence, documentation, and automation patch boundary.
---

Read the diff, approved request, affected specification, and actual test results.
Check behavior and failure cases, runtime/manifests/lockfile consistency, valid evidence
references, and preservation of the starter's own tests. Static links alone prove no behavior.
For agent patches run `python tools/agent.py check-patch --patch <file>` from a clean baseline,
then verify the applied change. Use a fresh checkout when reviewing workflow-produced patches.
Report concrete findings by severity with file references and unverified assumptions.
If no findings remain, state the checks performed and their limits. Do not merge by default.
