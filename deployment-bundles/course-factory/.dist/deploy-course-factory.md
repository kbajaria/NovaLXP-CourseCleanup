# Deploy NovaLXP Course Factory

This runbook deploys the separate AI course-factory capability using:

- Moodle plugin: `local_novalxpcoursefactory`
- Existing Moodle API plugin: `local_novalxpapi`
- AWS Lambda package: `aws/lambda-course-factory`

## Architecture

Runtime path:

1. Learner submits a course brief on the front page.
2. Moodle AJAX external function handles the request.
3. Moodle invokes AWS Lambda through the AWS CLI on the EC2 host role.
4. Lambda generates the course with OpenAI.
5. Lambda calls `local_novalxpapi` web service functions to build the course in Moodle.

## Prerequisites

You need:

- access to the live Moodle codebase
- access to the live `local_novalxpapi` plugin codebase
- the Moodle web service token already used for `local_novalxpapi`
- AWS access to deploy/update Lambda in the target account
- permission for the Moodle EC2 instance role to invoke the Lambda function
- OpenAI API key for the Lambda environment
- a Secrets Manager secret for the Moodle API token is recommended

## Files To Deploy

From this repo:

- [moodle/local_novalxpcoursefactory](/Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory)
- [aws/lambda-course-factory](/Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory)

For `local_novalxpapi`, either:

- apply [patches/local_novalxpapi-course-factory-guardrails.patch](/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch), or
- copy the equivalent changes from:
  - [external.php](/Users/kamilabajaria/Projects/NovaLXP-Dashboard/artifacts/source/novalxpapi/classes/external.php#L625)
  - [services.php](/Users/kamilabajaria/Projects/NovaLXP-Dashboard/artifacts/source/novalxpapi/db/services.php)

## Step 1: Update `local_novalxpapi`

In the real Moodle codebase:

1. Add the new service function registration:
   - `local_novalxpapi_apply_quiz_completion_guardrails`
2. Add the implementation method:
   - `apply_quiz_completion_guardrails(...)`
3. Deploy the updated plugin files.
4. Run Moodle upgrade if required:

```bash
php admin/cli/upgrade.php --non-interactive
```

5. Purge caches:

```bash
php admin/cli/purge_caches.php
```

## Step 2: Confirm The Web Service Token Can Call The New Function

In Moodle admin:

1. Open `Site administration -> Server -> Web services -> External services`
2. Open the service used by your existing token
3. Confirm it contains:
   - `local_novalxpapi_create_course`
   - `local_novalxpapi_add_section`
   - `local_novalxpapi_add_page`
   - `local_novalxpapi_create_quiz`
   - `local_novalxpapi_apply_quiz_completion_guardrails`

If the service does not automatically include the new function, add it manually.

## Step 3: Install `local_novalxpcoursefactory`

Copy:

```bash
cp -R /Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory /path/to/moodle/local/
```

Then run:

```bash
php admin/cli/upgrade.php --non-interactive
php admin/cli/purge_caches.php
```

In Moodle admin, configure:

`Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`

Set:

- `Enable front-page course factory` = enabled
- `Lambda function name` = environment-specific function name
- `Lambda region` = `eu-west-2` or your target region
- `Request timeout` = `120` recommended

## Step 4: Deploy Lambda

From this repo:

```bash
cd /Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory
npm install
zip -r function.zip index.mjs package.json node_modules
```

Create or update the function:

```bash
aws lambda update-function-code \
  --function-name novalxp-course-factory-dev \
  --zip-file fileb://function.zip
```

Set environment variables:

```bash
aws lambda update-function-configuration \
  --function-name novalxp-course-factory-dev \
  --environment "Variables={OPENAI_API_KEY=replace-me,OPENAI_MODEL=gpt-5-mini,MOODLE_BASE_URL=https://dev.novalxp.co.uk,MOODLE_SECRET_ARN=arn:aws:secretsmanager:eu-west-2:ACCOUNT_ID:secret:novalxp/course-factory/dev/moodle-api-XXXX,MOODLE_AI_GENERATED_CATEGORY_ID=5,MOODLE_AI_GENERATED_CATEGORY_NAME=AI-Generated,COURSE_PASS_MARK=80}"
```

Recommended secret name:

- `novalxp/course-factory/dev/moodle-api`

Recommended secret JSON:

```json
{
  "MOODLE_TOKEN": "replace-me",
  "MOODLE_BASE_URL": "https://dev.novalxp.co.uk"
}
```

## Step 5: Allow Moodle EC2 To Invoke Lambda

Attach IAM permission to the Moodle instance role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:eu-west-2:ACCOUNT_ID:function:novalxp-course-factory-dev"
    }
  ]
}
```

Also ensure the AWS CLI is available on the Moodle host:

```bash
aws --version
```

If Lambda reads the token from Secrets Manager, attach `secretsmanager:GetSecretValue` on the secret ARN to the Lambda execution role.

## Step 6: Front-Page Validation

Log in as a learner and verify:

1. Front page loads.
2. Edutor featured pane 1 block 4 is replaced by the multiline form.
3. Placeholder guidance appears.
4. Submitting a realistic course brief returns a success link.

## Step 7: Moodle Course Validation

For the created course, verify:

1. Category is `AI-Generated`.
2. Course is visible.
3. Learners can self-enrol.
4. Section pages exist for each generated section.
5. Quiz exists with five questions.
6. Quiz has a pass mark of `80`.
7. Quiz activity completion requires pass grade.
8. Course completion contains the quiz activity criterion.

## Step 8: Learner Completion Validation

Using a learner account:

1. Enrol in the generated course.
2. Open the quiz.
3. Pass the quiz.
4. Confirm the quiz shows complete.
5. Confirm the course shows complete.

## Failure Points To Check First

If course creation fails:

- plugin settings missing Lambda function name or region
- Moodle EC2 instance role lacks `lambda:InvokeFunction`
- AWS CLI missing on Moodle host
- Lambda environment missing `OPENAI_API_KEY`
- Moodle token service missing the new `local_novalxpapi_apply_quiz_completion_guardrails` function

If the course is created but completion does not work:

- the new `local_novalxpapi_apply_quiz_completion_guardrails` function was not deployed
- the Lambda cannot call the new function with the current token
- the course completion criterion was not added
- the quiz grade pass mark did not persist

## Recommended First Environment

Deploy to `dev` first, validate with one generated course, then promote to `test`, then `production`.
