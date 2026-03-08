#!/usr/bin/env python3
"""Deploy authored NovaLXP course folders to Moodle via web services."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
        line = raw_line.rstrip()
        stripped = line.strip()

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


def moodle_call(base_url: str, token: str, wsfunction: str, params: dict) -> object:
    form = {
        "wstoken": token,
        "wsfunction": wsfunction,
        "moodlewsrestformat": "json",
    }
    for key, value in params.items():
        if value is None or value == "":
            continue
        form[key] = str(value)

    body = urllib.parse.urlencode(form).encode("utf-8")
    url = base_url.rstrip("/") + "/webservice/rest/server.php"
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read().decode("utf-8")

    parsed = json.loads(payload)
    if isinstance(parsed, dict) and parsed.get("exception"):
        raise RuntimeError(f"{wsfunction} failed: {parsed.get('message') or parsed.get('exception')}")
    return parsed


def deploy_course(course_dir: Path, base_url: str, token: str, category_id: int, pass_mark: int) -> dict:
    manifest = load_json(course_dir / "course.json")
    course_meta = manifest["course"]
    quiz_config = load_json(course_dir / manifest["quiz"]["config"])
    quiz_name = quiz_config["quiz_name"]
    questionbank_path = course_dir / manifest["quiz"]["questionbank_gift"]
    questionbank = questionbank_path.read_text(encoding="utf-8")

    create_result = moodle_call(
        base_url,
        token,
        "local_novalxpapi_create_course",
        {
            "fullname": course_meta["fullname"],
            "shortname": course_meta["shortname"],
            "categoryid": category_id,
            "summary": course_meta["summary"],
        },
    )
    course_id = int(create_result)

    for section in manifest["sections"]:
        section_id = int(
            moodle_call(
                base_url,
                token,
                "local_novalxpapi_add_section",
                {"courseid": course_id, "name": section["title"]},
            )
        )
        content = (course_dir / section["source"]).read_text(encoding="utf-8")
        moodle_call(
            base_url,
            token,
            "local_novalxpapi_add_page",
            {
                "courseid": course_id,
                "section": section_id,
                "title": section["title"],
                "content": markdown_to_html(content),
                "visible": 1,
            },
        )

    quiz_section_id = int(
        moodle_call(
            base_url,
            token,
            "local_novalxpapi_add_section",
            {"courseid": course_id, "name": quiz_name},
        )
    )
    quiz_result = moodle_call(
        base_url,
        token,
        "local_novalxpapi_create_quiz",
        {
            "courseid": course_id,
            "section": quiz_section_id,
            "quizname": quiz_name,
            "intro": "<p>Pass this quiz to complete the course.</p>",
            "visible": 1,
            "gifttext": questionbank,
            "sectionname": quiz_name,
        },
    )
    quiz_id = int(quiz_result.get("quizid", 0))
    quiz_cmid = int(quiz_result.get("cmid", 0))

    moodle_call(
        base_url,
        token,
        "local_novalxpapi_apply_quiz_completion_guardrails",
        {
            "courseid": course_id,
            "quizcmid": quiz_cmid,
            "quizid": quiz_id,
            "passmark": pass_mark,
            "shuffleanswers": 1,
        },
    )

    return {
        "course_id": course_id,
        "shortname": course_meta["shortname"],
        "fullname": course_meta["fullname"],
        "url": base_url.rstrip("/") + f"/course/view.php?id={course_id}",
        "quiz_id": quiz_id,
        "quiz_cmid": quiz_cmid,
    }


def build_path_overview_html(title: str, summary: str, deployed_courses: list[dict]) -> str:
    items = "".join(
        f'<li><strong>{html.escape(course["fullname"])}</strong> '
        f'- <a href="{html.escape(course["url"], quote=True)}">Open course</a></li>'
        for course in deployed_courses
    )
    return (
        "<div>"
        f"<h1>{html.escape(title)}</h1>"
        f"<p>{html.escape(summary)}</p>"
        "<h2>Recommended order</h2>"
        f"<ol>{items}</ol>"
        "<p>Complete each course quiz with a passing score before moving to the next course.</p>"
        "</div>"
    )


def deploy_learning_path(path_dir: Path, base_url: str, token: str, category_id: int, pass_mark: int) -> list[dict]:
    manifest = load_json(path_dir / "learning-path.json")
    deployed: list[dict] = []

    for course in manifest["courses"]:
        deployed.append(
            deploy_course(path_dir / course["slug"], base_url, token, category_id, pass_mark)
        )

    path_meta = manifest["learning_path"]
    overview_title = path_meta["title"]
    overview_shortname = path_meta["id"]
    overview_summary = path_meta["summary"]
    overview_course_id = int(
        moodle_call(
            base_url,
            token,
            "local_novalxpapi_create_course",
            {
                "fullname": overview_title,
                "shortname": overview_shortname,
                "categoryid": category_id,
                "summary": overview_summary,
            },
        )
    )
    overview_section_id = int(
        moodle_call(
            base_url,
            token,
            "local_novalxpapi_add_section",
            {"courseid": overview_course_id, "name": "Learning path overview"},
        )
    )
    moodle_call(
        base_url,
        token,
        "local_novalxpapi_add_page",
        {
            "courseid": overview_course_id,
            "section": overview_section_id,
            "title": "Learning path overview",
            "content": build_path_overview_html(overview_title, overview_summary, deployed),
            "visible": 1,
        },
    )

    deployed.append(
        {
            "course_id": overview_course_id,
            "shortname": overview_shortname,
            "fullname": overview_title,
            "url": base_url.rstrip("/") + f"/course/view.php?id={overview_course_id}",
            "quiz_id": 0,
            "quiz_cmid": 0,
            "is_overview": True,
        }
    )
    return deployed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path_dir", help="Path to the learning-path directory")
    parser.add_argument("--moodle-base-url", default=os.environ.get("MOODLE_BASE_URL", ""))
    parser.add_argument("--moodle-token", default=os.environ.get("MOODLE_TOKEN", ""))
    parser.add_argument("--category-id", type=int, default=5)
    parser.add_argument("--pass-mark", type=int, default=80)
    args = parser.parse_args()

    if not args.moodle_base_url or not args.moodle_token:
        print("MOODLE_BASE_URL and MOODLE_TOKEN are required", file=sys.stderr)
        return 2

    path_dir = Path(args.path_dir).resolve()
    deployed = deploy_learning_path(path_dir, args.moodle_base_url, args.moodle_token, args.category_id, args.pass_mark)
    print(json.dumps({"deployed": deployed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
