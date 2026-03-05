#!/usr/bin/env python3
"""Apply Moodle course changes via AWS SSM on app instance(s).

Uses Moodle CLI on the EC2 instance instead of web service APIs.
CSV format:
    CourseID,Action
    182,Delete
    197,Hide
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

VALID_ACTIONS = {"delete", "hide"}
ENV_TG_PREFIX = {
    "dev": "dev",
    "test": "test",
    "production": "prod",
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
    failure_type: str = ""
    ssm_command_id: str = ""
    ssm_status: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Moodle delete/hide course changes via SSM."
    )
    parser.add_argument("--csv", default="course_changes.csv", help="Input CSV path.")
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
            "Default: NovaLXP-CourseCleanup/logs/ssm-course-changes-<timestamp>.csv"
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


def parse_changes(csv_path: str) -> List[Change]:
    changes: List[Change] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        required = {"CourseID", "Action"}
        found = set(reader.fieldnames or [])
        missing = required - found
        if missing:
            raise ValueError(
                f"CSV missing required columns: {', '.join(sorted(missing))}."
            )

        for row_number, row in enumerate(reader, start=2):
            raw_id = (row.get("CourseID") or "").strip()
            raw_action = (row.get("Action") or "").strip().lower()
            if not raw_id and not raw_action:
                continue
            if not raw_id:
                raise ValueError(f"Row {row_number}: CourseID is empty.")
            if raw_action not in VALID_ACTIONS:
                raise ValueError(
                    f"Row {row_number}: invalid Action '{row.get('Action')}'. "
                    "Expected Delete or Hide."
                )
            try:
                course_id = int(raw_id)
            except ValueError as exc:
                raise ValueError(f"Row {row_number}: invalid CourseID '{raw_id}'.") from exc
            if course_id <= 0:
                raise ValueError(f"Row {row_number}: CourseID must be positive.")
            changes.append(Change(course_id=course_id, action=raw_action))

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
    tg_arn = groups[0]["TargetGroupArn"]

    th_resp = run_aws_json(
        [
            "aws",
            "elbv2",
            "describe-target-health",
            "--region",
            region,
            "--target-group-arn",
            tg_arn,
            "--output",
            "json",
        ]
    )
    descriptions = th_resp.get("TargetHealthDescriptions", [])
    if not descriptions:
        raise RuntimeError(f"No targets found in target group: {tg_name}")

    # Prefer healthy target if present; otherwise first target.
    healthy = [
        d for d in descriptions if d.get("TargetHealth", {}).get("State") == "healthy"
    ]
    selected = healthy[0] if healthy else descriptions[0]
    target_id = selected.get("Target", {}).get("Id")
    if not target_id:
        raise RuntimeError(f"Could not resolve target instance from target group: {tg_name}")
    return target_id


def build_remote_command(change: Change, moodle_root: str) -> str:
    if change.action == "delete":
        return (
            f"cd {moodle_root} && "
            f"sudo -u apache /usr/bin/php admin/cli/delete_course.php "
            f"--non-interactive --disablerecyclebin --courseid={change.course_id}"
        )

    return (
        f"cd {moodle_root} && "
        "sudo -u apache /usr/bin/php -r "
        "'define(\"CLI_SCRIPT\", true); "
        "require_once(\"config.php\"); "
        "require_once($CFG->dirroot . \"/course/lib.php\"); "
        f"course_change_visibility({change.course_id}, false); "
        f"echo \"Course {change.course_id} hidden\\n\";'"
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
    if "course not found" in lower:
        return "COURSE_NOT_FOUND"
    if "undefined function course_get_format()" in lower:
        return "MOODLE_CODE_EXCEPTION"
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
    return Path("NovaLXP-CourseCleanup") / "logs" / f"ssm-course-changes-{ts}.csv"


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
                "course_id",
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
                    r.course_id,
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

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Environment: {args.env}")
    print(f"Region: {args.region}")
    print(f"Instance: {instance_id}")
    print(f"Moodle root: {args.moodle_root}")
    print(f"CSV: {args.csv}")
    print(f"Changes loaded: {len(changes)}")
    log_file = resolve_log_file(args.log_file)
    print(f"Log file: {log_file}")

    results: List[Result] = []

    for change in changes:
        command = build_remote_command(change, args.moodle_root)
        if not args.execute:
            results.append(
                Result(
                    course_id=change.course_id,
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
                        change.course_id,
                        change.action,
                        "SUCCESS",
                        detail,
                        ssm_command_id=command_id,
                        ssm_status=status,
                    )
                )
            else:
                detail = stderr or stdout or f"SSM status: {status}"
                results.append(
                    Result(
                        change.course_id,
                        change.action,
                        "FAILED",
                        detail,
                        failure_type=classify_failure(detail, status),
                        ssm_command_id=command_id,
                        ssm_status=status,
                    )
                )
        except RuntimeError as exc:
            detail = str(exc)
            results.append(
                Result(
                    change.course_id,
                    change.action,
                    "FAILED",
                    detail,
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
            failure_counts[result.failure_type or "UNKNOWN_FAILURE"] = (
                failure_counts.get(result.failure_type or "UNKNOWN_FAILURE", 0) + 1
            )
        else:
            dry_run += 1

        print(
            f"CourseID={result.course_id:<8} "
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
