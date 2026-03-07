# Course Factory Release Manifest

## Code artifacts

- Moodle plugin:
  - [/Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory](/Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory)
- Lambda package:
  - [/Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory](/Users/kamilabajaria/Projects/NovaLXP-Courses/aws/lambda-course-factory)
- `local_novalxpapi` extension:
  - [/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch](/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch)

## AWS naming convention

- Lambda function: `novalxp-course-factory-<env>`
- Lambda role: `novalxp-course-factory-<env>-lambda-role`
- Moodle API secret: `novalxp/course-factory/<env>/moodle-api`
- OpenAI secret: `novalxp/course-factory/<env>/openai`

## Moodle dependencies

Required `local_novalxpapi` service functions:

- `local_novalxpapi_create_course`
- `local_novalxpapi_add_section`
- `local_novalxpapi_add_page`
- `local_novalxpapi_create_quiz`
- `local_novalxpapi_apply_quiz_completion_guardrails`

## Promotion gates

`dev` to `test`
- front-page form visible
- one generated course created successfully
- quiz completion marks the course complete
- CloudWatch and Moodle logs show no unresolved errors

`test` to `production`
- same checks repeated in test
- no unexpected enrolment or permission issues
- generated course structure acceptable to stakeholders
