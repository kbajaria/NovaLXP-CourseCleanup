# Test Deployment Record

- Date (UTC): 2026-03-08
- Environment: test
- Host: `i-00c24ea634d4728ba` (`test-moodle-app`)
- Moodle wwwroot: `https://test.novalxp.co.uk`
- Theme: `Edutor`

## Change applied
Deployed the first-time hackathon primer pathway to test and aligned the test environment with the dev rollout:

- created the five pathway courses in test
- created and assigned the `Hackathon Primer` category
- updated the front-page featured carousel so block 2 points to the pathway hub course
- updated the default dashboard featured HTML block and reset student dashboards
- configured the pathway hub as a rollup completion course
- created the course completion badge for course 1
- applied the crop-safe `BG` course image to all five courses

## Test course ids
- `202` `Hackathon Pathway 1 of 4: AI Hackathon Orientation`
- `203` `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
- `204` `Hackathon Pathway 3 of 4: Agent Foundations`
- `205` `Hackathon Pathway 4 of 4: Data and Integration Foundations`
- `206` `Start Here: First-Time Hackathon Pathway`

## Category and surfacing
- Created category:
  - id `15`
  - name `Hackathon Primer`
- Moved courses `202` to `206` into category `15`
- Updated `theme_edutor` Pane 1 block 2:
  - title `Start Here: First-Time Hackathon Pathway`
  - url `/course/view.php?id=206`
  - image `/course_images/ai.png`
- Updated dashboard HTML block id `93`
- Reset student dashboards:
  - `73`

## Completion and badge configuration
- Training courses `202` to `205` each have:
  - `pagecount = 6`
  - `quizcount = 1`
  - activity-based completion criterion (`criteriatype = 4`)
- Overview course `206` has:
  - `pagecount = 1`
  - `quizcount = 0`
  - `enablecompletion = 1`
  - four course dependency criteria (`criteriatype = 8`) for `202`, `203`, `204`, and `205`
- Created course badge for course `202`:
  - badge id `2`
  - name `AI Hackathon Orientation Completion Badge`
  - status `1` (`BADGE_STATUS_ACTIVE`)
  - course criteria param `course_202 = 202`

## Course images
- Applied the crop-safe shared-media asset:
  - `hackathon-first-timers-learning-path/shared-media/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
- Uploaded into each course `overviewfiles` area for courses `202` to `206`

## Verification summary
- `202` to `206` are visible in test and point to category `15`
- Pane 1 block 2 now points to course `206`
- Dashboard featured HTML block contains the primer CTA and the existing Google Workspaces CTA
- Course `202` has an active completion badge
- Course `206` now has the expected rollup completion criteria
- Course image pluginfiles were created for all five courses

## Deployment method
- Initial course creation:
  - `python3 scripts/course_factory/deploy_authored_course.py hackathon-first-timers-learning-path --moodle-base-url https://test.novalxp.co.uk --moodle-token ... --category-id 5 --pass-mark 80`
- Rollup completion sync:
  - `python3 scripts/course_factory/sync_learning_pathway_via_ssm.py hackathon-first-timers-learning-path --instance-id i-00c24ea634d4728ba --region eu-west-2`
- Additional Moodle-side updates executed with host-side PHP over AWS SSM

## Notes
- The initial clean deployment created the overview course without the rollup completion dependencies; that was corrected immediately afterward using the sync utility.
- The original badge configuration in this deployment targeted course `202`. That was later corrected by `pathway-badge-rollup-fix-2026-03-08.md` so the active badge now awards from hub course `206`.
- No manual browser QA was performed after the final test deployment.
