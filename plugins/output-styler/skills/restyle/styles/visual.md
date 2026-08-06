# visual — Diagrams and tables first, prose where a picture can't reach

The content's *shape* becomes visible: flows become flowcharts, comparisons
become tables, lifecycles become state diagrams. Mermaid renders natively in
Claude Code and in artifacts — no external tooling. Prose survives only to
say what a picture cannot (the why, the caveats).

## Pick the form from the content's shape

| The content is… | Reader's question | Form |
| --- | --- | --- |
| A process, pipeline, dependency map | what leads to what? | `flowchart` |
| An interaction between 2+ components over time | who calls whom, in what order? | `sequenceDiagram` |
| A lifecycle, statuses, retries | what states, what triggers each move? | `stateDiagram-v2` |
| Options being compared | how do they differ? | table, criteria as rows |
| A composition or taxonomy | what belongs to what? | `mindmap` |
| Phases, chronology, rollout | what happens when? | `timeline` |
| Quantities, trends | how much, compared to what? | load the `dataviz` skill first, then chart |

## Rules

1. **One primary visual** answering the content's central question. A second
   only if it answers a *different* question, with a one-line title naming
   it. Never a third.
2. **Nodes name real things** from the original text — actual files,
   commands, components, options. No generic "System" / "Process" boxes.
3. **Short labels** (≤ 4 words); detail goes in the caption, not the node.
4. **Caption under every visual**, ≤ 3 lines: what to notice, not a
   restatement of the boxes.
5. **Remaining prose is only what the picture can't say** — rationale,
   trade-offs, caveats. If a sentence repeats an edge or a row, delete it.
6. **Color is never the only signal** — pair it with shape, stroke, or a
   marker; light fills need explicit dark text (`color:#111`) to survive
   dark themes.
7. **Dense content → offer an artifact**: when the result needs more than
   two visuals or side-by-side layout, propose rendering it as an HTML
   artifact page instead of flooding the chat.
8. End with *Omitted:* naming whatever nuance the visual could not carry.

## Before

> The request first hits the edge cache; on a miss it goes to the
> application, which checks Redis, and only on a second miss does it query
> Postgres, after which both caches are populated on the way back.

## After

> ```mermaid
> flowchart LR
>     R[Request] --> E{Edge cache}
>     E -- hit --> OK[Response]
>     E -- miss --> A[Application] --> X{Redis}
>     X -- hit --> OK
>     X -- miss --> P[(Postgres)] --> W[Populate both caches] --> OK
> ```
> Two cache layers fail independently — only a double miss reaches Postgres,
> and the write-back fills both on the return path.
