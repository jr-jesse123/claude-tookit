---
name: log-calibration
description: Append an honest entry to the project's model-calibration log after a task finishes, filling the outcome fields from what actually happened in the session. Companion to choose-model, which advises before the task and never writes.
when_to_use: Use at the end of a task whose model or effort was chosen via the choose-model advisor, or whenever the user asks to log a calibration entry. Never use before or during the task — the outcome fields are only knowable after it ends.
argument-hint: "[optional outcome notes]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python3 *log-calibration.py*)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Calibration logger

Append one entry to `${CLAUDE_PROJECT_DIR}/.claude/model-calibration.jsonl`
describing how the task that just finished actually went. The schema and the
thresholds that consume this log live in the choose-model skill's
`calibration.md` — this skill only records, it never routes.

**The one rule: outcomes come from evidence, not optimism.** Every field you
fill must be traceable to something that happened in this session. If you
cannot determine a field from the conversation, ask the user or omit it
(`--minutes` is the only omittable outcome) — never guess.

## 1. Gather the fields

From the current session, determine:

| Field | Where it comes from |
| --- | --- |
| `category` | Read the existing log first (`.claude/model-calibration.jsonl`) and **reuse a slug** when one fits — inventing near-duplicate slugs is what stops categories from ever reaching the three-entry threshold. If the advisor ran, its calibration command names the slug it chose. |
| `provider` | `anthropic` (default) or `openai` — the provider of the model the task ran on. |
| `model` / `effort` | What the task **actually started with**, not what was recommended. Omit `effort` for models that take none (haiku); each provider has its own level names — log the literal level used. |
| `escalated` | `true` only if a stronger model or higher effort was actually needed mid-task (the user switched, or the work had to be redone on a stronger tier). |
| `corrections` | Count the user turns that corrected your work — wrong approach, wrong output, missed requirement. Clarifications and scope additions are not corrections. |
| `minutes` | Wall-clock duration if it is evident or the user tells you. Omit otherwise. |
| `tokens_in` / `tokens_out` | From `/cost` or the harness's usage display, if available. Omit otherwise — never estimate token counts. |
| `tests` | `pass` / `fail` from the last relevant test run in the session; `none` if nothing was run. |
| `rework` | `true` only if the result required architectural rework afterward. |
| `note` | Include the advisor's score (`"scored N/15"`) if a choose-model recommendation exists in the conversation, and whether the recommendation matched reality. `$ARGUMENTS`, if provided, goes here too. |

## 2. Confirm before writing

Show the user the assembled entry as a single line and ask them to confirm it
is honest — the log drives future routing, so a flattering entry is worse than
no entry. Adjust anything they push back on.

## 3. Append via the script

Run the bundled script — this is the only write path, and it validates every
field before touching the file:

```sh
python3 "${CLAUDE_SKILL_DIR}/log-calibration.py" \
  --provider <anthropic|openai> --category "<slug>" \
  --model <alias> --effort <level> \
  --escalated <true|false> --corrections <n> --minutes <n> \
  --tests <pass|fail|none> --rework <true|false> \
  --note "<free text>"
```

The script is append-only against the fixed path
`${CLAUDE_PROJECT_DIR}/.claude/model-calibration.jsonl`; it exits non-zero
without writing if any field is invalid. Do not edit the log by any other
means — if an existing entry is wrong, tell the user and let them fix it.

## Rules

- Never run this skill's script speculatively or before the task ends.
- One entry per task. If the task escalated mid-way, that is **one** entry with
  `escalated: true` under the model it *started* with — not two entries.
- Do not summarize the policy's thresholds back to the user or recommend
  routing changes here; that is the choose-model advisor's job on its next run.
