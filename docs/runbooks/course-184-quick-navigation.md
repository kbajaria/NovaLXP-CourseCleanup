# Course 184 Quick Navigation

This runbook captures the repo-backed artifacts needed to recreate or modify the custom navigation labels used throughout course `184` (`Finova Onboarding Programme`).

## Stored artifacts

- Manifest: `templates/course-184-quick-navigation.json`
- Rendered HTML snippet: `templates/course-184-quick-navigation.html`
- Apply script: `scripts/course_factory/apply_course_navigation_via_ssm.py`

The live feature is implemented as repeated Moodle `Label` activities whose names start with `Quick Navigation`. The labels are stored in the course itself, not in the `course_sections.summary` field.

## Current shape

- Course ID: `184`
- Matching label name prefix: `Quick Navigation`
- Expected repeated label count: `13`
- Link policy: use relative internal links such as `/course/view.php?id=184` and `/course/section.php?id=<sectionid>`

## How to modify it

1. Edit `templates/course-184-quick-navigation.json`.
2. Regenerate the HTML artifact:

```bash
python3 scripts/course_factory/apply_course_navigation_via_ssm.py \
  templates/course-184-quick-navigation.json \
  --render-output templates/course-184-quick-navigation.html
```

3. Review the rendered HTML in `templates/course-184-quick-navigation.html`.
4. Apply to an environment:

```bash
python3 scripts/course_factory/apply_course_navigation_via_ssm.py \
  templates/course-184-quick-navigation.json \
  --env dev \
  --apply
```

5. Validate in Moodle, then repeat for `test` and `production`.

## Environment application examples

```bash
python3 scripts/course_factory/apply_course_navigation_via_ssm.py \
  templates/course-184-quick-navigation.json \
  --env test \
  --apply
```

```bash
python3 scripts/course_factory/apply_course_navigation_via_ssm.py \
  templates/course-184-quick-navigation.json \
  --env production \
  --apply
```

If needed, you can bypass target-group discovery and point to a specific EC2 instance:

```bash
python3 scripts/course_factory/apply_course_navigation_via_ssm.py \
  templates/course-184-quick-navigation.json \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --apply
```

## Notes

- The section IDs currently referenced in the manifest are environment-consistent as of `2026-03-08`.
- If section IDs ever change, update only the manifest and regenerate/reapply.
- The script updates every matching `Quick Navigation%` label in the target course and rebuilds the Moodle course cache afterward.
