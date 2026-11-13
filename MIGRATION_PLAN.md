# Language-neutral starter migration plan

**Today:** Prove issue → implementation → real Python 3.12 tests → linked PR. The application starts on 3.10;
the independent orchestration runtime is 3.12. JavaScript support ships in the same first milestone.

1. **Separate the shared model from language adapters.** Common configuration, specs, acceptance IDs, commands,
   normalized facts, and rendering must not depend on application syntax. Python uses AST; JavaScript uses Babel.
   Both supply the same versioned contract. Runtime pins, source roots, checks, and dependency locks belong to each
   configured project. Pure Python, pure JavaScript, and mixed projects share the workflow.

2. **Bring automation and starter tests forward.** The first milestone includes root agent instructions, four skills,
   installation guides, fixed test fixtures, both scanners, reference validation, reproducible documentation, and one
   verification command. Test the starter separately from applications. Cover discovery/ignores, parse errors, invalid
   references, failed checks, runtime selection, patch policy, and a real 3.10 → 3.12 smoke migration.

3. **Ship the smallest hosted issue loop first.** A trusted actor creates/labels an `agent:ready` issue containing approved
   intent. The agent plans, updates specs, implements, and tests; a fresh verifier reruns checks before an isolated
   publisher opens the PR and dispatches CI. Bound retries/time, serialize issues, skip duplicate open PRs, and preserve
   failed-run evidence. Secrets stay out of code and the verifier. Merge remains manual initially.

4. **Extract World Archives components after that acceptance succeeds.** Migrate intake/context packing and the normalized
   documentation model first. Then generalize `scripts/docs/` and `scripts/review/` scanners, reference/boundary checks,
   browser, and process/SIPOC/Draw.io renderers. Move product rules and paths to configuration; preserve process-first
   behavior with neutral fixtures. Assess `scripts/truth/` and repair scripts individually. Keep authored feature/process
   YAML as intent, adapt it into the shared model, and generate views once. The small JSON spec/browser in this first
   milestone is a bootstrap, not a completed migration of those richer components.

5. **Add deeper quality and supply-chain checks later.** Ingest JUnit/coverage for per-criterion execution evidence,
   add actual project lint/type/build commands, then introduce npm/Python or OSV dependency scans, scheduled reports,
   and reviewed dependency updates. Add required checks before considering automatic merge.

**Completion evidence:** From a fresh clone, install from locks; open the supplied upgrade issue; receive a PR updating
the runtime pin, minimum Python, lock, docs, and spec; confirm starter/application tests pass under real 3.12 and branch
CI is green. Local tests alone do not establish hosted credentials, triggers, or agent behavior.

See [installation](guides/INSTALL.md) and [automation](guides/AUTOMATION.md) for Bash commands and activation prerequisites.
