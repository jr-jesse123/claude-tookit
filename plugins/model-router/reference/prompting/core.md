# Prompt adaptation core

Last reviewed: 2026-10-02

Shared invariants for `prepare-prompt`. Provider/model files describe behavioral
deltas; harness guidance describes context already supplied by the execution
environment. This file defines what may and may not change.

## Objective

Produce the **smallest prompt that preserves the task and improves fit for the
selected model/harness**.

Prompt adaptation is successful when it:
- preserves user intent and constraints exactly;
- removes redundant scaffolding;
- makes implicit completion criteria operational only when needed;
- adds model-specific guidance only when that behavior is relevant;
- avoids duplicating instructions already provided by the harness/project.

A longer prompt is not inherently better. Returning the original prompt nearly
unchanged is a valid and often desirable result.

## Priority order

When guidance conflicts, apply this order:

1. Explicit user intent and constraints.
2. Safety/permission boundaries.
3. Project/harness instructions already in force.
4. Task-specific success criteria and oracle.
5. Provider/model prompting guidance.
6. Style preferences.

Provider guidance must never override the user's requested outcome.

## Semantic lock

Preserve:
- objective;
- scope;
- constraints;
- requested output;
- relevant facts/context;
- explicit permissions and prohibitions;
- uncertainty the user intentionally left open.

Do not:
- invent requirements;
- broaden the task;
- strengthen a preference into a requirement;
- silently add deliverables;
- change the selected provider/model/effort/execution shape.

## Minimality test

For every line you add, be able to answer:

> What observed or documented model behavior does this line correct for this task?

If there is no concrete answer, omit it.

For every line you remove, be able to answer:

> Is this duplicated by the harness/project, semantically redundant, or obsolete
> scaffolding for an older model?

If not, keep it.

## Useful task structure

Structure is optional. When ambiguity warrants it, prefer these concepts:

- **Goal** — the desired outcome.
- **Context** — only facts the model needs.
- **Constraints** — hard boundaries.
- **Definition of done** — observable completion conditions.
- **Output** — only when a consumer needs a specific format.

Do not force headings/XML onto short prompts whose meaning is already obvious.

## Oracle-aware prompting

When an observable oracle exists, name it:
- compiler/build;
- deterministic tests;
- schema/validator;
- expected diff or query result;
- explicit acceptance criteria.

When the oracle is weak, do not manufacture certainty through stronger wording.
The router should already have selected a stronger model when weak-oracle risk
matters.

## Reasoning instructions

Do not request private chain-of-thought or add phrases such as:
- "think step by step";
- "show your reasoning";
- "reason extensively".

Current reasoning models expose effort/thinking controls outside the task prompt.
Use provider-specific effort settings instead of trying to micromanage internal
reasoning in prose.

It is fine to request concise decision rationale or evidence in the **final
answer** when that is part of the deliverable.

## Examples

Examples are useful only when they:
- encode a product/output contract that prose would express poorly;
- demonstrate an edge case;
- correct a measured failure mode.

Do not add examples merely because prompting documentation mentions few-shot
prompting.

## Tools and freshness

Mention tool/search use only when:
- the task depends on current/external information;
- a particular tool is required by the task;
- the selected model has a documented tendency not to trigger a needed tool.

Do not restate the entire tool catalog.

## Verification

Verification belongs in the prompt when:
- correctness has an observable oracle;
- failure would be costly enough to justify the work;
- the selected model may otherwise stop before checking.

Bound verification to the task. "Run affected tests" is often better than
"run the entire suite".

Do not add independent second-pass verification when the model/harness already
self-verifies adequately and independent perspective is not part of the task.

## Completion and assumptions

When the task should proceed autonomously, it may help to state:
- continue until the definition of done is met;
- make reasonable reversible assumptions when details are non-material;
- stop and ask only when missing information would materially change the result
  or make the action unsafe.

Add this only when premature check-ins are plausible for the selected model or
the task is genuinely autonomous.

## Provenance

Prompting policy files should distinguish:
- **provider guidance** — documented by the model vendor;
- **project rule** — this repository's conservative interpretation;
- **calibrated rule** — measured on the user's own workflows.

Durable external findings belong in the policy file with a date and primary URL.
