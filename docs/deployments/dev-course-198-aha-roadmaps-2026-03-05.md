# Dev Deployment Record

- Date (UTC): 2026-03-05
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Course id: `198`
- Course shortname: `aha-roadmaps-beginners`
- Category: `AI-Generated` (`id=5`)

## Change applied
Deployed a new course in dev:
- Full name: `Aha! Roadmaps for Beginners: Create Your First Roadmap`
- Summary set from local manifest
- Completion tracking enabled at course level

Created content structure:
- 6 named sections (`00` to `05`)
- 6 page activities (one per section)
- 1 quiz activity:
  - Quiz id: `78`
  - Course module id: `997`
  - Name: `Aha! Roadmaps for Beginners — Quiz`
  - Imported questions from `quiz/questionbank.gift`

## Enrollment and completion settings
- Self-enrolment is enabled and open (`status=0`, `allow new enrolments=1`)
- Quiz completion requires passing grade:
  - `course_modules.completion = 2`
  - `course_modules.completionpassgrade = 1`
- Quiz grade item pass mark: `80`
- Course completion criterion includes grade pass requirement (`criteriatype=6`, `gradepass=80`)

## Verification checks
- Course exists in `AI-Generated` category.
- Open self-enrolment instance present.
- Quiz exists and is visible in the course.
- Course-level completion criterion requires passing score.
- Module counts in course:
  - `page`: `6`
  - `quiz`: `1`
  - `forum`: `1` (default)

## Follow-up fixes (2026-03-05)
- Primer internal MP4 now hosted on dev app and embedded with a `<video>` player:
  - `https://dev.novalxp.co.uk/local/novalxpapi/media/The_Story_of_Your_Strategy.mp4`
- Added explicit `Activity completion` course criterion for the quiz (module `quiz`, moduleinstance `997`) so the quiz appears checked in completion settings.
- Kept `Course grade` criterion at `80` pass mark. Both criteria are now present.
- Re-rendered all section summaries from Markdown to HTML to prevent raw Markdown appearing in section descriptions when `summaryformat` is HTML.

## Follow-up fixes (2026-03-06)
- Learner completion issue (`0%` after passing quiz):
  - Retained quiz activity completion rule (`completion=2`, `completionpassgrade=1`)
  - Removed course-grade completion criterion (`criteriatype=6`) for this course to avoid dependency on course total grade aggregation
  - Kept explicit quiz activity completion criterion (`criteriatype=4`)
- Answer order issue (correct answer always option A):
  - Enabled quiz-level answer shuffling (`quiz.shuffleanswers=1`)
  - Enabled multichoice answer shuffling on all quiz-context imported questions (`qtype_multichoice_options.shuffleanswers=1` for 12 questions)
