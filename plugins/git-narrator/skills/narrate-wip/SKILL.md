---
name: narrate-wip
description: Forward-mode narration - turn the current dirty working tree into 1-3 semantic commits at a natural pause point, instead of "git add -A && commit -m wip". No history rewrite, no force-push, safe on branches with an open PR. Slices by purpose then layer, optionally build-gates each commit in a disposable worktree, and never touches file content.
argument-hint: "[gate: build | none, defaults to build when the tree compiles]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git show *)
  - Bash(git rev-parse *)
  - Bash(git ls-files *)
  - Bash(git stash create *)
  - Bash(git stash store *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git restore --staged *)
  - Bash(git reset --soft *)
  - Bash(git worktree *)
---

# Narrate the work in progress

This is the **forward** counterpart of `/git-narrator:narrate`. That skill
re-narrates a finished branch by rewriting its history; this one prevents the
mess at the source: at a natural pause point (a sub-task done, end of session,
context switch), it turns the dirty working tree into a small sequence of
semantic commits instead of one `wip` blob.

What it shares with `narrate`: the slicing axes, the `Stage:` trailer
vocabulary, the disposable-worktree build gate, and the rule that content is
immutable — you regroup changes, never edit them.

What it deliberately does **not** share: there is no history rewrite, no
`reset --hard`, no force-push, and no executor agent. Every operation is
additive (`git add` + `git commit`) and reversible with a single
`git reset --soft`, so planning and execution live in this one skill, behind
one approval. Because nothing is rewritten, this skill is safe on a branch
with an open PR under review — the scenario where `narrate` demands explicit
reviewer sign-off.

## 1. Preconditions

Verify, and stop with a clear message if any fails:

- There **is** something to commit: `git status --porcelain` is non-empty.
- No merge, rebase, or cherry-pick in progress (`git status` reports none).
- HEAD is on a branch, not detached.

Record two anchors:

- `start_head` = `git rev-parse HEAD` — the abort target.
- `backup` = `git stash create "narrate-wip backup"` — a commit SHA capturing
  the tracked working-tree state without touching the tree. If it returns
  empty while `--porcelain` showed only untracked files, note that: untracked
  files are not in the backup, but nothing in this flow deletes or edits
  files, so they are never at risk.

Keep `backup` alive for the run: `git stash store -m "narrate-wip backup" <sha>`
(drop it from the report if the user prefers; by default report it).

## 2. Discover the build command

Same sources as `narrate`: `package.json` scripts, `Makefile`,
`pyproject.toml`, `*.csproj` / `*.sln`, `justfile`, `.github/workflows/`.
Extract the cheapest full-tree check (compile/typecheck). Never invent
commands; if none exists, the gate degrades to `none` and the plan says so.

**Calibrate the gate before planning:** run the build once against the
working tree as it stands (it *is* the final state, so building in place is
correct here — unlike gate runs, which use a worktree). Green → default gate
is `build` per commit. Red → the tree is mid-thought; no slicing can make its
prefixes compile. Gate becomes `none`, and every commit carries a
`Wip-Build: red` trailer so the final `/narrate` pass knows these commits
never claimed to compile. `$ARGUMENTS` overrides the default either way.

## 3. Analyze the dirty changes

```
git status --porcelain
git diff --stat
git diff
git ls-files --others --exclude-standard   # untracked files
```

Build the full worklist: every modified, deleted, and untracked file. Each
one ends the plan in exactly one of:

- **a slice** — part of a planned commit, or
- **left out** — deliberately kept uncommitted (local config experiments,
  half-typed ideas the user wants to keep private to the tree). `narrate`
  has no such option because it consumes finished history; here it is a
  first-class outcome, chosen by the user, listed in the plan.

An unclassified file is a planning failure — recheck before presenting.

## 4. Slice

**Axis first:** one purpose in the pause → slice by layer. Several purposes
(a feature step plus an opportunistic fix) → slice vertically by purpose
first, then layer inside each.

**Layer order within a purpose** — same ladder as `narrate`, but a pause
point rarely spans all of it. One to three commits is the normal outcome;
producing five commits out of an afternoon's diff is over-slicing:

1. Intent docs — PRD, ADRs, reference notes
2. Domain / central definitions **+ their tests**
3. Support / infrastructure **+ their tests**
4. Wiring, composition **+ E2E tests**

Granularity is **file-level**. No partial staging, no `git add -p`: a file
that spans two slices goes whole into the later slice. When the gate is
`build`, every slice must leave the tree compilable — tests travel with the
code they test, and the fixture-in-support trap from `narrate` applies here
unchanged.

Messages follow the repo's existing style and carry the trailers the final
`/narrate` pass consumes:

```
Stage: docs | domain | support | e2e
Wip-Build: red          (only when the gate was calibrated to none by a red tree)
```

## 5. Present the plan and get approval

Show a table: one row per planned commit — position, message (with
trailers), files, gate. Below it, the **left-out list** (files that stay
uncommitted) — explicitly, so silence never hides a file.

State visibly, in one block: `start_head`, the backup stash SHA, and the
restore command:

```
git reset --soft <start_head> && git restore --staged .
```

(Everything committed by this run returns to the working tree exactly as it
was; untracked and left-out files were never moved.)

Then AskUserQuestion: **approve / adjust / abort**. Loop on adjust. Nothing
is committed before an explicit approve.

## 6. Execute

Per slice, in order:

1. `git add <the slice's files>` — explicit paths only. Never `git add -A`,
   `-u`, or `.`: the left-out list must survive.
2. `git commit` with the plan's message verbatim, trailers included.
3. If gate is `build`: build this commit in a disposable worktree — the
   working tree still holds later slices unstaged, so building it would test
   the wrong tree:

   ```
   git worktree add /tmp/narrate-wip-gate <commit-sha>
   (cd /tmp/narrate-wip-gate && <build_cmd>)
   git worktree remove --force /tmp/narrate-wip-gate
   ```

   The last commit's gate is redundant with the step-2 calibration run
   (same tree) — skip it and say so.

**Gate failure = slicing error**, never a code error: the full tree compiled
in step 2, so a red prefix is missing a file a later slice holds. Fix by
reassignment only: `git reset --soft <start_head>`, `git restore --staged .`,
move the file earlier, redo from step 6.1. Three amendment rounds maximum;
then merge the failing commit with its predecessor (concatenate messages,
keep both `Stage:` trailers). Never edit content to make a gate pass.

## 7. Verify and report

- `git status --porcelain` now lists **exactly** the left-out and untracked
  files from the plan — nothing more, nothing less. Any surprise → restore
  and report.
- `git diff <backup> HEAD --stat` must list only the left-out files'
  pending changes; with nothing left out, it must be empty. This is the
  content-immutability invariant made mechanical.

Report: the new `git log --oneline` range, gate results per commit
(including amendment rounds), the backup stash SHA, the restore command, and
the left-out list. **Do not push.** If the user asks, a plain `git push` —
this skill never has a reason to force.

## Relation to the final /narrate

This skill does not replace the pre-merge `/narrate` pass — discovery order
is not reading order, and explorations only reveal their fate at the end.
It changes what that pass receives: commits already atomic, staged-labeled,
and (gate permitting) compilable. The final narration becomes mostly
reordering and squashing of `Wip-Build: red` pairs, converging in fewer
amendment rounds because the forward slices tend to coincide with the ones
it would have created.

## Rules

- Existing history is untouchable: no `reset --hard`, no rebase, no
  `commit --amend` on commits that predate this run, no force-push — ever.
- Content is immutable: never `Edit`/`Write` project files, never let a
  fix leak in through staging. If you notice a bug while slicing, say so in
  the report; fixing it is the next work session, not this commit.
- `git reset --soft` may target only this run's `start_head`.
- An unclassified dirty file is a planning failure, not something to
  quietly `git add .` away.
