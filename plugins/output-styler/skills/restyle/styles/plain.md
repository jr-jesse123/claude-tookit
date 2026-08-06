# plain — Plain language (ISO 24495-1 / PlainLanguage.gov)

The reader finds what they need, understands it on first read, and can use
it. ISO 24495-1's four governing principles — relevant, findable,
understandable, usable — turned into writing moves, with PlainLanguage.gov's
concrete techniques on top. Works in any language; this is the style closest
to "good default prose".

## Rules

1. **Start from the reader's task**, not from the system or the history.
   First sentence answers "what does this mean for you / what do you do now".
2. **Address the reader as "you"**; name who does what — no agentless voice
   ("mistakes were made").
3. **Strong verbs, no nominalizations**: *decide*, not *make a decision*;
   *fails*, not *results in a failure condition*.
4. **Everyday words.** Jargon only when the reader's domain requires it, and
   defined in the same sentence it first appears.
5. **Sentences average ≤ 20 words**, one idea each. Paragraphs one topic
   each, 3–5 sentences.
6. **Findability is structure**: headings that state the message ("Back up
   before migrating", not "Migration considerations"), lists for any sequence
   of 3+, tables for anything with two dimensions.
7. **Front-load** every section and list item: key words first, qualifiers
   after.
8. Keep all conditions and exceptions — plain language simplifies wording,
   never truth.

## Before

> Prior to initiating the deployment procedure, verification of the backup's
> existence and integrity should be performed by the operator, inasmuch as
> restoration in the event of failure is contingent upon said backup.

## After

> Before you deploy, check that your backup exists and is valid. If the
> deployment fails, this backup is the only way to restore the system.
