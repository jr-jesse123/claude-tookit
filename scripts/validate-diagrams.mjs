#!/usr/bin/env node
// Validates every ```mermaid fence in markdown files under the given roots
// (default: plugins/). Fences may be indented or blockquoted (`> ```mermaid`);
// the leading prefix is stripped before validation. Two layers per fence:
//
//   1. Syntax — the official mermaid parser, via
//      `npx @zabaca/mermaid-validate -` fed the fence body on stdin, so both
//      layers see exactly the same set of diagrams. Skipped with a warning
//      only when npx is genuinely absent (ENOENT) or --no-npx is passed; any
//      other spawn failure (timeout etc.) counts as an error, so CI cannot
//      pass without the syntax layer having run.
//   2. Structure — checks the parser cannot do, on flowcharts:
//      - every `linkStyle N` index must be < the number of edges declared;
//      - every `class A,B name` / `:::name` must reference a declared classDef.
//
// Edge counting covers the arrow forms the skills emit (-->, -.->, ==>, --x,
// --o, chained or labeled); quoted labels are stripped first so arrows inside
// text don't count. Zero dependencies, Node 18+.

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const args = process.argv.slice(2);
const noNpx = args.includes("--no-npx");
const roots = args.filter((a) => !a.startsWith("--"));
if (roots.length === 0) roots.push("plugins");

let errors = 0;
const fail = (msg) => {
  errors++;
  console.error(`  ✗ ${msg}`);
};

function* mdFiles(dir) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) yield* mdFiles(p);
    else if (entry.endsWith(".md")) yield p;
  }
}

// Line-based so an opening fence's indent/blockquote prefix can be stripped
// from its body lines (a `> `-quoted diagram must reach the parser unquoted).
function fences(text) {
  const out = [];
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const open = lines[i].match(/^([ \t>]*)```mermaid[ \t]*$/);
    if (!open) continue;
    const prefix = open[1];
    const body = [];
    let j = i + 1;
    for (; j < lines.length; j++) {
      if (/^[ \t>]*```[ \t]*$/.test(lines[j])) break;
      body.push(
        lines[j].startsWith(prefix)
          ? lines[j].slice(prefix.length)
          : lines[j].replace(/^[ \t>]+/, "")
      );
    }
    out.push({ body: body.join("\n") + "\n", line: i + 1 });
    i = j;
  }
  return out;
}

const EDGE_RE = /(-\.+->|={2,}>|-{2,}(?:>|x\b|o\b))/g;

function checkFlowchart(body, where) {
  const stripped = body.replace(/"[^"]*"/g, '""');
  const lines = stripped.split("\n").map((l) => l.trim());
  const edgeCount = lines
    .filter((l) => !/^(linkStyle|classDef|class|style|click|subgraph|end|%%)/.test(l))
    .join("\n")
    .match(EDGE_RE)?.length ?? 0;

  const classDefs = new Set(
    [...stripped.matchAll(/^\s*classDef\s+(\w+)/gm)].map((m) => m[1])
  );
  for (const m of stripped.matchAll(/^\s*class\s+[\w,\s]+?\s(\w+)\s*$/gm)) {
    if (!classDefs.has(m[1]))
      fail(`${where}: \`class ... ${m[1]}\` references undeclared classDef "${m[1]}"`);
  }
  for (const m of stripped.matchAll(/:::(\w+)/g)) {
    if (!classDefs.has(m[1]))
      fail(`${where}: \`:::${m[1]}\` references undeclared classDef "${m[1]}"`);
  }
  for (const m of stripped.matchAll(/^\s*linkStyle\s+([\d,\s]+)/gm)) {
    for (const idx of m[1].split(",").map((s) => parseInt(s.trim(), 10))) {
      if (Number.isInteger(idx) && idx >= edgeCount)
        fail(
          `${where}: linkStyle index ${idx} out of range — only ${edgeCount} edge(s) declared`
        );
    }
  }
}

let npxAvailable = !noNpx;
function syntaxCheck(body, where) {
  if (!npxAvailable) return;
  const res = spawnSync(
    "npx",
    ["--yes", "@zabaca/mermaid-validate", "--quiet", "-"],
    { encoding: "utf8", input: body, timeout: 120_000 }
  );
  if (res.error) {
    if (res.error.code === "ENOENT") {
      console.warn("  ⚠ npx not found; skipping the syntax layer");
      npxAvailable = false;
    } else {
      fail(`${where}: syntax check failed to run (${res.error.code ?? res.error.message})`);
    }
    return;
  }
  if (res.status !== 0)
    fail(`${where}: mermaid parser rejected the diagram\n${(res.stdout + res.stderr).trim()}`);
}

for (const root of roots) {
  for (const file of mdFiles(root)) {
    const blocks = fences(readFileSync(file, "utf8"));
    if (blocks.length === 0) continue;
    console.log(`checking ${file} (${blocks.length} diagram(s))`);
    for (const { body, line } of blocks) {
      const where = `${file}:${line}`;
      const type = body.trim().split(/\s/)[0];
      if (/^(flowchart|graph)$/.test(type)) checkFlowchart(body, where);
      syntaxCheck(body, where);
    }
  }
}

if (errors > 0) {
  console.error(`\n${errors} diagram error(s)`);
  process.exit(1);
}
console.log("✓ all mermaid diagrams valid");
