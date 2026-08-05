# OpenAI provider policy

Last reviewed: 2026-08-05

This file is the **routing data for the OpenAI provider**. `SKILL.md` owns the
rubric, the tier layer, and the procedure; this file maps OpenAI models onto
the tiers and carries everything model-specific. When OpenAI routing changes,
change it here only.

Treat this as policy, not as a claim about model capability. Update it when
your own logged evidence contradicts it — see `../calibration.md`.

Sources for this revision: the GPT-5.6 launch announcement
(openai.com/index/gpt-5-6, 2026-07-09) and the 2026-07-30 price-cut coverage
(cnbc.com, axios.com). Items marked *(reported — verify)* came from secondary
sources only and should be confirmed against platform.openai.com before being
relied on for cost math.

## Tier mapping

| Tier | Model | Notes |
| --- | --- | --- |
| mechanical | `gpt-5.6-luna` | Fast/affordable tier; 80% price cut on 2026-07-30 |
| workhorse | `gpt-5.6-terra` | Balanced tier for everyday work |
| frontier | `gpt-5.6-sol` | Flagship |
| exceptional | `gpt-5.6-sol` at `reasoning_effort: max` | No separate top model — the exceptional path is Sol at `max`, optionally with Pro/ultra mode or multi-agent orchestration (beta) *(reported — verify)* |

Legacy rows (`gpt-5.5` at $5/$30, `gpt-5.4` at $2.50/$15, o-series) exist for
regression comparison only — do not route new work there.

## Baseline

| Model | Role | Default `reasoning_effort` | Context | $/MTok in-out |
| --- | --- | --- | --- | --- |
| `gpt-5.6-luna` | Bounded, mechanical, high-volume work | `none`/`low` | ~1M *(reported — verify)* | $0.20 / $1.20 |
| `gpt-5.6-terra` | Default for daily implementation | `medium` | ~1M *(reported — verify)* | $2 / $12 |
| `gpt-5.6-sol` | Reasoning, architecture, investigation, high-risk work | `high` | ~1M *(reported — verify)* | $5 / $30 |

Prices as of 2026-07-30 (post price cut; Sol kept its launch rate). Max output
128K *(reported — verify)*.

> *(reported — verify)* Long-context pricing: above roughly 270K input tokens
> the session reportedly bills 2× on input and 1.5× on output. If confirmed,
> large-context tasks flip the price comparison against Anthropic's flat 1M
> pricing — check before routing context-heavy work here on cost grounds.

> *(reported — verify)* Batch and Flex processing reportedly cut rates by 50%
> for latency-insensitive work.

## Effort ladder (`reasoning_effort`)

Levels on the GPT-5.6 family: `none`, `low`, `medium`, `high`, `xhigh`, `max`.
**These names look like Anthropic's but the semantics are not equivalent — never
carry a level across providers.** `none` disables deliberate reasoning entirely
(no Anthropic analogue); `max` was introduced with GPT-5.6 for Sol's deepest
reasoning.

### Horizon → effort mapping

Applied to the level the rubric's dimension 2 produces:

| Horizon | Terra | Sol |
| --- | --- | --- |
| 0–1 | `medium` | `high` |
| 2 | `high` | `xhigh` |
| 3 | `high` | `xhigh`, or `max` when correctness dominates cost |

Luna runs `none` or `low`; if a Luna task seems to need more, it is not a
mechanical-tier task — re-score it.

This mapping is a starting prior copied from the Anthropic ladder's shape, not
measured behavior. Retune it from calibration entries as they accumulate.

## Routing by task category

**No per-category routing yet.** This provider was added without local
evidence; route on the score and the tier mapping above, and let categories
earn their way in through the calibration log (three entries pointing the same
way, per `../calibration.md`). Do not copy the Anthropic category lists here —
they encode observed behavior of Anthropic models, not of these.

## Effort vs. model

Same principle as the Anthropic policy: raise `reasoning_effort` first when the
model is intellectually adequate and the limit is persistence or exploration;
raise the tier when judgment, abstraction, or hypothesis quality is the
bottleneck. Exhaust the ladder within a tier before moving up.

## Execution-shape notes

**OpenAI models do not run inside Claude Code.** Recommending one always
implies a harness switch — Codex CLI, a Responses API script, or another agent
— which means a cold prompt cache, a different tool-calling dialect, and none
of the current session's context. Per `SKILL.md` step 5.3, that switch must buy
something concrete; the output's execution shape must name the harness.

Suggested command shapes:

- Codex CLI: `codex --model gpt-5.6-<sol|terra|luna>` (set reasoning effort in
  the CLI/config per its current syntax — verify against Codex docs at use
  time).
- API: Responses API call with `model` and `reasoning_effort` set.

Multi-agent orchestration on the Responses API is in beta *(reported —
verify)*; treat agent-team shapes on this provider as experimental and
recommend a cap on fan-out, as with any orchestrated shape.

## Refusal and policy notes

No provider-specific refusal routing is documented here yet. If security- or
bio-adjacent work starts tripping OpenAI safety systems in practice, record it
via calibration notes and add the observed behavior to this section.
