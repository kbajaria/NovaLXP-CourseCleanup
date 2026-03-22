# Deployment Log

Use this file as the top-level chronological log for deployments across `dev`, `test`, and `production`.

Purpose:
- keep one index of environment promotions without relying on PR approval events
- show when a change first reached `dev`, `test`, or `production`
- link each deployment back to its detailed record in `docs/deployments/`

## Entries

| Date | Environment | PR | Commit | Summary | Deployment Record |
| --- | --- | --- | --- | --- | --- |
| 2026-03-22 | `dev`, `test`, `production` | — | `11e2ff8` | AI quality scoring via Bedrock added to course factory; WAF webservice allowlist; bug fixes | [docs/deployments/all-envs-ai-quality-scoring-2026-03-22.md](deployments/all-envs-ai-quality-scoring-2026-03-22.md) |
| 2026-03-20 | `production` | [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1) | `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9` | Promoted TalentLMS migration request feature to production | [docs/deployments/prod-talentlms-migration-request-2026-03-20.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-talentlms-migration-request-2026-03-20.md) |
| 2026-03-20 | `test` | [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1) | `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9` | Promoted TalentLMS migration request feature to test | [docs/deployments/test-talentlms-migration-request-2026-03-20.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/test-talentlms-migration-request-2026-03-20.md) |
| 2026-03-20 | `dev` | [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1) | `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9` | Deployed TalentLMS migration request feature to dev and corrected pane mapping/UI rollout | [docs/deployments/dev-talentlms-migration-request-2026-03-20.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/dev-talentlms-migration-request-2026-03-20.md) |

## Notes

- Keep this log for all environment deployments.
- Keep [docs/production-release-log.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/production-release-log.md) as the stricter production-only release index.
