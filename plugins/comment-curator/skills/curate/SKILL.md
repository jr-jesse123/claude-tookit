---
name: curate
description: Review the lifecycle of code comments - verify each against the code it describes, delete noise, keep load-bearing constraints. Scoped to uncommitted changes by default, or to a file/directory you name. Verification runs in the comment-curator verifier agent; approval and edits stay in the session. Use after LLM-heavy sessions or before merging a branch, when comments have accumulated faster than they were curated.
argument-hint: "[file or directory; empty = current diff]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Edit
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git blame *)
  - Bash(git rev-parse *)
  - Bash(git symbolic-ref *)
  - Bash(python3 *extract-candidates.py*)
---

# Curate comments

Review comments in scope and give each one of three verdicts: **stale**,
**delete**, or **keep**. You are the orchestrator: you resolve the scope, build
the inventory, present the verdict table, and apply what the user approves.
Reading code and judging candidates — the expensive part — belongs to the
`comment-curator:verifier` agent, which holds the verdict rules and keeps file
contents out of this conversation. Do not read scoped files or verify
candidates yourself; that defeats the split. Nothing is edited before the user
approves the verdict table. Every edit you make is comment-only — code never
changes.

## 1. Resolve the scope

- `$ARGUMENTS` names a file or directory → all comments in those files
  (recurse directories; respect `.gitignore`).
- Empty → uncommitted changes (`git diff` + `git diff --cached`); comments on
  changed or adjacent lines.
- Empty and the tree is clean → the branch diff against the default branch
  (`git diff $(git symbolic-ref refs/remotes/origin/HEAD)...HEAD`).

State which scope you resolved to — the mode (**diff** or **path**) goes into
the verifier prompt, because it sets the burden of proof: in diff mode a
comment must justify staying; in path mode it must be *demonstrably* wrong or
noisy to be touched. In **path mode**, if the scope exceeds ~50 files, report
the count and ask whether to proceed or narrow before reading anything.

## 2. Inventory

Build the candidate list with the bundled script — it is deterministic about
coverage and emits the exact `file:line` numbers the verdict table and the
edits depend on:

- **Diff mode:** pipe each diff from step 1 through it —
  `git diff | python3 "${CLAUDE_SKILL_DIR}/extract-candidates.py"`, then the
  same for `git diff --cached` (or the branch diff).
- **Path mode:** `python3 "${CLAUDE_SKILL_DIR}/extract-candidates.py" <files…>`.

Output is `path:line	flag	text`, one candidate per line (`+` added, `=`
context, `.` file scan); the candidate count goes to stderr. The script is
tuned for near-zero false negatives, so it emits *candidates*, not comments —
confirming each one in context is the verifier's job, not yours.

Zero candidates → report that and stop.

## 3. Delegate verification

Spawn the `comment-curator:verifier` agent. It holds the verdict rules and the
off-limits list; the agent sees none of this conversation, so its prompt must
be self-sufficient:

1. The mode — **diff** or **path** — stated explicitly.
2. The candidate lines from step 2, verbatim (all of them; the verifier
   discards false positives, you don't pre-filter).
3. That it must return the verdict table and observations in its documented
   format, nothing else.

**Fan out when the inventory is large.** Above ~150 candidates or ~15 files,
split by file into 2–4 verifiers with roughly balanced candidate counts —
never split one file across verifiers — and spawn them in parallel, each with
the same mode and its own slice. Merge the returned tables in file order.

While verifiers run, do not start reading the scoped files "to get ahead" —
the whole point is that those tokens are spent in the agent's context, not
here.

## 4. Verdict table and approval

Present the merged table: `file:line` · comment (truncated) · verdict ·
one-line reason · action (for stale: the replacement text or "delete"). Then
totals. Collapse `skip` rows (confirmed non-comments) into a single count —
they need no user decision.

Below it, the verifiers' **observations** section: things noticed but not
acted on in this pass. Report only — these are future work, not edits.

Then ask, via AskUserQuestion: **apply all** / **apply only commented-out code
deletions** (the safest subset) / **adjust** (loop back with their exceptions)
/ **abort**. Nothing is edited before an explicit choice.

## 5. Apply and verify

Apply the approved verdicts with Edit — comment lines only, reading only the
files being edited (this is the one place you open scoped files, and only the
approved ones). If a verifier row's line number doesn't match what you find on
disk, skip that row and say so — never guess at a drifted line. Then two
checks:

1. **Self-diff.** Run `git diff` on the touched files and confirm every changed
   line is a comment line. Any code line in the diff means you slipped: revert
   that file and say so.
2. **Build, if discoverable.** Find the project's build or lint command the way
   the project defines it (`package.json`, `Makefile`, `*.csproj`, CI config) —
   comment edits must not change the outcome. A new failure means a functional
   comment got past the verifier's off-limits list (a directive, a doc comment
   under CS1591): revert that file, reclassify, and note it in the report. If
   no command is discoverable, say so.

## 6. Report

Counts per verdict, files touched, fixes vs. deletions, anything reverted by
the checks and why, and the observations list. If the user declined some
verdicts, don't relitigate them — record and move on.
