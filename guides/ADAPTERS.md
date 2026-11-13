# Language adapter contract

Project configuration and specifications are language-independent. Each adapter discovers supported source extensions,
extracts facts, installs locked dependencies, and verifies its runtime; project commands remain argument arrays executed in the project directory.
The current adapters use [Python AST](https://docs.python.org/3.12/library/ast.html) and
[Babel parser](https://babeljs.io/docs/babel-parser). New adapters must satisfy the same tested contract.

`facts.json` has `schema_version: 1` and a sorted `files` array. Each file supplies:

| Field | Meaning |
| --- | --- |
| path / language / project | Repository-relative identity and configured ownership |
| sha256 | Hash of the actual parsed source |
| symbols | Stable `path::qualified.name`, declaration kind, line, documentation |
| imports | Observed import specifiers; no invented ownership or dependency resolution |
| tests | Statically observed `path::test.name` identities |

The envelope records the Git commit when available; file hashes also identify uncommitted inputs.
JavaScript dependency installation disables lifecycle scripts by default. Projects requiring such scripts need an
explicit reviewed setup change before unattended use.

Tests assert actual discovery, syntax failure, unique/resolvable references, reproducible output, runtime selection,
failed-check propagation, patch boundaries, and symlink rejection. The upgrade smoke exercises a real runtime transition
in disposable checkouts. CI invokes the same verification command used locally.

Static test discovery does not establish execution or coverage. The verifier records passing commands and their runtime
in `verification.json`; it does not yet ingest per-test JUnit/coverage results. Dynamic/aliased test names, Python
re-exports, and JavaScript variable exports that are not functions/classes are not claimed as mapped API symbols.
Source symlinks are rejected. Generated outputs omit timestamps and absolute local paths for reproducibility.

When replacing the example profiles, add your actual lint/type/test/build commands. CI currently boots both demo
toolchains; tailor runtime installation to your profiles. Production persistence, deployment, process diagrams,
coverage thresholds, and vulnerability gates are later migrations, not proven by this starter's demo tests.
