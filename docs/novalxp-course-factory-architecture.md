# NovaLXP Course Factory Architecture

## Goal
Provide a separate AI course-creation capability on the NovaLXP front page without coupling it to the RAG chatbot.

## Separation model
- Moodle plugin: `local_novalxpcoursefactory`
- Lambda package: `aws/lambda-course-factory`
- Shared idea only: implementation patterns reused from `NovaLXP-Bot` and the Lambda invoke pattern reused from `NovaLXP-Feedback`
- No shared runtime route, intent classifier, or user-facing chat surface

## Frontend path
1. Logged-in learner opens the front page.
2. Moodle plugin injects AMD JS on the front page only.
3. JS replaces Edutor pane 1 block 4 with the NovaLXP course request form.
4. Learner submits a descriptive course brief.
5. Moodle queues a job record in `moodledata`, invokes Lambda asynchronously through the AWS CLI, and returns immediately with a request id.
6. The browser polls a Moodle status endpoint until the job is complete or failed.
7. When complete, the UI shows the created course title as a direct clickable link so the learner can open the course immediately and enrol.

## Backend path
1. Moodle invokes Lambda via AWS CLI and the EC2 instance role using async invocation (`StatusCode 202`).
2. Lambda marks the Moodle job as `processing` through a Moodle web service callback.
3. Lambda validates the request.
4. Lambda uses OpenAI structured output to generate:
   - course title
   - course summary
   - up to 5 sections
   - exactly 5 quiz questions
5. Lambda calls Amazon Bedrock (Claude via EU cross-region inference profile) to score the generated course against the original brief on four dimensions: relevance, content depth, quiz alignment, and clarity — each 1–10 with a one-sentence explanation — plus an overall score and 2–3 sentence summary. Scoring is best-effort: if Bedrock is unavailable or returns an error, a fallback "unavailable" message is used and course creation continues normally.
6. Lambda provisions the course in Moodle through `local_novalxpapi` web service functions, including a read-only "AI Quality Review" section at the bottom of the course containing the Bedrock scorecard as a Bootstrap HTML table.
7. Lambda updates the Moodle job to `complete` or `failed` through `local_novalxpcoursefactory_update_job`.
8. The browser polling path reads that stored job state and surfaces success or failure to the learner.

## Moodle provisioning status
- Implemented:
  - course creation
  - section creation
  - page creation for section content
  - quiz creation with five GIFT questions
  - quiz-completion guardrails after quiz creation
  - course completion criterion tied to quiz pass
  - async job queueing and status polling
  - Lambda callback into Moodle to update job state
  - learner self-enrolment through existing `local_novalxpapi_create_course` behavior
  - AI Quality Review section added at course bottom with Bedrock-generated scorecard

## Bedrock scoring
- Model: `amazon.nova-lite-v1:0` (controlled by `BEDROCK_SCORING_MODEL` Lambda environment variable)
- Region: `eu-west-2` (same as Lambda)
- IAM: Lambda execution role has `bedrock:InvokeModel`, `bedrock:Converse`, `aws-marketplace:ViewSubscriptions`, and `aws-marketplace:Subscribe` via inline policy `BedrockScoringAccess` on all three Lambda roles
- Scorecard creation is wrapped in a try/catch — if the `add_page` call fails for any reason (e.g. WAF, network), the error is logged as `scorecard_section_failed` and course creation completes normally

## Production WAF
- The production CloudFront distribution (`learn.novalxp.co.uk`, `E317SOC1RRGSCT`) has a WAF ACL (`novalxp-secops-scan-temp-20260320`) with managed rule groups including `AWSManagedRulesCommonRuleSet` and `AWSManagedRulesSQLiRuleSet`
- Rule `AllowMoodleWebservice` (priority 1) allows all requests to `/webservice/rest/server.php` before the managed rule groups can inspect them, preventing HTML content in `add_page` calls from triggering XSS/SQLi blocks
- Dev and test do not have a WAF

## Why this is separate
- Different permissions from learner Q&A.
- Higher operational risk because it writes Moodle data.
- Different logging, rate limiting, and abuse controls.
- Easier to test and deploy independently.

## Important operational notes
- The learner-facing request is intentionally asynchronous because the OpenAI plus Moodle provisioning path can take 45 to 60 seconds and is too slow for a synchronous CloudFront-backed browser request.
- The Moodle token service must include both:
  - `local_novalxpapi_apply_quiz_completion_guardrails`
  - `local_novalxpcoursefactory_update_job`
- The Lambda deployment package must include `node_modules`; missing dependencies will fail at Lambda init time before any job update can occur.
- The `@aws-sdk/client-bedrock-runtime` package is required in addition to `@aws-sdk/client-secrets-manager` and `openai`.
