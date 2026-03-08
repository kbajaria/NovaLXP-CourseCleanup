#!/usr/bin/env python3
"""Move an existing Moodle course badge to the learning-path hub via AWS SSM."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


def load_manifest(path_dir: Path) -> dict:
    return json.loads((path_dir / "learning-path.json").read_text(encoding="utf-8"))


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
            return status, data.get("StandardOutputContent", ""), data.get("StandardErrorContent", "")
    raise RuntimeError("Timed out waiting for SSM command")


def php_string_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def build_remote_command(
    moodle_root: str,
    badge_name: str,
    new_badge_name: str,
    hub_shortname: str,
    purge_issued: bool,
) -> str:
    purge_flag = "true" if purge_issued else "false"
    php = f"""cat <<'PHP' >/tmp/rehome_badge_to_pathway_hub.php
<?php
define(\"CLI_SCRIPT\", true);
require_once({php_string_literal(str(Path(moodle_root) / "config.php"))});

$badge = $DB->get_record(\"badge\", array(\"name\" => {php_string_literal(badge_name)}), \"*\", MUST_EXIST);
$hub = $DB->get_record(\"course\", array(\"shortname\" => {php_string_literal(hub_shortname)}), \"*\", MUST_EXIST);
$criterion = $DB->get_record(\"badge_criteria\", array(\"badgeid\" => $badge->id, \"criteriatype\" => 4), \"*\", MUST_EXIST);
$params = $DB->get_records(\"badge_criteria_param\", array(\"critid\" => $criterion->id), \"id ASC\");
if (!$params) {{
    throw new Exception(\"Badge criteria params not found for badge \" . $badge->id);
}}

$original = array(
    \"badgeid\" => (int)$badge->id,
    \"name\" => $badge->name,
    \"courseid\" => (int)$badge->courseid,
    \"criterion\" => null,
);

foreach ($params as $param) {{
    $original[\"criterion\"] = array(\"name\" => $param->name, \"value\" => (int)$param->value);
    break;
}}

$badge->courseid = $hub->id;
$badge->name = {php_string_literal(new_badge_name)};
$badge->timemodified = time();
$DB->update_record(\"badge\", $badge);

$first = true;
foreach ($params as $param) {{
    if ($first) {{
        $param->name = \"course_\" . $hub->id;
        $param->value = $hub->id;
        $DB->update_record(\"badge_criteria_param\", $param);
        $first = false;
    }} else {{
        $DB->delete_records(\"badge_criteria_param\", array(\"id\" => $param->id));
    }}
}}

$purged = array(\"issued\" => 0, \"criteria_met\" => 0);
if ({purge_flag}) {{
    $issued = $DB->get_records(\"badge_issued\", array(\"badgeid\" => $badge->id));
    foreach ($issued as $row) {{
        $purged[\"criteria_met\"] += $DB->count_records(\"badge_criteria_met\", array(\"issuedid\" => $row->id));
        $DB->delete_records(\"badge_criteria_met\", array(\"issuedid\" => $row->id));
        $DB->delete_records(\"badge_issued\", array(\"id\" => $row->id));
        $purged[\"issued\"]++;
    }}
}}

$updated = $DB->get_record(\"badge\", array(\"id\" => $badge->id), \"*\", MUST_EXIST);
$updatedParam = $DB->get_record(\"badge_criteria_param\", array(\"critid\" => $criterion->id), \"*\", MUST_EXIST);

echo json_encode(
    array(
        \"badgeid\" => (int)$updated->id,
        \"old\" => $original,
        \"new\" => array(
            \"name\" => $updated->name,
            \"courseid\" => (int)$updated->courseid,
            \"criterion\" => array(\"name\" => $updatedParam->name, \"value\" => (int)$updatedParam->value),
        ),
        \"purged\" => $purged,
    ),
    JSON_PRETTY_PRINT
);
PHP
cd {moodle_root} && sudo -u apache /usr/bin/php /tmp/rehome_badge_to_pathway_hub.php && rm -f /tmp/rehome_badge_to_pathway_hub.php"""
    return php


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path_dir")
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--badge-name", required=True)
    parser.add_argument("--new-badge-name", required=True)
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--moodle-root", default="/var/www/moodle/public")
    parser.add_argument("--purge-issued", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(Path(args.path_dir).resolve())
    hub_shortname = manifest["learning_path"]["id"]
    command = build_remote_command(
        args.moodle_root,
        args.badge_name,
        args.new_badge_name,
        hub_shortname,
        args.purge_issued,
    )
    status, stdout, stderr = run_ssm(args.instance_id, args.region, command)
    if status != "Success":
        raise RuntimeError(stderr or stdout or f"SSM command failed with status {status}")
    print(stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
