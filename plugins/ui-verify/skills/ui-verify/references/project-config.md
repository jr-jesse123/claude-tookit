# Project configuration: `.claude/ui-verify.json`

Optional. The skill looks for the file through `$UI_VERIFY_CONFIG`, then upward from the working directory. Every field has a default, so a project with the defaults needs no file.

```json
{
  "targetsDir": ".claude/ui-targets",
  "defaultTarget": "int",
  "catalogDir": "ui-map",
  "planningNotes": [".claude/ui-verify/domain-rules.md"],
  "evidenceRoot": ".playwright-mcp/evidence"
}
```

| Field | Default | Meaning |
| --- | --- | --- |
| `targetsDir` | `.claude/ui-targets` | Folder of the target profiles (`references/target-profile.md`). A target is the file name without `.md`. |
| `defaultTarget` | none | Target used when the user names none. With no default and exactly one profile, that one runs; with several, the skill asks. |
| `catalogDir` | none | Folder of the project's UI catalog (`references/catalog-contract.md`). Without it the executors find elements by role and text. |
| `planningNotes` | `[]` | Files the planner reads before planning: the domain rules a plan must respect (who must be related to whom, what a role can see, which data is shared). |
| `evidenceRoot` | the `evidenceRoot` of `.claude/ui-evidence.json`, else `.playwright-mcp/evidence` | Where run folders are created. Keep it the same as `ui-evidence`'s, because record stages write there. |

Paths are relative to the folder that holds `.claude/`. The skill resolves them and passes absolute paths to the agents, which read no configuration themselves.

## What the project provides, and what the plugin provides

| Project | Plugin |
| --- | --- |
| target profiles, accounts, hosts | the orchestration flow, the plan format, the naming rule |
| UI catalog and its generator | the planner, the executors, their budgets and report format |
| planning notes (domain rules) | tracing, trace packing, video trimming, token report scripts |
| an agent that reads backend logs and traces, if the project has one | the account-check and write-policy contracts the profiles fill in |
| the Playwright MCP configuration | the rules about secrets, request headers and `evaluate` |

## Requirements the project must meet
- A Playwright MCP server with `--caps devtools` (tracing and video tools) and, for several Claude sessions at once, `--isolated`. Pin its version; the tool names the agents use are listed in their frontmatter.
- The `ui-evidence` plugin, for record stages.
- Optional: a tracker MCP for the planner. The planner's tool list names Linear and basic-memory tools; when they are absent the planner works from the ticket text the skill puts in its prompt. Copy the agent into the project's `.claude/agents/` and edit the list to use another tracker.
