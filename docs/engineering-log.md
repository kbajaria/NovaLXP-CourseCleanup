# Engineering Log — NovaLXP-Courses

Chronological record of features shipped, bugs fixed, and investigations completed in this repo. Newest entries first.

Used to generate the weekly engineering report. Each entry should be added at the time the work is done or concluded.

**Entry types:** `Feature` · `Bug` · `Investigation` · `Infra` · `Chore`
**Statuses:** `released` · `resolved` · `no-action` · `wont-fix` · `ongoing`

---

## 2026-03-22 — [Infra] Production CloudFront WAF — whitelist Moodle webservice endpoint

**Component:** AWS WAF (`novalxp-secops-scan-temp-20260320`) / production CloudFront
**Status:** released

### What changed
Added WAF rule `AllowMoodleWebservice` (priority 1) to the production CloudFront WAF ACL. The rule allows all requests whose URI path starts with `/webservice/rest/server.php` before the managed rule groups (`AWSManagedRulesCommonRuleSet`, `AWSManagedRulesSQLiRuleSet`, etc.) evaluate them.

### Why
The AI course factory Lambda calls the Moodle web service to create course content, including an `add_page` call that posts HTML table markup (the AI Quality Review scorecard). The managed XSS/SQLi rules blocked this POST, returning a CloudFront 403. Dev and test do not have a WAF and were unaffected.

---

## 2026-03-22 — [Bug] Scorecard section creation crashing Lambda and leaving course job pending

**Component:** `aws/lambda-course-factory` — `index.mjs`
**Status:** released

### Report
Course creation in production timed out from the learner's perspective. The course was created successfully but without the AI Quality Review section.

### Root cause
The `add_page` call posting the scorecard HTML was blocked by the CloudFront WAF (see Infra entry above), throwing an uncaught exception inside `provisionCourse`. This caused the Lambda to fail before calling `update_job` with `complete`, leaving the job record in `processing` state. The frontend polled until the 180-second timeout.

### Fix
Wrapped the scorecard `add_section` / `add_page` calls in a try/catch. Failures are logged as `scorecard_section_failed` and course creation completes normally. The scorecard is best-effort — a WAF block or transient error no longer aborts the course.

**File:** `aws/lambda-course-factory/index.mjs`

---

## 2026-03-22 — [Bug] Bedrock quality evaluator reporting content as truncated

**Component:** `aws/lambda-course-factory` — `index.mjs` `buildScoringPrompt()`
**Status:** released

### Report
The AI Quality Review scorecard consistently noted that course section text appeared truncated.

### Root cause
`buildScoringPrompt()` capped each section's content at 600 characters before sending it to Bedrock. The evaluator correctly identified this as truncation.

### Fix
Removed the `.slice(0, 600)` limit. Full section content is now sent to Bedrock. The 1 024-token output limit is unaffected since the scoring response (JSON scores + summary) is small.

**File:** `aws/lambda-course-factory/index.mjs`

---

## 2026-03-22 — [Bug] `[[jobqueued]]` raw string key shown in status bar after course submission

**Component:** `moodle/local_novalxpcoursefactory` — lang file + `job_store.php`
**Status:** released

### Report
After clicking "Create my course", a garbled `[[jobqueued]]` message appeared briefly in the status bar before being replaced by the processing message.

### Root cause
`job_store.php` called `get_string('jobqueued', 'local_novalxpcoursefactory')` to set the initial job message, but the string key `jobqueued` was missing from the lang file. Moodle returns the raw key in double brackets when a string is undefined.

### Fix
Added `$string['jobqueued'] = 'Your course request has been received. Generating your course...';` to `lang/en/local_novalxpcoursefactory.php`. Deployed to all three Moodle environments.

**File:** `moodle/local_novalxpcoursefactory/lang/en/local_novalxpcoursefactory.php`

---

## 2026-03-22 — [Bug] Bedrock scoring returning "unavailable" — marketplace subscription error

**Component:** `aws/lambda-course-factory` — IAM / Bedrock model selection
**Status:** released

### Report
The AI Quality Review section showed "evaluation unavailable" on all courses after the scoring feature was deployed.

### Root cause
Two separate issues:
1. The Lambda execution roles lacked `aws-marketplace:ViewSubscriptions` and `aws-marketplace:Subscribe`, which Bedrock requires to verify model subscriptions even for already-enabled models.
2. The intended model (`eu.anthropic.claude-haiku-4-5-20251001-v1:0`) had `modelAccessStatus: N/A` across all 57 models in the account — no Anthropic model had been enabled via Bedrock model access. The marketplace subscription check could not be satisfied regardless of IAM permissions.

### Fix
Switched scoring model to `amazon.nova-lite-v1:0` (Amazon Nova Lite), which requires no marketplace subscription and is callable without model access configuration. Set via `BEDROCK_SCORING_MODEL` environment variable on all three Lambda functions. IAM policies updated to include marketplace actions for completeness.

**Files:** Lambda environment variables (all three functions); IAM inline policy `BedrockScoringAccess`

---

## 2026-03-22 — [Feature] AI Quality Review scorecard added to AI-generated courses

**Component:** `aws/lambda-course-factory` — `index.mjs`
**Status:** released (all environments)

### What shipped
After OpenAI generates a course spec, the Lambda now calls Amazon Bedrock (Amazon Nova Lite) to score the course against the original learner brief on five dimensions:

| Dimension | What it measures |
|---|---|
| Relevance | Does the content address what the learner asked for? |
| Content depth | Are sections substantive or surface-level? |
| Quiz alignment | Do quiz questions test the key concepts taught? |
| Clarity | Is the writing clear and accessible? |
| Overall | Overall quality as a production learning resource |

Each dimension receives a score of 1–10 with a one-sentence explanation. A 2–3 sentence overall summary is also generated. The scorecard is added as a read-only **AI Quality Review** section at the bottom of every generated course, rendered as a Bootstrap HTML table with colour-coded badge scores. Scoring is best-effort — any failure falls back to a graceful "unavailable" message and course creation continues.

**Files:** `aws/lambda-course-factory/index.mjs`, `aws/lambda-course-factory/package.json`

---

## 2026-03-20 — [Feature] TalentLMS migration request feature

**Component:** `aws/lambda-course-factory`, `moodle/local_novalxpcoursefactory`
**Status:** released (all environments)

### What shipped
Learners can now request migration of a TalentLMS course into NovaLXP directly from the front page. A searchable catalog of TalentLMS courses is seeded into the plugin; the learner selects a course, provides a reason, and submits. The Lambda creates a Trello card in the NovaLXP roadmap feedback queue.

See deployment record: [`docs/deployments/prod-talentlms-migration-request-2026-03-20.md`](deployments/prod-talentlms-migration-request-2026-03-20.md)
