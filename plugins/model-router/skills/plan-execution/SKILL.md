---
name: plan-execution
description: Decompose a task that is too large or heterogeneous to route as one unit, then route each part with the shared rubric — producing an execution plan with parts, dependencies, a model and effort per part, an assembly shape, and fan-out caps, across the providers the project accepts. Companion to choose-model, which routes atomic tasks and hands off here when it detects a multi-model shape.
when_to_use: Use when choose-model's output names a multi-model execution shape (parallel scouts, advisor plus implementer, agent team, orchestrated workflow), or when a task visibly spans parts of different difficulty — a mechanical sweep feeding a judgment call, independent workstreams, work larger than one context window. Never execute the plan.
argument-hint: "[task description] [--providers=anthropic,openai]"
disable-model-invocation: true
model: opus
effort: high
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git diff --stat *)
  - Bash(git diff --name-only *)
  - Bash(git log --oneline *)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Execution planner

Plan how to run the task in `$ARGUMENTS` as more than one routed piece of
work. If `$ARGUMENTS` is empty, evaluate the most recent task the user
described — including a task `choose-model` just handed off.

**You are not doing the task.** Do not implement, edit, or execute any part of
it, and do not run the commands you end up suggesting. Inspect the repository
only to find real part boundaries (project layout, test topology, ownership
seams), with the read-only tools above.

The premise is an inversion of the single-task router: **decompose first,
route after.** `choose-model` answers "which model for this task" and cannot
answer when the honest answer is plural; this skill cuts the task into atomic
parts and applies the same shared rubric once per part. Nothing here re-defines
scoring — the rubric, tiers, tie-break, and effort rule come from
`${CLAUDE_PLUGIN_ROOT}/reference/routing-core.md`, and everything
model-specific from the provider policies. This file owns only the
decomposition rules, the assembly shapes, and the plan output.

## 1. Resolve providers and load inputs

Accepted providers come from, in order of precedence:

1. `--providers=` in `$ARGUMENTS` — comma-separated; `claude` is an alias for
   `anthropic`.
2. The `providers` array in `${CLAUDE_PROJECT_DIR}/.claude/model-router.json`.
3. Default: `anthropic` alone.

Then read:

- `${CLAUDE_PLUGIN_ROOT}/reference/routing-core.md` — always.
- **Only `${CLAUDE_PLUGIN_ROOT}/reference/policies/<provider>.md` for each
  accepted provider**, including its **Execution-shape notes** — they decide
  which assembly shapes are even available in that provider's harness and what
  they cost.
- `${CLAUDE_PROJECT_DIR}/.claude/model-calibration.jsonl` if it exists,
  interpreted per the routing core's thresholds — matched per part, by each
  part's `category` slug.

## 2. Gate: decomposition must pay for itself

First route the task **as a unit** with the routing core (a quick pass — no
output yet). Decompose only when at least one of these holds:

- The unit routing lands on a multi-model shape, or `choose-model` already
  handed off here.
- The task visibly contains parts that would score **at least one tier
  apart** — a mechanical sweep feeding a judgment call, boilerplate around an
  architectural decision.
- Independent parts could genuinely run in parallel.
- Oracle weakness ≥ 2 with blast radius ≥ 2, or context scale = 3 — the
  structured-verification and larger-than-one-context signals.

If none holds, the task is atomic: output one line —
`Atomic task — run /model-router:choose-model instead.` — optionally followed
by the unit route you already computed, and stop. A plan for an atomic task is
pure coordination overhead.

## 3. Decompose into parts

Cut the task into parts, each of which must be:

- **Independently describable** — a prompt someone could execute without
  reading the other parts' prompts.
- **Independently routable** — atomic in the routing core's sense: one model
  runs it end to end.
- **Independently checkable** — it names its own oracle: the test, diff
  property, or review that says the part is done and correct.

Make dependencies explicit — which parts wait on which, and what each hand-off
consists of. Prefer cut lines that fall on real seams:

- **By tier** — separate work that scores mechanical from work that scores
  frontier, so the cheap volume does not ride on frontier prices.
- **By independence** — parts with no data flow between them can run in
  parallel.
- **By role** — plan / implement / verify, when the planning or the
  verification genuinely needs a different tier than the implementation.
- **By context** — when the working set exceeds one context window, the cut
  must make each part's input self-sufficient.

Keep it to **2–7 parts**. More than that means the task should be staged:
decompose the first stage fully, list the later stages as one line each, and
say that they get their own plan when reached. Do not cut below the
coordination overhead — a part whose execution is cheaper than describing its
interface should be merged into its neighbor.

## 4. Route each part

Apply `routing-core.md` **once per part**, exactly as `choose-model` would for
a whole task:

- **Hard overrides fire per part** and do not leak: a data-loss-risk part gets
  the frontier floor even if it is small, and it does not drag its siblings up.
- Score the five dimensions per part, pick the tier, nominate candidates,
  break provider ties, translate effort — all from the core and the accepted
  policies.
- **Calibration slugs are per part.** Reuse existing slugs from the log where
  they fit; a decomposed migration whose scan part logs under `repo-scan` and
  whose schema part logs under `schema-migration` builds evidence for both
  categories at once.
- The cheapest-that-clears-the-bar rule applies per part, and each part's plan
  entry carries its own "why not one tier cheaper" failure.

Two sanity checks on the finished routing:

- **If every part lands on the same tier as the unit routing from step 2, the
  decomposition bought nothing.** Say so and fall back to the atomic answer —
  unless the point was parallelism or verification structure rather than tier
  spread, in which case name that as the payoff.
- **A part is only as routable as its inputs.** When a cheap part consumes a
  judgment part's output, the judgment part's deliverable must include the
  contract the cheap part needs (the plan, the spec, the file list) — put that
  in the Interfaces section.

## 5. Assemble the shape

Pick the shape that matches the dependency structure — this is where the
multi-model shapes that `choose-model` only detects get actually planned:

| Shape | Structure it fits |
| --- | --- |
| **Parallel scouts** | Independent read-only parts (searches, inventories, analyses) on a mechanical- or workhorse-tier model, fanned out, results joined by the caller |
| **Advisor plus implementer** | A frontier part produces the plan/spec/review; workhorse parts implement against it. The documented pattern on both providers — see each policy's Execution-shape notes |
| **Agent team** | Independent workstreams with real deliverables each, under active coordination — a lead, a shared task list, native peer messaging where the harness provides them (see the policies' Execution-shape notes for mechanism, opt-in, and per-teammate model/effort constraints) |
| **Orchestrated workflow** | Exhaustiveness or adversarial verification structured as fan-out: diverse finder lenses, independent verification of findings, judge panels. Buys coverage and confidence, not intelligence — the agents run on the same models, so it never substitutes for a higher tier |
| **Staged pipeline** | Sequential parts too large or too far apart in tier to share a session — each stage a fresh session or subagent, hand-offs written down |

Constraints:

- **Respect the provider's Execution-shape notes.** They are load-bearing
  here: harness availability (an orchestrated workflow on Claude Code is
  Workflow orchestration behind the `ultracode` opt-in; on OpenAI it is a
  hand-built script), cost multipliers, and behavior notes (a frontier model
  that already verifies its own work makes a same-perspective verify part
  redundant — a verification part must add an *independent* perspective or a
  different lens, or it is spend without safety).
- **Every fan-out gets a named cap** — scout count, verification votes, loop
  rounds, team size. An uncapped fan-out is not a plan.
- **Hand-offs name their transport.** For each Interfaces entry, say how the
  hand-off travels: the artifact itself (spec, file list, branch) goes through
  the repository, and the *notification* goes through whatever the shape
  provides — a team's own task list and mailbox, a workflow's return value, or,
  between plain sessions in a staged pipeline, the harness's cross-session
  messaging where the provider's Execution-shape notes say it is available.
  A hand-off whose transport is "the user relays it" is a cost — count it
  against the decomposition in the step 2 gate.
- **Name what the single-agent run would miss.** The most expensive shapes
  (orchestrated workflow, agent team) must justify themselves the same way a
  tier does: a concrete miss, not a feeling of thoroughness.

## 6. Output

Return exactly this structure and nothing else.

```
Task: <one line>
Assembly shape: <shape> — <named caps, e.g. "4 scouts max, 3 verification votes">
Providers: <accepted list>
Confidence: <low | medium | high>

Plan:
| # | Part | Depends on | Provider | Model | Effort | Tier | Oracle |
| - | ---- | ---------- | -------- | ----- | ------ | ---- | ------ |
<one row per part; "-" for no dependency>

Sequencing:
- <what runs in parallel, what waits on what, where the stages break>

Per-part reasons:
- Part <n> (<name>): <highest dimension or override> — why not one tier
  cheaper: <the named failure>

Interfaces:
- <part> → <part>: <what is handed over, in what form>

Suggested execution:
- <concrete first move per the policies' execution notes: the subagent
  prompts to write, the command per stage, the ultracode keyword when the
  shape requires it>

Escalate if:
- <observable per-part or plan-level signal that would justify moving a part up>

Calibration (one command per part, run as each part finishes — or invoke
/log-calibration at each part's end):
python3 "${CLAUDE_PLUGIN_ROOT}/skills/log-calibration/log-calibration.py" \
  --provider <provider> --category "<part slug>" --model <alias> \
  --effort <level, omit when n/a> --note "plan-execution part <n>/<total>" \
  --escalated <?> --corrections <?> --minutes <?> --tests <?> --rework <?>
```

## Rules for the output

- **A plan whose every part lands frontier is a failed decomposition.** Either
  the task is atomic (defer to choose-model) or the cuts missed the cheap
  volume — recut before outputting.
- Each part's "why not one tier cheaper" follows the routing core's rule: a
  named failure or a cheaper part.
- Confidence is `low` whenever part boundaries were assumed rather than read
  from the repository or the task description.
- The plan is advisory: do not execute any part, do not run the suggested
  commands, and do not write anything — `Write` is disallowed here by design.
