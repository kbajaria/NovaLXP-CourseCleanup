# Dev Deployment Record

- Date (UTC): 2026-03-20
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Live Moodle dirroot: `/var/www/moodle/public`
- Moodle admin CLI path: `/var/www/moodle/admin/cli`
- Correct plugin path: `/var/www/moodle/public/local/novalxpcoursefactory`
- Lambda function: `novalxp-course-factory-dev`
- Lambda log group: `/aws/lambda/novalxp-course-factory-dev`
- Trello destination: `NovaLXP Roadmap` board, `Feedback` list

## Change applied
Deployed the TalentLMS migration request feature to `dev`.

Later on the same day, corrected the front-page pane mapping after learner UX review:
- restored the original AI request experience to the `Text Course` pane
- moved the TalentLMS migration request experience to the `Video Course` pane

This deployment:
- installed the updated `local_novalxpcoursefactory` plugin in the dev Moodle codebase
- configured the plugin to use `novalxp-course-factory-dev`
- seeded the plugin catalog with the active-course JSON from:
  - [docs/finova-courses-seed-active.json](/C:/Users/kbaja/Projects/novalxp-courses/docs/finova-courses-seed-active.json)
- updated the Lambda code to support `talentlms_migration`
- added `TRELLO_SECRET_ARN` to the dev Lambda environment
- added Lambda role permission to read the dev Trello secret

## Path correction discovered during follow-up validation
During later UI validation on 2026-03-20, we confirmed the dev site is served from:
- `$CFG->dirroot = /var/www/moodle/public`

Two deployment footguns were then corrected:
- the plugin must live at `/var/www/moodle/public/local/novalxpcoursefactory`
- the folder name must be `novalxpcoursefactory`, not `local_novalxpcoursefactory`

This mattered because:
- `/var/www/moodle/local/...` is not the live plugin path for the served dev site
- `/var/www/moodle/public/local/local_novalxpcoursefactory` is treated by Moodle as a misplaced plugin and blocks upgrade

Also corrected during follow-up:
- `classes/catalog.php` now strips a UTF-8 BOM from pasted catalog JSON before `json_decode()`

## Moodle config state
Verified after deployment:
- `enabled = 1`
- `lambdafunctionname = novalxp-course-factory-dev`
- `buttontext = Create my course`
- `placeholdertext = Describe the course you want...`
- `talentlmscatalogjson` stored successfully
- stored catalog byte length: `401234`

## Web service state
- Existing dev manual service found: `CourseCreationAPI`
- `local_novalxpcoursefactory_update_job` was already present on that service at verification time

## Lambda state
Verified after deployment:
- function update succeeded
- environment now includes:
  - `MOODLE_SECRET_ARN`
  - `OPENAI_SECRET_ARN`
  - `OPENAI_MODEL`
  - `TRELLO_SECRET_ARN`
  - existing course-factory variables

## Smoke test
Executed a direct Lambda smoke test for the migration request branch.

Result:
- status: success
- requested course: `Executive Welcome (IND-01)`
- Trello card created:
  - `https://trello.com/c/lEskaPjS/93-talentlms-migration-request-executive-welcome-ind-01-codex-deployment-smoke-test`

## What is still not fully verified
- A logged-in browser check on the dev NovaLXP front page to confirm:
  - `Video Course` shows the TalentLMS migration search/request UI
  - `Text Course` shows the restored AI brief form
- A full learner-submitted request from the real Moodle UI end to end

## Remote file verification after the UI correction
Verified on the dev Moodle host:
- `amd/build/frontpage_factory.min.js` targets `#feature-pane-4`
- `amd/build/frontpage_migration.min.js` targets `#feature-pane-3`
- `classes/hook_callbacks.php` injects:
  - `course_factory.php` for the AI pane
  - `migration_request.php` for the migration pane
- `theme_edutor/tab3name = Search TalentLMS`
- catalog parsing succeeds against the stored seeded JSON after BOM handling

## Temporary deployment artifacts
Temporary S3 deployment bucket used during rollout:
- `novalxp-dev-deploy-070017892219-20260320`

Status:
- removed after deployment
