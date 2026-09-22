# Anthropic provider policy

Last reviewed: 2026-09-22

This file is the **routing data for the Anthropic provider**. The shared
`routing-core.md` owns the rubric and the tier layer, and the skills own their
procedures; this file maps Anthropic models onto the tiers and carries
everything model-specific. When Anthropic routing changes, change it here only.

Treat this as policy, not as a claim about model capability. Update it when your
own logged evidence contradicts it — see `../calibration.md`.

## Tier mapping

| Tier | Model | Notes |
| --- | --- | --- |
| mechanical | `haiku` | 200K context — disqualified when input approaches it |
| workhorse | `sonnet` | |
| frontier | `opus` | Current alias target: Opus 5.5 |
| exceptional | `fable` | Current alias target: Fable 5.1. Keep as an evidence-driven exception; Opus 5.5 now matches Fable 5.1 on most work at materially lower cost |

`claude-opus-4-8` sits outside the ladder: regression comparison, compatibility
with an already-evaluated workflow, and the documented refusal fallback only.

## Baseline

| `--model` | Role | Default `--effort` | Context | $/MTok in-out |
| --- | --- | --- | --- | --- |
| `haiku` | Bounded, mechanical, high-volume work | **omit — see note** | 200K | $1 / $5 |
| `sonnet` | Default for daily implementation | `medium` (policy default; API/Claude Code default is `high`) | 1M | $2 / $10 |
| `opus` | Opus 5.5: reasoning, architecture, investigation, high-risk and long-horizon work | `medium` (vendor default; raise from evidence) | 1M | $4 / $20 |
| `fable` | Fable 5.1: demanding reasoning and exceptional long-horizon work | `high` | 1M | $10 / $50 |
| `claude-opus-4-8` | Regression and compatibility only | `high` | 1M | $5 / $25 |

Prices reviewed 2026-09-22. Sonnet 5 remains $2/$10. Opus 5.5 is $4/$20, with $0.20/MTok cache reads and $5/MTok cache writes. Fable 5.1 remains $10/$50 with $0.25/MTok cache reads. Anthropic reports Opus 5.5 costs about 40% less than Opus 5 on typical workloads at default settings.

> **Do not pass `--effort` with `haiku`.** Haiku 4.5 does not accept the effort
> parameter; the four other rows accept `low`, `medium`, `high`, `xhigh`, `max`.

> **Haiku's context is 200K, not 1M.** A task whose input alone approaches that
> ceiling is disqualified from Haiku regardless of how mechanical it is.

## Effort ladder

| Level | Use for |
| --- | --- |
| `low` | Short, scoped, latency-sensitive work with a strong oracle |
| `medium` | Normal implementation — the Sonnet default |
| `high` | Judgment is the bottleneck or project calibration shows material gains above Opus 5.5 `medium` |
| `xhigh` | Demanding or long-running coding/agentic work (roughly >30 minutes / million-token budgets), or other tasks whose evals show measurable headroom above `high` |
| `max` | Correctness matters more than cost, and the task is not latency-sensitive. Prone to overthinking on simple work — never a default |

### Horizon → effort mapping

Applied to the level the rubric's dimension 2 produces:

| Horizon | Sonnet | Opus |
| --- | --- | --- |
| 0–1 | `medium` | `medium` |
| 2 | `high` | `high` |
| 3 | `high` | `xhigh`, or `max` when correctness dominates cost |

Opus 5.5 defaults to `medium`. Treat that as the starting point even for substantial
coding: Anthropic reports 54.6% on FrontierCode v1.1 and 52.5% on CursorBench 4.0
at default `medium`, with the latter slightly above Fable 5.1 at `max`. Raise effort
when the task's horizon, risk, or project calibration demonstrates headroom; do not
inherit Opus 5's old `high` default mechanically.

Escalating effort is cheaper than escalating model. Exhaust the ladder within a
tier before moving up a tier, **except** when the bottleneck is judgment rather
than persistence (see [Effort vs. model](#effort-vs-model)).

At `xhigh` or `max`, allow a large output budget — these levels spend heavily on
thinking before answering, and a tight cap truncates mid-answer.

## Routing by task category

These reflect this repository owner's stack. Retune them from logged evidence,
not from intuition.

### Haiku

- Locate all implementations of an interface.
- Inventory projects and dependencies.
- Summarize logs.
- Produce a mechanical rename plan.
- Classify test failures.
- Draft a commit message from an existing diff.
- Independent repository-scanning subtasks running in parallel.

Do not choose Haiku because the requested *change* looks short. A one-line edit
with hidden dependents is not a Haiku task.

### Sonnet `medium`

- Implement a specified ASP.NET or F# endpoint.
- Add xUnit or Verify tests for known behavior.
- Modify an HTMX or React component following an existing pattern.
- Add a repository method with clear SQL requirements.
- Refactor a bounded component.
- Investigate a deterministic test failure.
- Write routine technical documentation.

### Sonnet `high`

- Debug a broader but familiar feature.
- Implement across several layers with strong tests.
- Understand brownfield code before making a bounded change.
- Review a medium-sized diff in detail.
- Work through a long but conceptually familiar test failure.

### Opus 5.5 `medium` / `high`

- Investigate Oracle isolation or concurrency behavior.
- Design transaction and idempotency semantics.
- Make an architectural decision involving coupling or availability.
- Review a change for subtle semantic or distributed-system defects.
- Design an IL instrumentation, compiler-service, analyzer, or LSP approach.
- Research undocumented or conflicting framework behavior.
- Diagnose an intermittent E2E failure with no clear oracle.
- Model a complex domain in F#, or compare F# and C# representations.

### Opus 5.5 `xhigh`

- Demanding coding or agentic work whose horizon or evals justify more than the
  `high` default — especially long-running sessions with repeated tool use.
- Large cross-project refactoring.
- Framework or persistence migration.
- Investigation of several competing root-cause hypotheses.
- Building a substantial developer tool.
- Autonomous work across code, tests, CI, infrastructure, and documentation.
- Long agent runs that must repeatedly validate and correct themselves.

### Fable 5.1

- Demanding reasoning where Opus 5.5 at higher effort still falls short on this
  project's calibration log or a task-specific evaluation.
- Multi-repository or exceptionally large migrations.
- Work whose human equivalent spans multiple days.
- Very long autonomous execution where context coherence is the main risk.
- High-value work where a small increase in success probability is worth the
  remaining cost premium.

Do not choose Fable for ordinary review, explanation, feature work, or merely
because a run is long/cache-heavy. Opus 5.5 cache reads are cheaper ($0.20 vs
$0.25/MTok), and Anthropic reports Opus 5.5 matching Fable 5.1 on most work.
Route to Fable when calibration or task-specific evidence demonstrates an
advantage, or after a serious Opus 5.5 attempt falls short.

### `claude-opus-4-8`

Only for: regression comparison, compatibility with an already-evaluated
workflow, or diagnosing behavior differences between Opus 4.8 and Opus 5. It is
also the documented fallback target when Opus 5 declines a request — see
[Refusals](#refusals-on-security-adjacent-work).

## Escalation ladder

Apply in order unless a hard override (see `routing-core.md` → Hard
overrides) fires.

1. Haiku for obviously mechanical work.
2. Sonnet `medium` for normal development.
3. Sonnet `high` when the problem is familiar but needs more persistence.
4. Opus 5.5 `medium` when reasoning or judgment is the bottleneck.
5. Opus 5.5 `high` when task risk/horizon or calibration shows useful headroom above `medium`.
6. Opus 5.5 `xhigh`/`max` only when demanding long-horizon work or measured gains justify the extra spend.
7. Fable 5.1 `high` after a serious Opus 5.5 shortfall or task-specific/calibration evidence that Fable is better.
8. Fable 5.1 `xhigh` only when that same evidence also justifies maximum long-horizon capability.

## Effort vs. model

**Raise effort first** when the current model is intellectually adequate and the
limitation is exploration, verification, or tool persistence — or when the task
turned out larger than expected but is still familiar.

**Raise model first** when judgment, abstraction, hypothesis quality, or
architectural understanding is the bottleneck; when the cheaper model reaches
plausible but shallow conclusions repeatedly; when the problem is substantially
novel; or when there is hidden semantic or operational risk.

## Context behavior

Seeded 2026-08-05; same provenance tags as the OpenAI policy (`[vendor]` =
Anthropic's claims/evals, `[reported]` = independent sources). Calibration
entries confirm or demote these like any prior.

- **Hard limits.** Haiku 200K (the disqualifier above); Sonnet, Opus, and
  Fable 1M — **at flat pricing, with no long-context surcharge** since
  Opus 4.7. `[vendor]` That is a structural advantage over OpenAI's reported
  >~270K surcharge (see `openai.md` → Baseline) when comparing prices on
  context-heavy work.
- **Effective vs. advertised.** Industry-wide long-context evals (NVIDIA
  RULER family) put most models' *effective* context at ~50–65% of nominal —
  a model advertising 200K typically turns unreliable around 130K.
  `[reported]` This is a cross-model prior, not a Claude-specific
  measurement. Practical rule: when dimension 5 scores 3 **and** the input
  alone fills more than about half the candidate's window, treat the
  candidate as one tier weaker than nominal unless log evidence says
  otherwise.
- **Frontier tier holds up at high fill.** Launch-era MRCR v2 (8 identical
  needles across 1M tokens, requiring sequential reasoning): ~76% for the
  Opus line, described by Anthropic as a qualitative shift in usable
  context `[vendor]`; independent commentary placed it among the only
  models viable on that eval. `[reported]` Prior: high-fill retrieval and
  cross-file consistency belong to Opus or above, not Sonnet.
- **Compaction is itself a degradation mode.** Server-side compaction (beta)
  summarizes earlier context, triggering by default around 150K tokens.
  `[vendor]` For tasks whose working set must stay *verbatim* — citation,
  auditing, cross-file consistency over a large diff — summarization loses
  exactly what the task needs: score dimension 5 up and prefer the frontier
  tier over relying on compaction.
- **Long-horizon routing changed with Opus 5.5.** Anthropic reports successful
  multi-repository runs lasting more than 18 hours and a C→Rust migration that
  finished in 9.5 hours versus 12 hours for Fable 5.1 at 51% lower cost. Treat
  long horizon alone as an Opus 5.5 signal, not an automatic Fable promotion;
  keep Fable evidence-driven.

## Token economics (input)

Output volume is steerable (effort, `max_tokens`, prompting) and is therefore
not legislated here — the calibration log measures it per category instead.
Input-side token density is not steerable; these notes exist so the price
tie-break (`routing-core.md` → tie-break rule 2) uses real counts:

- **Tokenizers differ within this provider.** Sonnet 5's tokenizer produces
  ~30% more tokens than Sonnet 4.6's for the same text; the Opus 4.7+/Fable
  tokenizer runs ~1×–1.35× vs pre-4.7 models. `[vendor]` A count measured on
  one model is invalid on another — re-measure, never scale by feel.
- **Measure, don't estimate.** `count_tokens` is model-specific and cheap.
  When price decides a cross-provider or cross-tier tie on an input-heavy
  task, run the actual input through each candidate's counter before
  comparing — one API call per candidate beats any multiplier.
- **Caching bends the effective input rate, but not uniformly.** Opus 5.5 cache
  reads cost $0.20/MTok; Fable 5.1 cache reads cost $0.25/MTok. The unusually
  cheap Fable cache multiplier no longer makes cache-heavy work a direct Fable
  signal because Opus 5.5 is cheaper in absolute cached-input cost. Compare the
  effective workload cost and let calibration decide any remaining capability
  premium. Ecosystem affinity still matters when a warm cache already exists.
- **No long-context surcharge** at 1M (see Context behavior) — the input rate
  is flat where OpenAI's is reportedly not.

## Refusals on security-adjacent work

Opus 5.5 and Fable 5.1 ship safety classifiers and can decline or transparently reroute a request
— the turn ends with `stop_reason: "refusal"` rather than an error. Benign
security or life-sciences work can still trip them.

This inverts the usual direction for one category: **escalating security work up
the ladder can move it toward a classifier-equipped model.** When routing
security-adjacent work, say so and recommend using the model's documented
fallback mechanism rather than assuming a single hard-coded target. For Opus 5.5, Anthropic says most cybersecurity tasks are transparently rerouted
to Opus 4.8; biology and other safeguarded categories can use different fallback
models. Do not hard-code a universal fallback target.

Fable 5.1 requires 30-day data retention and is unavailable under ZDR unless
Anthropic expressly authorizes it.

## Execution-shape notes

Suggested command shape: `claude --model <alias> --effort <level>` (omit
`--effort` for haiku). Anthropic models run natively in Claude Code — no
provider/harness switch is required.

**Model switches and effort changes are different cache events.** Switching the
model of a running conversation still invalidates the prompt cache. Opus 5 and
Fable 5.1 additionally support per-message effort via `output_config` (beta),
which preserves the prompt cache; use that capability when the active harness
exposes it. Other models, including Sonnet 5, restart the cache when effort is
changed through the top-level request setting. In Claude Code, `/effort` can
change the session effort; do not promise cache preservation unless the current
Claude Code version is known to map that turn to per-message effort. When that
is unknown, recommend a new session only if the cache-reset cost matters enough
to justify it.

Two Opus 5.5 behaviors change which shape is worth recommending:

- **It verifies its own work unprompted.** Do not recommend a separate
  verification pass, a verifier subagent, or "double-check your answer" wording
  as a routine step — that produces redundant work, not more safety. Reserve a
  second pass for cases where an independent perspective genuinely matters.
- **It delegates to subagents readily.** When recommending a subagent or agent
  team on Opus, recommend a cap alongside it. Unbounded fan-out multiplies cost
  and latency without a matching gain.

### Orchestrated workflow → ultracode

In Claude Code the **Orchestrated workflow** shape materializes as Workflow
orchestration, which requires explicit user opt-in: the keyword `ultracode` in
the task prompt (or enabled session-wide). The suggested command is the task
prompt itself with the keyword included — the router's recommendation is the
moment that opt-in becomes a deliberate decision rather than a reflex.

- **Cost model.** A workflow spawns anywhere from a handful to dozens of
  agents; expect roughly 5–20× the tokens of a solo run depending on fan-out
  and verification depth. The tier multiplier stacks on top: an orchestrated
  workflow on Opus costs Opus prices per agent.
- **When it clears the bar.** Audits and reviews where a miss is expensive
  (adversarial verification, loop-until-dry), work larger than one context
  window (mass migrations, codebase-wide sweeps), and decisions wanting
  independent perspectives (judge panels). These map to the plan-execution
  skill's decomposition signals — do not recommend it on tier alone.
- **When it does not.** Ordinary implementation, single-file debugging, or
  anything a solo run plus its tests already verifies. Opus verifies its own
  work unprompted (above), so a workflow whose only job is "check the answer
  again" is redundant spend.
- **Cap the fan-out.** As with subagents, recommend a bound (finder count,
  verification votes, loop rounds) alongside the shape.

### Agent team → Agent Teams (experimental)

Reviewed 2026-08-08 against code.claude.com/docs/en/agent-teams. In Claude
Code the **Agent team** shape materializes as the experimental Agent Teams
feature, behind explicit opt-in: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in
the environment or settings. As with ultracode, name the opt-in in the
recommendation — it is a deliberate decision, not a default.

- **Mechanism — active coordination, not hand-offs at seams.** A permanent
  lead session spawns teammates, each a separate Claude Code instance with
  its own context window and prompt cache. They coordinate through a shared
  task list (teammates claim work themselves) and native peer-to-peer mailbox
  messages, mid-work — the team does not need manual relay or file-based
  hand-off notifications.
- **Model per teammate: yes. Effort per teammate: no.** Each teammate's model
  is choosable (in the spawn prompt, or via the "Default teammate model"
  setting), so a decomposed plan can route each part to its own model.
  **Effort is inherited from the lead with no per-teammate override** — parts
  routed to different effort levels cannot be expressed as one team; split
  the team or stage the odd part as a separate session.
- **Cost.** Roughly 7× a solo session, scaling linearly with team size and
  lifetime; each teammate bills its own full context and keeps its own cache.
  The docs' own cost advice matches this policy: workhorse-tier (sonnet)
  teammates by default, teams of 3–5, shut teammates down when their part
  ends.
- **Limitations (as of 2026-08).** Same machine only; one team per session;
  no nested teams; `/resume` and `/rewind` do not restore teammates. Work
  that must survive a session restart should not be shaped as a team —
  prefer a staged pipeline of plain sessions.

### Cross-session messaging ("socket")

Since v2.1.224 (2026-08-07), local Claude Code sessions on the same machine
discover each other (`ListAgents`) and exchange plain-text messages
(`SendMessage`) over a Unix domain socket; cross-machine delivery routes
through Anthropic servers. **This is a coordination medium, not an execution
shape**: it creates no new context, cannot choose a model or effort (the
receiver's current settings apply), and carries text only — never recommend it as a routing
destination.

What it changes for routing:

- **It cheapens coordination for Staged pipeline and independent parallel
  sessions** — the shapes that previously needed the user to relay hand-off
  notifications by hand. It is *not* how Agent Teams coordinate; teams have
  their own task list and mailbox (above).
- **The message is the bell, not the package.** Structured hand-off contracts
  (specs, file lists, diffs) still travel via files or branches; the message
  only says they are ready and where.
- **Cost and timing.** Each delivered message starts a turn in the receiving
  session, billed against that session's full context; caches are per-session
  and never shared. Delivery waits for the receiver's turn boundary — it is
  not a synchronous orchestration channel; for synchronous fan-out the shape
  is still a subagent or an orchestrated workflow.

Switching the model of a running conversation invalidates its prompt cache and
re-reads the history at full price. Prefer a new session or a subagent over
repeatedly switching a long-running main conversation. Do **not** apply that
warning mechanically to an Opus 5 or Fable 5.1 effort-only change when the
harness is using per-message effort; that path preserves the cache.
