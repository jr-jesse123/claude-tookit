---
name: pr-tour
description: Build a guided tour of a pull request or branch — how the changes connect (narrative plus Mermaid diagrams when they help), a contracts section when the diff introduces, changes, or removes a promise other code relies on (types/interfaces, events, endpoints, schemas, config keys, CLI flags — promise delta with before→after where both exist, a new contract has no before and a removed one no after, compatibility verdict, blast radius), and a suggested file-by-file reading order with what to focus on in each. Use when the user wants to understand or start reviewing a PR, not to find bugs.
argument-hint: [PR number/URL or branch; defaults to current branch vs default branch]
allowed-tools: Bash(git fetch:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git merge-base:*), Bash(git symbolic-ref:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(npx --yes @zabaca/mermaid-validate:*), Read, Grep, Glob
---

# PR tour

Orient a reviewer before they read a single diff hunk: explain how the changes
connect, then say in what order to read the files and what matters in each.

This skill does not review. It reports no bugs, no style issues, no missing
tests — for findings, point the user to `/code-review:quick-review`. Write the
tour in the language the user is speaking.

## Resolve the target

Decide which diff to tour, in this order:

1. `$ARGUMENTS` looks like a PR number or URL → `gh pr view <ref> --json
   title,body,baseRefName,headRefName` for context, `gh pr diff <ref>` for the
   diff. If `gh` is missing or unauthenticated, say so and treat the argument
   as a branch name instead.
2. `$ARGUMENTS` is a branch → diff it against the merge-base with the default
   branch: `git diff $(git symbolic-ref refs/remotes/origin/HEAD)...<branch>`.
   If the symbolic ref is not set in this clone, fall back to `origin/main`,
   then `origin/master`. Run `git fetch origin` first when the remote refs
   look stale — a stale base silently drags already-merged work into the
   tour.
3. No argument → same as 2, with the current branch.

Also gather `git log --oneline` and `git diff --stat` for the same range. Use
the PR title, body, and commit messages as context for the narrative — the
author already said what they meant to do.

If the diff is empty, say so and stop. Do not tour the last commit unless the
user asks for it.

## Map the change

The diff alone rarely shows how pieces relate — read before you narrate.

1. Tag each changed file with a role: **contract** (types, schemas,
   interfaces, public API), **core logic**, **wiring** (call sites, routes,
   DI, config), **tests**, **generated** (lockfiles, snapshots, build
   output). These roles are a lens, not a form — for a diff that is mostly
   docs, config, or prose, substitute roles that fit (e.g. spec, procedure,
   example, manifest).
2. With Read and Grep, trace the connections *among the changed files*: which
   changed function is called by which changed caller, which new type flows
   into which consumer. This graph drives both the narrative and the order.
3. Split into independent groups. Two files belong to the same group only if
   one calls, imports, or tests the other — directly or through another
   changed file. A feature, an unrelated refactor, and a dependency bump are
   three groups. Docs and metadata that call nothing (README, manifests,
   changelogs) join the group they describe; when one such file spans several
   groups, put those files in a final housekeeping group instead of forcing
   them into one.

**Fan out on large diffs.** Above ~20 changed files (excluding generated), or
whenever the split yields several independent groups, do steps 1–3 with cheap
evidence only — paths, `git diff --stat`, import-level Grep, no full file
reads — and delegate the deep tracing: one `code-review:mapper` agent per
group, spawned in parallel with at most 4 in flight; when there are more
groups, run them in waves, most substantive groups first (the report is
ordered that way anyway). Each mapper's prompt must be self-sufficient (the
agent sees none of this conversation): the diff range, the group's file list
with change statuses, the other groups' file lists (so it can flag boundary
errors), and a pointer to return its documented map format. The mappers
return facts — call-graph edges, verbatim contract deltas with grep-found
blast radius, reading-order candidates, diagram-worthy spots. Everything
downstream stays here: the narrative, the diagram choice and painting, and
the contracts section's compatibility verdicts are written *from the maps*,
at this session's full model — judgment does not ride along with the
delegation. Apply any boundary corrections the mappers report (merge groups
joined by a verified edge) before writing, and open a changed file yourself
only when a map is missing a quote or anchor you need.

Below the threshold, map inline as steps 1–3 describe — spawning overhead
buys nothing on a small diff, and the files you read while mapping stay in
context for the review conversation that usually follows the tour.

## Report — how the changes connect

A cohesive PR gets one tour. Independent groups each get their own complete
tour — narrative, optional diagrams, reading order — ordered from the most
substantive group to the most trivial. Do not add group headers when there is
only one group.

**Narrative.** One paragraph per group: entry point of the change → what
triggers what → net effect. Name real files and symbols, not abstractions.
This paragraph is the answer to "what do these changes do together?" — if the
reviewer reads nothing else, this must be enough to start.

**Diagrams.** Default is a single Mermaid `flowchart`: nodes are the changed
modules plus any untouched neighbors needed as context (dimmed), edges are
call or data flow between them, with added, modified, and removed elements
painted distinctly (see *Painting the diff* below). Skip the diagram entirely
when the group touches only 1–2 files — the paragraph covers it.

Multiple diagrams are an explicit option when distinct perspectives or zoom
levels help more than one picture can — for example, an overview `flowchart`
of the modules plus a `sequenceDiagram` of the runtime flow, or a macro map
plus a zoom into the most-changed subsystem. Each diagram must answer a
different question ("who depends on whom?" vs "in what order does it happen?"
vs "what does the hot spot look like inside?") and carries a one-line title
naming that question. If two diagrams answer the same question, keep one. The
criterion is clarity, never quantity.

**Picking the type.** The reviewer's question selects the diagram — dense
procedural blocks in the diff deserve the type that matches their shape:

| Complexity in the diff | Reviewer's question | Diagram |
| --- | --- | --- |
| Structure: new modules, dependencies, wiring | who depends on whom? | `flowchart` |
| Imperative procedure; runtime interaction between components | in what order? who calls whom? | `sequenceDiagram` — `alt`/`loop`/`par` for branches, retries, parallelism |
| Lifecycle, entity status, flags, retry/backoff | what states exist, what triggers each transition? | `stateDiagram-v2` |
| Schema, migrations, data model | how do the entities relate? | `erDiagram` |
| Contracts between types (inheritance, composition) | what is the contract between types? | `classDiagram` |
| Dense conditional logic (validation, routing, dispatch) | which path does the input take? | `flowchart` with decision nodes |
| Broad diff touching many loosely related areas | what areas does this change touch? | `mindmap` |
| Phased work: rollout, migration steps, deprecation | what happens in which phase? | `timeline` |
| Restructuring where the topology itself is the story | how was it wired before vs after? | painted before/after pair of `flowchart`s — see *Painting the diff* |

A `sequenceDiagram` needs two or more participants exchanging messages — a
single-actor linear procedure reads better as the numbered list it already
is. A state machine hiding in scattered `if`s is the case most worth drawing:
it is exactly where a reviewer gets lost reading a diff.

The tour's first goal is the reviewer's own comprehension, above PR-page
rendering — pick whichever type fits, including `mindmap` and `timeline`,
when it is the right tool for that situation. Only if the user says they will
paste the tour into GitHub, note that `mindmap`/`timeline` render less
reliably there and offer a `flowchart`/list fallback.

**Anchoring nodes.** Every node is named after a real path — `billing/charge.ts`,
never "Billing Service"; a node that stands for a piece smaller than a file
carries the symbol too: `charge() · billing/charge.ts`. The same file name in
the diagram and in the reading order is what lets the eye jump between the
two. Line numbers stay out of diagrams — they shift on every push, and their
home is the reading-order entry, where `path:line` is clickable — with one
exception: a changed hunk buried in a large file may anchor its node as
`charge() · billing/charge.ts:L142`, noting the line is valid at the branch's
current HEAD.

**Painting the diff.** Structural diagrams carry the diff in their styling.
The default is one *painted delta*: draw the union of before and after, with
added elements solid and thicker (`classDef added`, ⊕ in the label), removed
elements dashed (`classDef removed`, ⊖), modified elements in the default
styling — undimmed and unmarked, the baseline the exceptions stand out from —
and untouched context dimmed gray. Paint edges with `linkStyle` to match: an
edge that exists only before the change is removed, only after is added.

When a restructuring changes the topology so much that the delta becomes a
tangle of marks (sync calls → event queue, monolith chain → workers), draw a
*painted before/after pair* instead: the "before" diagram paints what leaves,
the "after" paints what arrives, and the untouched nodes appear in both with
the same name, position, and dimmed style — they are the anchors the eye uses
to compare the two shapes. Never ship an unpainted pair: side-by-side
diagrams without painted diffs push the visual diffing onto the reviewer.

Painting rules:

- Color is never the only signal. Pair it with stroke style (dashed vs
  solid/thick) and ⊕/⊖ markers, so the diagram survives color-blind readers
  and renderers that drop styles.
- `linkStyle` targets edges by index — paint edges last, once the edge list
  is final, and check the indices one by one.
- Light fills need an explicit dark text color (e.g. `color:#111`) so labels
  stay readable on dark themes.

**Validate before presenting.** When `npx` is available, run each fence
through the official mermaid parser before showing the tour — the command
must start with `npx` (a leading `echo ... |` would not match the allowed
tool prefix), so feed the body via heredoc:

```
npx --yes @zabaca/mermaid-validate - <<'DIAGRAM'
<fence body>
DIAGRAM
```

On failure, fix and re-validate; double-check `linkStyle` indices against the
edge order, which the parser only partially covers. If `npx` is unavailable
or offline, skip silently — never block the tour on validation.

**Examples — read only what you selected.** Few-shot references live in the
`examples/` directory next to this SKILL.md, one file per diagram type: `flowchart.md`
(painted delta + before/after pair), `sequence.md`, `state.md`,
`er-class.md`, `mindmap-timeline.md` — plus `prose.md` for the narrative and
reading order at three PR sizes (small, medium, large with group splits),
and `contracts.md` for the contracts section below (read only when that
section applies). After the selector has picked the type(s), read the
matching file(s) and `prose.md`; never read the whole folder. They are
format references, not templates — size the real tour to the real diff.

## Report — contracts (only when the diff touches one)

A contract is a promise other code relies on without reading the
implementation: an exported type or interface, a function signature, an
event name and its payload, an HTTP/RPC endpoint, a DB schema, a config
key, a CLI flag. When a group introduces, changes, or removes such a
promise, insert this section between its narrative and its reading order —
one entry per contract. When the diff touches no contract, omit the
section entirely; a diff of pure implementation gets no empty
"Contracts: none".

Each entry moves promise → verdict → radius:

```
- `Invoice.status` · `src/billing/schema.ts:12` — union widened:
  `"open" | "paid"` → `"open" | "paid" | "refunded"`. Additive for
  producers; breaking for exhaustive consumers. Bound by it:
  `billing/report.ts:88` (switch, updated here), `export/csv.ts:31`
  (switch, **not in this diff**).
```

- **Promise delta** — quote the contract in its own language, before →
  after: the old and new type or signature, payload fields, verb + route +
  status codes, column set. Never paraphrase a shape the reader could be
  shown.
- **Compatibility verdict** — *additive* (existing readers and writers keep
  working) or *breaking*, always with direction: for whom. Direction is
  where reviewers slip — a widened union or return type is additive for
  producers but breaks exhaustive consumers; a widened parameter is the
  reverse; a new member on an interface reads as an addition in the diff
  but is breaking for every implementor.
- **Blast radius** — who is bound by the promise, found with Grep (or taken
  from a mapper's map on a fanned-out tour), never
  assumed: producers, consumers, implementors, each anchored `path:line`
  and marked as updated in this diff or **not in this diff**. The off-diff
  consumers are the reason this section exists — the diff cannot show
  them. Consumers that Grep cannot reach get a one-line note instead: API
  clients outside the repo, rows and messages persisted under the old
  shape, serialized payloads, `any`-typed call sites, reflection.

**Quoting in blocks.** A one-line delta stays inline, as above. When the
shape does not fit a line — a record with several fields, a payload
schema, an endpoint with request, response, and status codes — quote it in
a fenced code block in the contract's native notation; the fence is the
visual aid, syntax highlighting included:

- The repo's own contract artifact first, when one exists: the changed
  fragment of its OpenAPI/JSON Schema (` ```yaml `/` ```json `), protobuf,
  GraphQL SDL, SQL DDL — never a spec fabricated for the tour; for a
  code-first endpoint the honest quote is the source signature or a
  compact ` ```http ` request/response sample.
- Otherwise the conventional notation for the kind: the source language
  for types and signatures (` ```ts `, ` ```fsharp `, …), a ` ```json `
  payload for events.
- Carry the painting language into the block: ⊕/⊖ as comments on added and
  removed lines; or a ` ```diff ` fence when before and after interleave —
  it trades syntax highlight for +/− painting, pick per block.
- Quote the delta plus the minimum context needed to read it, never the
  whole type or document; the verdict and the radius stay in the prose
  around the block. The structural picture stays with the diagrams
  (`classDiagram`/`erDiagram`) — the block shows the promise's text, not
  its neighborhood.

The ends of the spectrum follow the tours' painting language. A **new
contract** (⊕) has no before: quote the promise being made, and in place
of a break the verdict names the commitment — what surface is now
promised, to whom (public API? internal? persisted?), and so what will be
expensive to change later. Its radius is the consumers this diff wires up;
"no consumers outside this diff yet" is worth saying — it tells the
reviewer this is the cheapest moment the contract will ever have to be
reshaped. A **removed contract** (⊖) has no after: breaking by definition;
Grep for stragglers still bound to it that the diff missed.

By kind, what the promise consists of:

| Contract | Quote as the promise | Easy to miss |
| --- | --- | --- |
| Types, interfaces, signatures | exported shape: fields, unions, parameter/return types, generic bounds | the compiler flags compiled consumers — name the ones it cannot: serialized data, `any` call sites, downstream repos |
| Events / messages | event name + payload schema | nothing type-checks across a queue — a renamed or repurposed field breaks subscribers silently; in-flight messages still carry the old payload |
| Endpoints | verb + route + request/response shapes + status codes + auth | callers outside the repo; stricter validation is a contract change with no schema diff |
| Persisted schema | table/column set, serialized format | old rows and old messages are consumers of the old contract that keep arriving after deploy |
| Config keys / CLI flags | key or flag name + value type + default + accepted values | consumers live outside the code — deploy manifests, CI pipelines, users' scripts; a changed default is a contract change with no call-site diff |

An un-updated consumer is reported as a fact of the terrain, not a finding
— whether it is a bug belongs to `/code-review:quick-review`. The section
does not repeat the diagram either: `classDiagram`/`erDiagram` show the
structure; this section states the verdict and the off-diff radius. When
an entry names an off-diff consumer, point the reading order's contract
entry at it.

## Report — reading order

Per group, a numbered list. Each entry has three parts:

```
1. `src/billing/schema.ts` — [Contracts] — first: every other change consumes
   the new `Invoice` type. Look at: the widened `status` union — everything
   downstream must handle the new value.
```

- **Why here** — the reason this file sits at this position in the order.
- **Look at** — the one or two things that matter in this file, concrete
  ("signature of `charge()` changed — check its callers follow") rather than
  generic ("review the logic"). Anchor precise spots as `path:line` — this is
  where line numbers belong, clickable and cheap to update, not in the
  diagrams.

Default ordering, to adapt whenever the actual flow disagrees: contracts
first, then core logic following the data flow, then wiring and call sites,
then tests (read them as the promised behavior — do they match the
narrative?), then generated files last, skim only.

**Category labels** like `[Contracts]` above are optional. Invent the 3–6
labels that fit *this* diff — Models, Integrations, Tests, Config, UI,
Migrations, whatever the changes actually contain — instead of forcing a fixed
taxonomy. When every file plays the same role, drop the labels; do not
classify for its own sake.

## What not to do

- No findings. If you notice a bug while mapping, one line at the end
  ("possible issue in X — run `/code-review:quick-review` to confirm") is the
  maximum.
- Do not restate the diff file by file — the reading order says where to look
  and why, not what changed line by line.
- Do not pad: no diagram that repeats the paragraph, no labels on a
  single-role diff, no group headers on a cohesive PR.
