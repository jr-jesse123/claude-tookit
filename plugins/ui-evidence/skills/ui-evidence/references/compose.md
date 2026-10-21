# Before/after images

For a ticket or PR comment: the same thing shown before and after the change,
side by side or one above the other, with the difference highlighted. Made
only when the user asks.

## 1. Capture the two states

- **Same entity.** Open the same record, list or screen in the environment
  with `role: "before"` and the one with `role: "after"`, one tab each
  (`browser_tabs` → new). If the two environments do not share data, pick
  entities that are equivalent for the case and say so in the README.
- **Same frame.** Same viewport size, same scroll position, same open panels,
  same sort and filters. Capture the same region in both: `locator.screenshot()`
  on the same container, or `page.screenshot({ clip })` with the same box.
- **Highlight only for the capture.** Inject the highlight just before the
  screenshot and remove it right after, so the page is left as found:

  ```js
  const style = await page.addStyleTag({ content: '.target { outline: 3px solid #e5484d; outline-offset: 2px; }' });
  await page.locator('.target').first().screenshot({ path: `${EVIDENCE_DIR}/compose/02-after.png` });
  await style.evaluate((el) => el.remove());
  ```

  Prefer `outline` (it does not shift layout) over `border`. With
  `--caps devtools`, `browser_highlight` on the element and
  `browser_hide_highlight` after do the same without a script. For a region with
  no single element, inject an absolutely positioned overlay `div` at the
  element's bounding box and remove it the same way.
- Mask `maskSelectors` in both captures.
- Files go to `<evidence>/compose/`, numbered in the order they will appear
  in the comment: `01-before.png`, `02-after.png`, `03-detail.png`.

## 2. Compose

When one image should show both states, write a small HTML page in
`compose/` that lays the two captures out with labels, open it and capture it
with `fullPage`:

```html
<!doctype html>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 16px; font: 14px system-ui, sans-serif; background: #fff; }
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
  figure { margin: 0; }
  figcaption { font-weight: 600; margin-bottom: 6px; }
  img { max-width: 100%; border: 1px solid #ddd; }
</style>
<div class="pair">
  <figure><figcaption>Before (staging, main)</figcaption><img src="01-before.png"></figure>
  <figure><figcaption>After (local, branch)</figcaption><img src="02-after.png"></figure>
</div>
```

The Playwright MCP blocks `file:` URLs, and a script cannot read the images
to inline them. Serve the evidence folder on localhost for the capture (for
example `python3 -m http.server 8765 --bind 127.0.0.1 --directory <evidence>`
in the background, through the Bash tool), open
`http://127.0.0.1:8765/compose/compare.html`, wait for the images to load,
take the `fullPage` screenshot into `compose/`, then stop the server. For wide
captures use one column (`grid-template-columns: 1fr`).

## 3. Comment text

Prepare the comment for the user to paste, with markers where each file goes:

```markdown
**Before** (staging, main): the total ignores filtered rows.
[attach 01-before.png]

**After** (local, `feature/x`): the total follows the filter.
[attach 02-after.png]

Highlights (red outline) were added for the capture; they are not part of the UI.
```

Say which highlights were added. Do not attach, upload or post: give the user
the files and the text.
