# UI catalog contract

A catalog is the project's map of its UI, so an executor drives the app without rediscovering it. It is optional and project-owned; the plugin ships no generator. The executors and the planner expect this layout under `catalogDir`:

```
<catalogDir>/
  generated/<app>/routes/<route>.md        # per page: the data-testid values on screen and how to reach the page
  generated/<app>/routes/<route>.opens.md  # per page: dialogs, menus and steps, with the click that opens each
  generated/<app>/routes/<route>/<Component>.md   # ids of a component named in an .opens.md
  widgets/<widget>.md                      # how to drive a shared component (a grid, a picker)
  flows/<flow>.md                          # verified click paths across pages, marked verified or inferred
```

Conventions the executors rely on:
- Elements are clicked with `[data-testid="<id>"]`. An id marked `[per row]` is scoped to its row by exact text: `[role="row"]:has(:text-is("<full row name>")) [data-testid="<id>"]`. A bare id on a grid clicks the first row, and `:has-text()` matches substrings.
- `browser_find` and snapshots do not show `data-testid`; a click that works is the only proof an id exists. A missing or wrong id goes to `CATALOG NOTES` in the executor's report, and a note becomes a catalog change only after the user reviews it.
- An entry marked "trigger not identified" or a page marked "no click path found" is a question to answer by looking at the screen.
- A dialog's confirm button is often not listed because it comes from a shared component: find it by its visible text.

A project with another layout can keep it: the plan names the catalog files each stage needs, and the executors read only those. What matters is that a stage can name its files and that each file says how to reach a page and which ids it holds.
