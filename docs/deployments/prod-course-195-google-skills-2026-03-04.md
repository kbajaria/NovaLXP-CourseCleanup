# Production Deployment Record

- Date (UTC): 2026-03-04T19:21:31Z
- Environment: production
- Host: `i-02bcf20804a48b781` (`prod-moodle-app`)
- Moodle wwwroot verified: `https://learn.novalxp.co.uk`
- Course id: `195`
- Source section reference: `course/section.php?id=918`

## Change applied
Added a new final section in course 195:
- New section id: `942`
- New section number: `11` (last section)
- Section name: `External Google Skills Course`

Added learner manual completion activity in new section:
- Activity type: `page`
- Course module id (`cmid`): `988`
- Page instance id: `527`
- Activity name: `Mark this section complete`
- Completion tracking: `manual` (`completion=1`)

## Summary content
- External launch URL: `https://www.skills.google/course_templates/779`
- Internal return URL (relative): `/course/section.php?id=918`
- Launch control uses `btn btn-primary` class.

## Verification checks
- Section exists and is visible.
- Section summary stored as HTML (`summaryformat=1`).
- Completion page exists in section `942` and is visible.
- Course max section is `11` confirming new section is at end.

## Execution method
- AWS SSM command execution (`AWS-RunShellScript`) as `apache` user for Moodle API script.
- Script was idempotent for section/activity creation checks.
