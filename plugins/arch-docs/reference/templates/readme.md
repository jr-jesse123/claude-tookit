# Architecture documentation

Navigation map only — the knowledge lives in the linked files. Do not
accumulate content here.

| Question | Where |
| --- | --- |
| What is this system, its constraints and priorities? | [overview.md](overview.md) |
| Who uses it and what does it depend on? | [diagrams/system-context.md](diagrams/system-context.md) |
| What runs, stores, and talks to what? | [diagrams/containers.md](diagrams/containers.md) |
| Why is it built this way? | [adr/](adr/) |

## Maintenance rule

A pull request must answer the documentation question — explicitly, even if
the answer is "nothing to update" — whenever it touches: module or service
boundaries, communication protocols, public contracts, data persistence or
ownership, deployment topology, security mechanisms, architectural
characteristics, or a previously documented decision.

Recording a decision: `/arch-docs:adr` drafts it and interviews you for the
context the code cannot reveal. Checking a diff: the `arch-docs:drift-reviewer`
subagent reports which of these files need attention.
