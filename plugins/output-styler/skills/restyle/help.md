<!--
Presentation rules (do not print this block):
- Read this file only when the user passes `--help`; then present it and stop.
- Present it in the language the conversation is happening in — translate the
  prose, but keep style names, aliases, flags and the code/commands verbatim.
- Keep the picker table and the six samples: they are what makes the choice
  possible without running the skill.
- Do not restyle anything in the same turn; close by offering the invocation
  the user seems to want ("quer que eu rode `bluf docs` nisso?").
-->

# Restyle — choosing a style

Six styles, one target. They all keep the facts identical and change only the
form. Pick by what you need the reader to *do*, not by what sounds nicest.

## Quick picker

| You need the reader to… | Style |
| --- | --- |
| Decide in 30 seconds, then stop reading | `bluf` |
| Understand it on the first read, no background assumed | `plain` |
| Follow a procedure and get it right | `docs` |
| Execute something risky, possibly tired, possibly not in their language | `ste` |
| Grasp an unfamiliar mechanism from zero | `eli5` |
| See the shape — flow, states, comparison | `visual` |

Combine freely: `bluf docs` gives the decision *and* the procedure. `all`
(or `todos`) runs the six in the order below.

## The same content in every style

Everything under **Sample** is this source text, restyled — the facts never
move:

> The deploy job failed because the migration lock was still held by a previous
> run. You can wait 15 minutes for the lock to expire, or clear it manually with
> `make unlock-db` — but clearing it while a migration is genuinely running
> corrupts the schema.

### `bluf` — aliases `exec`, `minto`

- **Thesis** — answer first, grouped arguments below, raw data last. The reader
  who stops after line one still acts correctly.
- **Pick it when** the output is a decision, a recommendation, a status
  someone will act on; when the audience is senior and time-poor.
- **It costs** — detail moves below the fold and nuance gets compressed into
  claims; a variant that had to cut ends with an *Omitted:* line.
- **Anchored in** BLUF (US Army) and Barbara Minto's Pyramid Principle.
- **Sample**

  > **Wait for the lock; don't clear it blindly.** The deploy failed on a
  > migration lock held by an earlier run, and it expires on its own in 15
  > minutes.
  >
  > **The manual escape has one condition:** `make unlock-db` clears the lock
  > immediately, but only run it after confirming no migration is in progress —
  > clearing a live one corrupts the schema.

### `plain` — aliases `simple`, `iso`

- **Thesis** — reader-first prose: everyday words, strong verbs, short
  sentences, headings that state the message so the answer is findable.
- **Pick it when** you want a good default. It is the safest style for mixed
  audiences and the one that loses the least.
- **It costs** — almost nothing; it just won't compress like `bluf` or draw
  like `visual`.
- **Anchored in** ISO 24495-1 and PlainLanguage.gov.
- **Sample**

  > Your deploy failed because an earlier run still holds the migration lock.
  > You have two ways out. Wait 15 minutes and the lock expires by itself, or
  > clear it now with `make unlock-db`. Only clear it if no migration is
  > running — clearing a running migration corrupts the schema.

### `docs` — aliases `devdocs`, `google`

- **Thesis** — a page from well-kept product docs: second person, present
  tense, anything you *do* becomes a numbered procedure with its expected
  result.
- **Pick it when** the output is heading for a README, a runbook, an onboarding
  page — or whenever the reader will follow along step by step.
- **It costs** — length. Procedures and headings are added scaffolding, so the
  text usually grows.
- **Anchored in** the Google developer documentation and Microsoft writing
  style guides.
- **Sample**

  > ## Recover from a held migration lock
  >
  > The deploy job fails when a previous run still holds the migration lock.
  >
  > 1. Wait 15 minutes. The lock expires and the job runs on the next retry.
  > 2. If you can't wait, confirm no migration is in progress, then run
  >    `make unlock-db`.
  >
  > **Warning:** clearing the lock during a running migration corrupts the
  > schema.

### `ste` — aliases `technical`, `controlled`

- **Thesis** — controlled technical writing: ≤ 20-word sentences, active
  imperative voice, one word with exactly one meaning, warnings before the step
  they protect.
- **Pick it when** a misreading is expensive: incident procedures, migrations,
  anything destructive — or when readers work in a second language.
- **It costs** — all rhythm and nuance. It reads like a manual because it is
  one; it is also the most verbose per idea.
- **Anchored in** ASD-STE100 (the aviation maintenance standard).
- **Sample**

  > WARNING: Do not clear the lock while a migration operates. A cleared lock
  > can cause damage to the schema.
  >
  > The deploy job stopped. A previous run holds the migration lock.
  >
  > 1. Wait 15 minutes. The lock expires.
  > 2. If you cannot wait, make sure that no migration operates. Then run
  >    `make unlock-db`.

### `eli5` — alias `thing-explainer`

- **Thesis** — only words everybody knows, plus one analogy held from start to
  finish. The words get simpler; the facts do not.
- **Pick it when** the reader is smart but has zero background — a stakeholder,
  a new teammate, yourself in an unfamiliar area.
- **It costs** — precision at the edges. Analogies leak, so the variant ends
  with a *This leaves out:* line naming what didn't fit.
- **Anchored in** xkcd's *Thing Explainer* and Simple English Wikipedia.
- **Sample**

  > Changing the shape of the database needs a key, and only one job can hold
  > it at a time. An older job walked away still holding it. You can wait about
  > 15 minutes and the key comes back on its own, or take it back now with
  > `make unlock-db`. Only take it back if nobody is using it. Taking the key
  > mid-change leaves the data half-rebuilt.
  >
  > *This leaves out: why the older job kept the key.*

### `visual` — aliases `diagram`, `mermaid`

- **Thesis** — the content's shape becomes visible: flows into flowcharts,
  lifecycles into state diagrams, options into tables. Prose survives only for
  what a picture can't say.
- **Pick it when** the content is structure, sequence, state or comparison —
  and when you'd otherwise re-read three paragraphs to reconstruct an order.
- **It costs** — everything that isn't structure. Rationale and caveats thin
  out, so the variant ends with *Omitted:*. A decorative diagram over simple
  facts is worse than the prose.
- **Anchored in** Mermaid (renders natively in Claude Code) and structured
  tables.
- **Sample**

  ```mermaid
  flowchart TD
    A["Deploy job fails"] --> B["Lock held by earlier run"]
    B --> C{"Migration in progress?"}
    C -- "No" --> D["make unlock-db"]
    C -- "Yes / unsure" --> E["Wait 15 min for expiry"]
    D --> F["Retry deploy"]
    E --> F
  ```

  > The only branch that matters is C: the manual escape is safe on one side
  > and corrupts the schema on the other.
  >
  > *Omitted: why the earlier run kept the lock.*

  This one is also available as a **native output style** (`Visual`, via
  `/config` → *Output style*) — that makes Claude converse this way by
  default, instead of on demand.

## Flags and targets

| Argument | Effect |
| --- | --- |
| `all`, `todos` | Every style, in the order above |
| `--score` | Appends a metrics table (words, sentences, avg words/sentence, long words; Flesch for English) over the original and every variant |
| `--help` | This catalog. Nothing is restyled |
| a file path | Restyles that file's content |
| quoted text | Restyles the quoted text |
| nothing else | Restyles the last substantive response in the conversation |

The target stays pinned across invocations: calling the skill again restyles
the *original* content, not the previous variant — otherwise the comparison
falls apart. Say so explicitly if you want a variant restyled on top of another.

Two or more styles also get a **Comparison** block at the end, saying what each
one bought and cost *for that specific content*. When one keeps winning, the
skill offers to record it — in `CLAUDE.md`, or as the project's output style
when a native port exists.
