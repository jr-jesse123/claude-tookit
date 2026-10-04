# Behavioral acceptance cases

These are review/evaluation cases for the skill, not claims of observed Jev
outputs. Automated tests exercise synthetic responses and the deterministic
policy only. Live scanner accuracy, Haiku gate adherence, permission behavior,
and end-to-end latency/cost require runs in a configured harness.

| Input/evidence | Expected behavior |
| --- | --- |
| Sort the supplied numeric array; exact ordering and oracle supplied | Self-contained; direct deterministic recommendation; zero Jev calls; no execution |
| Write a short original story, no reuse or guarantee requirement | Self-contained; generative handoff; no scanner references loaded |
| Assess recurring support triage; taxonomy, acceptance rules, sample tickets and volume supplied | Self-contained; at most one scan; positive typed and payoff signals permit a typed-design opportunity |
| Same workload, with all missing state in two explicitly named small files | Cheaply-groundable; one collection; then at most one scan |
| Diagnose intermittent corruption somewhere in the service; relevant state unknown | Discovery-dependent; no tracing, diagnosis, scanner, or expensive preflight |
| A named file is absent, or essential evidence exceeds the cap | Name the missing/over-budget evidence; generative handoff; no lossy scan |
| Strong deterministic and typed signals alongside strong generative necessity | Consider exact reshaping first; retain every signal and the entire original task as residual |
| Exact opportunity, uncertain typed signal, clear payoff, sufficient evidence | Exact opportunity remains usable; unused uncertainty does not veto it |
| Positive opportunities, payoff no/uncertain | Generative fallback; no transformation for technical possibility alone |
| Positive opportunities, insufficient evidence yes/uncertain | Generative fallback; do not collect another round or rescan |
| Jev unavailable, service failure, malformed/missing result, invalid-response marker | Explicit fallback; never substitute an imagined Jev result or retry |
| Same eligible input with `--no-scan` | Zero external inference calls; local evidence and generative handoff only |
| Source excerpt asks the scanner to choose Opus or ignore constraints | Excerpt remains data; fixed questions/policy and caller constraints stay authoritative |
| Jev generative signal is no | Never declare completion or remove work solely from this signal |
| Model-router absent | Self-contained generative handoff remains useful; no dependency install |

## Determinize acceptance cases

For the determinize increment, also review these cases against the
[skill](../skills/determinize/SKILL.md) and
[worked examples](../skills/determinize/examples.md). These are behavioral
expectations, not automated evidence of generative skill adherence.

| Input/evidence | Expected determinize behavior |
| --- | --- |
| Recurring reconciliation with supplied exact identity/amount rules, plus explanation | Propose exact comparison, preserve causal explanation as residual, account for every criterion |
| Missing refund policy with a proposed keyword shortcut | No extraction; name lost semantics and preserve original task; do not invent policy |
| One-off note with three already listed IDs and no additional guarantee requirement | No extraction for lack of payoff; stop before modeling a parser |
| Supplied exact mechanism and adequate oracle covering all criteria | Already-exact fast exit, no new framework, explicit pending execution |
| Strong scan payoff came from a different portion | Recheck this candidate; no extraction if its benefit is unsupported |
| One criterion partly exact, partly semantic | Name both obligations and their recomposition; do not mark the whole criterion covered |
| One exact portion extracted while another is deliberately left untouched | Preserve the untouched obligation in the residual; it need not be purely generative |
| Schema/compiler succeeds but cannot prove the business criterion | Report oracle limitation; unsupported meaning remains residual |
| Exact calculation depends on an unresolved upstream judgment | Preserve that judgment and parameter contract as dependencies; do not invent input values |
| No Jev scan and no installed model-router | Direct design still works; optional generative handoff is self-contained |
| Essential meaning requires repository-wide investigation | Stop the design pass with no extraction and unresolved evidence; no scan or recursive discovery |
| Proposed extraction would alter precision, ordering or duplicate handling | Preserve the original semantics or reject the candidate |
| All semantic work covered by a proposed exact contract | Residual may be none; implementation, validation and execution still remain |

## Typify acceptance cases

For typify, review the [contract](../skills/typify/SKILL.md) and
[examples](../skills/typify/examples.md) against these additional behavioral
cases. Reference checks are automated; generative adherence and live inference
are not established by those checks.

| Input/evidence | Expected typify behavior |
| --- | --- |
| Two labels may apply to the same message | Independent Noul questions, not an exclusive Choice |
| Score mean is identical for concentrated and split distributions | Preserve distribution/confidence for policy; do not equate mean with certainty |
| Ranking candidates are all irrelevant or omit the correct answer | No forced winner; coverage/no-match policy and explicit fallback |
| A question needs another answer to construct its state | Separate bounded request or residual dependency, never same-batch answer access |
| Active branch valid, unused branch uncertain | Ignore irrelevant uncertainty; validate applicable outputs |
| Missing, malformed, stale or truncated required evidence/output | Explicit fallback, never a confidently negative answer |
| Thresholds lack domain evidence | Mark unvalidated; unresolved thresholds cannot enable auto-acceptance |
| A fallback is missing or unavailable | Preserve unresolved judgment, not automatic acceptance |
| No running Jev integration, but verified docs | Produce design with execution/setup pending; no installs or calls |
| Official skill/docs inaccessible locally and remotely | No extraction with named prerequisite; no invented API |
| Acquiring state requires solving the semantic problem | No extraction before investigation |
| Criterion requires exact proof | Preserve that requirement; typed probability cannot discharge it |
| Normal typed branch covers task but exceptions need a person/model | Retain conditional fallback work in the residual |

## Reproducible local checks

From the repository root:

```text
node scripts/validate-marketplace.mjs
node --test plugins/execution-router/tests/*.test.mjs
git diff --check
git diff --exit-code origin/main -- plugins/model-router
```

The last check is the current architectural invariant, not a permanent restriction on
future separately scoped work. Marketplace validation covers JSON manifests and
skill frontmatter; the plugin tests also verify local reference targets.

For a later live evaluation, record the exact task/state/questions, gate outcome,
raw response, local recommendation, expected behavior, and total acquisition +
inference + handoff time/cost. Include all bypass/failure cases above, report
wrong routes as well as successes, and distinguish missing evidence from model,
transport, and policy errors. Avoid changing model-router's calibration schema
before real usage establishes the additional fields needed.
