# OpenAI provider policy

Last reviewed: 2026-10-02

This file is the **routing data for the OpenAI provider**. The shared
`routing-core.md` owns the rubric and the tier layer, and the skills own their
procedures; this file maps OpenAI models onto the tiers and carries everything
model-specific. When OpenAI routing changes, change it here only.

Treat this as policy, not as a claim about model capability. Update it when
your own logged evidence contradicts it — see `../calibration.md`.

Primary sources for this revision:

- GPT-6.1 Sol launch: https://openai.com/index/introducing-gpt-6-1-sol/
- GPT-6.1 Sol model docs: https://developers.openai.com/api/docs/models/gpt-6.1-sol
- GPT-6 Sol and Luna launch: https://openai.com/index/introducing-gpt-6-sol-and-luna/
- GPT-6 Astra launch: https://openai.com/index/gpt-6-astra/
- Current model catalog: https://developers.openai.com/api/docs/models
- Pricing: https://developers.openai.com/api/docs/pricing
- Prompt caching / effort updates: https://developers.openai.com/api/docs/guides/prompt-caching
- Codex integration guidance: https://developers.openai.com/api/docs/guides/code-generation,
  https://developers.openai.com/api/docs/guides/agents-api/overview

## Tier mapping

| Tier | Model | Notes |
| --- | --- | --- |
| mechanical | `gpt-6-luna` | Focused/high-volume work; use the oracle, not the low sticker price, to decide whether it clears the bar |
| workhorse | `gpt-6.1-sol` | Default OpenAI model for substantial implementation, review, and agentic coding |
| frontier | `gpt-6.1-sol` | Same model at higher effort; near-Astra launch results make effort the first escalation axis |
| exceptional | `gpt-6-astra` | Hardest end-to-end work where Sol fails, project calibration shows a material gap, or an Astra-specific capability is the bottleneck |

The duplicate Sol mapping is deliberate. GPT-6.1 Sol keeps Sol's $2/$10 fresh
input/output price while moving materially closer to Astra on coding, computer
use, professional work, factuality, and scientific workflows. Effort is therefore
the first escalation axis. Astra is a capability escalation, not the automatic
answer to every frontier-tier task.

GPT-6 Sol is now a regression/compatibility target rather than an active routing
destination: the model page points to GPT-6.1 Sol as the newer Sol, at the same
$2/$10 fresh input/output price and half the cached-input price ($0.10 vs $0.20).
GPT-5.6 models likewise remain regression/existing-workflow only.

## Baseline

| Model | Role | Default `reasoning.effort` | Context | Standard $/MTok in / cached / write / out |
| --- | --- | --- | --- | --- |
| `gpt-6-luna` | Focused, high-volume, bounded work | `medium` | 1.05M | $0.10 / $0.01 / $0.125 / $0.50 |
| `gpt-6.1-sol` | Near-Astra complex coding, review, computer use, and professional work | `medium` | 1.05M | $2 / $0.10 / $2.50 / $10 |
| `gpt-6-astra` | Hardest end-to-end reasoning, coding, computer use, research | `medium` policy default | 1.05M | $10 / $1 / $12.50 / $50 |

All three support 128K max output. GPT-6.1 Sol supports `low`, `medium`, `high`,
`xhigh`, and `max` and defaults to `medium`; unlike GPT-6 Sol, it does **not**
support `none`. Luna supports `none` through `max` and defaults to `medium`.
Astra supports `low` through `max` and does not support `none`.

> **Long-context surcharge is confirmed.** Above 272K input tokens, the whole
> request bills at 2× input/cache rates and 1.5× output. That is a material
> cross-provider cost cliff; include it in price tie-breaks.

> **Batch/Flex:** 50% of Standard. **Fast:** 2× Standard. Do not mix service-tier
> pricing with model-quality comparisons.

## Effort ladder (`reasoning.effort`)

| Level | Use for |
| --- | --- |
| `none` | Luna only among active routes: deterministic transforms or latency-sensitive work where deliberate reasoning has no value |
| `low` | Short, scoped work with a strong oracle |
| `medium` | Default for Luna and GPT-6.1 Sol; normal starting point |
| `high` | More exploration/verification when the model remains intellectually adequate |
| `xhigh` | Demanding or long-running agentic work where extra iterations are worth the tokens |
| `max` | Correctness dominates cost and latency; use only when calibration or task shape justifies it |

### Horizon → effort mapping

| Horizon | Luna | GPT-6.1 Sol | Astra |
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

### GPT-6.1 Sol

- Daily implementation that spans layers/files but has good automated checks.
- Complex coding, debugging, code review, and agentic workflows.
- Debugging with multiple hypotheses but an observable oracle.
- Architecture/design made from known engineering concepts when project
  calibration does not show a need for Astra.
- Long-running coding sessions where cost compounds heavily.
- Computer-use and professional-document work that does not need Astra's final
  increment of capability.

OpenAI's launch evidence materially strengthens Sol's workhorse/frontier role:
- on DeepSWE 1.1, GPT-6.1 Sol matches Astra at roughly one-fifth the cost and
  exceeds GPT-6 Sol's best score by 6.4 percentage points at lower effort/cost;
- on AutomationBench it scores 2.2 points above Opus 5.5 at medium effort at
  roughly one-third the cost;
- on OSWorld 2.0 at max effort it comes within 2.1 points of Astra at roughly
  one-seventh the cost per task;
- on Terminal-Bench Science, Astra still leads, showing that the remaining
  premium is real for the hardest scientific work.

These are within-provider routing priors plus vendor-reported cross-provider
context. Per `routing-core.md`, the cross-provider numbers never decide a tie;
project calibration does.

### Astra

Astra is not "Sol but safer to recommend." Route here when at least one concrete
Astra-specific reason exists:

- A serious GPT-6.1 Sol `xhigh`/`max` attempt failed because judgment,
  abstraction, or hypothesis quality — not merely persistence — was the bottleneck.
- Project calibration or a task-specific eval shows a repeatable quality gap
  worth roughly 5× GPT-6.1 Sol's fresh-token price.
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
3. GPT-6.1 Sol `medium` for normal substantial implementation and review.
4. GPT-6.1 Sol `high` when more exploration/verification is needed.
5. GPT-6.1 Sol `xhigh`/`max` for demanding or long-horizon work when Sol remains
   the right model.
6. Astra `medium` when GPT-6.1 Sol's capability — not effort — is the bottleneck, or
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

A GPT-6.1 Sol failure caused by context/tool persistence is not automatically
an Astra signal; a failure caused by judgment may be.

## Token economics

- **Measure model-specific tokens.** GPT and Claude tokenize differently; never
  reuse a count measured on another provider.
- **Cached input is model-specific.** GPT-6.1 Sol cache reads are 5% of fresh
  input ($0.10 vs $2), while Luna and Astra are 10%; cache writes are 1.25×
  fresh input. Warm repeated context therefore makes GPT-6.1 Sol even more
  attractive for long agent/review loops.
- **>272K is a hard economic cliff:** 2× input/cache and 1.5× output for the
  full request.
- **Effort changes can preserve cache on GPT-6.** In standard single-agent mode,
  append a `configuration_update` to change reasoning effort while leaving the
  request-level effort unchanged; this preserves the earlier reusable prefix.
  Tool definitions/order still affect cache identity, so prefer `allowed_tools`
  or append-only tool updates rather than rewriting the tool list.
- When price decides a cross-provider tie, compare the expected workload shape
  (fresh input, cached input, output, service tier, and long-context surcharge)
  rather than sticker input alone.

## Execution-shape notes

OpenAI models do not run inside Claude Code. Recommending one from a Claude Code
session implies a harness switch — usually Codex CLI, ChatGPT Work, or a
Responses API/Agents API workflow — with provider/tooling/context costs. Per
`routing-core.md` tie-break rule 3, the switch must buy something concrete.

Suggested execution shapes:

- Codex CLI: `codex --model gpt-6-luna`, `codex --model gpt-6.1-sol`, or
  `codex --model gpt-6-astra` (set effort using the current Codex config).
- Direct model call: Responses API with `model` and `reasoning.effort`.
- New automation/integration: prefer the Codex SDK, Codex app-server, or Agents
  API depending who should own the agent loop/state.
- Review-specific CLI work can use Codex's review surface (`codex review`) when
  the desired artifact is a code/diff review.

Do **not** recommend the old `codex mcp-server` path for new integrations. OpenAI
marks that Codex-as-MCP server integration deprecated/removed; MCP remains useful
for giving Codex/Agents access to external tools, not as the preferred way to
invoke Codex itself.

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

GPT-6.1 Sol now uses the same safeguards stack as Astra for the capability areas
called out in its system-card addendum. Record any repeated provider-specific
interruptions in calibration before turning them into a hard routing rule.
