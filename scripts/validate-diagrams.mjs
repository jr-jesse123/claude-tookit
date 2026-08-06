#!/usr/bin/env node
// Validates every ```mermaid fence in markdown files under the given roots
// (default: plugins/). Two layers:
//
//   1. Syntax — the official mermaid parser, via `npx @zabaca/mermaid-validate`
//      run per file (its directory mode is unreliable). Skipped with a warning
//      when npx is unavailable or --no-npx is passed.
//   2. Structure — checks the parser cannot do, on flowcharts:
//      - every `linkStyle N` index must be < the number of edges declared;
//      - every `class A,B name` / `:::name` must reference a declared classDef.
//
// Edge counting covers the arrow forms the skill emits (-->, -.->, ==>, --x,
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

function fences(text) {
  const out = [];
  const re = /^```mermaid[ \t]*\n([\s\S]*?)^```/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    const line = text.slice(0, m.index).split("\n").length;
    out.push({ body: m[1], line });
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
function syntaxCheck(file) {
  if (!npxAvailable) return;
  const res = spawnSync(
    "npx",
    ["--yes", "@zabaca/mermaid-validate", "--quiet", file],
    { encoding: "utf8", timeout: 120_000 }
  );
  if (res.error) {
    console.warn(`  ⚠ npx unavailable (${res.error.code}); skipping syntax layer`);
    npxAvailable = false;
    return;
  }
  if (res.status !== 0)
    fail(`${file}: mermaid parser rejected a diagram\n${(res.stdout + res.stderr).trim()}`);
}

for (const root of roots) {
  for (const file of mdFiles(root)) {
    const blocks = fences(readFileSync(file, "utf8"));
    if (blocks.length === 0) continue;
    console.log(`checking ${file} (${blocks.length} diagram(s))`);
    for (const { body, line } of blocks) {
      const type = body.trim().split(/\s/)[0];
      if (/^(flowchart|graph)$/.test(type)) checkFlowchart(body, `${file}:${line}`);
    }
    syntaxCheck(file);
  }
}

if (errors > 0) {
  console.error(`\n${errors} diagram error(s)`);
  process.exit(1);
}
console.log("✓ all mermaid diagrams valid");
