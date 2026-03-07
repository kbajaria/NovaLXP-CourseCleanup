# NovaLXP Course Factory Lambda

This Lambda is invoked by the Moodle `local_novalxpcoursefactory` plugin through the AWS CLI on the EC2 host.

## Flow
- Moodle learner submits course brief
- Moodle AJAX external function invokes Lambda
- Lambda calls OpenAI to generate structured course content
- Lambda calls exposed Moodle API functions in `local_novalxpapi`

## Required environment variables
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `MOODLE_BASE_URL`
- `MOODLE_TOKEN` or `MOODLE_SECRET_ARN`
- `MOODLE_AI_GENERATED_CATEGORY_ID`
- `MOODLE_AI_GENERATED_CATEGORY_NAME`

## Recommended secret shape

Secret name:
- `novalxp/course-factory/dev/moodle-api`

Secret JSON:

```json
{
  "MOODLE_TOKEN": "replace-me",
  "MOODLE_BASE_URL": "https://dev.novalxp.co.uk"
}
```

## Moodle API functions expected
- `local_novalxpapi_create_course`
- `local_novalxpapi_add_section`
- `local_novalxpapi_add_page`
- `local_novalxpapi_create_quiz`
