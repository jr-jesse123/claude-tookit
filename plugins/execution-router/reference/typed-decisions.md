# Canonical guidance and execution mapping

Read on typify's eligible design branch. The application-level contract owns
state meaning, question semantics and policy. These pointers keep vendor facts
in their upstream homes instead of creating a fork of either plugin.

## Design knowledge: official TypeSafe skill

Read the installed `/typesafe:typesafe-ai` skill through the host's discovered
skill location. If unavailable locally, read the marketplace-pinned
[official SKILL.md](https://github.com/typesafe-ai/skills/blob/65a39f393687675ce170e6094757de20370365b9/skills/typesafe-ai/SKILL.md).
Do not guess plugin cache paths or install an integration to obtain guidance.
Follow its live-documentation procedure: start from the
[index](https://docs.typesafe.ai/llms.txt), then read the selected primitive,
state/uncertainty guidance and nearest relevant cookbook. Read API/SDK docs
only if the deliverable includes that integration detail. If live docs fail,
use verified local or pinned guidance, state the limitation, and avoid claims
about unverified current behavior. If all official guidance is unavailable,
typify returns no extraction with the missing prerequisite.

Useful decision distinctions (follow the corresponding source when relevant):

| Contract need | Design pointer | Distinction to preserve |
| --- | --- | --- |
| Yes/no or several simultaneous labels | [Noul](https://docs.typesafe.ai/primitives/noul) | Probability of yes; no separate confidence. Near 0.5 is uncertainty, not intensity |
| Exactly one option | [Choice](https://docs.typesafe.ai/primitives/choice) | Define alternatives and no-match handling; multiple valid labels may need separate questions |
| Graded dimension | [Score](https://docs.typesafe.ai/primitives/score) | Concrete independent level descriptions; keep distribution/confidence, not just the mean |
| Candidate ranking | [Reranking cookbook](https://docs.typesafe.ai/cookbooks/rerank_typesafe) | Candidate coverage, relevance and deterministic ordering; the first result need not be suitable |
| Evidence sufficiency | [State](https://docs.typesafe.ai/concepts/state) | Named source fields and current relevant facts; do not substitute the desired answer |
| Uncertainty policy | [Confidence](https://docs.typesafe.ai/confidence) | Distribution concentration differs from correctness; thresholds need domain evaluation |
| Bounded verification | [Citation checks](https://docs.typesafe.ai/cookbooks/citation_check) | Exact evidence preparation and semantic verification can have separate contracts |

Ranking is a contract over candidates, not a fourth System One primitive.
Choose probability-of-relevance Nouls or comparable Scores according to what
the ranking means; code sorts and applies tie/no-match policy.

## Execution capability: jev-code

Read the installed tool schema/reference before specifying a payload, or use
the marketplace-pinned
[jev-code tool contract](https://github.com/FrancoisChastel/jev-code/blob/cee3202c0321e30e6eb1ae968ece6a79d4181f57/skills/jev/references/tools.md).
This mapping was checked against v0.3.0. It is an adapter reference, not a
dependency on the upstream `/jev-code:jev` skill's design guidance.

| Application contract | Tool candidate | Adapter boundary |
| --- | --- | --- |
| Independent binary judgments over one state | `jev_check` | Map each check ID and probability; local policy owns acceptance |
| One class per item | `jev_classify` | Map class definitions and raw distribution; inspect threshold semantics |
| One described scale per item | `jev_score` | Preserve scale, distribution and confidence where required |
| Relevance ranking over supplied candidates | `jev_rank` | Check `any_relevant`, per-candidate relevance and coverage before using rank |
| Mixed types or a contract requiring raw answers | `jev_ask` | Map named state/questions and raw typed answers; compose locally |

Verify that the chosen adapter exposes every field the decision policy needs;
if a convenience tool omits one, consider the raw interface or report the gap.
Respect verified request limits and truncation flags. Losing necessary evidence,
unknown IDs, malformed values, missing answers or service errors activate the
contract's fallback; they never become successful negative judgments.

No tool's convenience `auto`, `yes`, or `relevant` label supersedes application
policy. Configure supported thresholds consistently, retain raw outputs and
validate their types/ranges before applying the contract. Runtime availability,
credentials and evaluation are separate from a design's adapter mapping.
Typify does not call MCP/CLI tools or test credentials. Generic `--providers=`
arguments apply only to later generative model-router handoffs, not Jev hosting.
