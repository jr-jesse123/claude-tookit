---
description: Generate a changelog section from the commits since the last tag.
argument-hint: [since-ref, defaults to the latest tag]
allowed-tools: Bash(git log:*), Bash(git tag:*), Bash(git describe:*), Read
disable-model-invocation: true
---

Generate a changelog section for the commits since `$ARGUMENTS`, or since the
most recent tag when no argument is given.

Collect the commits:

```
git describe --tags --abbrev=0
git log <since>..HEAD --pretty=format:'%h %s%n%b' --no-merges
```

Group them under these headings, omitting any that would be empty:
`Added`, `Changed`, `Fixed`, `Removed`, `Security`.

Rules:

- One bullet per user-visible change, written for someone who did not read the
  diff. Merge several commits that implement one change into one bullet.
- Drop pure refactors, formatting, and CI-only commits unless they change
  behavior.
- Keep the commit's short SHA at the end of each bullet: `(a1b2c3d)`.
- Note breaking changes first, prefixed with `**BREAKING**`.

If the repo has a `CHANGELOG.md`, match its existing heading style and date
format, and show the new section without writing the file — the user decides
where it goes.
