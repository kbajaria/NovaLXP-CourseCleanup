# Production Release Log

Use this file as the top-level log of PRs and releases that reach `production`.

Purpose:
- keep one chronological index of production releases
- link each release back to its PR, commit, and detailed deployment record
- make it easy to answer "what shipped to production, and when?"

## How To Use This Log

For each production release:
1. Create or update the detailed deployment record in `docs/deployments/`.
2. Add one new row to the table below.
3. Include:
   - release date
   - PR number/link
   - merge commit or release commit
   - short summary
   - deployment record link
   - status

Suggested statuses:
- `released`
- `rolled back`
- `partially released`

## Releases

| Date | PR | Commit | Summary | Deployment Record | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-03-22 | — | `11e2ff8` | AI quality scoring via Bedrock; WAF webservice allowlist; jobqueued lang fix; scorecard fault-tolerance | [docs/deployments/all-envs-ai-quality-scoring-2026-03-22.md](deployments/all-envs-ai-quality-scoring-2026-03-22.md) | released |
| 2026-03-20 | [#1](https://github.com/kbajaria/NovaLXP-CourseCleanup/pull/1) | `3c58b8ba21a6ab9dfcfb2a50c7a27e9f41e9c4a9` | TalentLMS migration request feature released to production | [docs/deployments/prod-talentlms-migration-request-2026-03-20.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-talentlms-migration-request-2026-03-20.md) | released |
| 2026-03-06 | Not recorded | Not recorded | Front-page featured pane 1 production mapping update | [docs/deployments/prod-frontpage-featured-pane1-2026-03-06.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-frontpage-featured-pane1-2026-03-06.md) | released |
| 2026-03-06 | Not recorded | Not recorded | Aha! Roadmaps beginner course released to production | [docs/deployments/prod-course-198-aha-roadmaps-2026-03-06.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-course-198-aha-roadmaps-2026-03-06.md) | released |
| 2026-03-04 | Not recorded | Not recorded | Google Skills course deployment to production | [docs/deployments/prod-course-195-google-skills-2026-03-04.md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-course-195-google-skills-2026-03-04.md) | released |

## Entry Template

Copy this row when adding the next production release:

| YYYY-MM-DD | [#PR](https://github.com/ORG/REPO/pull/PR) | `commitsha` | Short release summary | [docs/deployments/prod-...md](/C:/Users/kbaja/Projects/novalxp-courses/docs/deployments/prod-...md) | released |
