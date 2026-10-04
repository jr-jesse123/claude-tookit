---
name: choose-execution
description: Recommend a computation form for large, repetitive, mixed, or paradigm-ambiguous work using a cheap grounding gate and optional Jev shape scan.
argument-hint: "[task description] [--no-scan] [--providers=anthropic,openai]"
disable-model-invocation: true
model: haiku
allowed-tools:
  - Read
  - Bash(git status *)
  - Bash(git diff --stat *)
  - Bash(git diff --name-only *)
  - Bash(git --no-pager diff --no-ext-diff --no-textconv *)
  - Bash(node *route-scan.mjs*)
  - mcp__plugin_jev-code_jev__jev_check
  - mcp__jev__jev_check
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Computation advisor

Advise on `$ARGUMENTS`, or the latest proposed task if empty. Return a routing
record; leave the task and repository unchanged. The only inference tool call
allowed here is one optional Jev shape scan. Handoffs are recommendations for
the caller to inspect, never skill invocations or execution commands to run.

Use the least expressive computation that preserves the requested meaning,
when the savings or guarantees justify reshaping. This skill chooses computation
form; `/model-router:choose-model` independently chooses a generative model.
Keep provider/model selection, review escalation, and calibration there.

## 1. Take the cheap exit or ground once

Use only the task, supplied evidence, and named local sources. Evaluate the
bypasses below from already supplied facts before collecting anything. Collect
only when no bypass settles the recommendation. Before reading source bodies,
decide whether acquisition is mechanical:

| Evidence state | Observable condition | Next step |
| --- | --- | --- |
| `self-contained` | The supplied state supports the opportunity questions; no lookup needed | Check the bypasses below |
| `cheaply-groundable` | Missing state has named files, an explicit diff range, or an existing log; collecting it needs no diagnosis | One bounded collection, then check the bypasses |
| `discovery-dependent` | Finding or selecting the relevant state needs hypotheses, call-chain tracing, semantic search, or unknown business rules | Skip scan; generative handoff |

**Decision separability:** if finding the context would do approximately the
same semantic work as deciding the task, route generatively immediately. When
that distinction is unclear, use `discovery-dependent`; do not investigate it.
The gate assesses evidence for an opportunity scan, not proof that the task is
solved. It never diagnoses, decomposes, or designs a transformation.

Collection budget: at most three explicitly named local sources and 12,000
characters of evidence in total, in one pass. These are initial overhead caps,
not model limits. Read exact supplied files/ranges or existing log excerpts;
for diffs disable external diff and textconv as in the allowed command. Do not
run tests/builds, search the repository, follow newly discovered references,
or summarize a large input with another model. If necessary state is missing,
stale, inaccessible, or over budget, report it and hand off generatively.
Never silently truncate required evidence to fit the cap.

Bypasses, before loading scanner material:

- A supplied exact mechanism and oracle already cover the entire task:
  recommend direct deterministic execution, naming both; do not execute it.
  A parser existing somewhere is insufficient if the task still needs judgment.
- Wholly open-ended generation with no visible exact or bounded-judgment portion,
  a trivial one-off with no material benefit from reshaping, or no stated
  reuse/scale/guarantee/savings basis: generative handoff. A mixed task does not
  qualify for the first bypass merely because some generation is obvious.
  Do not invent reuse counts, prices, or a payoff estimate.
- `--no-scan`, no available `jev_check`, or evidence cannot be sent through the
  configured Jev service under the project's existing permissions: generative
  handoff with the reason. Do not install/configure a service or inspect secrets.

Done when the evidence state and either a bypass reason or scan eligibility
are recorded. Stop inspecting after that point.

## 2. Scan opportunity, then apply local policy

Only on the eligible branch, read
`${CLAUDE_PLUGIN_ROOT}/reference/shape-scan.md` and its linked request template.
Submit the unchanged questions together over the bounded evidence. Jev reports
independent signals; it neither selects models nor invents transformations.

Run the local policy helper as specified in that reference. A failed call,
invalid response, or unavailable helper yields an explicit generative fallback.
Do not retry, call another scanner, or approximate the probabilities yourself.
The upstream transport may have its own bounded retries; this skill adds none.

Done when the helper returns a recommendation, or a failure is recorded. This
skill stops there. `determinize` is a separate, advisory design handoff;
`typify` and residual rescans remain future increments. Read
`${CLAUDE_PLUGIN_ROOT}/reference/architecture.md` only for architecture or
roadmap questions, never as a runtime prerequisite.

## 3. Return the advisory record

```text
Task: <objective and acceptance criteria>
Evidence: <self-contained | cheaply-groundable | discovery-dependent>
Grounding: <sources actually read; missing state; why collection was separable>
Scan: <skipped + reason | completed | failed + reason>
Signals: <IDs, raw probabilities and local verdicts; omit if scan did not complete>
Recommendation: <direct-deterministic | generative | consider-determinize | consider-typify>
Reason: <bypass reason or helper reason; cite the supplied payoff evidence>
Residual: <the original task, unchanged; no extraction has happened>
Next step: <advisory handoff below, or the already-known exact mechanism>
```

For a generative recommendation, suggest
`/model-router:choose-model "<task, constraints, acceptance criteria, evidence and unresolved facts>"`.
Preserve an explicit `--providers=` argument unchanged; otherwise leave provider
resolution to model-router. For an already explicit multi-part generative plan,
suggest `/model-router:plan-execution` instead; do not invent parts here.

For `consider-determinize`, suggest
`/execution-router:determinize "<original task, constraints, acceptance criteria, evidence, opportunity signals and payoff basis>"`.
Carry any explicit `--providers=` unchanged for later generative handoffs.
This is an opportunity requiring generative design, not a ready exact executor.
The caller may inspect the recommendation before invoking the skill; do not
load its instructions or start designing here.

For `consider-typify`, the specialized skill is not shipped yet. Suggest
`choose-model` for the bounded generative design task: preserve the original
acceptance criteria, identify only the covered judgment and its typed contract,
and return remaining work. Do not emit a runnable typify command.

The scan's overall payoff is preliminary: recheck the economics of the actual
proposed extraction before committing to modeling or execution work.
Carry all signals, including generative necessity and simultaneous opportunities,
into the handoff; do not declare the residual empty based on a scan.

For handoffs requiring model-router, if it is absent, return the same
self-contained text for a generative session and name the optional plugin.
The determinize handoff does not depend on model-router. Do not copy its policy here.
