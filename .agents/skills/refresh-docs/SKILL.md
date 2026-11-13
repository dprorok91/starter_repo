---
name: refresh-docs
description: Regenerate and diagnose the starter's shared Python and JavaScript code inventory and specification evidence.
---

Run `python tools/starter.py docs` for static documentation or `verify` for executed checks.
Authored intent lives in `docs/specs.json`; generated facts and browser live in
`docs/generated/` and must not be edited or committed. Never invent implementation links.
Investigate scanner parse errors and unresolved references at their source.
For missing files inspect `starter.json`, project roots, Git ignore rules, and adapter extensions.
Check a second generation for reproducibility after generator changes.
Report static evidence separately from runtime results in `verification.json` and CI logs.
