# Mindmap and timeline examples — breadth and phases

Format reference, not a template. Rare types; comprehension outranks PR-page
rendering, so use them when they fit — but only if the user says they will
paste the tour into GitHub, offer a `flowchart`/list fallback (these two
render less reliably there). No styling hooks: ⊕ markers carry the diff.

## Mindmap — broad diff touching loosely related areas ("what does this touch?")

```mermaid
mindmap
  root((PR: billing revamp))
    Billing core
      billing/charge.ts
      billing/retry.ts ⊕
    API surface
      api/orders.ts
      api/refunds.ts ⊕
    Ops
      alerts/billing.yml ⊕
    Docs
      README.md
```

Use it as the opening overview of a sprawling PR, before per-group tours —
it answers breadth, not connection; pair it with a flowchart per group when
connections matter.

## Timeline — phased work ("what happens in which phase?")

```mermaid
timeline
    title Migration to async billing
    Phase 1 (this PR) : dual-write behind flag ⊕ : workers deployed idle ⊕
    Phase 2 : flag ramp-up : sync path measured
    Phase 3 : remove sync path : drop legacy columns
```

Mark which phase this PR is — the reviewer's question is usually "how much of
the plan am I approving right now?"
