# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Category: `AI-Generated` (`id=5`)

## Change applied
Deployed a new beginner-first hackathon preparation set for the Tech Enablement Track, then refactored it into an ordered pathway implementation that works within core Moodle.

Created courses:

1. Course id `209`
   - Shortname: `hackathon-digital-basics`
   - Full name: `Hackathon Pathway 1 of 4: Digital Basics`
   - URL: `https://dev.novalxp.co.uk/course/view.php?id=209`
   - Quiz id `88`
   - Quiz course module id `1075`

2. Course id `210`
   - Shortname: `hackathon-terminal-github-cloud-basics`
   - Full name: `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
   - URL: `https://dev.novalxp.co.uk/course/view.php?id=210`
   - Quiz id `89`
   - Quiz course module id `1083`

3. Course id `211`
   - Shortname: `hackathon-agent-and-subagent-basics`
   - Full name: `Hackathon Pathway 3 of 4: Agent Foundations`
   - URL: `https://dev.novalxp.co.uk/course/view.php?id=211`
   - Quiz id `90`
   - Quiz course module id `1091`

4. Course id `212`
   - Shortname: `hackathon-data-rag-mcp-maps-rehearsal`
   - Full name: `Hackathon Pathway 4 of 4: Data and Integration Foundations`
   - URL: `https://dev.novalxp.co.uk/course/view.php?id=212`
   - Quiz id `91`
   - Quiz course module id `1099`

5. Learning-path overview course id `213`
   - Shortname: `hackathon-first-timers-tech-enablement`
   - Full name: `Start Here: First-Time Hackathon Pathway`
   - URL: `https://dev.novalxp.co.uk/course/view.php?id=213`
   - Contains a single start-here page linking to the four recommended courses in order
   - Course completion is configured as a rollup of the four pathway courses

## Content structure
- Each of the four training courses contains:
  - 6 named sections
  - 6 page activities
  - 1 quiz activity
  - learner-facing YouTube references inside the section content and media source files
  - updated welcome and wrap-up content showing pathway position and next course
- The overview course contains:
  - 1 section
  - 1 page activity
  - no quiz
  - pathway instructions and ordered deep links to all four courses

## Completion and quiz settings
Verified on the dev Moodle host for courses `209` to `212`:

- `course.enablecompletion = 1`
- `course_modules.completion = 2` for the quiz
- `course_modules.completionpassgrade = 1` for the quiz
- `quiz.shuffleanswers = 1`
- `grade_items.gradepass = 80`
- `course_completion_criteria` contains only activity-based quiz completion (`criteriatype = 4`)

Overview course `213`:

- visible
- no quiz
- `course.enablecompletion = 1`
- `course_completion_criteria` contains four course dependency criteria (`criteriatype = 8`) for courses `209`, `210`, `211`, and `212`

## Verification summary
- All five courses are visible in `AI-Generated`.
- Each training course has `pagecount = 6`.
- Each training course has `quizcount = 1`.
- The overview course has `pagecount = 1` and `quizcount = 0`.
- The overview course is the pathway rollup course.
- URLs were generated and recorded at deployment time.

## Deployment method
- Source content: `hackathon-first-timers-learning-path/`
- Local deploy utility used:
  - `scripts/course_factory/deploy_authored_course.py`
- Local pathway sync utility used:
  - `scripts/course_factory/sync_learning_pathway_via_ssm.py`
- Moodle credentials source:
  - AWS Secrets Manager secret `novalxp/course-factory/dev/moodle-api`
