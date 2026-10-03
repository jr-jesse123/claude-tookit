#!/usr/bin/env node
// Pure routing policy over a jev_check result; CLI reads stdin and prints JSON.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const template = JSON.parse(readFileSync(new URL("../reference/scan-request.json", import.meta.url), "utf8"));
const ids = Object.keys(template.checks);
const thresholds = { yes_at: template.yes_at, no_at: template.no_at };

export function routeScan(scan) {
  const fallback = (reason, signals = null) => ({ recommendation: "generative", reason, signals });
  if (!scan || scan.isError || scan.truncated || !Array.isArray(scan.results) ||
      scan.results.length !== ids.length ||
      scan.thresholds?.yes_at !== thresholds.yes_at ||
      scan.thresholds?.no_at !== thresholds.no_at) return fallback("invalid-scan");

  const signals = {};
  for (const row of scan.results) {
    if (!row || !ids.includes(row.id) || Object.hasOwn(signals, row.id) ||
        row.status !== undefined || row.truncated ||
        typeof row.probability !== "number" || !Number.isFinite(row.probability) ||
        row.probability < 0 || row.probability > 1) return fallback("invalid-scan");
    const p = row.probability;
    signals[row.id] = {
      probability: p,
      verdict: p >= thresholds.yes_at ? "yes" : p <= thresholds.no_at ? "no" : "uncertain",
    };
  }

  if (signals.insufficient_evidence.verdict !== "no") return fallback("insufficient-evidence", signals);
  if (signals.reshaping_payoff.verdict !== "yes") return fallback("payoff-not-established", signals);
  if (signals.deterministic_opportunity.verdict === "yes") {
    return { recommendation: "consider-determinize", reason: "exact-opportunity-with-payoff", signals };
  }
  if (signals.typed_decision_opportunity.verdict === "yes") {
    return { recommendation: "consider-typify", reason: "typed-opportunity-with-payoff", signals };
  }
  return fallback("no-supported-reshaping-opportunity", signals);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let scan;
  try { scan = JSON.parse(readFileSync(0, "utf8")); } catch { scan = null; }
  process.stdout.write(JSON.stringify(routeScan(scan)) + "\n");
}
