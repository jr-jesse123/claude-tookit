#!/usr/bin/env python3
"""PreToolUse guard: escalate destructive infrastructure commands to the user.

Reads the hook payload on stdin and, when the Bash command matches a
destructive pattern, prints a `permissionDecision: "ask"` so Claude Code shows a
confirmation dialog instead of running it under an auto-approve mode.

This never denies outright — the user stays in control and can approve. Anything
that does not match exits 0 with no output, which lets the normal permission
flow apply.
"""

import json
import re
import sys

# (compiled pattern, reason shown in the permission dialog)
RULES = [
    (r"\bterraform\s+destroy\b", "terraform destroy tears down managed infrastructure"),
    (r"\bterraform\s+apply\b.*--?auto-approve\b", "terraform apply with -auto-approve skips the plan review"),
    (r"\bkubectl\s+delete\b", "kubectl delete removes live cluster resources"),
    (r"\bkubectl\s+.*\s--all-namespaces\b.*\bdelete\b", "kubectl delete across all namespaces"),
    (r"\bhelm\s+(uninstall|delete)\b", "helm uninstall removes a deployed release"),
    (r"\baws\s+\S+\s+delete-", "aws CLI delete-* removes a cloud resource"),
    (r"\baws\s+s3\s+rm\b.*--recursive\b", "recursive S3 delete"),
    (r"\bgcloud\s+.*\bdelete\b", "gcloud delete removes a cloud resource"),
    (r"\baz\s+.*\bdelete\b", "az delete removes a cloud resource"),
    (r"\bdocker\s+system\s+prune\b.*(-a\b|--all\b)", "docker system prune -a removes all unused images and volumes"),
    (r"\bdocker\s+volume\s+rm\b", "docker volume rm destroys persisted data"),
    (r"\bdrop\s+(table|database|schema)\b", "SQL DROP destroys data"),
    (r"\btruncate\s+table\b", "SQL TRUNCATE empties a table"),
    (r"\bgit\s+push\b.*(--force\b(?!-with-lease)|(?<!\w)-f\b)", "force push can overwrite remote history"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards uncommitted work"),
    (r"\bgit\s+clean\b.*-\w*[fx]", "git clean deletes untracked files"),
    (r"\brm\s+(-\w*\s+)*-\w*[rR]\w*f|\brm\s+(-\w*\s+)*-\w*f\w*[rR]", "recursive force delete"),
]

COMPILED = [(re.compile(pattern, re.IGNORECASE), reason) for pattern, reason in RULES]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # not our business; let the normal flow apply

    if payload.get("tool_name") != "Bash":
        return 0

    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    for pattern, reason in COMPILED:
        if pattern.search(command):
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": f"devops-tools guard: {reason}. Confirm before running.",
                    }
                },
                sys.stdout,
            )
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
