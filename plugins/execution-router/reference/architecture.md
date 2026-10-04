# Execution routing: architecture and staged delivery

Status: grounding and scanning shipped in #41, exact extraction design in #42.
This increment adds the independently invocable, read-only `typify` design skill.
Residual orchestration, cross-paradigm planning, and assurance refactoring below
remain future work, not current behavior.

## Responsibilities

| Module | Question it owns | Interface to adjacent work |
| --- | --- | --- |
| `execution-router` | What form of computation should solve this task or portion? | A computation recommendation, supporting evidence, and an explicit residual |
| `model-router` | Given generative execution, what is the cheapest reliable provider/model/effort/execution/review shape? | Generative routing and planning, prompt adaptation, calibration |
| Upstream `jev-code` | How can an agent execute Jev typed judgments? | MCP/CLI tools; remains a separately installed upstream |
| Upstream `typesafe` | How should System One judgments and workflows be designed? | Canonical `/typesafe:typesafe-ai` knowledge skill; remains separate |

Dependency direction is **execution-router -> model-router**, never the reverse.
Direct `/model-router:choose-model` remains correct for obviously generative
work. Obviously deterministic work may need neither router. Execution routing
earns its cost primarily on large, repetitive, mixed, or paradigm-ambiguous work.
Missing optional integrations produce a self-contained advisory handoff.

The least expressive adequate executor is preferred: exact computation, then
bounded typed judgment, then open-ended generation. This is a semantic and
economic preference, not a mandatory conversion sequence or a quality ranking.
Every extraction must preserve acceptance criteria and expose remaining work.

## Cheap entry, not speculative discovery

The entry skill uses a fixed mechanical-tier model (`haiku`, no unsupported
effort field) for its bounded common case: inspect supplied state or copy named
evidence, then follow policy. Hard cases exit to generative routing instead of
making the scanner host perform architectural reasoning. This is a design-time
choice using the toolkit's cheapest-that-clears-the-bar principle; it does not
import model-router policies at runtime. Model identity alone does not make the
gate cheap: the collection and inference budgets are part of its interface.

Grounding states are self-contained, cheaply-groundable, and discovery-dependent.
Decision separability is the stopping rule: when acquiring context would already
perform the semantic judgment, a preliminary typed decision buys nothing. Even
available evidence may be too expensive to package within the entry budget.
Do not spend an expensive generative pass discovering whether a cheap executor
might have worked.

An eligible scan asks independent opportunity, generative-necessity, payoff, and
evidence-sufficiency questions. Jev supplies typed judgments; local deterministic
policy consumes them. Jev never chooses models or discovers transformations.
The fixed scan is itself a bounded typed decision, separate from general
`typify` design. Probabilities remain inspectable and uncertainty has a fallback.

## Intended residual pipeline

```text
raw task -> grounding gate -> eligible cheap shape scan
         -> determinize, if worthwhile -> scan the actual residual
         -> typify, if worthwhile -> remaining generative work -> model-router
```

Each stage may be skipped. Discovery-dependent work goes directly to generative
routing. Defaults: at most one determinize attempt and one typify attempt per
original task; at most the initial scan plus one scan per changed residual.
An attempt that extracts nothing or changes no residual advances or stops; it
does not retry with cosmetic rewording. An exception needs a concrete new fact
or measured payoff and an explicit budget before another attempt. These are
future orchestration rules; the shipped entry skill permits one scan only.

`determinize` uses generative reasoning to discover **how** an exact portion
can be extracted. Its contract names the portion, deterministic mechanism,
oracle, preserved semantics, preconditions, criterion coverage, and semantic
residual. It returns a proposal, no extraction, or an already-exact fast exit.
A regex that drops meaning is not a successful transformation. Designing the
contract never counts as implementing, executing or validating it: even an
empty semantic residual carries explicit remaining execution obligations.

The design skill uses `opus` / `high` for its common hard case: finding a useful
exact contract without losing meaning when the oracle is incomplete. This is
a design-time judgment consistent with the existing generative planner; it
does not import or change model-router policy at runtime. The cheap Haiku gate
never auto-invokes this more expensive step. `determinize` checks candidate-specific
payoff before a bounded design pass and rejects unsupported or uneconomic
extractions. A supplied exact mechanism can exit without new modeling.

See the [skill contract](../skills/determinize/SKILL.md) and
[worked examples](../skills/determinize/examples.md) when using or reviewing that
design step. It works without a scan or either upstream integration, and neither
recurses on its residual nor invokes model-router automatically.

`typify` uses generative reasoning to model state, independent questions,
Noul/Choice/Score/candidate-ranking outputs, and uncertainty/threshold/fallback
policy. It uses the official TypeSafe skill for design and jev-code for
execution capability, while keeping the contract independent of adapter details.
It produces a proposed contract or no extraction; it never calls Jev. Read the
[skill](../skills/typify/SKILL.md) for its contract and
[canonical guidance/mapping](typed-decisions.md) only on that design branch.
The Opus/high design-time default addresses the common hard case of preserving
meaning while defining sufficient state and an adequate fallback; no runtime
model-router dependency or policy change is introduced.

Its output covers every original criterion, evaluation cases and residual work,
including conditional human/generative fallbacks and exact work left outside
the contract. Ranking is a candidate contract implemented with judgments and
deterministic ordering, not a fourth System One primitive. Confidence never
replaces an exact guarantee. Unvalidated thresholds are identified, and unresolved
thresholds cannot enable automatic acceptance. Missing tools leave execution
pending; missing official guidance is reported rather than silently invented.

Economic justification includes expected reuse/scale, execution savings, or a
required reliability/guarantee gain that materially exceeds modeling,
grounding, evaluation and coordination cost. Exact guarantees can justify a
one-off transformation; mere technical possibility cannot. Unknown economics
does not become an invented ROI. Measure total workflow cost, not only Jev time.

## Increment boundaries and evidence gates

Numbers below are roadmap labels from the design discussion, not promises of
GitHub-assigned PR numbers. Each increment must be reviewable on its own.

| Increment | Deliverable | Acceptance boundary |
| --- | --- | --- |
| 41: entry (shipped) | Plugin, grounding gate, fixed Jev shape scan, local policy, advisory handoff | No transformation or model-router changes; failure and mixed-signal cases covered |
| 42: determinize (shipped) | Exact extraction design skill and worked examples | Preserves meaning, names mechanism/oracle, returns residual or no extraction; no task execution |
| 43: typify (this increment) | Typed-contract design skill and worked examples | Official TypeSafe guidance, Jev adapter separation, explicit uncertainty/fallback; no live decision execution |
| 44: composition | Bounded residual pipeline | Separability and economics at each relevant gate; changed-state rescans only; termination examples |
| 45: planner, evidence-gated | Cross-paradigm execution planning | Real mixed workflows demonstrate that moving/generalizing plan-execution is worth it |
| 46: assurance, evidence-gated | Assurance requirement separate from executor family | Real review contracts justify a change beyond today's R0-R4 ladder |

Before composition, collect examples where extraction succeeds, fails, or is
uneconomic, recording original acceptance criteria and the actual residual.
Before a planner move, demonstrate interfaces such as deterministic parser ->
Jev classification -> generative implementation -> deterministic tests ->
independent review. Preserve model-router:plan-execution's current multi-model
generative behavior until that evidence exists.

Assurance is eventually a requirement on evidence, not a synonym for another
LLM: deterministic checks can prove exact invariants; Jev can judge a closed
rubric at runtime; a generative reviewer can discover open-ended defects;
high assurance may combine independent evidence sources. Jev is a legitimate
bounded executor/reviewer, not only preflight. Preserve current R0-R4 behavior,
provider policies, routing core, and calibration until a separately scoped
change is supported by usage.
