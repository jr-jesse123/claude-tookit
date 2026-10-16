# Writing a knowledge note

The default guide. A project can replace it with its own (`style` in the
config); when it does, this file is not read.

A note is read months later by someone (or a model) who did not see the
session. It must say what is true, say how we know, and stop.

## Shape

1. **One subject per note.** A concept, a system, a mechanism — not a session
   recap. A second subject gets its own note and a link.
2. **Lead with what it is**, in one or two sentences a newcomer can follow.
   Then why it matters or where it shows up.
3. **Then how it works**: the mechanism, in the order things happen. Name the
   actual parts (files, services, tables, screens, people's roles) rather than
   describing them vaguely.
4. **Then the edges**: limits, failure modes, surprising behaviour, what it is
   often confused with.
5. **Related**: links to the notes it depends on or that depend on it.
6. **Open questions** last, each marked `[question]`.

Use headings only when the note has more than one of these parts. Prefer
short paragraphs and lists over tables, except for genuinely tabular facts.

## Truth markers

- A fact carries its source inline, in the most specific form you have:
  `` `src/auth/refresh.ts:42` ``, a page id, an issue key, a URL.
- An inference is marked as one: "(inferred from …)".
- Anything unsettled is a `[question]`, never a confident sentence.
- When sources disagree, say so and cite both.

## What stays out

- Status and time-bound facts: ticket states, build results, "currently
  broken", today's workaround, who is on leave.
- Anything a single search gives back in seconds (a constant's value, a file
  list) unless the note explains *why* it is that way.
- Session narration: "we found", "after some digging", "as discussed".
- Passwords, tokens, keys, certificates — even when a source shows them.

## Frontmatter

When the store uses frontmatter, keep it minimal and consistent with the
notes already there. Absent a convention:

```yaml
---
title: <Title Case name of the subject>
type: <kind, from the placement map>
tags: [<2-5 tags>]
updated: <YYYY-MM-DD>
---
```

Follow the existing notes' conventions over this guide whenever the two differ.
