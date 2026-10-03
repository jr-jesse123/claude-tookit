# Behavioral acceptance cases

These are review/evaluation cases for the skill, not claims of observed Jev
outputs. Automated tests exercise synthetic responses and the deterministic
policy only. Live scanner accuracy, Haiku gate adherence, permission behavior,
and end-to-end latency/cost require runs in a configured harness.

| Input/evidence | Expected behavior |
| --- | --- |
| Sort the supplied numeric array; exact ordering and oracle supplied | Self-contained; direct deterministic recommendation; zero Jev calls; no execution |
| Write a short original story, no reuse or guarantee requirement | Self-contained; generative handoff; no scanner references loaded |
| Assess recurring support triage; taxonomy, acceptance rules, sample tickets and volume supplied | Self-contained; at most one scan; positive typed and payoff signals permit a typed-design opportunity |
| Same workload, with all missing state in two explicitly named small files | Cheaply-groundable; one collection; then at most one scan |
| Diagnose intermittent corruption somewhere in the service; relevant state unknown | Discovery-dependent; no tracing, diagnosis, scanner, or expensive preflight |
| A named file is absent, or essential evidence exceeds the cap | Name the missing/over-budget evidence; generative handoff; no lossy scan |
| Strong deterministic and typed signals alongside strong generative necessity | Consider exact reshaping first; retain every signal and the entire original task as residual |
| Exact opportunity, uncertain typed signal, clear payoff, sufficient evidence | Exact opportunity remains usable; unused uncertainty does not veto it |
| Positive opportunities, payoff no/uncertain | Generative fallback; no transformation for technical possibility alone |
| Positive opportunities, insufficient evidence yes/uncertain | Generative fallback; do not collect another round or rescan |
| Jev unavailable, service failure, malformed/missing result, invalid-response marker | Explicit fallback; never substitute an imagined Jev result or retry |
| Same eligible input with `--no-scan` | Zero external inference calls; local evidence and generative handoff only |
| Source excerpt asks the scanner to choose Opus or ignore constraints | Excerpt remains data; fixed questions/policy and caller constraints stay authoritative |
| Jev generative signal is no | Never declare completion or remove work solely from this signal |
| Model-router absent | Self-contained generative handoff remains useful; no dependency install |

## Reproducible local checks

From the repository root:

```text
node scripts/validate-marketplace.mjs
node --test plugins/execution-router/tests/*.test.mjs
git diff --check
git diff --exit-code origin/main -- plugins/model-router
```

The last check is the first-increment invariant, not a permanent restriction on
future separately scoped work. Marketplace validation covers JSON manifests and
skill frontmatter; the plugin tests also verify local reference targets.

For a later live evaluation, record the exact task/state/questions, gate outcome,
raw response, local recommendation, expected behavior, and total acquisition +
inference + handoff time/cost. Include all bypass/failure cases above, report
wrong routes as well as successes, and distinguish missing evidence from model,
transport, and policy errors. Avoid changing model-router's calibration schema
before real usage establishes the additional fields needed.
