#!/usr/bin/env bash
# PreToolUse guard for the Playwright MCP's code-running and devtools tools.
#
# browser_run_code_unsafe runs arbitrary JavaScript in the MCP's Node process.
# This hook lets one narrow case through without a prompt: a script file kept
# in a ui-evidence folder (<root>/<evidenceRoot>/<folder>/scripts/*.js) that
# passes the lexical rules below. Every other call to the two tools asks.
# browser_evaluate runs in the page; it asks only when it touches the network
# or saves its result to a file.
#
# The native video tools (--caps devtools): browser_start_video is allowed
# only with an absolute filename <root>/<evidenceRoot>/<folder>/<name>.webm;
# stopping, chapters and action overlays are allowed. The other devtools tools
# ask: tracing writes request headers and typed secret values in clear text,
# annotate waits for a person in a dashboard it spawns, resume and recording
# have no place in an evidence run.
#
# A lexical filter, not a sandbox: a deliberate bypass is possible. See the
# plugin README for what it does not cover.
#
# Needs bash, jq, grep and GNU coreutils (realpath -m).

set -u

if ! command -v jq >/dev/null 2>&1; then
  echo "ui-evidence guard: jq is not installed, so the Playwright code cannot be checked" >&2
  exit 2
fi

emit() { # decision, reason
  jq -cn --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'
  exit 0
}

input=$(cat)
if ! printf '%s' "$input" | jq -e 'type == "object"' >/dev/null 2>&1; then
  emit ask "ui-evidence guard: hook input is not valid JSON"
fi

tool_name=$(printf '%s' "$input" | jq -r '.tool_name // ""')
tool=${tool_name##*__}
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')
[ -n "$cwd" ] || cwd=$PWD

NET='\bfetch\b|XMLHttpRequest|sendBeacon|WebSocket|\baxios\b|\.ajax\b'

case "$tool" in
  browser_evaluate)
    fn=$(printf '%s' "$input" | jq -r '.tool_input.function // ""')
    if printf '%s' "$fn" | grep -qE "$NET"; then
      emit ask "ui-evidence guard: browser_evaluate function uses the network"
    fi
    if [ -n "$(printf '%s' "$input" | jq -r '.tool_input.filename // ""')" ]; then
      emit ask "ui-evidence guard: browser_evaluate saves its result to a file"
    fi
    emit allow "ui-evidence guard: page-only evaluate"
    ;;
  browser_stop_video|browser_video_chapter|browser_video_show_actions|browser_video_hide_actions)
    emit allow "ui-evidence guard: video control"
    ;;
  browser_start_tracing)
    emit ask "ui-evidence guard: tracing writes request headers (bearer tokens) and typed values, secrets included, in clear text to the MCP's output folder"
    ;;
  browser_annotate)
    emit ask "ui-evidence guard: browser_annotate opens the Playwright dashboard and waits for a person to draw"
    ;;
  browser_resume|browser_start_recording)
    emit ask "ui-evidence guard: $tool is not part of an evidence run"
    ;;
  browser_run_code_unsafe|browser_start_video) ;;
  *) exit 0 ;;
esac

# ---- config: where scripts may live -------------------------------------

DEFAULT_EVIDENCE_ROOT=".playwright-mcp/evidence"
config=""
if [ -n "${UI_EVIDENCE_CONFIG:-}" ]; then
  config=$UI_EVIDENCE_CONFIG
else
  dir=$cwd
  while :; do
    if [ -f "$dir/.claude/ui-evidence.json" ]; then
      config="$dir/.claude/ui-evidence.json"
      break
    fi
    [ "$dir" = "/" ] || [ -z "$dir" ] && break
    dir=$(dirname "$dir")
  done
fi

config_problem=""
if [ -n "$config" ]; then
  config_dir=$(dirname "$config")
  if [ "$(basename "$config_dir")" = ".claude" ]; then
    root=$(dirname "$config_dir")
  else
    root=$config_dir
  fi
  if ! jq -e 'type == "object"' "$config" >/dev/null 2>&1; then
    config_problem="config $config is missing, unreadable or not a JSON object"
  elif [ "$(jq '[.. | objects | keys[] | select(test("pass|secret|token|cookie|credential"; "i"))] | length' "$config")" != "0" ]; then
    config_problem="config $config has a secret-looking key; it must hold pointers, never credentials"
  else
    evidence_root=$(jq -r --arg d "$DEFAULT_EVIDENCE_ROOT" \
      'if .evidenceRoot == null then $d elif (.evidenceRoot | type) == "string" then .evidenceRoot else "" end' "$config")
  fi
else
  root=${CLAUDE_PROJECT_DIR:-$cwd}
  evidence_root=$DEFAULT_EVIDENCE_ROOT
fi

if [ -z "$config_problem" ]; then
  case "/$evidence_root/" in
    *"/../"*|"//"*) config_problem="evidenceRoot \"$evidence_root\" must be a relative path without '..'" ;;
  esac
  [ -n "$evidence_root" ] || config_problem="evidenceRoot must be a non-empty string"
fi

# ---- the call itself -----------------------------------------------------

code=$(printf '%s' "$input" | jq -r '.tool_input.code // ""')
filename=$(printf '%s' "$input" | jq -r '.tool_input.filename // ""')

[ -z "$code" ] || emit ask "ui-evidence guard: inline code; write the script under the evidence folder and pass it as filename"
[ -n "$filename" ] || emit ask "ui-evidence guard: no filename given"
case "$filename" in
  /*) ;;
  *) emit ask "ui-evidence guard: relative filename '$filename'; the MCP resolves it against its own workspace, so pass an absolute path" ;;
esac
[ -z "$config_problem" ] || emit ask "ui-evidence guard: $config_problem; every script and video asks"

evidence_base=$(realpath -m -- "$root/$evidence_root")

if [ "$tool" = "browser_start_video" ]; then
  video=$(realpath -m -- "$filename")
  case "$video" in
    "$evidence_base"/*) rest=${video#"$evidence_base"/} ;;
    *) emit ask "ui-evidence guard: video $video is outside $evidence_base" ;;
  esac
  printf '%s' "$rest" | grep -qE '^[^/]+/[^/]+\.webm$' \
    || emit ask "ui-evidence guard: video $video is not <evidence folder>/<name>.webm under $evidence_base"
  emit allow "ui-evidence guard: video into evidence folder $(dirname "$video")"
fi

script=$(realpath -m -- "$filename")
[ -f "$script" ] || emit ask "ui-evidence guard: script $filename does not exist"
[ -r "$script" ] || emit ask "ui-evidence guard: script $filename is not readable"

case "$script" in
  "$evidence_base"/*) rest=${script#"$evidence_base"/} ;;
  *) emit ask "ui-evidence guard: $script is outside $evidence_base" ;;
esac
printf '%s' "$rest" | grep -qE '^[^/]+/scripts/[^/]+\.js$' \
  || emit ask "ui-evidence guard: $script is not <evidence folder>/scripts/<name>.js under $evidence_base"
evidence_dir=$(dirname "$(dirname "$script")")

# ---- lexical rules over the script ---------------------------------------

reasons=()
has() { grep -qE -- "$1" "$script"; }

ESCAPE='require[[:space:]]*\(|import[[:space:]]*\(|^[[:space:]]*import[[:space:]]|child_process|\bprocess\b|eval[[:space:]]*\(|Function[[:space:]]*\(|\bglobalThis\b|\bmodule\b|__dirname|__filename|\bBuffer\b|\bconstructor\b|__proto__|\bReflect\b'
HTTP='newContext|\.route[[:space:]]*\(|routeFromHAR|routeWebSocket|\.request[[:space:]]*\[|\bmethod[[:space:]]*:|\bbrowserType\b|newCDPSession|connectOverCDP|\bstorageState\b|\bcookies\b|\baddCookies\b'

has "$ESCAPE" && reasons+=("escape token: $(grep -oE -- "$ESCAPE" "$script" | head -1)")
has "$NET" && reasons+=("network token: $(grep -oE -- "$NET" "$script" | head -1)")
has "$HTTP" && reasons+=("direct HTTP or browser-state token: $(grep -oE -- "$HTTP" "$script" | head -1)")

# .request is allowed only as .request.get(, .request.head( or .request().
bad_request=$(grep -oE '\.request\b[[:space:]]*(\.[[:space:]]*[A-Za-z_$]+|\()?' "$script" \
  | tr -d ' \t\r' | grep -vxE '\.request(\.get|\.head|\()' | head -1)
[ -z "$bad_request" ] || reasons+=("request use other than .request.get/.head/(): $bad_request")

# obj['name'] would hide any of the tokens above from this filter.
has "[]A-Za-z0-9_$)][[:space:]]*\\[[[:space:]]*['\"\`]" && reasons+=("member access by string (obj['name'])")

has 'saveAs[[:space:]]*\(' && reasons+=("saveAs( writes a download to disk")
has 'setInputFiles[[:space:]]*\(' && reasons+=("setInputFiles( reads local files into the page")

# Two-dot segments ('..'), but not the spread operator ('...').
has '(^|[^.])\.\.([^.]|$)' && reasons+=("'..' in the script")

# EVIDENCE_DIR: declared once as a string literal equal to the script's evidence folder.
decl_re="^[[:space:]]*const[[:space:]]+EVIDENCE_DIR[[:space:]]*=[[:space:]]*['\"][^'\"\`\$]*['\"][[:space:]]*;?[[:space:]]*\$"
decls=$(grep -cE -- "$decl_re" "$script")
binds=$(grep -oE '\b(const|let|var)[[:space:]]+EVIDENCE_DIR\b' "$script" | wc -l)
assigns=$(grep -oE '\bEVIDENCE_DIR[[:space:]]*=([^=]|$)' "$script" | wc -l)
if [ "$decls" != "1" ] || [ "$binds" -ne 1 ] || [ "$assigns" -ne 1 ]; then
  reasons+=("EVIDENCE_DIR must be declared exactly once as const EVIDENCE_DIR = '<absolute path>'")
else
  value=$(grep -E -- "$decl_re" "$script" | sed -E "s/^[^'\"]*['\"]([^'\"]*)['\"].*/\1/")
  case "$value" in
    /*) [ "$(realpath -m -- "$value")" = "$evidence_dir" ] \
          || reasons+=("EVIDENCE_DIR '$value' is not this script's evidence folder $evidence_dir") ;;
    *) reasons+=("EVIDENCE_DIR '$value' is not absolute") ;;
  esac
fi

# Every path option derives from EVIDENCE_DIR: `${EVIDENCE_DIR}/... or EVIDENCE_DIR + '/...
paths_all=$(grep -oE '\bpath\b' "$script" | wc -l)
paths_ok=$(grep -oE "\bpath[[:space:]]*:[[:space:]]*(\`\\\$\{EVIDENCE_DIR\}/|EVIDENCE_DIR[[:space:]]*\+[[:space:]]*['\"\`]/)" "$script" | wc -l)
[ "$paths_all" -eq "$paths_ok" ] || reasons+=("a path is not derived from EVIDENCE_DIR (every 'path' must be path: \`\${EVIDENCE_DIR}/...\`)")

if has 'screencast\.start\b'; then
  { has 'screencast\.stop\b' && has '\bfinally\b'; } \
    || reasons+=("screencast.start without screencast.stop in a finally block")
fi

# Secrets are typed through browser_type, never from a script (action titles show typed text on video).
secret_fill=$(grep -iE 'passw|pwd|secret' "$script" | grep -E '\.(fill|type|pressSequentially|insertText)[[:space:]]*\(' | head -1)
[ -z "$secret_fill" ] || reasons+=("types into a password-like field from a script")

if [ "${#reasons[@]}" -gt 0 ]; then
  msg=$(printf '%s; ' "${reasons[@]}")
  emit ask "ui-evidence guard: ${msg%; }"
fi

emit allow "ui-evidence guard: evidence script $script passed the checks"
