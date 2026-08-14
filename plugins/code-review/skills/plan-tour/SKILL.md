---
name: plan-tour
description: Ground an implementation plan in the real codebase before any code is written — trace the terrain the plan touches, narrate how it works today and how the plan transforms it, paint a prospective Mermaid delta (existing code dimmed, planned additions ⊕, planned removals ⊖), state the contracts the plan will change (today's promise quoted from the code → the planned promise, compatibility, blast radius), and report factual plan-vs-code discrepancies plus the open questions the plan leaves. Use after a plan exists and before implementing — not for touring diffs (pr-tour) or finding bugs (quick-review).
argument-hint: [path to a plan file, or pasted plan text; defaults to the plan in this conversation]
allowed-tools: Bash(git log:*), Bash(git show:*), Bash(npx --yes @zabaca/mermaid-validate:*), Read, Grep, Glob
---

# Plan tour

The mirror of `pr-tour` across time: `pr-tour` paints the delta that already
happened; this skill paints the delta that is *about to* happen. Given a
plan, it explores the code the plan touches and answers two questions the
plan itself cannot: **does the terrain look the way the plan assumes?** and
**what will the change look like once it lands?**

This skill does not plan and does not implement. It proposes no steps, no
alternatives, no improvements. The only thing it says *about* the plan is
where the plan and the code factually disagree — with citations. Deciding
what to do with a discrepancy (fix the plan, accept the difference) belongs
to the user and to plan mode, not here. Write the tour in the language the
user is speaking.

## Resolve the plan

Decide which plan to tour, in this order:

1. `$ARGUMENTS` is a path → Read the file; that is the plan.
2. `$ARGUMENTS` is prose → treat the text itself as the plan.
3. No argument → use the most recent plan in this conversation (typically
   what just came out of plan mode).

If there is no plan anywhere, say so and stop — do not invent one, and do
not fall back to touring the working tree. Suggest plan mode (or writing
the plan down) and end there.

## Trace the terrain

The plan names its touch points; the code decides whether they are real.

1. Extract every touch point the plan states or implies: files, symbols,
   routes, tables, config keys, commands. Classify each by the plan's
   intent: **create** (does not exist yet), **modify**, **remove**, or
   **assumed context** (the plan relies on it but does not change it).
2. Explore around each with Read, Grep, and Glob. For modify/remove
   targets: find the real callers, callees, and contracts — especially the
   ones the plan does not mention. For assumed context: verify the
   assumption (does the symbol exist, with that signature, called from
   where the plan thinks?). For create targets: check nothing already
   occupies the name or the role. `git log --oneline -5 -- <path>` on a
   load-bearing file is cheap context for how live that area is.
3. Record every mismatch between what the plan says and what the code
   shows, with `path:line` — these become the *Plan vs. code* section.
   A neighbor the plan silently misses (a third call site, a second
   implementation of the interface) is a mismatch too.
4. Split the plan's touch points into independent groups exactly as
   `pr-tour` does: two files belong together only if one calls, imports,
   or tests the other — directly or through another touched file.

## Report — how the plan lands

A cohesive plan gets one tour; independent groups each get their own,
ordered most substantive first. No group headers when there is one group.

**Narrative.** One paragraph per group, in two movements: how the terrain
works *today* (entry point → what triggers what), then how the plan
transforms it (what appears, what disappears, net effect). Name real files
and symbols — for pieces that do not exist yet, use the name the plan gives
them, and say they are planned.

**Prospective delta.** Default is a single Mermaid `flowchart` painting the
union of today and the planned end state, with the same conventions as
`pr-tour`: planned-new elements solid and thicker (`classDef added`, ⊕ in
the label), planned-removed dashed (`classDef removed`, ⊖), planned-modified
in default styling — undimmed and unmarked — and untouched context dimmed
gray, edges painted with `linkStyle` to match. The one semantic shift: ⊕
means *will exist*, not *was added* — the diagram is a promise, and saying
so once near the diagram is enough. Skip the diagram when the group touches
only 1–2 files.

Multiple diagrams are an explicit option when distinct perspectives or zoom
levels help more than one picture can — an overview `flowchart` of the
terrain plus a `sequenceDiagram` of the planned runtime flow, or a macro
map plus a zoom into the subsystem the plan reshapes most. `pr-tour`'s
discipline applies unchanged: each diagram answers a different question
("who will depend on whom?" vs "in what order will it happen?") and
carries a one-line title naming that question; if two diagrams answer the
same question, keep one. And when the plan changes the topology so much
that the painted union becomes a tangle of marks, draw the painted pair
instead — the before/after pair from the `pr-tour` examples, with *before*
= today and *after* = the plan's end state. The criterion is clarity,
never quantity.

Read before drawing — never from memory:

- `${CLAUDE_PLUGIN_ROOT}/skills/pr-tour/examples/flowchart.md` (the
  `pr-tour` skill's examples directory, sibling of this skill's folder, if
  the variable is unavailable) — painting rules and edge accounting; they
  apply here unchanged.
- `${CLAUDE_SKILL_DIR}/examples/prospective.md` — the full output shape of
  a plan tour at small scale.

Other diagram types follow `pr-tour`'s selector: a planned runtime
interaction reads as a `sequenceDiagram`, a planned lifecycle as a
`stateDiagram-v2`, a planned schema as an `erDiagram` — when one of those
fits better, read the matching file in the `pr-tour` examples directory
first. The criterion is the reader's question, never variety.

**Validate before presenting.** When `npx` is available, run each fence
through the parser — the command must start with `npx`, so feed the body
via heredoc:

```
npx --yes @zabaca/mermaid-validate - <<'DIAGRAM'
<fence body>
DIAGRAM
```

On failure, fix and re-validate; double-check `linkStyle` indices against
the edge order. If `npx` is unavailable or offline, skip silently.

## Report — contracts (only when the plan changes one)

`pr-tour`'s contracts section, shifted to the future tense. When the plan
changes a promise other code relies on — an exported type or interface, a
function signature, an event payload, an endpoint, a DB schema, a config
key — add one entry per contract, in `pr-tour`'s promise → verdict →
radius shape:

- **Promise delta** — today's real shape, quoted from the code with
  `path:line`, → the shape the plan promises. When the plan's stated shape
  and the code's current shape already disagree, that is a *Plan vs. code*
  entry, not a contract delta.
- **Compatibility verdict** — additive or breaking, always with direction:
  for whom, same rules as `pr-tour` (a widened union breaks exhaustive
  consumers, a new interface member breaks every implementor, …).
- **Blast radius** — every producer, consumer, or implementor bound by
  today's promise, found with Grep and anchored `path:line`, each marked
  as one the plan accounts for or one **the plan does not mention**. An
  unmentioned consumer usually earns a *Plan vs. code* entry too.
  Consumers no Grep can reach (external clients, rows and messages
  persisted under today's shape, serialized payloads) get a one-line note
  — the plan has to survive them after deploy.

When no contract changes, omit the section. Read
`${CLAUDE_PLUGIN_ROOT}/skills/pr-tour/examples/contracts.md` before
writing it — the entry shape applies unchanged; only the tense shifts.

## Report — plan vs. code

The section that earns the tour its keep. One entry per mismatch found
while tracing, each in the same shape:

```
- The plan assumes `charge()` has one caller (`api/orders.ts`); the code
  shows three — `api/orders.ts:88`, `jobs/retry.ts:41`, `cli/backfill.ts:19`.
```

*The plan assumes … ; the code shows … .* Always factual, always cited.
Typical kinds: a symbol or path that does not exist; a signature that
differs; a caller, implementation, or route the plan misses; behavior the
plan schedules that already exists; a contract wider or narrower than
assumed. Never editorialize ("the plan should…") and never rank — the
reader decides what is fatal and what is noise.

If tracing found no mismatches, say so in one line — a verified plan is a
result, not an empty section.

## Report — terrain reading order

Per group, a numbered list of the *existing* files worth reading before
implementing — the same entry shape as `pr-tour`: why this position, then
one or two concrete things to look at, anchored as `path:line`. Planned-new
files do not appear (there is nothing to read yet); modify/remove targets
and their load-bearing neighbors do. Contracts first, then the code the
plan will change following the flow, then the neighbors that constrain it,
then existing tests (they are the behavior the plan must not break —
unless it says so).

## Report — open questions

Decisions the plan leaves unanswered that the code cannot answer either —
each one names the spot where the answer will land:

```
- Per-route or global limits? Decides whether `config/limits.ts` is a map
  or a scalar, and how `middleware/rate-limit.ts` looks up its budget.
```

Only questions whose answer changes the implementation; do not answer them,
and do not manufacture questions to fill the section. None is a fine
answer — one line.

## What not to do

- No planning: no step sequences, no alternatives, no estimates, no
  "consider instead". The plan's content is the user's; only its collisions
  with reality are yours.
- No implementation, no scaffolding — every tool here is read-only.
- No code review of the existing terrain. A bug noticed while tracing gets
  one line at the end ("possible issue in X — run
  `/code-review:quick-review` to confirm") at most.
- Do not restate the plan — the user wrote it; tour the terrain, not the
  text.
- Do not pad: no diagram for a 1–2 file group, no invented questions, no
  discrepancy entries for cosmetic differences (a paraphrased name the
  plan clearly means).
