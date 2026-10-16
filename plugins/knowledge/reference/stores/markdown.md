# Store: markdown

Notes are plain `.md` files under `store.root`. Works for a `docs/` folder in
the repository, an Obsidian vault, or any folder of notes. Needs no MCP
server: only Read, Grep, Glob, Write and Edit.

Resolve `root` once: relative paths are relative to `${CLAUDE_PROJECT_DIR}`;
expand `~`. A root that does not exist yet is fine — it is created on the
first write.

## Conventions first

Before the first search, look at the store's existing shape and follow it:

- **Links**: `[[wikilinks]]` if the root holds `.obsidian/` or existing notes
  use them; otherwise relative markdown links (`[Token refresh](../mechanisms/token-refresh.md)`).
- **File names**: match the existing style (`kebab-case.md`, `Title Case.md`).
  Empty store → `kebab-case.md`.
- **Frontmatter**: match what existing notes carry; empty store → the block in
  the writing guide.
- **Index**: if the root has an index or map-of-content file (`README.md`,
  `index.md`, `_index.md`, `MOC.md`), new notes get a link line there.

## Operations

| Operation | How |
| --- | --- |
| **search** | Grep, case-insensitive, under the root for the subject's name and two or three synonyms or key terms; Glob for file names containing them. Read the frontmatter and headings of each hit before classifying. |
| **read** | Read the file. |
| **create** | Write `<root>/<placement folder>/<file name>.md`. Add the index line in the same step when an index exists. |
| **edit** | Edit only the sections that change; bump `updated` when the note carries it. |

Researcher and reviewer agents use **search** and **read** only.

## After writing

When the root is inside a git repository, the notes are ordinary working-tree
changes: say which files were written and leave committing to the user.
