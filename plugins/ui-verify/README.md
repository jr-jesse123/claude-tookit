# ui-verify

Plan, run and judge a UI verification in a real browser, on a named target environment (int, local, staging...), from a ticket or a description. Two modes: `repro` (reproduce a bug: the ticket's actual result is the expected outcome) and `verify` (check a feature against its acceptance criteria).

It is the orchestration layer above `ui-evidence`: `ui-evidence` records trustworthy evidence of one run; `ui-verify` decides what to run, in which stages, with which agent, checks who is logged in after every account change, and closes the run with facts, a verdict, packed traces and trimmed videos.

Install: `/plugin marketplace add jr-jesse123/claude-tookit`, then `/plugin install ui-verify@jr-claude-toolkit` (and `ui-evidence@jr-claude-toolkit` for record stages).

| Component | Name | What it does |
| --- | --- | --- |
| skill | `/ui-verify:ui-verify <ticket-or-description> [repro\|verify] [<target>]` | The controller: frame, plan, ask, run read-only stages, phase B, approve writes, run write and record stages, verdict, close. Runs in the main session because only it can ask the user. |
| agent | `ui-verify:ui-planner` | Opus. Expands preconditions from code, the UI catalog and the project's planning notes; picks stages, executor tier of each write and the oracle reads; writes `plan.md` (and a `cases.md` draft). Never opens a browser. |
| agent | `ui-verify:ui-browser` | Sonnet or Haiku, as the plan says. Runs one approved stage through the Playwright MCP, reaching pages by clicking, inside a Playwright trace, and reports facts (answers, steps, catalog notes, console counts, deviations, trace path). Does not plan, judge or fix. |
| agent | `ui-verify:ui-browser-measure` | The same plus read-only `browser_evaluate` for values the page does not show as text, only for stages whose plan lists the exact expressions. |
| script | `scripts/pack-trace.py` | Packs one Playwright MCP trace, by id, into a self-contained zip and an action list (and, on request, a captioned video). Never mixes traces of the same session. |
| script | `scripts/trim-idle-video.py` | Cuts the idle stretches out of a recording, keeps every frame where something moves, and joins the parts of a case. |
| script | `scripts/trace-summary.py` | One line per span of a Jaeger-format trace, with `--grep` on the operation. |
| script | `scripts/session-usage.py` | Token usage of a session and its subagents by role, with `--since` and `--until` to cut a window. |
| reference | `references/plan-format.md` | The plan contract: names (verification › stage › step, never `S7`/`W4`), summary, header, stages, writes with tiers and target checks, trace questions, verdict. |
| reference | `references/target-profile.md` | What a project writes per environment: hosts, pre-run checks, login, account check, write policy, backend evidence, build check, quirks. |
| reference | `references/project-config.md` | `.claude/ui-verify.json` and the split between what the project provides and what the plugin provides. |
| reference | `references/catalog-contract.md` | The optional UI catalog the executors read. |

## What stays in the project

The plugin knows nothing about your application. The project provides:

- **Target profiles** (`.claude/ui-targets/<target>.md`): hosts, how to log in and out, the account check, the write policy with the author and date of the decision, how backend evidence is read, the build check.
- **A UI catalog** (optional): per page, the test ids and how to reach it. Without one, executors find elements by role and text and plans use more `explore` stages.
- **Planning notes** (optional): the domain rules a plan must respect.
- **An agent that reads backend logs and traces** (optional): the profile's "Backend evidence" section names it. The plugin only passes it the run's window, ids and questions.

A profile can declare a target a sandbox: writes are then announced and run without an approval stop, and whatever the profile reserves (resets, deletes of existing data) still needs a yes. Without that declaration every write needs a yes, only on data the run creates.

## Requirements

- A Playwright MCP server with `--caps devtools` (tracing and video tools); `--isolated` lets several Claude sessions each have their own browser. Pin its version.
- The `ui-evidence` plugin, for `record` stages.
- Optional: a tracker MCP for the planner. Its tool list names Linear and basic-memory tools. When they are missing, the skill puts the ticket text in the prompt; copy the agent into the project's `.claude/agents/` to change the list. Not verified: how the harness treats a listed tool whose server is absent.
- `uv` for the scripts that declare dependencies (`pack-trace.py`, `trim-idle-video.py`, `session-usage.py`); `trace-summary.py` is plain Python.

Agent definitions load when a session starts: restart the session after installing or updating the plugin.

## Origin

Extracted from a workspace that verified a multi-app web product on a shared integration environment and on a local one. What it measured there: one Opus planning call, Haiku executors for mapped read and write stages, and a controller whose context is the main cost (`session-usage.py` reports it). The plugin keeps those mechanisms and none of the product.
