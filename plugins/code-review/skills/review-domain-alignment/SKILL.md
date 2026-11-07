---
name: review-domain-alignment
description: Review a feature, bug, implementation plan, or diff for alignment between business commitments, domain concepts, and implementation guarantees. Use when a change challenges domain rules or system responsibilities, or introduces technical choices with observable business consequences and potentially unaccepted limitations.
argument-hint: [request, plan, PR, branch, or paths to review]
---

# Review domain alignment

Make implicit decisions visible so the user can judge whether the system fulfills
its agreed responsibility at its current scale. Work read-only. Return the review
in the user's language. Do not implement fixes, update business records, accept
limitations on behalf of stakeholders, or invoke other skills automatically.

## Establish the review boundary

Resolve the supplied request, plan, PR, branch, or paths from `$ARGUMENTS` and
the conversation. Identify the relevant bounded context, intended outcome,
current responsibility, and scale constraints supported by evidence.

For a working-tree review, include staged, unstaged, and relevant untracked
files. For a branch or PR, establish the base and head and inspect their diff.
For a plan, distinguish existing behavior from proposed mechanisms throughout.
If the target is ambiguous, ask one focused question before drawing conclusions.
An empty diff has no implementation delta to review. Do not substitute the last
commit. A supplied request or plan can still be reviewed on its own.

Read repository instructions and relevant requirements, decisions, tests, code,
configuration, and consumers. Use connected sources only when relevant and
accessible. Follow the affected behavior beyond changed files, stopping when
the evidence is sufficient to assess the commitment. Avoid a repository-wide audit.

## Reconstruct the commitment

Keep these evidence categories explicit wherever they affect a conclusion.

- **Agreed expectation** — cite the user's instruction, acceptance criterion,
  or recorded business decision and its scope/date when available.
- **Observed implementation** — cite code, configuration, or test evidence.
  Distinguish what a test asserts from what was actually executed.
- **Hypothesis** — label an inference and explain what would confirm it.
- **Pending decision** — identify the missing choice and its behavioral impact.

Code and passing tests establish current behavior, not stakeholder agreement.
Do not infer agreement from silence, an old implementation, a proposed plan, or
documentation that merely describes the system. Surface conflicting sources and
uncertain applicability. State inaccessible evidence and narrow conclusions.

Ask what the request challenges: an implementation defect, an inaccurate mental
model of existing code, a missing domain distinction, a changed business rule,
or an expanded responsibility. Keep multiple explanations open when necessary.
Do not label a previously adequate model wrong merely because scope has grown.
Consider whether existing records retain old semantics or require migration.

## Trace decisions into behavior

For each material choice, connect the requested outcome to the domain concept,
implementation mechanism, resulting guarantee, and observable consequence.
Include decisions embedded in existing components newly used by this change.

Investigate only dimensions touched by the evidence. Examples include atomicity,
ordering, repetition, concurrency, consistency delay, timeout outcomes, rounding,
identity, retention, capacity, and responsibility for recovery. Translate each
relevant constraint into a concrete scenario a stakeholder could recognize.

Verify component guarantees against the actual version and configuration, using
primary documentation when necessary. Review the composed path end to end.
Retries, transactions, deduplication, an outbox, or recovery may compensate for a
component limitation, but verify their scope, failure windows, and consumers.
Do not infer an end-to-end guarantee from a component's name or marketing claim.

Use contrasting examples that require different outcomes to expose hidden
assumptions. For instance, volume allocation among two carriers and a primary
carrier with a backup have different rules despite both storing two carrier IDs.
Include a failure or boundary case when it changes the promised behavior.

Classify material results as follows.

- **Aligned** — sufficient evidence shows the composed behavior meets the agreement.
- **Mismatch** — a concrete scenario contradicts an evidenced commitment.
- **Decision pending** — the proposed behavior adds or changes a commitment whose
  acceptance is unknown. Explain the viable choices and their consequences.
- **Accepted limitation** — cite explicit acceptance and its scope. Check that
  the current change remains within it.
- **Insufficient evidence** — name the specific missing evidence and affected claim.

A documented limitation is still pending until accepted by the appropriate
decision-maker. If constraints make the commitment infeasible, explain which
design or commitment must be reconsidered. Do not silently relax the requirement.
Keep already authorized technical choices within that authorization. Ask only
about unresolved choices that materially change the judgment.

## Deliver a bounded review

Start with the reviewed target and the commitment you could establish. Summarize
the domain change, then show only material findings in a compact table.

| Commitment and evidence | Decision or mechanism | Observable consequence | Status and next step |
| --- | --- | --- | --- |

For each mismatch or pending decision, provide a concrete input/event/failure
scenario and the expected versus implemented or proposed outcome. Cite exact
paths and lines or source references. Mark prospective claims as proposed.
Suggest the smallest compensating mechanism or decision needed without expanding
the current scope. Include the relevant success/boundary examples as candidate
acceptance criteria, clearly marked as proposed until agreed.

End with the few unresolved questions that materially affect the result and the
limits of verification. If no material delta exists, say so briefly with the
review boundary. Do not manufacture findings or enumerate generic risks.

When revisiting an implemented plan, compare promised and delivered guarantees,
including newly introduced decisions. Suggest preserving accepted rules in
existing tests, types, or decision records as appropriate, without writing them.
The adjacent plan-tour and pr-tour skills can supply structural evidence, but
this review must substantiate its own business-alignment conclusions.
