#!/usr/bin/env python3
"""Append one validated entry to the project's intent-lexicon log.

This is the only write path the intent-compiler plugin ships. It is
deliberately narrow so it can be allowlisted on its own instead of granting a
blanket Write permission:

- append-only: opens the log with mode "a"; it can never edit or truncate
- fixed path: always `<project>/.claude/intent-lexicon.jsonl` — there is no
  flag to point it anywhere else
- validated: every field is checked against the schema in reference/lexicon.md
  before anything touches disk; a bad field means exit 1 and no write

The project root is `CLAUDE_PROJECT_DIR` when set, else the current directory.
"""

import argparse
import datetime
import json
import os
import re
import sys

KINDS = ["usage", "pact"]
MODES = ["pure", "trimmed", "pact", "expanded"]
TERM_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Fields that only make sense for one kind. Passing one to the other kind is a
# mistake worth failing on: a silently ignored flag looks like a recorded one.
USAGE_ONLY = ["mode", "adhered", "leak", "misread", "corrections", "tokens_in", "tokens_out"]
PACT_ONLY = ["definition"]

LOG_RELPATH = os.path.join(".claude", "intent-lexicon.jsonl")


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
        description="Append one entry to .claude/intent-lexicon.jsonl"
    )
    parser.add_argument("--kind", default="usage", choices=KINDS, help="usage: how an anchor behaved; pact: a local term's agreed definition (default: usage)")
    parser.add_argument("--term", required=True, help="lowercase slug of the term; reuse existing slugs from the lexicon")
    parser.add_argument("--mode", choices=MODES, help="[usage] what compile emitted for this term")
    parser.add_argument("--adhered", type=bool_flag, metavar="{true,false}", help="[usage] the output matched the intent the compression stood for")
    parser.add_argument("--leak", type=non_negative_int, help="[usage] frame elements produced that the intent never asked for")
    parser.add_argument("--misread", type=bool_flag, metavar="{true,false}", help="[usage] the model expanded to the wrong frame entirely")
    parser.add_argument("--corrections", type=non_negative_int, help="[usage] user turns spent correcting the result")
    parser.add_argument("--tokens-in", type=non_negative_int, help="[usage] input tokens consumed (e.g. from /cost); omit if unknown")
    parser.add_argument("--tokens-out", type=non_negative_int, help="[usage] output tokens generated, thinking included; omit if unknown")
    parser.add_argument("--definition", help="[pact] one line fixing the local term's intension")
    parser.add_argument("--note", help="free text; for usage, record the compressibility score and whether it matched")
    parser.add_argument("--date", help="ISO date the prompt ran (default: today)")
    args = parser.parse_args()

    if not TERM_RE.match(args.term):
        print(f"error: term {args.term!r} is not a lowercase slug ([a-z0-9-])", file=sys.stderr)
        return 1

    wrong = PACT_ONLY if args.kind == "usage" else USAGE_ONLY
    for field in wrong:
        if getattr(args, field) is not None:
            flag = "--" + field.replace("_", "-")
            print(f"error: {flag} does not apply to --kind {args.kind}", file=sys.stderr)
            return 1

    if args.kind == "usage":
        missing = [f for f in ("mode", "adhered", "leak", "misread", "corrections", "note")
                   if getattr(args, f) is None]
        if missing:
            flags = ", ".join("--" + f for f in missing)
            print(f"error: --kind usage requires {flags}", file=sys.stderr)
            return 1
    else:
        if args.definition is None:
            print("error: --kind pact requires --definition", file=sys.stderr)
            return 1
        if not args.definition.strip():
            print("error: --definition is empty; a pact with no intension records nothing", file=sys.stderr)
            return 1

    if args.date is not None:
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            print(f"error: --date {args.date!r} is not an ISO date (YYYY-MM-DD)", file=sys.stderr)
            return 1

    date = args.date or datetime.date.today().isoformat()
    if args.kind == "usage":
        entry = {
            "kind": "usage",
            "date": date,
            "term": args.term,
            "mode": args.mode,
            "adhered": args.adhered,
            "leak": args.leak,
            "misread": args.misread,
            "corrections": args.corrections,
            "tokens_in": args.tokens_in,
            "tokens_out": args.tokens_out,
            "note": args.note,
        }
    else:
        entry = {
            "kind": "pact",
            "date": date,
            "term": args.term,
            "definition": args.definition,
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
