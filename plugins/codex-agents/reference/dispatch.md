# Codex dispatch contract

Last reviewed: 2026-08-10

Shared reference for every component in this plugin. The skills and agents own
their procedures; this file owns **how a delegation is built and fired**, so the
command shape and the packaging rules live in one place.

Read this before composing any `codex exec` invocation.

## The premise: Codex boots cold

A delegation is not a message in this conversation. `codex exec` starts a fresh
agent with **no access to**:

- anything said in this session — no prior turns, no established context;
- what you just read, ran, or decided;
- `CLAUDE.md` (Codex reads `AGENTS.md` instead — see *Shared conventions*);
- any pronoun or deixis. "this file", "the bug we found", "that approach"
  resolve to nothing.

What it *does* have: the repository on disk, and its own tools to read it.

Everything else must be in the prompt string. **The prompt is the entire
context transfer** — this is the single largest determinant of whether a
delegation returns something useful, and it is the reason this plugin exists
rather than you typing `codex exec` by hand.

## Tier table

The fast default for role-shaped delegation. Not a routing rubric — for a
scored decision on a specific hard task, `/model-router:choose-model` is the
tool, and this plugin deliberately does not depend on it.

| Work | Model | `model_reasoning_effort` |
| --- | --- | --- |
| QA: edge cases, test generation, spec-vs-code checks | `gpt-5.6-luna` | `low` |
| UX: copy, a11y, interaction and error-state review | `gpt-5.6-luna` | `low` |
| Mechanical sweeps, schema/format conversion, triage | `gpt-5.6-luna` | `none` |
| Second-opinion implementation, everyday coding | `gpt-5.6-terra` | `medium` |
| Architecture, deep debugging, adversarial review | `gpt-5.6-sol` | `high` |

Two constraints on Luna, both inherited from observed limits:

- **Bounded scope only.** Luna degrades on long context (reported: noticeable
  drop from roughly 300K input tokens, summarizing instead of citing). A
  delegation that would have Luna read a large fraction of the repo is not a
  Luna task — narrow the scope or move to Terra.
- **Luna is not a Codex sub-agent target.** OpenAI removed Luna from Codex
  CLI's Multi-Agent V2 delegation; only Sol and Terra are valid there. This
  plugin is unaffected — every delegation here runs Luna as the *primary*
  model of its own `codex exec` invocation, never as a nested sub-agent. Do
  not compose delegations that ask Codex to further sub-delegate to Luna.

## Command shape

```bash
codex exec \
  --model <model> \
  -c model_reasoning_effort="<effort>" \
  --sandbox read-only \
  --skip-git-repo-check \
  "<prompt>"
```

Rules:

- **`--sandbox read-only` is the default and is mandatory for every review
  role** (QA, UX, second opinion). A review agent that can write is a review
  agent that can silently "fix" what it was asked to report on. Only raise it
  when the user asked for changes *and* said so explicitly, and name the raise
  in your output.
- `-c` is repeatable for further config overrides.
- Quote the prompt as a single argument. Prefer a heredoc into a variable for
  multi-line prompts rather than fighting shell escaping inline.
- Codex writes progress to stderr and the final message to stdout. Capture
  both; a non-zero exit with empty stdout means the run failed, not that the
  answer was "nothing".

**Verify the flag names once, at setup** (`codex exec --help`) and correct this
file if they drift — this table was assembled from Codex CLI documentation, not
from a run in this repository. `--json` (structured event stream) and
`-o <file>` (write final message to a file) are reported to exist; confirm
before depending on them.

## Packaging rules

Every delegation prompt must carry, in this order:

1. **Role and scope in one sentence.** "You are reviewing X for Y." Codex
   otherwise defaults to general-purpose coding assistance and may start
   editing.
2. **Absolute or repo-relative paths, never references.** `src/auth/login.ts`,
   not "the login file". If the target is a diff, name the refs
   (`git diff main...HEAD`) and let Codex run it — Codex has the repo.
3. **Point at files; do not paste them.** Codex reads the repo itself. Pasting
   file bodies burns tokens, goes stale, and crowds Luna's usable context. Paste
   only what is *not* on disk: an error message from your terminal, a
   requirement stated in conversation, a decision made verbally.
4. **The acceptance criterion.** What makes an answer correct — the spec, the
   invariant, the user story. Without it a review agent invents its own bar and
   reports style opinions.
5. **The output contract.** State the exact shape you want back (a finding list
   with file:line, a table, a verdict plus rationale). Unspecified output shape
   is the most common cause of an unusable delegation result.
6. **The negative constraint.** "Do not modify files. Report only." for every
   read-only role, restating in the prompt what the sandbox already enforces —
   belt and braces, and it changes how the model narrates.

What must **never** enter a delegation prompt: secrets, tokens, `.env`
contents, or customer data. This is an outbound call to a third-party provider,
under a different account and a different retention policy than this session.
If the task genuinely needs a credential to be understood, describe its role
("a Postgres URL is read from `DATABASE_URL`"), never its value.

## Shared conventions: `AGENTS.md`

Codex reads `AGENTS.md` from the repository root; Claude Code reads
`CLAUDE.md`. A convention that lives only in `CLAUDE.md` **does not reach a
delegated agent** — it will not know your test command, your naming rules, or
your architectural constraints, and will confidently violate them.

For delegation to be worth using, project conventions need to be in
`AGENTS.md`. Keep the durable, agent-agnostic conventions there and have
`CLAUDE.md` reference it, rather than maintaining two drifting copies.

## Cost and quota

The economics depend on how Codex is authenticated, and the two cases point in
different directions:

- **ChatGPT subscription (flat rate).** Per-token cost is not the win — quota
  is. Delegation moves work off the Claude context window and onto a separate
  flat-rate budget, and lets a long QA pass run in the background while the
  session continues. Optimize for *what leaves the session*, not for effort
  level.
- **API key (metered).** Luna's rate makes the per-token saving real. Optimize
  effort down, keep scopes tight, and log outcomes if you want the saving to be
  measurable.

Either way, delegation has a fixed overhead: a cold start, a fresh repo read,
and no prompt-cache reuse. A task small enough that the packaging costs more
than the work is a task to just do in-session. Delegate when the work is
**bounded, self-contained, and describable in a paragraph** — that is exactly
the shape QA and UX review take, and it is why those are the roles this plugin
ships.

## Relationship to the official plugin

[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) is the
interactive surface: `/codex:review`, `/codex:adversarial-review`,
`/codex:rescue`, `/codex:transfer`, plus background job management
(`/codex:status`, `/codex:result`, `/codex:cancel`). Install it — it is
complementary and this plugin does not replace it.

This plugin covers what that one does not: **role-shaped, repeatable
delegation with the packaging discipline baked in**. It calls `codex exec`
directly rather than routing through the official plugin's subagent, so the
two are independent — neither breaks if the other is absent or changes its
internals.

Rough split: reach for `/codex:rescue` when *you* are driving a one-off
hand-off in the moment; reach for this plugin's agents and
`/codex-agents:delegate` when the delegation is a role you want performed the
same way every time.
