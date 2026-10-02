# Harness prompting policy

Last reviewed: 2026-10-02

Apply exactly one harness section when the execution environment is known.
Harness rules exist mainly to prevent duplicated context.

## Claude Code

Claude Code already supplies:
- its system behavior and tool semantics;
- repository/project instructions such as CLAUDE.md when present;
- installed skills and their descriptions;
- conversation/session context.

Therefore the task prompt should usually contain:
- the task objective;
- task-specific context not already available;
- hard scope/permission boundaries;
- the definition of done and relevant oracle.

Do not paste CLAUDE.md, tool descriptions, skill instructions, or generic
"inspect the repository first" boilerplate back into every task unless the task
specifically depends on overriding/clarifying one of them.

When the provider profile says a model needs explicit search, verification,
completion, or progress behavior, add only the task-local instruction.

For long tasks, a concise completion contract is better than repeating "continue"
throughout the prompt.

## Codex

Codex may already receive repository instructions through AGENTS.md and skills.

Avoid duplicating:
- AGENTS.md rules;
- skill guidance;
- tool descriptions;
- generic software-engineering workflow prose.

This matters especially for GPT-6 Astra, which OpenAI documents as highly
sensitive to inherited instructions.

Prefer a task prompt that says:
- what outcome is wanted;
- what constraints/invariants matter;
- what files/area are in scope when that is not obvious;
- what bounded verification demonstrates completion.

When safe autonomous progress is desired, explicitly permit reasonable
reversible assumptions instead of adding a broad "never ask questions" rule.

## API

The API has less ambient context, so the adapted prompt may need more explicit
structure than Claude Code/Codex.

Keep stable application behavior separate from task-specific input when the
calling code supports separate instruction/system/developer fields. This:
- reduces repetition;
- makes cacheable prefixes more stable;
- avoids mixing product rules with one-off task details.

Tool descriptions belong in the tool schema/configuration, not duplicated in
the task prompt.

Output schemas belong in structured-output/API configuration when available;
do not reproduce a large JSON schema in prose unless the API surface requires it.

Provider-specific parameters such as effort, thinking mode, service tier, or
cache controls belong in request configuration, not task prose, unless the user
is explicitly asking to construct the request itself.

## Unknown harness

Apply no harness-specific deletion. Use provider/model guidance only and preserve
context that might otherwise have been supplied externally.
