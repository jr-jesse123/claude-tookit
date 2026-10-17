# Claim lists

The contract between the `harvest` skill, the `harvest-researcher` agent and
the `harvest-reviewer` agent. The researcher writes a claim list, the reviewer
judges it line by line, the skill drafts the note from what survives. The
skill also writes claim lists itself on the confirm and record paths.

## Format

```
# Claims: <topic>

Target note: <store path or title, or "new: <intended path>">
Format: id | claim | source(s) | seen|inferred|stated | new|contradicts

C1 | <one fact, one sentence> | <most specific source> | seen | new
C2 | <one fact> | <source A> ; <source B> | seen | new
C3 | <a decision or its reason> | user, session <id or "this session"> <YYYY-MM-DD> | stated | new

## Extension points for other notes
E1 | <fact that belongs in another note> | <source> | seen|inferred | <note title, or "new: <topic>">

## Open questions
- <what could not be settled, and what would settle it>
```

- **One fact per claim.** A claim with two sources that each prove half of it
  is two claims. A claim with two sources that each prove all of it is one
  claim, with both sources separated by ` ; `.
- **Source** = the most specific locator opened: `path:line` over a file, a
  page id over a space, an issue key, a URL with an anchor, a commit SHA.
- **seen** = the cited source was opened and says it. **inferred** = a
  conclusion drawn from what was opened, however confident. **stated** = the
  user said or decided it in a session and nothing else records it; its
  source is the user and the session. Only what the user said qualifies: a
  conclusion the assistant drew is never `stated`.
- **new** = the target note does not hold it. **contradicts** = the target
  note says otherwise (quote the note's sentence after the claim, in brackets).
- **Extension points** are facts met on the way that belong to another
  subject. They carry the source already opened and are never researched
  further.

`stated` claims never go to the reviewer: there is no source to open. They
go straight to the draft, marked as stated.

## Evidence levels

What a fact in a note rests on. The skill sets the level from the review.

| Level | Meaning | Comes from |
| --- | --- | --- |
| `stated` | The user said it; no source to check. | A `stated` claim. |
| `verified` | One source, reopened by the reviewer in a clean context. | `confirmed` with 1 independent source. |
| `corroborated` | Two or more independent sources agree, each reopened by the reviewer. | `confirmed` with 2+ independent sources. |

Reopening the claim's own source is verification, not corroboration: a
`confirmed` claim with one source is `verified`, however good the source.

**Independent** means neither source is derived from the other. Code and the
design doc that describes it are independent (one is behaviour, the other
intent); so are a config file and the ticket that decided its value. Two
pages that copy each other, a ticket that quotes a doc, a doc generated from
the code, or two lines of the same file are not.

**Load-bearing claims** are the ones the note's lead and mechanism rest on:
if one is wrong, the note misleads. Corroboration effort, when there is any,
goes to these and nowhere else.

## Review verdicts

| Verdict | Meaning | In the note |
| --- | --- | --- |
| `confirmed` | The source says it and the label is right. | As fact, `verified` or `corroborated`. |
| `downgrade` | The source supports it only partly, or it is a conclusion. | As a marked inference or `[question]`. |
| `cut` | The source contradicts it, it repeats the note, it is ephemeral, or it is too vague to use. | Dropped. |
| `unverified` | The source could not be opened. | Dropped, or a `[question]` if it matters. Never as fact. |

For a claim with several sources, open each one. The claim is `confirmed`
when at least one says it; `independent` counts the cited sources that say
it and are independent of each other. A cited source that does not say it
is named in the reason.

## Review output

```
# Review: <topic>

| id | verdict | independent | reason (one line; for cut/downgrade, what the source actually says) |
|----|---------|-------------|------|
| C1 | confirmed | 1 | src/path-list.ts:64-70 lists exactly these children |
| C2 | confirmed | 2 | src/retry.ts:12 and ENG-482 both give 3 attempts |

## Whole-list findings
- Duplicates: ...
- Gaps: ...
- Contradicted notes: <note, the sentence, the claim id that contradicts it>
- Credentials: none | <claim ids>

Summary: <n> confirmed (<n> corroborated), <n> downgrade, <n> cut, <n> unverified
```

`independent` is 0 for anything but `confirmed`.
