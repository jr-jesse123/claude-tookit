# Mixed-plan contracts and worked examples

Read the family contract when assigning a part; read a worked case when its
dependency or readiness issue matches the task. These are illustrative plans,
not live Jev outputs, measured savings or completed runs.

## Family contracts and readiness

| Family | Required contract | What does not establish readiness |
| --- | --- | --- |
| Deterministic | Exact mechanism, input semantics/preconditions, output contract, independent oracle and invalid-input behavior | A proposed parser, successful compilation, or a keyword approximation to an unknown business rule |
| Typed decision | Supplied state/questions, applicability, deterministic thresholds/uncertainty/failure policy, fallback, evaluation and adapter/call caps | An opportunity scan, uncalibrated confidence, unavailable state or an unimplemented adapter |
| Generative | Self-contained objective, constraints, evidence/dependencies, expected artifact and oracle; matched model-router record or explicit pending routing | A model name chosen from memory or a route for a different part/input |
| Human obligation | Named responsible role/process, inputs, activation, output and availability; no invented person | An unnamed "ask someone" branch or treating silence as approval |

When a typed contract is incomplete, preserve its unresolved fields. Use a
design checkpoint or fallback-only behavior already defined by that contract;
the planner does not invent thresholds. TypeSafe remains the canonical design
knowledge used by typify, and jev-code remains the execution adapter. Missing
tools/configuration/permissions remain explicit prerequisites; planning does not
install or authorize them. Secrets are not part of handoff artifacts.

Keep a part's purpose separate from its executor family: a test run may be
deterministic, writing those tests may be generative, and reviewing their coverage
may require an independently routed generative part. Reuse model-router's returned
review contract without deriving a new assurance level here.

## Case A: recurring reconciliation, classification and explanation

Supplied criteria: C1 exact ID/decimal reconciliation including duplicates; C2
bounded anomaly labels with uncertainty fallback; C3 explanation without invented
causes. Constraints: private ledger stays in permitted systems; immutable input
snapshot; no corrective payments. Recurrence supplies the economic reason to
separate exact volume from semantic decisions. The planner does not fabricate
volume, token prices or a savings percentage.

Assume supplied exact/typed designs and *verified existing* implementations.
The typed policy defines valid, uncertain and failed outcomes, and permits a
generative fallback over the same bounded anomaly evidence. Service permission,
state completeness, threshold validation and fallback availability must actually
be established before runtime use. Otherwise retain them as blockers.

| ID | Part / family | Inputs and dependencies | Output / oracle |
| --- | --- | --- | --- |
| P1 | Run exact reconciliation / deterministic | Supplied immutable ledgers, validated decimal/duplicate rules | Difference records with provenance; independent reconciliation fixtures and total invariants |
| P2 | Apply anomaly policy / typed-decision | P1 records and supplied taxonomy/state contract | Accepted labels plus unresolved records; deterministic policy checks, not confidence as proof |
| P3 | Resolve exceptions / generative, conditional | P2 unresolved records and original evidence; activate only when unresolved set is nonempty | Resolution records or explicit unresolved facts; traceable evidence and stated rubric |
| P4 | Join labels / deterministic | P2 normal results plus P3 resolution OR an explicit skipped-empty result | Every anomaly has an accepted outcome or remains unresolved; no silently dropped IDs |
| P5 | Explain outcomes / generative | P1 differences and P4 joined outcomes | Explanation plus structured ID references; preserve uncertainty and avoid unsupported causes |
| P6 | Validate assembled references/totals / deterministic | P5 structured ID references, P1 and P4 | Exact coverage and amount checks; not proof of narrative correctness |

P3 and P5 each receive their own model-router handoff. No provider/model/effort
is invented here. Any required independent review from those returned routes
must remain visible in their subplans/dependencies; P6 does not replace it.
The plan is `routing pending` until matched routing records arrive.

The sequence is P1 -> P2 -> conditional P3 -> P4 -> P5 -> P6. P4 must not wait
forever for an inactive P3, nor run early on uncertainty. P3 failure keeps the
affected records unresolved and blocks a complete C2 result. A fully negative
but valid typed answer is not the same as transport failure. Calls/retries use
the supplied typed contract's bounds. There is no automatic retry loop or
unjustified parallel work in this example.

If C2 instead requires a human reviewer, P3 becomes a `human` obligation with
that supplied role/process and availability. It is never routed to model-router.
If no such role is available, expose the blocker; do not auto-approve labels.

Coverage: C1 -> P1/P6; C2 -> P2/P3/P4; C3 -> P5 and its model-router review
contract, with P6 covering only exact references. All constraints apply globally.
Artifacts travel through permitted caller-carried records; notifications are
manual in this advisory version. Count that relay cost in the payoff.

## Case B: composition returned designs, but nothing is implemented

Input is a #44 record with an accepted exact contract, a proposed typed contract
with unresolved thresholds, and an explanation residual. Replay/retain the
record and all its spent attempts. A `design-complete` result is not runtime
readiness; the record's `workRemaining` is still part of the task.

First stage:

1. Generative implementation of the exact mechanism and independent oracle
   fixtures from the exact contract. Route with model-router.
2. Generative implementation of the typed adapter, deterministic policy and
   evaluation harness from the typed contract. Route independently. Only run
   in parallel with 1 if file ownership, inputs and contracts are independent;
   otherwise order them. Keep permission/setup work explicit.
3. Deterministic execution of exact checks after 1; retain implementation review
   required by its returned model-router route.
4. Typed evaluation/threshold-resolution checkpoint after 2. Describe the
   labeled evidence and evaluation required by the contract; if it is unavailable,
   keep this checkpoint blocked. Do not generate labels or thresholds to unblock it.

Deferred work retains C1/C2/C3: runtime reconciliation, typed decisions/fallbacks,
explanation, result checks and assembly. Runtime depends on validated artifacts
from this stage, not merely on implementation finishing. Existing fallback-only
policy may be used only if the supplied contract defines it and its destination
is available. Do not recursively typify or reset the composition budget.

## Case C: raw discovery is not a cheap typed decision

Request: "Find why production sometimes charges twice and fix it." Relevant
state and cause are unknown, and no bounded classification contract is supplied.
Return a self-contained generative investigation handoff, preserving exact
invariants as acceptance criteria. Do not first trace production behavior to
decide whether Jev could diagnose it. If later artifacts establish a useful
exact or typed portion, that is new evidence for an explicit subsequent decision,
not an optimizer loop hidden inside the planner.

## Daily Claude Code trial

Use the installed plugin's namespaced commands; these are separate alternatives
or caller-invoked checkpoints, not commands the planner runs itself:

```text
/execution-router:compose-execution <task, evidence, acceptance criteria and payoff basis>
/execution-router:plan-execution <the resulting record, full contracts and remaining work>
```

For an already explicit mixed workflow, start directly with plan-execution.
For a wholly generative workflow, keep `/model-router:plan-execution` instead.
Follow the generated per-part model-router handoffs, then return their outputs
with the same part IDs and plan to execution-router:plan-execution. Missing
model-router leaves those routes pending but does not erase the mixed plan.
Planning never runs the resulting implementation, tools or review passes.

Observe whether supplied criteria survive every handoff; whether exact/typed
work was actually ready; whether conditional joins and reviews were respected;
and whether time saved exceeds planning, routing, relay and fallback cost. Record
failures as well as successes. An experiment is useful even if the simpler
single-session workflow wins. No new calibration schema or logger is required.
