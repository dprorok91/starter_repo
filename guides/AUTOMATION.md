# Issue to tested PR

The checked-in workflow responds to open GitHub issues labeled `agent:ready`.
It uses the [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action) and an OpenAI API key;
this setup does not assume a ChatGPT subscription supplies CI API authentication.
The action checks the triggering user's repository write access by default. Creating or labeling an issue authorizes
the implementation only when the triggering actor is trusted. Other issue authors cannot start the agent successfully.

## Activate once

The destination already has remote `https://github.com/dprorok91/starter_repo.git`.
Review and publish the prepared files to its default branch. Workflows must exist there before issue events can run.
These commands publish code and configure the remote repository; run them when ready:

```bash
cd /home/lenovo/projects/starter_repo
git status --short
git add .
git commit -m "Set up spec-driven Python and JavaScript issue automation"
git push origin HEAD
gh auth login
gh secret set OPENAI_API_KEY --repo dprorok91/starter_repo
gh label create agent:ready --repo dprorok91/starter_repo --color 1D76DB --description 'Approved for unattended implementation' --force
```

`gh secret set` prompts for the key; do not paste it into a committed file or shell command.
In **Settings → Actions → General**, allow GitHub Actions to create and approve pull requests.
Organization policy may also restrict workflow permissions or third-party actions. No personal access token or GitHub
App is required for this first milestone. API usage and GitHub Actions usage are subject to their account billing.

## Create today's upgrade issue

The Python example deliberately remains pinned to 3.10. The tooling itself runs on 3.12 so it can orchestrate both.
Use the supplied acceptance criteria:

```bash
gh issue create --repo dprorok91/starter_repo \
  --title 'Upgrade the Python demo from 3.10 to 3.12' \
  --label agent:ready \
  --body-file guides/issues/upgrade-python.md
gh run list --repo dprorok91/starter_repo --workflow resolve-issue.yml --limit 5
```

Inspect a selected run, substituting its numeric ID:

```bash
gh run watch RUN_ID --repo dprorok91/starter_repo --exit-status
gh run view RUN_ID --repo dprorok91/starter_repo --log-failed
gh pr list --repo dprorok91/starter_repo
```

## Expected behavior

1. The implementation job installs dependencies, confirms a green baseline, and passes the issue as data to the agent.
2. The agent updates the project runtime pin, minimum Python, lockfile, docs, and acceptance evidence; it runs tests.
3. A trusted script restricts the patch to configured project roots, specs, decisions, and active change packets.
   Automation code, agent instructions, starter tests, and core configuration are protected. Symlinks are rejected.
4. A fresh job applies the patch and reruns starter tests, project tests, runtime checks, parsing, and doc generation
   without the OpenAI API secret. Failure prevents publication.
5. A separate job receives write permissions, pushes `agent/issue-<number>`, and opens a PR containing `Closes #<number>`.
   It explicitly dispatches branch CI and uploads verification artifacts. The issue closes when the PR merges.

The publisher dispatches CI because workflows triggered with `GITHUB_TOKEN` have special recursion/approval behavior.
Explicit `workflow_dispatch` runs are supported; see [GitHub's workflow trigger rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

Runs for the same issue are serialized; an existing open agent PR makes later attempts skip implementation.
The agent is instructed to stop after three repair attempts; the job timeout bounds the overall run. Logs explain
failures or unclear requirements; the system does not claim resolution after a failed or empty patch.
To retry a failed issue, remove and reapply `agent:ready`. If an earlier publisher pushed a branch but failed before
opening its PR, inspect that branch before retrying: publication will not force-push over it.

## Completion and later options

Today's hosted acceptance is a PR with an actual Python 3.12 verification record, passing application and starter
tests, updated lock/spec/docs, and a green dispatched CI run. Local smoke success proves the verifier, not agent quality
or GitHub permissions. A real issue run is required to validate the hosted path.

Merge remains manual by default. Later, enable automatic merge only after configuring required branch checks and
reviewing the desired issue authorization policy. Broader tooling changes use a regular reviewed PR.

Dependency scanning follows this milestone: `npm audit` for npm packages and [pip-audit](https://pypi.org/project/pip-audit/)
for resolved Python dependencies, or [OSV-Scanner](https://google.github.io/osv-scanner/) for a shared scanner. Schedule
scans, upload reports, and track exceptions with owners/expiry; do not automatically rewrite dependencies on a finding.
Dependabot already proposes updates for GitHub Actions and the JavaScript parser. Vulnerability scanning is not yet
a blocking starter check.
