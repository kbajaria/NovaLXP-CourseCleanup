# NovaLXP Course Ops Artifacts

Artifacts and runbooks for repeatable course-content changes in NovaLXP (Moodle 5.3.1) across `dev`, `test`, and `production`.

## Initial change in this repo
- Course target: `course/section.php?id=918`
- Add final section linking to external Google Skills course
- Include learner guidance and a styled button
- Include a manual completion step for learners
- Preserve relative URLs for NovaLXP internal links

## Repository layout
- `docs/` implementation runbooks and change records
- `docs/production-release-log.md` top-level index of releases that reached `production`
- `docs/runbooks/` reusable course-factory runbooks
- `templates/` ready-to-paste Moodle HTML snippets
- `scripts/` helper scripts for environment discovery, bootstrap, and course-factory guardrails
- `NovaLXP-CourseCleanup/` cleanup and maintenance artifacts/scripts for Moodle course-catalog operations

## Quick start
1. Review the change runbook:
   - `docs/course-918-google-skills-change.md`
2. For legacy course rebuilds from TalentLMS:
   - `docs/talentlms-to-novalxp-migration-runbook.md`
   - `templates/talentlms-course-template/`
   - `docs/talentlms-catalog-seed.sample.json`
   - `docs/finova-courses-seed-active.json`
   - `docs/deploy-talentlms-migration-request-dev.md`
   - `docs/deployments/dev-talentlms-migration-request-2026-03-20.md`
3. Review environment/domain reference:
   - `docs/environment-endpoints.md`
4. Review production release history/process:
   - `docs/production-release-log.md`
   - `docs/runbooks/production-release-process.md`
5. (Optional) Discover ALB hostnames once AWS credentials are configured:
   - `./scripts/discover_alb_domains.sh eu-west-2`
6. Apply the Moodle UI change in `dev` first, then `test`, then `production`.

## Course factory standard (quiz-driven completion)
For new courses where passing a quiz should complete the course, use:
- Runbook: [/Users/kamilabajaria/Projects/NovaLXP-Courses/docs/runbooks/course-factory-quiz-completion-guardrails.md](/Users/kamilabajaria/Projects/NovaLXP-Courses/docs/runbooks/course-factory-quiz-completion-guardrails.md)
- Guardrail script: [/Users/kamilabajaria/Projects/NovaLXP-Courses/scripts/course_factory/moodle_quiz_guardrails.php](/Users/kamilabajaria/Projects/NovaLXP-Courses/scripts/course_factory/moodle_quiz_guardrails.php)
- Quiz config template: [/Users/kamilabajaria/Projects/NovaLXP-Courses/templates/course-factory-quiz-config.template.json](/Users/kamilabajaria/Projects/NovaLXP-Courses/templates/course-factory-quiz-config.template.json)

## AWS credentials note
This workstation currently has no configured AWS credentials. Run `aws login` (or your org credential process) before using discovery scripts.

## GitHub remote setup
If GitHub CLI is authenticated, run:
- `./scripts/create_github_repo.sh novalxp-course-ops`

Otherwise, create a remote repo manually and then:
- `git remote add origin <repo-url>`
- `git push -u origin main`
