#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Token usage of one Claude Code session and of its subagents, split by role.

Reads ~/.claude/projects/<project>/<session>.jsonl and <session>/subagents/*.jsonl. Each assistant
message is counted once (the last record of a message id wins). Prints, per role, the number of
calls, output tokens, cache written, cache read, and the context size per call (input + cache
read + cache written: min, median, max). The thinking text is not stored in the transcript, so
output tokens that do not show up as text or tool input are mostly thinking.

Usage: session-usage.py <session id or path> [--project DIR] [--until ISO] [--since ISO]
"""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

DEFAULT_PROJECT = Path.home() / ".claude/projects" / str(Path.cwd()).replace("/", "-")


def read_calls(path: Path, since: str, until: str):
    calls = {}
    for line in path.open(errors="ignore"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = record.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant" or not message.get("usage"):
            continue
        stamp = record.get("timestamp", "")
        if (since and stamp < since) or (until and stamp >= until):
            continue
        calls[message.get("id") or record.get("uuid")] = (stamp, message["usage"], message.get("model"))
    return list(calls.values())


def summarise(calls):
    contexts = [u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0) for _, u, _ in calls]
    return {
        "calls": len(calls),
        "output": sum(u.get("output_tokens", 0) for _, u, _ in calls),
        "cache_write": sum(u.get("cache_creation_input_tokens", 0) for _, u, _ in calls),
        "cache_read": sum(u.get("cache_read_input_tokens", 0) for _, u, _ in calls),
        "ctx_min": min(contexts, default=0),
        "ctx_median": int(statistics.median(contexts)) if contexts else 0,
        "ctx_max": max(contexts, default=0),
    }


def role_of(meta_path: Path) -> str:
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    kind = meta.get("agentType", "unknown")
    return f"{kind} / {meta.get('model') or 'default'}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", help="session id (uuid) or path to the .jsonl")
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--since", default="", help="ISO time; only calls at or after it")
    parser.add_argument("--until", default="", help="ISO time; only calls before it")
    args = parser.parse_args()

    main_path = Path(args.session) if args.session.endswith(".jsonl") else args.project / f"{args.session}.jsonl"
    folder = main_path.with_suffix("") / "subagents"

    roles = defaultdict(list)
    roles["controller (main session)"] = read_calls(main_path, args.since, args.until)
    agents = defaultdict(int)
    for transcript in sorted(folder.glob("agent-*.jsonl")):
        role = role_of(transcript.with_suffix(".meta.json"))
        roles[role] += read_calls(transcript, args.since, args.until)
        agents[role] += 1

    header = f"{'role':42} {'agents':>6} {'calls':>6} {'output':>9} {'cache_write':>12} {'cache_read':>12} {'ctx min/median/max':>22}"
    print(header)
    total = defaultdict(int)
    for role, calls in sorted(roles.items(), key=lambda item: -sum(u.get('cache_read_input_tokens', 0) for _, u, _ in item[1])):
        if not calls:
            continue
        s = summarise(calls)
        print(f"{role:42} {agents.get(role, 1):>6} {s['calls']:>6} {s['output']:>9,} {s['cache_write']:>12,} {s['cache_read']:>12,} {s['ctx_min']:>8,}/{s['ctx_median']:,}/{s['ctx_max']:,}")
        for key in ("calls", "output", "cache_write", "cache_read"):
            total[key] += s[key]
    print(f"{'TOTAL':42} {sum(agents.values()) + 1:>6} {total['calls']:>6} {total['output']:>9,} {total['cache_write']:>12,} {total['cache_read']:>12,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
