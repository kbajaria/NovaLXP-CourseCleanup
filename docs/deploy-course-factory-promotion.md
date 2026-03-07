# Promote Course Factory Across Environments

## Sequence

1. Deploy AWS stack and Moodle plugins in `dev`
2. Validate one end-to-end generated course in `dev`
3. Deploy the same code path in `test`
4. Validate again with a fresh generated course in `test`
5. Deploy to `production`

## Reusable AWS command

Use:

```bash
scripts/aws/deploy_course_factory_stack.sh
```

Environment naming convention:

- Lambda: `novalxp-course-factory-<env>`
- Lambda role: `novalxp-course-factory-<env>-lambda-role`
- Moodle secret: `novalxp/course-factory/<env>/moodle-api`
- OpenAI secret: `novalxp/course-factory/<env>/openai`

## Moodle-side promotion

For each environment:

1. apply the `local_novalxpapi` guardrails update
2. install/update `local_novalxpcoursefactory`
3. run Moodle upgrade so `local_novalxpcoursefactory_update_job` is registered
4. confirm the environment token service includes both callback and guardrail functions
5. set plugin config for the environment Lambda name and region
6. purge caches
7. run one learner test

Important:
- Confirm which external service the environment token actually uses.
- If the token is attached to a restricted manual service such as `CourseCreationAPI`, add `local_novalxpapi_apply_quiz_completion_guardrails` to that service before smoke testing.
- Add `local_novalxpcoursefactory_update_job` to that same service as well.
- Updating only the plugin-defined service registration will not update a separate manual service record already tied to the token.
- The learner flow is asynchronous by design. A correct deployment should show queued/processing state first, then success after polling completes.

## Recommended environment values

`dev`
- Moodle URL: `https://dev.novalxp.co.uk`
- Lambda: `novalxp-course-factory-dev`

`test`
- Moodle URL: set to the test domain in use
- Lambda: `novalxp-course-factory-test`

`production`
- Moodle URL: set to the production domain in use
- Lambda: `novalxp-course-factory-production`
