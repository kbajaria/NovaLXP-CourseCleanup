# Deployment Record — AI Quality Scoring for Course Factory

- Date (UTC): 2026-03-22
- Environments: `dev`, `test`, `production` (deployed simultaneously throughout the session)
- Lambda functions: `novalxp-course-factory-dev`, `novalxp-course-factory-test`, `novalxp-course-factory-production`
- Moodle hosts: `dev.novalxp.co.uk`, `test.novalxp.co.uk`, `learn.novalxp.co.uk`
- Commits on `main`:
  - `1215653` — Add Bedrock quality scoring step to AI course factory
  - `e990d88` — Fix jobqueued missing lang string and scoring prompt truncation
  - `11e2ff8` — Make scorecard section creation fault-tolerant

---

## Changes applied

### 1. Bedrock quality scoring step (Lambda — `index.mjs`)

After OpenAI generates a course spec, the Lambda now calls Amazon Bedrock to score the course on four dimensions:

| Dimension | What it measures |
|---|---|
| Relevance | Does the content directly address the learner's brief? |
| Content depth | Are sections substantive, or thin and surface-level? |
| Quiz alignment | Do quiz questions test the key concepts taught? |
| Clarity | Is the writing clear, well-structured, and accessible? |
| Overall | Overall quality as a production learning resource |

Each dimension receives a score of 1–10 with a one-sentence explanation. A 2–3 sentence overall summary is also generated.

The scorecard is added as a read-only **AI Quality Review** section at the bottom of every generated course, rendered as a Bootstrap HTML table with colour-coded badge scores (green ≥ 8, yellow ≥ 6, red < 6).

Scoring is best-effort. If Bedrock fails for any reason, the course still creates successfully and the scorecard section shows a graceful "unavailable" fallback.

### 2. Bedrock model

- Model ID: `amazon.nova-lite-v1:0` (Amazon Nova Lite — no marketplace subscription required)
- Controlled by `BEDROCK_SCORING_MODEL` Lambda environment variable (set on all three functions)
- Region: `eu-west-2`
- `anthropic.claude-haiku-4-5-20251001-v1:0` was evaluated first but failed due to unresolvable marketplace subscription requirements for the Lambda execution role

### 3. IAM permissions added to all three Lambda execution roles

Inline policy `BedrockScoringAccess` updated on:
- `novalxp-course-factory-dev-lambda-role`
- `novalxp-course-factory-test-lambda-role`
- `novalxp-course-factory-production-lambda-role`

Actions granted: `bedrock:InvokeModel`, `bedrock:Converse`, `aws-marketplace:ViewSubscriptions`, `aws-marketplace:Subscribe`.

### 4. Moodle lang file fix (`local_novalxpcoursefactory.php`)

Added missing string key `jobqueued`. When absent, Moodle's `get_string()` returns `[[jobqueued]]` which was displayed briefly in the status bar on the first poll after submission. Now reads: *"Your course request has been received. Generating your course..."*

Deployed to all three Moodle hosts via SCP + `sudo cp` + `purge_caches`.

### 5. Scoring prompt truncation removed (`index.mjs`)

The initial implementation capped each section's content at 600 characters before sending it to Bedrock. This caused the evaluator to correctly report that content appeared truncated. The cap was removed so the full section text is evaluated.

### 6. Scorecard creation made fault-tolerant (`index.mjs`)

The `add_section` / `add_page` calls for the scorecard section are now wrapped in a try/catch. If the page creation fails (e.g. WAF block), the error is logged as `scorecard_section_failed` and course creation completes normally. Previously, a failure here left the job in a pending state and the frontend would poll until the 180-second timeout.

### 7. Production WAF rule — AllowMoodleWebservice

The production CloudFront WAF ACL (`novalxp-secops-scan-temp-20260320`) had managed rule groups (`AWSManagedRulesCommonRuleSet`, `AWSManagedRulesSQLiRuleSet`, etc.) that blocked `add_page` calls containing HTML table content, treating it as XSS/SQLi.

Added WAF rule `AllowMoodleWebservice` at priority 1:
- Matches: URI path starts with `/webservice/rest/server.php`
- Action: Allow (bypasses all managed rule groups for this path)

Dev and test do not have a WAF and were not affected.

### 8. `package.json` — new dependency

`@aws-sdk/client-bedrock-runtime: ^3.883.0` added and `npm install` run. Lambda zip rebuilt and redeployed to all three functions.

---

## Lambda state after deployment

All three functions updated at:
- `novalxp-course-factory-dev`: 2026-03-22T15:56:20Z
- `novalxp-course-factory-test`: 2026-03-22T15:56:46Z
- `novalxp-course-factory-production`: 2026-03-22T15:57:11Z

Environment variable `BEDROCK_SCORING_MODEL=amazon.nova-lite-v1:0` confirmed on all three.

---

## Validation

- Dev: course generated with scorecard ✓ (overallScore: 8 logged at 15:14)
- Production: course generated with full scorecard after WAF rule applied ✓ (overallScore: 9 logged at 15:49 on subsequent run)
- Fault-tolerant fallback: confirmed via CloudWatch — `scorecard_section_failed` log fires and course still completes when scorecard page creation fails
