---
name: log-lexicon
description: Append an honest entry to the project's intent lexicon after a compiled prompt has run — how the anchor actually behaved, or the agreed definition of a local term. Companion to the compile and expand skills, which run before the task and never write.
when_to_use: Use at the end of a task whose prompt was produced by the compile skill, whenever an anchored term visibly misbehaved, or when the user fixes the meaning of a project-local term and wants it recorded. Never use before or during the task — the outcome fields are only knowable after it ends.
argument-hint: "[optional outcome notes]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python3 *log-lexicon.py*)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Lexicon logger

Append one entry to `${CLAUDE_PROJECT_DIR}/.claude/intent-lexicon.jsonl`
describing how an anchored term actually behaved, or fixing a local term's
definition. The schema and the thresholds that consume this log live in the
plugin's `reference/lexicon.md` — this skill only records, it never compiles.

**The one rule: outcomes come from evidence, not optimism.** Every field must
be traceable to something that happened in this session. If you cannot
determine a field, ask the user or omit it (`--tokens-in` / `--tokens-out` are
the only omittable ones) — never guess. A lexicon that flatters your prompts
will talk you into compressions that do not work.

## 1. Decide the kind

| Kind | When |
| --- | --- |
| `usage` | A compiled prompt ran and you can see how its anchors behaved. One entry **per anchored term**, not per task — a prompt anchored on three terms teaches you three things. |
| `pact` | The user fixed the meaning of a project-local term, in this session or in a document you can cite. One entry per term; a changed definition is a new entry, and the newest wins. |

## 2. Gather the fields

For a `usage` entry, from the current session:

| Field | Where it comes from |
| --- | --- |
| `term` | Read the existing lexicon first and **reuse a slug** when one fits — near-duplicate slugs are what stop a term from ever reaching the three-entry threshold. If `compile` ran, its lexicon command names the slug it chose. |
| `mode` | What `compile` actually emitted: `pure`, `trimmed`, `pact`, `expanded`. If the prompt was hand-written, classify it by shape. |
| `adhered` | `true` only if the output matched the intent the compression stood for. Output that was *fine but not what was asked* is `false`. |
| `leak` | **Count the frame elements the model produced that nobody asked for** — the companion pattern it added, the extra file it wrote, the abstraction it introduced because the term implies one. This is the number the thresholds turn on, so count it rather than estimating. Zero is a real and common answer. |
| `misread` | `true` only when the model expanded to the *wrong frame* — `saga` as redux-saga, `projection` as a column list, `agent` as a daemon. Different from leaking, and worse. |
| `corrections` | User turns that corrected the work. Clarifications and scope additions are not corrections. |
| `tokens_in` / `tokens_out` | From `/cost` or the harness's usage display, when available. Omit otherwise — never estimate token counts. |
| `note` | The compressibility score from `compile` (`"scored N/12"`) and whether it matched reality. `$ARGUMENTS`, when provided, goes here too. |

For a `pact` entry you need only `term`, `definition` — one line fixing the
intension — and a `note` saying where the definition came from. Quote the
user's own words where they gave them; a pact you paraphrased is a pact they
did not agree to.

## 3. Confirm before writing

Show the user the assembled entry as a single line and ask them to confirm it
is honest. For `leak`, show *what* you counted, not just the number — that is
the field most easily inflated by hindsight and most easily zeroed by
politeness. Adjust anything they push back on.

## 4. Append via the script

Run the bundled script — the only write path, validating every field first:

```sh
python3 "${CLAUDE_SKILL_DIR}/log-lexicon.py" \
  --term "<slug>" --mode <pure|trimmed|pact|expanded> \
  --adhered <true|false> --leak <n> --misread <true|false> \
  --corrections <n> --note "<free text>"
```

```sh
python3 "${CLAUDE_SKILL_DIR}/log-lexicon.py" --kind pact \
  --term "<slug>" --definition "<one line>" --note "<where it came from>"
```

The script is append-only against the fixed path
`${CLAUDE_PROJECT_DIR}/.claude/intent-lexicon.jsonl` and exits non-zero
without writing if any field is invalid. Do not edit the lexicon by any other
means — if an existing entry is wrong, tell the user and let them fix it.

## Rules

- Never run the script speculatively or before the prompt's task ends.
- One `usage` entry per anchored term per task. A term that leaked and was
  then corrected is **one** entry with `leak > 0` and `corrections > 0`, not
  two.
- `adhered: true` with `leak > 0` is a normal and useful entry — it means the
  compression worked and cost something. Do not round it to either extreme.
- Do not summarize the thresholds back to the user or recommend changing how
  a term is compressed; that is `compile`'s job on its next run.
