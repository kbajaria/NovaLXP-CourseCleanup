# Course Factory Release Checklist

## Before Dev

- AWS Lambda exists and is configured for `dev`
- Moodle API token exists and can call all required `local_novalxpapi` functions
- OpenAI key exists in Secrets Manager
- Moodle EC2 role can invoke the Lambda
- Lambda role can read both Moodle and OpenAI secrets

## Dev Deployment

- Apply `local_novalxpapi` update
- Install/update `local_novalxpcoursefactory`
- Run Moodle upgrade
- Purge caches
- Configure plugin settings
- Run one end-to-end learner test

## Dev Exit Criteria

- course created in `AI-Generated`
- five-question quiz created
- learners can self-enrol
- passing the quiz marks course completion
- CloudWatch logs and Moodle logs are clean enough to explain any warnings

## Test Deployment

- Use the same code artifacts
- Use `novalxp-course-factory-test`
- Use test Moodle token and test secrets
- Repeat learner validation

## Production Deployment

- Use the same code artifacts already validated in test
- Use `novalxp-course-factory-production`
- Use production Moodle token and production secrets
- Validate with a single controlled course brief first

## Rollback

- disable `local_novalxpcoursefactory` in Moodle settings
- revert or remove the plugin if needed
- leave `local_novalxpapi` extension in place unless it proves faulty
- disable or ignore the Lambda if front-page entry is turned off
