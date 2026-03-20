# TalentLMS to NovaLXP Migration Runbook

## Goal
Migrate legacy TalentLMS course content into NovaLXP so learners can continue to access useful training after the TalentLMS contract ends.

This runbook assumes the target delivery format in NovaLXP is:
- a standard Moodle course
- section content stored as Moodle pages
- a completion quiz when the course needs a completion signal

## Migration principles
- Preserve learner access to valuable content, not TalentLMS-specific UI behavior.
- Prefer rebuilding content cleanly in NovaLXP over trying to mirror every TalentLMS feature.
- Capture source-of-truth exports before the TalentLMS contract termination date.
- Migrate in batches and validate in `dev`, then `test`, then `production`.
- Keep a mapping of old TalentLMS course identifiers to new NovaLXP course identifiers.

## Recommended content tiers
Classify each TalentLMS course before migrating it.

### Tier 1: Rebuild as a full NovaLXP course
Use when the course is still relevant, compliance-sensitive, or frequently used.

Target shape:
- local course folder with `course.json`
- Markdown content sections
- GIFT quiz and quiz config
- provision into NovaLXP through the course-factory path or manual Moodle build

### Tier 2: Archive as a reference-only course
Use when the course is still useful but does not need tracked completion.

Target shape:
- NovaLXP course with a short intro
- uploaded reference assets or linked documents/videos
- no graded quiz unless reporting is required

### Tier 3: Retire
Use when the content is obsolete, duplicated elsewhere, or no longer appropriate to retain.

Target shape:
- no rebuild
- include decision in migration tracker

## What to export from TalentLMS before shutdown
For every course planned for migration, capture:
- course title
- course short description and full description
- module or lesson structure
- lesson body text
- downloadable files
- embedded video URLs or original video files
- images used in lessons
- quiz questions and answers
- completion requirements
- audience or enrolment notes
- course owner / business sponsor
- source course URL or identifier

Store raw exports in a separate secure location if needed. Do not commit confidential source exports to this repo unless approved.

## Repo workflow for each migrated course
1. Create a new course folder by copying [templates/talentlms-course-template/README.md](/C:/Users/kbaja/Projects/novalxp-courses/templates/talentlms-course-template/README.md) and its sibling files into a new top-level folder named with the future NovaLXP shortname.
2. Fill in `course.json` with the new NovaLXP metadata.
3. Rewrite each TalentLMS lesson into learner-friendly Markdown sections under `content/`.
4. Add media files under `media/` only when they are required and licensed for reuse.
5. Convert assessment questions into `quiz/questionbank.gift`.
6. Configure completion rules in `quiz/quiz-config.json`.
7. Validate the structure against the existing example course in [aha-roadmaps-beginners/course.json](/C:/Users/kbaja/Projects/novalxp-courses/aha-roadmaps-beginners/course.json).
8. Build and test in `dev` first.

## Suggested migration tracker fields
Maintain a CSV or sheet outside this runbook with:
- `SourceCourseId`
- `SourceCourseTitle`
- `Owner`
- `Priority`
- `MigrationTier`
- `AssetsExported`
- `ContentDrafted`
- `QuizDrafted`
- `DevValidated`
- `TestValidated`
- `ProductionLive`
- `NovaLXPCourseId`
- `Notes`

## Authoring guidance
When converting TalentLMS content into NovaLXP:
- remove TalentLMS-specific navigation instructions
- replace "click next" style copy with section headings and clear transitions
- turn slide fragments into complete paragraphs
- normalize tone and terminology across the course
- replace broken embeds with approved file uploads or stable links
- move knowledge checks into the final quiz unless an inline check is essential

## Assessment guidance
Use a quiz when:
- completion tracking matters
- the learner must demonstrate understanding
- a certificate, badge, or compliance signal depends on completion

Skip or simplify the quiz when:
- the course is reference-only
- the source course had no meaningful assessment
- the content is purely informational

## Validation checklist in NovaLXP
For each migrated course, verify:
- title and summary are clear
- all sections render correctly
- images and files load
- external links work
- quiz imports correctly
- pass mark and completion rules are correct
- learner self-enrolment works as expected
- course completion behaves correctly for a learner account

## Retirement and learner continuity
Once a replacement course is live:
- record the new NovaLXP course URL against the old TalentLMS course
- notify stakeholders of the replacement path
- if possible, add redirect or signposting content before TalentLMS is terminated
- use the cleanup workspace under [NovaLXP-CourseCleanup/README.md](/C:/Users/kbaja/Projects/novalxp-courses/NovaLXP-CourseCleanup/README.md) for any related course-catalog hide/delete actions in NovaLXP

## Recommended first batch
Start with 3 to 5 courses that are:
- high-traffic
- low legal/compliance risk
- structurally simple
- still clearly valuable to learners

This gives you a repeatable migration pattern before tackling larger SCORM-heavy or media-heavy courses.
