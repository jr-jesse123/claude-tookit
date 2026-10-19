# AG Grid screens

Techniques for reading and acting on AG Grid reliably. App-specific parts
(custom tool panels, the endpoint that saves a grid's layout, screen names)
belong in a project reference listed in the config, not here.

## Scope every query to one grid

A page often holds several grids, and a grid holds several header and body
containers (pinned left, centre, pinned right). Scope to the grid under test
first and read from there:

```js
const grid = page.locator('.ag-root-wrapper').first();
const headers = grid.locator('.ag-header-cell[col-id]');
```

Use `.nth(i)` or a surrounding container when the grid under test is not the
first one, and say in the README which grid was read.

## Columns are virtualised: sweep by aria-colindex

AG Grid renders only the columns near the viewport. A read of
`.ag-header-cell` returns what is rendered, not what exists. To read the full
column order, scroll the centre viewport horizontally in steps and collect
headers keyed by `aria-colindex` until it stops growing:

```js
const read = async () => page.evaluate(async () => {
  const root = document.querySelector('.ag-root-wrapper');
  const viewport = root.querySelector('.ag-body-horizontal-scroll-viewport') || root.querySelector('.ag-center-cols-viewport');
  const seen = new Map();
  const collect = () => root.querySelectorAll('.ag-header-cell[col-id]').forEach((h) => {
    seen.set(Number(h.getAttribute('aria-colindex')), h.getAttribute('col-id'));
  });
  viewport.scrollLeft = 0;
  for (let i = 0; i < 50; i += 1) {
    await new Promise((r) => setTimeout(r, 100));
    collect();
    if (viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth) break;
    viewport.scrollLeft += viewport.clientWidth * 0.8;
  }
  viewport.scrollLeft = 0;
  return [...seen.entries()].sort((a, b) => a[0] - b[0]).map((e) => e[1]);
});
```

Rows are virtualised the same way (`aria-rowindex`, vertical viewport
`.ag-body-viewport`). Prefer reading a count or a value the grid shows
(status bar, row-count label) when one exists.

## Computed style over classes

A class like `ag-row-selected` or a theme class says what the grid intended,
not what the user sees. When the case is about appearance (colour, weight,
visibility, width), return `getComputedStyle(el)` values for the properties in
question, and the class list only as context.

## Drags: real mouse moves

Column moves, resizes and row drags listen to pointer events and ignore a
jump from source to target. Drag with the mouse in small steps:

```js
const from = await grid.locator('.ag-header-cell[col-id="price"]').boundingBox();
const to = await grid.locator('.ag-header-cell[col-id="name"]').boundingBox();
await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
await page.mouse.down();
for (let i = 1; i <= 15; i += 1) {
  await page.mouse.move(
    from.x + from.width / 2 + ((to.x - from.x) * i) / 15,
    from.y + from.height / 2 + ((to.y - from.y) * i) / 15,
  );
}
await page.waitForTimeout(300);
await page.mouse.up();
```

Read the column order before and after; the screenshot alone does not prove a
move.

## Highlights

To point at a cell or header in a capture, prefer `outline` (no layout shift)
injected with `page.addStyleTag` and removed after the screenshot. For an area
that is not one element (a range of cells), add an absolutely positioned
overlay `div` at the union of their bounding boxes. Grid cells are recycled on
scroll: take the screenshot before scrolling, or re-apply the highlight.
Declare every highlight in the README.
