#!/usr/bin/env python3
"""Apply Moodle category hide/delete changes via AWS SSM.

CSV format examples:
    category_id,operation
    4,Delete
    8,Hide
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

import subprocess
import sys

VALID_ACTIONS = {"delete", "hide"}
ENV_TG_PREFIX = {
    "dev": "dev",
    "test": "test",
    "production": "prod",
}
CATEGORY_ID_KEYS = ["category_id", "categoryid", "CategoryID", "CategoryId"]
OPERATION_KEYS = ["operation", "Operation", "action", "Action"]


@dataclass
class Change:
    category_id: int
    action: str


@dataclass
class Result:
    category_id: int
    action: str
    status: str
    detail: str
    failure_type: str = ""
    ssm_command_id: str = ""
    ssm_status: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Moodle category hide/delete changes via SSM."
    )
    parser.add_argument("--csv", default="category_changes.csv", help="Input CSV path.")
    parser.add_argument(
        "--env",
        required=True,
        choices=sorted(ENV_TG_PREFIX.keys()),
        help="NovaLXP environment target.",
    )
    parser.add_argument(
        "--instance-id",
        help="Explicit EC2 instance ID. If omitted, discovered from <env>-novalxp-tg.",
    )
    parser.add_argument(
        "--region",
        default="eu-west-2",
        help="AWS region (default: eu-west-2).",
    )
    parser.add_argument(
        "--moodle-root",
        default="/var/www/moodle",
        help="Moodle root directory on instance (default: /var/www/moodle).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes. Without this flag, show planned operations only.",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=180,
        help="Per-command wait timeout in seconds (default: 180).",
    )
    parser.add_argument(
        "--log-file",
        help=(
            "Optional CSV log output path. "
            "Default: NovaLXP-CourseCleanup/logs/ssm-category-changes-<timestamp>.csv"
        ),
    )
    return parser.parse_args()


def run_aws_json(command: List[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown AWS CLI error"
        raise RuntimeError(stderr)
    stdout = completed.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unexpected AWS CLI output: {stdout}") from exc


def get_first_value(row: dict, keys: List[str]) -> str:
    for key in keys:
        if key in row:
            return (row.get(key) or "").strip()
    return ""


def parse_changes(csv_path: str) -> List[Change]:
    changes: List[Change] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames or []
        if not any(key in fieldnames for key in CATEGORY_ID_KEYS):
            raise ValueError(
                "CSV missing category id column. Use one of: "
                + ", ".join(CATEGORY_ID_KEYS)
            )
        if not any(key in fieldnames for key in OPERATION_KEYS):
            raise ValueError(
                "CSV missing operation column. Use one of: "
                + ", ".join(OPERATION_KEYS)
            )

        for row_number, row in enumerate(reader, start=2):
            raw_id = get_first_value(row, CATEGORY_ID_KEYS)
            raw_action = get_first_value(row, OPERATION_KEYS).lower()

            if not raw_id and not raw_action:
                continue
            if not raw_id:
                raise ValueError(f"Row {row_number}: category id is empty.")
            if raw_action not in VALID_ACTIONS:
                raise ValueError(
                    f"Row {row_number}: invalid operation '{get_first_value(row, OPERATION_KEYS)}'. "
                    "Expected Delete or Hide."
                )
            try:
                category_id = int(raw_id)
            except ValueError as exc:
                raise ValueError(f"Row {row_number}: invalid category id '{raw_id}'.") from exc
            if category_id <= 0:
                raise ValueError(f"Row {row_number}: category id must be positive.")

            changes.append(Change(category_id=category_id, action=raw_action))

    if not changes:
        raise ValueError("No valid rows in CSV.")
    return changes


def discover_instance_id(env: str, region: str) -> str:
    prefix = ENV_TG_PREFIX[env]
    tg_name = f"{prefix}-novalxp-tg"

    tg_resp = run_aws_json(
        [
            "aws",
            "elbv2",
            "describe-target-groups",
            "--region",
            region,
            "--names",
            tg_name,
            "--output",
            "json",
        ]
    )
    groups = tg_resp.get("TargetGroups", [])
    if not groups:
        raise RuntimeError(f"Target group not found: {tg_name}")

    th_resp = run_aws_json(
        [
            "aws",
            "elbv2",
            "describe-target-health",
            "--region",
            region,
            "--target-group-arn",
            groups[0]["TargetGroupArn"],
            "--output",
            "json",
        ]
    )
    descriptions = th_resp.get("TargetHealthDescriptions", [])
    if not descriptions:
        raise RuntimeError(f"No targets found in target group: {tg_name}")

    healthy = [
        d for d in descriptions if d.get("TargetHealth", {}).get("State") == "healthy"
    ]
    selected = healthy[0] if healthy else descriptions[0]
    target_id = selected.get("Target", {}).get("Id")
    if not target_id:
        raise RuntimeError(f"Could not resolve target instance from target group: {tg_name}")
    return target_id


def build_remote_command(change: Change, moodle_root: str) -> str:
    php_prelude = (
        'define("CLI_SCRIPT", true); '
        'require_once("config.php"); '
        'require_once($CFG->dirroot . "/course/classes/category.php"); '
        'if (!class_exists("core_course_category")) { '
        'fwrite(STDERR, "core_course_category class not loaded\\n"); exit(1); } '
        f"$catid = {change.category_id}; "
        "$category = core_course_category::get($catid, IGNORE_MISSING); "
        'if (!$category) { fwrite(STDERR, "Category not found\\n"); exit(1); } '
    )

    if change.action == "delete":
        php_code = (
            php_prelude
            + 'echo "Deleting category id {$category->id}\\n"; '
            + 'echo "Category name: {$category->get_formatted_name()}\\n"; '
            + "$category->delete_full(false); "
            + 'echo "Done!\\n";'
        )
        return (
            f"cd {moodle_root} && "
            "sudo -u apache /usr/bin/php -r "
            f"'{php_code}'"
        )

    php_code = (
        php_prelude
        + 'if (!$category->visible) { echo "Category already hidden\\n"; exit(0); } '
        + "$category->hide(); "
        + 'echo "Category {$catid} hidden\\n";'
    )
    return (
        f"cd {moodle_root} && "
        "sudo -u apache /usr/bin/php -r "
        f"'{php_code}'"
    )


def send_ssm_command(instance_id: str, region: str, command: str) -> str:
    resp = run_aws_json(
        [
            "aws",
            "ssm",
            "send-command",
            "--region",
            region,
            "--instance-ids",
            instance_id,
            "--document-name",
            "AWS-RunShellScript",
            "--parameters",
            json.dumps({"commands": ["set -e", command]}),
            "--output",
            "json",
        ]
    )
    return resp["Command"]["CommandId"]


def wait_ssm_result(command_id: str, instance_id: str, region: str, timeout: int) -> tuple[str, str, str]:
    start = time.time()
    while True:
        resp = run_aws_json(
            [
                "aws",
                "ssm",
                "get-command-invocation",
                "--region",
                region,
                "--command-id",
                command_id,
                "--instance-id",
                instance_id,
                "--output",
                "json",
            ]
        )
        status = resp.get("Status", "Unknown")
        if status in {"Success", "Failed", "TimedOut", "Cancelled", "Undeliverable", "Terminated"}:
            stdout = (resp.get("StandardOutputContent") or "").strip()
            stderr = (resp.get("StandardErrorContent") or "").strip()
            return status, stdout, stderr

        if time.time() - start > timeout:
            return "TimedOut", "", f"Timed out waiting for command {command_id}"
        time.sleep(2)


def classify_failure(detail: str, ssm_status: str) -> str:
    lower = detail.lower()
    if "category not found" in lower:
        return "CATEGORY_NOT_FOUND"
    if "cannot delete" in lower or "can not delete" in lower:
        return "CATEGORY_DELETE_BLOCKED"
    if "default exception handler" in lower or "error code:" in lower:
        return "MOODLE_EXCEPTION"
    if ssm_status in {"TimedOut"}:
        return "SSM_TIMEOUT"
    if ssm_status in {"Cancelled", "Undeliverable", "Terminated"}:
        return "SSM_COMMAND_ERROR"
    if "failed to run commands" in lower:
        return "SSM_REMOTE_FAILURE"
    if "unknown aws cli error" in lower or "an error occurred" in lower:
        return "AWS_CLI_ERROR"
    return "UNKNOWN_FAILURE"


def resolve_log_file(log_file_arg: str | None) -> Path:
    if log_file_arg:
        return Path(log_file_arg)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("NovaLXP-CourseCleanup") / "logs" / f"ssm-category-changes-{ts}.csv"


def write_log(
    *,
    log_file: Path,
    env: str,
    region: str,
    instance_id: str,
    csv_path: str,
    execute: bool,
    results: List[Result],
) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()

    with log_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp_utc",
                "env",
                "region",
                "instance_id",
                "execute",
                "input_csv",
                "category_id",
                "action",
                "status",
                "failure_type",
                "ssm_status",
                "ssm_command_id",
                "detail",
            ]
        )
        for r in results:
            writer.writerow(
                [
                    timestamp,
                    env,
                    region,
                    instance_id,
                    "true" if execute else "false",
                    csv_path,
                    r.category_id,
                    r.action,
                    r.status,
                    r.failure_type,
                    r.ssm_status,
                    r.ssm_command_id,
                    r.detail.replace("\n", "\\n"),
                ]
            )


def main() -> int:
    args = parse_args()
    try:
        changes = parse_changes(args.csv)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        instance_id = args.instance_id or discover_instance_id(args.env, args.region)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    log_file = resolve_log_file(args.log_file)

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Environment: {args.env}")
    print(f"Region: {args.region}")
    print(f"Instance: {instance_id}")
    print(f"Moodle root: {args.moodle_root}")
    print(f"CSV: {args.csv}")
    print(f"Changes loaded: {len(changes)}")
    print(f"Log file: {log_file}")

    results: List[Result] = []

    for change in changes:
        command = build_remote_command(change, args.moodle_root)
        if not args.execute:
            results.append(
                Result(
                    category_id=change.category_id,
                    action=change.action,
                    status="DRY-RUN",
                    detail=command,
                )
            )
            continue

        try:
            command_id = send_ssm_command(instance_id, args.region, command)
            status, stdout, stderr = wait_ssm_result(
                command_id, instance_id, args.region, args.wait_seconds
            )
            if status == "Success":
                detail = stdout or "Completed"
                results.append(
                    Result(
                        category_id=change.category_id,
                        action=change.action,
                        status="SUCCESS",
                        detail=detail,
                        ssm_command_id=command_id,
                        ssm_status=status,
                    )
                )
            else:
                detail = stderr or stdout or f"SSM status: {status}"
                results.append(
                    Result(
                        category_id=change.category_id,
                        action=change.action,
                        status="FAILED",
                        detail=detail,
                        failure_type=classify_failure(detail, status),
                        ssm_command_id=command_id,
                        ssm_status=status,
                    )
                )
        except RuntimeError as exc:
            detail = str(exc)
            results.append(
                Result(
                    category_id=change.category_id,
                    action=change.action,
                    status="FAILED",
                    detail=detail,
                    failure_type=classify_failure(detail, "RuntimeError"),
                    ssm_status="RuntimeError",
                )
            )

    print("\nExecution summary")
    print("-" * 96)
    success = failed = dry_run = 0
    failure_counts: dict[str, int] = {}

    for result in results:
        if result.status == "SUCCESS":
            success += 1
        elif result.status == "FAILED":
            failed += 1
            key = result.failure_type or "UNKNOWN_FAILURE"
            failure_counts[key] = failure_counts.get(key, 0) + 1
        else:
            dry_run += 1

        print(
            f"CategoryID={result.category_id:<8} "
            f"Action={result.action:<6} "
            f"Status={result.status:<7} "
            f"Detail={result.detail}"
        )

    print("-" * 96)
    print(
        f"Totals: {len(results)} processed | success={success} failed={failed} dry_run={dry_run}"
    )
    if failure_counts:
        print("Failure breakdown:")
        for key in sorted(failure_counts.keys()):
            print(f"- {key}: {failure_counts[key]}")

    write_log(
        log_file=log_file,
        env=args.env,
        region=args.region,
        instance_id=instance_id,
        csv_path=args.csv,
        execute=args.execute,
        results=results,
    )
    print(f"Detailed log written: {log_file}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
