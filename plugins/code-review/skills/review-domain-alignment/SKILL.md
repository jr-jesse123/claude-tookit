---
name: review-domain-alignment
description: Review a feature, bug, implementation plan, or diff for alignment between business commitments, domain concepts, and implementation guarantees. Use when a change challenges domain rules or system responsibilities, or introduces technical choices with observable business consequences and potentially unaccepted limitations, or when technically representable states create unnecessary business decisions.
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

## Review the decision space before escalating questions

For each material output, boundary, or combination that would require a new
business decision, first ask whether the state is reachable in the composed
implementation and whether it is legitimate under the evidenced domain contract.
Prioritize states whose uncertainty fans out across multiple consumers or
combinations. Do not exhaustively enumerate every theoretical combination.

Distinguish four kinds of evidence:

- **Domain invariant** — an agreed business rule excludes or requires a state
  within a stated scope.
- **Implementation guarantee** — a verified algorithm, contract, validation, or
  component configuration excludes or requires a state at a specified boundary.
- **Empirical observation** — sampled or historical data has or has not shown a
  state; document dataset, filters, period, and coverage where available.
- **Unknown** — evidence does not establish reachability or impossibility.

Never infer impossibility solely from an empty query result, passing tests, a
non-null annotation, or a developer's expectation. Conversely, do not escalate
hypothetical edge cases as business decisions before checking relevant producers,
guards, schemas, tests, data, and integration boundaries. Distinguish a state
that cannot be produced today from one forbidden by the domain: future changes,
migration, deserialization, external inputs, and races may invalidate a local
implementation guarantee.

For each material implementation choice, report its **decision-space delta**:

- **Opened questions** — new decisions caused by the selected mechanism,
  guarantees, missing guarantees, or their composition.
- **Closed questions** — questions made unnecessary by evidenced guarantees,
  with the exact scope and boundary where the guarantee holds.
- **Residual questions** — legitimate uncertainty, including questions that
  remain visible to consumers because a guarantee has not been propagated.

Check whether a closed question is actually closed for downstream consumers.
A producer returning only nonempty successful forecasts internally while
publishing an unconstrained list may leave the empty-success question open for
UI, persistence, and messaging. Recommend the smallest suitable contract, type,
validation, test, or decision record to preserve a verified guarantee; do not
assume every guarantee deserves a new type.

Before asking stakeholders to choose behavior for an edge case, state the
reachability evidence, the potential business impact, and why the question
cannot be eliminated. If evidence is incomplete, recommend bounded
investigation, defensive handling, or an explicit pending decision according to
risk. Do not silently discard an unknown state or claim a proof that has not
been established.

Example: a forecast output is combined with three other outputs. Before
asking for behavior for every empty-forecast combination, trace the forecast
producer and completion contract. If successful empty forecasts are impossible
by a verified guarantee, close those combinations within that boundary and
check that consumers can rely on it. If only historical data contains no empty
forecasts, record an observation, not an invariant, and keep appropriate
residual handling or verification.

## Audit decision authority and hazardous fallback behavior

Implementation pressure is not decision authority. For each material branch,
fallback, or error path introduced or changed by the implementation, trace the
decision from an evidenced business rule, accepted policy, or explicitly
delegated technical discretion to its observable effect. Distinguish:

- **Required behavior** — supported by an evidenced commitment.
- **Authorized technical choice** — within a documented delegation and without
  silently changing the business contract.
- **Unapproved policy inference** — a plausible interpretation selected merely
  to complete the code, without authority to define its business consequences.

Pay special attention to empty results, nulls, partial responses, stale data,
timeouts, retries, reconciliation, and recovery. Do not treat "no data returned"
as "the authoritative desired state is empty" without evidence of completeness,
source authority, and permission to replace existing state. Separate data
interpretation from authorization of side effects: even a legitimately empty
snapshot does not by itself authorize deletion.

Trace potentially destructive or hard-to-reverse effects, including deletion,
overwrites, financial changes, external messages, and irreversible transitions.
Check whether a speculative branch introduces a newly reachable hazardous
behavior under future producer changes, corrupted inputs, or combined failures,
even when the nominal path cannot currently reach it. Do not mark a branch safe
solely because it appears unreachable today.

If an unapproved interpretation could cause destructive effects, report it as
a material finding with the trigger, assumption, effect, missing authority, and
the smallest safe next step. Prefer preserving existing state and surfacing an
explicit failure or pending decision when this is consistent with established
requirements; do not invent a universal fallback policy. Never silently
choose a destructive default or accept a business policy on stakeholders'
behalf. Distinguish a proven contract violation from a risk that still needs
confirmation.

Example: a forecast sync returns an empty list. The agent infers that
synchronization should delete all stored forecasts. Challenge both premises:
does empty mean a complete authoritative snapshot, and does that authorize
deletion? If neither is evidenced, flag the inferred deletion policy even if
the empty output is currently unobserved or nominally unreachable. Recommend
a bounded guard/contract investigation and explicit authorization before
allowing the destructive path.

## Deliver a bounded review

Start with the reviewed target and the commitment you could establish. Summarize
the domain change and material decision-space changes (opened, closed, and
residual questions), then show only material findings in a compact table.

| Commitment and evidence | Decision or mechanism | Observable consequence | Status and next step |
| --- | --- | --- | --- |

For each mismatch or pending decision, provide a concrete input/event/failure
scenario and the expected versus implemented or proposed outcome. Cite exact
paths and lines or source references. Mark prospective claims as proposed.
Suggest the smallest compensating mechanism or decision needed without expanding
the current scope. Include the relevant success/boundary examples as candidate
acceptance criteria, clearly marked as proposed until agreed.

For each claimed closed question, cite the evidence and boundary; flag any
consumer that still exposes the eliminated state. Do not manufacture questions
for unreachable combinations. End with the few unresolved questions that
materially affect the result, including any unapproved policy inference,
and the limits of verification. If no material delta exists, say so briefly with the
review boundary. Do not manufacture findings or enumerate generic risks.

When revisiting an implemented plan, compare promised and delivered guarantees,
including newly introduced decisions. Suggest preserving accepted rules in
existing tests, types, or decision records as appropriate, without writing them.
The adjacent plan-tour and pr-tour skills can supply structural evidence, but
this review must substantiate its own business-alignment conclusions.
