# Production Deployment Record

- Date (UTC): 2026-03-08
- Environment: production
- Host: `i-02bcf20804a48b781` (`prod-moodle-app`)
- Moodle wwwroot: `https://learn.novalxp.co.uk`
- Theme: `Edutor`

## Change applied
Deployed the first-time hackathon primer pathway to production and aligned production to the same learner-facing pattern now used in dev and test:

- created the five pathway courses in production
- created and assigned the `Hackathon Primer` category
- updated the front-page featured carousel so block 2 points to the pathway hub course
- updated the default dashboard featured HTML block and reset student dashboards
- configured the pathway hub as a rollup completion course
- created the course completion badge for course 1
- applied the crop-safe `BG` course image to all five courses

## Production course ids
- `207` `Hackathon Pathway 1 of 4: AI Hackathon Orientation`
- `208` `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
- `209` `Hackathon Pathway 3 of 4: Agent Foundations`
- `210` `Hackathon Pathway 4 of 4: Data and Integration Foundations`
- `211` `Start Here: First-Time Hackathon Pathway`

## Category and surfacing
- Created category:
  - id `15`
  - name `Hackathon Primer`
- Moved courses `207` to `211` into category `15`
- Updated `theme_edutor` Pane 1 block 2:
  - title `Start Here: First-Time Hackathon Pathway`
  - url `/course/view.php?id=211`
  - image `/course_images/ai.png`
- Updated dashboard HTML block id `93`
- Reset student dashboards:
  - `73`

## Completion and badge configuration
- Training courses `207` to `210` each have:
  - `pagecount = 6`
  - `quizcount = 1`
  - activity-based completion criterion (`criteriatype = 4`)
- Overview course `211` has:
  - `pagecount = 1`
  - `quizcount = 0`
  - `enablecompletion = 1`
  - four course dependency criteria (`criteriatype = 8`) for `207`, `208`, `209`, and `210`
- Created course badge for course `207`:
  - badge id `2`
  - name `AI Hackathon Orientation Completion Badge`
  - status `1` (`BADGE_STATUS_ACTIVE`)
  - course-scoped to `207`

## Course images
- Applied the crop-safe shared-media asset:
  - `hackathon-first-timers-learning-path/shared-media/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
- Uploaded into each course `overviewfiles` area for courses `207` to `211`

## Verification summary
- `207` to `211` are visible in production and point to category `15`
- Pane 1 block 2 now points to course `211`
- Course `211` now has the expected rollup completion criteria
- Course `207` has an active completion badge
- Course image pluginfiles were created for all five courses

## Deployment method
- Initial course creation:
  - `python3 scripts/course_factory/deploy_authored_course.py hackathon-first-timers-learning-path --moodle-base-url https://learn.novalxp.co.uk --moodle-token ... --category-id 5 --pass-mark 80`
- Rollup completion sync:
  - `python3 scripts/course_factory/sync_learning_pathway_via_ssm.py hackathon-first-timers-learning-path --instance-id i-02bcf20804a48b781 --region eu-west-2`
- Additional Moodle-side updates executed with host-side PHP over AWS SSM

## Notes
- The initial clean deployment created the overview course without the rollup completion dependencies; that was corrected immediately afterward using the sync utility.
- The original badge configuration in this deployment targeted course `207`. That was later corrected by `pathway-badge-rollup-fix-2026-03-08.md` so the active badge now awards from hub course `211`.
- No manual browser QA was performed after the final production deployment.
