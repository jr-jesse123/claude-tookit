---
name: narrate
description: Re-narrate the current feature branch before merge - replace messy exploratory commits with a semantic sequence (intent docs, domain + tests, support + tests, wiring + E2E) while keeping the final tree byte-identical. Plans interactively, then delegates execution to the git-narrator executor agent.
argument-hint: "[base branch, defaults to the repo default branch]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git show *)
  - Bash(git merge-base *)
  - Bash(git rev-parse *)
  - Bash(git rev-list *)
  - Bash(git symbolic-ref *)
---

# Narrate this branch

You are in **phase 1 of 2: analysis and planning.** You produce an approved plan;
you do not touch history yourself. Execution belongs to the
`git-narrator:executor` agent, which you spawn at the end with the plan and the
protocol path.

Read `${CLAUDE_SKILL_DIR}/execution-protocol.md` now — the plan you produce must
satisfy its input contract, and its gates shape what a valid plan looks like.

## 1. Preconditions

The base branch is `$ARGUMENTS`, or the repo default
(`git symbolic-ref refs/remotes/origin/HEAD`) when empty. Verify, and stop with
a clear message if any fails:

- Working tree and index are clean.
- Current branch is not the base branch.
- The branch is ahead of base (`git rev-list --count base..HEAD` > 0).
- Ask the user directly: **is there already a PR under review for this branch?**
  Rewriting during review destroys the anchors of existing review comments. If
  yes, get explicit confirmation that reviewers agreed before continuing.

Record `git rev-parse HEAD` — this SHA goes into the plan so the executor can
detect drift between approval and execution.

## 2. Discover build and test commands

Read what the project defines — `package.json` scripts, `Makefile`,
`pyproject.toml`, `*.csproj` / `*.sln`, `justfile`, or `.github/workflows/` —
and extract:

- the **build command** (compile/typecheck; the cheapest full-tree check),
- the **test command**, and how to scope it to a path or filter if the runner
  supports it (`dotnet test --filter`, `npm test -- <path>`, `pytest <path>`).

If no build step exists, pick the closest cheap gate (linter, `py_compile`) and
say so in the plan. Never invent commands.

## 3. Analyze the branch

```
git log --oneline base..HEAD
git diff base...HEAD --stat
git log --diff-filter=A --name-only base..HEAD   # files born on the branch
git log --diff-filter=D --name-only base..HEAD   # files deleted on the branch
```

Build three artifacts:

**a. The full changed-file list** (`git diff base...HEAD --name-status`). Every
file must end up assigned to exactly one slice — the executor fails fast on an
incomplete plan.

**b. Exploration pairs**: files added *and* deleted within the branch, and
commit pairs that introduce then revert an approach. These are candidates for
the user decision in step 5.

**c. Purpose count**: does the branch carry one unit of purpose or several
(multiple features, a feature plus an opportunistic refactor)? Judge from commit
messages and file clustering.

## 4. Slice

**Axis first:** one purpose → slice by layer. Several purposes → slice
vertically by purpose first, then apply the layer order inside each purpose.

**Layer order within a purpose** (each slice must leave the tree compilable —
tests travel *with* the code they test, never ahead of it):

1. Intent docs — PRD, ADRs, reference files, scripts that document intent
2. Domain / central definitions **+ their tests**
3. Support / infrastructure **+ their tests**
4. Wiring, composition **+ E2E tests**

Granularity is **file-level**. If one file genuinely spans two slices, prefer
assigning it to the later slice; splitting a file across commits is the
protocol's advanced path and needs a strong reason.

While classifying, watch for the classic trap: test fixtures and builders used
by domain tests but living in a "support" directory. If domain tests import
them, they belong in the domain slice — the build gate will catch this, but
catching it at planning is one less re-slice cycle.

## 5. Decide the fate of explorations (user decision)

For each exploration pair from 3b, use AskUserQuestion with these options:

- **Extract to ADR** — the learning matters, the wandering doesn't. You draft
  the ADR (short: context, what was tried, why rejected, decision), write it
  now, and commit it on the current branch before delegation. It then becomes
  part of the tree and lands in the intent-docs slice. This is the only write
  phase 1 performs, and it happens before the executor's baseline is taken.
- **Keep as intent → removal pair** — the trying-and-removing is itself the
  story. The executor reconstructs it: the file's content is restored from
  original history (`git checkout <old-sha> -- path`), committed early, removed
  in a later commit with a message that names where the learning went.
- **Drop silently** — noise; appears in no commit.

## 6. Present the plan and get approval

Show a table: one row per planned commit — position, message (with trailers),
files, and which gate applies. Messages follow the repo's existing style and
carry machine-readable trailers for future archaeology:

```
Stage: docs | domain | support | e2e
Refs: ADR-014            (when applicable)
Narrated-From: <original HEAD sha>   (last commit only)
```

State visibly, in one block: the backup ref name the executor will create, the
restore command (`git reset --hard <backup>`), the gate level, and whether the
result will be pushed (`--force-with-lease`) or left local — ask if not obvious.

Gate level (ask unless the user already said):

- `build` — compile each commit (default)
- `scoped` — build + each commit's own tests
- `full` — build + accumulated test suite per commit (expensive)

Then AskUserQuestion: **approve / adjust / abort**. Loop on adjust. Nothing is
executed before an explicit approve.

## 7. Delegate

Spawn the `git-narrator:executor` agent. Its prompt must contain, complete and
self-sufficient (the agent sees none of this conversation):

1. The absolute path to the protocol: `${CLAUDE_SKILL_DIR}/execution-protocol.md`
   — first instruction is to read it and follow it exactly.
2. Base branch, branch name, expected HEAD SHA.
3. Build command, test command and its scoping syntax, gate level.
4. The ordered slices: message (with trailers), full file list per slice.
5. Reconstruction pairs: path, source SHA for content, position of the add
   commit, position and message of the removal commit.
6. Push decision.

Report the executor's result to the user verbatim where it matters: the
old → new commit mapping, gate outcomes, the backup ref, and the restore
command. If the executor aborted, its report says why and confirms the branch
was restored — relay that without softening.

## Rules

- You never run `git reset`, `git add`, `git commit`, `git push`, or any
  mutating git command. If the analysis makes you want to — that work belongs in
  the plan, executed by the executor behind its gates.
- The one exception is writing ADR files in step 5, which happens through the
  normal permission prompt, visibly.
- An unassigned changed file is a planning failure, not an executor problem.
  Recheck 3a before delegating.
