# Knowledge configuration

Where notes live, which sources research may use, and how notes are written.
Read by the `harvest` skill in step 0. Nothing here is required: without a
config the skill detects sensible defaults and proposes them.

## Lookup order

1. `${CLAUDE_PROJECT_DIR}/.claude/knowledge.json` — the project's knowledge base.
2. `~/.claude/knowledge.json` — a personal knowledge base shared by all projects.
3. Neither → **detect** (below) and propose.

The first file found wins as a whole; fields are not merged across files.

## Fields

A fuller example, with Basic Memory, several sources and a custom kind, is in
`config.example.json` next to this file.

```json
{
  "store": { "type": "markdown", "root": "docs/knowledge" },
  "language": "en",
  "placement": {
    "concept": "concepts",
    "system": "systems",
    "component": "components",
    "mechanism": "mechanisms",
    "process": "processes",
    "environment": "environments",
    "decision": "decisions"
  },
  "style": "docs/knowledge/WRITING.md",
  "sources": [
    { "name": "repo", "kind": "code", "where": "." },
    { "name": "Confluence", "kind": "docs", "hint": "space ENG on acme.atlassian.net" },
    { "name": "Jira", "kind": "tickets", "hint": "project ABC" },
    { "name": "web", "kind": "web" }
  ],
  "max": 3,
  "budget": 12
}
```

| Field | Meaning | Default |
| --- | --- | --- |
| `store` | Where notes are searched, read and written. One of the store types below. | detected |
| `language` | Language notes are written in, whatever language the user speaks. `"auto"` = the language most existing notes use. | `"auto"` (falls back to the user's language when the store is empty) |
| `placement` | Folder per kind of knowledge, relative to the store. A kind not listed goes to the store root. Add or rename kinds freely (`screen`, `api`, `dataset`…). | the map above |
| `style` | Path to the project's own note-writing guide. Replaces `reference/note-writing.md` entirely when set. | the plugin's guide |
| `sources` | Sources research may use, each with a `kind` (ranking below) and an optional `where` (path, URL) or `hint` (site, space, project key — anything that tells a researcher where to look). | detected |
| `max` | Default `--max`. | `3` |
| `budget` | Source reads (files, pages, tickets, commits, web pages opened) each researcher may spend on one candidate before it stops and lists the rest as open questions. Research is most of a harvest's cost; raise it for a knowledge base where notes must go deep, lower it to save tokens. | `12` |

## Store types

Each type has an adapter in `reference/stores/` that maps the four operations
the skill needs — **search**, **read**, **create**, **edit** — to tools. Load
only the adapter of the configured type.

| `type` | Extra fields | Adapter |
| --- | --- | --- |
| `markdown` | `root`: folder, relative to the project or absolute (`~` allowed). An Obsidian vault or a `docs/` folder both qualify. | `stores/markdown.md` |
| `basic-memory` | `project` (optional): Basic Memory project name. | `stores/basic-memory.md` |
| `mcp` | `server`, and `tools`: `{ "search", "read", "create", "edit" }` tool names on that server. For Notion, Confluence, an Obsidian MCP, or any other note service. | `stores/mcp.md` |

## Source kinds and ranking

Research trusts sources in this order. Each step down needs more
corroboration before a claim may be marked `seen`.

1. **Primary** — `code`, `config`, `schema`, `data`, `spec` (a standard, an
   official API reference). What actually runs or what defines it.
2. **Documentation** — `docs` (design docs, wikis, READMEs, official guides).
3. **Records of discussion** — `tickets`, `chat`, `pr` (issues, PR threads,
   meeting notes). Good for *why* and *when*, weak for *what is true now*.
4. **Secondary web** — `web` (blogs, forums, answers). Leads, rarely proof.
5. **Memory** — what a session remembered or assumed. Never proof.

A `kind` outside this list ranks with documentation unless its entry says
otherwise (`"rank": 1..5`).

## Detecting defaults (no config)

**Store**, first match:
1. Basic Memory tools are available (a tool named `*search_notes` next to a
   `*write_note` on the same MCP server) → `basic-memory`.
2. An existing knowledge folder in the project: `docs/knowledge/`,
   `knowledge/`, `notes/`, or a folder holding `.obsidian/` → `markdown` there.
3. Otherwise → `markdown` at `docs/knowledge/` (created on first write).

**Sources**: the project itself (`code`, when the working directory is a
repository), each connected MCP server whose tools read documents or tickets
(name it and guess the kind from its tools), and `web` when WebSearch or
WebFetch is available.

Show the detected config to the user once, as JSON. Offer to save it to
`.claude/knowledge.json` (project) or `~/.claude/knowledge.json` (personal);
saving needs a yes, and a harvest can run on the detected config without it.
`/knowledge:harvest --setup` runs only this part, interactively (see the
skill).

## Hard read-only (optional)

The researcher and reviewer agents cannot use Write, Edit or NotebookEdit.
MCP write tools are barred only by their instructions, because their names
depend on how each server was registered. Permission rules in
`.claude/settings.json` make that hard — but they apply to the whole session,
the harvest's own write step included. So:

- **`ask`** for the store's write tools: the session's approved write prompts
  once more, and an agent that tries to write shows up as a prompt you
  decline.
- **`deny`** for what no step of a harvest should ever do: ticket edits and
  transitions, page creation or update on source systems, CLIs that bypass
  the MCP servers.

```json
{
  "permissions": {
    "ask": [
      "mcp__basic-memory__write_note",
      "mcp__basic-memory__edit_note"
    ],
    "deny": [
      "mcp__basic-memory__delete_note",
      "mcp__basic-memory__move_note",
      "mcp__atlassian__editJiraIssue",
      "mcp__atlassian__transitionJiraIssue",
      "mcp__atlassian__updateConfluencePage",
      "mcp__atlassian__createConfluencePage",
      "Bash(az:*)",
      "Bash(gcloud:*)"
    ]
  }
}
```

Use your servers' actual names (the middle part of `mcp__<server>__<tool>`).
`--setup` can draft this block from the tools it finds.
