#!/usr/bin/env python3
"""Plan or apply the standard GitHub repository governance policy."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

API_VERSION = "2026-03-10"


class CommandError(RuntimeError):
    """Raised when a gh command fails."""


def run(command: list[str], *, stdin: str | None = None) -> str:
    process = subprocess.run(
        command,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip()
        raise CommandError(f"{' '.join(command)} failed: {detail}")
    return process.stdout


def gh_api(method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    command = [
        "gh",
        "api",
        "--method",
        method,
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version: {API_VERSION}",
        endpoint,
    ]
    stdin = None
    if payload is not None:
        command.extend(["--input", "-"])
        stdin = json.dumps(payload)
    output = run(command, stdin=stdin)
    return json.loads(output) if output.strip() else None


def resolve_repository(explicit: str | None) -> str:
    if explicit:
        if explicit.count("/") != 1 or any(not part for part in explicit.split("/")):
            raise ValueError("--repo must use owner/name")
        return explicit

    output = run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
    ).strip()
    if not output:
        raise ValueError("could not resolve the current GitHub repository")
    return output


def load_standard() -> dict[str, Any]:
    path = Path(__file__).with_name("standard.json")
    with path.open(encoding="utf-8") as handle:
        standard = json.load(handle)

    if standard.get("version") != 1:
        raise ValueError("unsupported standard.json version")
    if not standard.get("ruleset", {}).get("name"):
        raise ValueError("standard.json must define ruleset.name")
    return standard


def prepare_ruleset(
    raw: dict[str, Any],
    *,
    human_approvals: int | None,
    required_checks: list[str],
    review_drafts: bool | None,
) -> dict[str, Any]:
    ruleset = json.loads(json.dumps(raw))

    for rule in ruleset["rules"]:
        if rule["type"] == "pull_request" and human_approvals is not None:
            rule["parameters"]["required_approving_review_count"] = human_approvals
        if rule["type"] == "copilot_code_review" and review_drafts is not None:
            rule["parameters"]["review_draft_pull_requests"] = review_drafts

    if required_checks:
        ruleset["rules"] = [
            rule for rule in ruleset["rules"] if rule["type"] != "required_status_checks"
        ]
        ruleset["rules"].append(
            {
                "type": "required_status_checks",
                "parameters": {
                    "do_not_enforce_on_create": True,
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {"context": context} for context in sorted(set(required_checks))
                    ],
                },
            }
        )

    return ruleset


def repository_settings_snapshot(
    repository: dict[str, Any], desired: dict[str, Any]
) -> dict[str, Any]:
    return {key: repository.get(key) for key in desired}


def normalize_ruleset(ruleset: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": ruleset.get("name"),
        "target": ruleset.get("target"),
        "enforcement": ruleset.get("enforcement"),
        "bypass_actors": ruleset.get("bypass_actors", []),
        "conditions": ruleset.get("conditions"),
        "rules": ruleset.get("rules", []),
    }


def find_ruleset(repository: str, name: str) -> tuple[int | None, dict[str, Any] | None]:
    summaries = gh_api("GET", f"/repos/{repository}/rulesets?includes_parents=false")
    matches = [
        item
        for item in summaries
        if item.get("name") == name and item.get("source_type") == "Repository"
    ]

    if len(matches) > 1:
        raise ValueError(f"multiple repository rulesets are named {name!r}")
    if not matches:
        return None, None

    ruleset_id = int(matches[0]["id"])
    ruleset = gh_api(
        "GET", f"/repos/{repository}/rulesets/{ruleset_id}?includes_parents=false"
    )
    return ruleset_id, normalize_ruleset(ruleset)


def build_plan(
    repository: str,
    standard: dict[str, Any],
    *,
    human_approvals: int | None,
    required_checks: list[str],
    review_drafts: bool | None,
) -> dict[str, Any]:
    current_repository = gh_api("GET", f"/repos/{repository}")
    desired_settings = standard["repository_settings"]
    current_settings = repository_settings_snapshot(current_repository, desired_settings)

    desired_ruleset = prepare_ruleset(
        standard["ruleset"],
        human_approvals=human_approvals,
        required_checks=required_checks,
        review_drafts=review_drafts,
    )
    ruleset_id, current_ruleset = find_ruleset(repository, desired_ruleset["name"])

    settings_changed = current_settings != desired_settings
    if current_ruleset is None:
        ruleset_action = "create"
    elif current_ruleset != desired_ruleset:
        ruleset_action = "update"
    else:
        ruleset_action = "none"

    return {
        "repository": repository,
        "repository_settings": {
            "action": "update" if settings_changed else "none",
            "current": current_settings,
            "desired": desired_settings,
        },
        "ruleset": {
            "action": ruleset_action,
            "id": ruleset_id,
            "current": current_ruleset,
            "desired": desired_ruleset,
        },
    }


def apply_plan(plan: dict[str, Any]) -> None:
    repository = plan["repository"]

    if plan["repository_settings"]["action"] == "update":
        gh_api("PATCH", f"/repos/{repository}", plan["repository_settings"]["desired"])

    ruleset = plan["ruleset"]
    if ruleset["action"] == "create":
        gh_api("POST", f"/repos/{repository}/rulesets", ruleset["desired"])
    elif ruleset["action"] == "update":
        gh_api(
            "PUT",
            f"/repos/{repository}/rulesets/{ruleset['id']}",
            ruleset["desired"],
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plan or apply the repository standard. Planning is the default; "
            "writes require --apply and an exact --confirm-repo value."
        )
    )
    parser.add_argument("--repo", help="target repository in owner/name form")
    parser.add_argument(
        "--apply", action="store_true", help="apply the planned repository changes"
    )
    parser.add_argument(
        "--confirm-repo",
        help="required with --apply; must exactly equal the resolved owner/name",
    )
    parser.add_argument(
        "--human-approvals",
        type=int,
        choices=range(0, 7),
        metavar="0..6",
        help="override the standard number of required human approvals",
    )
    parser.add_argument(
        "--required-check",
        action="append",
        default=[],
        help="require a status check by exact context name; repeat as needed",
    )
    draft_group = parser.add_mutually_exclusive_group()
    draft_group.add_argument(
        "--review-drafts",
        dest="review_drafts",
        action="store_true",
        help="ask Copilot to review draft pull requests",
    )
    draft_group.add_argument(
        "--no-review-drafts",
        dest="review_drafts",
        action="store_false",
        help="do not ask Copilot to review drafts",
    )
    parser.set_defaults(review_drafts=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repository = resolve_repository(args.repo)
        if args.apply and args.confirm_repo != repository:
            raise ValueError(
                "--apply requires --confirm-repo with the exact target "
                f"({repository})"
            )

        standard = load_standard()
        plan = build_plan(
            repository,
            standard,
            human_approvals=args.human_approvals,
            required_checks=args.required_check,
            review_drafts=args.review_drafts,
        )
        print(json.dumps(plan, indent=2, sort_keys=True))

        if not args.apply:
            return 0

        apply_plan(plan)
        print(f"\nApplied repository standard to {repository}.")
        return 0
    except (CommandError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
