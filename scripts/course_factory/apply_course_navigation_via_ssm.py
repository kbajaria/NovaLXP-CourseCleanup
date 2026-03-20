#!/usr/bin/env python3
"""Render and apply repeated Moodle navigation labels from a JSON manifest via AWS SSM."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import time
from pathlib import Path


ENV_TG_PREFIX = {
    "dev": "dev",
    "test": "test",
    "production": "prod",
}


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_html(manifest: dict) -> str:
    button_class = manifest["button_class"]
    button_style = manifest["button_style"]
    buttons = []
    for button in manifest["buttons"]:
        label = html.escape(button["label"], quote=False)
        href = html.escape(button["href"], quote=True)
        buttons.append(
            f'<a class="{button_class}" style="{button_style}" href="{href}">{label}</a>'
        )
    container_class = html.escape(manifest["container_class"], quote=True)
    aria_label = html.escape(manifest["aria_label"], quote=True)
    return (
        f'<div class="{container_class}" role="navigation" aria-label="{aria_label}">'
        + " ".join(buttons)
        + "</div>"
    )


def run_aws_json(command: list[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown AWS CLI error"
        raise RuntimeError(stderr)
    stdout = completed.stdout.strip()
    if not stdout:
        return {}
    return json.loads(stdout)


def discover_instance_id(env: str, region: str) -> str:
    tg_name = f"{ENV_TG_PREFIX[env]}-novalxp-tg"
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
    tg_arn = tg_resp["TargetGroups"][0]["TargetGroupArn"]
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
    descriptions = th_resp["TargetHealthDescriptions"]
    healthy = [
        desc for desc in descriptions if desc.get("TargetHealth", {}).get("State") == "healthy"
    ]
    selected = healthy[0] if healthy else descriptions[0]
    return selected["Target"]["Id"]


def run_ssm(instance_id: str, region: str, command: str) -> tuple[str, str, str]:
    command_id = subprocess.check_output(
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
            "--query",
            "Command.CommandId",
            "--output",
            "text",
        ],
        text=True,
    ).strip()

    for _ in range(60):
        time.sleep(2)
        out = subprocess.check_output(
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
            ],
            text=True,
        )
        data = json.loads(out)
        status = data["Status"]
        if status not in ("Pending", "InProgress", "Delayed"):
            return status, data.get("StandardOutputContent", ""), data.get(
                "StandardErrorContent", ""
            )
    raise RuntimeError("Timed out waiting for SSM command")


def php_string_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def build_remote_command(
    manifest: dict,
    rendered_html: str,
    moodle_root: str,
) -> str:
    course_id = int(manifest["course_id"])
    label_name_prefix = manifest["label_name_prefix"]
    php = f"""cat <<'PHP' >/tmp/apply_course_navigation_via_ssm.php
<?php
define("CLI_SCRIPT", true);
require_once({php_string_literal(str(Path(moodle_root) / "config.php"))});
require_once($CFG->libdir . "/modinfolib.php");

$courseid = {course_id};
$prefix = {php_string_literal(label_name_prefix)};
$html = {php_string_literal(rendered_html)};
$sql = "SELECT l.*
          FROM {{label}} l
          JOIN {{course_modules}} cm ON cm.instance = l.id
          JOIN {{modules}} m ON m.id = cm.module
         WHERE cm.course = ? AND m.name = 'label' AND " . $DB->sql_like("l.name", "?", false);
$labels = $DB->get_records_sql($sql, array($courseid, $prefix . "%"));
$changed = array();
foreach ($labels as $label) {{
    if ($label->intro === $html) {{
        continue;
    }}
    $label->intro = $html;
    $DB->update_record("label", $label);
    $changed[] = array("id" => (int)$label->id, "name" => $label->name);
}}
rebuild_course_cache($courseid, true);
echo json_encode(
    array(
        "courseid" => $courseid,
        "matched" => count($labels),
        "changed" => count($changed),
        "labels" => $changed
    ),
    JSON_PRETTY_PRINT
);
PHP
cd {moodle_root} && sudo -u apache /usr/bin/php /tmp/apply_course_navigation_via_ssm.php && rm -f /tmp/apply_course_navigation_via_ssm.php"""
    return php


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        default="templates/course-184-quick-navigation.json",
        help="Path to the navigation manifest JSON.",
    )
    parser.add_argument(
        "--render-output",
        help="Optional path to write the rendered HTML snippet.",
    )
    parser.add_argument(
        "--print-html",
        action="store_true",
        help="Print the rendered HTML to stdout.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the rendered HTML to matching label activities via SSM.",
    )
    parser.add_argument(
        "--env",
        choices=sorted(ENV_TG_PREFIX.keys()),
        help="NovaLXP environment target. Required with --apply unless --instance-id is set.",
    )
    parser.add_argument(
        "--instance-id",
        help="Explicit EC2 instance ID. If omitted, discovered from the target group for --env.",
    )
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--moodle-root", default="/var/www/moodle/public")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)
    rendered_html = render_html(manifest)

    if args.render_output:
        Path(args.render_output).write_text(rendered_html + "\n", encoding="utf-8")

    if args.print_html:
        print(rendered_html)

    if not args.apply:
        return 0

    if not args.instance_id and not args.env:
        raise ValueError("Provide --env or --instance-id when using --apply.")

    instance_id = args.instance_id or discover_instance_id(args.env, args.region)
    command = build_remote_command(manifest, rendered_html, args.moodle_root)
    status, stdout, stderr = run_ssm(instance_id, args.region, command)
    if status != "Success":
        raise RuntimeError(stderr or stdout or f"SSM command failed with status {status}")
    print(stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
