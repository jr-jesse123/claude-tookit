# Flowchart examples — painted delta and painted before/after pair

Format reference, not a template. Skip flowcharts entirely for 1–2 file
groups.

## Painted delta (the default): union of before and after, diff in the styling

One diagram answering "who depends on whom, and what changed in that graph?"
— added solid/thick with ⊕, removed dashed with ⊖, untouched context dimmed.

```mermaid
flowchart LR
    A[api/orders.ts] -->|"⊖ direct call"| B[billing/charge.ts]
    A -->|"⊕ publish"| Q[["queue: order-events ⊕"]]
    Q --> W["workers/billing.ts ⊕"]
    B --> C[(db)]
    W --> C

    classDef added fill:#e0f5e6,stroke:#0a7d33,color:#111,stroke-width:2px
    classDef removed fill:#ffe3e3,stroke:#c00000,color:#111,stroke-dasharray:6 4
    classDef ctx fill:none,stroke:#999999,color:#888888

    class Q,W added
    class B removed
    class A,C ctx
    linkStyle 0 stroke:#c00000,stroke-dasharray:6 4
    linkStyle 1,2 stroke:#0a7d33,stroke-width:2px
    linkStyle 3,4 stroke:#999999
```

## Painted before/after pair: only when the topology change IS the story

Two diagrams, same orientation, untouched nodes (`api/orders.ts`, `db`) kept
with the same name and dimmed style in both — they are the anchors. The
"before" paints what leaves; the "after" paints what arrives. Never ship an
unpainted pair.

**Before — what leaves (⊖):**

```mermaid
flowchart LR
    A[api/orders.ts] -->|"⊖ direct call"| B[billing/charge.ts]
    B --> C[(db)]
    classDef removed fill:#ffe3e3,stroke:#c00000,color:#111,stroke-dasharray:6 4
    classDef ctx fill:none,stroke:#999999,color:#888888
    class B removed
    class A,C ctx
    linkStyle 0 stroke:#c00000,stroke-dasharray:6 4
    linkStyle 1 stroke:#999999
```

**After — what arrives (⊕):**

```mermaid
flowchart LR
    A[api/orders.ts] -->|"⊕ publish"| Q[["queue: order-events ⊕"]]
    Q --> W["workers/billing.ts ⊕"] --> C[(db)]
    classDef added fill:#e0f5e6,stroke:#0a7d33,color:#111,stroke-width:2px
    classDef ctx fill:none,stroke:#999999,color:#888888
    class Q,W added
    class A,C ctx
    linkStyle 0,1 stroke:#0a7d33,stroke-width:2px
    linkStyle 2 stroke:#999999
```

Notes carried by these examples: nodes named by real paths (symbol + path for
sub-file pieces, e.g. `charge() · billing/charge.ts`); `linkStyle` indices
match the edge order in the code — paint edges last; color never the only
signal (dash/weight + ⊕/⊖ ride along).
