# Shape scan contract

Read only after the cheap grounding gate admits a scan. The scan classifies
opportunity; the local policy selects the next advisory step.

## Request

Read [scan-request.json](scan-request.json). Copy its `checks`, `yes_at`, and
`no_at` unchanged into one `jev_check` request and add this `state` object:

- `task`: the requested objective, verbatim where practical.
- `constraints`: supplied semantic, operational, and permission constraints.
- `acceptance`: supplied success criteria; mark unspecified criteria unknown.
- `economics`: supplied reuse/volume/savings/guarantee facts; mark unknowns.
- `evidence`: bounded raw source excerpts with source/range or diff identity.

Preserve material limitations, omissions and freshness. The task description
is evidence about intent, not proof of its factual claims. Do not replace raw
evidence with your conclusions, fetch additional state, or solve the task to
prepare this payload. Use only the configured, permitted Jev endpoint.

Use the installed `jev-code` tool's advertised name: normally
`mcp__plugin_jev-code_jev__jev_check` for the plugin, or
`mcp__jev__jev_check` for standalone setup. If neither is callable, fall back;
the router does not spawn a CLI, install a tool, or read credentials.

The five signals are independent, not an exclusive class or a normalized
distribution across executors. A high generative signal may coexist with both
opportunities. A probability near 0.5 is uncertainty about yes/no, not a medium
amount of opportunity. Typed output is not a correctness guarantee.

## Local policy

Pass the tool's JSON result via standard input to:

```text
node "${CLAUDE_PLUGIN_ROOT}/scripts/route-scan.mjs"
```

Use a literal stdin block or the harness's stdin facility, without creating a
file or evaluating tool text as shell syntax. The helper only parses JSON and
prints JSON. A tool error, an MCP error envelope instead of the result body, or
invalid JSON produces `generative` with `invalid-scan`. If stdin execution is
unavailable, use the explicit generative fallback; do not improvise a policy.

[route-scan.mjs](../scripts/route-scan.mjs) is the authoritative executable
policy. It validates the expected IDs, finite probabilities, echoed thresholds,
and upstream invalid-response markers, then computes its own verdicts. It does
not trust an upstream verdict or ask Jev for a route. The ordered rules are:

1. Invalid response, or evidence insufficiency not confidently `no`: generative.
2. Payoff not confidently `yes`: generative.
3. Deterministic opportunity confidently `yes`: consider deterministic reshaping.
4. Otherwise, typed opportunity confidently `yes`: consider typed reshaping.
5. Otherwise: generative, naming uncertainty or lack of a supported opportunity.

The generative signal is retained for residual planning, never used to erase
other opportunities or certify an empty residual. Uncertainty on an unused
signal does not veto an otherwise eligible opportunity. Invalid transport data
does invalidate the scan as a whole. Missing confidence is normal for a Noul.

Thresholds in the request template are conservative **initial policy**, not
empirically calibrated for toolkit tasks. There are no live accuracy or savings
claims. Evaluate representative tasks, wrong-route costs and actual total
latency/cost before changing them. The helper reads the same template so request
and local policy cannot silently use different thresholds.

## Sources and ownership

Contract checked against the marketplace's pinned `jev-code` v0.3.0 on
2026-10-03:

- [Tool contract](https://github.com/FrancoisChastel/jev-code/blob/cee3202c0321e30e6eb1ae968ece6a79d4181f57/skills/jev/references/tools.md)
- [Check implementation and invalid-response behavior](https://github.com/FrancoisChastel/jev-code/blob/cee3202c0321e30e6eb1ae968ece6a79d4181f57/src/tools/check.ts)
- [Official TypeSafe skill](https://github.com/typesafe-ai/skills/blob/65a39f393687675ce170e6094757de20370365b9/skills/typesafe-ai/SKILL.md)
- [Noul semantics](https://docs.typesafe.ai/primitives/noul),
  [state](https://docs.typesafe.ai/concepts/state), and
  [confidence](https://docs.typesafe.ai/confidence)

`jev-code` supplies execution capability. `/typesafe:typesafe-ai` is the
canonical design skill for future typed contracts; this fixed scanner does not
load it on every invocation. Neither upstream owns this router's policy.
