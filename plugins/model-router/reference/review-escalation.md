# Review escalation policy

Last reviewed: 2026-10-02

This file is shared by `choose-model` and `plan-execution`. It decides **how
much independent review a task warrants after normal routing**.

It does not change the five routing dimensions, provider tier mappings, or the
cross-provider tie-break in `routing-core.md`. Review is an execution-shape
decision: first decide whether another perspective is worth buying, then route
that review part normally.

## Principle

Independent review exists to add **new evidence**, not to repeat verification
that a strong oracle already provides.

The default remains:

> Use the cheapest verification shape that can expose a plausible failure the
> primary run and its oracle may miss.

A compiler, deterministic test, validator, or exact acceptance check can be more
valuable than another model. Do not add a reviewer merely because the task is
expensive or because a stronger model exists.

## Extra signal: hypothesis dependence

The routing core already provides oracle weakness and blast radius. Review adds
one binary signal:

**Hypothesis dependence = true** when the primary result materially depends on a
single interpretation, root-cause hypothesis, architectural judgment, or
assumption that the observable oracle does not independently prove.

Examples:
- an intermittent bug where one root cause became the favored explanation;
- an architecture decision whose trade-offs are mostly judgment;
- a concurrency fix where tests pass but do not prove the memory/ordering model;
- a migration plan whose safety depends on assumptions about production data.

Do not set it merely because reasoning occurred. A routine implementation with
deterministic tests is not hypothesis-dependent.

## Review escalation ladder

Choose the lowest level that clears the bar.

| Level | Shape | Use when |
| --- | --- | --- |
| **R0 — self verification** | Primary model + normal oracle | Strong oracle, low blast radius, no uncovered hard override, no hypothesis dependence |
| **R1 — fresh-context same-model review** | Separate invocation of the same model with fresh context | One moderate review signal exists, but model diversity is unlikely to justify its cost |
| **R2 — independent model peer** | Fresh-context reviewer on a different model; same provider is allowed | Multiple review signals or an uncovered hard-risk property make correlated model behavior worth reducing |
| **R3 — cross-provider peer** | Fresh-context reviewer from a different accepted provider | R2 applies and provider diversity is itself expected to add useful independent evidence |
| **R4 — review panel** | At most two independent reviewers plus adjudication | Exceptional weak-oracle/high-blast work, critical reviewer disagreement, or irreversible/high-consequence work where one peer is not enough |

### R0 — self verification

Use R0 when all are true:
- oracle weakness <= 1;
- blast radius <= 1;
- no hard override remains unproven by the oracle;
- hypothesis dependence is false.

A hard override does not automatically force external review if a deterministic
oracle directly proves the risky property. Example: a formally checked invariant
may make another same-perspective pass redundant.

### R1 — fresh-context same-model review

Consider R1 when exactly one moderate signal exists:
- oracle weakness = 2; or
- blast radius = 2; or
- hypothesis dependence = true; or
- the user explicitly requests a second look.

R1 is useful for de-anchoring from the working transcript without paying for a
different capability profile.

The reviewer must run in a fresh context. Do not pass the author's chain of
reasoning. Pass the contract described under **Reviewer input contract**.

### R2 — independent model peer

Use at least R2 when any of these holds:
- oracle weakness >= 2 **and** blast radius >= 2;
- a hard override fires and the available oracle does not directly prove the
  risky property;
- hypothesis dependence is true and either oracle weakness >= 2 or blast radius
  >= 2;
- the primary model already committed strongly to one hypothesis and tests only
  show consistency with it, not uniqueness.

R2 requires a different model from the author. It may stay within the same
provider when that is the cheapest useful source of model diversity.

Route the review as its own atomic task with `routing-core.md`. Do not require
the reviewer to be at least the author's tier mechanically; the **review task**
must clear its own capability floor. If the review itself inherits a hard
override (security, concurrency, transactions, distributed consistency, etc.),
that override naturally floors the reviewer at frontier.

### R3 — cross-provider peer

Escalate R2 to R3 when all are true:
- at least two providers are accepted;
- a candidate on another provider clears the review task's capability floor;
- the reason for review is materially about judgment, hypothesis lock-in,
  ambiguous semantics, or correlated blind spots rather than simple execution
  completeness;
- the context-transfer / harness-switch cost is reasonable relative to the
  expected value of a genuinely different model family.

R3 is **not** a new general cross-provider tie-break. It is a requirement of this
review shape: once R3 is selected, nominate reviewer candidates only from
accepted providers different from the primary author's provider, then apply the
normal routing core within that reduced candidate set.

This keeps provider diversity from contaminating ordinary task routing.

### R4 — review panel

Use R4 only when one of these holds:
- oracle weakness = 3 and blast radius >= 2;
- blast radius = 3 and oracle weakness >= 2;
- irreversible/production/data/security consequences combine with a weak oracle
  and the property cannot be deterministically proven;
- an R2/R3 reviewer reports a critical unresolved issue and author/reviewer
  evidence conflicts;
- the user explicitly requests adversarial multi-review for a consequential
  decision.

Default cap: **two reviewers plus one adjudication step**. More reviewers require
an explicit reason.

The adjudicator receives the artifact, requirements, evidence, and reviewer
findings. It should resolve disagreements, not redo the whole implementation.

## Reviewer input contract

For R1–R4, pass:
- original spec / acceptance criteria;
- relevant constraints and invariants;
- the final artifact, diff, design, or decision;
- observed tests, measurements, logs, or other evidence;
- known unresolved facts.

Do **not** pass the author's private reasoning or favored hypothesis on the first
review pass unless the reviewer specifically needs to audit that reasoning.
This reduces anchoring.

If the author's rationale itself is the artifact under review, separate the
first pass:
1. reviewer inspects requirements + artifact independently;
2. only then compare against the author's rationale.

## Reviewer output contract

The reviewer returns **findings**, not a silent rewrite.

Each material finding should name:
- severity / consequence;
- the concrete evidence;
- the requirement, invariant, or assumption involved;
- confidence / uncertainty;
- a recommended next check or correction when useful.

The primary model or the user adjudicates and applies changes unless the plan
explicitly creates a separate remediation part.

## Provider-specific independence notes

### Anthropic

Anthropic's Advisor Tool can pair Opus 5.5 with Fable 5.1 (and other compatible
peer/higher models). This makes Fable a valid **same-provider model-diversity**
option even though it is not a normal capability rung in the routing ladder.

Do not interpret this as "Fable is above Opus". In review/advisor use, the value
can be perspective diversity.

Advisor Tool receives the executor transcript, so it is appropriate for
**in-flight advice**, not for the fresh-context guarantee in R1–R4. For
adversarial review, use a separate fresh-context invocation.

Fable's price means it should not be the default reviewer when a cheaper model
clears the review bar.

Primary source:
https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool

### OpenAI

GPT-6.1 Sol is the normal OpenAI workhorse/frontier review candidate; Astra is
the premium candidate when the review task itself justifies exceptional
capability.

Codex exposes review-oriented workflows, including the review command for local
changes / branch comparisons. Prefer that surface when the review artifact is a
code diff and Codex is the chosen harness.

Primary sources:
https://developers.openai.com/api/docs/guides/latest-model
https://developers.openai.com/blog/mastering-codex-remote-for-engineering

## Calibration

Review effectiveness must be calibrated separately from authoring.

Use category slugs that preserve both the artifact category and review role, for
example:
- `concurrency-review`
- `architecture-review`
- `migration-review`
- `security-review`

This revision does **not** change the calibration schema. Log review runs through
the existing fields and put concise review-specific evidence in `note` when
useful (for example, "material finding survived adjudication"). Do not invent
new JSON fields here.

A follow-up calibration revision can formalize reviewer-specific outcomes such
as material findings, adjudication survival, and remediation impact once the
review shapes have real project data.

## Anti-patterns

Do not:
- automatically review every frontier task;
- equate a more expensive reviewer with more independence;
- send the author's full reasoning transcript to an "independent" reviewer;
- use cross-provider review when a strong deterministic oracle already closes
  the important risk;
- let the reviewer silently rewrite the work before findings are adjudicated;
- create three or more reviewers without an explicit R4 reason;
- use public cross-provider benchmark rankings as the reason for choosing the
  reviewer.
