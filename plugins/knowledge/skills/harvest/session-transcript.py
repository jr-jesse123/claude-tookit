#!/usr/bin/env python3
"""Print a readable transcript of an earlier Claude Code session.

Usage:
  session-transcript.py <session-id | id-prefix | path/to/session.jsonl> [--max-result N]

The session id is the UUID of a file under ~/.claude/projects/<project>/
(or $CLAUDE_CONFIG_DIR/projects/). A unique prefix is enough. Prints the
title, dates and working directory, then each user message, assistant answer
and tool call with its target, and the first N characters of each tool result
(default 400). Thinking blocks, attachments and sub-agent sidechains are left
out. Exits 1 with "session not found" when no file matches.
"""

import argparse
import json
import os
import sys
from pathlib import Path

TARGET_KEYS = (
    "file_path", "path", "notebook_path", "command", "pattern", "url", "query",
    "skill", "subagent_type", "description", "prompt",
)


def projects_dir():
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(Path.home(), ".claude")
    return Path(base) / "projects"


def find_session(arg):
    p = Path(arg).expanduser()
    if p.suffix == ".jsonl" and p.is_file():
        return p
    sid = arg.removeprefix("sess_").removeprefix("session_")
    root = projects_dir()
    if not root.is_dir():
        return None
    matches = sorted(root.glob(f"*/{sid}*.jsonl"))
    if len(matches) > 1:
        names = ", ".join(m.stem for m in matches[:5])
        sys.exit(f"ambiguous session id {arg!r}: {names}")
    return matches[0] if matches else None


def clip(text, limit):
    text = text.strip()
    if limit and len(text) > limit:
        return text[:limit] + f" … [{len(text) - limit} more chars]"
    return text


def result_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, dict):
                parts.append(f"[{block.get('type', 'block')}]")
        return "\n".join(parts)
    return str(content)


def tool_target(inp):
    if not isinstance(inp, dict):
        return ""
    for key in TARGET_KEYS:
        if inp.get(key):
            return f"{key}={clip(str(inp[key]).replace(chr(10), ' '), 200)}"
    return clip(json.dumps(inp, ensure_ascii=False), 200)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--max-result", type=int, default=400, help="characters kept per tool result (0 = all)")
    args = ap.parse_args()

    path = find_session(args.session)
    if not path:
        print("session not found", file=sys.stderr)
        sys.exit(1)

    title = None
    cwd = None
    first = last = None
    body = []

    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get("type")
            if kind == "summary" and rec.get("summary"):
                title = title or rec["summary"]
            if kind in ("custom-title", "ai-title") and (rec.get("customTitle") or rec.get("title")):
                title = rec.get("customTitle") or rec.get("title")
            if kind not in ("user", "assistant") or rec.get("isSidechain"):
                continue
            ts = rec.get("timestamp")
            if ts:
                first = first or ts
                last = ts
            cwd = cwd or rec.get("cwd")
            content = (rec.get("message") or {}).get("content")
            if isinstance(content, str):
                if content.strip():
                    who = "USER" if kind == "user" else "ASSISTANT"
                    if rec.get("isMeta"):
                        who += " (meta)"
                    body.append(f"\n## {who}\n{content.strip()}")
                continue
            for block in content or []:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text" and block.get("text", "").strip():
                    who = "USER" if kind == "user" else "ASSISTANT"
                    body.append(f"\n## {who}\n{block['text'].strip()}")
                elif btype == "tool_use":
                    body.append(f"- tool {block.get('name')}: {tool_target(block.get('input'))}")
                elif btype == "tool_result":
                    flag = " (error)" if block.get("is_error") else ""
                    text = clip(result_text(block.get("content")), args.max_result)
                    indented = "\n".join("    " + l for l in text.splitlines()) or "    (empty)"
                    body.append(f"  result{flag}:\n{indented}")

    print(f"# Session {path.stem}")
    print(f"Title: {title or '(none)'}")
    print(f"Dates: {first or '?'} → {last or '?'}")
    print(f"Working directory: {cwd or '?'}")
    print(f"Source: {path}")
    print("\n".join(body))


if __name__ == "__main__":
    main()
