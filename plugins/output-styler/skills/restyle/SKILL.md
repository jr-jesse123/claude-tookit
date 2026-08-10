---
name: restyle
description: Rewrite the previous response — or a text/file the user points at — in one or more named writing styles (ste, plain, bluf, eli5, docs, visual) so the user can compare variants side by side and mature a preferred output style per project. Use when the user asks to restyle, reformulate, simplify, summarize differently, or visualize an explanation they just received; `--help` describes each style, with samples, so the user can choose before restyling anything.
argument-hint: "[bluf|plain|docs|ste|eli5|visual|all] [--score] [--help] [file|text]"
allowed-tools: Read, Glob, Grep, Edit, Write
---

# Restyle

Rewrite one piece of content in one or more named styles. The content's *facts*
are frozen; only the *form* changes. The point is comparison: the user is
experimenting to find the best output style for each kind of project, so every
variant must be a faithful rendering of the same substance — otherwise the
comparison is meaningless.

Write every variant in the language the conversation is happening in. The
styles are language-independent; where a standard is English-specific (STE's
dictionary), apply its rules' spirit, as the style file explains.

## 0. `--help` short-circuits everything

`--help` (or `-h`, or `help` as the only word) anywhere in `$ARGUMENTS` → read
`${CLAUDE_SKILL_DIR}/help.md`, present it in the conversation's language (translate prose,
but keep style names, aliases, flags, and code/commands verbatim), and stop.
Nothing is restyled, no target is resolved, no style file is loaded — even when styles
were named in the same invocation. Close by offering the invocation the user seems to be heading for.

## 1. Resolve the target

Decide what to restyle, in this order:

1. `$ARGUMENTS` contains a path that exists → Read that file.
2. `$ARGUMENTS` contains quoted text of more than a few words → that text.
3. Otherwise → the last substantive assistant response in this conversation:
   the most recent message with real content (an explanation, report, plan,
   answer), skipping tool-status chatter and this invocation itself.

Open the report by naming the target in one line ("Restyling: *<first words of
the target>…*") so a wrong guess is caught immediately.

**The target stays pinned across invocations.** When the user calls the skill
again to try more styles, restyle the *original* content again — not the
previous restyle — unless they explicitly point at a restyled variant ("agora o
eli5 em cima desse bluf").

## 2. Resolve the styles

Styles come from `$ARGUMENTS`, separated by spaces or commas, case-insensitive.

| Style | Aliases | One line | Anchored in |
| --- | --- | --- | --- |
| `bluf` | `exec`, `minto` | Answer first, arguments grouped below, data last | BLUF (US Army), Minto Pyramid |
| `plain` | `simple`, `iso` | Plain language: reader-first, everyday words, findable | ISO 24495-1, PlainLanguage.gov |
| `docs` | `devdocs`, `google` | Developer documentation: second person, present tense, task-oriented | Google / Microsoft style guides |
| `ste` | `technical`, `controlled` | Controlled technical writing: short, active, one meaning per word | ASD-STE100 |
| `eli5` | `thing-explainer` | Only the most common words, one sustained analogy | Simple-vocabulary writing |
| `visual` | `diagram`, `mermaid` | The content becomes a Mermaid diagram or table, prose only where a picture can't reach | Mermaid, structured tables |

- `all` (or `todos`) → every style, in the table's order.
- Unknown name → show this table and ask; do not guess.
- No style given → show this table and ask which one(s).
- Whenever you show this table, add one line: `--help` gives the full catalog —
  when each style pays off, what it costs, and the same text rendered in all
  six.
- `--score` anywhere in the arguments → append readability metrics (step 5).

## 3. Load only the selected styles

Each style's rules and a before/after example live in
`${CLAUDE_SKILL_DIR}/styles/<style>.md`. **Read only the files for the styles
selected this invocation** — never the whole folder. On a repeat invocation in
the same session, don't re-read files already loaded.

## 4. Rewrite

Invariants that hold for every style:

- **Facts are frozen.** Same claims, same numbers, same conclusions, same
  recommendations. Add nothing the original didn't say; restyling is not a
  second opinion.
- **Caveats don't vanish silently.** When a style forces cuts (bluf, eli5,
  visual often do), end that variant with one line — *Omitted: …* — naming
  what was dropped. An executive summary that hides the risks is a bug.
- **Code blocks, commands, and identifiers pass through verbatim.** Styles
  reshape the prose around them.
- **Length is an outcome, not a goal.** A variant may legitimately grow (ste,
  docs) or shrink (bluf, eli5); never pad or truncate to hit a size.

### Report format

One style → deliver the rewrite directly, no scaffolding.

Multiple styles → one `## <style>` section per style, in the requested order
(catalog order for `all`), each a complete standalone rendering. Close with a
short **Comparison** block: one line per style stating what it bought and what
it cost *for this specific content* ("bluf: decision readable in 5 lines, but
the two edge cases moved below the fold") — concrete observations, not
definitions of the styles. This block is what matures the user's per-project
preference; make it earn its lines.

## 5. `--score`

When `--score` is present, append one metrics table covering the original and
every variant:

| Variant | Words | Sentences | Avg words/sentence | Words > 6 chars |
| --- | --- | --- | --- | --- |

Count from the prose only (skip code blocks and diagram source). If the text
is in English, add a Flesch Reading Ease column (60–70 ≈ comfortable adult
reading); for other languages omit it — the formula is English-calibrated —
and let sentence length and long-word share carry the comparison.

## 6. Maturing a project style

When the user declares a winner ("gostei do bluf", "visual ganhou para esse
tipo de projeto"), offer — never do it unasked — the mechanism that matches
the winner:

- **The winner ships as a native output style in this plugin** (today:
  `visual`) → offer to make it the project's output style: set
  `"outputStyle": "Visual"` in the project's `.claude/settings.json` (the
  user can also do it via `/config` → *Output style*). This changes the
  register at the system-prompt level and persists across sessions — the
  mechanism Claude Code recommends for persistent tone. Mention the
  difference: the output style makes Claude *speak* that way natively, while
  this skill keeps existing for on-demand comparison.
- **Any other winner** → offer to record the preference in the project's
  `CLAUDE.md` under an `## Output style` heading: the chosen style, one line
  on when it applies, and the date. A style that keeps winning here is the
  signal it has earned its own native output style port.

Either way, use Edit on the existing file or Write to create it, only after
explicit confirmation. That closes the experiment loop: the next session
picks the preference up automatically.

## What not to do

- No new analysis, opinions, or recommendations inside a variant.
- No restyling of code semantics — prose only.
- No producing styles beyond what was asked; `all` is an explicit choice.
- No stacking restyles by accident: the pinned target is the original.
- No verdict on which style "won" — observations in the Comparison block,
  decision with the user.
