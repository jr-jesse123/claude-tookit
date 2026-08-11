# Right-sizing core

Shared rubric for every `arch-docs` component. Both skills and the drift
reviewer answer to these rules — when a step below conflicts with being
helpful or thorough, these rules win.

## The economic test

A document earns its place only when **"code + documentation" costs less than
"code alone"** (Elemar Jr., *Manual do Arquiteto de Software*, vol. 1): the
cost of producing *and maintaining* it must be lower than the savings it
generates in other activities plus the risk it mitigates. When in doubt,
document less — an outdated document costs more than a missing one, because
it is actively wrong.

Two sharper forms of the same test, both from the chapter:

- **A document is useful only if it gets consulted.** One that is never
  actively used is worth less than the bytes committed to it.
- **Effort must match project risk** (Fairbanks): each project faces
  different risks; there is no single right way to document — only the
  appropriate way for this project.

Corollaries:

- Never document what can be reliably recovered by reading the code: class
  inventories, table schemas, endpoint lists, config values. Code is the
  evidence of the solution; documentation records the **intent** behind it.
- Document what the code cannot reveal: goals and constraints, rejected
  alternatives, quality attributes, consciously accepted limitations, and
  the conditions under which a decision should be revisited.

## The significance test

A decision or change is **architecturally significant** when it affects at
least one of:

- availability, security, performance, or scalability characteristics;
- boundaries between modules, services, or domains;
- communication protocols or public contracts;
- data persistence, ownership, retention, or movement;
- deployment topology;
- a technology dependency that is difficult to replace;
- significant operational cost;
- anything expensive or difficult to reverse.

Elemar Jr.'s markers for a decision worth an ADR overlap and extend this
list: it is hard to undo; it implies considerable spending or savings of
time or money; its formulation demanded real team effort (proofs of concept,
trade-off analysis); or it is complex enough to make no sense at first sight
without the background.

**Not** significant: renames, refactors that stay inside a boundary, routine
dependency bumps, bug fixes that restore already-documented behavior, style
changes. Do not manufacture significance to justify producing a document.

## The durability ordering

Since maintenance must cost as little as possible, record first what will
stay true the longest:

1. **Constraints and quality attributes** — the most durable facts about a
   system.
2. **Strategy** — the coherent pattern for decision-making that authorizes
   change: which criteria determine when a component is added, removed, or
   replaced.
3. **Current structure** — last, because it churns. In highly dynamic
   topologies (microservices with discovery, auto-scaling), hand-maintained
   interaction diagrams lose the economic test to automated capture (APM,
   tracing, dependency graphs); document the stable boundaries and let
   tooling report the architecture-of-the-moment.

## The artifact ladder

Every artifact sits on a rung, and every rung above the first requires a
named trigger — one sentence stating the concrete risk it mitigates. No
trigger, no artifact.

**Tier 0 — no `docs/architecture/` at all.** A small single-purpose library
or tool, one or two maintainers, no external consumers: an "Architecture"
section in the top-level README plus an `adr/` folder (when a significant
decision ever appears) is the right size. Recommending Tier 0 is a success,
not a failure of the skill.

"Starting with a Haiku and ADRs is a solid first step in the right
direction" — the chapter's own bottom line. Tier 0 is exactly that, with the
Haiku living in the top-level README.

**Tier 1 — the core set.** Default for a mid-sized product repo (multiple
integrations, more than a couple of contributors, expected to outlive its
authors' memory):

| Artifact | Answers |
| --- | --- |
| `README.md` | navigation map only — where is what |
| `overview.md` | an Architecture Haiku — one page: solution summary, context, constraints, prioritized quality attributes, key decisions with trade-offs |
| `diagrams/system-context.md` | who uses it, what it depends on (C4 L1) |
| `diagrams/containers.md` | what runs, what stores, what talks to what (C4 L2) |
| `adr/` | why it is built this way |

**Tier 2 — risk-added.** Each item only with its trigger written into the
scaffold-time proposal:

| Artifact | Trigger (examples) |
| --- | --- |
| `diagrams/critical-flows.md` | a flow whose behavior is not obvious from the container diagram: sagas, retries, money movement, idempotency |
| `diagrams/deployment.md` | more than one deployable unit, multi-region, or non-obvious scaling topology |
| `quality-attributes.md` | SLOs, regulatory pressure, or a characteristic the team actively trades against — expressed as measurable scenarios |
| integration contracts (OpenAPI/AsyncAPI links) | other teams or external parties consume the interfaces |
| ownership map | more than one team owns parts of the system |
| component view (C4 L3) | one container's internal structure is genuinely complex |
| threat model, resilience strategy, capacity, risk register, regulatory traceability | the corresponding risk is real, named, and current |

## Diagram semantics

- C4 defines **what** to communicate; Mermaid is only **how** it renders.
- Every arrow carries a label naming the interaction kind: `sync:` (request/
  response), `event:` (publication/subscription), `data:` (batch/replication),
  `dep:` (build/library dependency), `deploy:` (deployment relationship).
  An unlabeled arrow is a defect — diagram as code is not diagram without
  method.
- Context + Container are the default levels. Component only with a named
  trigger; the Code level almost never earns its maintenance cost.
- Nodes name real things — actual service names, actual external systems —
  never generic placeholders left in a committed diagram.

## The maintenance rule

A change triggers the documentation question when it touches: module or
service boundaries, communication protocols, public contracts, data
persistence or ownership, deployment topology, security mechanisms,
architectural characteristics, or a previously documented decision.

Not every trigger produces a new ADR or diagram — but every trigger must
produce an explicit answer to the question, even when the answer is "nothing
to update".

## Human knowledge vs machine knowledge

The model may draft from evidence found in the repository: code, diffs,
benchmarks, configs, linked issues. It must **never invent**: negotiations
with stakeholders, budget constraints, organizational limitations, regulatory
requirements, operational incidents, or historical context. Anything in those
categories comes from the human — or appears in the artifact as an explicit
`TODO(human): <specific question>` marker or open question. Plausible
invented prose in a "why" field is worse than an empty field: it records an
intent that never existed.
