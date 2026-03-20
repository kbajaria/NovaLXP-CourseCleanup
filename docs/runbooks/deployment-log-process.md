# Deployment Log Process

Use this short process whenever a change is deployed to `dev`, `test`, or `production`.

## During Deployment

1. Capture:
   - environment
   - target host or service
   - release or feature commit
   - important config values
   - validation steps performed
   - rollback notes if relevant
2. Create or update the detailed environment deployment record under `docs/deployments/`.

## After Deployment

1. Add the deployment to [docs/deployment-log.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployment-log.md).
2. If the environment is `production`, also add the release to [docs/production-release-log.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/production-release-log.md).
3. Link:
   - PR if applicable
   - commit
   - deployment record
4. Keep the summary short and environment-specific.

## Naming Convention

Detailed deployment records should use:

- `docs/deployments/dev-<change>-YYYY-MM-DD.md`
- `docs/deployments/test-<change>-YYYY-MM-DD.md`
- `docs/deployments/prod-<change>-YYYY-MM-DD.md`
