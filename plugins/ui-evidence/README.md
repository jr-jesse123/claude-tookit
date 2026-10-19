# ui-evidence

Verify UI behaviour in a real browser through the Playwright MCP and leave
evidence a reviewer, QA or PM can trust without re-running it:

- test cases agreed with you before the browser opens;
- a WebM video per run, one chapter per case, recorded safely;
- per-case screenshots, values read from the DOM before and after each
  action, real timestamps;
- a `README.md` with a PASS / FAIL / not covered table, and a `timeline.txt`;
- on request, before/after images with highlights and comment text for a
  ticket or PR.

Nothing is uploaded, attached or posted. You get files and text; you post them.

| Component | Name | What it does |
| --- | --- | --- |
| skill | `/ui-evidence:ui-evidence <ticket-or-label> [what to verify]` | The workflow: configure, agree cases, prepare, run and record, before/after images, restore, write up and hand over. User-invoked only. |
| hook | `PreToolUse` on the Playwright MCP's `browser_run_code_unsafe` and `browser_evaluate` | Lets an evidence script run without a prompt, asks for any other Playwright code. |
| reference | `references/recording.md` | The script harness, the safe-video rules, README and timeline format. |
| reference | `references/config.md` | `.claude/ui-evidence.json`: discovery, fields, defaults. |
| reference | `references/compose.md` | Before/after captures, compose page, comment text. |
| reference | `references/ag-grid.md` | Generic AG Grid techniques (scoping, virtualised columns, computed style, real-mouse drags, highlights). |

## Requirements

- A Playwright MCP server, configured by you (this plugin does not ship one).
  Pin its version: the guard and the harness depend on its tool names and on
  `page.screencast`, which `@playwright/mcp@latest` provides today through
  Playwright 1.64.0-alpha (`@playwright/mcp@0.0.83`). For example
  `npx @playwright/mcp@0.0.83`.
- Recommended MCP options: `--secrets <dotenv file>` so `browser_type` can type
  a secret by name without its value entering the conversation, and
  `--output-dir <root>/.playwright-mcp` when sessions start in folders below
  the evidence root (see "Where scripts may live").
- For the hook: `bash`, `jq`, `grep` and GNU coreutils (`realpath -m`). On
  macOS install coreutils. Without `jq` the hook exits 2, which blocks the
  call.

## Configuration

Optional. One file, `.claude/ui-evidence.json`, found through
`$UI_EVIDENCE_CONFIG` or by walking up from the working directory, read by
both the skill and the hook. It names the evidence folder, the environments
(with `role` before/after and `shared` for environments other people use), a
login pointer, selectors to mask and project references. It never holds
credentials: a secret-looking key makes the skill stop and the hook ask for
everything. Details in
[`skills/ui-evidence/references/config.md`](skills/ui-evidence/references/config.md).

Project procedures (how to start the app, app-specific grid components, test
data) are not fields: they go in project reference files listed under
`references`, kept in the project, not in this plugin.

## The guard hook

`browser_run_code_unsafe` runs arbitrary JavaScript in the MCP's Node process.
Under Claude Code, a hook that stays silent leaves the call to the normal
permission flow, so the guard always decides:

| Call | Decision |
| --- | --- |
| `browser_evaluate` with no network token and no `filename` | allow |
| `browser_evaluate` using `fetch`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `axios`, `.ajax`, or saving to a `filename` | ask |
| `browser_run_code_unsafe` with a script that passes every rule below | allow |
| `browser_run_code_unsafe`, anything else | ask |

### Where scripts may live

Only `<root>/<evidenceRoot>/<folder>/scripts/<name>.js`, resolved with
`realpath` (so `..` and symlinks that leave the folder ask), passed as an
absolute `filename`. Inline `code`, a relative `filename` (the MCP resolves it
against its own workspace, which may not be the session's), a missing file or
a config problem all ask.

The MCP itself refuses a `filename` outside its workspace and its output
folder (`File access denied ... outside allowed roots`), seen on 0.0.83. With
the default `evidenceRoot` (`.playwright-mcp/evidence`) evidence sits in the
output folder; when the session's working directory is below `<root>`, start
the MCP with `--output-dir <root>/.playwright-mcp`.

### Rules on the script's text

| Rule | Asks when the script has |
| --- | --- |
| Escape | `require(`, `import(`, a line-leading `import`, `child_process`, `process`, `eval(`, `Function(`, `globalThis`, `module`, `__dirname`, `__filename`, `Buffer`, `constructor`, `__proto__`, `Reflect` |
| Network | `fetch`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `axios`, `.ajax` |
| Direct HTTP and browser state | `newContext`, `.route(`, `routeFromHAR`, `routeWebSocket`, `.request[`, `method:`, `browserType`, `newCDPSession`, `connectOverCDP`, `storageState`, `cookies`, `addCookies`; `.request` used other than `.request.get(`, `.request.head(`, `.request()` |
| Obfuscation | member access by string (`obj['name']`), which would hide the tokens above |
| Evidence path | `const EVIDENCE_DIR = '<abs>'` missing, declared more than once, or not equal to the script's evidence folder; any `path` not written as ``path: `${EVIDENCE_DIR}/...` `` or `path: EVIDENCE_DIR + '/...'`; `..` anywhere |
| Other file sinks | `saveAs(` (downloads), `setInputFiles(` (local files into the page) |
| Stop guarantee | `screencast.start` without `screencast.stop` and a `finally` |
| Secrets | a fill or type (`fill(`, `type(`, `pressSequentially(`, `insertText(`) on a line naming a password, `pwd` or secret, recording or not: secrets are typed only through `browser_type` |

The escape and network token lists come from an earlier guard written for
another agent; this port rebuilt them from that guard's documented token list
rather than copying its regexes. Changes since: word boundaries on bare
identifiers, plus the obfuscation, browser-state and `constructor` rules,
each motivated by a test in `hooks/test.sh`.

### Honest limits

A lexical filter, not a sandbox; a deliberate bypass is possible (for example
building a token from pieces in a way the rules do not anticipate). Not
covered: `page.goto` to any host; the file changing between the check and the
run; MCP tools other than the two (`browser_file_upload`,
`browser_take_screenshot`'s own output, `browser_route`, the cookie and storage
tools, the `devtools` video tools). Hardening left for later: a host allowlist
from `environments[].url`; trusting the hook input's `mcp_server.source`
(Claude Code 2.1.274+) instead of the tool-name prefix; a separate browser
profile or container for the MCP.

## Tests

```
bash plugins/ui-evidence/hooks/test.sh
```

135 checks in a temp dir with a temp config, each under both tool-name shapes
(`mcp__playwright__…` and `mcp__plugin_playwright_playwright__…`): the
regression (inline `require("fs")` under the Claude Code name used to pass
silently, now asks), the documented harness taken straight from
`recording.md` (allow, with `hookEventName` present), every token, every
evidence-path, sink, stop and secret rule with passing and asking fixtures,
`..` and symlink escapes, relative `filename`, invalid stdin JSON, config
discovery and config sanity. Runs in CI.

## Verified facts

Answers to the questions this plugin was built on, with how each was settled.

1. **Hook input and output.** Input carries `tool_name`, `tool_input`, `cwd`,
   `permission_mode` and, for MCP tools, `mcp_server` (2.1.274+).
   `hookSpecificOutput.hookEventName` is required. Source: Claude Code hooks
   docs.
2. **Permission semantics.** A hook `allow` skips the prompt (except for
   actions no mode auto-approves); settings `deny` and `ask` rules are still
   evaluated whatever the hook returns, so your `deny` rules win. A hook `ask`
   **does** force a prompt in `auto` mode: the classifier can still deny but
   cannot approve silently (since Claude Code 2.1.211). With several hooks,
   `deny` > `defer` > `ask` > `allow`. Source: hooks docs; not exercised in a
   live session here.
3. **Tool names.** `mcp__<server>__<tool>`; a plugin-provided server is
   `mcp__plugin_<plugin>_<server>__<tool>`. The matcher
   `^mcp__.*playwright.*__browser_(run_code_unsafe|evaluate)$` covers both.
   Source: hooks docs; both shapes in the tests.
4. **Playwright version.** `@playwright/mcp@latest` is 0.0.83 and runs
   Playwright 1.64.0-alpha, which has `page.screencast` (`start`, `stop`,
   `showActions`, `hideActions`, `showChapter`, `showOverlay`). Pin the MCP
   version. Source: installed and inspected.
5. **Typed values in action titles.** Yes. `showActions` titles render
   `Fill "<value>"` and `Type "<value>"` in clear text, also for
   `type=password` inputs; after `hideActions()` no title is drawn. Source:
   recorded and inspected frames on Playwright 1.64.0-alpha.
6. **`filename` outside the MCP's roots.** Refused: `File access denied: … is
   outside allowed roots`, roots being the MCP's workspace and its output
   folder, unless `--allow-unrestricted-file-access`. Paths written by the
   script itself (`page.screenshot({ path })`, `screencast.start({ path })`)
   are not checked by the MCP, which is why the guard checks them. Source: run
   against `@playwright/mcp@0.0.83` over stdio, and its source.
7. **Invocation and updates.** The skill is `/ui-evidence:ui-evidence` (plugin
   prefix, as for every plugin here). Installed plugins run from a copy in
   `~/.claude/plugins/cache`; after editing a local clone, hook changes need
   `/reload-plugins` or a reinstall. Source: this repository's README; not
   re-tested here.
8. **Attachment limits.** GitHub: 10 MB per video on free plans, 100 MB on
   paid ones (Playwright's reference). Jira Cloud: 1 GB per file by default,
   adjustable by a site admin up to 2 GB (Atlassian docs).

## Acceptance status

Run here, in a scratch workspace against a local page with
`@playwright/mcp@0.0.83` over stdio, headless Chromium:

- the guard allowed the documented harness at its real path; the MCP ran it,
  returned per-case `before`/`after` values with ISO times, and wrote
  `run-1.webm` (chapter card and action titles visible in the frames) and the
  case screenshot;
- a script with a forced error returned the error in its result and still
  left a finished `run-2.webm` (the `finally` stopped the recording);
- a `filename` outside the MCP's roots was refused by the MCP.

Not run here: installing the plugin into a Claude Code session, the skill
end to end with an agent (case table, approval, write-up), and the prompt
behaviour per permission mode (`default` and `auto`); item 2 above rests on the
docs. Run those once on a public demo page such as
`https://demo.playwright.dev/todomvc` after installing.
