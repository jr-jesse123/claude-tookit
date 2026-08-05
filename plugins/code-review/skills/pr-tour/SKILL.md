---
name: pr-tour
description: Build a guided tour of a pull request or branch — how the changes connect (narrative plus Mermaid diagrams when they help) and a suggested file-by-file reading order with what to focus on in each. Use when the user wants to understand or start reviewing a PR, not to find bugs.
argument-hint: [PR number/URL or branch; defaults to current branch vs default branch]
allowed-tools: Bash(git fetch:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git merge-base:*), Bash(git symbolic-ref:*), Bash(gh pr view:*), Bash(gh pr diff:*), Read, Grep, Glob
---

# PR tour

Orient a reviewer before they read a single diff hunk: explain how the changes
connect, then say in what order to read the files and what matters in each.

This skill does not review. It reports no bugs, no style issues, no missing
tests — for findings, point the user to `/code-review:quick-review`. Write the
tour in the language the user is speaking.

## Resolve the target

Decide which diff to tour, in this order:

1. `$ARGUMENTS` looks like a PR number or URL → `gh pr view <ref> --json
   title,body,baseRefName,headRefName` for context, `gh pr diff <ref>` for the
   diff. If `gh` is missing or unauthenticated, say so and treat the argument
   as a branch name instead.
2. `$ARGUMENTS` is a branch → diff it against the merge-base with the default
   branch: `git diff $(git symbolic-ref refs/remotes/origin/HEAD)...<branch>`.
   If the symbolic ref is not set in this clone, fall back to `origin/main`,
   then `origin/master`. Run `git fetch origin` first when the remote refs
   look stale — a stale base silently drags already-merged work into the
   tour.
3. No argument → same as 2, with the current branch.

Also gather `git log --oneline` and `git diff --stat` for the same range. Use
the PR title, body, and commit messages as context for the narrative — the
author already said what they meant to do.

If the diff is empty, say so and stop. Do not tour the last commit unless the
user asks for it.

## Map the change

The diff alone rarely shows how pieces relate — read before you narrate.

1. Tag each changed file with a role: **contract** (types, schemas,
   interfaces, public API), **core logic**, **wiring** (call sites, routes,
   DI, config), **tests**, **generated** (lockfiles, snapshots, build
   output). These roles are a lens, not a form — for a diff that is mostly
   docs, config, or prose, substitute roles that fit (e.g. spec, procedure,
   example, manifest).
2. With Read and Grep, trace the connections *among the changed files*: which
   changed function is called by which changed caller, which new type flows
   into which consumer. This graph drives both the narrative and the order.
3. Split into independent groups. Two files belong to the same group only if
   one calls, imports, or tests the other — directly or through another
   changed file. A feature, an unrelated refactor, and a dependency bump are
   three groups. Docs and metadata that call nothing (README, manifests,
   changelogs) join the group they describe; when one such file spans several
   groups, put those files in a final housekeeping group instead of forcing
   them into one.

## Report — how the changes connect

A cohesive PR gets one tour. Independent groups each get their own complete
tour — narrative, optional diagrams, reading order — ordered from the most
substantive group to the most trivial. Do not add group headers when there is
only one group.

**Narrative.** One paragraph per group: entry point of the change → what
triggers what → net effect. Name real files and symbols, not abstractions.
This paragraph is the answer to "what do these changes do together?" — if the
reviewer reads nothing else, this must be enough to start.

**Diagrams.** Default is a single Mermaid `flowchart`: nodes are the changed
modules, edges are call or data flow between them, new nodes marked distinctly
from modified ones. Skip the diagram entirely when the group touches only 1–2
files — the paragraph covers it.

Multiple diagrams are an explicit option when distinct perspectives or zoom
levels help more than one picture can — for example, an overview `flowchart`
of the modules plus a `sequenceDiagram` of the runtime flow, or a macro map
plus a zoom into the most-changed subsystem. Each diagram must answer a
different question ("who depends on whom?" vs "in what order does it happen?"
vs "what does the hot spot look like inside?") and carries a one-line title
naming that question. If two diagrams answer the same question, keep one. The
criterion is clarity, never quantity.

## Report — reading order

Per group, a numbered list. Each entry has three parts:

```
1. `src/billing/schema.ts` — [Contracts] — first: every other change consumes
   the new `Invoice` type. Look at: the widened `status` union — everything
   downstream must handle the new value.
```

- **Why here** — the reason this file sits at this position in the order.
- **Look at** — the one or two things that matter in this file, concrete
  ("signature of `charge()` changed — check its callers follow") rather than
  generic ("review the logic").

Default ordering, to adapt whenever the actual flow disagrees: contracts
first, then core logic following the data flow, then wiring and call sites,
then tests (read them as the promised behavior — do they match the
narrative?), then generated files last, skim only.

**Category labels** like `[Contracts]` above are optional. Invent the 3–6
labels that fit *this* diff — Models, Integrations, Tests, Config, UI,
Migrations, whatever the changes actually contain — instead of forcing a fixed
taxonomy. When every file plays the same role, drop the labels; do not
classify for its own sake.

## What not to do

- No findings. If you notice a bug while mapping, one line at the end
  ("possible issue in X — run `/code-review:quick-review` to confirm") is the
  maximum.
- Do not restate the diff file by file — the reading order says where to look
  and why, not what changed line by line.
- Do not pad: no diagram that repeats the paragraph, no labels on a
  single-role diff, no group headers on a cohesive PR.
