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
3. set plugin config for the environment Lambda name and region
4. purge caches
5. run one learner test

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
