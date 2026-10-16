# Store: basic-memory

Notes live in a [Basic Memory](https://github.com/basicmachines-co/basic-memory)
project, reached through its MCP server.

## Finding the tools

The tools are named `mcp__<server>__<tool>`, and the server name is whatever
the user registered (`basic-memory`, `basic_memory`, `memory`…). Find it from
the available tools: the server that offers both `search_notes` and
`write_note`. If no such server is available, stop and tell the user — do not
fall back to writing files on disk, which would land outside their knowledge
base.

When the config names a `project`, pass it to every call that takes one.

## Conventions first

Read one or two existing notes in the target folder before drafting and match
their shape. Basic Memory parses two structures inside a note, and notes that
use them are more useful to its search and graph:

- **Observations**: `- [category] fact #tag (context)` lines, typically under
  `## Observations`.
- **Relations**: `- relation_type [[Other Note]]` lines, typically under
  `## Relations`.

Use them when the project's notes do; otherwise write plain prose with
`[[wikilinks]]`. Keep sources inline in either form.

## Operations

| Operation | Tool |
| --- | --- |
| **search** | `search_notes` with the subject's name, then synonyms. `build_context` on a hit (when available) shows its linked notes. |
| **read** | `read_note` by title or permalink. |
| **create** | `write_note` with `title`, `folder` (the placement folder) and `content`. |
| **edit** | `edit_note` with `operation` `append`, `prepend`, `find_replace` or `replace_section` — the narrowest one that does the change. |

Researcher and reviewer agents use **search** and **read** only; `write_note`,
`edit_note`, `delete_note` and `move_note` are off-limits to them.
