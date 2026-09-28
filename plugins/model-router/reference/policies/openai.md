# OpenAI provider policy

Last reviewed: 2026-09-22

This file is the **routing data for the OpenAI provider**. The shared
`routing-core.md` owns the rubric and the tier layer, and the skills own their
procedures; this file maps OpenAI models onto the tiers and carries everything
model-specific. When OpenAI routing changes, change it here only.

Treat this as policy, not as a claim about model capability. Update it when
your own logged evidence contradicts it — see `../calibration.md`.

Primary sources for this revision:

- GPT-6 Sol and Luna launch: https://openai.com/index/introducing-gpt-6-sol-and-luna/
- GPT-6 Astra launch: https://openai.com/index/gpt-6-astra/
- Model docs: https://developers.openai.com/api/docs/models/gpt-6-sol,
  https://developers.openai.com/api/docs/models/gpt-6-luna,
  https://developers.openai.com/api/docs/models/gpt-6-astra
- Pricing: https://developers.openai.com/api/docs/pricing

## Tier mapping

| Tier | Model | Notes |
| --- | --- | --- |
| mechanical | `gpt-6-luna` | Focused/high-volume work; use the oracle, not the low sticker price, to decide whether it clears the bar |
| workhorse | `gpt-6-sol` | Default OpenAI model for substantial implementation and agentic coding |
| frontier | `gpt-6-sol` | Same model at higher effort; judgment/risk alone does not justify the 5× Astra price jump |
| exceptional | `gpt-6-astra` | Hardest end-to-end work where Sol fails, project calibration shows a material gap, or an Astra-specific capability is the bottleneck |

The duplicate Sol mapping is deliberate. GPT-6 Sol costs like a workhorse but
OpenAI positions it for complex coding and agentic workflows; effort is the
first escalation axis. Astra is a model escalation, not the automatic answer to
every frontier-tier task.

GPT-5.6 models remain useful for regression comparison and existing evaluated
workflows. Do not route new work to Terra merely to fill a naming gap between
Luna and Sol: GPT-6 Sol now costs $2/$10, the same input and lower output price
than Terra's former $2/$12 baseline, while being the newer family.

## Baseline

| Model | Role | Default `reasoning.effort` | Context | Standard $/MTok in / cached / write / out |
| --- | --- | --- | --- | --- |
| `gpt-6-luna` | Focused, high-volume, bounded work | `medium` | 1.05M | $0.10 / $0.01 / $0.125 / $0.50 |
| `gpt-6-sol` | Complex coding and agentic workflows | `medium` | 1.05M | $2 / $0.20 / $2.50 / $10 |
| `gpt-6-astra` | Hardest end-to-end reasoning, coding, computer use, research | `medium` policy default | 1.05M | $10 / $1 / $12.50 / $50 |

All three support 128K max output. Sol and Luna support `none`, `low`,
`medium`, `high`, `xhigh`, and `max`; both default to `medium`.
Astra supports `low` through `max` and does not support `none`.

> **Long-context surcharge is confirmed.** Above 272K input tokens, the whole
> request bills at 2× input/cache rates and 1.5× output. That is a material
> cross-provider cost cliff; include it in price tie-breaks.

> **Batch/Flex:** 50% of Standard. **Fast:** 2× Standard. Do not mix service-tier
> pricing with model-quality comparisons.

## Effort ladder (`reasoning.effort`)

| Level | Use for |
| --- | --- |
| `none` | Luna/Sol only: deterministic transforms or latency-sensitive work where deliberate reasoning has no value |
| `low` | Short, scoped work with a strong oracle |
| `medium` | Default for Luna/Sol and the normal starting point |
| `high` | More exploration/verification when the model remains intellectually adequate |
| `xhigh` | Demanding or long-running agentic work where extra iterations are worth the tokens |
| `max` | Correctness dominates cost and latency; use only when calibration or task shape justifies it |

### Horizon → effort mapping

| Horizon | Luna | Sol | Astra |
| --- | --- | --- | --- |
| 0–1 | `low` / `medium` | `medium` | `medium` |
| 2 | `high` only with strong oracle | `high` | `high` |
| 3 | do not default here | `xhigh`, or `max` when correctness dominates | `xhigh`, or `max` when correctness dominates |

Do not use effort to smuggle a model across a capability boundary. Luna at
`max` can be extremely cost-effective, but a weak oracle, hidden semantic
risk, or repeated shallow failures are reasons to move to Sol rather than keep
buying more Luna reasoning.

## Routing by task category

These rows are launch-evidence priors. They never outrank project calibration,
and public cross-provider benchmark scores never decide a provider tie.

### Luna

- Inventory, extraction, classification, summarization, schema conversion.
- High-volume repository scanning and operational triage.
- Bounded implementation when requirements are explicit and deterministic
  tests/compiler feedback provide a strong oracle.
- Parallel scouts whose outputs will be checked by a stronger model.

OpenAI reports Luna `max` at 66.6% on DeepSWE 1.1, comparable in that eval to
older frontier Claude models at medium effort, while costing dramatically less.
Use that as evidence that Luna deserves serious bounded work — **not** as a
reason to send weak-oracle architecture or high-risk changes to the mechanical
tier.

### Sol

- Daily implementation that spans layers/files but has good automated checks.
- Complex coding and agentic workflows.
- Debugging with multiple hypotheses but an observable oracle.
- Architecture/design where the problem is made from known engineering
  concepts and project calibration does not show a need for Astra.
- Long-running coding sessions where cost compounds heavily.

Within OpenAI's launch evals, Sol closes much of the gap to much more expensive
models on coding and professional workflows. That is why it occupies both the
workhorse and frontier tiers in this policy. It does **not** override the
cross-provider benchmark rule in `routing-core.md`.

### Astra

Astra is not "Sol but safer to recommend." Route here when at least one concrete
Astra-specific reason exists:

- A serious Sol `xhigh`/`max` attempt failed because judgment, abstraction,
  or hypothesis quality — not merely persistence — was the bottleneck.
- Project calibration or a task-specific eval shows a repeatable quality gap
  worth roughly 5× Sol's base token price.
- Computer use / browser work where visual judgment and reliable interaction
  are central and the task is consequential.
- Scientific/mathematical work where frontier reasoning is itself the product.
- Very long Codex work where Astra's experimental cross-context notes +
  searchable prior context materially reduce compaction loss.
- A high-value end-to-end deliverable where fewer iterations/rework are worth
  the premium.

OpenAI calls Astra its most capable model, but the same vendor tables show that
the advantage is not uniform across every coding benchmark. Treat its price as
buying **specific additional capability**, not prestige.

## Escalation ladder

1. Luna `low`/`medium` for focused mechanical work.
2. Luna `high` only for bounded work with a strong oracle where its economics
   justify more reasoning.
3. Sol `medium` for normal substantial implementation.
4. Sol `high` when more exploration/verification is needed.
5. Sol `xhigh`/`max` for demanding or long-horizon work when Sol remains the
   right model.
6. Astra `medium` when Sol's capability — not effort — is the bottleneck, or
   when an Astra-specific capability is required.
7. Astra `high`/`xhigh`/`max` only when the task's value and evidence
   justify the additional reasoning spend.

This makes Astra the exceptional tier, not a reflexive frontier default.

## Effort vs. model

**Raise effort first** when the model is finding the right hypotheses but needs
more search, tool persistence, verification, or iterations.

**Raise model first** when it repeatedly reaches plausible but shallow
conclusions, misses abstractions, misjudges ambiguous requirements, or when the
task depends on a capability documented as materially stronger on Astra.

A Sol failure caused by context/tool persistence is not automatically an Astra
signal; a Sol failure caused by judgment may be.

## Token economics

- **Measure model-specific tokens.** GPT and Claude tokenize differently; never
  reuse a count measured on another provider.
- **Cached input is 10% of fresh input** on GPT-6; cache writes are 1.25× fresh
  input. A warm cache can dominate long agent costs.
- **>272K is a hard economic cliff:** 2× input/cache and 1.5× output for the
  full request.
- **Effort/tool changes can preserve cache on GPT-6.** OpenAI documents changing
  reasoning effort and tool availability without breaking the reusable prompt
  prefix. Prefer that over starting a cold session when the harness supports it.
- When price decides a cross-provider tie, compare the expected workload shape
  (fresh input, cached input, output, service tier, and long-context surcharge)
  rather than sticker input alone.

## Execution-shape notes

OpenAI models do not run inside Claude Code. Recommending one from a Claude Code
session implies a harness switch — usually Codex CLI, ChatGPT Work, or a
Responses API/Agents API workflow — with provider/tooling/context costs. Per
`routing-core.md` tie-break rule 3, the switch must buy something concrete.

Suggested command shapes:

- Codex CLI: `codex --model gpt-6-luna`, `codex --model gpt-6-sol`, or
  `codex --model gpt-6-astra` (set effort using the current Codex config).
- API: Responses API with `model` and `reasoning.effort`.

For GPT-6, OpenAI documents cache-preserving changes to reasoning effort and
tool availability. Do not recommend a new session solely to change effort when
the active GPT-6 harness can preserve the prefix.

### Astra long-context memory in Codex

Astra can experimentally keep notes across context windows while older context
remains searchable, reducing information loss from repeated compaction. Treat
this as an **execution-shape advantage** for very long work, not as a reason to
route normal coding to Astra.

### Multi-agent work

OpenAI now exposes native multi-agent/Agents API capabilities, but model choice
still happens per atomic part. When the honest answer needs multiple models or
agents, hand off to `plan-execution`; do not let this policy invent a bundle
inside one tier decision.

## Refusal and policy notes

Astra has stronger cybersecurity safeguards. OpenAI says advanced cyber tasks
may be refused and legitimate defensive work can be slowed, paused, or stopped
by extra checks; in the API, a stopped task ends rather than silently completing
through a weaker model. Account for this in security-adjacent routing.

Sol and Luna also inherit GPT-6 alignment improvements. Record any repeated
provider-specific interruptions in calibration before turning them into a hard
routing rule.
