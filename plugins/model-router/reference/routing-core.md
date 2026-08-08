# Routing core

Shared by the `choose-model` and `plan-execution` skills: the hard overrides,
the task rubric, the tier layer, the calibration-log thresholds, the
cross-provider tie-break, and the effort translation rule. **This file names no
models** — everything model-specific (tier mappings, effort ladders, prices,
category lists, execution notes) lives in `policies/<provider>.md`. The skills
own their procedures and output formats; when the *scoring* changes, change it
here only.

The unit this file scores is **one atomic task** — a piece of work one model
runs end to end. `choose-model` applies it to the whole task; `plan-execution`
applies it once per part after decomposing. It never scores a bundle: if the
honest answer to "which model" is plural, the input is not atomic — decompose
first, score after.

## Hard overrides

Hard overrides are properties of the **task**, not of any provider. If the task
involves any of:

- possible data loss or corruption;
- concurrency or transaction semantics;
- security boundaries;
- a production migration;
- distributed consistency;
- a weak or misleading test oracle;
- irreversible architectural consequences;
- unfamiliar compiler or runtime behavior;

skip the scoring: the floor is the **frontier tier** at that provider's
high-effort floor. Note which override fired; effort and execution shape still
need choosing. Accepted policies may attach provider-specific notes that fire
alongside an override (e.g. refusal risk on security-adjacent work in the
Anthropic policy).

When scoring a *part* of a decomposed task, overrides apply to the part alone:
a data-loss-risk part gets the frontier floor even if it is small, and it does
not drag the sibling parts up with it.

## Five dimensions, 0–3 each

Score only these. Each is one line of justification in the output.

| # | Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- | --- |
| 1 | **Reasoning novelty** | Familiar transformation | Known engineering pattern | Complex interaction of known concepts | Novel problem needing new hypotheses |
| 2 | **Execution horizon** | One or two operations | Normal implementation and tests | Many tool calls, iterative debugging | Longer than a single sitting |
| 3 | **Oracle weakness** | Compiler or deterministic test proves it | Good automated tests exist | Tests incomplete or expensive | Correctness hard to observe at all |
| 4 | **Blast radius** | Local and easily reversible | Normal application defect | Cross-layer, or production/data risk | Failure could silently corrupt behavior or data |
| 5 | **Context scale** | Small and self-contained | Normal repository exploration | Large codebase or long history | Very large or multi-repository |

## Decision rule → capability tier

Providers are compared through four abstract tiers; each policy maps its own
models onto them. The rubric outputs a tier, never a model.

| Tier | Meaning |
| --- | --- |
| **mechanical** | Bounded, high-volume, mechanical work with a strong oracle |
| **workhorse** | Normal daily implementation |
| **frontier** | Reasoning, architecture, investigation, high-risk work |
| **exceptional** | Long-horizon or very large work beyond a single sitting |

Apply in order; the first match wins.

1. Any dimension scored **3** → frontier, effort floor at the provider's
   high level.
2. Total **≥ 9** → frontier.
3. Total **5–8** → workhorse.
4. Total **≤ 4** → mechanical, but only if no dimension exceeds 1 and the input
   fits the candidate model's context window. Otherwise workhorse at the
   provider's default effort.
5. Frontier already indicated and the task exceeds a single sitting, or a
   serious frontier attempt already failed → consider exceptional, per the
   accepted policies.

## Calibration-log thresholds

The log's schema, location, and recording flow live in `calibration.md` next
to this file. When the log exists, look only at entries whose `category`
matches this task (or this part) and whose `provider` is accepted (entries
without a `provider` field are `anthropic`):

- **Three or more entries with `escalated: true`** at a tier → that route is
  too cheap. Recommend one tier up and say the log drove it.
- **Three or more entries with `escalated: false` and `corrections: 0`** at
  the frontier tier or above → routed too expensively. Recommend one tier down.
- **Fewer than three, or mixed** → not yet a signal. Ignore it and route on
  the score.

Logged evidence outranks the score and any external research; it does not
outrank a hard override.

## Nominate candidates and break ties

Each accepted policy nominates its model for the tier. With one provider, that
is the recommendation. With more than one, break the tie in this order — and
name which rule decided in the output:

1. **Logged evidence.** Calibration entries matching this category for one
   provider's candidate outrank everything below.
2. **Price.** $/MTok at the tier — the only directly comparable axis across
   providers. Compare the blended cost for the task's expected shape
   (input-heavy exploration vs output-heavy generation), not just the sticker.
   For input-heavy tasks the sticker alone is wrong twice: tokenizers differ
   across models and providers (the same file yields different counts — never
   reuse a count measured on another model), and caching/surcharge rules bend
   the effective input rate. See each policy's **Token economics** section;
   when a multiplier is unknown, say so instead of faking precision.
3. **Ecosystem affinity.** Prefer the provider whose harness the session is
   already running in. Claude Code executes only Claude models — recommending
   an OpenAI model implies a different harness (Codex CLI, a Responses API
   script, another agent), a cold prompt cache, and a different tool-calling
   dialect. That switch must buy something concrete; in an even tie, stay.

**Never resolve a tie by comparing public benchmark scores across providers.**
Benchmarks are priors of different shapes measured on different suites; the
calibration log is the only comparator that reflects your tasks.

## Effort

Take the level from dimension 2 (execution horizon) and translate it with the
accepted provider's ladder — each policy owns its horizon→effort mapping, its
level names, and its parameter (`--effort` vs `reasoning_effort`). **Never map
one provider's level names onto another's**; identical words carry different
semantics across providers.

## The cheapest-that-clears-the-bar rule

Recommend the cheapest option that clears the bar — this plugin exists to
prevent overspending as much as underspending, and a reflexive frontier-tier
recommendation makes it worthless. The check is the **"Why not one tier
cheaper"** line every output must carry: it must name a failure, not a
feeling. "The workhorse tier would likely miss the write-skew under
`READ COMMITTED`" is useful; "this needs deeper reasoning" is not. If you
cannot name the failure, the cheaper tier is probably right — change the
recommendation.
