#!/usr/bin/env bash
# PreToolUse guard for the two Playwright MCP tools that run code.
#
# browser_run_code_unsafe runs JavaScript inside the Playwright server process:
# treat it as remote code execution. browser_evaluate runs JavaScript in the page.
#
# Policy ("ask by default"):
#   browser_evaluate        ask when the function makes a network call
#                           (fetch(, XMLHttpRequest, sendBeacon, WebSocket, axios,
#                           .ajax); otherwise no output, so the normal permission
#                           flow applies.
#   browser_run_code_unsafe ask, except for one shape that is allowed without a
#                           prompt: `filename` names an existing file whose resolved
#                           path (realpath, so `..` and symlinks cannot escape)
#                           matches the scripts glob under the project root, and
#                           the file has no Node-escape token, no direct-HTTP token
#                           and no `.request` use other than .request.get(,
#                           .request.head( or .request().
#   any other tool          no output.
#
# Configuration:
#   PLAYWRIGHT_GUARD_SCRIPTS_GLOB  scripts glob relative to the project root.
#                                  Default: .playwright-mcp/guarded-scripts/*.js
#                                  `*` never crosses a `/`; no `**`.
#   Project root: $CLAUDE_PROJECT_DIR, else the hook input's `cwd`, else $PWD.
#   Relative filenames resolve against the project root.
#
# The checks are lexical. They catch mistakes and naive injected code, not a
# deliberate bypass (string building, indirection). See README.md.
#
# Needs bash, jq, grep and GNU realpath (-m). Fails closed (exit 2) without them
# or when the hook input is not a JSON object.

set -u

block() {
  echo "playwright-guard: $1" >&2
  exit 2
}

decide() {
  jq -cn --arg d "$1" --arg r "playwright-guard: $2" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'
  exit 0
}

command -v jq >/dev/null 2>&1 || block "jq not found; install jq. Blocking the Playwright code call."
realpath -m / >/dev/null 2>&1 || block "GNU realpath (with -m) not found; install coreutils. Blocking the Playwright code call."

input=$(cat)
jq -e 'type == "object"' >/dev/null 2>&1 <<<"$input" || block "hook input is not a JSON object. Blocking the Playwright code call."

tool=$(jq -r '.tool_name // "" | strings' <<<"$input")
# mcp__playwright__browser_evaluate, mcp__plugin_playwright_playwright__browser_evaluate, ...
tool=${tool##*__}

page_net_tokens='fetch[[:space:]]*\(|XMLHttpRequest|sendBeacon|WebSocket|axios|\.ajax'
escape_tokens='require[[:space:]]*\(|import[[:space:]]*\(|^[[:space:]]*import[[:space:]]|child_process|process|eval[[:space:]]*\(|Function[[:space:]]*\(|globalThis|module|__dirname|Buffer|constructor'
script_net_tokens="$page_net_tokens"'|newContext|\.route\(|routeFromHAR|routeWebSocket|\.request\[|method["'"'"']?[[:space:]]*:'

case "$tool" in
  browser_evaluate)
    if jq -c '.tool_input // {}' <<<"$input" | grep -Eq -- "$page_net_tokens"; then
      decide ask "browser_evaluate function makes a network call."
    fi
    exit 0
    ;;
  browser_run_code_unsafe) ;;
  *) exit 0 ;;
esac

code=$(jq -r '.tool_input.code // "" | if type == "string" then . else tojson end' <<<"$input")
[[ -z "$code" ]] || decide ask "inline code in browser_run_code_unsafe; only script files in the allowed folder run without a prompt."

filename=$(jq -r '.tool_input.filename // "" | if type == "string" then . else tojson end' <<<"$input")
[[ -n "$filename" ]] || decide ask "browser_run_code_unsafe without a script file."
[[ "$filename" != *$'\n'* ]] || decide ask "script filename contains a newline."

root=${CLAUDE_PROJECT_DIR:-}
[[ -n "$root" ]] || root=$(jq -r '.cwd // "" | strings' <<<"$input")
[[ -n "$root" ]] || root=$PWD
root=$(realpath -m -- "$root")

glob=${PLAYWRIGHT_GUARD_SCRIPTS_GLOB:-.playwright-mcp/guarded-scripts/*.js}
glob=${glob#./}
case "/$glob/" in
  //* | */../* | */./* | *//*) decide ask "PLAYWRIGHT_GUARD_SCRIPTS_GLOB must be a relative path without '.', '..' or empty segments (got '$glob')." ;;
esac

[[ "$filename" == /* ]] && path=$filename || path=$root/$filename
resolved=$(realpath -m -- "$path")

# Anchored, segment-by-segment match: same number of segments, each one
# matching its glob segment, so `*` never crosses a `/`.
in_glob() {
  local rel segs pats i
  if [[ "$root" == / ]]; then
    rel=${resolved#/}
  else
    [[ "$resolved" == "$root"/* ]] || return 1
    rel=${resolved#"$root"/}
  fi
  IFS=/ read -ra segs <<<"$rel"
  IFS=/ read -ra pats <<<"$glob"
  ((${#segs[@]} == ${#pats[@]})) || return 1
  for i in "${!pats[@]}"; do
    # shellcheck disable=SC2053 # the right side is a glob pattern on purpose
    [[ "${segs[$i]}" == ${pats[$i]} ]] || return 1
  done
}

in_glob || decide ask "script $resolved is outside the allowed folder ($glob under $root)."
[[ -f "$resolved" && -r "$resolved" ]] || decide ask "script $resolved is missing or unreadable."

if grep -Eq -- "$escape_tokens" "$resolved"; then
  decide ask "script $resolved contains a Node-escape token ($(grep -Eo -- "$escape_tokens" "$resolved" | head -n1))."
fi
if grep -Eq -- "$script_net_tokens" "$resolved"; then
  decide ask "script $resolved makes a direct HTTP call or changes routing ($(grep -Eo -- "$script_net_tokens" "$resolved" | head -n1))."
fi
# Any .request left after removing the allowed GET/HEAD forms.
if sed -E 's/\.request\.(get|head)[[:space:]]*\(//g; s/\.request\(\)//g' "$resolved" | grep -q '\.request'; then
  decide ask "script $resolved uses .request in a form other than .request.get(, .request.head( or .request()."
fi

decide allow "script $resolved is in the allowed folder and passed the lexical checks."
