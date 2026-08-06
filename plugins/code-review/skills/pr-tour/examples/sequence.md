# Sequence example — imperative procedure / runtime interaction

Format reference, not a template. Requires 2+ participants exchanging
messages — a single-actor linear procedure reads better as the numbered list
it already is.

Participants cannot take `classDef` styling, so the diff markers ride in the
display names and message labels: ⊕ new, ⊖ removed. `alt`/`opt` carry the
branches, `loop` the retries, `par` the parallelism that dense prose hides.

```mermaid
sequenceDiagram
    autonumber
    participant API as api/orders.ts
    participant Q as queue: order-events ⊕
    participant W as workers/billing.ts ⊕
    participant G as gateway (external)

    API->>Q: ⊕ publish OrderPlaced
    Q->>W: deliver
    activate W
    W->>G: charge(order)
    alt charge ok
        G-->>W: receipt
        W->>W: mark invoice paid
    else gateway timeout
        loop up to 3, exponential backoff
            W->>G: retry charge
        end
        G-->>W: receipt or dead-letter
    end
    deactivate W
    Note over API,G: ⊖ the old synchronous api→gateway call is gone
```

One-line title above the diagram in the real tour: "In what order does a
placed order get charged now?" — the question this type answers.
