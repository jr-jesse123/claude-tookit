# playwright-guard

A `PreToolUse` hook for the two [Playwright MCP](https://github.com/microsoft/playwright-mcp)
tools that run code:

- `browser_run_code_unsafe` runs JavaScript **in the Playwright server process**. Its own
  description calls it "RCE-equivalent".
- `browser_evaluate` runs JavaScript in the page.

The policy is **ask by default**. One narrow shape runs without a prompt: a script **file**
in a configured folder, with no Node-escape tokens and no direct non-GET HTTP.

Everything ships in the plugin. You do not need to edit any project's `settings.json` or
`settings.local.json`.

## Install

```
/plugin marketplace add jr-jesse123/claude-tookit
/plugin install playwright-guard@jr-claude-toolkit
```

Run `/hooks` to confirm the hook is loaded. It is listed under `PreToolUse`, with the matcher
`^mcp__.*playwright.*__browser_(run_code_unsafe|evaluate)$`. The matcher covers a server
named `playwright` (`mcp__playwright__browser_evaluate`) and a Playwright server bundled by
another plugin (`mcp__plugin_<plugin>_<server>__browser_evaluate`). Inside the script the
tool name is reduced to the part after the last `__`.

Requirements: `bash`, `jq`, `grep`, `sed` and GNU coreutils (`realpath` with `-m`, `cat`,
`head`). If `jq` or GNU `realpath` is missing, the hook fails closed: it exits 2 and blocks
the call, and the message says what to install. On macOS, install `coreutils` and put its
GNU `realpath` on `PATH`. `test.sh` runs the hook with only these commands on `PATH`.

## Decision table

| Situation | Decision |
| --- | --- |
| Any other tool | No output. The normal permission flow applies. |
| `browser_evaluate` whose input has no network token | No output. The normal permission flow applies. |
| `browser_evaluate` whose input has a network token: `fetch(`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `axios`, `.ajax` | `ask` |
| `browser_run_code_unsafe` with inline `code`, including when `filename` is also set | `ask` |
| `browser_run_code_unsafe` with no `code` and no `filename` | `ask` |
| `filename` resolves outside the scripts glob, or the file is missing or unreadable | `ask` |
| Script has a Node-escape token: `require(`, `import(`, a line-leading `import `, `child_process`, `process`, `eval(`, `Function(`, `globalThis`, `module`, `__dirname`, `Buffer`, `constructor` | `ask` |
| Script has a direct-HTTP or routing token: `fetch(`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `axios`, `.ajax`, `newContext`, `.route(`, `routeFromHAR`, `routeWebSocket`, `.request[`, `method:` | `ask` |
| Script uses `.request` in any form other than `.request.get(`, `.request.head(` or `.request()` (this catches `.request.put`, `.request.fetch`, `const r = page.request`) | `ask` |
| Script is in the allowed folder and passes every check above | **`allow`** (no prompt) |
| Hook input is not a JSON object, or `jq` / GNU `realpath` is missing | Exit 2 (blocks the call) |

Notes on the table:

- Whitespace before `(` is accepted: `require (`, `fetch (`, `eval (` and the others also
  match. A quoted key is accepted too: `"method":` also matches.
- Matching is lexical. A token anywhere in the file asks, even inside a comment or a string.
  For example, `processItems` matches `process`. False positives become an `ask`, never an
  `allow`.
- When both `code` and `filename` are set, the Playwright MCP runs `filename` and ignores
  `code`. The guard asks anyway, so that only one simple shape can be allowed.
- Every decision includes `hookEventName: "PreToolUse"` and a reason. Claude Code shows the
  `ask` reason in the prompt, labeled `[plugin:playwright-guard]`.

## Configuration

| Setting | Default | Meaning |
| --- | --- | --- |
| `PLAYWRIGHT_GUARD_SCRIPTS_GLOB` | `.playwright-mcp/guarded-scripts/*.js` | Allowed script files, relative to the project root. Each `*`, `?` or `[...]` matches **within one path segment**: `*` never crosses a `/`, and `**` is not supported. The glob must not be absolute and must not contain `.`, `..` or empty segments. A bad glob makes every script call `ask`. |

The project root is `$CLAUDE_PROJECT_DIR` (the directory where the session started). If that
variable is empty, the hook uses the `cwd` field of the hook input, then `$PWD`. A relative
`filename` resolves against the project root. The filename and the root both go through
`realpath -m`, and the hook compares the resolved path. This way, `..` and symlinks (on the
file or on any folder above it) cannot escape the glob.

Why `$CLAUDE_PROJECT_DIR` comes before `cwd`: the input's `cwd` follows the session's
current directory. If `cwd` came first, a `cd` into another tree would move the allowed
folder there. The Playwright MCP resolves relative names against its own workspace root:
the first MCP root the client advertises, or the server's working directory. In Claude Code
that is normally the project root **[inferred]**. If your MCP config gives the server a
different `cwd`, pass absolute filenames.

To set the glob, you can:

- set `PLAYWRIGHT_GUARD_SCRIPTS_GLOB` in the `env` block of `~/.claude/settings.json` (all
  projects) or of a project's `.claude/settings.json` (one project). Claude Code applies the
  `env` block to the processes it starts, including hooks **[verify on your version]**;
- or export it in the shell that starts `claude`.

Example, one folder per ticket:

```json
{ "env": { "PLAYWRIGHT_GUARD_SCRIPTS_GLOB": ".playwright-mcp/evidence/*/scripts/*.js" } }
```

## How Claude Code treats the decisions

From the [hooks reference](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)
and the [permissions page](https://code.claude.com/docs/en/permissions#extend-permissions-with-hooks),
read on 2026-10-19:

- **Input.** On stdin the hook gets `tool_name`, `tool_input`, `cwd`, `hook_event_name`,
  `permission_mode` and more. `hookSpecificOutput` must include `hookEventName`.
- **No output, exit 0.** This means "no decision": the call goes through the normal
  permission flow. Staying silent does not approve the call. This is why the clean case
  returns an explicit `allow`.
- **`allow`.** Skips the permission prompt, except for the actions that no mode
  auto-approves.
- **Your own rules still win.** Claude Code evaluates deny and ask rules whatever the hook
  returns. A `deny` rule for one of these tools still blocks, and an `ask` rule still
  prompts, even after this hook says `allow`.
- **`ask` in `auto` mode.** A hook `ask` forces a prompt. The classifier can still deny the
  call but cannot approve it silently.
- **Several hooks.** Precedence is `deny` > `defer` > `ask` > `allow`. Exit 2 counts as
  `deny`, and stderr is the reason.
- **Errors.** A hook that times out (10 s here) or exits with a code other than 0 or 2 does
  not block: the call continues through the normal permission flow. In `default` mode that
  still prompts for an MCP tool.

### Measured end to end

Measured on 2026-10-19 with Claude Code 2.1.303 and `@playwright/mcp` 0.0.83 (headless
Chromium), using `claude -p --plugin-dir plugins/playwright-guard`. In `-p` no one can
answer a prompt, so Claude Code denies a call that would prompt. A **ran** result shows the
call went through without a prompt; a **denied** result shows it needed a prompt.

| Call | `default` | `auto` | `bypassPermissions` | `dontAsk` |
| --- | --- | --- | --- | --- |
| Clean script in the allowed folder | ran | ran | – | ran |
| Inline `code` | denied (hook `ask`) | denied (hook `ask`) | denied (hook `ask`) | denied (hook `ask`) |
| Script with `require("fs")` | denied (hook `ask`) | denied (hook `ask`) | – | – |
| Script with `page.request.put(...)` | denied (hook `ask`) | denied (hook `ask`) | – | – |
| `browser_evaluate` `() => document.title` | denied (normal MCP prompt, no hook output) | ran (classifier approved) | – | – |
| `browser_evaluate` with `fetch(` | denied (hook `ask`) | denied (hook `ask`) | – | – |
| **Without the plugin:** clean script | denied (normal MCP prompt) | – | – | – |
| **Without the plugin:** inline `require("fs")` | – | **ran** (classifier approved; `require` then threw inside the Playwright `vm`) | – | – |
| **Without the plugin:** inline code | – | – | ran | – |

A dash means the case was not run. What this shows:

- The `allow` path removes the prompt in `default`, `auto` and `dontAsk`. Without the plugin,
  the same clean script needs a prompt in `default` mode.
- In `auto` mode a hook `ask` is a real prompt; the classifier did not approve it. Without
  the plugin, the classifier ran inline code that called `require("fs")`.
- `bypassPermissions` still honored the hook's `ask`. The control run, without the plugin,
  shows that bypass mode was active.
- `browser_evaluate` with no network token is left to the normal flow. In `default` mode
  that is still a prompt, unless you add an allow rule for the tool.
- These runs used `-p`, where a prompt becomes a denial. In an interactive session the same
  calls show a prompt labeled `[plugin:playwright-guard]`. That interactive behaviour was not
  measured here.

## What this is not

This is a **lexical filter, not a sandbox.** It catches mistakes and naive injected code. It
does not stop a deliberate bypass. Names built from strings, values passed in from the
page, and patterns the token list does not know can all get past it.
Whatever the browser can reach, a script that passes the filter can reach too.

Not covered (known gaps):

- `page.screenshot({ path })`, `page.pdf({ path })`, `page.screencast.start({ path })` and
  downloads can write to any path the server process can write. Code run by
  `browser_run_code_unsafe` skips the Playwright MCP's own file-access check.
- `page.goto` can open any host, and `.request.get` / `.request.head` can reach any host.
  GET is allowed, not made safe.
- `browser_evaluate`'s `filename` parameter saves the result to a file. The guard does not
  look at it. The Playwright MCP limits it to the workspace and output folders unless
  `--allow-unrestricted-file-access` is set.
- **TOCTOU:** the file can change between the check and the run.
- The allowed folder is only as protected as the agent's write access. If the agent can
  write a file there, the lexical checks are the only control.
- Other tools are not guarded: `browser_navigate`, `browser_file_upload`,
  `browser_fill_form`, `browser_type`, and any wrapper tool that calls
  `browser_run_code_unsafe` under another name.
- A server whose name does not contain `playwright` does not match the hook.

Possible hardening for a later version (not in this one): a host allowlist for `page.goto`
and `.request.get`, a path allowlist for `path:` arguments, and running the Playwright MCP
in a separate browser profile or a container.

## Tests

```
plugins/playwright-guard/hooks/test.sh
```

The script builds fixtures in a temp dir and runs every `browser_run_code_unsafe` case under
two tool names: `mcp__playwright__…` and the plugin-scoped `mcp__plugin_playwright_playwright__…`.
It covers the decision table, relative paths, `..`, symlinked files and folders, a custom
glob, a bad glob, a missing `jq`, invalid JSON, and the regression that started this plugin:
inline `require("fs")` under a Claude Code tool name used to pass silently. CI runs the
script ([`validate.yml`](../../.github/workflows/validate.yml)).
