#!/usr/bin/env python3
"""Emit candidate comment lines for the curate skill.

Two modes:
  stdin — parse a unified diff (git diff output); emit added (+) and
          context ( ) lines that look like comments, with new-file line
          numbers.
  args  — scan the named files line by line.

Output, one candidate per line:  path:lineno<TAB>flag<TAB>text
  flag: '+' added in the diff, '=' unchanged context, '.' file scan.

Candidates only: tuned for near-zero false negatives, so false positives
are expected — every flagged line must still be confirmed by reading it in
context. Middle lines of block comments and docstrings carry no marker of
their own; find them by reading around the flagged delimiters.
"""
import re
import sys

# Markers that can appear anywhere in the line.
ANYWHERE = ("//", "#", "/*", "*/", "<!--", "-->", '"""', "'''")
# Markers only meaningful at the start of the stripped line
# (block-comment continuation, SQL/Lua/Haskell, asm/Lisp, TeX/Erlang, VB).
AT_START = ("*", "--", ";", "%", "'")
REM = re.compile(r"(?i)^\s*rem(\s|$)")

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def is_candidate(text):
    if any(m in text for m in ANYWHERE):
        return True
    stripped = text.lstrip()
    if any(stripped.startswith(m) for m in AT_START):
        return True
    return bool(REM.match(text))


def emit(out, path, lineno, flag, text):
    out.write(f"{path}:{lineno}\t{flag}\t{text.strip()}\n")


def scan_diff(stream, out):
    path = None
    lineno = None
    count = 0
    for raw in stream:
        line = raw.rstrip("\n")
        if line.startswith("+++ "):
            target = line[4:].split("\t")[0]
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            lineno = None
            continue
        if line.startswith("@@"):
            m = HUNK.match(line)
            if m and path is not None:
                lineno = int(m.group(1))
            continue
        if path is None or lineno is None:
            continue
        if line.startswith("+"):
            flag, text = "+", line[1:]
        elif line.startswith(" ") or line == "":
            flag, text = "=", line[1:]
        elif line.startswith("-") or line.startswith("\\"):
            continue  # deleted line / "\ No newline" — not in the new file
        else:
            lineno = None  # next file's "diff --git" header
            continue
        if is_candidate(text):
            emit(out, path, lineno, flag, text)
            count += 1
        lineno += 1
    return count


def scan_file(path, out):
    count = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, raw in enumerate(f, 1):
                text = raw.rstrip("\n")
                if is_candidate(text):
                    emit(out, path, i, ".", text)
                    count += 1
    except OSError as e:
        print(f"error: {path}: {e}", file=sys.stderr)
    return count


def main():
    paths = sys.argv[1:]
    if paths:
        total = sum(scan_file(p, sys.stdout) for p in paths)
    else:
        total = scan_diff(sys.stdin, sys.stdout)
    print(f"{total} candidate line(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
