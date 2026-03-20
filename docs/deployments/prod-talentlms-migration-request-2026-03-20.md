# Production Deployment Record

- Date (UTC): 2026-03-20
- Environment: production
- Host: `i-02bcf20804a48b781`
- Moodle wwwroot: `https://learn.novalxp.co.uk`
- Live Moodle dirroot: `/var/www/moodle/public`
- Moodle admin CLI path: `/var/www/moodle/admin/cli`
- Correct plugin path: `/var/www/moodle/public/local/novalxpcoursefactory`
- Lambda function: `novalxp-course-factory-production`
- Lambda log group: `/aws/lambda/novalxp-course-factory-production`
- PR: [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1)
- Feature merge commit: `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9`
- Deployment docs commit on `main`: `2799e8a6912f81bcb1623c212fdf06336202de4f`
- Trello destination: `NovaLXP Roadmap` board, `Feedback` list via `novalxp/feedback/prod/trello`

## Change applied
Promoted the TalentLMS migration request feature to `production` using the same tested plugin archive and Lambda artifact validated in `test`.

This deployment:
- updated the live `local_novalxpcoursefactory` plugin in the production Moodle codebase
- seeded the plugin with the active TalentLMS catalog from:
  - [docs/finova-courses-seed-active.json](/C:/Users/kbaja/Projects/novalxp-courses/docs/finova-courses-seed-active.json)
- set the front-page pane label to `Search TalentLMS`
- set the pane title to `Request a TalentLMS course`
- set safe fallback intro copy for pane 3
- disabled pane 3 blocks so stale theme content does not render behind the injected UI
- updated the production Lambda code to the tested build
- added `TRELLO_SECRET_ARN` to the production Lambda environment
- added the missing production Lambda IAM policy permitting `secretsmanager:GetSecretValue` on the production Trello secret

## Moodle state after deployment
Verified on the production Moodle host:
- `$CFG->dirroot = /var/www/moodle/public`
- live plugin path present: `/var/www/moodle/public/local/novalxpcoursefactory`
- `lambdafunctionname = novalxp-course-factory-production`
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
- verified Moodle config values through CLI on the production host
- verified the seeded catalog is stored and parses successfully
- verified the production Lambda update completed successfully
- verified a direct `talentlms_migration` Lambda smoke test succeeded
- verified production Trello card creation:
  - `https://trello.com/c/Mg6Wrr4M/97-talentlms-migration-request-executive-welcome-ind-01-codex-production-smoke-test`

## Remaining validation
- logged-in browser check on `https://learn.novalxp.co.uk`
- one real learner-submitted TalentLMS migration request through the live Moodle UI
