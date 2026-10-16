# Claim lists

The contract between the `harvest` skill, the `harvest-researcher` agent and
the `harvest-reviewer` agent. The researcher writes a claim list, the reviewer
judges it line by line, the skill drafts the note from what survives. The
skill also writes claim lists itself on the light path.

## Format

```
# Claims: <topic>

Target note: <store path or title, or "new: <intended path>">
Format: id | claim | source | seen|inferred | new|contradicts

C1 | <one fact, one sentence> | <most specific source> | seen | new
C2 | ...

## Extension points for other notes
E1 | <fact that belongs in another note> | <source> | seen|inferred | <note title, or "new: <topic>">

## Open questions
- <what could not be settled, and what would settle it>
```

- **One fact per claim.** A claim with two sources that each prove half of it
  is two claims.
- **Source** = the most specific locator opened: `path:line` over a file, a
  page id over a space, an issue key, a URL with an anchor, a commit SHA.
- **seen** = the cited source was opened and says it. **inferred** = a
  conclusion drawn from what was opened, however confident.
- **new** = the target note does not hold it. **contradicts** = the target
  note says otherwise (quote the note's sentence after the claim, in brackets).
- **Extension points** are facts met on the way that belong to another
  subject. They carry the source already opened and are never researched
  further.

## Review verdicts

| Verdict | Meaning | In the note |
| --- | --- | --- |
| `confirmed` | The source says it and the label is right. | As fact. |
| `downgrade` | The source supports it only partly, or it is a conclusion. | As a marked inference or `[question]`. |
| `cut` | The source contradicts it, it repeats the note, it is ephemeral, or it is too vague to use. | Dropped. |
| `unverified` | The source could not be opened. | Dropped, or a `[question]` if it matters. Never as fact. |

## Review output

```
# Review: <topic>

| id | verdict | reason (one line; for cut/downgrade, what the source actually says) |
|----|---------|------|
| C1 | confirmed | src/path-list.ts:64-70 lists exactly these children |

## Whole-list findings
- Duplicates: ...
- Gaps: ...
- Contradicted notes: <note, the sentence, the claim id that contradicts it>
- Credentials: none | <claim ids>

Summary: <n> confirmed, <n> downgrade, <n> cut, <n> unverified
```
