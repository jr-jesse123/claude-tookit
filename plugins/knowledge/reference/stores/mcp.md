# Store: mcp

Notes live in a service reached through an MCP server that is not Basic
Memory: Notion, Confluence, an Obsidian or other note-taking MCP, an internal
wiki. The config names the server and maps the four operations to its tools:

```json
"store": {
  "type": "mcp",
  "server": "notion",
  "tools": {
    "search": "search",
    "read": "fetch",
    "create": "create-pages",
    "edit": "update-page"
  },
  "parent": "Engineering Knowledge"
}
```

Tool names are the server's own names (the part after `mcp__<server>__`).
Any extra field (`parent`, `space`, `database`…) is passed through to the
tools where it fits: the container new notes go under.

## Rules

- If the server or a mapped tool is not available, stop and tell the user.
  Never fall back to another store.
- Read the tool's input schema before the first call; services differ in how
  they take content (markdown, blocks, storage format). Convert the approved
  draft faithfully and say so if anything (a table, a link style) cannot be
  carried over.
- When `edit` cannot change a single section, it replaces the whole body:
  read the current note right before writing and show the user the full new
  body, not only the changed section.
- Placement folders map to whatever the service uses for hierarchy (parent
  pages, databases, labels). Say which one you chose.

Researcher and reviewer agents use **search** and **read** only.
