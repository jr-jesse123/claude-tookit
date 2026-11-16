#!/usr/bin/env python3
"""Prints one TSV line per span of a Jaeger-format trace saved by a backend trace reader (for example a tracing MCP tool).

Columns: offset_ms from the first span, service, operation, duration_ms, error, span id, parent span id.
Usage: trace-summary.py <trace.json> [--grep REGEX]   (--grep keeps spans whose operation matches)
"""

import json
import re
import sys


def has_error(span):
    for tag in span.get("tags") or []:
        if tag["key"] == "error" and tag["value"] in (True, "true"):
            return True
        if tag["key"] == "otel.status_code" and tag["value"] == "ERROR":
            return True
    return False


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)

    pattern = re.compile(argv[argv.index("--grep") + 1]) if "--grep" in argv else None

    with open(argv[0], encoding="utf-8") as handle:
        document = json.load(handle)

    for trace in document["data"]:
        services = {pid: proc["serviceName"] for pid, proc in trace["processes"].items()}
        spans = sorted(trace["spans"], key=lambda span: span["startTime"])
        origin = spans[0]["startTime"]
        print(f"# trace {trace['traceID']} spans {len(spans)} errors {sum(has_error(s) for s in spans)}")

        for span in spans:
            operation = span["operationName"]
            if pattern and not pattern.search(operation):
                continue

            parents = [ref["spanID"] for ref in span.get("references") or [] if ref["refType"] == "CHILD_OF"]
            print(
                "\t".join(
                    [
                        f"{(span['startTime'] - origin) / 1000:.1f}",
                        services[span["processID"]],
                        operation[:140],
                        f"{span['duration'] / 1000:.1f}",
                        "error" if has_error(span) else "ok",
                        span["spanID"],
                        parents[0] if parents else "",
                    ]
                )
            )


main(sys.argv[1:])
