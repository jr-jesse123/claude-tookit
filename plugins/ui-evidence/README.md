# ui-evidence

Verify UI behaviour in a real browser through the Playwright MCP and leave
evidence a reviewer, QA or PM can trust without re-running it:

- test cases agreed with you before the browser opens;
- a WebM video per run, one chapter per case, recorded safely;
- per-case screenshots, values read from the DOM before and after each
  action, timestamps;
- a `README.md` with a PASS / FAIL / not covered table, and a `timeline.txt`;
- on request, before/after images with highlights and comment text for a
  ticket or PR.

Nothing is uploaded, attached or posted. You get files and text; you post them.

| Component | Name | What it does |
| --- | --- | --- |
| skill | `/ui-evidence:ui-evidence <ticket-or-label> [what to verify]` | The workflow: configure, agree cases, prepare, run and record, before/after images, restore, write up and hand over. Invoked by you, or by a workflow that hands it an approved case file (a delegated run, below); its description keeps it from triggering on a quick look at a page. |
| reference | `references/recording.md` | Native recording with the MCP's video tools (sequence, parts, what loses a recording, action titles, tabs), the script harness, techniques by situation (appearance, virtualised content, drags, repeated components), the safe-video rules, README and timeline format. |
| reference | `references/config.md` | `.claude/ui-evidence.json`: discovery, fields, defaults. |
| reference | `references/compose.md` | Before/after captures, compose page, comment text. |

## Requirements

- A Playwright MCP server, configured by you (this plugin does not ship one).
  Pin its version: the skill and the harness depend on its tool names and on
  `page.screencast`, which `@playwright/mcp@latest` provides today through
  Playwright 1.64.0-alpha (`@playwright/mcp@0.0.83`). For example
  `npx @playwright/mcp@0.0.83`.
- For native recording, the default mode: `--caps devtools`. Without it the
  video tools (`browser_start_video`, `browser_stop_video`,
  `browser_video_chapter`, `browser_video_show_actions`,
  `browser_video_hide_actions`) do not exist and only script mode works. The
  same flag also turns on `browser_highlight`, `browser_hide_highlight`,
  `browser_start_tracing`, `browser_stop_tracing`, `browser_annotate`,
  `browser_resume`, `browser_start_recording` and `browser_stop_recording`;
  the skill does not use tracing, annotate, resume or action recording. After moving the pin, start the new version with
  `--caps devtools`, list its tools and compare the names with
  `references/recording.md` before relying on it.
- Recommended MCP options: `--secrets <dotenv file>` so `browser_type` can type
  a secret by name without its value entering the conversation, and
  `--output-dir <root>/.playwright-mcp` when sessions start in folders below
  the evidence root (the MCP refuses a `filename` outside its workspace and
  its output folder: `File access denied ... outside allowed roots`).

## Delegated runs

Another skill or a subagent can run the browser part on its own: the main
session agrees the cases and the writes with you, writes them with your
approval to `<evidence folder>/cases.md`, and the delegated run works from
that file. A subagent cannot ask you questions, so in a delegated run the file
stands in for step 1's yes and for each write's yes, and the run stops and
returns instead of asking whenever something is not in it: no approval line,
a case to change, a write not listed, a login that needs a person, no config.
The skill's "Delegated runs" section has the exact rules. A subagent preloads
the skill with `skills: [ui-evidence:ui-evidence]` in its frontmatter.

## Configuration

Optional. One file, `.claude/ui-evidence.json`, found through
`$UI_EVIDENCE_CONFIG` or by walking up from the working directory, read by
the skill. It names the evidence folder, the environments
(with `role` before/after and `shared` for environments other people use), a
login pointer, selectors to mask and project references. It never holds
credentials: a secret-looking key makes the skill stop. Details in
[`skills/ui-evidence/references/config.md`](skills/ui-evidence/references/config.md).

Project procedures (how to start the app, how to read the components and
screens the app has, test data) are not fields: they go in project reference files
listed under `references`, kept in the project, not in this plugin.

## Permissions

The plugin ships no hook: Playwright calls (`browser_run_code_unsafe`,
`browser_evaluate`, the video tools) go through Claude Code's normal
permission flow. Allow or deny them with your own permission rules.

## Troubleshooting

- `Browser is already in use for …/.playwright-mcp/profile, use --isolated`
  after restarting the MCP (`/mcp`): the previous Chromium is still running
  and holds the profile. Find it (`ps -eo pid,etime,cmd | grep chromium`),
  check that it is this workspace's Playwright browser, and end it.
- `Executable doesn't exist at …/ffmpeg-<rev>/ffmpeg-linux` from
  `browser_start_video`: Playwright's ffmpeg is not installed for the
  MCP's Playwright version (`npx playwright install ffmpeg` with that
  version). The stop after it still lists a file; there is none.
- Playwright's own ffmpeg can extract a frame to check a video
  (`ffmpeg -ss <seconds> -i run-1.webm -frames:v 1 frame.png`); it lacks
  most filters.

## Verified facts

Answers to the questions this plugin was built on, with how each was settled.

1. **Playwright version.** `@playwright/mcp@latest` is 0.0.83 and runs
   Playwright 1.64.0-alpha, which has `page.screencast` (`start`, `stop`,
   `showActions`, `hideActions`, `showChapter`, `showOverlay`). Pin the MCP
   version. Source: installed and inspected.
2. **Typed values in action titles.** Yes. `showActions` titles render
   `Fill "<value>"` and `Type "<value>"` in clear text, also for
   `type=password` inputs; after `hideActions()` no title is drawn. Source:
   recorded and inspected frames on Playwright 1.64.0-alpha.
3. **`filename` outside the MCP's roots.** Refused: `File access denied: … is
   outside allowed roots`, roots being the MCP's workspace and its output
   folder, unless `--allow-unrestricted-file-access`. Paths written by the
   script itself (`page.screenshot({ path })`, `screencast.start({ path })`)
   are not checked by the MCP. Source: run
   against `@playwright/mcp@0.0.83` over stdio, and its source.
4. **Invocation and updates.** The skill is `/ui-evidence:ui-evidence` (plugin
   prefix, as for every plugin here). Installed plugins run from a copy in
   `~/.claude/plugins/cache`; after editing a local clone, changes may need
   `/reload-plugins` or a reinstall. Source: this repository's README; not
   re-tested here.
5. **Attachment limits.** GitHub: 10 MB per video on free plans, 100 MB on
   paid ones (Playwright's reference). Jira Cloud: 1 GB per file by default,
   adjustable by a site admin up to 2 GB (Atlassian docs).

6. **Native video tools.** `@playwright/mcp@0.0.83` has `browser_start_video`
   (`filename`, `size`, `fps`, `cursor`), `browser_stop_video`,
   `browser_video_chapter`, `browser_video_show_actions` and
   `browser_video_hide_actions`, listed only with `--caps devtools`. The
   recording covers the whole browser context: a popup or new tab gets its
   own file (`<name>-1.webm`, ...) without action titles; chapters and titles
   act on the selected tab. Without `size` the video is scaled to 800 pixels
   wide. `cursor: true` draws a pointer and hides action titles. A second
   start errors; a stop with nothing recording answers `No videos were
   recorded.`. `filename` goes through the same roots check as item 3, and
   its extension is not checked. Source: the MCP's source and runs over
   stdio, below.
7. **When a native recording is saved.** Only at `browser_stop_video`: the
    video is kept in a temporary folder and copied to `filename` then. A
    killed browser leaves nothing; an MCP that exits mid-recording leaves a
    0-byte file; `browser_close` saves the file but the next stop answers
    `No videos were recorded.`; after a failed start, the stop still lists a
    file that does not exist. Source: runs below. A script records the same
    way, so its `finally` covers script errors, not a dead browser (read in
    the source, not run).
8. **Secrets in native action titles.** `browser_type` with the name of a
    `--secrets` entry filled the real value, and with
    `browser_video_show_actions` on the video showed `Fill "<value>"`, while
    the tool's answer showed only the name. `browser_video_hide_actions` and
    `style.title: "display: none"` removed the title. Source: frames of the
    runs below, with a fake secret.
9. **Tracing.** `browser_start_tracing` wrote, under
    `.playwright-mcp/traces/`, the `Authorization: Bearer …` header of a page
    request in the `.network` file and the value of a `--secrets` entry typed
    with `browser_type` in the `.trace` file, both in clear text. Source: runs
    below.
10. **Annotations.** The MCP marks the video and tracing tools and
    `browser_annotate` `readOnlyHint: true`; `browser_annotate` spawns a
    detached dashboard process and waits for a person. Source: the MCP's tool
    list and source.

## Acceptance status

Run here, in a scratch workspace against a local page with
`@playwright/mcp@0.0.83` over stdio, headless Chromium:

- the MCP ran the documented harness at its real path,
  returned per-case `before`/`after` values with ISO times, and wrote
  `run-1.webm` (chapter card and action titles visible in the frames) and the
  case screenshot;
- a script with a forced error returned the error in its result and still
  left a finished `run-2.webm` (the `finally` stopped the recording);
- a `filename` outside the MCP's roots was refused by the MCP.

Native recording, run here with `@playwright/mcp@0.0.83 --caps devtools`
over stdio from a small MCP client, headless Chromium 1194 (not the 1247 the
pin expects; `--no-sandbox` because the container had no sandbox), against a
local page with a popup, a new-tab link and an iframe: items 6 to 9 above.

Not run here: installing the plugin into a Claude Code session, the skill
end to end with an agent (case table, approval, write-up), and a subagent preloading the skill and loading the deferred video tools
through `ToolSearch`. Run those once on a public demo page such as
`https://demo.playwright.dev/todomvc` after installing.
