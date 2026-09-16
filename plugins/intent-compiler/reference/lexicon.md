# Project lexicon

`polysemous.md` is a prior about terms in general; this log is evidence about
terms **in your project, with your models**. It is the only thing in the
plugin that can prove a term is or is not in the codebook you actually ship
against, so it outranks every shipped prior (`compression-core.md` →
**Lexicon thresholds**).

**The lexicon lives at `${CLAUDE_PROJECT_DIR}/.claude/intent-lexicon.jsonl`** —
in the project, not inside the plugin. A plugin's directory is replaced on
every update and is documented as ephemeral, so a lexicon kept there would be
wiped on the first upgrade. The project path also puts the vocabulary next to
the codebase it describes, which is the scope that matters: a bounded context
is not a bounded context in the next repository.

This file is a Ubiquitous Language artifact that a machine can read. That is
the point of the `pact` entries: the definitions your team agreed on, written
once, reused verbatim instead of re-derived every session.

## Two kinds of entry

One JSON object per line, discriminated by `kind`.

### `usage` — how an anchor actually behaved

```json
{"kind":"usage","date":"2026-09-16","term":"event-sourcing","mode":"trimmed","adhered":true,"leak":1,"misread":false,"corrections":0,"note":"scored 11/12; leaked snapshots despite the trim"}
```

| Field | Meaning |
| --- | --- |
| `date` | ISO date the compiled prompt ran |
| `term` | Lowercase slug of the anchor (`event-sourcing`, `circuit-breaker`) — this is the join key |
| `mode` | `pure`, `trimmed`, `pact`, or `expanded` — what `compile` emitted |
| `adhered` | Whether the output matched the intent the compression stood for |
| `leak` | Count of frame elements the model produced that the intent never asked for. **The number that matters** — it measures the cost of compression, not its benefit |
| `misread` | `true` when the model expanded to the wrong frame entirely (`saga` as redux-saga, `projection` as SELECT) — a different failure from leaking, and a far worse one |
| `corrections` | User turns spent correcting the result |
| `tokens_in` / `tokens_out` | Optional, from `/cost`. These are how you find out whether the compression paid for itself at all |
| `note` | Free text; record the compressibility score and whether it matched |

### `pact` — a local term, defined once

```json
{"kind":"pact","date":"2026-09-16","term":"apolice-ativa","definition":"policy with status=VIGENTE and no open cancellation request; excludes grace-period policies","note":"agreed with the domain expert"}
```

| Field | Meaning |
| --- | --- |
| `term` | Slug of your local term |
| `definition` | One line, the intension. This is what gets pasted into future prompts verbatim |
| `note` | Where the definition came from — a person, a spec, a meeting |

A term with a `pact` entry is always emitted in mode `pact`: the definition
once, then the short form. Re-deriving an agreed definition is the failure
this file exists to prevent.

## Recording an entry

`compile` and `expand` **never write this file.** They run before the task,
and every outcome field (`adhered`, `leak`, `misread`) is only knowable after
it ends — an entry written at compile time cannot be honest. `compile` reads
the lexicon when present and emits a ready-to-run logging command with the
outcome flags left as placeholders.

In order of preference:

1. **`/intent-compiler:log-lexicon`** — invoke when the task finishes. It
   fills the outcomes from what happened in the session, shows you the entry,
   and appends via the bundled script. The script is the plugin's only write
   path: append-only, fixed to `.claude/intent-lexicon.jsonl`, validating
   every field before writing — which is why it can be allowlisted on its own
   without granting a blanket `Write` permission.
2. **Run the emitted command yourself**, filling in the placeholders.
3. **Manual append**, when no plugin is available:

```sh
mkdir -p .claude
echo '{"kind":"usage","date":"2026-09-16",...}' >> .claude/intent-lexicon.jsonl
```

## Thresholds

Evaluated per `term`. Restated from `compression-core.md` so this file stands
alone; the core is authoritative if they ever drift.

- **≥ 3 entries with `leak > 0`** → never emit this term as `pure`; Trimmed is
  its floor, reusing the trim lines that worked.
- **≥ 3 with `misread: true`** → the term is not in your models' codebook.
  Canonicity drops to 0: Expanded, or Pact if the word is worth keeping.
- **≥ 3 with `adhered: true`, `leak: 0`, `corrections: 0` at `trimmed`** → the
  trim is inert; try `pure` and say the log drove it.
- Fewer than three, or mixed → noise.

Promote what the log proves. When a term accumulates `misread` entries, it
belongs in `polysemous.md` as a project-local note; when a `pact` definition
stops changing across three tasks, it belongs in the team's glossary and in
`CLAUDE.md`, where it costs nothing to load and stops being rediscovered.
