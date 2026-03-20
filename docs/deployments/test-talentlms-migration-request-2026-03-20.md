# Test Deployment Record

- Date (UTC): 2026-03-20
- Environment: test
- Host: `i-00c24ea634d4728ba` (`test-moodle-app`)
- Moodle wwwroot: `https://test.novalxp.co.uk`
- Live Moodle dirroot: `/var/www/moodle/public`
- Moodle admin CLI path: `/var/www/moodle/admin/cli`
- Correct plugin path: `/var/www/moodle/public/local/novalxpcoursefactory`
- Lambda function: `novalxp-course-factory-test`
- Lambda log group: `/aws/lambda/novalxp-course-factory-test`
- PR: [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1)
- Merge commit: `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9`
- Trello destination: `NovaLXP Roadmap` board, `Feedback` list via `novalxp/feedback/test/trello`

## Change applied
Promoted the TalentLMS migration request feature from merged `main` into `test`.

This deployment:
- updated the live `local_novalxpcoursefactory` plugin in the test Moodle codebase
- seeded the plugin with the active TalentLMS catalog from:
  - [docs/finova-courses-seed-active.json](/C:/Users/kbaja/Projects/novalxp-courses/docs/finova-courses-seed-active.json)
- set the front-page pane label to `Search TalentLMS`
- set the pane title to `Request a TalentLMS course`
- set safe fallback intro copy for pane 3
- disabled pane 3 blocks so stale theme content does not render behind the injected UI
- updated the test Lambda code to the same build promoted in `dev`
- added `TRELLO_SECRET_ARN` to the test Lambda environment
- later added the missing test Lambda IAM policy permitting `secretsmanager:GetSecretValue` on the test Trello secret

## Moodle state after deployment
Verified on the test Moodle host:
- `$CFG->dirroot = /var/www/moodle/public`
- live plugin path present: `/var/www/moodle/public/local/novalxpcoursefactory`
- `lambdafunctionname = novalxp-course-factory-test`
- `theme_edutor/tab3name = Search TalentLMS`
- seeded catalog present
- parsed catalog count: `1300`
- first parsed course: `(Virtual) Standup Meeting Accreditation`

## Lambda state after deployment
Verified after deployment:
- `CodeSha256 = gkLUeOaeCKhWxaY/6aDKZpwdiK3J2tz88djNPBfaJUg=`
- `LastUpdateStatus = Successful`
- environment includes:
  - `MOODLE_SECRET_ARN`
  - `OPENAI_SECRET_ARN`
  - `OPENAI_MODEL`
  - `TRELLO_SECRET_ARN`
  - existing course-factory variables

## Validation completed
- verified Moodle config values through CLI on the test host
- verified the seeded catalog is stored and parses successfully
- verified the test Lambda update completed successfully
- verified a direct `talentlms_migration` Lambda smoke test succeeded after the Trello secret-read IAM fix
- verified Trello card creation after the IAM fix:
  - `https://trello.com/c/f0az6PkI/95-talentlms-migration-request-executive-welcome-ind-01-codex-test`

## Post-deploy issue and fix
Observed during initial learner testing in `test`:
- browser submission reached the Lambda, but the request failed with:
  - `is not authorized to perform: secretsmanager:GetSecretValue`
- root cause:
  - the test Lambda environment had `TRELLO_SECRET_ARN`, but the Lambda execution role did not yet have permission to read that secret

Fix applied:
- attached inline policy `NovaLXPCourseFactoryTestReadTrelloSecret`
- granted `secretsmanager:GetSecretValue` on:
  - `arn:aws:secretsmanager:eu-west-2:070017892219:secret:novalxp/feedback/test/trello-60352e`

Pre-production lesson:
- when promoting this feature, treat the Trello secret-read IAM policy as a required deployment step, not as optional follow-up

## Remaining validation
- logged-in browser check on `https://test.novalxp.co.uk`
- one learner-submitted TalentLMS migration request through the real Moodle UI
- optional Trello smoke test against the test feedback list
