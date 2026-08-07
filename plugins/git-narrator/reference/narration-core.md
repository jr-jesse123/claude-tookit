# Narration core — shared by /narrate and /narrate-wip

Definitions both narration modes share. Each skill layers its own deltas on
top; when a skill's text and this file disagree, the skill wins — it knows
its mode.

## Discovering build and test commands

Read what the project defines — `package.json` scripts, `Makefile`,
`pyproject.toml`, `*.csproj` / `*.sln`, `justfile`, or `.github/workflows/` —
and extract:

- the **build command** (compile/typecheck; the cheapest full-tree check),
- the **test command**, and how to scope it to a path or filter if the runner
  supports it (`dotnet test --filter`, `npm test -- <path>`, `pytest <path>`).

Never invent commands. If no build step exists, pick the closest cheap gate
(linter, `py_compile`) and say so in the plan.

## Slicing

**Axis first:** one purpose → slice by layer. Several purposes → slice
vertically by purpose first, then apply the layer order inside each purpose.

**Layer order within a purpose** (each slice must leave the tree compilable —
tests travel *with* the code they test, never ahead of it):

1. Intent docs — PRD, ADRs, reference files, scripts that document intent
2. Domain / central definitions **+ their tests**
3. Support / infrastructure **+ their tests**
4. Wiring, composition **+ E2E tests**

Granularity is **file-level**. If one file genuinely spans two slices, assign
it whole to the later slice.

While classifying, watch for the classic trap: test fixtures and builders
used by domain tests but living in a "support" directory. If domain tests
import them, they belong in the domain slice — the build gate will catch
this, but catching it at planning is one less re-slice cycle.

## Trailers

Commit messages follow the repo's existing style and carry machine-readable
trailers for future archaeology. The shared one:

```
Stage: docs | domain | support | e2e
```

One `Stage:` line per commit is the norm; a commit produced by merging two
slices (see the amendment ceiling below) keeps both `Stage:` lines —
repetition is the signal that it spans layers.

Each mode adds its own trailers on top (`Refs:` / `Narrated-From:` for
`narrate`, `Wip-Build:` for `narrate-wip`) — defined in the respective skill.

## The disposable-worktree gate

Gate runs never use the user's working tree: while commits are being built,
it holds later slices' files unstaged, so building it would test the wrong
tree. Per commit to gate:

```
git worktree add /tmp/<gate-dir> <commit-sha>   # detached; legal even while
(cd /tmp/<gate-dir> && <build_cmd> [tests])     # the branch is checked out
git worktree remove --force /tmp/<gate-dir>     # elsewhere
```

Docs-only commits pass the build gate trivially; run the build anyway if it
is cheap, skip with a note if not.

## Gate failure = slicing error

The full tree compiled before slicing began, so a red gate at commit N is
**information about the slicing, not about the code**: commit N is missing a
file that a later slice holds. Diagnose, don't guess — read the error, find
the missing symbol or import, locate which slice owns that file, move it one
slice earlier, and redo the commits from the start of the mode's
reconstruction step. Never edit content to make a gate pass.

**Three amendment rounds maximum.** Not converging means two slices are
genuinely interdependent: merge the failing commit with its predecessor
(concatenate messages, keep both `Stage:` trailers) and re-gate. A slightly
coarser history that is green beats a purer one that is red.

---

Maintenance note: `skills/narrate/execution-protocol.md` deliberately
restates the gate rules — the executor agent reads only the protocol and
must stay self-sufficient. A change to gate semantics here needs a matching
change there.
