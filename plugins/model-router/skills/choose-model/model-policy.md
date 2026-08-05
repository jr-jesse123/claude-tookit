# Claude Code model routing policy

Last reviewed: 2026-07-28

This file is the **single source of truth for routing decisions**. `SKILL.md` owns
the procedure for applying it; it deliberately contains no model criteria of its
own. When routing changes, change it here only.

Treat this as policy, not as a claim about model capability. Update it when your
own logged evidence contradicts it — see [Calibration](#calibration).

## Baseline

| `--model` | Role | Default `--effort` | Context | $/MTok in-out |
| --- | --- | --- | --- | --- |
| `haiku` | Bounded, mechanical, high-volume work | **omit — see note** | 200K | $1 / $5 |
| `sonnet` | Default for daily implementation | `medium` | 1M | $3 / $15 |
| `opus` | Reasoning, architecture, investigation, high-risk work | `high` (`xhigh` for coding/agentic) | 1M | $5 / $25 |
| `fable` | Exceptional long-horizon and very large tasks | `high` | 1M | $10 / $50 |
| `claude-opus-4-8` | Regression and compatibility only | `high` | 1M | $5 / $25 |

Prices as of 2026-07-28; Sonnet has a promotional $2/$10 rate through 2026-08-31.
**Fable costs exactly 2× Opus per token** — that ratio is the whole economic
argument for the top of the ladder, so keep it in view when recommending it.

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

Apply in order unless a [hard override](#hard-overrides) fires.

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

## Hard overrides

Go straight to Opus `high` or above, skipping the scoring in `SKILL.md`, when the
task involves:

- possible data loss or corruption;
- concurrency or transaction semantics;
- security boundaries;
- a production migration;
- distributed consistency;
- a weak or misleading test oracle;
- irreversible architectural consequences;
- unfamiliar compiler or runtime behavior.

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

Two Opus 5 behaviors change which shape is worth recommending:

- **It verifies its own work unprompted.** Do not recommend a separate
  verification pass, a verifier subagent, or "double-check your answer" wording
  as a routine step — that produces redundant work, not more safety. Reserve a
  second pass for cases where an independent perspective genuinely matters.
- **It delegates to subagents readily.** When recommending a subagent or agent
  team on Opus, recommend a cap alongside it. Unbounded fan-out multiplies cost
  and latency without a matching gain.

Switching the model of a running conversation invalidates its prompt cache and
re-reads the history at full price. Prefer a new session or a subagent over
repeatedly switching a long-running main conversation.

## Calibration

Benchmarks are a prior; your own completed tasks are evidence.

**The log lives at `${CLAUDE_PROJECT_DIR}/.claude/model-calibration.jsonl`** — in
the project, not beside this file. A plugin's own directory is replaced on every
update and is documented as ephemeral, so a log kept there would be silently
wiped the first time the plugin is upgraded. The project path also keeps the
history next to the codebase whose routing it describes, which is the scope that
actually matters: routing that fits an Oracle-backed service will not fit a
static site.

The advisor **never writes this file.** It runs before the task, and every
outcome field (`escalated`, `corrections`, `tests`, …) is only knowable after
the task ends — so an entry written at recommendation time cannot be honest.
The advisor reads the log when present and emits a ready-to-run logging
command with the outcome flags left as placeholders.

**Recording an entry — in order of preference:**

1. **`/log-calibration`** (same plugin) — invoke at the end of the task. It
   fills the outcome fields from what actually happened in the session, shows
   you the entry for confirmation, and appends via the bundled
   `log-calibration.py` script. The script is the plugin's only write path:
   append-only, fixed to `.claude/model-calibration.jsonl`, and it validates
   every field against this schema before writing — which is why it can be
   allowlisted on its own without granting a blanket `Write` permission.
2. **Run the emitted command yourself**, filling in the placeholders.
3. **Manual append** (no plugin available):

```sh
mkdir -p .claude
echo '{"date":"2026-07-28",...}' >> .claude/model-calibration.jsonl
```

One JSON object per line. See `calibration.example.jsonl` next to this file for a
populated sample.

```json
{"date":"2026-07-28","category":"oracle-isolation","model":"opus","effort":"high","escalated":false,"corrections":2,"minutes":24,"tests":"pass","rework":false,"note":"scored 11/15, matched"}
```

| Field | Meaning |
| --- | --- |
| `date` | ISO date the task ran |
| `category` | Short task-category slug, reused across entries — this is the join key |
| `model` / `effort` | What was actually started with, not what was recommended |
| `escalated` | Whether a stronger model or effort was needed mid-task |
| `corrections` | Number of user corrections during the task |
| `minutes` | Wall-clock duration |
| `tests` | `pass`, `fail`, or `none` |
| `rework` | Whether the result required architectural rework afterward |
| `note` | Free text; recording the score and whether it matched is the most useful thing to put here |

Revise the routing tables above when a category accumulates entries pointing the
same way — repeated `escalated: true` means the entry is routed too cheaply;
repeated `escalated: false` with zero corrections at a high tier means it is
routed too expensively. One surprising task is noise; five in a category are not.
