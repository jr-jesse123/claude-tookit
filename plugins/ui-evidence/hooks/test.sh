#!/usr/bin/env bash
# Tests for playwright-code-guard.sh. Everything runs in a temp dir with a temp
# config; nothing is written into a real workspace.
#
# Usage: bash plugins/ui-evidence/hooks/test.sh

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
GUARD="$HERE/playwright-code-guard.sh"
TMP=$(mktemp -d)
trap 'rm -rf "${TMP:?}"' EXIT
unset UI_EVIDENCE_CONFIG CLAUDE_PROJECT_DIR

ROOT="$TMP/ws"
EV="$ROOT/.playwright-mcp/evidence"
DIR="$EV/2026-10-19-demo-todo"
mkdir -p "$ROOT/.claude" "$DIR/scripts" "$ROOT/nested/repo"
echo '{ "evidenceRoot": ".playwright-mcp/evidence" }' > "$ROOT/.claude/ui-evidence.json"

pass=0
fail=0

# The clean harness from references/recording.md, with a correct EVIDENCE_DIR.
harness() { # evidence dir, extra case code
  cat <<EOF
async (page) => {
  // Must equal this script's evidence folder (the parent of scripts/). The guard checks it.
  const EVIDENCE_DIR = '$1';
  const RUN = 'run-1';
  const at = () => new Date().toISOString();
  const steps = [];
  const read = async () => page.evaluate(() => document.querySelectorAll('.todo-list li').length);

  await page.screencast.start({ path: \`\${EVIDENCE_DIR}/\${RUN}.webm\`, size: { width: 1280, height: 800 } });
  try {
    await page.screencast.showActions({ duration: 600, position: 'top-right' });
    await page.screencast.showChapter('C1 – add a todo', { duration: 1500 });
    const before = await read();
    await page.getByPlaceholder('What needs to be done?').fill('buy milk');
    await page.keyboard.press('Enter');
    const after = await read();
    await page.screenshot({ path: \`\${EVIDENCE_DIR}/\${RUN}-C1-added.png\`, mask: [] });
    await page.screenshot({ path: EVIDENCE_DIR + '/' + RUN + '-C1-list.png' });
    const res = await page.request.get('https://x.test/api/items');
    const status = (await page.waitForResponse(/items/)).request().url();
$2
    steps.push({ id: 'C1', at: at(), before, after, items: res.status(), status });
  } catch (e) {
    steps.push({ at: at(), error: String(e) });
  } finally {
    await page.screencast.stop();
  }
  return steps;
}
EOF
}

write() { # name, content -> path
  printf '%s\n' "$2" > "$DIR/scripts/$1"
  printf '%s' "$DIR/scripts/$1"
}

payload() { # tool, input-json, [cwd]
  jq -cn --arg t "$1" --argjson i "$2" --arg c "${3:-$ROOT}" \
    '{hook_event_name: "PreToolUse", tool_name: $t, tool_input: $i, cwd: $c}'
}

decision_of() { # stdin-payload -> decision (or exit:N)
  local out rc
  out=$(printf '%s' "$1" | "$GUARD" 2>/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ]; then echo "exit:$rc"; return; fi
  if [ -z "$out" ]; then echo "silent"; return; fi
  printf '%s' "$out" | jq -r 'if .hookSpecificOutput.hookEventName == "PreToolUse"
    then .hookSpecificOutput.permissionDecision else "no-hookEventName" end'
}

check() { # label, expected, tool-short, input-json, [cwd]
  local label=$1 want=$2 short=$3 input=$4 cwd=${5:-$ROOT} name got
  for name in "mcp__playwright__$short" "mcp__plugin_playwright_playwright__$short"; do
    got=$(decision_of "$(payload "$name" "$input" "$cwd")")
    if [ "$got" = "$want" ]; then
      pass=$((pass + 1))
    else
      fail=$((fail + 1))
      echo "FAIL [$name] $label: want $want, got $got"
      printf '%s' "$(payload "$name" "$input" "$cwd")" | "$GUARD" 2>&1 | jq -r '.hookSpecificOutput.permissionDecisionReason? // .' 2>/dev/null | sed 's/^/       /'
    fi
  done
}

run() { jq -cn --arg f "$1" '{filename: $f}'; }

# ---- run_code_unsafe: clean scripts --------------------------------------

clean=$(write clean.js "$(harness "$DIR" "")")
check "clean harness" allow browser_run_code_unsafe "$(run "$clean")"
check "clean harness from a nested cwd" allow browser_run_code_unsafe "$(run "$clean")" "$ROOT/nested/repo"
check "spread operator is not '..'" allow browser_run_code_unsafe \
  "$(run "$(write spread.js "$(harness "$DIR" "    const all = [...steps];")")")"
check "non-secret fill while recording" allow browser_run_code_unsafe \
  "$(run "$(write fill.js "$(harness "$DIR" "    await page.getByLabel('Search').fill('milk');")")")"
# The harness exactly as documented, so the reference and the guard cannot drift apart.
documented=$(awk '/^#+ The harness/{h=1} h&&/^```js/{c=1;next} c&&/^```/{exit} c' \
  "$HERE/../skills/ui-evidence/references/recording.md" | sed "s#'/abs/evidence/folder'#'$DIR'#")
[ -n "$documented" ] || { echo "FAIL could not extract the harness from recording.md"; fail=$((fail + 1)); }
check "harness from references/recording.md" allow browser_run_code_unsafe \
  "$(run "$(write documented.js "$documented")")"
noshot=$(write noshot.js "async (page) => {
  const EVIDENCE_DIR = '$DIR';
  return page.title();
}")
check "script without recording" allow browser_run_code_unsafe "$(run "$noshot")"

# ---- run_code_unsafe: how the code arrives -------------------------------

check "inline require(\"fs\") (regression: was silent)" ask browser_run_code_unsafe \
  '{"code":"async (page) => { const fs = require(\"fs\"); return fs.readdirSync(\"/\"); }"}'
check "inline code even with a clean filename" ask browser_run_code_unsafe \
  "$(jq -cn --arg f "$clean" '{filename: $f, code: "async (page) => 1"}')"
check "no code, no filename" ask browser_run_code_unsafe '{}'
check "missing file" ask browser_run_code_unsafe "$(run "$DIR/scripts/nope.js")"
check "relative filename (resolved by the MCP, not by cwd)" ask browser_run_code_unsafe \
  "$(run ".playwright-mcp/evidence/2026-10-19-demo-todo/scripts/clean.js")"
check "outside the evidence root" ask browser_run_code_unsafe \
  "$(run "$(cp "$clean" "$ROOT/elsewhere.js" && echo "$ROOT/elsewhere.js")")"
mkdir -p "$DIR/other"
cp "$clean" "$DIR/other/clean.js"
check "not in a scripts/ folder" ask browser_run_code_unsafe "$(run "$DIR/other/clean.js")"
check "'..' escape in filename" ask browser_run_code_unsafe \
  "$(run "$DIR/scripts/../../../../elsewhere.js")"
mkdir -p "$TMP/outside"
cp "$clean" "$TMP/outside/evil.js"
ln -s "$TMP/outside/evil.js" "$DIR/scripts/link.js"
check "symlink escape" ask browser_run_code_unsafe "$(run "$DIR/scripts/link.js")"
got=$(printf 'not json' | "$GUARD" 2>/dev/null | jq -r '.hookSpecificOutput.permissionDecision')
if [ "$got" = "ask" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL invalid JSON: got $got"; fi

# ---- run_code_unsafe: escape and direct-HTTP tokens ----------------------

for snippet in \
  "const fs = require('fs');" \
  "const m = await import('fs');" \
  "const cp = 'child_process';" \
  "const env = process.env;" \
  "eval('1');" \
  "const f = Function('return 1');" \
  "const g = globalThis;" \
  "const x = module;" \
  "const d = __dirname;" \
  "const b = Buffer.from('x');" \
  "const c = page.constructor;" \
  "const r = await fetch('https://x.test');" \
  "await page.evaluate(() => fetch('https://x.test', { method: 'POST' }));" \
  "await page.evaluate(() => new XMLHttpRequest());" \
  "await page.evaluate(() => navigator.sendBeacon('https://x.test'));" \
  "await page.evaluate(() => new WebSocket('wss://x.test'));" \
  "const ctx = await page.context().browser().newContext();" \
  "await page.route('**', r => r.abort());" \
  "await page.routeFromHAR('x.har');" \
  "await page.request.post('https://x.test/api');" \
  "await page.request.fetch('https://x.test/api');" \
  "const rq = page.request;" \
  "await page['request']['post']('https://x.test');" \
  "const s = await page.context().storageState();" \
  "const k = await page.context().cookies();" \
  "const cdp = await page.context().newCDPSession(page);"
do
  check "token: $snippet" ask browser_run_code_unsafe \
    "$(run "$(write tok.js "$(harness "$DIR" "    $snippet")")")"
done
check "line-leading import" ask browser_run_code_unsafe \
  "$(run "$(write imp.js "import fs from 'fs';
$(harness "$DIR" "")")")"

# ---- run_code_unsafe: evidence-path, sinks, stop, secrets ----------------

check "wrong EVIDENCE_DIR" ask browser_run_code_unsafe \
  "$(run "$(write wrongdir.js "$(harness "$EV/another-folder" "")")")"
check "relative EVIDENCE_DIR" ask browser_run_code_unsafe \
  "$(run "$(write reldir.js "$(harness ".playwright-mcp/evidence/2026-10-19-demo-todo" "")")")"
check "EVIDENCE_DIR declared twice" ask browser_run_code_unsafe \
  "$(run "$(write twice.js "$(harness "$DIR" "    { const EVIDENCE_DIR = '/tmp'; }")")")"
check "EVIDENCE_DIR missing" ask browser_run_code_unsafe \
  "$(run "$(write nodir.js "async (page) => page.title()")")"
check "path not derived from EVIDENCE_DIR" ask browser_run_code_unsafe \
  "$(run "$(write badpath.js "$(harness "$DIR" "    await page.screenshot({ path: '/tmp/x.png' });")")")"
check "path shorthand" ask browser_run_code_unsafe \
  "$(run "$(write shorthand.js "$(harness "$DIR" "    const path = '/tmp/x.png'; await page.screenshot({ path });")")")"
check "'..' after EVIDENCE_DIR" ask browser_run_code_unsafe \
  "$(run "$(write dotdot.js "$(harness "$DIR" "    await page.screenshot({ path: \`\${EVIDENCE_DIR}/../../x.png\` });")")")"
check "saveAs(" ask browser_run_code_unsafe \
  "$(run "$(write saveas.js "$(harness "$DIR" "    const dl = await page.waitForEvent('download'); await dl.saveAs('x');")")")"
check "setInputFiles(" ask browser_run_code_unsafe \
  "$(run "$(write upload.js "$(harness "$DIR" "    await page.locator('input[type=file]').setInputFiles('/etc/hosts');")")")"
check "screencast.start without stop" ask browser_run_code_unsafe \
  "$(run "$(write nostop.js "async (page) => {
  const EVIDENCE_DIR = '$DIR';
  await page.screencast.start({ path: \`\${EVIDENCE_DIR}/run-1.webm\` });
  return 1;
}")")"
check "screencast.stop outside finally" ask browser_run_code_unsafe \
  "$(run "$(write nofinally.js "async (page) => {
  const EVIDENCE_DIR = '$DIR';
  await page.screencast.start({ path: \`\${EVIDENCE_DIR}/run-1.webm\` });
  await page.screencast.stop();
  return 1;
}")")"
check "password fill while recording" ask browser_run_code_unsafe \
  "$(run "$(write pw.js "$(harness "$DIR" "    await page.getByLabel('Password').fill('x');")")")"
check "password typed sequentially" ask browser_run_code_unsafe \
  "$(run "$(write pw2.js "$(harness "$DIR" "    await page.locator('#pwd').pressSequentially('x');")")")"

# ---- config sanity -------------------------------------------------------

echo '{ "evidenceRoot": ".playwright-mcp/evidence", "login": { "password": "x" } }' > "$ROOT/.claude/ui-evidence.json"
check "secret key in config" ask browser_run_code_unsafe "$(run "$clean")"
echo '{ not json' > "$ROOT/.claude/ui-evidence.json"
check "unreadable config" ask browser_run_code_unsafe "$(run "$clean")"
echo '{ "evidenceRoot": "../outside" }' > "$ROOT/.claude/ui-evidence.json"
check "evidenceRoot with '..'" ask browser_run_code_unsafe "$(run "$clean")"
echo '{ "evidenceRoot": "/abs/evidence" }' > "$ROOT/.claude/ui-evidence.json"
check "absolute evidenceRoot" ask browser_run_code_unsafe "$(run "$clean")"
echo '{ "evidenceRoot": "proof" }' > "$ROOT/.claude/ui-evidence.json"
check "script outside a custom evidenceRoot" ask browser_run_code_unsafe "$(run "$clean")"
mkdir -p "$ROOT/proof/2026-10-19-x/scripts"
cp "$(write c2.js "$(harness "$ROOT/proof/2026-10-19-x" "")")" "$ROOT/proof/2026-10-19-x/scripts/c2.js"
check "script inside a custom evidenceRoot" allow browser_run_code_unsafe "$(run "$ROOT/proof/2026-10-19-x/scripts/c2.js")"
echo '{}' > "$ROOT/.claude/ui-evidence.json"

# Explicit config path via UI_EVIDENCE_CONFIG; no config at all uses the default under the project dir.
mkdir -p "$TMP/cfg/.claude"
echo '{ "evidenceRoot": "proof" }' > "$TMP/cfg/.claude/ui-evidence.json"
got=$(UI_EVIDENCE_CONFIG="$TMP/cfg/.claude/ui-evidence.json" decision_of "$(payload mcp__playwright__browser_run_code_unsafe "$(run "$clean")")")
if [ "$got" = "ask" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL UI_EVIDENCE_CONFIG points elsewhere: got $got"; fi
rm "$ROOT/.claude/ui-evidence.json"
got=$(CLAUDE_PROJECT_DIR="$ROOT" decision_of "$(payload mcp__playwright__browser_run_code_unsafe "$(run "$clean")" "$TMP")")
if [ "$got" = "allow" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL no config, default root: got $got"; fi

# ---- browser_evaluate ----------------------------------------------------

check "evaluate, page only" allow browser_evaluate '{"function":"() => document.title"}'
check "evaluate with fetch" ask browser_evaluate '{"function":"() => fetch(\"/api\")"}'
check "evaluate with sendBeacon" ask browser_evaluate '{"function":"() => navigator.sendBeacon(\"/x\")"}'
check "evaluate saving to a file" ask browser_evaluate '{"function":"() => 1","filename":"out.json"}'

# ---- native video and other devtools tools -------------------------------

echo '{ "evidenceRoot": ".playwright-mcp/evidence" }' > "$ROOT/.claude/ui-evidence.json"
vid() { jq -cn --arg f "$1" '{filename: $f, size: {width: 1280, height: 720}}'; }
check "video into the evidence folder" allow browser_start_video "$(vid "$DIR/run-1.webm")"
check "video from a nested cwd" allow browser_start_video "$(vid "$DIR/run-1-part2.webm")" "$ROOT/nested/repo"
check "video, folder not created yet" allow browser_start_video "$(vid "$EV/2026-10-20-new/run-1.webm")"
check "video without filename (lands in the output folder)" ask browser_start_video '{}'
check "video, relative filename" ask browser_start_video \
  "$(vid ".playwright-mcp/evidence/2026-10-19-demo-todo/run-1.webm")"
check "video outside the evidence root" ask browser_start_video "$(vid "$ROOT/run-1.webm")"
check "video directly in the evidence root" ask browser_start_video "$(vid "$EV/run-1.webm")"
check "video in a subfolder of the evidence folder" ask browser_start_video "$(vid "$DIR/scripts/run-1.webm")"
check "video, '..' escape" ask browser_start_video "$(vid "$DIR/../../../run-1.webm")"
check "video, not .webm" ask browser_start_video "$(vid "$DIR/run-1.mp4")"
ln -s "$TMP/outside" "$EV/linked-folder"
check "video, symlinked folder escape" ask browser_start_video "$(vid "$EV/linked-folder/run-1.webm")"
echo '{ "login": { "token": "x" } }' > "$ROOT/.claude/ui-evidence.json"
check "video with a secret key in config" ask browser_start_video "$(vid "$DIR/run-1.webm")"
echo '{}' > "$ROOT/.claude/ui-evidence.json"
check "video stop" allow browser_stop_video '{}'
check "video chapter" allow browser_video_chapter '{"title":"C1 – add a todo","duration":1500}'
check "video show actions" allow browser_video_show_actions '{"duration":600}'
check "video hide actions" allow browser_video_hide_actions '{}'
check "tracing (headers and typed secrets in clear)" ask browser_start_tracing '{}'
check "annotate (waits for a person)" ask browser_annotate '{}'
check "resume" ask browser_resume '{}'
check "action recording" ask browser_start_recording '{}'

# ---- other tools ---------------------------------------------------------

check "other Playwright tool is not ours" silent browser_snapshot '{}'
check "stop tracing is not ours" silent browser_stop_tracing '{}'

echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
