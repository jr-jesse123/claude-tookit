---
name: compose-execution
description: Coordinate bounded, read-only execution reshaping across grounding, determinize, typify and a remaining-work handoff. Resume explicit checkpoints without repeating transformations or losing residual obligations.
argument-hint: "[task and evidence, or existing composition record plus stage result] [--no-scan] [--providers=anthropic,openai]"
disable-model-invocation: true
model: haiku
allowed-tools:
  - Read
  - Bash(node *compose-residual.mjs*)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Residual composition advisor

Coordinate `$ARGUMENTS`, or resume the latest supplied composition record.
Return the record and one next action in chat. Do not dispatch skills, call Jev,
execute work, install tools or write state to disk. This is a resumable advisory
pipeline, not an autonomous orchestrator or cross-paradigm execution planner.
Direct use of choose-execution, determinize, typify and model-router stays valid.

## Establish or resume a checkpoint

Read `${CLAUDE_PLUGIN_ROOT}/reference/residual-record.md` for the record and
helper interface. Start from the original objective, stable acceptance criterion
IDs and all constraints. Do not invent a decomposition. If they are missing,
request the missing input; do not investigate the domain to create it.
Keep explicit provider arguments and `--no-scan` in every applicable handoff.

On resume, retain the original task, all earlier steps and every accepted
contract. Match the returned stage and revision to the pending checkpoint.
If a result is missing, wait for it or record the caller's explicit failure or
cancellation; do not start the stage again. Interrupted attempts consume their
budget. A missing/contradictory history needs repair, not a fresh task identifier.

Use the pure helper to determine the next action. Pipe the supplied JSON through
stdin to `node "${CLAUDE_PLUGIN_ROOT}/scripts/compose-residual.mjs"`; do not
interpolate task text into executable shell syntax. If the helper is unavailable,
stop with the unchanged record and a self-contained handoff, not an invented
policy result. The helper validates accounting, not semantic correctness.

## Follow the next action

| Action | Advisory checkpoint |
| --- | --- |
| `ground-and-scan` | Suggest `/execution-router:choose-execution` on the current residual with original criteria/constraints, relevant evidence, current payoff basis and flags. Return here with its complete record and raw scan, if any. |
| `determinize` | Suggest `/execution-router:determinize` with that same residual, evidence and signals. Record a pending attempt before handing off. |
| `typify` | Suggest `/execution-router:typify` with that same residual, evidence and signals. Record a pending attempt before handing off. |
| `await-result` | Show the pending stage and revision; no further calls. |
| `direct-deterministic` | Stop routing; retain the residual as pending exact execution with its supplied mechanism/oracle. |
| `generative-handoff` | Stop reshaping; identify remaining generative work for model-router, keeping exact/typed execution and human fallbacks as separate pending obligations. |
| `design-complete` | No semantic residual; implementation, evaluation, execution and assembly remain pending. Never report the task as done. |
| `repair-record` | Preserve the entire record and original task; ask for correction of the missing/stale/conflicting checkpoint. No new scan or design attempt. |

Each grounding checkpoint uses choose-execution's cheap gate and collection
budget, not new discovery by this coordinator. Reuse supplied evidence only
where still valid. If obtaining the correct state essentially performs the
judgment, skip Jev and stop reshaping. Missing permissions/tools, `--no-scan`,
trivial work, no current payoff basis or excessive context cost take its normal
bypass. Do not load transformation or scanner instructions speculatively.

Budgets belong to the original task: at most one determinize attempt, then at
most one typify attempt. At most two scan opportunities: initially and after an
accepted determinize changes a nonempty residual. No scan after typify; there
is no remaining transformation to inform. No retries, backward edges, cosmetic
rewordings, or resets on resume. An exception requires a separately authorized
new budget and concrete new evidence; this helper does not implement overrides.

An unchanged/rejected exact design can advance to a still-supported typed
opportunity from the same scan without rescanning. A changed residual needs a
fresh cheap gate and current payoff evidence; old signals cannot justify typify.
Even if the fresh scan still prefers exact reshaping, that attempt is spent:
local policy may choose its independent typed signal, otherwise it stops.
Candidate-specific economics remain the design skill's responsibility; overall
scanner payoff cannot authorize every candidate's modeling cost.

## Preserve meaning before accepting a result

Check the supplied design's criterion coverage, constraints, dependencies,
economics and recomposition against its input. Accept only a complete design
contract from the corresponding skill, with explicit pending work. Every input
criterion belongs to the extracted contract, the residual, or both. Partial
coverage and conditional human/generative fallbacks require `both` or `residual`.
Retain exact work left outside a contract; residual does not mean generative-only.

This check is bounded comparison of supplied artifacts, not another design
pass. If coverage/semantics cannot be established cheaply, do not set `reviewed`:
preserve the input as residual and record no extraction with the reason. Do not
repair a design here or treat a scalar confidence/empty string as proof of
coverage. A proposal neither implements a mechanism nor executes its oracle.

Return: original objective/constraints, current revision and residual, accepted
contracts with criterion coverage and recomposition, pending work including
conditional fallbacks, attempt/scan counts, one advisory next step, and the full
resumable JSON record. Do not discard earlier contracts to shorten the handoff.
For remaining generative design/implementation/judgments, suggest
`/model-router:choose-model` with a self-contained description and unchanged
`--providers=`. If absent, give that same text for a generative session.
Do not allocate models across exact/typed work, move plan-execution, select
reviewer families, or modify provider policy, R0-R4 or calibration.
