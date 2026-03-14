#!/usr/bin/env python3
"""Promote SCORM activities from one NovaLXP Moodle environment to another via AWS SSM.

This script is designed for cases like course 184 / section 844 where dev contains real
SCORM package activities and test still contains URL resources. It inspects the source
environment, reuses the already-uploaded SCORM package zips from Moodle's file pool, and
can recreate matching SCORM activities in the target environment using Moodle core APIs.

The default mode is dry-run. Use --apply to make changes.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ENV_INSTANCE_IDS = {
    "dev": "i-0cbdd881027b14e09",
    "test": "i-00c24ea634d4728ba",
    "production": "i-02bcf20804a48b781",
}

DEFAULT_PROFILE = "devops-070017892219-070017892219"
DEFAULT_REGION = "eu-west-2"
DEFAULT_COURSE_ID = 184
DEFAULT_SECTION_ID = 844


def run_command(command: list[str], *, expect_json: bool = False) -> object:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "Unknown command failure"
        raise RuntimeError(stderr)
    output = completed.stdout.strip()
    if expect_json:
        return json.loads(output) if output else {}
    return output


def send_ssm_commands(
    profile: str,
    region: str,
    instance_id: str,
    commands: list[str],
    comment: str,
    timeout_seconds: int = 600,
) -> dict:
    command_id = run_command(
        [
            "aws",
            "--profile",
            profile,
            "--region",
            region,
            "ssm",
            "send-command",
            "--instance-ids",
            instance_id,
            "--document-name",
            "AWS-RunShellScript",
            "--comment",
            comment,
            "--parameters",
            json.dumps({"commands": commands}),
            "--query",
            "Command.CommandId",
            "--output",
            "text",
        ]
    )

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = run_command(
            [
                "aws",
                "--profile",
                profile,
                "--region",
                region,
                "ssm",
                "get-command-invocation",
                "--command-id",
                str(command_id),
                "--instance-id",
                instance_id,
                "--output",
                "json",
            ],
            expect_json=True,
        )
        status = response["Status"]
        if status not in {"Pending", "InProgress", "Delayed"}:
            if status != "Success":
                message = response.get("StandardErrorContent") or response.get("StandardOutputContent") or status
                raise RuntimeError(message.strip())
            return response
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for SSM command {command_id}")


def php_single_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def build_php_script(body: str) -> str:
    return "\n".join(
        [
            "<?php",
            'define("CLI_SCRIPT", true);',
            'require_once("config.php");',
            "global $CFG, $DB, $USER;",
            "error_reporting(E_ALL);",
            "ini_set('display_errors', 'stderr');",
            body,
        ]
    )


def run_remote_php(
    profile: str,
    region: str,
    instance_id: str,
    comment: str,
    php_body: str,
    *,
    run_as_apache: bool = False,
) -> str:
    php_script = build_php_script(php_body)
    remote_path = "/tmp/codex_scorm_promotion.php"
    commands = [
        "set -e",
        f"cd /var/www/moodle/public",
        f"cat <<'PHP' > {remote_path}\n{php_script}\nPHP",
    ]
    if run_as_apache:
        commands.append(f"sudo -u apache /usr/bin/php {remote_path}")
    else:
        commands.append(f"/usr/bin/php {remote_path}")
    commands.append(f"rm -f {remote_path}")
    response = send_ssm_commands(profile, region, instance_id, commands, comment)
    return response.get("StandardOutputContent", "")


def fetch_source_section_plan(
    profile: str,
    region: str,
    instance_id: str,
    course_id: int,
    section_id: int,
) -> dict:
    php_body = f"""
require_once($CFG->dirroot . '/lib/filelib.php');
$courseid = {course_id};
$sectionid = {section_id};
$section = $DB->get_record('course_sections', ['id' => $sectionid, 'course' => $courseid], '*', MUST_EXIST);
$modulemap = [];
$sql = "SELECT cm.id AS cmid, cm.instance, cm.completion, cm.completionview, cm.completionpassgrade,
               cm.completiongradeitemnumber, cm.completionexpected,
               sc.*
          FROM {{course_modules}} cm
          JOIN {{modules}} m ON m.id = cm.module
          JOIN {{scorm}} sc ON sc.id = cm.instance
         WHERE cm.course = ? AND cm.section = ? AND m.name = 'scorm'
         ORDER BY cm.id";
$rows = $DB->get_records_sql($sql, [$courseid, $sectionid]);
$fs = get_file_storage();
foreach ($rows as $row) {{
    $context = $DB->get_record('context', ['contextlevel' => CONTEXT_MODULE, 'instanceid' => $row->cmid], '*', MUST_EXIST);
    $files = $fs->get_area_files($context->id, 'mod_scorm', 'package', 0, '', false);
    $package = reset($files);
    if (!$package) {{
        throw new moodle_exception('missingpackage', 'error', '', $row->name);
    }}
    $modulemap[] = [
        'name' => $row->name,
        'cmid' => (int)$row->cmid,
        'instance' => (int)$row->id,
        'course' => (int)$row->course,
        'sectionid' => (int)$sectionid,
        'sectionnum' => (int)$section->section,
        'completion' => (int)$row->completion,
        'completionview' => (int)$row->completionview,
        'completionpassgrade' => (int)$row->completionpassgrade,
        'completiongradeitemnumber' => $row->completiongradeitemnumber === null ? null : (int)$row->completiongradeitemnumber,
        'completionexpected' => (int)$row->completionexpected,
        'scormtype' => $row->scormtype,
        'reference' => $row->reference,
        'intro' => $row->intro,
        'introformat' => (int)$row->introformat,
        'version' => $row->version,
        'maxgrade' => (int)$row->maxgrade,
        'grademethod' => (int)$row->grademethod,
        'whatgrade' => (int)$row->whatgrade,
        'maxattempt' => (int)$row->maxattempt,
        'forcecompleted' => (int)$row->forcecompleted,
        'forcenewattempt' => (int)$row->forcenewattempt,
        'lastattemptlock' => (int)$row->lastattemptlock,
        'masteryoverride' => (int)$row->masteryoverride,
        'displayattemptstatus' => (int)$row->displayattemptstatus,
        'displaycoursestructure' => (int)$row->displaycoursestructure,
        'updatefreq' => (int)$row->updatefreq,
        'sha1hash' => $row->sha1hash,
        'revision' => (int)$row->revision,
        'skipview' => (int)$row->skipview,
        'hidebrowse' => (int)$row->hidebrowse,
        'hidetoc' => (int)$row->hidetoc,
        'nav' => (int)$row->nav,
        'navpositionleft' => (int)$row->navpositionleft,
        'navpositiontop' => (int)$row->navpositiontop,
        'auto' => (int)$row->auto,
        'popup' => (int)$row->popup,
        'width' => (int)$row->width,
        'height' => (int)$row->height,
        'timeopen' => (int)$row->timeopen,
        'timeclose' => (int)$row->timeclose,
        'completionstatusrequired' => $row->completionstatusrequired === null ? null : (int)$row->completionstatusrequired,
        'completionscorerequired' => $row->completionscorerequired === null ? null : (int)$row->completionscorerequired,
        'completionstatusallscos' => (int)$row->completionstatusallscos,
        'autocommit' => (int)$row->autocommit,
        'filename' => $package->get_filename(),
        'contenthash' => $package->get_contenthash(),
        'filepath' => $CFG->dataroot . '/filedir/' . substr($package->get_contenthash(), 0, 2) . '/' .
            substr($package->get_contenthash(), 2, 2) . '/' . $package->get_contenthash(),
    ];
}}
echo json_encode([
    'courseid' => $courseid,
    'sectionid' => (int)$section->id,
    'sectionnum' => (int)$section->section,
    'sectionname' => $section->name,
    'modules' => array_values($modulemap),
], JSON_PRETTY_PRINT);
"""
    output = run_remote_php(profile, region, instance_id, "Inspect source SCORM section", php_body)
    return json.loads(output)


def fetch_target_section_state(
    profile: str,
    region: str,
    instance_id: str,
    course_id: int,
    section_id: int,
) -> dict:
    php_body = f"""
$courseid = {course_id};
$sectionid = {section_id};
$section = $DB->get_record('course_sections', ['id' => $sectionid, 'course' => $courseid], '*', MUST_EXIST);
$sql = "SELECT cm.id AS cmid, cm.instance, cm.completion, cm.completionview, cm.visible,
               m.name AS modname, u.name AS urlname, u.externalurl, sc.name AS scormname
          FROM {{course_modules}} cm
          JOIN {{modules}} m ON m.id = cm.module
     LEFT JOIN {{url}} u ON u.id = cm.instance AND m.name = 'url'
     LEFT JOIN {{scorm}} sc ON sc.id = cm.instance AND m.name = 'scorm'
         WHERE cm.course = ? AND cm.section = ?
         ORDER BY cm.id";
$rows = $DB->get_records_sql($sql, [$courseid, $sectionid]);
$modules = [];
foreach ($rows as $row) {{
    $modules[] = [
        'cmid' => (int)$row->cmid,
        'modname' => $row->modname,
        'name' => $row->scormname ?: $row->urlname ?: '',
        'externalurl' => $row->externalurl ?: '',
        'completion' => (int)$row->completion,
        'completionview' => (int)$row->completionview,
        'visible' => (int)$row->visible,
    ];
}}
echo json_encode([
    'courseid' => $courseid,
    'sectionid' => (int)$section->id,
    'sectionnum' => (int)$section->section,
    'sectionname' => $section->name,
    'modules' => $modules,
], JSON_PRETTY_PRINT);
"""
    output = run_remote_php(profile, region, instance_id, "Inspect target section state", php_body)
    return json.loads(output)


def fetch_package_bytes(
    profile: str,
    region: str,
    instance_id: str,
    filepath: str,
    filename: str,
) -> bytes:
    escaped = filepath.replace("'", "'\"'\"'")
    commands = [
        "set -e",
        f"test -f '{escaped}'",
        f"base64 < '{escaped}' | tr -d '\\n'",
    ]
    response = send_ssm_commands(profile, region, instance_id, commands, f"Fetch package {filename}")
    return base64.b64decode(response.get("StandardOutputContent", "").strip())


def chunk_string(value: str, size: int = 3000) -> list[str]:
    return [value[i : i + size] for i in range(0, len(value), size)]


def stage_file_on_target(
    profile: str,
    region: str,
    instance_id: str,
    filename: str,
    payload: bytes,
) -> str:
    encoded = base64.b64encode(payload).decode("ascii")
    remote_b64 = f"/tmp/{filename}.b64"
    remote_zip = f"/tmp/{filename}"
    commands = ["set -e", f": > {remote_b64}"]
    for chunk in chunk_string(encoded):
        commands.append(f"printf '%s' {php_single_quote(chunk)} >> {remote_b64}")
    commands.append(f"base64 -d {remote_b64} > {remote_zip}")
    commands.append(f"rm -f {remote_b64}")
    send_ssm_commands(profile, region, instance_id, commands, f"Stage package {filename} on target")
    return remote_zip


def create_or_reuse_target_scorms(
    profile: str,
    region: str,
    instance_id: str,
    course_id: int,
    section_id: int,
    module_specs: list[dict],
    hide_replaced_urls: bool,
) -> dict:
    spec_json = json.dumps(module_specs, separators=(",", ":"))
    php_body = f"""
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->libdir . '/filelib.php');
require_once($CFG->dirroot . '/mod/scorm/lib.php');
require_once($CFG->dirroot . '/mod/scorm/locallib.php');
require_once($CFG->libdir . '/completionlib.php');

$courseid = {course_id};
$sectionid = {section_id};
$hideurls = {1 if hide_replaced_urls else 0};
$specs = json_decode({php_single_quote(spec_json)}, true, 512, JSON_THROW_ON_ERROR);
$course = get_course($courseid);
$section = $DB->get_record('course_sections', ['id' => $sectionid, 'course' => $courseid], '*', MUST_EXIST);
$admin = get_admin();
$USER = $admin;
\\core\\session\\manager::set_user($USER);

$moduleid = $DB->get_field('modules', 'id', ['name' => 'scorm'], MUST_EXIST);
$results = [];
foreach ($specs as $spec) {{
    $existing = $DB->get_record_sql(
        "SELECT cm.id AS cmid, sc.id AS scormid
           FROM {{course_modules}} cm
           JOIN {{modules}} m ON m.id = cm.module
           JOIN {{scorm}} sc ON sc.id = cm.instance
          WHERE cm.course = ? AND cm.section = ? AND m.name = 'scorm' AND sc.name = ?",
        [$courseid, $sectionid, $spec['name']]
    );
    if ($existing) {{
        $results[] = [
            'name' => $spec['name'],
            'action' => 'reused',
            'cmid' => (int)$existing->cmid,
            'scormid' => (int)$existing->scormid,
        ];
        continue;
    }}

    $draftid = file_get_unused_draft_itemid();
    $usercontext = context_user::instance($USER->id);
    $fs = get_file_storage();
    $fs->create_file_from_pathname([
        'contextid' => $usercontext->id,
        'component' => 'user',
        'filearea' => 'draft',
        'itemid' => $draftid,
        'filepath' => '/',
        'filename' => basename($spec['staged_package']),
        'userid' => $USER->id,
    ], $spec['staged_package']);

    $moduleinfo = (object)[
        'course' => $courseid,
        'module' => (int)$moduleid,
        'modulename' => 'scorm',
        'section' => (int)$section->section,
        'visible' => 1,
        'visibleoncoursepage' => 1,
        'groupmode' => 0,
        'groupingid' => 0,
        'name' => $spec['name'],
        'intro' => $spec['intro'],
        'introformat' => (int)$spec['introformat'],
        'completion' => (int)$spec['completion'],
        'completionview' => (int)$spec['completionview'],
        'completionpassgrade' => (int)$spec['completionpassgrade'],
        'completiongradeitemnumber' => $spec['completiongradeitemnumber'],
        'completionexpected' => (int)$spec['completionexpected'],
        'scormtype' => $spec['scormtype'],
        'packagefile' => $draftid,
        'maxgrade' => (int)$spec['maxgrade'],
        'grademethod' => (int)$spec['grademethod'],
        'whatgrade' => (int)$spec['whatgrade'],
        'maxattempt' => (int)$spec['maxattempt'],
        'forcecompleted' => (int)$spec['forcecompleted'],
        'forcenewattempt' => (int)$spec['forcenewattempt'],
        'lastattemptlock' => (int)$spec['lastattemptlock'],
        'masteryoverride' => (int)$spec['masteryoverride'],
        'displayattemptstatus' => (int)$spec['displayattemptstatus'],
        'displaycoursestructure' => (int)$spec['displaycoursestructure'],
        'updatefreq' => (int)$spec['updatefreq'],
        'skipview' => (int)$spec['skipview'],
        'hidebrowse' => (int)$spec['hidebrowse'],
        'hidetoc' => (int)$spec['hidetoc'],
        'nav' => (int)$spec['nav'],
        'navpositionleft' => (int)$spec['navpositionleft'],
        'navpositiontop' => (int)$spec['navpositiontop'],
        'auto' => (int)$spec['auto'],
        'popup' => (int)$spec['popup'],
        'width' => (int)$spec['width'],
        'height' => (int)$spec['height'],
        'timeopen' => (int)$spec['timeopen'],
        'timeclose' => (int)$spec['timeclose'],
        'completionstatusrequired' => $spec['completionstatusrequired'],
        'completionscorerequired' => $spec['completionscorerequired'],
        'completionstatusallscos' => (int)$spec['completionstatusallscos'],
        'autocommit' => (int)$spec['autocommit'],
    ];

    $created = add_moduleinfo($moduleinfo, $course);
    $results[] = [
        'name' => $spec['name'],
        'action' => 'created',
        'cmid' => (int)$created->coursemodule,
        'scormid' => (int)$created->instance,
    ];
}}

if ($hideurls) {{
    foreach ($specs as $spec) {{
        $urlcm = $DB->get_record_sql(
            "SELECT cm.id
               FROM {{course_modules}} cm
               JOIN {{modules}} m ON m.id = cm.module
               JOIN {{url}} u ON u.id = cm.instance
              WHERE cm.course = ? AND cm.section = ? AND m.name = 'url' AND u.name = ?",
            [$courseid, $sectionid, $spec['name']]
        );
        if ($urlcm) {{
            set_coursemodule_visible($urlcm->id, 0);
            $results[] = [
                'name' => $spec['name'],
                'action' => 'hid_url',
                'cmid' => (int)$urlcm->id,
            ];
        }}
    }}
}}

rebuild_course_cache($courseid, true);
echo json_encode(['results' => $results], JSON_PRETTY_PRINT);
"""
    output = run_remote_php(
        profile,
        region,
        instance_id,
        "Create target SCORM activities",
        php_body,
        run_as_apache=False,
    )
    return json.loads(output)


def cleanup_target_staged_files(
    profile: str,
    region: str,
    instance_id: str,
    staged_paths: list[str],
) -> None:
    if not staged_paths:
        return
    commands = ["set -e", "rm -f " + " ".join(staged_paths)]
    send_ssm_commands(profile, region, instance_id, commands, "Cleanup staged SCORM packages")


def build_plan(source_plan: dict, target_state: dict) -> dict:
    target_by_name = {(module["modname"], module["name"]): module for module in target_state["modules"]}
    creates: list[dict] = []
    existing: list[dict] = []
    url_replacements: list[dict] = []

    for module in source_plan["modules"]:
        scorm_key = ("scorm", module["name"])
        url_key = ("url", module["name"])
        if scorm_key in target_by_name:
            existing.append({"name": module["name"], "target": target_by_name[scorm_key]})
        else:
            creates.append({"name": module["name"], "source_cmid": module["cmid"], "filename": module["filename"]})
        if url_key in target_by_name:
            url_replacements.append({"name": module["name"], "target": target_by_name[url_key]})

    return {
        "source": source_plan,
        "target": target_state,
        "creates": creates,
        "already_present": existing,
        "matching_urls": url_replacements,
    }


def print_plan(plan: dict) -> None:
    print(f"Source section: {plan['source']['sectionname']} (course {plan['source']['courseid']}, section {plan['source']['sectionid']})")
    print(f"Target section: {plan['target']['sectionname']} (course {plan['target']['courseid']}, section {plan['target']['sectionid']})")
    print()
    print("Source SCORM activities:")
    for module in plan["source"]["modules"]:
        print(f"- {module['name']} | cmid {module['cmid']} | {module['filename']}")
    print()
    print("Target section modules:")
    for module in plan["target"]["modules"]:
        suffix = f" -> {module['externalurl']}" if module["externalurl"] else ""
        print(f"- {module['modname']} | {module['name']} | cmid {module['cmid']}{suffix}")
    print()
    print("Planned SCORM creates:")
    if not plan["creates"]:
        print("- None")
    for item in plan["creates"]:
        print(f"- {item['name']} from dev cmid {item['source_cmid']} ({item['filename']})")
    print()
    print("Matching URL resources in target:")
    if not plan["matching_urls"]:
        print("- None")
    for item in plan["matching_urls"]:
        print(f"- {item['name']} | target cmid {item['target']['cmid']} | {item['target']['externalurl']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--source-env", default="dev", choices=sorted(ENV_INSTANCE_IDS))
    parser.add_argument("--target-env", default="test", choices=sorted(ENV_INSTANCE_IDS))
    parser.add_argument("--course-id", type=int, default=DEFAULT_COURSE_ID)
    parser.add_argument("--section-id", type=int, default=DEFAULT_SECTION_ID)
    parser.add_argument("--apply", action="store_true", help="Create the missing SCORM activities in the target environment.")
    parser.add_argument(
        "--hide-replaced-urls",
        action="store_true",
        help="Hide matching URL resources in the target section after SCORM creation.",
    )
    parser.add_argument(
        "--plan-output",
        help="Optional path to write the computed promotion plan as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_instance = ENV_INSTANCE_IDS[args.source_env]
    target_instance = ENV_INSTANCE_IDS[args.target_env]

    source_plan = fetch_source_section_plan(
        args.profile,
        args.region,
        source_instance,
        args.course_id,
        args.section_id,
    )
    target_state = fetch_target_section_state(
        args.profile,
        args.region,
        target_instance,
        args.course_id,
        args.section_id,
    )
    plan = build_plan(source_plan, target_state)

    if args.plan_output:
        Path(args.plan_output).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    print_plan(plan)

    if not args.apply:
        return 0

    if not plan["creates"]:
        print("\nNo missing SCORM activities found in target; nothing to create.")
        return 0

    staged_paths: list[str] = []
    staged_specs: list[dict] = []
    try:
        for module in source_plan["modules"]:
            if not any(item["name"] == module["name"] for item in plan["creates"]):
                continue
            package_bytes = fetch_package_bytes(
                args.profile,
                args.region,
                source_instance,
                module["filepath"],
                module["filename"],
            )
            staged_path = stage_file_on_target(
                args.profile,
                args.region,
                target_instance,
                module["filename"],
                package_bytes,
            )
            staged_paths.append(staged_path)
            spec = dict(module)
            spec["staged_package"] = staged_path
            spec.pop("filepath", None)
            staged_specs.append(spec)

        result = create_or_reuse_target_scorms(
            args.profile,
            args.region,
            target_instance,
            args.course_id,
            args.section_id,
            staged_specs,
            args.hide_replaced_urls,
        )
        print("\nApply results:")
        print(json.dumps(result, indent=2))
    finally:
        cleanup_target_staged_files(args.profile, args.region, target_instance, staged_paths)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
