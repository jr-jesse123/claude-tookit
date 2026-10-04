# Resumable residual record

Read when using [compose-execution](../skills/compose-execution/SKILL.md).
This is a chat-carried accounting record, not a job queue, execution plan or
durable transaction log. The user invokes each recommended skill explicitly,
then returns its output here. There is no automatic dispatch or persistence.

## Record and pure helper

```json
{
  "version": 1,
  "original": {
    "text": "Reconcile the supplied recurring ledger and explain anomalies.",
    "criteria": {
      "C1": "Compare every supplied ID and amount exactly.",
      "C2": "Explain anomalies without inventing causes."
    },
    "constraints": ["Preserve decimal precision and duplicate semantics."]
  },
  "providers": "--providers=anthropic,openai",
  "noScan": false,
  "steps": []
}
```

`providers` is optional and opaque: copy the user's explicit argument unchanged.
`noScan` is required and applies across the entire composition. Original task,
criterion meanings, constraints and flags are immutable on resume. Evidence,
source/freshness notes and the complete upstream skill output may be retained
as additional fields; the helper does not interpret them as instructions.

Run `scripts/compose-residual.mjs` with one JSON record on stdin. The helper
returns the next `action`, its `reason`, revision, attempt and scan counts,
original task, constraints, residual, accepted contracts, work remaining and
`taskExecuted: false`. It never writes files, calls a model or invokes a skill.
Keep the input record alongside the output; the latter does not replace history.

Only four completed steps are possible: gate, determinize, gate, typify. Stages
may be skipped. A pending attempt occupies its eventual completed step rather
than adding another step. Replaying the same input is safe and deterministic;
it is not authorization to repeat any previously issued call.

## Grounding/scan checkpoint

For each `ground-and-scan`, request the existing choose-execution advisor's
output for the current revision. Keep that request as pending in chat; do not
invoke it twice while waiting. Append its result as one `kind: "gate"` step:

- `revision`: helper's current integer, initially 0.
- `evidence`: `self-contained`, `cheaply-groundable`, or `discovery-dependent`.
- `separable`: boolean, with `reason` describing actual evidence/collection and
  bypass. Unclear separability is false, not a reason for more investigation.
- Generative bypass: `bypass: "generative"`; omit `scan`. Covers no-scan, missing
  tools, permissions, unsupported payoff and all other entry-skill bypasses.
- Exact bypass: `bypass: "direct-deterministic"`, supplied `mechanism` and `oracle`
  covering the entire current residual; omit `scan`. Exact execution is pending.
- Eligible scan: omit `bypass`, include concrete current `payoff` basis and `scan`
  containing the complete raw `jev_check` JSON response, not just its recommendation.
  A failed call uses `scan: null`. There is no retry or synthetic live probability.

The helper imports the existing scanner policy for response validation and raw
probability thresholds. It additionally skips spent transformation stages.
Malformed/uncertain/insufficient scan results stop reshaping. Scans cannot erase
criteria or prove completion, even when generative necessity is negative.

After determinize changes the residual, use a fresh gate for that residual and
its remaining economics. Do not reuse the old payoff or probability vector.
When a rejected design reveals stale/missing evidence, stop rather than reusing
the old scan for typify. No rescanning an unchanged residual to get a better answer.

## Transformation checkpoint

Before suggesting a transformation, append:

```json
{"kind":"attempt","revision":0,"stage":"determinize","result":null}
```

This consumes the attempt and returns `await-result`. On return, replace only
that pending `result` with the matching skill output normalized below. A result
from another stage/revision is not interchangeable. If a record was lost, ask
for it instead of assuming zero attempts. No later step may follow a pending one.

Rejected, failed or explicitly cancelled attempt:

```json
{"status":"no-extraction","reason":"This candidate has no material payoff.","evidenceChanged":false}
```

`failed` is also supported. Residual remains byte-for-byte unchanged. Set
`evidenceChanged: true` when the design reveals stale/incomplete state; this
prevents reuse of the previous scan. If unsure, use true. Otherwise a rejected
determinize can advance to the same scan's independent typed opportunity.
Rejection of one candidate does not establish the other candidate's economics.

Accepted exact design for the example above:

```json
{
  "status": "proposed-extraction",
  "reason": "Repeated exact comparison has a supplied business rule and oracle.",
  "reviewed": true,
  "contract": "Full determinize output, including mechanism, oracle, preconditions, economics and coverage; keep the actual artifact here, not this placeholder.",
  "coverage": {"C1":"extracted","C2":"residual"},
  "residual": {"text":"Explain anomalies from the exact comparison without inventing causes.","criteria":["C2"]},
  "recomposition": "Feed comparison results to the explanation; preserve input IDs and precision.",
  "workRemaining": ["Implement and validate the comparison against its oracle.","Run comparison on the supplied data.","Assemble exact results and the explanation."]
}
```

This example illustrates normalization, not an accepted production contract.
Keep the full design, not merely its title or a path unavailable to the receiver.
`status` is `proposed-extraction` or `already-exact` for determinize, and
`proposed-contract` for typify. `reviewed: true` attests the coordinator's bounded
comparison of supplied artifacts; it is not evidence of execution or evaluation.
If that check would require deep reasoning, record no extraction instead.

`coverage` has exactly the current residual's criterion IDs; values are
`extracted`, `residual` or `both`. The new residual retains exactly the `residual`
and `both` IDs with self-contained obligations, dependencies and conditional
fallbacks. All original constraints remain global, even after their criteria
leave the residual. For no remaining semantic work use `text: ""`, `criteria: []`;
pending implementation/evaluation/execution/recomposition must still be nonempty.
Partial extraction can keep the same criterion ID via `both` but must change
the actual obligations. Cosmetic rewrites do not qualify for a new scan.

The helper checks structural accounting and ordering. It cannot prove that
the contract preserves meaning, that economics are real, that evidence stayed
fresh, or that a rewritten record accurately represents earlier invocations.
These remain explicit caller checks, not guarantees of this local JSON format.
An invalid record yields `repair-record` with the entire input retained, never
a silent restart. Preserve the original task if restoration is impossible.

## Termination examples

| Supplied workflow | Expected stop/continuation |
| --- | --- |
| Initial scan supports exact and typed; exact extraction succeeds | Retain exact contract/pending execution; one fresh residual gate; typed only if current evidence and payoff support it |
| Fresh residual scan still strongly supports exact and typed | Exact attempt is spent; choose typed from the independent signal, not another exact attempt |
| Exact candidate is uneconomic, state unchanged, original typed signal is strong | Keep entire input; advance to typify without another scan; typify rechecks its own payoff |
| Exact design reveals evidence was stale | Preserve input; stop reshaping; no reused scan or discovery pass |
| Exact proposal changes nothing | No contract accepted or rescan; consider unused typed opportunity or stop |
| Typify normal branch works but uncertainty requires human/generative judgment | Keep conditional fallback in residual; no scan after typify, no recursive design |
| Exact design covers every semantic criterion | `design-complete`, not task complete; keep mechanism implementation, oracle validation and execution pending |
| Interrupted design, absent response, or duplicate/out-of-order result | Wait for pending result or repair record; do not reset attempts |
| No payoff, discovery-dependent state, no-scan, or missing Jev | Zero scans; generative handoff preserving all original work |

At a generative handoff the residual may still contain exact work. List that
work separately rather than sending deterministic execution or human decisions
to model-router. Route only remaining generative implementation/design/judgment.
Do not turn this ledger into a scheduler or a new review hierarchy. The next
planner/assurance changes require observed mixed-workflow evidence first.
