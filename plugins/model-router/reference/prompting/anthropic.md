# Anthropic prompting policy

Last reviewed: 2026-10-07

Apply **Common** plus exactly one selected-model section. These are prompt
adaptation deltas, not routing rules; model and effort are already chosen.

Primary sources:
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
- https://platform.claude.com/docs/en/build-with-claude/effort

## Common

**Provider guidance.** Claude responds well to clear, direct instructions with
the context needed to do the task. Use examples and XML/section structure when
they genuinely disambiguate instructions, context, examples, and input; do not
apply those techniques mechanically.

**Project rule.** Prefer outcome + constraints + definition of done over telling
Claude how to reason internally. Effort/thinking controls are model settings,
not prompt prose.

For long supplied documents, keep the documents/context clearly separated from
the task. Do not repeat the same instructions before and after the context merely
for emphasis.

When current/external facts are required, say so explicitly and name the needed
tool/search behavior only if the harness exposes it.

### Alias mapping

- `haiku` -> Haiku 5.5
- `sonnet` -> Sonnet 5.5
- `opus` -> Opus 5.5
- `fable` -> Fable 5.1

Exact version IDs use the matching section when recognizable.

## Haiku 5.5

Source:
https://www.anthropic.com/claude-haiku-5-5

Haiku 5.5 is the first Haiku with adjustable effort. Keep the task bounded and
let the router's effort setting control how much work the model spends; do not
simulate effort with "think harder" prompt prose.

**Project rule:** keep Haiku prompts compact and bounded:
- state the concrete transformation/task;
- include the strong oracle or output contract;
- specify exact scope when repository breadth could expand accidentally;
- avoid optional exploration, broad research, or elaborate planning scaffolds.

For focused coding, subagent work, browser/computer use, classification,
summarization, routing, and compaction, give a crisp output contract and the
available oracle. Do not add "think harder" instructions. If the task needs
nuanced judgment or a weak oracle, that is a routing concern, not a prompting
fix.

## Sonnet 5.5

Source:
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

### Initiative and completion

**Provider guidance.** On long agentic work, especially at lower effort, Sonnet
5.5 may stop and check in before the task is complete.

When the task is meant to be autonomous and reversible, add a concise completion
boundary such as:
- continue until the stated definition of done is met;
- make reasonable reversible assumptions;
- ask only when missing information would materially change the result or make
  an action unsafe.

Do not add this to ordinary conversational or advisory prompts.

### Scope control

When scope creep is plausible, state what is **not** part of the task. Prefer a
specific boundary ("change only the affected component and tests") over generic
"do not over-engineer" language.

### Verification

**Provider guidance.** At lower effort, Sonnet can keep reasoning short and may
skip verification on coding work.

When coding has a useful oracle, name bounded verification explicitly:
- build/compile;
- affected unit/integration tests;
- a specific reproduction.

Do not instruct it to run broad suites for a tiny local change unless the task
requires that coverage.

### Search/tool triggering

If the task requires fresh information, documentation lookup, or repository
search before editing, say so. Do not add search merely as a generic best
practice.

### Effort-aware prompting

The router owns effort. Do not compensate for a low effort selection by adding
"think deeply" or verbose reasoning instructions.

For well-specified agentic coding, Anthropic recommends `medium` as a starting
point; harder/longer work moves to `high`. `xhigh` and `max` should be
eval-driven. `prepare-prompt` must not change the selected effort.

### Per-message effort and cache

Sonnet 5.5 supports per-message effort (beta) through `output_config`, which
preserves the prompt cache when adaptive thinking is used. With
`between_tools`, changing effort mid-conversation is not supported.

This is an execution note; do not insert API parameter instructions into a
normal Claude Code task prompt.

## Opus 5.5

Source:
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5

### Let effort control thinking

Opus 5.5 uses effort as the primary quality/latency/cost control. Do not add
prompt text telling it to think less or think longer to compensate for model
settings. Keep the task prompt about the work.

### Judgment-heavy work

Opus is typically selected because ambiguity, weak oracle, architecture, or
semantic risk matters. Preserve that ambiguity rather than fabricating a
procedural recipe. Supply:
- the actual constraints;
- relevant evidence;
- decision criteria;
- what must remain compatible.

Let the model choose the reasoning path.

### Verification

Do not automatically add a separate "double-check everything" instruction.
When the task has a concrete oracle, name it. When independent verification is
actually required, say why it must be independent.

### Subagents

If the task genuinely benefits from parallel specialists, specify the purpose
and a bound on fan-out. Do not add subagents solely because Opus can delegate.

### Long autonomous work

For an autonomous task, define completion and safe assumption boundaries. Avoid
repeated reminders to continue; one crisp completion contract is preferable.

### Per-message effort and cache

Opus 5.5 supports per-message effort via `output_config` while preserving prompt
cache. Keep this as harness/API configuration, not task prose.

## Fable 5.1

Source:
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1

Fable is evidence-gated in the routing policy. If it has already been selected,
adapt the prompt for the documented behavior; do not second-guess routing.

### Long-task completion

For multi-step work, make the completion boundary explicit. If premature
stopping would be costly, state that it should continue through the defined
deliverable unless genuinely blocked.

### Progress updates

Fable 5.1 can provide little user-facing text between tool calls. Add a request
for concise progress updates only when the user will be watching a long run and
those updates are useful. Do not force commentary into short tasks.

### Tool-call batching

When several tool calls are independent, a prompt may explicitly permit
batching/parallel calls. Do not add this when ordering or dependencies matter.

### Search triggering

At lower effort, make required external/repository search explicit when the task
cannot be completed reliably from supplied context.

### Writing and formatting

Specify density, format, or output structure when the deliverable depends on it.
Do not add style constraints merely to counter a general model tendency.

### Per-message effort and cache

Fable 5.1 supports per-message effort changes that preserve prompt cache. Keep
that configuration outside the normal task prompt unless the user is explicitly
asking for API request construction.
