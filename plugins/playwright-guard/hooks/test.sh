#!/usr/bin/env bash
# Tests for playwright-code-guard.sh. Feeds hook JSON on stdin and checks the
# outcome: pass (no output, exit 0), ask / allow (decision JSON, exit 0) or
# block (exit 2). Fixtures live in a temp dir; nothing is written elsewhere.
#
# The guard runs with PATH limited to bash, jq, grep, sed and coreutils
# (realpath, cat, head), so a new dependency fails the suite.
#
# Usage: hooks/test.sh

set -u

here=$(cd "$(dirname "$0")" && pwd)
guard=$here/playwright-code-guard.sh

for dep in jq bash grep sed realpath cat head mktemp ln; do
  command -v "$dep" >/dev/null 2>&1 || { echo "test.sh needs $dep" >&2; exit 1; }
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

bin=$tmp/bin
mkdir -p "$bin"
for dep in bash jq grep sed realpath cat head; do ln -s "$(command -v "$dep")" "$bin/$dep"; done
nojq=$tmp/bin-nojq
mkdir -p "$nojq"
for dep in bash grep sed realpath cat head; do ln -s "$(command -v "$dep")" "$nojq/$dep"; done

root=$tmp/project
scripts=$root/.playwright-mcp/guarded-scripts
outside=$tmp/outside
mkdir -p "$scripts/sub" "$outside" "$root/.playwright-mcp/other" "$tmp/elsewhere/.playwright-mcp/guarded-scripts"

fixture() { printf '%s\n' "$2" >"$scripts/$1.js"; }

fixture clean 'async (page) => {
  await page.goto("https://example.test/");
  return await page.title();
}'
fixture get 'async (page) => {
  const r = await page.request.get("https://example.test/api/a");
  return r.status();
}'
fixture head 'async (page) => (await page.request.head("https://example.test/api/a")).status()'
fixture request-call 'async (page) => {
  const res = await page.goto("https://example.test/");
  return res.request().url();
}'
fixture require 'async (page) => { return require("fs").readFileSync("/etc/hostname", "utf8"); }'
fixture require-space 'async (page) => { return require ("fs"); }'
fixture dynamic-import 'async (page) => { const fs = await import("fs"); return fs; }'
fixture import 'import fs from "fs";
async (page) => fs'
fixture process 'async (page) => process.env'
fixture child-process 'async (page) => { const cp = "child_process"; return cp; }'
fixture eval 'async (page) => eval("1 + 1")'
fixture function 'async (page) => Function("return this")()'
fixture globalthis 'async (page) => globalThis'
fixture module 'async (page) => module.exports'
fixture dirname 'async (page) => __dirname'
fixture buffer 'async (page) => Buffer.from("x")'
fixture constructor 'async (page) => page.constructor["constructor"]("return 1")()'
fixture constructor-chain 'async (page) => page.constructor.constructor("return 1")()'
fixture put 'async (page) => page.request.put("https://example.test/api/a", { data: {} })'
fixture post 'async (page) => page.request.post("https://example.test/api/a", { data: {} })'
fixture fetch-method 'async (page) => page.request.fetch("https://example.test/api/a", { method: "PUT" })'
fixture quoted-method 'async (page) => page.request.get("https://example.test/api/a", { "method": "POST" })'
fixture alias 'async (page) => {
  const r = page.request;
  return r.put("https://example.test/api/a");
}'
fixture index 'async (page) => page.request["put"]("https://example.test/api/a")'
fixture page-fetch 'async (page) => page.evaluate(() => fetch("https://example.test/api/a", { method: "DELETE" }))'
fixture route 'async (page) => page.route("**/*", (r) => r.fulfill({ body: "" }))'
fixture new-context 'async (page) => (await page.context().browser().newContext()).pages()'
cp "$scripts/clean.js" "$scripts/sub/clean.js"
mkdir -p "$scripts/dir.js"
cp "$scripts/clean.js" "$scripts/dir.js/clean.js"
cp "$scripts/clean.js" "$outside/clean.js"
cp "$scripts/clean.js" "$root/.playwright-mcp/other/clean.js"
cp "$scripts/clean.js" "$tmp/elsewhere/.playwright-mcp/guarded-scripts/clean.js"
ln -s "$outside/clean.js" "$scripts/link-out.js"
printf 'async (page) => require("fs")\n' >"$outside/evil.js"
ln -s "$outside/evil.js" "$scripts/link-evil.js"

# Custom glob with a directory wildcard, plus a symlinked directory escaping it.
evidence=$root/.playwright-mcp/evidence
mkdir -p "$evidence/T1/scripts" "$evidence/T1/x/scripts" "$outside/T2/scripts"
cp "$scripts/clean.js" "$evidence/T1/scripts/a.js"
cp "$scripts/clean.js" "$evidence/T1/x/scripts/a.js"
cp "$scripts/clean.js" "$outside/T2/scripts/a.js"
ln -s "$outside/T2" "$evidence/T2"
evidence_glob='.playwright-mcp/evidence/*/scripts/*.js'

RUN=mcp__playwright__browser_run_code_unsafe
RUN_PLUGIN=mcp__plugin_playwright_playwright__browser_run_code_unsafe
EVAL=mcp__playwright__browser_evaluate
EVAL_PLUGIN=mcp__plugin_playwright_playwright__browser_evaluate

pass=0
fail=0

# check <expect> <description> <stdin> [VAR=value ...]
# Runs with CLAUDE_PROJECT_DIR=$root unless overridden.
check() {
  local expect=$1 desc=$2 stdin=$3 out err code got
  shift 3
  out=$(env -i PATH="$bin" CLAUDE_PROJECT_DIR="$root" "$@" bash "$guard" <<<"$stdin" 2>"$tmp/stderr")
  code=$?
  err=$(cat "$tmp/stderr")
  if [[ $code -eq 2 ]]; then
    got=block
    [[ -n "$err" && -z "$out" ]] || got="block (stderr empty or stdout set)"
  elif [[ $code -ne 0 ]]; then
    got="exit $code"
  elif [[ -z "$out" ]]; then
    got=pass
  else
    got=$(jq -r 'if .hookSpecificOutput.hookEventName == "PreToolUse"
                    and (.hookSpecificOutput.permissionDecisionReason | type == "string" and length > 0)
                 then .hookSpecificOutput.permissionDecision
                 else "malformed decision" end' <<<"$out" 2>/dev/null) || got="invalid JSON: $out"
  fi
  if [[ "$got" == "$expect" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    printf 'FAIL  %s: expected %s, got %s\n      stdout: %s\n      stderr: %s\n' "$desc" "$expect" "$got" "$out" "$err"
  fi
}

file_input() { jq -cn --arg t "$1" --arg f "$2" --arg c "${3:-$root}" '{hook_event_name: "PreToolUse", tool_name: $t, cwd: $c, tool_input: {filename: $f}}'; }
code_input() { jq -cn --arg t "$1" --arg code "$2" --arg c "$root" '{hook_event_name: "PreToolUse", tool_name: $t, cwd: $c, tool_input: {code: $code}}'; }
eval_input() { jq -cn --arg t "$1" --arg fn "$2" --arg c "$root" '{hook_event_name: "PreToolUse", tool_name: $t, cwd: $c, tool_input: {function: $fn}}'; }

for name in "$RUN" "$RUN_PLUGIN"; do
  n=${name%%__browser*}
  # Regression: this exact input used to pass silently under Claude Code names.
  check ask "$n: inline require(\"fs\")" \
    "{\"tool_name\":\"$name\",\"tool_input\":{\"code\":\"async (page) => { return require(\\\"fs\\\") }\"}}"
  check ask "$n: inline clean code" "$(code_input "$name" 'async (page) => page.title()')"
  check ask "$n: inline code next to an allowed filename" \
    "$(jq -cn --arg t "$name" --arg f "$scripts/clean.js" '{tool_name: $t, tool_input: {filename: $f, code: "async (page) => 1"}}')"
  check ask "$n: neither code nor filename" "{\"tool_name\":\"$name\",\"tool_input\":{}}"
  check ask "$n: non-string filename" "{\"tool_name\":\"$name\",\"tool_input\":{\"filename\":[\"a.js\"]}}"

  for f in clean get head request-call; do
    check allow "$n: $f.js" "$(file_input "$name" "$scripts/$f.js")"
  done
  for f in require require-space dynamic-import import process child-process eval function globalthis module \
    dirname buffer constructor constructor-chain put post fetch-method quoted-method alias index page-fetch route new-context; do
    check ask "$n: $f.js" "$(file_input "$name" "$scripts/$f.js")"
  done

  check allow "$n: relative filename resolves against CLAUDE_PROJECT_DIR" \
    "$(file_input "$name" .playwright-mcp/guarded-scripts/clean.js "$tmp/elsewhere")"
  check allow "$n: relative filename resolves against cwd without CLAUDE_PROJECT_DIR" \
    "$(file_input "$name" .playwright-mcp/guarded-scripts/clean.js)" CLAUDE_PROJECT_DIR=
  check ask "$n: cwd cannot move the allowed folder when CLAUDE_PROJECT_DIR is set" \
    "$(file_input "$name" .playwright-mcp/guarded-scripts/clean.js "$tmp/elsewhere")" CLAUDE_PROJECT_DIR="$root/sub"
  check allow "$n: .. that stays inside the folder" \
    "$(file_input "$name" .playwright-mcp/other/../guarded-scripts/clean.js)"
  check ask "$n: .. escaping the folder" "$(file_input "$name" .playwright-mcp/guarded-scripts/../other/clean.js)"
  check ask "$n: absolute path outside the project" "$(file_input "$name" "$outside/clean.js")"
  check ask "$n: symlink in the folder to a clean file outside" "$(file_input "$name" "$scripts/link-out.js")"
  check ask "$n: symlink in the folder to a dirty file outside" "$(file_input "$name" "$scripts/link-evil.js")"
  check ask "$n: file nested below the glob" "$(file_input "$name" "$scripts/sub/clean.js")"
  check ask "$n: file below a folder whose name matches the glob" "$(file_input "$name" "$scripts/dir.js/clean.js")"
  check ask "$n: wrong extension" "$(file_input "$name" "$scripts/clean.ts")"
  check ask "$n: missing file" "$(file_input "$name" "$scripts/missing.js")"
  check ask "$n: directory instead of file" "$(file_input "$name" "$scripts/sub")"

  check allow "$n: custom glob, file in a ticket folder" \
    "$(file_input "$name" "$evidence/T1/scripts/a.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="$evidence_glob"
  check ask "$n: custom glob, * does not cross /" \
    "$(file_input "$name" "$evidence/T1/x/scripts/a.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="$evidence_glob"
  check ask "$n: custom glob, symlinked ticket folder outside" \
    "$(file_input "$name" "$evidence/T2/scripts/a.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="$evidence_glob"
  check ask "$n: custom glob, default folder no longer allowed" \
    "$(file_input "$name" "$scripts/clean.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="$evidence_glob"
  check allow "$n: custom glob with leading ./" \
    "$(file_input "$name" "$evidence/T1/scripts/a.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="./$evidence_glob"
  check ask "$n: glob with .. is rejected" \
    "$(file_input "$name" "$scripts/clean.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB='.playwright-mcp/x/../guarded-scripts/*.js'
  check ask "$n: absolute glob is rejected" \
    "$(file_input "$name" "$scripts/clean.js")" PLAYWRIGHT_GUARD_SCRIPTS_GLOB="$scripts/*.js"

  check block "$n: no jq fails closed" "$(file_input "$name" "$scripts/clean.js")" PATH="$nojq"
done

for name in "$EVAL" "$EVAL_PLUGIN"; do
  n=${name%%__browser*}
  check pass "$n: evaluate without network" "$(eval_input "$name" '() => document.title')"
  check ask "$n: evaluate with fetch(" "$(eval_input "$name" '() => fetch("/api/a").then((r) => r.status)')"
  check ask "$n: evaluate with fetch (" "$(eval_input "$name" '() => fetch ("/api/a")')"
  check ask "$n: evaluate with sendBeacon" "$(eval_input "$name" '() => navigator.sendBeacon("/api/a", "x")')"
  check ask "$n: evaluate with XMLHttpRequest" "$(eval_input "$name" '() => new XMLHttpRequest()')"
  check ask "$n: evaluate with WebSocket" "$(eval_input "$name" '() => new WebSocket("wss://example.test")')"
done

check pass "other Playwright tool" "$(jq -cn '{tool_name: "mcp__playwright__browser_navigate", tool_input: {url: "https://example.test"}}')"
check pass "unrelated tool" '{"tool_name":"Bash","tool_input":{"command":"ls"}}'
check pass "no tool_name" '{"tool_input":{}}'
check block "invalid JSON fails closed" 'not json'
check block "empty stdin fails closed" ''
check block "JSON that is not an object fails closed" '["mcp__playwright__browser_run_code_unsafe"]'

echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
