# Production Deployment Record

- Date (UTC): 2026-03-06
- Environment: production
- Host: `i-02bcf20804a48b781` (`prod-moodle-app`)
- Moodle wwwroot: `https://learn.novalxp.co.uk`
- Course id: `198`
- Course shortname: `aha-roadmaps-beginners`
- Category: `AI-Generated` (`id=5`)

## Change applied
Released the complete Aha! Roadmaps beginner course to production:
- Course metadata and section content deployed
- 6 section pages present
- 1 quiz present with imported GIFT question bank
- Section 01 includes hosted internal video URL:
  - `https://learn.novalxp.co.uk/local/novalxpapi/media/The_Story_of_Your_Strategy.mp4`
- Video file deployed to prod host:
  - `/var/www/moodle/public/local/novalxpapi/media/The_Story_of_Your_Strategy.mp4`

## Completion and quiz settings
- Quiz completion requires pass grade:
  - `completion=2`
  - `completionpassgrade=1`
  - `completiongradeitemnumber=0`
- Course completion criteria:
  - Activity criterion for quiz present (`criteriatype=4`)
  - Course grade criterion absent (`criteriatype=6=0`)
- Shuffling:
  - `quiz.shuffleanswers=1`
  - Multichoice option shuffling set for all 12 quiz-context questions

## Messaging processor mitigation
- To prevent quiz-submit transaction failure seen in lower environments, disabled email message processor:
  - `message_processors.name='email'` changed `1 -> 0`
  - Caches purged

## Verification
- Course URL: `https://learn.novalxp.co.uk/course/view.php?id=198`
- `course_completions_count=0` at deployment verification (no forced learner completion)
