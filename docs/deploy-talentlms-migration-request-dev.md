# Deploy TalentLMS Migration Request Feature In Dev

Deployment scope for this runbook is `dev` only.

Current status:
- Deployed to `dev` on 2026-03-20
- UI corrected on `dev` on 2026-03-20 after initial deployment
- Deployment record:
  - [docs/deployments/dev-talentlms-migration-request-2026-03-20.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/dev-talentlms-migration-request-2026-03-20.md)
- Remaining validation:
  - logged-in browser verification of the front-page learner UI
  - one real learner-submitted request through Moodle

Target environment:
- Moodle URL: `https://dev.novalxp.co.uk`
- Moodle plugin: `local_novalxpcoursefactory`
- Live Moodle dirroot on dev: `/var/www/moodle/public`
- Moodle admin CLI path on dev: `/var/www/moodle/admin/cli`
- Correct live plugin directory on dev: `/var/www/moodle/public/local/novalxpcoursefactory`
- Lambda function: `novalxp-course-factory-dev`
- AWS region: `eu-west-2`
- Trello destination: `NovaLXP Roadmap` board, `Feedback` list

## What this feature does in dev
- Restores the original AI request experience in the `Text Course` pane
- Replaces the `Video Course` pane with the TalentLMS migration request UI
- Lets learners search a seeded TalentLMS course catalog
- Lets learners submit a reason for wanting a TalentLMS course migrated into NovaLXP
- Sends the request to AWS Lambda
- Creates a Trello card in the roadmap feedback queue

## Deployment boundaries
- Deploy this to `dev` only
- Do not promote to `test` or `production` yet
- Use the seeded catalog file in this repo for `dev` validation only:
  - [docs/finova-courses-seed-active.json](/C:/Users/kbaja/Projects/novalxp-courses/docs/finova-courses-seed-active.json)

## 1. Copy the Moodle plugin into the dev Moodle codebase

Important path note:
- The repo folder is named `moodle/local_novalxpcoursefactory`, but the Moodle plugin component is `local_novalxpcoursefactory`.
- In the live Moodle codebase, the folder name must therefore be `local/novalxpcoursefactory`.
- On dev specifically, the running site uses `$CFG->dirroot = /var/www/moodle/public`, so the live destination is:
  - `/var/www/moodle/public/local/novalxpcoursefactory`
- Do not deploy this plugin to `/var/www/moodle/local/...`.
- Do not deploy it as `/var/www/moodle/public/local/local_novalxpcoursefactory`.

Copy:

```bash
cp -R /Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory /var/www/moodle/public/local/novalxpcoursefactory
```

Then run:

```bash
php /var/www/moodle/admin/cli/upgrade.php --non-interactive
php /var/www/moodle/admin/cli/purge_caches.php
```

## 2. Configure the Moodle plugin in dev

Open:

`Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`

Set:
- `Enable front-page course factory` = enabled
- `Lambda function name` = `novalxp-course-factory-dev`
- `Lambda region` = `eu-west-2`
- `Submit button text` = `Create my course`
- `Placeholder text` = `Describe the course you want...`
- `Seeded TalentLMS catalog JSON` = paste the entire contents of:
  - [docs/finova-courses-seed-active.json](/C:/Users/kbaja/Projects/novalxp-courses/docs/finova-courses-seed-active.json)

## 3. Confirm Moodle service function availability

This feature still requires:
- `local_novalxpcoursefactory_update_job`

If you are deploying the shared Lambda that still also supports AI course generation, keep the existing `local_novalxpapi` functions available too.

## 4. Create or update the Moodle API secret in AWS

Recommended secret name:
- `novalxp/course-factory/dev/moodle-api`

Example:

```bash
aws secretsmanager create-secret \
  --name novalxp/course-factory/dev/moodle-api \
  --secret-string '{"MOODLE_TOKEN":"replace-me","MOODLE_BASE_URL":"https://dev.novalxp.co.uk"}'
```

If it already exists:

```bash
aws secretsmanager put-secret-value \
  --secret-id novalxp/course-factory/dev/moodle-api \
  --secret-string '{"MOODLE_TOKEN":"replace-me","MOODLE_BASE_URL":"https://dev.novalxp.co.uk"}'
```

## 5. Reuse or create the Trello secret for the Feedback list

This feature should create cards in the same Trello destination used by `novalxp-feedback`.

The Lambda expects:
- `TRELLO_SECRET_ARN`

Secret JSON shape:

```json
{
  "TRELLO_KEY": "replace-me",
  "TRELLO_TOKEN": "replace-me",
  "TRELLO_LIST_ID": "replace-me"
}
```

If the `novalxp-feedback` dev secret already targets the correct `Feedback` list, reuse that secret ARN.

## 6. Deploy the dev Lambda

Package:

```bash
cd /Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory
npm install
zip -r function.zip index.mjs package.json package-lock.json node_modules
```

Deploy code:

```bash
aws lambda update-function-code \
  --function-name novalxp-course-factory-dev \
  --zip-file fileb://function.zip
```

Configure environment:

```bash
aws lambda update-function-configuration \
  --function-name novalxp-course-factory-dev \
  --environment "Variables={OPENAI_API_KEY=replace-me,OPENAI_MODEL=gpt-5-mini,MOODLE_BASE_URL=https://dev.novalxp.co.uk,MOODLE_SECRET_ARN=arn:aws:secretsmanager:eu-west-2:ACCOUNT_ID:secret:novalxp/course-factory/dev/moodle-api-XXXX,TRELLO_SECRET_ARN=arn:aws:secretsmanager:eu-west-2:ACCOUNT_ID:secret:novalxp/feedback/dev/trello-XXXX,MOODLE_AI_GENERATED_CATEGORY_ID=5,MOODLE_AI_GENERATED_CATEGORY_NAME=AI-Generated,COURSE_PASS_MARK=80}"
```

Notes:
- `OPENAI_*` stays because the shared Lambda still contains the AI-generation branch
- `TRELLO_SECRET_ARN` is required for the TalentLMS migration request branch

## 7. Ensure IAM is correct in dev

The dev Moodle EC2 role must be able to invoke:
- `novalxp-course-factory-dev`

The Lambda execution role must be able to read:
- the Moodle API secret
- the Trello secret

Also confirm the Moodle host has the AWS CLI:

```bash
aws --version
```

## 8. Sync the Edutor pane label and fallback copy

Run this on the dev Moodle host after the plugin is in place:

```bash
php /var/www/moodle/public/local/novalxpcoursefactory/scripts/set_edutor_pane3_migration.php
```

This helper should only update safe Edutor theme settings:
- sets the third tab label to `TalentLMS`
- keeps the pane title as `Request a TalentLMS course`
- replaces the pane intro with plain fallback HTML
- disables pane 3 blocks so stale carousel content does not show behind the injected UI

Do not store JavaScript in `theme_edutor/pane3intro`.
The Edutor renderer passes that field through `format_text()`, which strips the `<script>` tag and can leave the JavaScript body visible as raw text in the pane.

## 9. Dev validation

As a learner in `dev`:
1. Open the front page.
2. Confirm the third tab label reads `TalentLMS`.
3. Confirm `Text Course` shows the original AI course brief form.
4. Confirm `TalentLMS` shows the migration request UI.
5. Search for a known seeded course.
6. Select it and submit a reason.
7. Confirm the UI shows queued then success.
8. Confirm a new Trello card appears in the `Feedback` list on `NovaLXP Roadmap`.

Latest smoke test result:
- Direct Lambda smoke test succeeded on 2026-03-20
- Trello card created successfully in the dev `Feedback` list
- Live dev fixes applied later on 2026-03-20:
  - plugin moved into the actual live Moodle dirroot
  - plugin folder corrected from `local_novalxpcoursefactory` to `novalxpcoursefactory`
  - catalog parser updated to strip a UTF-8 BOM from pasted seed JSON

## 10. Expected Trello card content

The card should include:
- TalentLMS course title
- TalentLMS course id
- learner reason
- learner identity details
- request id
- NovaLXP page URL

## 11. First places to check if dev validation fails

- Moodle plugin settings were not saved after pasting the catalog JSON
- catalog JSON is malformed
- the Lambda env is missing `TRELLO_SECRET_ARN`
- the Trello secret points to the wrong list
- the Moodle EC2 role cannot invoke `novalxp-course-factory-dev`
- the Lambda execution role cannot read one or both secrets
- Moodle caches were not purged after plugin deployment
- the browser is still serving old AMD assets
- the plugin was copied into `/var/www/moodle/local/...` instead of `/var/www/moodle/public/local/...`
- the plugin folder on the Moodle host is `local_novalxpcoursefactory` instead of `novalxpcoursefactory`
- `theme_edutor/tab3name` still says `Video Course`
- `theme_edutor/pane3intro` still contains pasted JavaScript from an earlier fix attempt
