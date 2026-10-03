import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { routeScan } from "../scripts/route-scan.mjs";

const root = fileURLToPath(new URL("../", import.meta.url));
const cli = fileURLToPath(new URL("../scripts/route-scan.mjs", import.meta.url));
const request = JSON.parse(readFileSync(new URL("../reference/scan-request.json", import.meta.url)));
const ids = ["deterministic_opportunity", "typed_decision_opportunity", "generative_necessity", "reshaping_payoff", "insufficient_evidence"];

// Synthetic transport fixtures exercise policy, not Jev's classification accuracy.
function scan(d = 0.1, t = 0.1, g = 0.9, p = 0.9, i = 0.1) {
  return {
    results: ids.map((id, n) => ({ id, probability: [d, t, g, p, i][n] })),
    thresholds: { yes_at: 0.85, no_at: 0.15 },
    model: "jev-latest",
  };
}

test("mixed opportunities keep generative work visible and prefer exact reshaping", () => {
  const input = scan(0.95, 0.94, 0.96);
  const before = structuredClone(input);
  const result = routeScan(input);
  assert.equal(result.recommendation, "consider-determinize");
  assert.equal(result.signals.typed_decision_opportunity.verdict, "yes");
  assert.equal(result.signals.generative_necessity.verdict, "yes");
  assert.deepEqual(input, before);
});

test("typed opportunity is useful without proving there is no generative residual", () => {
  assert.equal(routeScan(scan(0.1, 0.9, 0.9)).recommendation, "consider-typify");
  assert.equal(routeScan(scan(0.5, 0.9, 0.5)).recommendation, "consider-typify");
});

test("uncertainty on unused signals does not reject an exact opportunity", () => {
  assert.equal(routeScan(scan(0.9, 0.5, 0.5)).recommendation, "consider-determinize");
});

test("insufficient or uncertain evidence vetoes positive opportunities", () => {
  for (const p of [0.150001, 0.5, 0.9]) {
    const result = routeScan(scan(0.99, 0.99, 0.9, 0.99, p));
    assert.equal(result.recommendation, "generative");
    assert.equal(result.reason, "insufficient-evidence");
  }
});

test("technical possibility without established payoff does not trigger reshaping", () => {
  for (const p of [0, 0.15, 0.5, 0.849999]) {
    const result = routeScan(scan(0.99, 0.99, 0.9, p));
    assert.equal(result.recommendation, "generative");
    assert.equal(result.reason, "payoff-not-established");
  }
});

test("threshold endpoints are inclusive and match the shipped request", () => {
  assert.equal(request.yes_at, 0.85);
  assert.equal(request.no_at, 0.15);
  assert.deepEqual(Object.keys(request.checks), ids);
  assert.equal(routeScan(scan(0.85, 0.5, 0.5, 0.85, 0.15)).recommendation, "consider-determinize");
  assert.equal(routeScan(scan(0.849999, 0.85, 0.9)).recommendation, "consider-typify");
});

test("no supported opportunity falls back even when generative necessity is no", () => {
  for (const g of [0.1, 0.5, 0.9]) {
    assert.equal(routeScan(scan(0.1, 0.5, g)).recommendation, "generative");
  }
});

test("raw probability owns the verdict, regardless of an upstream label", () => {
  const input = scan(0.1, 0.9);
  input.results[0].verdict = "yes";
  input.results[1].verdict = "no";
  assert.equal(routeScan(input).recommendation, "consider-typify");
});

test("invalid, missing, duplicate, extra and errored results fail closed", () => {
  const variants = [null, {}, [], { isError: true }, { results: [] }];
  for (const change of [
    s => s.results.pop(),
    s => s.results.push({ id: "extra", probability: 0.9 }),
    s => { s.results[1].id = s.results[0].id; },
    s => { s.results[0].id = "unknown"; },
    s => { s.results[0] = null; },
    s => { s.results[4].status = "invalid_response"; s.results[4].probability = 0; },
    s => { s.results[0].truncated = true; },
    s => { s.truncated = true; },
    s => { s.isError = true; },
    s => { s.thresholds.yes_at = 0.75; },
    s => { delete s.thresholds; },
  ]) {
    const input = scan(0.9, 0.9);
    change(input);
    variants.push(input);
  }
  for (const input of variants) assert.equal(routeScan(input).reason, "invalid-scan");
});

test("probabilities must be finite numbers within the unit interval", () => {
  for (const p of [NaN, Infinity, -Infinity, -0.01, 1.01, "0.9", null, undefined, true]) {
    const input = scan(0.9, 0.9);
    input.results[0].probability = p;
    assert.equal(routeScan(input).reason, "invalid-scan");
  }
});

test("CLI accepts stdin JSON and produces an explicit fallback on malformed JSON", () => {
  for (const [input, expected] of [[JSON.stringify(scan(0.9)), "consider-determinize"], ["not json", "generative"]]) {
    const result = spawnSync(process.execPath, [cli], { input, encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    assert.equal(JSON.parse(result.stdout).recommendation, expected);
  }
});

function* markdown(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) yield* markdown(path);
    else if (entry.name.endsWith(".md")) yield path;
  }
}

test("all local Markdown links and literal plugin-root references resolve", () => {
  for (const path of markdown(root)) {
    const text = readFileSync(path, "utf8");
    for (const match of text.matchAll(/\]\(([^)]+)\)/g)) {
      if (/^(https?:|#)/.test(match[1])) continue;
      assert.ok(existsSync(resolve(dirname(path), match[1].split("#")[0])), `${path}: ${match[1]}`);
    }
    for (const match of text.matchAll(/\$\{CLAUDE_PLUGIN_ROOT\}\/([\w./-]+)/g)) {
      assert.ok(existsSync(resolve(root, match[1])), `${path}: ${match[1]}`);
    }
  }
});
