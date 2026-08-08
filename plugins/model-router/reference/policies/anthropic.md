# Anthropic provider policy

Last reviewed: 2026-08-05

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
| frontier | `opus` | |
| exceptional | `fable` | Costs exactly 2× Opus per token — that ratio is the whole economic argument |

`claude-opus-4-8` sits outside the ladder: regression comparison, compatibility
with an already-evaluated workflow, and the documented refusal fallback only.

## Baseline

| `--model` | Role | Default `--effort` | Context | $/MTok in-out |
| --- | --- | --- | --- | --- |
| `haiku` | Bounded, mechanical, high-volume work | **omit — see note** | 200K | $1 / $5 |
| `sonnet` | Default for daily implementation | `medium` | 1M | $3 / $15 |
| `opus` | Reasoning, architecture, investigation, high-risk work | `high` (`xhigh` for coding/agentic) | 1M | $5 / $25 |
| `fable` | Exceptional long-horizon and very large tasks | `high` | 1M | $10 / $50 |
| `claude-opus-4-8` | Regression and compatibility only | `high` | 1M | $5 / $25 |

Prices as of 2026-07-28; Sonnet has a promotional $2/$10 rate through 2026-08-31.

> **Do not pass `--effort` with `haiku`.** Haiku 4.5 does not accept the effort
> parameter; the four other rows accept `low`, `medium`, `high`, `xhigh`, `max`.

> **Haiku's context is 200K, not 1M.** A task whose input alone approaches that
> ceiling is disqualified from Haiku regardless of how mechanical it is.

## Effort ladder

| Level | Use for |
| --- | --- |
| `low` | Short, scoped, latency-sensitive work with a strong oracle |
| `medium` | Normal implementation — the Sonnet default |
| `high` | Judgment is the bottleneck; the Opus default |
| `xhigh` | **Coding and agentic work on Opus**, and long execution horizons |
| `max` | Correctness matters more than cost, and the task is not latency-sensitive. Prone to overthinking on simple work — never a default |

### Horizon → effort mapping

Applied to the level the rubric's dimension 2 produces:

| Horizon | Sonnet | Opus |
| --- | --- | --- |
| 0–1 | `medium` | `high` |
| 2 | `high` | `xhigh` |
| 3 | `high` | `xhigh`, or `max` when correctness dominates cost |

Coding and agentic work on Opus starts at `xhigh` regardless of horizon — that
is the policy's starting point, not an escalation.

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

### Opus `high`

- Investigate Oracle isolation or concurrency behavior.
- Design transaction and idempotency semantics.
- Make an architectural decision involving coupling or availability.
- Review a change for subtle semantic or distributed-system defects.
- Design an IL instrumentation, compiler-service, analyzer, or LSP approach.
- Research undocumented or conflicting framework behavior.
- Diagnose an intermittent E2E failure with no clear oracle.
- Model a complex domain in F#, or compare F# and C# representations.

### Opus `xhigh`

- Any substantial coding or agentic work — this is the recommended starting
  point for Opus on code, not an escalation from `high`.
- Large cross-project refactoring.
- Framework or persistence migration.
- Investigation of several competing root-cause hypotheses.
- Building a substantial developer tool.
- Autonomous work across code, tests, CI, infrastructure, and documentation.
- Long agent runs that must repeatedly validate and correct themselves.

### Fable

- Multi-repository or exceptionally large migrations.
- Work whose human equivalent spans multiple days.
- Very long autonomous execution where context coherence is the main risk.
- A task Opus `xhigh` attempted seriously and could not complete.
- High-value work where a small increase in success probability is worth 2× cost.

Do not choose Fable for ordinary review, explanation, or feature work merely
because it is the strongest model.

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
4. Opus `high` when reasoning or judgment is the bottleneck.
5. Opus `xhigh` for coding, agentic work, or a long execution horizon.
6. Opus `max` when correctness dominates cost and latency does not matter.
7. Fable `high` after a serious Opus failure, or for exceptional task size.
8. Fable `xhigh` only when maximum long-horizon capability is justified.

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
- **Fable's context coherence.** Very long autonomous execution where context
  coherence is the main risk is already Fable's category (above) — that is
  the exceptional-tier answer when even Opus's window discipline is the
  binding constraint.

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
- **Caching bends the effective input rate by ~10×.** Cache reads bill at
  ~0.1× base input; an input-heavy session with a warm cache pays a fraction
  of sticker. This compounds with ecosystem affinity (tie-break rule 3): the provider
  whose harness already holds the session's cache wins input-heavy ties
  almost by default.
- **No long-context surcharge** at 1M (see Context behavior) — the input rate
  is flat where OpenAI's is reportedly not.

## Refusals on security-adjacent work

Opus 5 and Fable 5 ship elevated cybersecurity safeguards and can decline a
request outright — the turn ends with a refusal rather than an error. Benign
security tooling and life-sciences work occasionally trip them.

This inverts the usual direction for one category: **escalating security work up
the ladder moves it toward the models most likely to refuse it.** When routing
security-adjacent work, say so, and name `claude-opus-4-8` as the fallback —
cyber-category refusals route there by design. That is the one case where the
regression-only row is the correct destination.

Fable 5 additionally requires 30-day data retention and is unavailable to
organizations configured for zero retention.

## Execution-shape notes

Suggested command shape: `claude --model <alias> --effort <level>` (omit
`--effort` for haiku). Anthropic models run natively in Claude Code — no
harness switch, and the session's prompt cache survives.

Two Opus 5 behaviors change which shape is worth recommending:

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
repeatedly switching a long-running main conversation.
