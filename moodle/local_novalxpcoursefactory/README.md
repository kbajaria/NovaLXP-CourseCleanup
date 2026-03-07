# local_novalxpcoursefactory

Separate Moodle local plugin for the NovaLXP AI course-factory workflow.

## Scope
- Replaces the Edutor front-page featured section pane 1 block 4 card with a learner prompt form.
- Sends learner briefs through a Moodle AJAX external function.
- Invokes AWS Lambda from the Moodle EC2 host using the instance role.
- Does not share runtime intent routing with the RAG chatbot.

## Configure in Moodle
1. Install plugin in `local/novalxpcoursefactory`.
2. Visit `Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`.
3. Set:
   - Lambda function name
   - Lambda region
   - optional timeout/placeholder/button copy

## AWS requirement
- The Moodle EC2 instance role must be allowed to invoke the configured Lambda function with `lambda:InvokeFunction`.
- The Moodle host must have the AWS CLI available, matching the same pattern used by `NovaLXP-Feedback`.

## Moodle API requirement
The Lambda expects these exposed Moodle web service functions from `local_novalxpapi`:
- `local_novalxpapi_create_course`
- `local_novalxpapi_add_section`
- `local_novalxpapi_add_page`
- `local_novalxpapi_create_quiz`

## Front-page behaviour
- Only loads for logged-in non-guest users.
- Only loads on the Moodle front page.
- Replaces `.featured-carousel .item-1-4 .item-inner` in the Edutor featured section.

## AJAX contract
Web service method:
- `local_novalxpcoursefactory_create_course`

Arguments:
- `brief`
