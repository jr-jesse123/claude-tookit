# HTML mode — the tour as an annotatable page (Lavish)

Shared by `pr-tour` and `plan-tour` when `$ARGUMENTS` carries `--html`.
The tour itself does not change — same mapping, same sections, same
diagrams, same rules. Only the surface changes: the tour is written as one
HTML file and opened in [Lavish](https://github.com/kunchenguid/lavish-axi),
where the reviewer sees the Mermaid diagrams rendered and can annotate any
node, contract entry, or reading-order item; the annotations come back to
this session as feedback.

## Preconditions — fall back instead of failing

Lavish serves the page on `127.0.0.1` and needs a browser on the same
machine. Produce the plain markdown tour instead, with one line saying why,
when any of these holds:

- the session is remote (`CLAUDE_CODE_REMOTE=true` in the environment — a
  cloud container has no browser the user can reach);
- `npx` is unavailable, or the `lavish-axi` command fails to start;
- the user will paste the tour into GitHub — markdown is the format for
  that.

## The CLI — always pinned, telemetry off

Every call has exactly this prefix (the `allowed-tools` entry matches it):

```
env LAVISH_AXI_TELEMETRY=0 npx --yes lavish-axi@0.1.89 <args>
```

Version pinned like any upstream this toolkit consumes; bumping it is an
explicit change here. Never run `share` — it publishes the page on a
third-party host, public by default; if the user asks to share, point them
to the browser's own menu so the decision stays theirs.

Lavish's own CLI prints design guidance and playbooks (`design`,
`playbook`). Do not fetch them: the tour's conventions below win, and its
diagrams stay Mermaid.

## Writing the page

Write to `.lavish/<skill>-<slug>.html` in the working directory
(`.lavish/pr-tour-feat-rate-limit.html`). If `.lavish/` is not in
`.gitignore`, say so in the closing line — do not edit `.gitignore`.

One self-contained file, no build step:

```html
<!doctype html>
<html lang="en" data-theme="auto">
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PR tour — feat/rate-limit</title>
<script>
  // Theme: the viewer's toggle wins while the file's data-theme is unchanged;
  // editing data-theme in the file resets every viewer to the new default.
  (() => {
    const root = document.documentElement;
    const fileTheme = root.getAttribute("data-theme") || "auto";
    let pick = null;
    try {
      const saved = JSON.parse(localStorage.getItem("tour-theme") || "null");
      if (saved && saved.file === fileTheme) pick = saved.pick;
    } catch {}
    const systemDark = matchMedia("(prefers-color-scheme: dark)").matches;
    const wanted = pick || fileTheme;
    root.dataset.theme = wanted === "auto" ? (systemDark ? "dark" : "light") : wanted;
    root.dataset.fileTheme = fileTheme;
  })();
</script>
<style>
  :root { color-scheme: light; --bg:#fff; --fg:#111; --muted:#666; --line:#ddd; --code:#f5f5f5;
          --add:#e0f5e6; --rem:#ffe3e3; }
  :root[data-theme="dark"] { color-scheme: dark; --bg:#16181d; --fg:#e8e8e8; --muted:#9a9a9a;
          --line:#333; --code:#1f2228; --add:#16361f; --rem:#3d1a1a; }
  body { background:var(--bg); color:var(--fg); font:16px/1.55 system-ui, sans-serif;
         max-width:72rem; margin:0 auto; padding:24px 16px; }
  .tour-diagram { overflow-x:auto; margin:8px 0 24px; }
  pre { background:var(--code); padding:12px; overflow-x:auto; border-radius:6px; }
  .d-add { background:var(--add); display:block; } .d-rem { background:var(--rem); display:block; }
  .off-diff { font-weight:600; }
  #theme-toggle { position:fixed; top:12px; right:12px; padding:4px 10px; font:inherit;
                  background:var(--code); color:var(--fg); border:1px solid var(--line);
                  border-radius:6px; cursor:pointer; }
</style></head><body>
  <button id="theme-toggle" type="button"></button>
  <!-- one <section> per group; see "Structure" -->

<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.15.0/dist/mermaid.esm.min.mjs";
const root = document.documentElement;
const dark = root.dataset.theme === "dark";

const toggle = document.getElementById("theme-toggle");
toggle.textContent = dark ? "☀ Light" : "☾ Dark";
toggle.onclick = () => {
  try {
    localStorage.setItem("tour-theme", JSON.stringify(
      { file: root.dataset.fileTheme, pick: dark ? "light" : "dark" }));
  } catch {}
  location.reload(); // Mermaid bakes its theme into the SVG: render again from scratch
};
if (root.dataset.fileTheme === "auto")
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => location.reload());

mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "default", securityLevel: "strict" });
for (const el of document.querySelectorAll(".tour-diagram")) {
  const src = document.getElementById(el.id + "-src").textContent;
  el.innerHTML = (await mermaid.render(el.id + "-svg", src)).svg;
}
</script>
</body></html>
```

**Diagrams.** Each fence body you would have shown goes, unchanged and
already validated, into a source block, rendered next to it:

```html
<h3>Who depends on whom — and what changed in that graph?</h3>
<div class="tour-diagram" data-lavish-mermaid id="d1"></div>
<script type="text/plain" id="d1-src">
flowchart LR
    A[api/orders.ts] -->|"⊕ publish"| Q[["queue: order-events ⊕"]]
    ...
</script>
```

Never use a `class="mermaid"` container. Lavish converts those into
Excalidraw whiteboards, and the conversion keeps `classDef` node painting
but drops every `linkStyle` — the removed/added edges lose their paint and
the painted delta stops reading as one. The `data-lavish-mermaid` wrapper
keeps Mermaid's own SVG (painting intact) and still lets the reviewer
annotate individual nodes. Because nodes are named after real paths, the
feedback for a node arrives labeled with the file.

**Contract blocks.** A quoted promise is a `<pre><code>` in the contract's
native notation. When the markdown tour would have used a ` ```diff `
fence, wrap each line in `<span class="d-add">` / `<span class="d-rem">`
and keep the `+`/`−` and ⊕/⊖ in the text — color is never the only signal,
here as in the diagrams. No diff library: the blocks are minimal
fragments, not file diffs.

**Structure.** Mirror the markdown tour section for section, and give every
item the reviewer might want to push back on its own element with a stable
`id`, so an annotation lands on exactly that claim:

- one `<section id="group-N">` per group, narrative first as `<p>`;
- each diagram under an `<h3>` naming its question;
- each contract entry an `<article id="contract-<symbol>">`; off-diff
  consumers in `<span class="off-diff">` (the bold of the markdown);
- each reading-order entry an `<li id="read-N">`, `path:line` in `<code>`;
- for `plan-tour`, each plan-vs-code entry an `<li id="mismatch-N">` and
  each open question an `<li id="question-N">`.

Nothing is added for the page's sake: no summary cards, no extra
narrative, no restyling of the painting palette. The one exception is the
theme toggle in the template (see *Theme*).

## Theme — light, dark, or the system's

The page's default theme lives in one place: the `data-theme` attribute on
`<html>`, with three values:

- `auto` (the default) — follows the viewer's system setting and switches
  live when it changes;
- `light` or `dark` — fixed, whatever the system says.

Set it from `--theme light`, `--theme dark` or `--theme auto` in
`$ARGUMENTS` (strip it with `--html` before resolving the target); without
the flag, write `auto`. Without `--html`, `--theme` does nothing: the
markdown tour takes the theme of whatever renders it — say so in one line
if the user passed it.

Everything else in the template derives from that attribute, so keep it
that way when writing the page:

- colors are tokens on `:root` and on `:root[data-theme="dark"]` — never a
  color written straight into an element or a `style=`;
- the head script resolves `auto` to `light` or `dark` before the first
  paint, so there is no flash of the wrong theme;
- Mermaid gets `theme: "dark"` or `"default"` from the resolved value. It
  bakes the theme into the SVG at render time, which is why the toggle and
  a system change reload the page instead of restyling it;
- the painting classes (`classDef added`/`removed`/`ctx`) keep their fixed
  colors in both themes — light fills with an explicit `color:#111`, as the
  painting rules in `SKILL.md` already require — so the painted delta reads
  the same on either background. Do not add per-theme variants of them.

**The toggle.** The button at the top right flips between light and dark
for that viewer, in that browser (stored in `localStorage`; in a private
window it lasts until the page closes). It wins only while the file's
`data-theme` stays what it was when the viewer clicked: once the file's
default changes, every viewer starts again from the new default. Lavish
treats the button like any other element; it is not part of the tour, so
ignore annotations on it.

**Switching after the page is done.** When the user asks for another
theme once the tour is written ("deixa escuro", "make it light", "follow
my system"):

1. Edit the one attribute — `<html lang="…" data-theme="auto">` →
   `data-theme="dark"` (or `light`, `auto`). Nothing else changes: no
   rewrite of the page, no re-validation of the diagrams, no new mapping.
2. Lavish reloads the page on its own when the file changes; the open
   `poll` keeps listening. If the page was opened outside Lavish, the
   reviewer reloads the tab.
3. Reply in one line: the new default, and that the toggle still lets
   each viewer flip it.

For several tours at once (`.lavish/*.html`), make the same one-attribute
Edit in each file. A page written before this section existed has no
`data-theme` and no toggle: say so, and offer to rewrite it from the
template — do not patch the old page piece by piece.

## Open, then listen

1. Open: `env LAVISH_AXI_TELEMETRY=0 npx --yes lavish-axi@0.1.89 <file>`.
   Tell the user, in one or two lines, the URL it prints and that they can
   annotate anything and press *Send*. Do not print the tour in the
   terminal too — the page is the tour.
2. Listen: `... lavish-axi@0.1.89 poll <file>`. It blocks until the
   reviewer sends feedback. Run it as a tracked background command when
   the harness offers one (the result wakes this session); otherwise in
   the foreground with the longest timeout available. Never detach it
   (`&`, `nohup`). If it times out before feedback arrives, run it again —
   feedback stays queued.
3. Each returned prompt carries what was annotated (`target.label`, the
   node's file, or the element's text) and the reviewer's words. Answer it
   inside the tour's own scope:
   - a question ("who else calls this?", "why is this read third?") →
     answer from the code, short, with `path:line`, via
     `poll <file> --agent-reply "<answer>"`, which replies and keeps
     listening;
   - a correction (wrong edge, missing consumer, wrong group) → verify it
     against the code; if it holds, fix the page in place (Lavish reloads
     it), re-validate any diagram you touched, and say what changed in the
     reply;
   - a request for findings ("is this a bug?") → the tour still reports
     none; reply pointing to `/code-review:quick-review`.
4. Stop when the reviewer ends the session (*Send & End* — its final
   feedback still arrives once) or the user moves on in the terminal. Do
   not reopen an ended session unless asked. Close with one line in the
   terminal: the file path, and the `.gitignore` note if it applies.
