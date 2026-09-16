# Compression core

Shared by the `compile` and `expand` skills: the reducible/irreducible split,
the compressibility rubric, the commitment gate, the mode table, and the
lexicon thresholds. **This file names no specific terms** — the catalogue of
terms that misbehave lives in `polysemous.md`, and measured evidence about
your own terms lives in the project lexicon (`lexicon.md`). The skills own
their procedures and output formats; when the *scoring* changes, change it
here only.

## Why this works at all

A term is short only because the decoder already contains its expansion. This
is Kolmogorov compression against a shared prior: `event sourcing` costs three
tokens because the model's weights hold the append-only log, the immutable
facts, the replay, the projections. A phrase you invented costs its own length
and expands to nothing — or worse, silently expands to the nearest frame the
model *does* hold.

So compressibility is never a property of the words. It is a property of the
pair (term, decoder). Everything below scores that pair.

Two consequences the rubric depends on:

- **The compiler's codebook must not exceed the executor's.** A term this
  session knows but the executing model does not is a silent miscompression.
  When the target model is weaker than the one running this skill, drop
  canonicity by one (see the rubric). When it is stronger, the anchors are
  safe by construction.
- **The anchor keeps the language of its catalogue.** `event sourcing` is
  dense; `fonte de eventos` is a paraphrase wearing a term's clothes — the
  catalogue, the papers and the training mass are in English, so the
  translation evokes no frame. Write the intent in whatever language you
  think in and leave the anchors untranslated. A mixed-language prompt costs
  nothing; a translated anchor costs the whole frame.

## The split: what may be compressed at all

Before scoring anything, cut the raw intent in two. Only one half is even a
candidate.

| | Contents | Treatment |
| --- | --- | --- |
| **Reducible** | Mechanism, architectural pattern, process, convention, code style, role framing — anything the model already knows under a name | Score it, compress it |
| **Irreducible** | Repository facts (paths, symbols, versions, the actual error text), business rules, external constraints, quantities and thresholds, explicit negations, **and the acceptance criterion** | Carry through verbatim, never paraphrase |

**Compress the *how*; never the *done*.** A wrong decompression of mechanism
shows up in the diff and costs one round. A wrong decompression of the
acceptance criterion is undetectable — you accept the wrong work and the
error leaves the session with you. The oracle is irreducible even when a
perfectly good term exists for it.

Explicit negations are irreducible for a structural reason: a frame is a set
of things a term *includes*. There is no term whose meaning is the absence of
something, so "no CQRS" can only be said the long way.

## Compressibility: four dimensions, 0–3 each

Score only these, against the term you are considering. Each is one line of
justification in the output. Higher is more compressible.

| # | Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- | --- |
| 1 | **Canonicity** — is the intension fixed anywhere? | Invented here, or no term exists | Folklore: used, never defined | Widely used, informally stable | Catalogued (GoF, PoEAA/Fowler, RFC, ISO, W3C, POSIX, a named paper) |
| 2 | **Frame precision** — how many scenes does it evoke? | Three or more strong senses | Two strong senses | One dominant sense, minor variants | One sense, no serious competitor |
| 3 | **Frame fit** — how much of what it imports do you want? | Mostly wrong for this task | About half | Most of it, a few exclusions | All of it |
| 4 | **Shared ground** — whose vocabulary is it? | Project-local only | Org- or industry-local | Public within a niche | Public and common |

Total is **0–12**. Subtract 1 from dimension 1 when the target model is a tier
below the one running this skill (`--target=`); a term the executor may not
hold is not canonical *for this job*, whatever the catalogue says.

## Commitment: the gate, not a fifth score

Commitment is what a wrong decompression costs. It is deliberately **not
summed** with the four dimensions, because it does not measure the same thing:
compressibility says which mode is *available*, commitment says which modes
are *allowed*. Adding them would let a well-catalogued term buy its way past a
production migration, which is exactly backwards.

| Level | Meaning |
| --- | --- |
| 0 | Throwaway — a scratch script, an exploration, output you will read and discard |
| 1 | Normal application change, reversible, covered by tests |
| 2 | Cross-layer, touches production behaviour, or the oracle is weak |
| 3 | Irreversible: a migration, a security boundary, data shape, a public contract |

Gate rules, applied after the mode is chosen:

- **Commitment ≥ 1** → the compiled output must carry the acceptance criterion
  verbatim in the irreducible section. No exceptions; this is the oracle rule.
- **Commitment ≥ 2** → **Pure term is unavailable.** The floor is Trimmed:
  even a perfect-fit term gets its frame stated explicitly, so a wrong
  expansion is visible before it is expensive.
- **Commitment = 3** → Trimmed is still the floor, and the output carries an
  **Expansion check**: run `/intent-compiler:expand` on the compiled prompt
  and read the bill before using it.

## Decision rule → mode

Apply in order; the first match wins.

1. **Dimension 4 scored 0** (the term is yours, not the world's) → **Pact**.
2. **Any of dimensions 1–3 scored 0** → **Expanded**. A term with no fixed
   intension, three competing frames, or a frame that is mostly wrong is not
   a shortcut — it is a wrong answer that costs fewer tokens.
3. **Total ≥ 10 and every dimension ≥ 2** → **Pure term**.
4. **Total 6–9** → **Trimmed term**.
5. **Total ≤ 5** → **Expanded**.

| Mode | Shape of the output |
| --- | --- |
| **Pure term** | The name alone. The frame is imported whole and wanted whole. |
| **Trimmed term** | The name, then one to three lines naming the frame elements that do **not** apply here. Still far cheaper than describing from scratch — the term does the lifting, the trim stops the bleeding. |
| **Pact** | Define the local term once, in one line, then use it short for the rest of the session. Record it in the lexicon so the next session starts with the definition instead of rediscovering it. |
| **Expanded** | Describe it. Not as prose — name the frame elements you want as an explicit list, since no existing frame will supply them. |

A single intent usually produces several of these at once: one anchor pure,
one trimmed, one local term under a pact. Score per term, not per prompt.

## Lexicon thresholds

The schema and location live in `lexicon.md` next to this file. When the log
exists, look only at entries whose `term` matches the one being scored:

- **Three or more entries with `leak > 0`** → the frame bleeds. The term may
  never be emitted as **Pure**; Trimmed is its floor, and the trim lines that
  worked before are reused.
- **Three or more with `misread: true`** → the term is not reliably in your
  models' codebook. Treat canonicity as 0 → **Expanded**, or **Pact** if you
  want to keep the word.
- **Three or more with `adhered: true`, `leak: 0`, `corrections: 0` at mode
  `trimmed`** → the trim is doing nothing. Try **Pure** and say the log drove
  it.
- **A `pact` entry exists for the term** → mode is **Pact**, and the recorded
  definition is reused verbatim. Do not re-derive a definition you already
  agreed on; that is the whole point of a pact.
- **Fewer than three, or mixed** → not a signal. Ignore it and score.

Logged evidence outranks the score and outranks `polysemous.md`. It does
**not** outrank the commitment gate — no amount of history makes a migration
safe to compress blind.

## The honesty rule

Every compression must show what it removed. A compiled prompt that hides its
own losses cannot be audited, and an unauditable compression is indistinguish-
able from a hallucinated one. The `compile` output carries **Dropped** and
**Risk** sections for exactly this reason: if you cannot name the most likely
wrong expansion and the signal that would reveal it, you do not understand the
term well enough to lean on it — expand instead.
