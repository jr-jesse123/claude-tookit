---
name: pr-shape-review
description: Review a feature branch before publication and recommend the smallest coherent linear-history shape: squash, recomposed commits, split PRs, or stacked PRs. Use when deciding how a branch should enter main, especially after agentic or exploratory development.
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

# Review PR shape

Analyze the current branch and recommend how it should be published into a
**linear main history**. This skill is advisory: do not rewrite history, create
branches, commit, push, or edit files.

Read `${CLAUDE_SKILL_DIR}/policy.yml` before analysis. Its invariants are
mandatory. In particular, never recommend a merge commit.

## Decision vocabulary

Return exactly one primary recommendation:

- **squash** — one semantic delivery; intermediate commits are operational,
  corrective, exploratory, broken, or not useful as permanent history.
- **recompose** — one semantic delivery with multiple independently meaningful
  stages worth preserving as a curated linear commit series.
- **split** — multiple independent semantic deliveries should become separate
  PRs.
- **stacked-split** — multiple semantic deliveries are separately reviewable
  and releasable, but have an explicit dependency order.
- **insufficient-context** — repository evidence is not enough to distinguish
  the shapes safely.

Do not use branch age, commit count, author count, or diff size alone as the
reason for any recommendation.

## 1. Establish the comparison range

The base branch is `$ARGUMENTS`, or the repository default branch when empty:

```bash
git symbolic-ref refs/remotes/origin/HEAD
git merge-base <base> HEAD
git rev-parse HEAD
git status --short
git rev-list --count <base>..HEAD
```

Stop with a clear message when:

- the current branch is the base branch;
- the branch has no commits ahead of base;
- the base cannot be resolved.

A dirty working tree is allowed for analysis, but state explicitly that the
recommendation includes uncommitted changes only when they appear in the diff
being reviewed.

## 2. Gather evidence

Collect at minimum:

```bash
git log --reverse --format='%H%x09%s%x09%an' <base>..HEAD
git diff --name-status <base>...HEAD
git diff --stat <base>...HEAD
git log --reverse --stat <base>..HEAD
git log --reverse -p <base>..HEAD
```

Read the PR description, issue, ADR, or task specification when available in
repository context. Never infer business intent solely from directory names.

Build these artifacts:

1. **Stated intent** — what outcome the branch claims to deliver.
2. **Semantic deliveries** — externally meaningful outcomes that could be
   reviewed, reverted, and released separately.
3. **Dependency graph** — which deliveries require which others.
4. **Current commit roles** — classify each commit as semantic, supporting,
   mechanical, corrective, checkpoint, exploratory, or incidental.
5. **Intermediate validity** — whether each candidate permanent stage appears
   coherent and buildable. Mark as unverified unless repository evidence or
   commands prove it.

## 3. Identify semantic boundaries

A semantic delivery should have all of these properties:

- one clear purpose and observable outcome;
- a review boundary that does not require unrelated changes;
- an intelligible revert boundary;
- no knowingly broken intermediate repository state;
- tests or other evidence that can travel with the behavior they verify.

Do not split merely by layer (`domain`, `infrastructure`, `UI`, `tests`). A
vertical slice may legitimately span all layers. Split only when outcomes are
independently valuable or independently releasable.

Treat incidental refactors, CI changes, formatting, dependency upgrades, and
unrelated bug fixes as candidate separate deliveries even when they were found
while implementing the main feature.

## 4. Choose the shape

Apply this order:

### Multiple deliveries

- If two or more deliveries can land in any order, recommend **split**.
- If they form an acyclic dependency chain and each stage remains useful and
  reviewable, recommend **stacked-split**.
- If apparent deliveries exist only to make one inseparable behavior compile,
  treat them as stages inside one delivery instead.

### One delivery

Recommend **recompose** only when every proposed commit:

- has a distinct semantic purpose;
- leaves a coherent repository state;
- keeps tests with the behavior they verify;
- improves at least one of review, bisect, revert, backport, or future agent
  comprehension;
- is not merely a correction of an earlier commit in the same branch.

Otherwise recommend **squash**.

Default to squash when evidence is ambiguous. Permanent granularity must earn
its cost.

## 5. Produce the report

Use this exact structure:

```markdown
## PR shape recommendation

**Recommendation:** squash | recompose | split | stacked-split | insufficient-context
**Confidence:** high | medium | low
**Base:** <base>
**Head:** <sha>

### Semantic deliveries
| # | Delivery | Evidence | Depends on |
|---|---|---|---|

### Current history assessment
| Commit | Role | Permanent value | Notes |
|---|---|---|---|

### Proposed publication shape
<one of the structures below>

### Why not the alternatives
- ...

### Uncertainties
- ...
```

For **squash**, propose one final commit subject and a concise body.

For **recompose**, propose an ordered commit table containing subject, purpose,
files or change cluster, verification, and dependency on prior commits. Describe
this as a reconstructed semantic sequence, not as the historical truth of how
the work happened.

For **split**, propose one PR per delivery with title, scope, verification, and
whether it can merge independently.

For **stacked-split**, provide the same information plus the base branch or
preceding PR for every item.

For **insufficient-context**, name the minimum missing evidence needed to decide.

## Handoff

When the recommendation is **recompose**, offer `/git-narrator:narrate` as the
execution path after the user approves the shape. Do not invoke it automatically.

For **split** or **stacked-split**, provide a safe branch construction plan but
do not execute it.

## Rules

- Main history is linear by policy.
- Never recommend merge commits.
- Never equate a long-lived feature branch with a durable product line.
- Never rewrite history while a PR is under active review without explicit
  reviewer agreement.
- Never claim an intermediate commit builds or passes tests unless verified.
- Prefer one coherent delivery over decorative commit granularity.
- Prefer several small PRs over one PR containing unrelated outcomes.
