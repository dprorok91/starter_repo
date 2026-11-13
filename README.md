# Spec-driven agent starter

A shared specification, code inventory, and verification workflow for Python and JavaScript projects.
The core uses Python 3.12+; project runtimes are independent. The JavaScript adapter uses Node 24 and Babel.
The included Python application deliberately starts on **3.10** so an issue can upgrade it to **3.12**.

- [Installation and language setup](guides/INSTALL.md): Bash commands, runtime pins, lockfiles, and Git tracking.
- [Issue automation](guides/AUTOMATION.md): activation, example upgrade issue, logs, and PR behavior.
- [Migration plan](MIGRATION_PLAN.md): today's runnable milestone and later component extraction.
- [Adapter contract](guides/ADAPTERS.md): shared facts, supported syntax, and evidence limits.
- [Agent instructions](AGENTS.md) and [skills](.agents/skills/).

After installation:

```bash
python3.12 tools/starter.py verify
python3.12 tools/smoke_upgrade.py
python3.12 -m http.server 8000 --directory docs/generated
```

Open http://localhost:8000 for generated documentation. `verification.json` records commands and actual runtimes.
Starter tests live in `tests/`; each configured project's own tests run separately. Generated documentation is ignored
and uploaded by CI. Hosted automation requires publishing these files and configuring an OpenAI API secret.

The workflow implements and tests an eligible issue, opens a linked PR, and starts branch CI. Merge is manual by default;
GitHub closes the issue when its linked PR merges. No hosted agent run is implied by local test success.
