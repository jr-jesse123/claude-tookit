---
name: compile
description: Turn a raw intent into a compiled prompt — compressing the mechanism onto canonical terms the model already holds, carrying project facts and the acceptance criterion through verbatim, and naming what the compression removed. Scores each candidate term for canonicity, frame precision, frame fit and shared ground, then gates the result on what a wrong expansion would cost.
when_to_use: Use before handing a substantial intent to a model — an implementation task, an architecture request, a review brief, an agent or subagent prompt — when the intent is still in your own words and you want it anchored on terms that carry their meaning. Never execute the intent itself. To audit an already-compressed prompt for unwanted entailments, use expand instead.
argument-hint: "[raw intent] [--target=haiku|sonnet|opus] [--commitment=0..3]"
disable-model-invocation: true
model: sonnet
effort: medium
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git diff --stat *)
  - Bash(git log --oneline *)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Intent compiler

Compile the intent in `$ARGUMENTS` into a prompt whose mechanism rides on
terms the executing model already holds. If `$ARGUMENTS` is empty, compile the
most recent intent the user described in the conversation.

**You are not doing the task.** Do not implement, edit, or execute the intent,
and do not run the prompt you produce. Inspect the repository only to settle
whether a term is project-local or public, and only with the read-only tools
above.

The split, the rubric, the commitment gate, the mode table and the lexicon
thresholds are shared plugin material in
`${CLAUDE_PLUGIN_ROOT}/reference/compression-core.md`. This file owns only the
procedure and the output.

## 1. Load inputs

Read, in this order:

- `${CLAUDE_PLUGIN_ROOT}/reference/compression-core.md` — always; it is the
  rubric you apply in step 4.
- `${CLAUDE_PLUGIN_ROOT}/reference/polysemous.md` — **only when a candidate
  term is not obviously safe** (progressive disclosure). A prompt anchored
  entirely on `RFC 7807` and `exponential backoff` does not need the
  overloaded-terms catalogue in context.
- `${CLAUDE_PROJECT_DIR}/.claude/intent-lexicon.jsonl` if it exists. Absent on
  a fresh project; that is normal and you proceed on the rubric alone.
  Interpret it with the core's **Lexicon thresholds**; the schema lives in
  `${CLAUDE_PLUGIN_ROOT}/reference/lexicon.md`.
- `CLAUDE.md` and any project glossary, when the intent uses vocabulary you
  cannot place. A term defined there is shared ground *within this project* —
  score dimension 4 accordingly, and prefer a pact that cites it.

Resolve two parameters:

- **Target** — the model that will run the compiled prompt, from `--target=`.
  Default: assume the calling session's model. When the target is a tier below
  the model running this skill, subtract 1 from canonicity per the core.
- **Commitment** — from `--commitment=`, or inferred from the intent using the
  core's level table. When you infer it, say so and say from what; when the
  inference is between two levels, take the higher one.

## 2. Split the intent

Cut the raw intent into **reducible** and **irreducible** per the core's split
table. Do this before scoring anything — it is the step that decides what is
even a candidate, and skipping it is how acceptance criteria get paraphrased.

Two checks before moving on:

- **Find the oracle.** Locate the sentence that says what *done* looks like.
  If the intent does not contain one, that is the single most valuable thing
  you can report: say so, propose one, and put it in the output as irreducible.
  A compiled prompt with no oracle is a faster way to get the wrong thing.
- **Find the negations.** Anything the user said not to do is irreducible by
  construction — no frame is defined by what it excludes.

## 3. Nominate terms

For each reducible piece, name the candidate term — the catalogued concept
whose frame covers it. Zero, one, or several per piece.

Then apply the **implication test** to each candidate, which is the cheapest
canonicity check available: state, in bullets, what the term implies. Do it
from your own knowledge, not by asking the user. Compare against the intent:

- Elements you want and the term supplies → the compression's payload.
- Elements the term supplies that the intent never asked for → **candidate
  trim lines**, and the leak the lexicon measures later.
- Elements the intent wants that the term does not supply → these stay
  explicit; a term never covers the whole piece by itself.

If the implication list comes out different when you consider the term twice,
its intension is not fixed. Score canonicity ≤ 1 and say why.

## 4. Score and choose a mode

Apply `compression-core.md` in order:

1. **Four dimensions**, 0–3, one line of justification each, with the target
   adjustment applied to canonicity.
2. **Lexicon thresholds** — when a matching term has three or more entries,
   the log overrides the score. Say the log drove it.
3. **Decision rule** → mode, first match wins.
4. **Commitment gate** → the gate can only make the mode more explicit, never
   less. A Pure term at commitment 2 becomes Trimmed.

Score per term. One intent commonly produces a pure anchor, a trimmed anchor
and a pact in the same compiled prompt.

## 5. Write the compiled prompt

Assemble it in this order, which is also the order the executing model reads
it in:

1. The anchored mechanism — terms, with their trims immediately attached. A
   trim that drifts away from its term stops being read as a constraint on it.
2. The irreducible facts and constraints, verbatim.
3. The acceptance criterion, last and unambiguous.

Rules for the prompt itself:

- **Never translate an anchor.** Write the surrounding text in the user's
  language; leave catalogued terms in the language of their catalogue, per the
  core. A translated anchor evokes nothing.
- **Never compress below the point where you could reconstruct the intent.**
  If you cannot read the compiled prompt back and recover what the user meant,
  it is lossy in the direction that matters.
- **Do not add scope.** Compression removes words, never adds requirements. If
  the frame implies work the user did not ask for and you think they want it,
  that is a question in the Risk section, not a line in the prompt.
- Keep the user's own phrasing wherever it is already irreducible. Rewriting a
  precise sentence into a different precise sentence buys nothing and risks
  meaning.

## 6. Output

Return exactly this structure and nothing else. Every angle-bracket field is
required; omit an optional section only when its condition does not hold.

```
Mode: <the dominant term's mode; add "(mixed)" when the others differ>
Compressibility: canonicity N, precision N, fit N, ground N — total N/12
Commitment: N — <what a wrong expansion would cost here>
Target: <model the prompt is compiled for, and whether it was given or assumed>

--- compiled ---
<the prompt, ready to paste, nothing else inside these markers>
--- end ---

Anchored terms:
- <term> → <the frame it imports, one line> [mode, total N/12]

Trimmed:
- <frame element> — <why it does not apply here>

Irreducible (carried verbatim):
- <fact, constraint, or the acceptance criterion, and which it is>

Dropped:
- <what left the raw intent, and why it carried no information>

Risk:
- <the most likely wrong expansion, and the signal in the output that would reveal it>

Lexicon (run after the task, with the real outcomes filled in — or invoke
/intent-compiler:log-lexicon to have them filled from the session):
python3 "${CLAUDE_PLUGIN_ROOT}/skills/log-lexicon/log-lexicon.py" \
  --term "<slug>" --mode <mode> --note "scored N/12" \
  --adhered <?> --leak <?> --misread <?> --corrections <?>
```

The three header lines describe the **dominant term** — the one carrying the
most of the intent. Per-term scores and modes live in **Anchored terms**; never
average scores across terms, which produces a number describing no decision you
actually made.

Emit the lexicon command every time, one per anchored term, with `term`,
`mode` and the score in `--note` already filled and the outcome flags left as
`<?>` placeholders — those are only knowable after the prompt runs. Reuse an
existing slug from the lexicon whenever one fits; near-duplicate slugs are what
stop a term from ever reaching the three-entry threshold. **Do not run the
command and do not write the lexicon** — `Write` is disallowed here by design,
this skill runs before the task, and recording belongs to `log-lexicon` after.

Conditional sections, each included **only** when its condition holds:

- **Expansion check** — commitment is 3. State that the compiled prompt should
  be audited before use, and close with:
  `Run /intent-compiler:expand on the compiled block above before using it.`
- **New pact** — the compilation introduced or relied on a local term with no
  lexicon entry. Give the one-line definition and the `--kind pact` logging
  command so the next session starts with it.
- **Missing oracle** — the raw intent contained no acceptance criterion. State
  it plainly and give the one you proposed; this outranks every other finding
  in the output.
- **Routing note** — the compilation materially changed how hard the task
  looks (ambiguity was the difficulty, and anchoring removed it). Say so in
  one line and point at `/model-router:choose-model`, which scores the
  compiled intent rather than the raw one.

## Rules for the output

- The **Dropped** section is not optional and may not be empty when anything
  was removed. A compression that hides its losses cannot be audited.
- The **Risk** section must name a *failure and its signal*, not a feeling.
  "The model may treat `projection` as a SQL column list, which you would see
  as a query instead of a read-model class" is useful; "this term is somewhat
  ambiguous" is not. If you cannot name the failure, you do not know the term
  well enough to anchor on it — score precision down and re-run step 4.
- Never claim a token saving you have not counted. Compression that is really
  about adherence should say adherence.
- Do not begin the underlying task, and do not run the compiled prompt.
