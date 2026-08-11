---
name: adr
description: Draft one Architecture Decision Record, interviewing the user for the context, alternatives, and consequences the code cannot reveal. Use when a significant decision was made or is being made and its rationale should be recorded.
argument-hint: [the decision to record; defaults to mining the current diff and conversation]
allowed-tools: Bash(git diff:*), Bash(git log:*), Bash(git show:*), Read, Grep, Glob, Write
---

# Draft an ADR

Record **one** architecturally significant decision — its context, the
alternatives it beat, and what it trades away. The rules in
`${CLAUDE_PLUGIN_ROOT}/reference/right-sizing.md` (significance test,
human-vs-machine knowledge) govern every step. Interview the user in their
language; write the ADR in the language of the existing ADR log (or the
repository's dominant language for a first ADR).

## 1. Locate the log

Find the existing ADR convention: `docs/architecture/adr/`, `docs/adr/`,
`adr/`, `doc/architecture/decisions/`. An existing log wins over the plugin
template — match its numbering, filename style, and section structure. If
none exists, create `docs/architecture/adr/` (or the top-level `adr/` for a
repo with no `docs/`) using
`${CLAUDE_PLUGIN_ROOT}/reference/templates/adr.md`. Next number = highest
existing + 1.

## 2. Identify the decision — exactly one

From `$ARGUMENTS` if given; otherwise mine the current diff (`git diff`,
`git diff --cached`, recent `git log`) and the conversation for the decision
being made.

- Apply the significance test. If the decision does not pass, say so and
  recommend *not* recording it — declining is a correct outcome of this
  skill, not a failure.
- If the request bundles several decisions ("we chose Kafka and also moved
  to Postgres"), split them, confirm which to record now, and offer the rest
  as follow-ups. One ADR, one primary decision.

## 3. Gather machine-side evidence

Collect what the repository can honestly attest: the implementing diff or
commits, benchmark results checked into the repo, related contracts,
existing ADRs it touches. This becomes the *Evidence* section and the
implementation links — nothing more.

## 4. Interview the human

This is the load-bearing step. Ask **one batch** of questions covering:

- **Forces.** What pressure made this decision necessary now — technical,
  political, budgetary, regulatory?
- **Alternatives.** What else was evaluated, and why did each lose?
- **Negative consequences.** What is being consciously given up or accepted?
- **Outside evidence.** PoCs, benchmarks, incidents, or negotiations that
  exist outside the repo?
- **Reversibility.** How expensive is undoing this, and under which
  conditions should it be revisited?
- **Status and owners.** Proposed or already accepted? Who can confirm or
  revisit it?

Rules:

- Anything the user does not answer stays in the draft as an explicit open
  question — never filled with plausible prose. An invented rationale
  records an intent that never existed.
- Write the *Context* neutrally: describe the forces, do not defend the
  winner in advance.
- A decision with an empty *Negative consequences* section is being
  described superficially — push back once, then leave the open question.

## 5. Write and cross-link

Draft the ADR. Then:

- **Never rewrite the past.** If this decision replaces an accepted ADR, do
  not edit the old one's content — set its status to `Superseded by
  ADR-NNNN` and set `Supersedes: ADR-KKKK` in the new one. The reasoning
  trail is the point.
- Link the implementation: PRs, key files, contracts, diagrams affected. If
  a diagram in `docs/architecture/diagrams/` is now stale because of this
  decision, say so in the report — do not silently edit diagrams the user
  did not ask to change.

## 6. Report

State the file created, its status, the open questions still embedded in it
(quoted, so the user can answer inline), and any follow-up ADRs identified
in step 2. Do not commit.
