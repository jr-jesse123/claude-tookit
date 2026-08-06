---
name: name
description: Distill the current session into a short, searchable name and hand back the exact /rename command to apply it. Use when the user asks to name or rename this session, wants to find this conversation again later, or asks for help organizing sessions.
argument-hint: "[optional hint about what this session is really about]"
allowed-tools: Bash(git status *), Bash(git branch *), Bash(git log *), Bash(git rev-parse *)
---

# Name this session

Produce one name the user can find this session by, weeks from now, among dozens
of others. You cannot rename the session yourself — there is no tool for it, and
`/rename` only works when the **user** types it. Your deliverable is the name
plus the ready-to-paste command. Never claim the session was renamed.

## 1. Know what the picker already shows

The session picker (`/resume`, `claude --resume`) displays, per session: the
name, a summary, time since last activity, the **git branch**, and the
**project path**. So the name must not waste words repeating any of that:

- No repo or project name — the picker shows the path.
- No branch name — the picker shows the branch.
- No dates or "today"/"v2" — the picker shows recency.

The name carries the one thing the picker cannot infer: **intent + object** —
what the user was trying to accomplish, on what.

## 2. Distill the session

From the conversation (and `$ARGUMENTS`, if given — it overrides your reading):

- **The goal, not the current step.** A session that spent an hour on a failing
  test in service of adding OAuth is an OAuth session, not a test session. Name
  what the session will have been about when it ends.
- **The distinguishing detail.** "auth" is useless next to three other auth
  sessions; "auth-token-refresh" survives. If git context helps disambiguate
  (branch, recent commits), read it — but only to sharpen the object, never to
  copy the branch name in.
- If the session genuinely carries two unrelated work streams, name the
  dominant one and say so — one session, one name.

## 3. Shape the name

Rules, in priority order:

1. **kebab-case, 2–5 words, ≤ 40 chars.** Kebab-case makes it a shell-safe
   resume handle: `claude --resume auth-token-refresh` needs no quotes.
2. **Front-load the distinguishing term.** Pickers truncate; search matches
   prefixes. `token-refresh-auth-flow` beats `implement-new-auth-flow-tokens`.
3. **Pick the shape by session type:**

   | Session type | Shape | Example |
   | --- | --- | --- |
   | Feature / build | `<object>-<capability>` | `session-naming-skill` |
   | Bug / debugging | `<symptom>-<component>` | `login-500-token-expiry` |
   | Research / decision | `<topic>-<question>` | `queue-vs-cron-tradeoff` |
   | Review | `review-<subject>` | `review-payment-retries` |
   | Recurring / ops | `<system>-<routine>` | `staging-deploy-friday` |

4. **Ban the filler words:** fix, help, work, task, session, claude, new, misc,
   stuff, wip, update, changes. Each says nothing that distinguishes this
   session from any other.
5. **Avoid prefix collisions.** `claude --resume` matches names by search; if
   the user likely has sibling sessions (`api-auth`, `api-rate-limit`), make
   the first word the differentiator, not the shared prefix.

## 4. Deliver

Output exactly this structure:

1. The recommended name, with one line on why it will be findable.
2. Up to two alternatives only if they capture a genuinely different framing —
   not spelling variations.
3. The command, ready to paste:

   ```
   /rename <recommended-name>
   ```

4. One line on retrieval, so the name pays off: `claude --resume <name>` jumps
   straight back; `/resume` searches by name; in the picker, `Ctrl+R` renames
   without entering; on claude.ai and the desktop app, edit the title in the
   sidebar (syncs to the CLI on v2.1.221+).

If the session pivots to a different goal later, the user can re-invoke this
skill — a name that described the plan but not the outcome is the failure mode
this skill exists to prevent.
