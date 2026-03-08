# local_novalxpcoursefactory

Separate Moodle local plugin for the NovaLXP AI course-factory workflow.

## Scope
- Replaces the Edutor front-page featured section pane 1 block 4 card with a learner prompt form.
- Queues learner briefs in Moodle and invokes AWS Lambda from the Moodle EC2 host using the instance role.
- Polls Moodle job state until the generated course is ready.
- Shows the created course title as the final clickable link so the learner can open it and enrol immediately.
- Does not share runtime intent routing with the RAG chatbot.

## Configure in Moodle
1. Install plugin in `local/novalxpcoursefactory`.
2. Visit `Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`.
3. Set:
   - Lambda function name
   - Lambda region
   - optional placeholder/button copy

## AWS requirement
- The Moodle EC2 instance role must be allowed to invoke the configured Lambda function with `lambda:InvokeFunction`.
- The Moodle host must have the AWS CLI available, matching the same pattern used by `NovaLXP-Feedback`.

## Moodle API requirement
The Lambda expects these exposed Moodle web service functions:
- `local_novalxpapi_create_course`
- `local_novalxpapi_add_section`
- `local_novalxpapi_add_page`
- `local_novalxpapi_create_quiz`
- `local_novalxpapi_apply_quiz_completion_guardrails`
- `local_novalxpcoursefactory_update_job`

## Front-page behaviour
- Only loads for logged-in non-guest users.
- Only loads on the Moodle front page.
- Replaces `.featured-carousel .item-1-4 .item-inner` in the Edutor featured section.

## Front-end flow
- `course_factory.php` queues the job and returns a request id immediately.
- `job_status.php` returns queued, processing, complete, or failed status.
- The AMD module polls `job_status.php` until the course is ready.
