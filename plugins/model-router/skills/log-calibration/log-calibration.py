#!/usr/bin/env python3
"""Append one validated calibration entry to the project's model-calibration log.

This is the only write path the model-router plugin ships. It is deliberately
narrow so it can be allowlisted on its own instead of granting a blanket Write
permission:

- append-only: opens the log with mode "a"; it can never edit or truncate
- fixed path: always `<project>/.claude/model-calibration.jsonl` — there is no
  flag to point it anywhere else
- validated: every field is checked against the schema in model-policy.md
  before anything touches disk; a bad field means exit 1 and no write

The project root is `CLAUDE_PROJECT_DIR` when set, else the current directory.
"""

import argparse
import datetime
import json
import os
import re
import sys

# Anthropic aliases are a closed set; OpenAI's lineup churns too fast to
# hardcode, so its models are validated by shape only.
PROVIDERS = {
    "anthropic": {
        "models": ["haiku", "sonnet", "opus", "fable", "claude-opus-4-8"],
        "efforts": ["low", "medium", "high", "xhigh", "max"],
    },
    "openai": {
        "models": None,  # any slug matching MODEL_RE
        "efforts": ["none", "minimal", "low", "medium", "high", "xhigh", "max"],
    },
}
TESTS = ["pass", "fail", "none"]
CATEGORY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MODEL_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")

LOG_RELPATH = os.path.join(".claude", "model-calibration.jsonl")


def bool_flag(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise argparse.ArgumentTypeError(f"expected 'true' or 'false', got {value!r}")


def non_negative_int(value: str) -> int:
    n = int(value)
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append one calibration entry to .claude/model-calibration.jsonl"
    )
    parser.add_argument("--provider", default="anthropic", choices=sorted(PROVIDERS), help="provider of the model the task ran on (default: anthropic)")
    parser.add_argument("--category", required=True, help="task-category slug; reuse existing slugs from the log")
    parser.add_argument("--model", required=True, help="model the task actually started with")
    parser.add_argument("--effort", help="effort/reasoning level actually used; omit for models that take none")
    parser.add_argument("--escalated", required=True, type=bool_flag, metavar="{true,false}", help="a stronger model or effort was needed mid-task")
    parser.add_argument("--corrections", required=True, type=non_negative_int, help="number of user corrections during the task")
    parser.add_argument("--minutes", type=non_negative_int, help="wall-clock duration; omit if unknown")
    parser.add_argument("--tests", required=True, choices=TESTS)
    parser.add_argument("--rework", required=True, type=bool_flag, metavar="{true,false}", help="the result needed architectural rework afterward")
    parser.add_argument("--note", required=True, help="free text; include the advisor's score and whether it matched")
    parser.add_argument("--date", help="ISO date the task ran (default: today)")
    args = parser.parse_args()

    spec = PROVIDERS[args.provider]
    if not CATEGORY_RE.match(args.category):
        print(f"error: category {args.category!r} is not a lowercase slug ([a-z0-9-])", file=sys.stderr)
        return 1
    if spec["models"] is not None and args.model not in spec["models"]:
        print(f"error: model {args.model!r} is not a known {args.provider} alias {spec['models']}", file=sys.stderr)
        return 1
    if spec["models"] is None and not MODEL_RE.match(args.model):
        print(f"error: model {args.model!r} is not a lowercase model slug ([a-z0-9.-])", file=sys.stderr)
        return 1
    if args.effort is not None and args.effort not in spec["efforts"]:
        print(f"error: effort {args.effort!r} is not a {args.provider} level {spec['efforts']}", file=sys.stderr)
        return 1
    if args.provider == "anthropic":
        if args.model == "haiku" and args.effort is not None:
            print("error: haiku does not accept --effort; omit it", file=sys.stderr)
            return 1
        if args.model != "haiku" and args.effort is None:
            print(f"error: --effort is required for anthropic model {args.model!r}", file=sys.stderr)
            return 1
    if args.date is not None:
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            print(f"error: --date {args.date!r} is not an ISO date (YYYY-MM-DD)", file=sys.stderr)
            return 1

    entry = {
        "date": args.date or datetime.date.today().isoformat(),
        "provider": args.provider,
        "category": args.category,
        "model": args.model,
        "effort": args.effort,
        "escalated": args.escalated,
        "corrections": args.corrections,
        "minutes": args.minutes,
        "tests": args.tests,
        "rework": args.rework,
        "note": args.note,
    }

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    log_path = os.path.join(root, LOG_RELPATH)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    line = json.dumps(entry, ensure_ascii=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(f"appended to {log_path}:")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
