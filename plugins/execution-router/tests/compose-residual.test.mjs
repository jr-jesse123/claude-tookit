import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { composeResidual } from "../scripts/compose-residual.mjs";

const ids = ["deterministic_opportunity", "typed_decision_opportunity", "generative_necessity", "reshaping_payoff", "insufficient_evidence"];
function scan(d = .9, t = .9, g = .9, payoff = .9, insufficient = .1) {
  return { thresholds: { yes_at: .85, no_at: .15 },
    results: ids.map((id, i) => ({ id, probability: [d, t, g, payoff, insufficient][i] })) };
}
function record(steps = []) {
  return { version: 1, original: { text: "Compare records, label anomalies and explain them.",
    criteria: { exact: "Exact comparison", typed: "Bounded labels with fallback", open: "Explanation" },
    constraints: ["Preserve precision"] }, noScan: false, providers: "--providers=openai", steps };
}
function gate(revision = 0, response = scan()) {
  return { kind: "gate", revision, evidence: "self-contained", separable: true,
    reason: "Supplied schema and recurring workload", payoff: "Repeated daily volume", scan: response };
}
function attempt(stage = "determinize", revision = 0, result = null) {
  return { kind: "attempt", stage, revision, result };
}
function exact() {
  return { status: "proposed-extraction", reason: "Exact rule and repeated use", reviewed: true,
    contract: "Fixture: exact comparison with independent oracle and explicit economics",
    coverage: { exact: "extracted", typed: "residual", open: "residual" },
    residual: { text: "Label anomalies and explain them.", criteria: ["typed", "open"] },
    recomposition: "Feed exact comparison into labels and explanation",
    workRemaining: ["Implement, validate and run exact comparison"] };
}
function typed() {
  return { status: "proposed-contract", reason: "Bounded recurring label", reviewed: true,
    contract: "Fixture: typed normal branch with conditional human fallback",
    coverage: { typed: "both", open: "residual" },
    residual: { text: "Explain anomalies; human resolves uncertain labels when triggered.", criteria: ["typed", "open"] },
    recomposition: "Use labels only after policy or human fallback resolves them",
    workRemaining: ["Implement adapter and policy; evaluate and execute typed decision"] };
}
const reject = (evidenceChanged = false) => ({ status: "no-extraction", reason: "Candidate lacks payoff", evidenceChanged });

test("initial checkpoint is pure, retains constraints and forwards provider selection", () => {
  const input = record();
  const before = structuredClone(input);
  const out = composeResidual(input);
  assert.equal(out.action, "ground-and-scan");
  assert.deepEqual(out.residual.criteria, ["exact", "typed", "open"]);
  assert.deepEqual(out.constraints, input.original.constraints);
  assert.equal(out.providers, "--providers=openai");
  assert.equal(out.taskExecuted, false);
  assert.deepEqual(input, before);
});

test("full composition uses two scans, one attempt each and preserves conditional residue", () => {
  const input = record([gate(), attempt("determinize", 0, exact())]);
  assert.equal(composeResidual(input).action, "ground-and-scan");
  assert.equal(composeResidual(input).signals, null);
  input.steps.push(gate(1)); // Both signals yes: consumed exact stage must not win again.
  assert.equal(composeResidual(input).action, "typify");
  input.steps.push(attempt("typify", 1, typed()));
  const out = composeResidual(input);
  assert.equal(out.action, "generative-handoff");
  assert.deepEqual(out.attempts, { determinize: 1, typify: 1 });
  assert.equal(out.scans, 2);
  assert.equal(out.contracts.length, 2);
  assert.equal(out.workRemaining.length, 2);
  assert.deepEqual(out.residual, typed().residual);
  assert.deepEqual(out.constraints, input.original.constraints);
  assert.equal(out.taskExecuted, false);
});

test("unchanged rejection advances to independent typed signal without another scan", () => {
  const input = record([gate(), attempt("determinize", 0, reject())]);
  const out = composeResidual(input);
  assert.equal(out.action, "typify");
  assert.equal(out.scans, 1);
  assert.equal(out.residual.text, input.original.text);
  assert.equal(out.contracts.length, 0);
  input.steps.push(attempt("typify", 0, reject()));
  assert.equal(composeResidual(input).action, "generative-handoff");
});

test("stale evidence discovered during rejected design invalidates previous signals", () => {
  const out = composeResidual(record([gate(), attempt("determinize", 0, reject(true))]));
  assert.equal(out.action, "generative-handoff");
  assert.equal(out.signals, null);
  assert.equal(out.scans, 1);
});

test("no-change proposal cannot earn a rescan even if criterion order changes", () => {
  const input = record();
  const result = { ...exact(), coverage: { exact: "both", typed: "residual", open: "residual" },
    residual: { text: input.original.text, criteria: ["open", "typed", "exact"] } };
  input.steps = [gate(), attempt("determinize", 0, result)];
  const out = composeResidual(input);
  assert.equal(out.action, "typify");
  assert.equal(out.revision, 0);
  assert.equal(out.contracts.length, 0);
  assert.equal(out.scans, 1);
});

test("pending attempt consumes budget and cannot be followed by more work", () => {
  const input = record([gate(), attempt()]);
  const out = composeResidual(input);
  assert.equal(out.action, "await-result");
  assert.equal(out.attempts.determinize, 1);
  assert.deepEqual(composeResidual(input), out);
  input.steps.push(gate());
  assert.equal(composeResidual(input).action, "repair-record");
});

test("direct typify never loops back to exact design", () => {
  const input = record([gate(0, scan(.1, .9)), attempt("typify", 0, reject())]);
  const out = composeResidual(input);
  assert.equal(out.action, "generative-handoff");
  assert.deepEqual(out.attempts, { determinize: 0, typify: 1 });
  input.steps.push(attempt("determinize", 0, exact()));
  assert.equal(composeResidual(input).action, "repair-record");
});

test("new residual requires fresh current opportunity, evidence and payoff", () => {
  for (const response of [scan(.9, .1), scan(.9, .9, .9, .5), scan(.9, .9, .9, .9, .5), null, {}]) {
    const out = composeResidual(record([gate(), attempt("determinize", 0, exact()), gate(1, response)]));
    assert.equal(out.action, "generative-handoff");
    assert.equal(out.contracts.length, 1);
    assert.equal(out.residual.text, exact().residual.text);
  }
});

test("no semantic residual is design completion, never task completion", () => {
  for (const status of ["proposed-extraction", "already-exact"]) {
    const result = { ...exact(), status, coverage: { exact: "extracted", typed: "extracted", open: "extracted" },
      residual: { text: "", criteria: [] } };
    const out = composeResidual(record([gate(), attempt("determinize", 0, result)]));
    assert.equal(out.action, "design-complete");
    assert.equal(out.scans, 1);
    assert.equal(out.workRemaining.length, 1);
    assert.equal(out.taskExecuted, false);
  }
});

test("cheap bypasses preserve all work and make zero scan attempts", () => {
  for (const evidence of ["self-contained", "cheaply-groundable", "discovery-dependent"]) {
    const input = record([{ kind: "gate", revision: 0, evidence, separable: evidence !== "discovery-dependent",
      bypass: "generative", reason: "No payoff, unavailable scanner or inseparable evidence" }]);
    input.noScan = true;
    const out = composeResidual(input);
    assert.equal(out.action, "generative-handoff");
    assert.equal(out.scans, 0);
    assert.equal(out.residual.text, input.original.text);
  }
});

test("known exact mechanism exits with execution still pending", () => {
  const input = record([{ kind: "gate", revision: 0, evidence: "self-contained", separable: true,
    bypass: "direct-deterministic", reason: "Supplied exact contract covers task", mechanism: "Known comparator", oracle: "Independent expected values" }]);
  const out = composeResidual(input);
  assert.equal(out.action, "direct-deterministic");
  assert.equal(out.scans, 0);
  assert.equal(out.residual.text, input.original.text);
  assert.equal(out.direct.oracle, "Independent expected values");
});

test("lost criteria, missing review, pending work or stale revisions require repair", () => {
  const changes = [
    r => { delete r.coverage.open; },
    r => { r.coverage.extra = "residual"; },
    r => { r.residual.criteria = ["typed"]; },
    r => { r.residual.text = ""; },
    r => { r.reviewed = false; },
    r => { r.contract = ""; },
    r => { r.workRemaining = []; },
    r => { r.recomposition = ""; },
    r => { r.coverage.exact = "unknown"; },
  ];
  for (const change of changes) {
    const result = exact();
    change(result);
    const input = record([gate(), attempt("determinize", 0, result)]);
    const out = composeResidual(input);
    assert.equal(out.action, "repair-record");
    assert.deepEqual(out.preservedRecord, input);
  }
  assert.equal(composeResidual(record([gate(1)])).action, "repair-record");
  assert.equal(composeResidual(record([gate(), attempt("typify")])).action, "repair-record");
});

test("invalid records, no-scan violations and extra steps never silently reset", () => {
  const forbidden = record([gate()]);
  forbidden.noScan = true;
  const inseparable = record([{ ...gate(), separable: false }]);
  for (const input of [null, {}, [], record([null]), forbidden, inseparable,
    record([gate(), attempt("determinize", 0, exact()), gate(1), attempt("typify", 1, typed()), gate(2)])]) {
    assert.equal(composeResidual(input).action, "repair-record");
  }
});

test("CLI returns deterministic checkpoint JSON and retains malformed-input failure", () => {
  const cli = fileURLToPath(new URL("../scripts/compose-residual.mjs", import.meta.url));
  for (const [input, action] of [[JSON.stringify(record()), "ground-and-scan"], ["not JSON", "repair-record"]]) {
    const result = spawnSync(process.execPath, [cli], { input, encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr || result.error?.message);
    assert.equal(JSON.parse(result.stdout).action, action);
  }
});

test("result annotations cannot overwrite authoritative stage and revision", () => {
  const result = { ...exact(), stage: "typify", inputRevision: 99 };
  const out = composeResidual(record([gate(), attempt("determinize", 0, result)]));
  assert.equal(out.contracts[0].stage, "determinize");
  assert.equal(out.contracts[0].inputRevision, 0);
});

test("each fresh probability combination respects spent stages and shared vetoes", () => {
  for (const d of [.1, .5, .9]) for (const t of [.1, .5, .9]) {
    for (const p of [.1, .5, .9]) for (const i of [.1, .5, .9]) {
      const input = record([gate(), attempt("determinize", 0, exact()), gate(1, scan(d, t, .9, p, i))]);
      const out = composeResidual(input);
      assert.equal(out.action, t === .9 && p === .9 && i === .1 ? "typify" : "generative-handoff");
      assert.deepEqual(out.attempts, { determinize: 1, typify: 0 });
      assert.equal(out.scans, 2);
      assert.equal(out.contracts.length, 1);
    }
  }
});
