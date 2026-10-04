---
name: determinize
description: Design a semantics-preserving extraction of an exact portion of a task, naming its deterministic mechanism, oracle, economics, and remaining semantic work. Returns a proposal or no extraction; never implements it.
argument-hint: "[task, evidence, acceptance criteria and payoff basis] [--providers=anthropic,openai]"
disable-model-invocation: true
model: opus
effort: high
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git diff --stat *)
  - Bash(git diff --name-only *)
  - Bash(git --no-pager diff --no-ext-diff --no-textconv *)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Exact extraction designer

Design one useful exact portion of `$ARGUMENTS`, or the most recent task and
handoff. Direct invocation is supported: a Jev scan, model-router installation,
and a previous choose-execution record are optional. Treat scanner signals as
leads, not proof of equivalence or economic value.

This is a generative design step, after deciding that reshaping may pay. Return
a proposal in chat. Leave files and external state unchanged; do not implement,
run commands/tests, invoke Jev, rescan, or execute a handoff. Read-only Git
inspection from the allowlist is permitted. One invocation considers one
candidate extraction; it is not a search over alternative architectures.

## 1. Preserve the task and check the investment

Record the original objective, acceptance criteria, constraints, evidence and
unknowns. Give the supplied criteria stable IDs for the coverage record below;
do not substitute easier criteria. An inherited residual is the input task for
this invocation; retain any original constraints that still apply to it.

If the supplied exact mechanism already covers the whole task and its oracle
is adequate, return `already-exact` with that mechanism and remaining execution
obligations. No new abstraction is needed. This fast exit precedes the economic
gate: there is no new transformation cost to amortize.

Choose a candidate portion from the supplied opportunity or plainly visible
structure. Name the specific reuse, volume, execution savings, or guarantee
gain that could outweigh its modeling, integration, evaluation and maintenance
cost. The scanner's overall payoff is insufficient when only a different
portion would benefit. Qualitative evidence is acceptable; invented timing,
reuse counts, prices and ROI are not. If benefit is absent, outweighed or too
uncertain to justify design, return `no-extraction` before further inspection.

Done when there is one candidate with a concrete payoff basis, or an early exit.

## 2. Design the exact portion

Use the supplied state first. If needed, inspect only the named scope in one
bounded pass: at most six files or existing log/diff excerpts, 24,000 characters
total. Scope Grep/Glob to that scope; do not run repository-wide discovery or
follow a growing call chain. These are initial design-overhead caps, not model
limits. Missing business meaning, inaccessible evidence, or a larger discovery
problem remains explicit residual work; do not solve it just to enable routing.

Describe the smallest exact mechanism that serves the candidate: for example,
a parser with a specified grammar, calculation, exact lookup, AST rewrite,
constraint solver, or deterministic check. Name its inputs, outputs, applicable
domain, preconditions and handling of invalid/out-of-domain inputs. Include
ordering, duplicates, precision, identity and side effects when material.

Distinguish deterministic execution from correct interpretation: a regex,
fixed model seed, cached LLM answer, or deterministic program implementing an
unproven heuristic does not establish semantic equivalence. Unknown rules stay
unknown. If an upstream judgment selects parameters, preserve that judgment as
a dependency; the exact mechanism is conditional on those inputs being valid.

Name the oracle for the *original* criterion and explain why it can detect a
wrong extraction. A compiler or schema check proves only its covered property;
a second copy of the implementation is not independent evidence of semantics.
State concrete boundary cases and at least one plausible counterexample that
would invalidate the proposed extraction. These are proposed checks, not test
results. Preserve disputed or unsupported meaning as residual rather than
declaring an approximate replacement exact.

Done when the mechanism, domain, oracle and limitations are specific enough
for another implementer to use without inventing business rules. Otherwise
return `no-extraction`, naming the missing fact or failed condition.

## 3. Account for the residual and recheck payoff

Account for every original criterion in a coverage table: exact obligation,
semantic residual, or explicitly split with both obligations named. Include
cross-cutting constraints in that accounting. Describe how exact outputs and
remaining judgments recombine to satisfy the original task, including any
upstream dependencies. Neither omission nor duplicated ownership closes a gap.

Recheck the candidate's economics against the actual proposed mechanism and
coordination cost. If the proposal is too costly or weakens meaning, return
`no-extraction`: empty extraction, original input task unchanged as residual.
Do not substitute another candidate, loosen the oracle, or recursively retry.

For a valid proposal, the semantic residual preserves every obligation not
covered by the exact contract, including exact work deliberately left outside
this extraction. It need not be purely generative. It may be `none` only when
every criterion and applicable constraint is accounted for. Implementation,
execution, validation and assembly
still belong in **Work remaining**, even when semantic residual is `none`.
A contract is not an executed result, and its oracle is not evidence of passing.

Done when coverage is exhaustive, recomposition is explicit, and the actual
extraction has an economic justification or has been rejected.

## 4. Return the contract

```text
Status: <proposed-extraction | no-extraction | already-exact>
Original task: <objective, unchanged criteria with IDs, constraints>
Evidence and unknowns: <sources actually inspected; assumptions and missing facts>
Economics: <candidate-specific benefit, setup/coordination cost, decision and uncertainty>
Exact portion: <covered work; none for no-extraction>
Mechanism: <algorithm/tool, input/output contract, domain, preconditions, failure behavior>
Oracle: <original property checked, independent basis, proposed boundary/counterexample cases, limitations>

Coverage:
| Criterion or constraint | Exact obligation | Semantic residual |
| --- | --- | --- |
<every criterion/constraint, split explicitly where necessary>

Semantic residual: <self-contained uncovered obligations and inherited constraints, or none with coverage justification>
Recomposition: <dependencies, exact outputs consumed by residual, and assembly obligations>
Work remaining: <implementation, execution, checks and assembly; none performed here>
Next step: <one advisory handoff, with the contract and residual as separate deliverables>
```

On `no-extraction`, omit Mechanism/Oracle when none is supported, explain the
failure, and preserve the original task verbatim where practical in the residual.
For `already-exact`, identify the supplied mechanism without designing a new one.

Suggest `/model-router:choose-model` only for generative implementation/design
or unresolved judgments in the residual, carrying constraints, acceptance
criteria, evidence, unknowns, and any explicit `--providers=` unchanged. Existing exact execution
needs neither router. If model-router is absent, return the same self-contained
handoff for a generative session. A clearly bounded typed opportunity may be
handed to `/execution-router:typify` with its evidence and payoff basis. This is
advisory only; do not auto-invoke it or orchestrate a residual pipeline here.
If this design came from a pending `/execution-router:compose-execution`
checkpoint, suggest returning this full output there with its input revision;
let that coordinator account for attempts and choose the next stage.

For a matching example or a disputed exact/residual split, read only the relevant
section of [worked examples](examples.md). They illustrate contracts, not measured
model performance or reusable business defaults.
