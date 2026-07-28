---
name: quick-review
description: Review uncommitted changes in the working tree for correctness, edge cases, and accidental leftovers. Use when the user asks to review their changes, check a diff before committing, or sanity-check work in progress.
argument-hint: [optional path or glob to narrow the review]
allowed-tools: Bash(git diff:*), Bash(git status:*), Bash(git log:*), Read, Grep, Glob
---

# Quick review

Review the current working-tree changes. Be concrete: every finding must name a
file, a line, and what actually breaks.

## Gather the diff

Run these first, in one batch:

```
git status --short
git diff --stat
git diff
git diff --cached
```

If `$ARGUMENTS` is set, scope the diff to that path (`git diff -- $ARGUMENTS`).

If both the unstaged and staged diffs are empty, say so and stop — do not review
the last commit unless the user asks.

## What to look for

Work through these in order. Read surrounding context with Read before flagging
anything — a diff hunk alone rarely shows enough to judge correctness.

1. **Correctness.** Off-by-one, inverted conditions, missing `await`, unhandled
   error paths, wrong variable in a copy-pasted block.
2. **Edge cases.** Empty collections, null/undefined, zero, negative numbers,
   concurrent access, unicode in string handling.
3. **Leftovers.** Debug prints, commented-out code, `TODO` added in this diff,
   hardcoded local paths, test credentials, `.only` / `.skip` in test files.
4. **Contract drift.** A changed function signature, return shape, or error type
   whose callers were not updated. Grep for callers before claiming it is fine.
5. **Tests.** New behavior with no test, or a test changed to match a bug rather
   than the intent.

Skip style and formatting — that is the linter's job.

## Report

Group findings by severity, most severe first:

- **Blocking** — will break at runtime or ship a bug.
- **Worth fixing** — real but not urgent.
- **Nit** — optional; at most three, or omit the section.

Format each as `path/to/file.ts:42` followed by one sentence on the defect and
one on the concrete failure case (inputs → wrong result).

If nothing is wrong, say so in one line. Do not invent findings to fill the
report, and do not restate what the diff does — the user wrote it.
