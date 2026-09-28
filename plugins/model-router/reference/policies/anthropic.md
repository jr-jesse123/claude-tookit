# Anthropic provider policy

Last reviewed: 2026-09-28

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
| workhorse | `sonnet` | Current alias target: Sonnet 5.5; keep scoped long-running work here when judgment/oracle/risk remain favorable |
| frontier | `opus` | Current alias target: Opus 5.5 |
| exceptional | `opus` | Opus 5.5 at `xhigh`/`max`; long horizon alone no longer promotes to Fable |

`fable` (Fable 5.1) sits **outside the normal tier ladder** as an evidence-gated
escape hatch. Route to it only when project calibration, a task-specific eval,
or a serious Opus 5.5 attempt demonstrates a capability advantage worth the
premium.

`claude-opus-4-8` sits outside the ladder: regression comparison, compatibility
with an already-evaluated workflow, and the documented refusal fallback only.

## Baseline

| `--model` | Role | Default `--effort` | Context | $/MTok in-out |
| --- | --- | --- | --- | --- |
| `haiku` | Bounded, mechanical, high-volume work | **omit — see note** | 200K | $1 / $5 |
| `sonnet` | Sonnet 5.5: default for daily implementation, bug fixing, review, and scoped agentic coding | `medium` (policy default; Claude Code/apps default `medium`, Claude Platform default `high`) | 1M | $2 / $10 |
| `opus` | Opus 5.5: careful judgment, architecture, investigation, weak-oracle and high-risk work | `medium` (vendor default; raise from evidence) | 1M | $4 / $20 |
| `fable` | Fable 5.1: calibration-only escape hatch, not a normal escalation tier | `high` | 1M | $10 / $50 |
| `claude-opus-4-8` | Regression and compatibility only | `high` | 1M | $5 / $25 |

Prices reviewed 2026-09-28. Sonnet 5.5 remains $2/$10 with $0.20/MTok cache reads; Anthropic reports 30%+ faster generation than Sonnet 5 and up to 30% lower cost per task from fewer tokens/tool calls. Opus 5.5 is $4/$20, with $0.20/MTok cache reads and $5/MTok cache writes. Fable 5.1 remains $10/$50 with $0.25/MTok cache reads.

> **Do not pass `--effort` with `haiku`.** Haiku 4.5 does not accept the effort
> parameter; the four other rows accept `low`, `medium`, `high`, `xhigh`, `max`.

> **Haiku's context is 200K, not 1M.** A task whose input alone approaches that
> ceiling is disqualified from Haiku regardless of how mechanical it is.

## Effort ladder

| Level | Use for |
| --- | --- |
| `low` | Short, scoped, latency-sensitive work with a strong oracle |
| `medium` | Normal implementation; the Sonnet 5.5 default in Claude Code/apps and the Opus 5.5 API default |
| `high` | Substantial implementation/debugging or more verification when the current model is still intellectually adequate; Claude Platform defaults Sonnet 5.5 here |
| `xhigh` | Demanding or long-running coding/agentic work where extra persistence is the bottleneck; compare per-task cost against moving up a model |
| `max` | Correctness dominates cost and the task is not latency-sensitive. Never a default: Sonnet 5.5 can over-explore at `max` and even score below `xhigh` on merge-oriented coding evals |

### Horizon → effort mapping

Applied to the level the rubric's dimension 2 produces:

| Horizon | Sonnet | Opus |
| --- | --- | --- |
| 0–1 | `medium` | `medium` |
| 2 | `high` | `high` |
| 3 | `xhigh` when the task remains well-scoped with a strong oracle | `xhigh`, or `max` when correctness dominates cost |

Sonnet 5.5 changes the horizon rule: long duration by itself is no longer a good
reason to promote to Opus. Anthropic reports multi-hour Sonnet work and strong
long-horizon results. If the task is well-scoped, familiar, and has a strong
oracle, Sonnet may stay in the workhorse tier at `high`/`xhigh` even when horizon
is the dimension that would otherwise push the generic rubric upward. Promote to
Opus when judgment, abstraction, weak oracle, hidden risk, or context fidelity is
the bottleneck.

Opus 5.5 still defaults to `medium`. Treat that as the starting point when Opus
is selected; raise effort from task risk/horizon or calibration rather than
inheriting Opus 5's old `high` default mechanically.

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

### Sonnet 5.5 `medium`

- Implement a specified ASP.NET or F# endpoint.
- Add xUnit or Verify tests for known behavior.
- Modify an HTMX or React component following an existing pattern.
- Add a repository method with clear SQL requirements.
- Refactor a bounded component.
- Investigate a deterministic test failure.
- Write routine technical documentation.

### Sonnet 5.5 `high`

- Debug a broader but familiar feature.
- Implement across several layers with strong tests.
- Understand brownfield code before making a bounded change.
- Review a medium-sized diff in detail.
- Work through a long but conceptually familiar test failure.
- Multi-file implementation or refactoring with clear invariants and strong automated checks.
- Simple and moderate code review where the expected failure modes are known.

### Sonnet 5.5 `xhigh`

- Multi-hour coding or agentic work whose scope is already clear and whose tests/compiler/runtime provide a strong oracle.
- Large but mechanical migrations/refactors where the architectural direction is already decided.
- Long brownfield implementation where repository understanding and tool persistence matter more than novel judgment.

Launch evidence explains this placement: Anthropic reports Sonnet 5.5 at 70.6%
on Terminal-Bench 4.0 versus 66.4% for Opus 5.5, 55.5% versus 57.8% on
CursorBench 4.0, and 1844 versus 1846 on GDPval-AA. FrontierCode still shows a
clearer Opus lead (Sonnet 5.5 52.1% at Xhigh versus Opus 5.5 54.4%). These are
within-provider launch priors, not guarantees for this repository.

Do not keep escalating Sonnet merely because its sticker price is lower. Anthropic's
launch curves show that at higher effort Sonnet 5.5 can approach Opus 5.5 in both
capability **and cost per task**. When judgment becomes the bottleneck, move to Opus
instead of buying more Sonnet effort.

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
- Large cross-project refactoring with ambiguous invariants, weak tests, or architectural choices still unresolved.
- Framework or persistence migration where compatibility, rollback, or semantic risk must still be designed.
- Investigation of several competing root-cause hypotheses.
- Building a substantial developer tool.
- Autonomous work across code, tests, CI, infrastructure, and documentation.
- Long agent runs that must repeatedly validate and correct themselves.

### Fable 5.1 — evidence-gated escape hatch

Fable is no longer a task-category destination. Do **not** route to it from task
size, duration, multi-repository scope, cache shape, or "hardest model" intuition
alone. Those workloads remain on Opus 5.5 and should first use the Opus effort
ladder.

Route to Fable only when one of these is true:

- Project calibration contains repeatable evidence that Fable succeeds on this
  category where Opus 5.5 does not.
- A task-specific eval demonstrates a material capability advantage that is
  worth the remaining price premium.
- A serious Opus 5.5 `xhigh`/`max` attempt failed because of reasoning,
  abstraction, or context-coherence quality rather than insufficient effort or
  tooling.

Even then, record the result. If Fable does not materially outperform Opus on
that category, demote it again; its role is to catch proven tails, not to occupy
a permanent rung in the ladder.

### `claude-opus-4-8`

Only for: regression comparison, compatibility with an already-evaluated
workflow, or diagnosing behavior differences between Opus 4.8, Opus 5, and Opus 5.5. It is
also the documented cybersecurity fallback target for most safeguarded Opus 5.5 requests — see
[Refusals](#refusals-on-security-adjacent-work).

## Escalation ladder

Apply in order unless a hard override (see `routing-core.md` → Hard
overrides) fires.

1. Haiku for obviously mechanical work.
2. Sonnet 5.5 `medium` for normal development.
3. Sonnet 5.5 `high` for broader familiar work that needs more persistence/verification.
4. Sonnet 5.5 `xhigh` for long-running but well-scoped work with a strong oracle.
5. Opus 5.5 `medium` when judgment, abstraction, weak oracle, context fidelity, or hidden risk is the bottleneck.
6. Opus 5.5 `high` when those same problems need more exploration/verification.
7. Opus 5.5 `xhigh`/`max` for exceptional work where both frontier judgment and long execution are required.

**Fable is not step 7.** It is an evidence-gated side path: use it only when
calibration, a task-specific eval, or a serious Opus 5.5 failure establishes a
reason to do so.

## Effort vs. model

**Raise effort first** when the current model is intellectually adequate and the
limitation is exploration, verification, or tool persistence — or when the task
turned out larger than expected but is still familiar.

**Raise model first** when judgment, abstraction, hypothesis quality, or
architectural understanding is the bottleneck; when the cheaper model reaches
plausible but shallow conclusions repeatedly; when the problem is substantially
novel; or when there is hidden semantic or operational risk.

For Sonnet 5.5 specifically, treat **scope/oracle quality** as the main boundary
with Opus 5.5. A long task with explicit acceptance criteria and strong tests can
stay on Sonnet. A shorter task with ambiguous requirements, weak observability,
concurrency/consistency risk, or architectural consequences belongs on Opus.
Because Sonnet at high effort can approach Opus's cost per task, compare the
expected total run cost rather than assuming `sonnet` is always the cheaper route.

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
- **Long horizon is no longer synonymous with a higher model.** Sonnet 5.5's
  launch evidence includes multi-hour coding and strong long-horizon knowledge
  work. Keep well-scoped, strongly testable long runs on Sonnet; use Opus when
  judgment, context fidelity, ambiguity, or risk is what makes the long run hard.
- **Opus 5.5 still owns the harder tail.** Anthropic reports successful
  multi-repository runs lasting more than 18 hours and a C→Rust migration that
  finished in 9.5 hours versus 12 hours for Fable 5.1 at 51% lower cost. Fable
  therefore still requires category-specific evidence.

## Token economics (input)

Output volume is steerable (effort, `max_tokens`, prompting) and is therefore
not legislated here — the calibration log measures it per category instead.
Input-side token density is not steerable; these notes exist so the price
tie-break (`routing-core.md` → tie-break rule 2) uses real counts:

- **Tokenizers differ within this provider.** Historical Sonnet/Opus releases
  have changed token density materially. Do not assume Sonnet 5.5 inherits
  Sonnet 5's token count for the same text; a count measured on one model is
  invalid on another — re-measure, never scale by feel.
- **Measure, don't estimate.** `count_tokens` is model-specific and cheap.
  When price decides a cross-provider or cross-tier tie on an input-heavy
  task, run the actual input through each candidate's counter before
  comparing — one API call per candidate beats any multiplier.
- **Caching bends the effective input rate, but not uniformly.** Sonnet 5.5 and
  Opus 5.5 both cost $0.20/MTok for cache reads even though fresh input is
  $2 vs $4/MTok. A warm, input-heavy session therefore narrows the Sonnet→Opus
  price gap; output/tool volume and task completion efficiency matter more than
  sticker input price. Fable 5.1 cache reads cost $0.25/MTok, so cache-heavy work
  is still not a direct Fable signal. Compare effective workload cost and let
  calibration decide any remaining capability premium.
- **No long-context surcharge** at 1M (see Context behavior) — the input rate
  is flat where OpenAI's is reportedly not.

## Refusals on security-adjacent work

Sonnet 5.5, Opus 5.5, and Fable 5.1 ship cyber safeguards/fallbacks for a narrow
set of high-risk requests. Sonnet 5.5 is the first Sonnet release to receive
these stronger cyber safeguards because Anthropic measures its cybersecurity
capability near Opus 5. Routine software development is intended to be
unaffected; security-adjacent work can still be rerouted or refused.

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
model of a running conversation still invalidates the prompt cache. Opus 5.5 and
Fable 5.1 support per-message effort via `output_config` (beta), which preserves
the prompt cache. Sonnet 5.5's launch material documents the effort ladder but
not cache-preserving per-message effort; until the Platform compatibility docs
say otherwise, treat a top-level Sonnet effort change as a cache restart. In
Claude Code, `/effort` can change the session effort; do not promise cache
preservation unless the current version is known to use a cache-safe path.

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
warning mechanically to an Opus 5.5 or Fable 5.1 effort-only change when the
harness is using per-message effort; that path preserves the cache. For Sonnet
5.5, assume an effort-only change restarts the cache until Anthropic documents a
cache-preserving per-message path.
