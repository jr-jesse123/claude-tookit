---
name: detour
description: "Step back from a codebase when concepts or APIs block understanding. The user names what is unclear; this session interviews them, anchored on the code, to find where their understanding is clear and where it blurs (concept, technology, this repo's usage, or how pieces interact), then helps them build the map of what must be understood, with several subjects as connected threads when needed: the base concepts (technology-independent), how the specific technology at the version this repo pins models them, how this repo actually uses those APIs, and a short picture of the project (domain, entities, constraints) to build examples from. The map is drafted with the user, then packaged as a self-contained handoff for another agent that already knows the user, which teaches, challenges and bridges as it sees fit. A PR, file or area can be given as context. --return reloads the map and reopens the spots in the code once the user feels ready."
argument-hint: "<what is not clear, in your words> [--pr <number|url|branch>] [paths or areas as context] | --return <slug>"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git diff:*)
  - Bash(git merge-base:*)
  - Bash(git symbolic-ref:*)
  - Bash(gh pr view:*)
  - Bash(gh pr diff:*)
  - Bash(mkdir -p .detour)
  - Write(.detour/**)
---

# Detour

Learning a concept through a project's code is slow. The code shows *one*
use of an idea, wrapped in the project's own names, and never says what the
idea is. The faster route is to step back: understand the concepts and how
the technology models them, then return to the code. This skill builds the
map of what must be understood, together with the user, and packages it for
an agent that already knows the user and how they learn.

The work splits in two:

- **This session plots the route.** It interviews the user to find where
  their understanding is clear and where it blurs. It researches the code
  and the technology, then drafts the map with the user. A badly plotted
  route is expensive: the destination will follow it. So the effort goes
  here, where the code is at hand and the conversation can adjust.
- **The destination teaches.** It knows the user, so it skips what they
  already understand, builds bridges from fields they master, and decides
  whether and how to check understanding or set challenges.

So this skill does not teach, does not guess the user's level, and does not
evaluate the user. The quality of the map is the whole job: complete on what
the subject needs, precise about the technology and the code, and free of
what it does not need. The handoff is written in the language the user is
speaking.

Arguments: whatever the user wrote with the invocation.
- **What is not clear**, in the user's words: a term, an API, a symbol, a
  `path:line`, or a sentence ("I don't get why everything here goes through
  this `Effect` type"). Several items are fine.
- **Context**, optional: `--pr <ref>`, or paths and areas named in the
  arguments. It is where the subject shows up. The subject itself comes
  from the user. Without context, use what this conversation has been
  looking at.
- `--return <slug>`: run **Return** below instead.

## 1. Start from the user's words

Restate what is unclear in two or three lines, and where it shows up
(`path:line`, a PR hunk, a module). When the user says what they want to do
once they understand it (read this module, judge a PR, change a flow), keep
that: it sets the scope. When they do not say, infer it from the
conversation, or leave it open. Do not hold the work up for it.

Then do a quick reconnaissance, enough to ask concrete questions: read the
spots, see which technology and constructs are involved, and see which
other pieces of the code they lean on. The full research comes after the
interview, aimed where the interview points.

## 2. Find the edges: interview the user

The destination knows the user in general. Only this session can find out
where their understanding stops *in this code*, and that is what decides
the route. Interview the user before researching in depth.

**Ask about the code, not about the topic.** "Do you know change tracking?"
gets a yes or no that says little. Anchor each question on a spot and ask
the user to explain it or to predict it: "in `ApproveOrderHandler.cs:41`,
what do you expect `SaveChangesAsync` to write, and why?" A prediction
shows where the edge is faster than any self-rating.

**Place each blur in a layer.** For every item, find out where it sits:

- the **concept** itself (the idea is new or hazy);
- the **technology's modeling** (the idea is clear, but this API's
  defaults or guarantees are not);
- **this repo's usage** (the API is clear, but the wrapper, the config or
  the convention here is not);
- the **interaction** between pieces (each part is clear alone, but the
  combination is not).

Also note what is solidly clear: the route should not spend time there.
When it helps the destination build bridges, note the neighboring
knowledge the user mentions ("I know this from Hibernate", "like
React's reconciliation").

**Adapt, and stop when the edges are found.**

- Ask at most three questions per message.
- Follow up where an answer is vague. Move on where it is solid.
- Stop when every item has a located edge, or when the user says to go
  ahead. There is no fixed number of rounds: one more question costs less
  here than a wrong route.
- When the user's words already place an item ("I get the API, what
  confuses me is why the repo wraps it"), do not ask about it again.

**Locate, do not evaluate.** Do not correct the user or teach during the
interview. A wrong prediction is an edge you found, not a mistake to fix.
Record it in the user's words, and it goes on the map. Correcting it is
the destination's job.

**Record the result** as one line per item: `clear`, `blurry in <layer>`
or `new`, with the user's own words or prediction. The research and the
handoff are built from this record.

## 3. Research the layers

Keep the layers apart. Mixing them is exactly what makes learning inside a
codebase slow.

**a. Base concepts: the technology-independent ideas.** For each: what
problem it solves, the core mechanism, and the vocabulary (the same idea
often has several names across ecosystems; list them). Describe each
concept without the API's names: a definition that only makes sense in the
library's terms belongs in layer b. Order the concepts by dependency, the
first one being what everything else builds on. List deeper prerequisites
in one line each under *assumed known*: the destination knows whether this
user already has them.

**b. How the technology models them, at the version this repo uses.**

- Pin the version from the manifest or lockfile (`package.json` with its
  lockfile, `*.csproj` or `Directory.Packages.props`, `go.mod`,
  `pyproject` with its lock, …). Every claim in this layer is about that
  version.
- Sources by strength: the library's own source (installed packages,
  vendored code, the tagged release), then official docs for that version,
  then changelogs and migration guides, then everything else. Memory is not
  a source; when memory is all there is, mark the claim `inferred`.
- Give the mapping as a table with one row per construct and these
  columns: concept → API construct → what it guarantees → its default →
  where it departs from the general concept. The defaults and the
  departures matter most: they surprise people who know only the concept,
  or only the API.

**c. How this repo uses it.**

- Find the call sites with Grep and group them into patterns. Give each
  pattern a count and one representative `path:line` ("37 queries go
  through `ReadOnlyOrderQueries`, which always adds `AsNoTracking`").
- Name the wrappers, helpers and config the repo puts on top of the API.
  These are often where the user actually got lost.
- Name the places that use the API in an unusual way: against its default,
  against the docs' guidance, or unlike the rest of the repo. State this
  as a fact about the code, not as a finding; whether it is a bug belongs
  to a review.
- Quote, minimally, the spots where the user got stuck and their
  neighbors.

**d. Project context, enough to build examples from.** The destination
teaches faster with examples in the project's own terms than with
`Foo`/`Bar`, and the user carries the idea back more easily. Cover only
what touches the subject:

- what the project does, in one or two lines (domain, kind of system), and
  the stack around the subject (framework, database, runtime);
- the part of the system where the subject lives: what that module or
  flow is for, and the request, job or event that runs through it;
- the domain entities and terms involved (`Order`, `Invoice`,
  "settlement"), with a line each, so examples can reuse them;
- the constraints that make the subject matter here, when the code or docs
  show them: concurrency, volume, latency, consistency ("several operators
  edit the same order at once"). Each carries a `path:line` or a doc as its
  source.

Take this from the README, the docs, the module's code and the PR
description. Do not invent context the sources do not show. Keep it to one
short section: it is a backdrop for examples, not a tour of the project.

**Markers.** Mark every claim in layers b, c and d `seen` or `inferred`,
with its source (`path:line`, a URL with an anchor, a commit), as defined
in `${CLAUDE_PLUGIN_ROOT}/reference/claims.md`. `seen` means the cited
source was opened and says it. The destination cannot reopen the sources;
the markers tell it which statements are solid.

**Several subjects at once.** Understanding often needs several things
together: a persistence API, the transaction behavior wrapped around it,
and the outbox that depends on both. Keep the map flexible without losing
focus:

- Each subject is a **thread**, anchored on a spot the user flagged or the
  interview surfaced. A subject with no spot in the code does not get a
  thread.
- Concepts that several threads need are written once, in the shared
  concepts list, in dependency order. Each thread points to the ones it
  uses.
- When the threads touch each other, add a **how they connect** part:
  which piece calls, wraps or depends on which, and the order in which
  things happen at runtime. When the interview placed a blur in
  *interaction*, this part is where it lands, and it gets its own
  comprehension targets.
- Threads that share no concept and no code path are separate detours.
  Propose splitting them into one handoff each. Separate subjects in one
  brief dilute both.
- Order the threads by dependency, the one the others need first. When
  there are more than three threads, ask the user which ones block them
  now, and leave the rest for a later detour.

The interview record steers the depth: an item marked `clear` gets a line
of context at most, a `blurry in <layer>` item gets depth in that layer,
and a `new` item gets the full treatment.

**Budget.** Research inline for one technology and a few dozen call
sites. When the sweep is wide (several technologies, call sites spread
across many modules), hand the call-site inventory of layer c to an
`Explore` agent. Give it the pinned version, the constructs to find and the
grouping you want. Keep layers a, b and d and all the writing here.

## 4. What must be understood

From the layers, write the **comprehension targets**: the points the user
needs to grasp to read this code with confidence, usually three to six.
Each target:

- is tied to a real spot (`path:line`), quoted in the handoff so the
  destination can see it;
- joins the concept and the technology's modeling, where the code depends
  on both. For example: "why an entity loaded with `AsNoTracking` and then
  passed to `SaveChanges` writes nothing (`ApproveOrderHandler.cs:41`)".
  Trivia about the API alone does not qualify;
- names the trap, when there is one: the default or the departure that
  makes the code behave differently from what the concept alone suggests;
- when the interview caught a wrong prediction, starts from it: that
  prediction is exactly what the destination has to move.

This list is the core of the map. The destination uses it however it sees
fit: as a syllabus, as the source of challenges, or as its own test of
when the user is ready.

## 5. Draft the map with the user

Before writing the handoff, show the map as a compact outline:

- the interview record, one line per item, so the user can correct how
  they were placed;
- the threads, if more than one, with how they connect;
- the concepts, in order, with the *assumed known* line;
- the technology and its version, with the constructs that will go in the
  table;
- the repo patterns and the unusual uses;
- the project context, in a few lines;
- the comprehension targets.

Ask in one message what to add, cut or go deeper on. The user knows what
they are missing. You know what the code needs. The map takes from both.
Revise it and research what they add, then show it again only when it
changed in substance. When they say it is right, write the handoff.

## 6. Package the handoff

Write one self-contained markdown file to `.detour/<slug>.md` in the
working directory (`mkdir -p .detour` first). The slug comes from the
subject and is short (`ef-change-tracking`). If `.detour/` is not in
`.gitignore`, say so in the closing line, and do not edit `.gitignore`.

Structure, in the user's language. See
`${CLAUDE_SKILL_DIR}/examples/handoff.md` for a full single-thread one and
`${CLAUDE_SKILL_DIR}/examples/multi-thread.md` for how several threads fit
together. Size the real one to the real subject.

1. **For the destination agent**: a short preamble with these points.
   - Who is learning and why. The person is working in `<project, one
     line>`, around `<area or PR>`. They got stuck on `<what, in their
     words>`. They want to come back able to `<goal, if they gave one>`.
   - The division of labor. You know this person. Skip what they already
     understand, bridge from fields they master, and check understanding
     or set challenges as you judge best. This brief maps *what* must be
     understood; it does not say *how* to teach it.
   - Scope. In scope: the base concepts, the technology's modeling at
     `<version>`, and the repo excerpts below. Out of scope: the rest of
     the project, and any judgment of the code, which happens back in the
     repo.
   - Examples. Draw them from *Project context* when that helps, so the
     idea lands in terms the person will meet again in the code.
   - The marker convention (`seen`, `inferred`).
   - The person goes back when they feel confident. Nothing needs to be
     reported back.
2. **Project context** (layer d).
3. **Where it showed up**: the spots, quoted.
4. **Where the person stands**: the interview record, item by item, in
   their own words: what is clear, what is blurry and in which layer, the
   predictions they made, and the neighboring knowledge they mentioned.
   Mark it as their own account, not an assessment.
5. **Base concepts**, in dependency order, plus *assumed known*. With
   several threads, this is the shared list.
6. **How `<technology>@<version>` models them**: the mapping table,
   defaults, guarantees and departures, with markers and sources. With
   several threads, give one block per thread here and in the next item.
7. **How this repo uses it**: patterns with counts, wrappers and config,
   unusual uses, and minimal excerpts.
8. **How they connect**, only with several threads that touch each other.
9. **What must be understood**: the comprehension targets.
10. **Sources**, with versions.

**What leaves the repo.** The handoff goes to another agent, possibly in
another product or account. Quote the minimum code that makes each point.
Never quote secrets, tokens, internal hostnames or URLs, customer data or
personal data: redact them or describe the shape instead. The project
context uses domain terms and architecture freely, since that is what makes
the examples work. It names the company, client or product only when the
user asks for it ("an order-management API for a retailer" is enough).

**Deliver.** Print the handoff in chat in a single fenced `markdown` block,
ready to copy. Close with one or two lines: the file path, the files it
quotes (so the user can decide before pasting it elsewhere), and
`/knowledge:detour --return <slug>` for when they are back.

## Return

`--return <slug>` means the user is back and feels ready. Do not quiz them
or check their understanding: that was the destination's job, and they
came back when they were confident.

1. Load `.detour/<slug>.md`. If it is not in the working directory and not
   in this conversation, ask for it once.
2. Reopen the code where they got stuck. Show the spots from *Where it
   showed up* and *What must be understood*, re-read at the current HEAD
   (say so if a spot moved or changed), so they can pick up from there.
3. When the user states something about the code that comes from what
   they learned and asks about it, answer it against the code, with
   `path:line`. Answer only what they ask.
4. Close in one line. Offer `/knowledge:harvest <subject>` to keep what
   they learned as a note, and, if a PR or tour was in progress, offer to
   pick it up where it stopped.

## What not to do

- Do not teach in this session: no tutorial, no analogies chosen for the
  user, no assumed level. Those belong to the destination.
- Do not evaluate the user, in the interview or after it, and do not
  write answers to the comprehension targets into the handoff. The
  interview locates edges; the destination decides how to check.
- Do not skip the interview because the topic seems obvious. The route
  depends on where *this* user's edges are in *this* code.
- Do not widen the map to "everything about `<technology>`". What the user
  is missing and what the code needs set its edges.
- Do not report findings. An unusual use of an API is a fact on the map;
  judging it belongs to a review.
- Do not leave claims about the technology unversioned, or claims about
  the repo without a `path:line`.
