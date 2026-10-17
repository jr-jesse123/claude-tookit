#!/usr/bin/env python3
"""Convert verified source line boundaries into a Stryker.NET mutate selector.

This does not discover methods. Choose full declaration bounds by inspecting
C# syntax (Roslyn if needed) before invoking.
"""
import argparse
from pathlib import Path
import sys


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def selector(root: Path, source: Path, start_line: int, end_line: int) -> str:
    root = root.resolve(strict=True)
    source = source.resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != ".cs":
        raise ValueError("source must be an existing .cs file")
    try:
        relative = source.relative_to(root)
    except ValueError as exc:
        raise ValueError("source must be inside the production project root") from exc
    with source.open("r", encoding="utf-8-sig", newline="") as file:
        lines = file.read().splitlines(keepends=True)
    if not 1 <= start_line <= end_line <= len(lines):
        raise ValueError(f"invalid line range {start_line}..{end_line} (1..{len(lines)})")
    start = utf16_length("".join(lines[:start_line - 1]))
    end = utf16_length("".join(lines[:end_line]))
    if end <= start:
        raise ValueError("empty span")
    return f"{relative.as_posix()}{{{start}..{end}}}"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", required=True, type=Path)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--start-line", required=True, type=int)
    p.add_argument("--end-line", required=True, type=int)
    args = p.parse_args()
    try:
        print(selector(args.project_root, args.file, args.start_line, args.end_line))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"line-span: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
