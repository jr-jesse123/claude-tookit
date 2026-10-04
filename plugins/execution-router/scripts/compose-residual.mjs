#!/usr/bin/env node
// Replay an advisory record. No dispatch, inference, persistence or task execution.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { routeScan } from "./route-scan.mjs";

const text = value => typeof value === "string" && value.trim().length > 0;
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const require = condition => { if (!condition) throw new Error("invalid-record"); };

export function composeResidual(record) {
  try {
    require(object(record) && record.version === 1 && object(record.original));
    const { original, steps } = record;
    require(text(original.text) && object(original.criteria) &&
      Object.keys(original.criteria).length > 0 && Object.keys(original.criteria).every(text) &&
      Object.values(original.criteria).every(text) &&
      Array.isArray(original.constraints) && original.constraints.every(text));
    require(Array.isArray(steps) && steps.length <= 4 && typeof record.noScan === "boolean");
    require(record.providers === undefined || text(record.providers));

    let residual = { text: original.text, criteria: Object.keys(original.criteria) };
    let revision = 0;
    let action = "ground-and-scan";
    let reason = "initial-gate";
    let signals = null;
    const attempts = { determinize: 0, typify: 0 };
    let scans = 0;
    const contracts = [];
    let direct = null;

    function select() {
      if (!signals || signals.insufficient_evidence.verdict !== "no" ||
          signals.reshaping_payoff.verdict !== "yes") return "generative-handoff";
      if (!attempts.determinize && !attempts.typify &&
          signals.deterministic_opportunity.verdict === "yes") return "determinize";
      if (!attempts.typify && signals.typed_decision_opportunity.verdict === "yes") return "typify";
      return "generative-handoff";
    }

    for (const step of steps) {
      require(object(step) && step.revision === revision);
      if (action === "ground-and-scan") {
        require(step.kind === "gate" &&
          ["self-contained", "cheaply-groundable", "discovery-dependent"].includes(step.evidence) &&
          typeof step.separable === "boolean" && text(step.reason));
        const eligible = step.evidence !== "discovery-dependent" && step.separable;
        if (!eligible || step.bypass === "generative") {
          require(step.scan === undefined);
          action = "generative-handoff";
          reason = step.reason;
        } else if (step.bypass === "direct-deterministic") {
          require(step.scan === undefined && text(step.mechanism) && text(step.oracle));
          direct = { mechanism: step.mechanism, oracle: step.oracle };
          action = "direct-deterministic";
          reason = step.reason;
        } else {
          require(!record.noScan && step.bypass === undefined && text(step.payoff));
          // A null response records a failed/unavailable scan; it is never retried.
          require(Object.hasOwn(step, "scan"));
          scans++;
          const route = routeScan(step.scan);
          signals = route.signals;
          action = select();
          reason = action !== "generative-handoff" ? "eligible-unused-transformation" :
            route.recommendation === "generative" ? route.reason : "no-unused-supported-transformation";
        }
      } else if (action === "determinize" || action === "typify") {
        const stage = action;
        require(step.kind === "attempt" && step.stage === stage && !attempts[stage]);
        attempts[stage]++;
        if (step.result === null) {
          action = "await-result";
          reason = `${stage}-already-issued`;
          continue;
        }
        const result = step.result;
        require(object(result) && text(result.reason));
        if (["no-extraction", "failed"].includes(result.status)) {
          require(typeof result.evidenceChanged === "boolean");
          action = stage === "typify" || result.evidenceChanged ? "generative-handoff" : select();
          if (result.evidenceChanged) signals = null;
          reason = result.reason;
          continue;
        }
        require((stage === "determinize"
          ? ["proposed-extraction", "already-exact"] : ["proposed-contract"]).includes(result.status));
        require(result.reviewed === true && text(result.contract) &&
          Array.isArray(result.workRemaining) && result.workRemaining.length > 0 &&
          result.workRemaining.every(text) && text(result.recomposition));
        require(object(result.coverage) && same(Object.keys(result.coverage).sort(), [...residual.criteria].sort()));
        const owners = Object.values(result.coverage);
        require(owners.every(owner => ["extracted", "residual", "both"].includes(owner)) &&
          owners.some(owner => owner !== "residual"));
        const remainingIds = residual.criteria.filter(id => result.coverage[id] !== "extracted");
        require(object(result.residual) && Array.isArray(result.residual.criteria) &&
          same([...result.residual.criteria].sort(), [...remainingIds].sort()) &&
          (remainingIds.length ? text(result.residual.text) : result.residual.text === ""));
        // No-change proposals do not earn a new scan or retry.
        if (result.residual.text === residual.text && same([...result.residual.criteria].sort(), [...residual.criteria].sort())) {
          action = stage === "typify" ? "generative-handoff" : select();
          reason = "unchanged-residual";
          continue;
        }
        contracts.push({ ...result, stage, inputRevision: revision });
        residual = result.residual;
        revision++;
        signals = null; // Opportunity/economics belong to the old residual.
        if (!residual.criteria.length) {
          action = "design-complete";
          reason = "execution-still-pending";
        } else if (stage === "typify") {
          action = "generative-handoff";
          reason = "transformation-budget-exhausted";
        } else {
          action = "ground-and-scan";
          reason = "changed-residual-needs-fresh-gate";
        }
      } else {
        throw new Error("step-after-stop-or-pending-result");
      }
    }

    return { action, reason, revision, original, residual, constraints: original.constraints,
      attempts, scans, signals, contracts, direct, providers: record.providers ?? null,
      workRemaining: contracts.flatMap(contract => contract.workRemaining), noScan: record.noScan, taskExecuted: false };
  } catch {
    // Do not silently restart, lose attempted work, or trust a partial replay.
    return { action: "repair-record", reason: "invalid-or-out-of-order-record",
      original: record?.original ?? null, preservedRecord: record ?? null, taskExecuted: false };
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let record;
  try { record = JSON.parse(readFileSync(0, "utf8")); } catch { record = null; }
  process.stdout.write(JSON.stringify(composeResidual(record)) + "\n");
}
