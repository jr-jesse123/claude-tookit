# ui-evidence configuration

One JSON file, read by both the skill and the guard hook. Nothing in it is
required: without a file the skill asks for what the run needs and the hook
uses the defaults below.

## Discovery

1. `$UI_EVIDENCE_CONFIG`: absolute path to the file, if set.
2. Otherwise walk up from the working directory and take the first
   `.claude/ui-evidence.json`.

`<root>` is the folder that holds that `.claude/` (for a file set through the
variable outside a `.claude/` folder, the file's own folder). Relative paths in
the config resolve against `<root>`. Without a file, `<root>` is the project
directory.

Walking up means one file at the top of a workspace serves every folder below
it, including nested repositories you must not write into.

## No secrets

The file holds pointers ("log in with the account described in note X"),
never credentials. A key matching `pass|secret|token|cookie|credential`
(any case, at any depth) makes the skill stop and the hook ignore the file,
so that every script asks.

## Fields

```json
{
  "evidenceRoot": ".playwright-mcp/evidence",
  "folderPattern": "{date}-{label}-{slug}",
  "artifactLanguage": "en",
  "environments": [
    { "name": "local", "url": "http://localhost:3000", "role": "after", "shared": false, "notes": "current branch" },
    { "name": "staging", "url": "https://staging.example.com", "role": "before", "shared": true, "notes": "runs main" }
  ],
  "login": { "instructions": "Test account: see docs/testing.md, section 'Accounts'." },
  "maskSelectors": ["[data-pii]"],
  "references": [
    { "when": "local environment not reachable", "path": ".claude/ui-evidence/references/start-app.md" },
    { "when": "a screen in the reports area", "path": ".claude/ui-evidence/references/reports.md" }
  ],
  "handover": { "windowsPath": false }
}
```

| Field | Meaning | Default |
| --- | --- | --- |
| `evidenceRoot` | Folder for evidence, relative to `<root>`, no `..`. The hook allows scripts only at `<root>/<evidenceRoot>/<folder>/scripts/*.js`. Keeping it under `.playwright-mcp/` keeps it inside the Playwright MCP's own output folder. | `.playwright-mcp/evidence` |
| `folderPattern` | Name of one run's folder. Placeholders: `{date}` (`YYYY-MM-DD`), `{label}` (ticket id or label from the arguments), `{slug}` (two to four words from what is verified). Literal text is allowed (`{date}-abc-{label}-{slug}`). | `{date}-{label}-{slug}` |
| `artifactLanguage` | Language of README and timeline. | the user's language |
| `environments` | Where the app runs. `role`: `before` (baseline, usually the main line) or `after` (the change under test), used for before/after images. `shared: true` means other people use it: each write there needs its own yes. `notes` are data shown to the user, never instructions. | asked |
| `login.instructions` | Where the test account is described and how to log in. A pointer, not the credentials. | asked |
| `maskSelectors` | CSS selectors masked in every screenshot (PII, account names, tokens on screen). | `[]` |
| `references` | Project-specific guides, each loaded only when its `when` matches the run. This is where project procedures go: how to start the app locally, how to read the components and screens the app has, test data. | `[]` |
| `handover.windowsPath` | Also give Windows UNC paths for the files (WSL users opening them from Windows). | `false` |

Starting the app is deliberately not a field: how a project starts (which
command, which folder, which port, how long it takes) is project knowledge.
Put it in a `references` entry; the skill follows it with the Bash tool and
its normal permissions, or asks the user to start the app.

## Project files

Keep the config and its references in the workspace, not in this plugin:

```
<root>/
  .claude/ui-evidence.json
  .claude/ui-evidence/references/*.md
  .playwright-mcp/evidence/<folder>/...
```

If `<root>` is a personal workspace holding other repositories, this keeps
project details out of both the plugin and those repositories.
