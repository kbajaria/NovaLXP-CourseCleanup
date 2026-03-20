#!/usr/bin/env python3
"""Sync authored learning-path content into an existing Moodle dev deployment via SSM."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import time
from pathlib import Path
import html
import re


def render_inline(text: str) -> str:
    text = html.escape(text, quote=True)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<![\">])(https?://[^\s<]+)", r'<a href="\1">\1</a>', text)
    return text


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            content = " ".join(part.strip() for part in paragraph if part.strip())
            blocks.append(f"<p>{render_inline(content)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            blocks.append(f"<h{level}>{render_inline(heading_match.group(2).strip())}</h{level}>")
            continue

        list_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if list_match:
            flush_paragraph()
            list_items.append(list_match.group(1).strip())
            continue

        ordered_match = re.match(r"^\d+\)\s+(.*)$", stripped) or re.match(r"^\d+\.\s+(.*)$", stripped)
        if ordered_match:
            flush_paragraph()
            list_items.append(ordered_match.group(1).strip())
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "<div>" + "".join(blocks) + "</div>"


def build_payload(path_dir: Path) -> dict:
    manifest = json.loads((path_dir / "learning-path.json").read_text(encoding="utf-8"))
    payload = {
        "learning_path": manifest["learning_path"],
        "courses": [],
    }
    for course in manifest["courses"]:
        course_dir = path_dir / course["slug"]
        course_json = json.loads((course_dir / "course.json").read_text(encoding="utf-8"))
        sections = []
        for section in course_json["sections"]:
            source_path = course_dir / section["source"]
            sections.append(
                {
                    "title": section["title"],
                    "html": markdown_to_html(source_path.read_text(encoding="utf-8")),
                }
            )
        payload["courses"].append(
            {
                "order": course["order"],
                "slug": course["slug"],
                "shortname": course_json["course"]["shortname"],
                "fullname": course_json["course"]["fullname"],
                "summary": course_json["course"]["summary"],
                "sections": sections,
            }
        )
    return payload


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path_dir")
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--moodle-root", default="/var/www/moodle/public")
    args = parser.parse_args()

    payload = build_payload(Path(args.path_dir).resolve())
    payload_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

    remote_template = """cd __MOODLE_ROOT__ && sudo -u apache /usr/bin/php -r '
define(\"CLI_SCRIPT\", true);
require_once(\"config.php\");
require_once($CFG->libdir . \"/completionlib.php\");
$payload = json_decode(base64_decode(\"__PAYLOAD_B64__\"), true);
if (!$payload) {{
    throw new Exception(\"Failed to decode payload\");
}}
$results = array();
$resolved = array();
foreach ($payload[\"courses\"] as $coursecfg) {{
    $course = $DB->get_record(\"course\", array(\"shortname\" => $coursecfg[\"shortname\"]), \"*\", MUST_EXIST);
    $course->fullname = $coursecfg[\"fullname\"];
    $course->summary = $coursecfg[\"summary\"];
    $course->enablecompletion = 1;
    $DB->update_record(\"course\", $course);
    $pages = $DB->get_records_sql(
        \"SELECT p.* FROM {page} p
          JOIN {course_modules} cm ON cm.instance = p.id
          JOIN {modules} m ON m.id = cm.module
         WHERE cm.course = ? AND m.name = ?
         ORDER BY p.id ASC\",
        array($course->id, \"page\")
    );
    $pages = array_values($pages);
    $sections = $DB->get_records_sql(
        \"SELECT * FROM {course_sections}
         WHERE course = ? AND section > 0
         ORDER BY section ASC\",
        array($course->id)
    );
    $sections = array_values($sections);
    if (count($pages) !== count($coursecfg[\"sections\"])) {{
        throw new Exception(\"Page count mismatch for \" . $coursecfg[\"shortname\"]);
    }}
    foreach ($coursecfg[\"sections\"] as $index => $sectioncfg) {{
        $page = $pages[$index];
        $page->name = $sectioncfg[\"title\"];
        $page->content = $sectioncfg[\"html\"];
        $page->contentformat = FORMAT_HTML;
        $DB->update_record(\"page\", $page);
        if (isset($sections[$index])) {{
            $sectionrow = $sections[$index];
            $sectionrow->name = $sectioncfg[\"title\"];
            $DB->update_record(\"course_sections\", $sectionrow);
        }}
    }}
    $resolved[] = array(
        \"order\" => (int)$coursecfg[\"order\"],
        \"id\" => (int)$course->id,
        \"fullname\" => $course->fullname,
        \"shortname\" => $course->shortname,
        \"url\" => $CFG->wwwroot . \"/course/view.php?id=\" . $course->id
    );
}}
usort($resolved, function($a, $b) {{ return $a[\"order\"] <=> $b[\"order\"]; }});
$overview = $DB->get_record(\"course\", array(\"shortname\" => $payload[\"learning_path\"][\"id\"]), \"*\", MUST_EXIST);
$overview->fullname = $payload[\"learning_path\"][\"title\"];
$overview->summary = $payload[\"learning_path\"][\"summary\"];
$overview->enablecompletion = 1;
$DB->update_record(\"course\", $overview);

$overviewitems = \"\";
foreach ($resolved as $item) {{
    $overviewitems .= \"<li><strong>Course {$item[\"order\"]} of 4:</strong> <a href=\\\"\" . s($item[\"url\"]) . \"\\\">\" . format_string($item[\"fullname\"], true) . \"</a></li>\";
}}
$overviewhtml = \"<div>\";
$overviewhtml .= \"<h1>Start Here</h1>\";
$overviewhtml .= \"<p>This hub course is the entry point for the First-Time Hackathon Pathway.</p>\";
$overviewhtml .= \"<p>Take the four courses in order. Each one builds on the previous course. The pathway is complete when all four course quizzes are complete.</p>\";
$overviewhtml .= \"<ol>\" . $overviewitems . \"</ol>\";
$overviewhtml .= \"<h2>How pathway completion works</h2>\";
$overviewhtml .= \"<p>This course will mark complete after you complete all four pathway courses.</p>\";
$overviewhtml .= \"</div>\";

$page = $DB->get_record_sql(
            \"SELECT p.* FROM {page} p
      JOIN {course_modules} cm ON cm.instance = p.id
      JOIN {modules} m ON m.id = cm.module
     WHERE cm.course = ? AND m.name = ? LIMIT 1\",
    array($overview->id, \"page\"),
    MUST_EXIST
);
$page->name = \"Start Here: Pathway Overview\";
$page->content = $overviewhtml;
$page->contentformat = FORMAT_HTML;
$DB->update_record(\"page\", $page);

$section = $DB->get_record_sql(
    \"SELECT * FROM {course_sections} WHERE course = ? AND section > 0 ORDER BY section ASC LIMIT 1\",
    array($overview->id)
);
if ($section) {{
    $section->name = \"Start here\";
    $DB->update_record(\"course_sections\", $section);
}}

$DB->delete_records(\"course_completion_crit_compl\", array(\"course\" => $overview->id));
$DB->delete_records(\"course_completion_criteria\", array(\"course\" => $overview->id));
foreach ($resolved as $item) {{
    $criterion = (object) array(
        \"course\" => $overview->id,
        \"criteriatype\" => COMPLETION_CRITERIA_TYPE_COURSE,
        \"courseinstance\" => $item[\"id\"]
    );
    $DB->insert_record(\"course_completion_criteria\", $criterion);
}}

rebuild_course_cache($overview->id, true);
echo json_encode(array(\"overviewcourse\" => $overview->id, \"dependencies\" => $resolved));
'"""
    remote = remote_template.replace("__MOODLE_ROOT__", args.moodle_root).replace("__PAYLOAD_B64__", payload_b64)

    status, stdout, stderr = run_ssm(args.instance_id, args.region, remote)
    print(status)
    print(stdout)
    if stderr:
        print(stderr)
    return 0 if status == "Success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
