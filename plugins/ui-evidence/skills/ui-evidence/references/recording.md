# Recording: harness, safe video, write-up

How step 3 of the skill writes and runs its scripts. The harness below is
what the plugin's guard expects; a script built on it runs without a prompt,
and any departure from it asks.

## Running a script

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

## The harness

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

Use one only when the case runs into its situation; none assumes the app has
any particular kind of screen or component.

- **The case is about appearance** (colour, weight, visibility, size): prove
  it with `getComputedStyle` values of the properties in question, not class
  names. A class says what the code intended, not what the user sees.
- **The content is longer than the viewport and may be virtualised** (only
  what is near the viewport exists in the DOM): a DOM read returns what is
  rendered, not what exists. Prefer a count or total the UI itself shows;
  otherwise scroll in steps and collect items by a stable key (an id, a
  data attribute, an ARIA index) until nothing new appears, then scroll back.
- **The action is a drag** (reorder, resize, move): use `page.mouse` with real
  moves (`move` to the source, `down`, about 15 `move` steps, a short wait,
  `up`). Many drag-and-drop implementations ignore a jump from source to
  target. Read the order or size before and after; the picture alone does not
  prove the move.
- **The page holds several instances of the same component**: scope every
  query to the instance under test first, and name it in the README.

How to read a specific library or component the app uses is project
knowledge: put it in a project reference (see `config.md`).

## Safe video

| Risk | Rule |
| --- | --- |
| Credentials on video | Start the screencast only after login. If the session expires mid-run, stop the screencast, log in outside the recording, start a new part (`run-1-part2.webm`). Never type a secret while recording. |
| Typed text in action titles | `showActions` titles render the typed value in clear text, `Fill "<value>"` and `Type "<value>"`, even for `type=password` fields (seen on Playwright 1.64). Call `page.screencast.hideActions()` before any fill whose text must not be filmed and `showActions(...)` again after, or pass `style: { title: 'display: none' }`. Secrets are never typed from a script at all: only `browser_type`, outside the recording. |
| PII in screenshots and video | `mask` with the config's `maskSelectors` on every screenshot. Video cannot be masked: prefer test entities, and never film real customer data when a test entity exists. |
| Files written anywhere | Every `path:` derives from `EVIDENCE_DIR`. |
| Recording left running | `screencast.stop()` in `finally`; errors returned, not swallowed. |
| Writes to shared environments | Declared in step 1 of the skill, confirmed one by one when they happen. |
| Oversized videos | The viewport's size (the MCP's default is 1280x720; set it with `browser_resize` before the run if the screen needs more), chapters only for cases, one video per run. Attachment limits where the user will post: GitHub 10 MB on free plans, 100 MB on paid ones; Jira Cloud's default is 1 GB per file, and a site admin can change it (up to 2 GB). |
| Uploading | Never. The user posts. |

## Captions and overlays

- `page.screencast.showChapter(title, { description, duration })`: the
  chapter card between cases. One per case, titled with the case id.
- `page.screencast.showOverlay(html, { duration })`: a caption over the page,
  for example to point at the cell under test. Returns a disposable; without
  `duration` it stays until disposed.
- `page.screencast.hideActions()` / `showActions(options)`: turn the action
  titles off and on.

Anything the script adds to the picture (captions, highlights, injected CSS)
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
- Script: scripts/run-1-filters.js
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

`timeline.txt`: one line per step, times as returned by the scripts. Any time
not returned by a script (a manual step, an estimate) is marked `~`.

```text
2026-10-19T14:02:11.204Z  run-1  start recording
2026-10-19T14:02:13.870Z  run-1  C1 before {"rows":12}
2026-10-19T14:02:15.012Z  run-1  C1 after  {"rows":13}
~2026-10-19T14:05        manual login on staging
```
