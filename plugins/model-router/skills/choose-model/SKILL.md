---
name: choose-model
description: Recommend the cheapest Claude model, effort level, and execution shape likely to complete a proposed task reliably. Use before coding, debugging, architecture, research, migrations, or long agentic work when the model choice is uncertain.
when_to_use: Use when the user asks which model or effort to use, when a task may cross files or architectural layers, or before delegating expensive or long-running work. Never execute the task itself.
argument-hint: "[task description]"
disable-model-invocation: true
model: sonnet
effort: medium
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git status *)
  - Bash(git diff --stat *)
  - Bash(git diff --name-only *)
  - Bash(git log --oneline *)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# Model advisor

Recommend how to run the task in `$ARGUMENTS`. If `$ARGUMENTS` is empty, evaluate
the most recent task the user described.

**You are not doing the task.** Do not implement, edit, or execute it, and do not
run the command you end up suggesting. Inspect the repository only when the
description leaves a scoring dimension genuinely undecidable, and only with the
read-only tools above.

## 1. Load the policy

Read `${CLAUDE_SKILL_DIR}/model-policy.md` before deciding anything. It owns the
model roles, the effort ladder, the per-category routing lists, the hard
overrides, and the calibration format. This file owns only the procedure.

If a task category is already listed explicitly in the policy, that listing wins
— score it anyway, but say so when the score disagrees.

## 2. Check the hard overrides first

If the task matches any entry under **Hard overrides** in the policy, skip the
scoring: the floor is Opus `high`. Note which override fired and continue to
step 4 to pick effort and execution shape.

## 3. Score five dimensions, 0–3 each

Score only these. Each is one line of justification in the output.

| # | Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- | --- |
| 1 | **Reasoning novelty** | Familiar transformation | Known engineering pattern | Complex interaction of known concepts | Novel problem needing new hypotheses |
| 2 | **Execution horizon** | One or two operations | Normal implementation and tests | Many tool calls, iterative debugging | Longer than a single sitting |
| 3 | **Oracle weakness** | Compiler or deterministic test proves it | Good automated tests exist | Tests incomplete or expensive | Correctness hard to observe at all |
| 4 | **Blast radius** | Local and easily reversible | Normal application defect | Cross-layer, or production/data risk | Failure could silently corrupt behavior or data |
| 5 | **Context scale** | Small and self-contained | Normal repository exploration | Large codebase or long history | Very large or multi-repository |

### Decision rule

Apply in order; the first match wins.

1. Any dimension scored **3** → Opus, floor `high`.
2. Total **≥ 9** → Opus.
3. Total **5–8** → Sonnet.
4. Total **≤ 4** → Haiku, but only if no dimension exceeds 1 and the input fits
   Haiku's 200K context. Otherwise Sonnet `medium`.
5. Opus already indicated and the task exceeds a single sitting, or a serious
   Opus attempt already failed → consider Fable, per the policy.

### Effort

Take the level from dimension 2 (execution horizon), then apply the policy's
ladder:

| Horizon | Sonnet | Opus |
| --- | --- | --- |
| 0–1 | `medium` | `high` |
| 2 | `high` | `xhigh` |
| 3 | `high` | `xhigh`, or `max` when correctness dominates cost |

Coding and agentic work on Opus starts at `xhigh` regardless of horizon — that is
the policy's starting point, not an escalation. Omit `--effort` entirely for
Haiku; it does not accept the parameter.

## 4. Pick an execution shape

Exactly one:

| Shape | When |
| --- | --- |
| **Current session** | The active model and effort already fit |
| **Temporary effort increase** | Same model, one bounded difficult step |
| **New session** | A different model is needed for substantial work |
| **Subagent** | A bounded specialist task should use another model without disturbing the main conversation |
| **Parallel scouts** | Several independent searches or analyses, on Haiku or Sonnet |
| **Advisor plus implementer** | Opus analyzes and reviews; Sonnet implements |
| **Agent team** | Genuinely independent workstreams justify the coordination overhead |
| **Fable autonomous run** | Exceptional long-horizon task |

Read the policy's **Execution-shape notes** before recommending a subagent or a
verification pass on Opus — both have caveats that change the recommendation.

## 5. Output

Return exactly this structure and nothing else. Every angle-bracket field is
required; omit an optional section only when the stated condition does not hold.

```
Model: <haiku | sonnet | opus | fable | claude-opus-4-8>
Effort: <low | medium | high | xhigh | max | omit for haiku>
Execution shape: <one shape from the table above>
Confidence: <low | medium | high>

Score: novelty N, horizon N, oracle N, blast radius N, context N — total N/15
<or: "Hard override: <which one> — scoring skipped">

Reasons:
- <what in the task drove the highest-scoring dimension>
- <what drove the effort level>
- <what drove the execution shape>

Why not one tier cheaper:
- <the specific thing the cheaper tier would likely get wrong, not a restatement of the score>

Escalate if:
- <observable signal that would justify moving up>
- <a second signal>

Suggested command: `claude --model <alias> --effort <level>`
```

Two conditional sections, each included **only** when its condition holds:

- **Refusal risk** — the task is security-adjacent. State that Opus 5 and Fable 5
  may decline it and name `claude-opus-4-8` as the fallback.
- **Cache note** — the recommendation implies switching models inside a running
  conversation. State that this invalidates the prompt cache and re-reads the
  history at full price, and that a new session or subagent avoids it.

## Rules for the output

- **"Why not one tier cheaper" must name a failure, not a feeling.** "Sonnet
  would likely miss the write-skew under `READ COMMITTED`" is useful; "this needs
  deeper reasoning" is not. If you cannot name the failure, the cheaper tier is
  probably right — change the recommendation.
- Confidence is `low` whenever you scored a dimension from an assumption rather
  than from the task description or the repository.
- Recommend the cheapest option that clears the bar. This skill exists to prevent
  overspending as much as underspending; a reflexive Opus recommendation makes it
  worthless.
- Do not run the suggested command, and do not begin the underlying task.
