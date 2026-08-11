---
name: init
description: Survey the repository and scaffold a right-sized docs/architecture layout — proposing the minimal artifact set that passes the economic test, including recommending no scaffold at all for small projects. Use when the user wants to start documenting a system's architecture.
argument-hint: [optional target directory, defaults to docs/architecture]
allowed-tools: Bash(git log:*), Bash(git shortlog:*), Bash(git ls-files:*), Bash(npx --yes @zabaca/mermaid-validate:*), Read, Grep, Glob, Write
---

# Architecture docs init

Scaffold the *smallest* architecture documentation set this repository can
justify — not the largest it could absorb. Read
`${CLAUDE_PLUGIN_ROOT}/reference/right-sizing.md` first; every step below
answers to it. Write prose to the user in their language; the scaffolded
files stay in the repository's dominant language.

## 1. Survey the repository (read-only)

Gather evidence before proposing anything:

- **Size and shape.** `git ls-files` for file count and languages; top-level
  layout; mono-repo vs single app.
- **Deployable units.** Dockerfiles, compose files, k8s manifests, serverless
  configs, Procfiles — how many things actually run.
- **External integrations.** Grep dependency manifests and config for HTTP
  clients, queue/broker drivers, database drivers, third-party SDKs, webhook
  handlers.
- **People.** `git shortlog -sn --since="1 year ago"` — one maintainer and
  twenty are different tiers.
- **What already exists.** Existing ADRs anywhere (`adr/`, `docs/adr/`,
  `doc/architecture/decisions/`), existing architecture notes in READMEs or
  wikis referenced from the repo. Never overwrite or duplicate an existing
  convention — adopt it.

## 2. Classify the tier and propose

Map the evidence onto the artifact ladder and present a proposal table
**before writing anything**:

| Artifact | Scaffold? | Justification (one sentence, naming the trigger) |

Rules for the proposal:

- **Tier 0 is a real recommendation.** Small single-purpose repo, one or two
  maintainers, no external consumers → recommend an Architecture Haiku
  section in the top-level README plus an empty `adr/` folder, and say
  plainly that a `docs/architecture/` tree would fail the economic test.
  Stop there unless the user overrides.
- Every Tier 2 artifact needs its trigger written in the table. No trigger
  in one sentence → not proposed.
- List what you are deliberately **not** scaffolding and why — the omissions
  are part of the proposal.

Wait for the user's approval or adjustments. This is the one mandatory
pause in the skill.

## 3. Scaffold

Templates live in `${CLAUDE_PLUGIN_ROOT}/reference/templates/` (`readme.md`
→ `README.md`, `overview.md`, `adr.md` → `adr/0000-template.md`,
`system-context.md` and `containers.md` → `diagrams/`). Target directory:
`$ARGUMENTS` if given, else `docs/architecture/`.

Pre-fill only what the survey evidenced:

- Real service, database, broker, and external-system names in the diagrams
  and overview — a committed generic placeholder is a defect.
- Styles and patterns actually observed in the code.
- Constraints that are visible in the repo (pinned platforms, license
  obligations, required runtimes).

Everything that requires human knowledge — the why, negotiations, budget,
regulatory pressure, history — stays as `TODO(human): <specific question>`.
Never fill a "why" field with plausible prose; an invented intent is worse
than an empty field.

Label every diagram arrow with the interaction kind (`sync:` / `event:` /
`data:` / `dep:` / `deploy:`) based on what the code shows. Validate every
mermaid fence: `npx --yes @zabaca/mermaid-validate -` with the fence body on
stdin (the trailing `-` is the stdin marker — same invocation as this repo's
`scripts/validate-diagrams.mjs`). A diagram that does not validate does not
get committed.

## 4. Report

Close with three things, in this order:

1. **What was created** — the file list, one line each.
2. **The `TODO(human)` inventory** — every open question, grouped by file,
   phrased so the user can answer them in one pass.
3. **ADR candidates** — significant decisions already embedded in the code
   whose rationale is recorded nowhere (a broker with no stated reason, a
   nonstandard datastore, a hand-rolled auth layer). For each: what the code
   shows, and the question an ADR would answer. Offer `/arch-docs:adr` per
   candidate — do not draft them unasked.

Do not commit; leave the working tree for the user to review.
