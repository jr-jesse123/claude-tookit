# Target profile

One Markdown file per environment the project verifies against, in the folder the config names (`targetsDir`, default `.claude/ui-targets/`). The file name is the target name: `int.md`, `local.md`, `staging.md`. The skill reads it at the start of a run and gives its path to every agent. Everything that differs between environments belongs here, so the skill, the planner and the executors stay the same for all of them.

A profile answers the same questions every time. Use these headings, in this order; leave a heading out only when it does not apply and say so.

## Hosts
The URLs of each app and of the login service. The executors open no host outside this list. Name the hosts that must never be opened (production) when the Playwright MCP does not already block them.

## Pre-run checks
What must be true before the browser opens and how to see it: the environment is up (ports that answer), the VPN is on or off, the branch under test is the one deployed or built, a seed has run. The skill stops with the reason when one fails and does not start the environment unasked.

## Login and account switch
The steps to log in and out and to pick an organization, written for an agent that has no memory of them: the pages, the test ids or the visible text, what a logged-out page looks like. Where the accounts live (a file in the repo, a git-ignored secrets file, a seed). Never write a password in a profile that is committed.

The rule the skill enforces: every account change is its own stage (logout, check the empty login form, login, org pick), and a session that was logged in before the run may still be logged in after a "logout" that did not finish.

## Account check
A recipe the controller runs after every switch to prove who the browser is, because the page may not show it. State the request to look for, the field to extract and what to compare it with. Example (a GraphQL app that has a current-user query): `browser_network_requests` with filter `CurrentUser`, take the last match, save its response body to a file, `jq -r '.data.currentUser.email'` on it, delete the file, compare with the stage's `account`.

## Write policy
Which writes a run may make and who decides. State it as the user's rule, with the author and the date, because the skill copies it into the approval line.

- A shared environment: writes only on data the run creates, only the exact writes approved, a yes per run.
- A sandbox (a local or throwaway environment): writes are announced and run without an approval stop. List what still needs a yes (resets, replay scripts, deletes of existing data, restarts).

## Backend evidence
How the backend side of a run is read. One of:
- `agent: <name>`: a project agent that reads logs, traces and metrics (read-only), with its retention. The skill starts it with the run's window, entity ids and questions.
- `controller reads`: the read-only calls the controller makes itself (a search query, a queue listing, a dashboard page), each with its address.
- `none`.

## Build check
How to know which build of the service under test runs on this target (a version endpoint, a commit of each repository and whether the host restarted after the build). `repro` plans include it, because a deployed fix changes the outcome.

## Quirks
What bites an agent on this target: slow pages, timers lost on restart, features that fail on purpose, data that disappears, a cache that needs a restart after a seed change.
