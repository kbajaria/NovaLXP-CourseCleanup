#!/usr/bin/env python3
"""Apply Moodle course delete/hide operations from a CSV file.

CSV format:
    CourseID,Action
    182,Delete
    197,Hide
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable, List

VALID_ACTIONS = {"delete", "hide"}
ENV_TO_VAR = {
    "dev": "NOVALXP_DEV_BASE_URL",
    "test": "NOVALXP_TEST_BASE_URL",
    "production": "NOVALXP_PRODUCTION_BASE_URL",
}


@dataclass
class Change:
    course_id: int
    action: str


@dataclass
class Result:
    course_id: int
    action: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete or hide Moodle courses from a CSV change list."
    )
    parser.add_argument(
        "--csv",
        default="course_changes.csv",
        help="Path to CSV file with CourseID and Action columns.",
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=sorted(ENV_TO_VAR.keys()),
        help="NovaLXP environment target.",
    )
    parser.add_argument(
        "--base-url",
        help=(
            "Moodle base URL, e.g. https://dev.novalxp.co.uk. "
            "If omitted, uses env var by --env (e.g. NOVALXP_DEV_BASE_URL)."
        ),
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("NOVALXP_MOODLE_TOKEN"),
        help="Moodle web service token. Defaults to NOVALXP_MOODLE_TOKEN.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform API calls. Without this flag, runs in dry-run mode.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30).",
    )
    return parser.parse_args()


def normalize_base_url(args: argparse.Namespace) -> str:
    if args.base_url:
        return args.base_url.rstrip("/")

    env_var = ENV_TO_VAR[args.env]
    base_url = os.environ.get(env_var)
    if base_url:
        return base_url.rstrip("/")

    if args.env == "dev":
        return "https://dev.novalxp.co.uk"

    raise ValueError(
        f"Missing base URL for env '{args.env}'. "
        f"Set --base-url or export {env_var}."
    )


def parse_changes(csv_path: str) -> List[Change]:
    changes: List[Change] = []

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = {"CourseID", "Action"}
        found_columns = set(reader.fieldnames or [])
        missing = required_columns - found_columns
        if missing:
            raise ValueError(
                f"CSV missing required columns: {', '.join(sorted(missing))}. "
                f"Found columns: {', '.join(sorted(found_columns)) or '<none>'}."
            )

        for row_number, row in enumerate(reader, start=2):
            raw_course_id = (row.get("CourseID") or "").strip()
            raw_action = (row.get("Action") or "").strip().lower()

            if not raw_course_id and not raw_action:
                continue

            if not raw_course_id:
                raise ValueError(f"Row {row_number}: CourseID is empty.")
            if raw_action not in VALID_ACTIONS:
                raise ValueError(
                    f"Row {row_number}: invalid Action '{row.get('Action')}'. "
                    f"Expected one of: Delete, Hide."
                )

            try:
                course_id = int(raw_course_id)
            except ValueError as exc:
                raise ValueError(
                    f"Row {row_number}: invalid CourseID '{raw_course_id}'."
                ) from exc

            if course_id <= 0:
                raise ValueError(
                    f"Row {row_number}: CourseID must be a positive integer."
                )

            changes.append(Change(course_id=course_id, action=raw_action))

    if not changes:
        raise ValueError("No valid rows found in CSV.")

    return changes


def post_moodle(
    *,
    base_url: str,
    token: str,
    wsfunction: str,
    params: dict,
    timeout: int,
) -> dict:
    form_data = {
        "wstoken": token,
        "moodlewsrestformat": "json",
        "wsfunction": wsfunction,
    }
    form_data.update(params)

    endpoint = f"{base_url}/webservice/rest/server.php"
    encoded = urllib.parse.urlencode(form_data).encode("utf-8")

    request = urllib.request.Request(endpoint, data=encoded, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")

    parsed = json.loads(body)
    if isinstance(parsed, dict) and parsed.get("exception"):
        message = parsed.get("message") or "Unknown Moodle exception"
        errorcode = parsed.get("errorcode") or "unknown"
        raise RuntimeError(f"Moodle error ({errorcode}): {message}")
    return parsed


def apply_change(
    change: Change,
    *,
    base_url: str,
    token: str,
    timeout: int,
    execute: bool,
) -> Result:
    action = change.action

    if not execute:
        return Result(
            course_id=change.course_id,
            action=action,
            status="DRY-RUN",
            detail="No API call made.",
        )

    try:
        if action == "delete":
            post_moodle(
                base_url=base_url,
                token=token,
                wsfunction="core_course_delete_courses",
                params={"courseids[0]": str(change.course_id)},
                timeout=timeout,
            )
            return Result(
                course_id=change.course_id,
                action=action,
                status="SUCCESS",
                detail="Course deleted.",
            )

        post_moodle(
            base_url=base_url,
            token=token,
            wsfunction="core_course_update_courses",
            params={
                "courses[0][id]": str(change.course_id),
                "courses[0][visible]": "0",
            },
            timeout=timeout,
        )
        return Result(
            course_id=change.course_id,
            action=action,
            status="SUCCESS",
            detail="Course hidden (visible=0).",
        )
    except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
        return Result(
            course_id=change.course_id,
            action=action,
            status="FAILED",
            detail=str(exc),
        )


def print_summary(results: Iterable[Result]) -> int:
    rows = list(results)
    print("\nExecution summary")
    print("-" * 72)

    success = 0
    failed = 0
    dry_run = 0

    for result in rows:
        if result.status == "SUCCESS":
            success += 1
        elif result.status == "FAILED":
            failed += 1
        elif result.status == "DRY-RUN":
            dry_run += 1

        print(
            f"CourseID={result.course_id:<8} "
            f"Action={result.action:<6} "
            f"Status={result.status:<7} "
            f"Detail={result.detail}"
        )

    print("-" * 72)
    print(
        f"Totals: {len(rows)} processed | "
        f"success={success} failed={failed} dry_run={dry_run}"
    )
    return failed


def main() -> int:
    args = parse_args()

    try:
        base_url = normalize_base_url(args)
        changes = parse_changes(args.csv)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.execute and not args.token:
        print(
            "ERROR: Missing Moodle token. Provide --token or set NOVALXP_MOODLE_TOKEN.",
            file=sys.stderr,
        )
        return 2

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Environment: {args.env}")
    print(f"Base URL: {base_url}")
    print(f"CSV: {args.csv}")
    print(f"Changes loaded: {len(changes)}")

    results = [
        apply_change(
            change,
            base_url=base_url,
            token=args.token or "",
            timeout=args.timeout,
            execute=args.execute,
        )
        for change in changes
    ]

    failed = print_summary(results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
