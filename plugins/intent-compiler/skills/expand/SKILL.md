---
name: expand
description: The mirror of compile — read a compressed prompt back and itemize the frames its terms import, separating what the model will assume as core from what it will merely lean toward, flagging terms whose sense is not pinned, and naming the entailments the intent never asked for. Shows the bill before you pay it.
when_to_use: Use on a prompt that is already compressed — one compile produced, one you wrote, a skill or agent description, a CLAUDE.md rule — when you want to see what it actually commits you to. Required by compile at commitment 3. Also useful on a prompt whose output keeps containing work nobody asked for. Never executes the prompt.
argument-hint: "[compressed prompt, term, or path to a file] [--intent=\"what you actually wanted\"]"
disable-model-invocation: true
model: sonnet
effort: medium
allowed-tools:
  - Read
  - Grep
  - Glob
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Frame expander

Expand the compressed prompt in `$ARGUMENTS` — or the file it names, or the
compiled block most recently produced in this conversation — into the frames
it imports. This is `compile` run backwards: `compile` chooses what to buy,
`expand` reads the receipt.

**You are not doing the task, and you are not improving the prompt.** Do not
execute it, rewrite it, or produce the work it asks for. You itemize; the user
decides. Suggested trim lines are the one exception, and they go in their own
section as text to add, never as a rewritten prompt.

Load `${CLAUDE_PLUGIN_ROOT}/reference/polysemous.md` — here it is always
relevant, since finding unpinned senses is most of the job. Load
`${CLAUDE_PLUGIN_ROOT}/reference/compression-core.md` only when you need the
split or the mode names. Read
`${CLAUDE_PROJECT_DIR}/.claude/intent-lexicon.jsonl` when it exists: a `pact`
entry means a term is local and its definition is the expansion — do not
expand a local term against a public frame it was never meant to evoke.

## 1. Find the terms

Scan the prompt for load-bearing terms: catalogued pattern names, standards,
named algorithms, architectural vocabulary, role framings ("act as a…"), and
anything from `polysemous.md`. Ignore ordinary words — a term is load-bearing
when removing it would leave the prompt underspecified.

Note which terms are anchors doing work and which are decoration. Decoration
is worth reporting: a term that imports a frame nobody needs is pure risk with
no payload.

## 2. Expand each term

For each, separate what the model treats as given from what it merely leans
toward. The distinction is the whole value of this skill: **core elements will
appear in the output whether or not you asked for them; non-core elements
appear often enough to surprise you.**

- **Core** — what the term means. Omitting one would make it the wrong term.
- **Non-core** — what usually travels with it: default implementations,
  companion patterns, conventional file layouts, the stack it is usually
  paired with.
- **Competing frames** — other senses the term carries. For each, say whether
  something in the prompt pins the intended sense, and quote the words that do
  it. A sense left unpinned is a `misread` waiting to happen, and is a
  stronger finding than any leak.

## 3. Compare against the intent

When `--intent=` is given, or the conversation states what the user wanted,
diff the expansion against it and sort every element into:

- **Asked for** — the payload. The compression is working.
- **Silent extras** — imported, never requested, not obviously wrong. This is
  the entailment leak, and it is what makes compressed prompts produce more
  than you wanted.
- **Contradicted** — the frame implies something the intent rules out. The
  most serious finding: the term is fighting the instructions, and which one
  wins is not predictable.
- **Missing** — wanted, not supplied by any term, not stated explicitly. The
  prompt is underspecified and no frame will cover it.

Without an intent to compare against, report the expansion and the unpinned
senses only. Do not invent an intent to diff against — say that the section
is unavailable and why.

## 4. Output

```
Terms found: N load-bearing, N decorative

## <term>  [pinned | UNPINNED]
Frame: <one line — the scene this term evokes>
Core (assumed):
- <element>
Non-core (likely):
- <element>
Competing senses:
- <other sense> — pinned by "<quoted words from the prompt>" | NOT PINNED

<repeat per term>

## Bill
Asked for: <count> — <one line>
Silent extras:
- <element> — <what it would look like in the output>
Contradicted:
- <element> — <the instruction it fights, quoted>
Missing:
- <element> — <what nothing in the prompt supplies>

## Verdict
<one paragraph: what this prompt actually commits you to, beyond what it says>

Suggested trim (text to add, not a rewrite):
- <line>
```

Sections `Asked for`, `Silent extras`, `Contradicted` and `Missing` require an
intent; when none is available, replace the whole **Bill** with one line
saying so. **Verdict** is always present.

## Rules

- **Report what the model will do, not what the pattern's canonical definition
  says.** These differ, and the difference is the finding. If `event sourcing`
  in practice drags CQRS along whatever the catalogue says, that belongs under
  non-core.
- An **UNPINNED** term outranks every leak in the output. A leak costs you
  extra work; a misread costs you the whole task.
- Never widen the prompt. Trims subtract; if something is missing, it goes
  under **Missing** for the user to add.
- Do not score compressibility here — that is `compile`'s job, and running the
  rubric on an existing prompt invites rewriting it.
