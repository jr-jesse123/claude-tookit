---
name: detour
description: "Step back from a PR or codebase when a concept or API blocks understanding: maps the base concepts (technology-independent), how the specific technology at the version this repo pins models them, and how this repo actually uses those APIs, plus a short picture of the project (domain, entities, constraints) to build examples from, then packages a self-contained handoff for another agent that already knows the user and how they learn, so it teaches the concepts and the user returns ready to decide. The handoff carries exit questions tied to the decisions waiting in the code (path:line) and a return-note template. --return re-anchors what was learned on the code, checks the user's new assumptions against it, and reopens the decision points."
argument-hint: "<what is not clear: a term, an API, a symbol or path:line> [--pr <number|url|branch>] | --return [<return note, or the handoff slug>]"
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

Learning a concept through a project's code is slow: the code shows *one*
use of an idea, wrapped in the project's own names, and never says what the
idea is. This skill takes the faster route. It steps back from the code,
maps what the user needs to learn, and hands that over to an agent that
already knows the user and how they learn, so the user can study there and
come back to the code ready to decide.

The work splits in two. **This skill maps; it does not teach.** It does not
write a tutorial, guess the user's level, or pick a teaching style: the
destination agent knows the user, and this brief tells it *what* to cover
and *when the user is done*, never *how* to teach. The handoff is written in
the language the user is speaking.

Arguments: whatever the user wrote with the invocation.
- **What is not clear** — a term ("backpressure"), an API (`AsNoTracking`,
  `useSyncExternalStore`), a symbol, or a `path:line` where the user got
  stuck. Several items are fine when they belong to the same subject.
- `--pr <ref>` — the PR or branch being read. Without it, use the PR or tour
  this conversation is about, if any; else the current branch against the
  default branch, when it has commits of its own.
- `--return [<note or slug>]` — run **Return** below instead.

## 1. Pin the blocker

Before researching, state in two or three lines, and show the user:

- **What** is unclear, in the user's words, and **where** it shows up
  (`path:line`, the PR hunk, the tour item).
- **What it blocks**: the decision the user cannot make yet ("approve the
  switch to `AsNoTracking` in the order loader", "judge whether the retry
  policy is safe"). This is what the detour is for; every later step serves
  it.

When the conversation does not show the decision, ask one question for it
and wait. Do not guess: a detour without a decision becomes a course on the
whole topic.

## 2. Map three layers, plus the project around them

Keep the layers apart. Mixing them is exactly what makes learning in the
codebase slow.

**a. Base concepts — the technology-independent idea.** What problem it
solves, the core mechanism, and the vocabulary (the same idea often has
several names across ecosystems; list them). Describe each concept without
the API's names: if a definition only makes sense in the library's terms, it
belongs in layer b. Order the concepts by dependency, from the one that must
come first. Stop at what the decision needs, usually one to four concepts.
For deeper prerequisites, list them in one line each under *assumed known*:
the destination knows whether this user already has them.

**b. How the technology models them — at the version this repo uses.**

- Pin the version from the manifest or lockfile (`package.json` +
  lockfile, `*.csproj`/`Directory.Packages.props`, `go.mod`, `pyproject` +
  lock, …). Every claim in this layer is about that version.
- Sources by strength: the library's own source (installed packages,
  vendored code, the tagged release) → official docs for that version →
  changelogs and migration guides → everything else. Do not use memory as a
  source; when memory is all there is, mark the claim `inferred`.
- Give the mapping as a table, one row per construct:
  concept → API construct → what it guarantees → its default → where it
  departs from the general concept. The departures and the defaults are the
  most valuable part: they are what surprises people who know only the
  concept or only the API.

**c. How this repo uses it.**

- Find the call sites with Grep and group them into patterns, with a count
  and one representative `path:line` each ("37 queries go through
  `ReadOnlyRepository`, which always adds `AsNoTracking`").
- Name the wrappers, helpers and config the repo puts on top of the API.
  They are often where the user actually got lost.
- Name the places that use the API in an unusual way: against its default,
  against the docs' guidance, or unlike the rest of the repo. This is a fact
  about the code, not a finding. Whether it is a bug is for
  `/code-review:quick-review`.
- Include the spots the decision depends on (the PR hunk and its
  neighbors), quoted minimally.

**d. Project context: enough to build examples from.** The destination
teaches faster with examples in the project's own terms than with
`Foo`/`Bar`, and the user transfers the idea back more easily. Gather a
short picture of the project, limited to what touches the subject:

- what the project does, in one or two lines (domain, kind of system), and
  the stack around the subject (framework, database, runtime);
- the part of the system where the subject lives: what that module or flow
  is for, and the request, job or event that runs through it;
- the domain entities and terms involved (`Order`, `Invoice`,
  "settlement"), with a line each, so examples can reuse them;
- the constraints that make the subject matter here, when the code or docs
  show them: concurrency, volume, latency, a consistency need ("orders are
  edited by several operators at once"). Each one carries a `path:line` or
  a doc as its source.

Take it from the README, docs, the module's code and the PR description.
Do not invent context the sources do not show. Keep it to one short
section: it is a backdrop for examples, not a tour of the project.

Mark every claim in layers b, c and d `seen` (the cited source was opened and
says it) or `inferred`, with its source (`path:line`, a URL with an anchor,
a commit), as in `${CLAUDE_PLUGIN_ROOT}/reference/claims.md`. The
destination cannot reopen the sources, so the markers are how it knows which
statements are solid.

**Budget.** Map inline for one technology and a few dozen call sites. When
the sweep is wide (several technologies, call sites across many modules),
hand the call-site inventory of layer c to an `Explore` agent with the
pinned version, the constructs to find and the grouping wanted. Keep layers
a and b and the writing here.

## 3. Exit questions — the way back

Write two to five questions that the user should be able to answer, in
their own words, once the concepts are clear. Each question:

- is tied to the decision and to a real spot (`path:line`), quoted in the
  handoff so the destination can see it;
- needs both the concept *and* the technology's modeling to answer ("in
  `OrderLoader.cs:88` the entity comes from a no-tracking query and is
  passed to `SaveChanges` — what gets written, and why?"), never only
  trivia about the API;
- has an answer you know and can back with sources. Keep the answers out
  of the handoff; they are for **Return**, which works them out again from
  the cited spots when it runs in a new session.

These questions are the destination's definition of done: the user is
ready to go back when they can answer them.

## 4. Package the handoff

Write one self-contained markdown file to `.detour/<slug>.md` in the
working directory (`mkdir -p .detour` first). The slug comes from the
subject and is short (`ef-change-tracking`). If `.detour/` is not in
`.gitignore`, say so in the closing line, and do not edit `.gitignore`.

Structure, in the user's language (see `${CLAUDE_SKILL_DIR}/examples/handoff.md`
for a full one, and size the real one to the real subject):

1. **For the destination agent**, a short preamble. It says who is
   learning and why: they are reading `<PR or area>` in `<project, one
   line>`, they are blocked on `<what>`, and the goal is to go back
   able to decide `<decision>`. It says that the destination knows this
   person and how they learn, and that this brief covers *what* to teach,
   not *how*. It fixes the scope: in scope are the base concepts, the
   technology's modeling at `<version>`, and the repo excerpts below; out
   of scope are the rest of the project and judging the PR, which happens
   back in the repo. Done means the user answers the exit questions in
   their own words; then the destination helps them fill in the return
   note. It also asks the destination to draw its examples from the
   project context section when that helps, so the idea lands in terms
   the user will meet again in the code.
2. **Project context** (layer d): the domain, the area of the system,
   the entities and terms, the constraints.
3. **Where it showed up**: the blocking spot, quoted, and the decision.
4. **Base concepts**, in dependency order, plus *assumed known*.
5. **How `<technology>@<version>` models them**: the mapping table,
   defaults, guarantees and departures, with markers and sources.
6. **How this repo uses it**: patterns with counts, wrappers and config,
   unusual uses, and minimal excerpts.
7. **Exit questions**, without answers.
8. **Sources**, with versions.
9. **Return note**, a template for the user to fill in with the
   destination and paste back here with `--return`:

   ```
   # Return: <subject> (<slug>)
   - In my words: <the idea, 3–5 lines>
   - Exit answers: Q1 → … / Q2 → …
   - What I now assume about this code: <statements to check>
   - Still fuzzy: <what is left>
   ```

**What leaves the repo.** The handoff goes to another agent, possibly
another product or account. Quote the minimum code that makes each point,
and never quote secrets, tokens, internal hostnames or URLs, customer data,
or personal data: redact them or describe the shape instead. The project
context uses domain terms and architecture freely, since that is what makes
the examples work, but it names the company, client or product only when
the user asks for it ("an order-management API for a retailer" is enough).

**Deliver.** Print the handoff in chat in a single fenced `markdown` block,
ready to copy, and close with one or two lines: the file path, the files it
quotes (so the user can decide before pasting it elsewhere), and how to come
back: `/knowledge:detour --return` with the filled-in note.

## Return

`--return` with the filled-in return note pasted (or with a slug, when the
note arrives in the next message). Load `.detour/<slug>.md` for the exit
questions and the spots. If the handoff is not in the working directory and
not in this conversation, ask for it once.

1. **Check the exit answers** against the answers you can source. Confirm
   the right ones briefly. Correct the wrong ones with the concept and a
   `path:line`. Do not grade; the point is that the user decides on solid
   ground.
2. **Check every "what I now assume about this code" line** against the
   code: `holds` (with `path:line`), `does not hold here` (what the code
   does instead, with `path:line`), or `cannot tell from the code` (what
   would settle it). New understanding often overgeneralizes to code that
   departs from the default, which is why this check exists.
3. **Reopen the decision.** Restate the decision from step 1 with the spots
   it depends on, now readable with the new concepts. Lay out what each
   option implies in this code. Do not make the decision unless the user
   asks for a recommendation.
4. **"Still fuzzy"** items: answer them briefly here when they are about
   this code. When they are about the concept, offer a short follow-up
   handoff for the destination (step 4 again, with only those items) rather
   than teaching here.
5. Close in one line: offer `/knowledge:harvest <subject>` to turn what was
   learned into a durable note, and, when a tour was in progress, offer to
   pick it up where it stopped.

## What not to do

- Do not teach in this session: no tutorial, no analogies chosen for the
  user, no assumed level. Those belong to the destination.
- Do not widen the scope to "everything about `<technology>`". The decision
  sets the scope.
- Do not report findings. An unusual use of an API is a fact on the map;
  judging it belongs to the review.
- Do not leave claims about the technology unversioned, and do not leave
  claims about the repo without `path:line`.
