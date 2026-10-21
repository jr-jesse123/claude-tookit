# Recording: native video or script, safe video, write-up

How step 3 of the skill records a run. Two modes, same evidence:

- **Native** (default): drive the page with the Playwright MCP's standard
  tools (`browser_click`, `browser_type`, `browser_snapshot`, ...) and record
  with its video tools (`browser_start_video` and the rest). Needs the MCP
  started with `--caps devtools`; without it the video tools do not exist.
  The run adapts as it goes, and a failing step does not end the recording.
- **Script**: write the whole group of cases as one script on the harness
  below and run it with `browser_run_code_unsafe`. Use it for an identical
  re-run (the same steps before and after a fix, for contrast), for
  screenshots that need `mask`, and when the MCP runs without
  `--caps devtools`.

The guard lets both through without a prompt when files stay in the
evidence folder, and asks otherwise (see the plugin README).

## Native recording

What follows was observed on `@playwright/mcp@0.0.83` (Playwright
1.64.0-alpha). The MCP's tool names and behaviour change between versions:
after changing the pinned version, check that the tools below still exist
(`--caps devtools`, then list the tools) before relying on this section.

### Sequence

1. **Before recording**: login, setup and data done; long waits (jobs,
   scheduled state changes) over. Check on the live page, with
   `browser_snapshot` or `browser_find`, every selector the run will use,
   above all the reads that follow a write. A selector taken from reading the
   app's code and never seen on the page is a guess.
2. `browser_resize` to the size the run needs (1280x720 unless the screen
   needs more).
3. Take the clock (`date -u +%Y-%m-%dT%H:%M:%S.%3NZ` through the Bash tool)
   and log `start recording`.
4. `browser_start_video` with:
   - `filename`: the **absolute** path `<evidence>/<run>.webm`, for example
     `<evidence>/run-1.webm` or `<evidence>/run-1-part2.webm`. The guard
     allows only `<evidence folder>/<name>.webm` and asks for anything else.
   - `size`: equal to the viewport set in step 2. Without `size` the video is
     scaled down to 800 pixels wide; with a size larger than the viewport the
     page fills only part of the frame and the rest is grey.
   - `cursor: true`: an animated pointer travels to each action, and no
     action title is drawn (see "Action titles" below).
5. Per case:
   - `browser_video_chapter` with `title: "C1 – <action>"` and
     `duration: 1500`.
   - **Read before**: `browser_snapshot` with `target` on the element under
     test, `browser_find`, or `browser_wait_for` with `text`. The text the
     tool returns is the value; copy it into the timeline as returned.
   - **Act** with the standard tools.
   - **Wait for the state**, not for time: `browser_wait_for` with `text`
     (or `textGone`) when the outcome has a text; a fixed wait only as the
     fallback.
   - **Read after**, the same way as before.
   - `browser_take_screenshot` with an absolute `filename`
     (`<evidence>/<run>-C1-<what>.png`) and `target` to frame the part under
     test.
   - Take the clock and log the case's lines.
6. `browser_stop_video`. It lists one file per page the run recorded (see
   "Tabs and popups"). Then check each file exists and is not empty
   (`ls -l`; `ffprobe` when installed): the result is not proof (see
   "When the recording is lost").

A failing step returns an error and the recording keeps going: read the
page, then go on with the next case or stop, and report the error. **Stop the
recording before ending the turn**, and before returning from a delegated
run, whatever the reason.

### Parts

The recording lives in memory until `browser_stop_video` (below), so record
in short parts: one per case or per small group, each with its own
`start`/`stop`.

- An **irreversible write** gets a part of its own, recorded only after its
  selectors and the reads after it were checked on the page (step 1).
- Waits longer than a few seconds are not recorded: stop, wait, start the
  next part.
- Name parts `run-1.webm`, `run-1-part2.webm`, ... and list every part in the
  README.

### When the recording is lost

| What happens | Result (seen on 0.0.83) |
| --- | --- |
| `browser_stop_video` | The file is written now, not before: until the stop it exists only in the MCP's temporary folder. |
| The browser dies mid-recording (crash, killed, machine hang) | Nothing is saved. The next `browser_stop_video` answers `No videos were recorded.` and the browser restarts on the next call. A script's `finally` would not help here either: it records the same way. |
| The MCP process ends mid-recording (`/mcp` restart, session end) | A 0-byte, unplayable file at the path. |
| `browser_close` mid-recording | The file is saved, yet the next `browser_stop_video` answers `No videos were recorded.`. |
| `browser_start_video` failed (for example ffmpeg missing) | `browser_stop_video` still lists the file, which does not exist. |
| `browser_start_video` while recording | Error `Video recording has already been started.`; the first recording goes on. |
| `browser_stop_video` with nothing recording | `No videos were recorded.` |

Hence: short parts, a file check after every stop, and a part re-recorded
(as `-partN`) when its file is missing or empty.

### Action titles

`browser_video_show_actions` draws a title for each action, such as
`Click locator('[data-testid="save"]')` or `Fill "<value>" locator(...)`,
and delays each action by its `duration`. **The title shows the typed value
in clear text, also when the value comes from the MCP's `--secrets` file**:
`browser_type` with a secret's name filmed `Fill "<the secret's value>"`,
while the tool's answer showed only the name.

- Default: no titles (`cursor: true` on start, no `show_actions`).
- Titles on (`browser_video_show_actions`, `duration` 600 to 1000): call
  `browser_video_hide_actions` before every `browser_type`,
  `browser_fill_form` or `browser_press_sequentially`, whatever the field,
  and turn them on again after. `style: { title: "display: none" }` also
  hides them.
- Secrets are still typed only outside the recording.

### Tabs and popups

The recording covers every page of the browser context, not one tab:

- a popup or a new tab opened while recording gets its own file,
  `<name>-1.webm`, `<name>-2.webm`, ..., at the same `size` (grey around a
  smaller window), with the cursor but **without action titles**;
- `browser_video_chapter` and the action titles act on the selected tab only
  (`browser_tabs` with `select`);
- the first file keeps recording its own tab, which stands still while the
  run works in another one.

Say in the README which file covers which case. Iframes are part of their
page and are filmed with it.

### Reads, proof and times

- **A screenshot shows; a returned value proves.** The verdict rests on the
  text a read tool returned, copied into the timeline.
- Appearance cases (colour, weight, visibility) need computed styles, which
  only code reads: `browser_evaluate` with a page-only function
  (`() => getComputedStyle(...).color`). It is code: say what it reads before
  using it. The guard allows it without network access or `filename`.
- Times: the clock taken through the Bash tool right after a read is close
  to it, not from it; timeline lines from native runs are marked `~`. The
  clock taken at step 3 gives video offsets (offset = time − start).

### Screenshots

`browser_take_screenshot` has no `mask`. When something on screen matches
`maskSelectors`, frame the capture with `target` so it stays out, or take that
screenshot from a script with the harness's `mask`. Video cannot be masked in
either mode.

### Other tools `--caps devtools` turns on

| Tool | What it does | In an evidence run |
| --- | --- | --- |
| `browser_highlight` / `browser_hide_highlight` | A persistent outline on an element, also on video. | Allowed by the MCP's normal permissions; declare it in the README and remove it after. |
| `browser_start_tracing` / `browser_stop_tracing` | A Playwright trace in `.playwright-mcp/traces/`. | Do not use. It wrote the `Authorization` header (bearer token) and values typed through `--secrets` in clear text. The guard asks. |
| `browser_annotate` | Opens the Playwright dashboard and waits for a person to draw on the page. | Do not use; the guard asks. |
| `browser_start_recording` / `browser_stop_recording` | Records a person's actions as Playwright code. Not video. | Not needed; the guard asks. |
| `browser_resume` | Resumes a paused Playwright debugger. | Not needed; the guard asks. |

## Script recording

### Running a script

- Write it to `<evidence>/scripts/<run>-<what>.js`, for example
  `scripts/run-1-filters.js`. Scripts stay in the folder as the record of what
  ran.
- Run it with `browser_run_code_unsafe` and `filename` set to the script's
  **absolute** path. Never pass `code`.
- The Playwright MCP reads `filename` only from inside its own roots: the
  workspace it was started in, and its output folder (`.playwright-mcp/`
  under that workspace unless `--output-dir` says otherwise). Anything else
  fails with `File access denied ... outside allowed roots`. If the session
  works in a nested folder while the evidence root sits higher up, start the
  MCP with `--output-dir <root>/.playwright-mcp` rather than
  `--allow-unrestricted-file-access`.
- The script is evaluated in a bare JavaScript context: no `require`, no
  `import`, no `process`. It gets `page` and returns plain JSON.

### The harness

Copy it into each script and fill in the cases. Keep it free of the tokens the
guard asks on: `require(`, `import`, `process`, `Buffer`, `globalThis`,
`eval(`, `Function(`, `module`, `__dirname`, `constructor`, `fetch`,
`method:`, `newContext`, `.route(`, `storageState`, `cookies`, `saveAs(`,
`setInputFiles(`, `..`, and `obj['name']` access. The word `path` may appear
only as `path: \`${EVIDENCE_DIR}/...\`` (or `path: EVIDENCE_DIR + '/...'`).

```js
async (page) => {
  // Must equal this script's evidence folder (the parent of scripts/). The guard checks it.
  const EVIDENCE_DIR = '/abs/evidence/folder';
  const RUN = 'run-1';
  // maskSelectors from the config, plus any case-specific ones.
  const MASK = [];
  const mask = () => MASK.map((s) => page.locator(s));
  const at = () => new Date().toISOString();
  const steps = [];
  // Case-specific read of the state under test. Return plain JSON.
  const read = async () => page.evaluate(() => null);

  // Video size = viewport size; a mismatch letterboxes the video.
  const size = page.viewportSize() || { width: 1280, height: 800 };
  await page.screencast.start({ path: `${EVIDENCE_DIR}/${RUN}.webm`, size });
  try {
    await page.screencast.showActions({ duration: 600, position: 'top-right' });

    // One block per case.
    await page.screencast.showChapter('C1 – <action>', { duration: 1500 });
    const before = await read();
    // ... the action, with real mouse moves for drags (down, ~15 moves, short wait, up) ...
    await page.waitForTimeout(1000);
    const after = await read();
    await page.screenshot({ path: `${EVIDENCE_DIR}/${RUN}-C1-<what>.png`, mask: mask() });
    steps.push({ id: 'C1', at: at(), before, after });
  } catch (e) {
    steps.push({ at: at(), error: String(e) });
  } finally {
    await page.screencast.stop();
  }
  return steps;
}
```

Notes on the parts:

- `read()` returns the state the case is about (a value, a count, a computed
  style, an order of items), read from the DOM. The verdict compares `before`
  and `after` against the case's Expected; the screenshot illustrates it.
- Waits: after an action, wait for the state, not for time, when a locator or
  `page.waitForFunction` can express it; the fixed `waitForTimeout(1000)` is
  the fallback. When a read and the screenshot disagree, re-run with a longer
  wait before concluding.
- Screenshots: `clip` or `locator.screenshot()` to frame the part under test;
  always pass `mask` when anything on screen matches `maskSelectors`.
- Errors land in `steps` with their time, and `finally` stops the recording,
  so a failing case still leaves a playable video.

## Techniques by situation

For both modes. Use one only when the case runs into its situation; none assumes the app has
any particular kind of screen or component.

- **The case is about appearance** (colour, weight, visibility, size): prove
  it with `getComputedStyle` values of the properties in question, not class
  names. A class says what the code intended, not what the user sees.
- **The content is longer than the viewport and may be virtualised** (only
  what is near the viewport exists in the DOM): a DOM read returns what is
  rendered, not what exists. Prefer a count or total the UI itself shows;
  otherwise scroll in steps and collect items by a stable key (an id, a
  data attribute, an ARIA index) until nothing new appears, then scroll back.
- **The action is a drag** (reorder, resize, move): many drag-and-drop
  implementations ignore a jump from source to target. Natively, try
  `browser_drag` and read the result; if the order or size did not change,
  do that case from a script with `page.mouse` and real moves (`move` to the
  source, `down`, about 15 `move` steps, a short wait, `up`). Read the order
  or size before and after; the picture alone does not prove the move.
- **The page holds several instances of the same component**: scope every
  query to the instance under test first, and name it in the README.

How to read a specific library or component the app uses is project
knowledge: put it in a project reference (see `config.md`).

## Safe video

| Risk | Rule |
| --- | --- |
| Credentials on video | Start recording only after login. If the session expires mid-run, stop the recording, log in outside it, start a new part (`run-1-part2.webm`). Never type a secret while recording. |
| Typed text in action titles | Titles render the typed value in clear text, `Fill "<value>"` and `Type "<value>"`, even for `type=password` fields and for values taken from the MCP's `--secrets` file (seen on Playwright 1.64). Natively: no titles by default; with titles on, `browser_video_hide_actions` before every typing tool. In a script: `page.screencast.hideActions()` before any fill whose text must not be filmed and `showActions(...)` again after, or `style: { title: 'display: none' }`. Secrets are never typed from a script at all: only `browser_type`, outside the recording. |
| Secrets and tokens in a trace | No tracing in an evidence run: a trace keeps request headers and typed values in clear text. |
| PII in screenshots and video | Screenshots: the script's `mask` with the config's `maskSelectors`; natively, frame with `target` to leave them out. Video cannot be masked: prefer test entities, and never film real customer data when a test entity exists. |
| Files written anywhere | Script: every `path:` derives from `EVIDENCE_DIR`. Native: absolute `filename`s in the evidence folder. |
| Recording left running or lost | Script: `screencast.stop()` in `finally`; errors returned, not swallowed. Native: stop before ending the turn or returning; short parts; check each file after the stop. Neither mode saves a recording when the browser dies. |
| Pages outside the frame | Popups and new tabs go to their own files without action titles (native) or are not recorded at all (a script records only its `page`). Name in the README what each file covers. |
| Writes to shared environments | Declared in step 1 of the skill, confirmed one by one when they happen. An irreversible write gets its own part, with its selectors checked on the page first. |
| Oversized videos | `size` equal to the viewport (1280x720 unless the screen needs more; set it with `browser_resize`), chapters only for cases, waits not recorded. About 30 KB/s at 25 fps on simple screens. Attachment limits where the user will post: GitHub 10 MB on free plans, 100 MB on paid ones; Jira Cloud's default is 1 GB per file, and a site admin can change it (up to 2 GB). |
| Uploading | Never. The user posts. |

## Captions and overlays

| Script | Native | What |
| --- | --- | --- |
| `page.screencast.showChapter(title, { description, duration })` | `browser_video_chapter` | The chapter card between cases. One per case, titled with the case id. |
| `page.screencast.showOverlay(html, { duration })` | none | A caption over the page, for example to point at the cell under test. Returns a disposable; without `duration` it stays until disposed. |
| `page.screencast.hideActions()` / `showActions(options)` | `browser_video_hide_actions` / `browser_video_show_actions` | Action titles off and on. |
| injected CSS | `browser_highlight` / `browser_hide_highlight` | An outline on the element under test. |

Anything the run adds to the picture (captions, highlights, injected CSS)
is declared in the README's run section, so nobody mistakes it for the app's
own UI.

## README and timeline

`README.md` in the evidence folder: a short header (what is verified, ticket
or label) written once, then one section per run, appended, never rewritten:

```markdown
## Run 1 — 2026-10-19 14:02

- Environment: local, https://localhost:3000, branch `feature/x` at `abc1234`
  (or the deployed version for a shared environment)
- Data: test entity "Demo list" (id 42)
- Mode: native, steps from cases.md (or: script, scripts/run-1-filters.js)
- Files: run-1.webm (C1–C2), run-1-1.webm (C2's popup), run-1-part2.webm (C3)
- Added to the picture: chapter cards; a red outline on the cell under test (C3)

| ID | Expected | Result | Evidence |
| --- | --- | --- | --- |
| C1 | ... | PASS | run-1.webm 00:03, run-1-C1-sorted.png |
| C2 | ... | FAIL: returned `3`, expected `4` | run-1-C2-count.png |
| C3 | ... | not covered: needs an admin account | — |

Probes: ...
Findings outside the change: ...
Writes made: none (or each write with its id, for cleanup).
```

`timeline.txt`: one line per step. Times returned by a script are written as
returned. Any other time is marked `~`: the clock taken after a native read,
a manual step, an estimate. Native reads are copied as the tool returned them.

```text
2026-10-19T14:02:11.204Z  run-1  start recording
2026-10-19T14:02:13.870Z  run-1  C1 before {"rows":12}
2026-10-19T14:02:15.012Z  run-1  C1 after  {"rows":13}
~2026-10-19T14:05:02Z    run-2  C2 before snapshot: - text: Used in 9 Events
~2026-10-19T14:05:09Z    run-2  C2 after  snapshot: - text: Used in 10 Events
~2026-10-19T14:05        manual login on staging
```
