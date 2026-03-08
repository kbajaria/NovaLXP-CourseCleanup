# Deploy NovaLXP Course Factory In Dev

Target environment:

- Moodle URL: `https://dev.novalxp.co.uk`
- Category: `AI-Generated` (`id=5`)
- Suggested Lambda name: `novalxp-course-factory-dev`
- Suggested region: `eu-west-2`

## 1. Update `local_novalxpapi` in the dev Moodle codebase

Apply the new guardrail function to the real `local_novalxpapi` plugin using either:

- [patches/local_novalxpapi-course-factory-guardrails.patch](/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch)
- or the updated artifact source at:
  - [external.php](/Users/kamilabajaria/Projects/NovaLXP-Dashboard/artifacts/source/novalxpapi/classes/external.php#L625)
  - [services.php](/Users/kamilabajaria/Projects/NovaLXP-Dashboard/artifacts/source/novalxpapi/db/services.php)

Then run:

```bash
php admin/cli/upgrade.php --non-interactive
php admin/cli/purge_caches.php
```

## 2. Confirm the dev web service token can call all required functions

The service behind the existing token must include:

- `local_novalxpapi_create_course`
- `local_novalxpapi_add_section`
- `local_novalxpapi_add_page`
- `local_novalxpapi_create_quiz`
- `local_novalxpapi_apply_quiz_completion_guardrails`
- `local_novalxpcoursefactory_update_job`

Important:
- In `dev`, the existing token is attached to a restricted manual service named `CourseCreationAPI`, not the plugin-defined `novalxpapi` service.
- If your token uses a similar restricted manual service in `test` or `production`, add `local_novalxpapi_apply_quiz_completion_guardrails` to that service as well.
- Updating only `db/services.php` is not enough when the token is tied to a different service record.

## 3. Install `local_novalxpcoursefactory` in dev

Copy:

```bash
cp -R /Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory /path/to/dev-moodle/local/
```

Then run:

```bash
php admin/cli/upgrade.php --non-interactive
php admin/cli/purge_caches.php
```

Plugin settings in Moodle:

`Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`

Set:

- `Enable front-page course factory` = enabled
- `Lambda function name` = `novalxp-course-factory-dev`
- `Lambda region` = `eu-west-2`

## 4. Deploy the dev Lambda

Package:

```bash
cd /Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory
npm install
zip -r function.zip index.mjs package.json package-lock.json node_modules
```

Deploy:

```bash
aws lambda update-function-code \
  --function-name novalxp-course-factory-dev \
  --zip-file fileb://function.zip
```

Create the Moodle API secret first:

```bash
aws secretsmanager create-secret \
  --name novalxp/course-factory/dev/moodle-api \
  --secret-string '{"MOODLE_TOKEN":"replace-me","MOODLE_BASE_URL":"https://dev.novalxp.co.uk"}'
```

If the secret already exists:

```bash
aws secretsmanager put-secret-value \
  --secret-id novalxp/course-factory/dev/moodle-api \
  --secret-string '{"MOODLE_TOKEN":"replace-me","MOODLE_BASE_URL":"https://dev.novalxp.co.uk"}'
```

Configure:

```bash
aws lambda update-function-configuration \
  --function-name novalxp-course-factory-dev \
  --environment "Variables={OPENAI_API_KEY=replace-me,OPENAI_MODEL=gpt-5-mini,MOODLE_BASE_URL=https://dev.novalxp.co.uk,MOODLE_SECRET_ARN=arn:aws:secretsmanager:eu-west-2:ACCOUNT_ID:secret:novalxp/course-factory/dev/moodle-api-XXXX,MOODLE_AI_GENERATED_CATEGORY_ID=5,MOODLE_AI_GENERATED_CATEGORY_NAME=AI-Generated,COURSE_PASS_MARK=80}"
```

## 5. Ensure the dev Moodle EC2 role can invoke the Lambda

Required IAM action:

- `lambda:InvokeFunction` on `novalxp-course-factory-dev`

Lambda execution role also needs:

- `secretsmanager:GetSecretValue` on `novalxp/course-factory/dev/moodle-api`

Also confirm the Moodle host has the AWS CLI:

```bash
aws --version
```

## 6. Run one dev end-to-end test

As a learner:

1. Open the dev front page.
2. Confirm pane 1 block 4 is replaced by the AI course form.
3. Submit a realistic course brief.
4. Confirm the UI immediately shows queued/processing status.
5. Confirm the created course title is shown as the clickable success link, then follow it to the generated course when polling completes.

## 7. Validate the generated dev course

Check:

1. Course is in `AI-Generated`.
2. Course is visible.
3. Learners can self-enrol.
4. Generated sections exist as Page activities.
5. Quiz exists with 5 questions.
6. Quiz pass mark is `80`.
7. Quiz activity completion requires pass grade.
8. Course completion contains the quiz activity criterion.

## 8. Validate learner completion in dev

Using a learner account:

1. Enrol.
2. Pass the quiz.
3. Confirm the quiz is marked complete.
4. Confirm the course is marked complete.

## First places to look if it fails

- `local_novalxpapi` was updated but not upgraded/purged
- token service does not include `local_novalxpapi_apply_quiz_completion_guardrails`
- token service does not include `local_novalxpcoursefactory_update_job`
- token is bound to a restricted manual service such as `CourseCreationAPI`
- Lambda env vars are incomplete
- Moodle EC2 role cannot invoke Lambda
- AWS CLI missing on the Moodle host
- Lambda package was deployed without `node_modules`

## Logging and troubleshooting

Moodle-side logging:

- PHP error log entries are prefixed with:
  - `[NovaLXPCourseFactory]`
- Key events logged:
  - AJAX request start and completion
  - Lambda invoke start and completion
  - service success/failure with request and course IDs

Lambda-side logging:

- CloudWatch log group:
  - `/aws/lambda/novalxp-course-factory-dev`
- Structured JSON stages logged:
  - `request_start`
- `openai_generation_start`
- `openai_generation_complete`
- `job_update_error`
- `moodle_ws_call_start`
  - `moodle_ws_call_complete`
  - `course_created`
  - `section_created`
  - `section_page_created`
  - `quiz_created`
  - `guardrails_applied`
  - `request_complete`
  - `request_error`

Useful first checks:

```bash
aws logs tail /aws/lambda/novalxp-course-factory-dev --follow
```

Look for:

- the Moodle `request_id`
- the Moodle web service function that failed
- whether the failure happened before or after OpenAI generation
