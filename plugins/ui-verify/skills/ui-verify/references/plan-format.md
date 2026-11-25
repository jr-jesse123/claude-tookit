# Plan format (`plan.md`)

The contract between `ui-planner` (writes it), the `ui-verify` skill (shows it, records the approval, runs the stages) and `ui-browser` (runs one stage). One plan per evidence folder: `<evidenceRoot>/<date>-<KEY>-<slug>/plan.md`.

The recorded part of a plan is also written as `cases.md` (the `ID` column holds the verification name) in the exact format the `ui-evidence` plugin expects for delegated runs (`ui-evidence:ui-evidence`, "Delegated runs") (cases table, selectors, listed writes, approval line). The plugin's file is a contract of its own: the planner only drafts it, the orchestrator writes the approval line, and any change after approval needs a new approval.

## Names
Every verification, stage, step and write has a meaningful name, and every reference to it (in the plan, `cases.md`, `stage-results.md`, the README, agent prompts and reports, and messages to the user) uses that name, never a position or a letter-number code (`S7`, `W4`, `C2`).

- Three levels: a **verification** (what is to be proved, one row of `cases.md`) contains **stages** (one executor run each), and a stage contains **steps** (one action or read each). A write belongs to the step that performs it.
- A reference is the path of names, `verification › stage › step`; the shortest part that is unambiguous is enough in conversation.
- A name is a kebab-case ASCII slug in English that says the effect, not the position: `admin-sees-new-user`, `create-user-form`, `submit-as-admin`. Not `step-1`, not `s7`.
- Unique inside its parent and stable: renaming voids the approval, like any edit.
- Order is the position in the list, never part of the name. The stage `type:` stays a separate field.
- Open questions, hand-off notes and the trace files are named after the stage (`<stage-name>.trace.zip`).

## Summary
At most 10 lines at the top of the file: oracle, expected outcome and why, stages with executor tier, writes, and the open questions the user must answer. The orchestrator shows this to the user.

## Header
- `mode`: `repro` (oracle = the ticket's Actual Result, a failure is the expected outcome) or `verify` (oracle = acceptance criteria, a pass is the expected outcome, negative cases derived).
- `target`: the target's name. Its profile (`references/target-profile.md`) is part of the plan's inputs: hosts, accounts, write policy, backend evidence and build check come from it.
- `phase`: `A` (no browser reads yet) or `B` (after the measure stage).
- Ticket, target, and the build check the target profile describes: which build of the service under test runs there, and how to read it. A deployed fix or feature branch changes the outcome.
- Oracle, verbatim from the ticket, and the reads that decide it.

## Preconditions
One line per link of the chain the oracle needs, expanded from code, the UI catalog and the project's planning notes, not from the ticket text. Each: what must exist, how it is measured on screen, how it is closed through the UI, or `suggest non-UI setup` with the reason (second role only for data, long async wait, bulk data, admin or flags). Who owns the data: `ours` or `shared`.

## Stages
In order. Each stage is one executor run with fresh context.

```
### <stage-name>
verification: the verification(s) this stage serves, by name (a setup stage names the one it prepares)
type:      switch | measure | explore | run | record
account:   email and organization expected during the stage (on the target's app)
executor:  haiku | sonnet, with the reason (write tier, unmapped pages)
agent:     ui-browser (default) | ui-browser-measure (only when a read is tagged instrument)
catalog:   catalog files to load (routes, widgets, flows)
pre:       state to check on screen first; if false, stop
steps:     named steps, in order; each `<step-name>: click path in plain words, with testids from the catalog (mark ids not in the catalog)`, and `writes: <entry>` on the step that writes
reads:     values to read verbatim, with the regex or text that finds them; an instrument read is written `instrument: <exact JS expression> on <element>` and needs agent ui-browser-measure
writes:    the entries of the steps that write (see Writes); none for read-only stages
abort:     stop rules specific to the stage
post:      state that must hold at the end
handoff:   what the next stage needs, in a few lines (names, counts, where the browser is left)
budget:    tool calls
```

Stage types:
- `switch`: logout, verify, login, org pick. The orchestrator checks `CurrentUser` after it, not the executor.
- `measure`: read-only. Reads the state the oracle depends on so the plan can be finalised (phase B). Skipped when the run creates its own data or the ticket gives the state. Reads lists and opens at most 3 items of a kind; split into two stages when more are needed.
- `explore`: read-only, for a page or step the catalog marks unmapped. Stops before the first write; records selectors, labels, blockers.
- `run`: setup steps that are not recorded.
- `record`: the stage that gets the video and the oracle reads, as `cases.md`.

## Tracing
Every stage run by `ui-browser` or `ui-browser-measure` is one Playwright trace: the agent starts it first and stops it last and reports the `trace-<id>.trace` path. The orchestrator writes the id next to the stage in `stage-results.md`. The MCP keeps all traces of a session in one folder, so a trace is only ever packed by its own id (`scripts/pack-trace.py`), which copies just the files that trace cites; never zip the folder. Traces and packed zips older than the run's retention need can be deleted. The trace is the complete history of the run; the `record` stage keeps its `.webm` and screenshots for the key moments. A video of any trace is built on demand with `pack-trace.py --video`.

## Instrument reads
User actions stay natural (click, type, drag). A value the page does not show as text (a column width, a computed style, a stored setting) may be read with `browser_evaluate` through `ui-browser-measure`. Each one is listed in the stage `reads` with its exact expression, read-only (no assignment, events, network calls or DOM changes), and says why text or a screenshot is not enough. The user's approval of the plan is the explanation the standing rule asks for; the executor reports each one verbatim and the README marks them as instrument reads.

## Writes
One entry per write, named by its path, all in one list at the end as well:

`<stage-name> › <step-name>: <environment>, <what is written>, <entity and exact name>, undo: <how>, tier: <haiku|sonnet>, target check: <what on screen names the target at commit time, or "none">`

Tier rule: `haiku` only when the target can be confirmed unambiguously on screen at the moment of commit (exact row text scoped, dialog naming the item). A dialog that names nothing, duplicate names, or shared data the run did not create means `sonnet` with the user's confirmation. Irreversible writes on shared data are never planned without an explicit user decision. Only data the run creates is written.

## Trace questions
What the backend should show for the run, for the backend evidence reader the profile names: the service and operation or consumer expected after each write (for example a consumer span after a create), the ids that identify the run's entities, and what an error would look like. Read-only; one line per question. Omit the section when the oracle is purely visual.

## Unmapped
Pages, steps or ids the plan needs that the catalog does not cover. Each gets an `explore` stage or an open question.

## Open questions
What the planner could not resolve: missing accounts, ambiguous ticket text, build on the target unknown. The orchestrator asks the user; the planner does not.

## Approval
Written only by the orchestrator: who approved, ISO time, and that it covers the stages and the writes as they stand. Left empty by the planner.

## Verdict (after the run, `repro` mode)
`reproduced` | `not reproduced` | `inconclusive`, with the reads that decide it, up to three hypothesis-backed variations to try, and what to hand to the developer or to a manual repro.
