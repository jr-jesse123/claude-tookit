# Calibration log

Benchmarks and provider policies are priors; your own completed tasks are
evidence. This file owns the log's schema and recording flow — it is shared by
every provider policy, by the routing skills (`choose-model`,
`plan-execution`), and by the `log-calibration` skill. It is also the **only
cross-provider comparator this plugin trusts**: public benchmarks measure
different suites with different shapes, but the log measures your tasks.

**The log lives at `${CLAUDE_PROJECT_DIR}/.claude/model-calibration.jsonl`** —
in the project, not inside the plugin. A plugin's own directory is replaced on
every update and is documented as ephemeral, so a log kept there would be
silently wiped the first time the plugin is upgraded. The project path also
keeps the history next to the codebase whose routing it describes, which is
the scope that actually matters: routing that fits an Oracle-backed service
will not fit a static site.

## Recording an entry

The routing advisors (`choose-model`, `plan-execution`) **never write this
file.** They run before the task, and every outcome field (`escalated`,
`corrections`, `tests`, …) is only knowable after the task ends — so an entry
written at recommendation time cannot be honest. The advisors read the log
when present and emit ready-to-run logging commands (one per task, or one per
part of a decomposed plan) with the outcome flags left as placeholders.

In order of preference:

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
echo '{"date":"2026-08-05",...}' >> .claude/model-calibration.jsonl
```

## Schema

One JSON object per line. See `calibration.example.jsonl` next to this file
for a populated sample.

```json
{"date":"2026-08-05","provider":"anthropic","category":"oracle-isolation","model":"opus","effort":"high","escalated":false,"corrections":2,"minutes":24,"tests":"pass","rework":false,"note":"scored 11/15, matched"}
```

| Field | Meaning |
| --- | --- |
| `date` | ISO date the task ran |
| `provider` | `anthropic` or `openai`. Entries written before this field existed are `anthropic`. |
| `category` | Short task-category slug, reused across entries — this is the join key |
| `model` / `effort` | What was actually started with, not what was recommended. `effort` is `null` where the model takes none (haiku; OpenAI at `none`, log the literal level instead). |
| `escalated` | Whether a stronger model or effort was needed mid-task |
| `corrections` | Number of user corrections during the task |
| `minutes` | Wall-clock duration |
| `tokens_in` / `tokens_out` | Optional token usage (e.g. from `/cost`). `tokens_out` includes thinking. These turn the policies' token-economics priors into measured per-category numbers — the blended-cost tie-break (`routing-core.md` → tie-break rule 2) prefers them over any prior. `null` when unknown. |
| `tests` | `pass`, `fail`, or `none` |
| `rework` | Whether the result required architectural rework afterward |
| `note` | Free text; recording the advisor's score and whether it matched is the most useful thing to put here |

## Thresholds

Evaluated per `category`, over entries whose `provider` is currently accepted:

- **Three or more entries with `escalated: true`** at a tier → the category is
  routed too cheaply; the advisor recommends one tier up and says the log
  drove it.
- **Three or more with `escalated: false` and `corrections: 0`** at the
  frontier tier or above → routed too expensively; one tier down.
- Fewer than three, or mixed → noise, not signal.

When entries for the same category exist under more than one provider, they
double as the cross-provider tie-break (`routing-core.md` → tie-break
rule 1): the provider whose
candidate has clean entries for the category wins over one with none.

Revise the provider policies' routing tables when a category accumulates
entries pointing the same way. One surprising task is noise; five in a
category are not.
