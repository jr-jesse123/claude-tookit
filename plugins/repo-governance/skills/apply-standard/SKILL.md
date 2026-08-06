---
name: apply-standard
description: Plan and apply a safe default GitHub repository governance standard: linear default-branch history, pull-request-only changes, no force pushes or deletion, automatic Copilot review, resolved review threads, clean merge defaults, and optional repository-specific status checks.
argument-hint: "[owner/name] [--human-approvals N] [--required-check CONTEXT ... | --clear-required-checks] [--review-drafts]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Bash(gh auth status *)
  - Bash(gh repo view *)
  - Bash(command -v python3)
  - Bash(command -v python)
  - Bash(python3 ${CLAUDE_SKILL_DIR}/apply-standard.py *)
  - Bash(python ${CLAUDE_SKILL_DIR}/apply-standard.py *)
---

# Apply the repository standard

Configure one GitHub repository using the declarative policy in
`${CLAUDE_SKILL_DIR}/standard.json` and the idempotent executor
`${CLAUDE_SKILL_DIR}/apply-standard.py`.

This is an administrative write. Always plan first, show the complete target and
diff, and apply only after explicit user approval.

## Standard

The default branch receives one active ruleset with no bypass actors:

- deletion is restricted;
- force pushes are blocked;
- linear history is required;
- all changes must arrive through a pull request;
- squash and rebase are the only allowed publication methods;
- all review conversations must be resolved;
- Copilot code review is requested automatically on every push;
- draft PRs are not reviewed by default.

Repository merge settings are aligned with that ruleset:

- merge commits disabled;
- squash and rebase enabled;
- auto-merge enabled;
- merged head branches deleted automatically;
- update-branch enabled;
- squash title taken from the PR title;
- squash body taken from the PR body.

The standard requires **zero human approvals by default**. Requiring a PR and
resolving review threads still creates an integration boundary without
deadlocking a solo repository. Team repositories should usually override this
with `--human-approvals 1` or a stricter organization policy.

On an existing `Standard default-branch governance` ruleset, omitted CLI options
preserve repository-specific approval count, required status checks, and draft
review preference. Removing or replacing those overrides must be explicit.

## 1. Resolve the target

Use the first plain `owner/name` argument when supplied. Otherwise resolve the
repository from the current checkout:

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Run `gh auth status` and stop if the authenticated account lacks repository
administration permission. Never guess a repository from directory names.

## 2. Choose repository-specific additions

The base standard deliberately omits rules that cannot be safe across every
repository.

### Required status checks

Add `--required-check "<exact context>"` once per stable CI check that must pass.
Supplying one or more replaces the checks managed by this standard ruleset.
Omitting the option preserves existing checks. Use `--clear-required-checks`
only when the user explicitly wants to remove them.

Use only exact context names observed in the repository's existing successful
checks or documented workflow contract. Never guess names: a nonexistent
required check permanently blocks merging.

Prefer requiring the cheapest authoritative checks, typically:

- build or compile;
- unit tests;
- lint/typecheck when it protects a real invariant;
- the marketplace/repository validator for tooling repositories.

Do not require every matrix leg merely because it exists. Require the smallest
set whose success means the PR is safe to integrate.

### Human approvals

- Personal/solo repository: creation default `0`.
- Active team with independent review: usually `--human-approvals 1`.
- Regulated or high-blast-radius repository: decide separately; do not infer a
  count from repository size.

Omitting `--human-approvals` preserves the existing value in this standard
ruleset. Copilot reviews are comments, not approvals, and do not satisfy a
required human approval.

### Draft review

Use `--review-drafts` only when early feedback is worth the additional review
runs and noise. Use `--no-review-drafts` to turn it off explicitly. Omitting both
preserves the existing preference; a new ruleset defaults to reviewing open PRs
and every subsequent push, but not drafts.

## 3. Produce the plan

Select `python3` when available, otherwise `python`. Run without `--apply`:

```bash
python3 "${CLAUDE_SKILL_DIR}/apply-standard.py" \
  --repo owner/name \
  [--human-approvals N] \
  [--required-check "context" | --clear-required-checks] \
  [--review-drafts | --no-review-drafts]
```

The script returns:

- current and desired repository settings;
- whether settings need an update;
- the existing matching ruleset, when present;
- whether the ruleset will be created, updated, or left unchanged;
- the exact desired rules and target repository.

Read the plan critically. In particular, verify:

1. the repository is exactly the one requested;
2. the ruleset targets `~DEFAULT_BRANCH`;
3. no unknown required status check was introduced;
4. approval count fits solo versus team operation;
5. there are no bypass actors;
6. Copilot review availability is appropriate for the repository/account.

If the plan is already a no-op, report that the repository conforms and stop.

## 4. Ask for approval

Present a concise table:

| Area | Current | Desired | Action |
| --- | --- | --- | --- |
| Merge methods | ... | squash + rebase | ... |
| Default branch | ... | PR-only, linear, no delete/force | ... |
| Review | ... | threads resolved, Copilot automatic | ... |
| CI | ... | named required checks or none | ... |
| Human approval | ... | N | ... |

Then ask **apply / adjust / abort**. Do not execute an administrative write
before an explicit `apply`.

## 5. Apply

After approval, rerun the identical arguments plus both safety flags:

```bash
python3 "${CLAUDE_SKILL_DIR}/apply-standard.py" \
  --repo owner/name \
  --apply \
  --confirm-repo owner/name \
  [the same overrides used in the approved plan]
```

`--confirm-repo` must exactly equal the resolved target. The executor upserts
the named ruleset rather than creating duplicates and patches only the declared
repository settings. If ruleset application fails after merge settings were
changed, it attempts to restore the previous merge settings and reports both
failures if rollback also fails.

Run the plan command once more afterward. Success means every action reports
`none`. Report any API rejection exactly; do not silently weaken the policy to
make the call pass.

## What is intentionally not defaulted

Do not add these without repository-specific evidence:

- **Required signed commits:** valuable in some supply-chain models, but can
  create unnecessary friction for agents, bots, web edits, and contributors.
- **Code-owner approval:** needs a maintained `CODEOWNERS` file and an actual
  ownership model.
- **Required deployments:** only meaningful when stable protected environments
  exist.
- **Code scanning or code-quality gates:** require the corresponding GitHub
  product and established results.
- **Merge queue:** valuable under high merge concurrency, unnecessary overhead
  for low-volume repositories.
- **Restrict updates:** would prevent normal PR merges unless a bypass design is
  added.
- **Copilot review effort level:** configured separately in GitHub's Copilot
  settings and may consume additional Actions minutes/AI credits.

## Rules

- Plan is the default; writing requires `--apply` and exact repository
  confirmation.
- Never replace or delete unrelated rulesets.
- Never invent status-check context names.
- Never create a bypass actor merely to make an update succeed.
- Never lower an existing stricter organization rule.
- Never claim Copilot review replaces human accountability.
- If GitHub rejects a rule because the repository plan or Copilot entitlement
  does not support it, report the unsupported capability and leave the existing
  policy intact.
