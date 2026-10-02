# OpenAI prompting policy

Last reviewed: 2026-10-02

Apply **Common** plus exactly one selected-model section. These rules adapt the
prompt after routing; they do not choose or upgrade the model.

Primary sources:
- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

## Common — GPT-6 family

**Provider guidance:** favor leaner prompts. OpenAI reports internal coding-agent
evals where removing repeated instructions/examples and simplifying tool
descriptions improved scores while materially reducing tokens and cost.

Apply that conservatively:
- state each instruction once;
- expose/describe only tools that matter to the task;
- keep examples only when they encode a real contract or measured correction;
- remove legacy scaffolding whose purpose was to compensate for older models;
- audit overlapping task prompt + AGENTS.md + skills rather than stacking all
  three blindly.

Do not strip project requirements merely to make a prompt shorter.

### Role and workflow

For coding/agentic tasks, a concise role plus concrete completion criteria can
help when the harness does not already provide them. Do not add a generic
"you are an expert software engineer" line if Codex/system instructions already
establish the role.

### Testing

Name the verification scope the task actually needs. Prefer "run affected tests"
over a generic demand for exhaustive testing on every change.

### Reasoning

Do not write "think step by step" or "think harder". `reasoning.effort` is a
model setting chosen upstream.

### Current model aliases

Profiles in this file cover:
- `gpt-6-luna`
- `gpt-6-sol`
- `gpt-6.1-sol` (use the Sol profile until a durable model-specific prompting
  delta is documented here)
- `gpt-6-astra`

Unknown GPT-6 variants receive **Common** guidance only unless `--research`
finds a primary-source delta.

## GPT-6 Luna

OpenAI positions Luna for focused, high-volume tasks. No durable prompt-specific
behavior beyond the GPT-6 family guidance is currently encoded here.

**Project rule:** keep Luna prompts highly bounded:
- one concrete objective;
- explicit input/output contract;
- a strong oracle when available;
- no optional research/planning branches unless required.

Do not try to turn an ambiguous/high-risk task into a Luna task through a more
elaborate prompt. That belongs in routing.

## GPT-6 Sol / GPT-6.1 Sol

Use GPT-6 Common guidance. Sol is capable enough that extra procedural
scaffolding should be justified by the task, not inherited from older prompts.

For substantial coding:
- keep architectural constraints and invariants;
- name the actual definition of done;
- name affected verification when correctness has a good oracle;
- allow the model to choose implementation details that are not constrained.

Do not add Astra-specific "make assumptions instead of asking" or subagent
instructions unless the observed Sol behavior actually needs them.

## GPT-6 Astra

Sources:
- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

### Initiative and follow-through

**Provider guidance:** Astra may stop to ask when additional information could
change the result.

When the task is safe/reversible and the user expects autonomous completion,
explicitly permit reasonable assumptions and continued execution:
- proceed with reasonable reversible assumptions when details are non-material;
- ask only when the missing information materially changes the result or safety.

Do not add this permission to destructive, irreversible, financial, security,
or otherwise sensitive actions.

### Instruction sensitivity

Astra follows instructions strongly and can be sensitive to skills and
`AGENTS.md`.

Before adding a task-level rule, ask whether the project/harness already states
it. Avoid duplicate or contradictory instructions. If inherited project rules
are known to be stale, surface the conflict instead of trying to overpower them
with stronger wording.

### Testing and verification

Astra tends to test thoroughly. For small changes, bound the verification scope
when broad testing would waste time:
- run the affected tests/build;
- do not expand to unrelated suites unless a failure or dependency justifies it.

For consequential changes, keep the stronger verification contract.

### Subagents

Astra may delegate less than desired. Add explicit subagent guidance only when
the task actually contains independent parallel work, and specify a cap/purpose.
Do not add delegation to ordinary single-threaded work.

### Style

Astra can produce detailed, highly formatted responses. Specify output density
or structure only when the deliverable benefits from it. For coding tasks whose
real artifact is the patch, prefer a concise final summary rather than elaborate
narrative.

### Prompt debt from older agents

Remove old scaffolding that:
- forces repeated check-ins;
- demands exhaustive testing for every edit;
- repeats repository rules already supplied elsewhere;
- prescribes an unnecessarily rigid step-by-step workflow.

Keep any such rule that encodes a real safety boundary or measured requirement.
