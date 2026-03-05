#!/usr/bin/env python3
"""Create or update a Moodle token secret in AWS Secrets Manager.

This script stores the token as JSON, e.g. {"token": "..."}, so it can be
consumed by apply-course-changes.py via --aws-secret-id.
"""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import subprocess
import sys

VALID_ENVS = {"dev", "test", "production"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create/update environment-specific Moodle token secret in AWS Secrets Manager."
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=sorted(VALID_ENVS),
        help="NovaLXP environment target.",
    )
    parser.add_argument(
        "--token",
        help="Moodle token value. If omitted, you will be prompted securely.",
    )
    parser.add_argument(
        "--secret-name",
        help=(
            "Secrets Manager name. Default: novalxp/<env>/moodle/webservice-token"
        ),
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "eu-west-2"),
        help="AWS region (default: AWS_REGION or eu-west-2).",
    )
    parser.add_argument(
        "--kms-key-id",
        help="Optional KMS key id/arn for create-secret.",
    )
    parser.add_argument(
        "--description",
        help="Optional secret description for create-secret.",
    )
    return parser.parse_args()


def run_aws(command: list[str]) -> dict:
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
        raise RuntimeError(f"Unexpected AWS CLI response: {stdout}") from exc


def secret_exists(secret_name: str, region: str) -> tuple[bool, str | None]:
    describe_cmd = [
        "aws",
        "secretsmanager",
        "describe-secret",
        "--secret-id",
        secret_name,
        "--region",
        region,
        "--output",
        "json",
    ]

    completed = subprocess.run(describe_cmd, capture_output=True, text=True, check=False)
    if completed.returncode == 0:
        parsed = json.loads(completed.stdout)
        return True, parsed.get("ARN")

    stderr = completed.stderr or ""
    if "ResourceNotFoundException" in stderr:
        return False, None

    raise RuntimeError(stderr.strip() or "Failed to describe secret.")


def resolve_token(passed_token: str | None) -> str:
    token = (passed_token or "").strip()
    if token:
        return token

    prompt_value = getpass.getpass("Enter Moodle token (input hidden): ").strip()
    if not prompt_value:
        raise ValueError("Token cannot be empty.")
    return prompt_value


def main() -> int:
    args = parse_args()
    secret_name = args.secret_name or f"novalxp/{args.env}/moodle/webservice-token"

    try:
        token = resolve_token(args.token)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = {
        "token": token,
        "environment": args.env,
        "updated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    try:
        exists, existing_arn = secret_exists(secret_name, args.region)

        if exists:
            update_cmd = [
                "aws",
                "secretsmanager",
                "update-secret",
                "--secret-id",
                secret_name,
                "--region",
                args.region,
                "--secret-string",
                json.dumps(payload),
                "--output",
                "json",
            ]
            response = run_aws(update_cmd)
            arn = response.get("ARN") or existing_arn
            print("Action: updated existing secret")
            print(f"Secret name: {secret_name}")
            print(f"Secret id (ARN): {arn}")
            return 0

        create_cmd = [
            "aws",
            "secretsmanager",
            "create-secret",
            "--name",
            secret_name,
            "--region",
            args.region,
            "--secret-string",
            json.dumps(payload),
            "--output",
            "json",
        ]
        if args.description:
            create_cmd.extend(["--description", args.description])
        if args.kms_key_id:
            create_cmd.extend(["--kms-key-id", args.kms_key_id])

        response = run_aws(create_cmd)
        print("Action: created new secret")
        print(f"Secret name: {response.get('Name', secret_name)}")
        print(f"Secret id (ARN): {response.get('ARN')}")
        return 0

    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
