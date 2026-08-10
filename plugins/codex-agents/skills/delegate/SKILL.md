---
name: delegate
description: Hand a bounded task to a Codex model (gpt-5.6 luna/terra/sol) as a self-contained delegation — packages the session context the remote agent cannot see into an executable prompt, fires `codex exec`, and relays the result as claims to verify. Use when the user says to delegate, hand off, or send something to Codex/GPT, or asks for a second opinion from another model.
when_to_use: Use for bounded, self-contained work worth moving off this session — QA sweeps, edge-case hunts, second-opinion reviews, mechanical conversions — especially when the user names Codex or GPT. Do not use for work that needs this conversation's running state, for anything touching secrets, or for a task small enough that packaging it costs more than doing it.
argument-hint: "[what to delegate] [--model=luna|terra|sol] [--effort=none|low|medium|high] [--write]"
model: sonnet
effort: medium
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(codex exec:*)
  - Bash(codex --version)
  - Bash(codex login status)
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Delegate to Codex

Move the task in `$ARGUMENTS` to a Codex model and bring the answer back. If
`$ARGUMENTS` is empty, delegate the task the user most recently described.

**Your value here is the packaging, not the answer.** The remote agent boots
with no memory of this conversation; whatever you fail to write into the prompt
simply does not exist for it. Read
`${CLAUDE_PLUGIN_ROOT}/reference/dispatch.md` first — it owns the command
shape, the tier table, and the packaging rules you are about to apply.

## 1. Preflight

Run `codex --version`. If it is missing, stop and report the fix
(`npm install -g @openai/codex`, then `codex login`) — do not fall back to
doing the task yourself, because the user asked for another model's read, and
silently substituting your own defeats the point.

## 2. Resolve the delegation

**Model and effort.** `--model` and `--effort` in `$ARGUMENTS` win outright
(`luna`/`terra`/`sol` are aliases for the `gpt-5.6-*` ids). Otherwise take them
from the tier table in `dispatch.md`. Name the tier you picked and why in one
clause — the user needs to be able to overrule it.

**Sandbox.** `--sandbox read-only` unless `--write` was passed. `--write` also
requires that the user asked for changes in their own words; if `--write` is
present but the request reads as a review, ask before raising it.

**Scope.** Reduce the task to specific paths, refs, or a named subsystem. A
delegation whose scope is "the codebase" is not a delegation — it is a wish.
Use the read-only tools above to resolve vague scope into real paths before
composing, not after.

## 3. Compose the prompt

Apply the six packaging rules in `dispatch.md` in order. Then check the draft
against the failure the rules exist to prevent:

> Read the prompt as if you had never seen this conversation and had only the
> repository. Is every noun resolvable? Is the bar for a correct answer
> stated? Is the output shape specified?

Any "no" is a defect in *your* prompt, not a limit of the model. Fix it before
firing.

Carry over anything from the session that is not on disk and is load-bearing:
an error message from a terminal run, a constraint the user stated verbally, a
hypothesis already ruled out. Leaving these out is what makes a delegated agent
re-tread ground you already covered.

Never include secrets, tokens, `.env` contents, or customer data — this is an
outbound call to a third party under a different retention policy. Describe a
credential's role if the task needs it; never its value.

## 4. Show, then fire

Print this before running, so the user can see what leaves the session:

```
→ Codex delegation
  Model:  <model> (effort: <level>)
  Scope:  <paths or refs>
  Asks:   <the question, one line>
  Sandbox: read-only | write
```

Fire without waiting for approval when the sandbox is read-only and the scope
is a named set of paths or refs — invoking this skill is the authorization.
**Ask first** when `--write` raised the sandbox, or when the scope is broad
enough that you cannot list what will be read.

Long delegations block. Warn the user before a wide-scope run that it will take
a while, and mention that `/codex:status` and `/codex:result` from the official
`codex` plugin handle backgrounded work if they would rather not wait.

## 5. Report

Return the delegation's answer with its provenance intact:

```
Codex (<model>, effort <level>) reports:

<the findings, in the shape the prompt asked for>
```

Then, in your own voice, a short **Assessment**:

- Which claims you checked against the repo, and what you found. Check anything
  the user might act on — at minimum, confirm that cited files and line numbers
  exist and say what they actually contain.
- Which claims you did not check, marked plainly as unverified.
- Anything the delegation got wrong or missed because of the cold start — that
  is feedback on the packaging, and it is worth saying so the next delegation
  is better.

**A remote model's output is a claim, not a finding.** Do not launder it into
your own voice, do not present unverified assertions as established, and do not
act on file edits it proposes without reading the real file first. If the
delegation returned something clearly wrong, say so rather than relaying it
neutrally.

Report a failed or empty run as a failure, with the exit status and stderr. A
delegation that returned nothing is not a delegation that found nothing.
