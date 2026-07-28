---
name: deploy-check
description: Run a pre-deploy checklist against the current branch — clean tree, synced with the base branch, tests and linters green, migrations and env vars accounted for. Use before shipping, tagging a release, or when the user asks whether a branch is safe to deploy.
argument-hint: [base branch, defaults to the repo default branch]
allowed-tools: Bash(git:*), Read, Grep, Glob
---

# Pre-deploy check

Verify the current branch is safe to deploy. Report facts, not reassurance —
if a check cannot be run, say so instead of assuming it passes.

## 1. Repository state

```
git status --short
git rev-parse --abbrev-ref HEAD
git log --oneline -10
```

The base branch is `$ARGUMENTS`, or the repo default branch when empty
(`git symbolic-ref refs/remotes/origin/HEAD`).

Check and report:

- Working tree clean? Uncommitted changes never reach the deploy.
- Behind the base branch? `git fetch origin <base>` then
  `git rev-list --count HEAD..origin/<base>`. Non-zero means the branch has not
  seen the latest base changes.
- Unpushed commits? `git rev-list --count origin/<branch>..HEAD`.

## 2. Checks

Find the project's real commands before running anything — read `package.json`
scripts, `Makefile`, `pyproject.toml`, `*.csproj`, `justfile`, or the CI
workflow under `.github/workflows/`. Use what the project actually defines.

Run tests and linters. Report the actual output on failure; never summarize a
red run as "mostly passing".

If no test command exists, say that outright — it is a finding, not a pass.

## 3. Deploy-shaped changes in the diff

Diff against the base branch (`git diff origin/<base>...HEAD --stat`) and flag:

- **Migrations.** New files under `migrations/`, `db/migrate/`, `alembic/`, or
  similar. Note whether each is reversible and whether it locks a large table.
- **Env vars.** New reads of `process.env` / `os.environ` / `Environment.Get*`
  that are not present in `.env.example`, the chart values, or the CI config.
- **Config and infra.** Changes to Dockerfile, compose files, k8s manifests,
  Terraform, or CI workflows.
- **Dependencies.** Lockfile changes without the corresponding manifest change,
  or vice versa.
- **Breaking API changes.** Removed or renamed public endpoints, fields, or
  message schemas.

## 4. Verdict

End with one of:

- **Ready** — every check passed; list them.
- **Blocked** — enumerate exactly what fails and the command that shows it.

Then list any manual step the deploy needs (run migration, set env var, warm a
cache), or state that there are none.
