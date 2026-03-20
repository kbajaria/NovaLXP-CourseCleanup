# Production Release Process

Use this short process whenever a PR is promoted to `production`.

## Before Release

1. Confirm the PR was reviewed and merged.
2. Confirm the exact commit or merge SHA being promoted.
3. Confirm `dev` and `test` validation is complete, if those environments are part of the path.
4. Prepare or update the detailed production deployment record under `docs/deployments/`.

## During Release

1. Deploy to `production`.
2. Capture:
   - environment
   - target host or service
   - release commit
   - important config values
   - validation steps performed
   - rollback notes if relevant

## After Release

1. Add the release to [docs/production-release-log.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/production-release-log.md).
2. Link:
   - PR
   - commit
   - deployment record
3. Mark the release status.
4. If the release was rolled back or partially released, update the same row instead of creating conflicting entries.

## Naming Convention

Detailed production deployment records should use:

- `docs/deployments/prod-<change>-YYYY-MM-DD.md`

Examples:
- `docs/deployments/prod-frontpage-featured-pane1-2026-03-06.md`
- `docs/deployments/prod-course-198-aha-roadmaps-2026-03-06.md`
