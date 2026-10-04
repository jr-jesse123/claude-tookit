# Worked typed contracts

Hypothetical inputs and proposed policies, not recorded model outputs. Numeric
thresholds below are illustrative evaluation candidates, not shared defaults.
Consult [canonical guidance](../../reference/typed-decisions.md) for the selected
primitive and actual adapter contract before creating payloads.

## Independent labels with a generative response residual

**Input.** A recurring support queue asks for suggested labels and a tailored
reply. C1: label billing questions and cancellation requests independently;
both may apply. C2: write a reply preserving the ticket's facts. K1: only suggest
labels/replies, never change the account. Supplied definitions cover billing
questions about charges/invoices and explicit requests to cancel a subscription.
The existing human triage queue is available for exceptions. Repeated use makes
a bounded labeling contract worth evaluating; no claim of guaranteed accuracy.

**Status:** `proposed-contract`. **State:** ticket ID, original message, supplied
label definitions/version and message revision, copied mechanically from the
queue. Missing definitions, missing text or a changed revision causes fallback.
Keep the original message for the reply; labels are not a replacement for it.

| ID | Type | Full question and definitions |
| --- | --- | --- |
| billing | Noul | Does `ticket.message` ask about a charge or invoice under `definitions.billing`? Yes: such a question is present. No: no such question is present |
| cancellation | Noul | Does `ticket.message` explicitly request ending a subscription under `definitions.cancellation`? Yes: an explicit request is present. No: none is present; merely mentioning cancellation is insufficient |

**Policy proposal.** Batch both questions in one `jev_check` request; preserve
raw probabilities. After local state/response validation, each probability
at least 0.90 proposes its label; at most 0.10 proposes absence; values between
them go to the existing human triage queue with the message and both signals.
If either answer is invalid or uncertain, mark the entire label set pending
human triage rather than presenting a partial set as complete. False positives
misdirect the queue, motivating a broad initial abstention band. There is no
separate Noul confidence. Both labels may be proposed simultaneously.

**Evaluation/readiness.** Until representative labeled evaluation supports these
thresholds and the owner's original accuracy requirements, use fallback-only
operation: every label set goes to human triage. The proposed thresholds do not
activate unattended acceptance. One inference request per ticket, zero application
retries; account separately for the configured transport's bounded retries and
latency. Service errors also go to human triage; no account action is authorized.

Cases include billing-only, cancellation-only, both, neither, negated cancellation,
ambiguous intent, missing definitions and unavailable service. Synthetic values
0.10/0.90 and immediately inside the band check policy boundaries, not Jev accuracy.

| Criterion/constraint | Typed/policy obligation | Residual obligation |
| --- | --- | --- |
| C1 | Independent label proposals with uncertainty handling | Conditional human judgment for rejected/uncertain cases; all cases until validated |
| C2 | Supply label evidence, never invent a reply | Generate a factual reply using the original message and resolved labels |
| K1 | Return suggestions only | Preserve no-account-changes rule during reply and assembly |

**Recomposition/work remaining.** Implement state/adapter/policy, evaluate the
contract, obtain resolved labels, generate the reply and present both suggestions.
Keep human fallback and generative reply work explicit. No live call or labeling
has occurred during design. Typify does not route a model for the reply.

## Candidate ranking without forcing a winner

**Input.** Repeatedly suggest up to three relevant approved help articles for a
question; a human writes the final answer. C1: suggestions must come from the
supplied approved catalog. C2: abstain when the catalog has no useful answer.
The bounded catalog and full article text are mechanically supplied.

**Status:** `proposed-contract`. State holds the question, catalog version and
unique article IDs/text. Exact membership checks enforce C1 before and after
inference. A relevance-ranking contract maps to `jev_rank`: probability of
relevance per article plus evidence that any candidate is relevant. Code orders
eligible results by relevance, then stable ID for ties, taking at most three.
Rank is not confidence, and the first candidate is not automatically acceptable.

**Policy/evaluation.** Proposed evaluation thresholds: `any_relevant >= 0.90`
and candidate relevance `>= 0.85`. Require both, otherwise return no suggestion
and pass the question/catalog to the existing human workflow. Empty catalogs
skip inference; duplicate IDs, stale catalog versions, truncated necessary text,
missing results or errors fall back. An omitted useful article cannot be selected;
check candidate coverage before inference. Keep fallback-only operation until
domain evaluation establishes these thresholds. Cap at one request and zero
application retries, with transport retries separately accounted for.

Evaluate a single clear match, multiple useful matches, equal scores, all
irrelevant articles, useful content absent from the catalog, and invalid/service
responses. Validate membership deterministically; assess semantic relevance on
labeled question/article cases. C1 belongs to exact membership policy, C2 to
relevance/abstention policy with conditional human residual. Writing the answer
always remains residual. Implementation, evaluation and execution remain pending.

## No extraction when acquiring evidence already makes the decision

**Input.** Determine the root cause of an intermittent outage from an unknown
subset of services, then write a repair plan. No relevant logs, causal hypotheses
or bounded candidate set is supplied.

**Status:** `no-extraction`. Creating a Choice list such as network/database/code
would conceal the needed investigation. Finding a sufficient state already costs
the semantic discovery. Residual is the entire root-cause and repair task,
unchanged. No repository search, invented candidates, or Jev request is justified
just to make this judgment look bounded. Return a generative handoff with the
missing evidence; do not select its model.

## No extraction when typed output would weaken the acceptance bar

**Input.** Prove that a proposed change preserves all specified arithmetic results
for every permitted input, with no probabilistic error allowed. A yes/no model
answer is proposed as the proof.

**Status:** `no-extraction`. A well-typed answer and a high probability cannot
satisfy the proof criterion. Preserve the full verification task and exact
guarantee as residual. Deterministic/formal verification may be appropriate;
designing it is a separate step, not an automatic typify-to-determinize loop.
