# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Category: `Hackathon Primer` (`id=15`)

## Change applied
Updated course `209` (`Hackathon Pathway 1 of 4: AI Hackathon Orientation`) in two ways:

- replaced the "why organizations run AI hackathons" video with a mortgage-specific Google Cloud video
- created and configured a course completion badge for successful learners

## Course content update
- Replaced:
  - `Common business use cases for generative AI`
- With:
  - `How to fast track the home loan application process with Lending DocAI`
  - `https://www.youtube.com/watch?v=e094iq4gWZE`

Updated source files:
- `hackathon-first-timers-learning-path/hackathon-digital-basics/content/section-03-reading-technical-instructions.md`
- `hackathon-first-timers-learning-path/hackathon-digital-basics/media/youtube-links.md`
- `hackathon-first-timers-learning-path/video-source-audit.md`

## Badge asset
- Created a square PNG badge asset at:
  - `hackathon-first-timers-learning-path/hackathon-digital-basics/media/ai-hackathon-orientation-badge.png`
- Working render output also saved at:
  - `output/imagegen/ai-hackathon-orientation-badge.png`

## Moodle badge configuration
- Created course badge:
  - badge id `3`
  - name `AI Hackathon Orientation Completion Badge`
- Badge is attached to course `209`
- Badge status is active:
  - `BADGE_STATUS_ACTIVE = 1`
- Badge criteria:
  - overall criteria id `5`
  - course completion criteria id `6`
  - course criteria param `course_209 = 209`

## Verification summary
- Course content synced successfully into dev with:
  - `python3 scripts/course_factory/sync_learning_pathway_via_ssm.py hackathon-first-timers-learning-path --instance-id i-0cbdd881027b14e09 --region eu-west-2`
- Badge image files were stored in Moodle for badge `3`
- Badge remains active and course-scoped to course `209`
- No badges had been issued yet at verification time

## Notes
- The badge image was generated locally without the OpenAI Image API because `OPENAI_API_KEY` was not set in the shell environment at deployment time.
- No manual browser QA was performed for the course page or badge display.
