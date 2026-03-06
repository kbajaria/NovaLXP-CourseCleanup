# Test Deployment Record

- Date (UTC): 2026-03-06
- Environment: test
- Host: `i-00c24ea634d4728ba` (`test-moodle-app`)
- Moodle wwwroot: `https://test.novalxp.co.uk`
- Course id: `198`
- Course shortname: `aha-roadmaps-beginners`
- Category: `AI-Generated` (`id=5`)

## Change applied
Migrated the Aha! Roadmaps beginner course changes from dev to test:
- Course metadata and section summaries updated
- 6 section pages present
- 1 quiz present with imported question bank
- Section 01 points to hosted internal MP4 on test:
  - `https://test.novalxp.co.uk/local/novalxpapi/media/The_Story_of_Your_Strategy.mp4`

## Completion and quiz behavior
- Quiz activity completion requires pass grade:
  - `completion=2`
  - `completionpassgrade=1`
  - `completiongradeitemnumber=0`
- Course completion criterion is activity-based for the quiz:
  - `criteriatype=4` present
  - `criteriatype=6` removed
- Answer shuffling enabled:
  - `quiz.shuffleanswers=1`
  - Multichoice question options set to shuffle

## Verification
- Open self-enrolment configured
- Video file exists on test host local filesystem:
  - `/var/www/moodle/public/local/novalxpapi/media/The_Story_of_Your_Strategy.mp4`
- Quiz completion settings and shuffling flags verified

## Explicit non-action
- Did **not** force any learner completion in test.
- `course_completions` count for this course at deploy verification: `0`.

## Follow-up fix (2026-03-06)
- Resolved quiz submit UI stack-trace caused by message processor failure in test:
  - Disabled `email` message processor on test (`message_processors.name='email'`, `enabled=0`)
  - Purged Moodle caches
- Scope: test environment only.
