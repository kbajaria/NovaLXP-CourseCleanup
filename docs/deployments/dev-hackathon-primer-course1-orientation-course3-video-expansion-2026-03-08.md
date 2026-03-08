# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Category: `Hackathon Primer` (`id=15`)

## Change applied
Updated the pathway per review feedback:

- Course `209` was rewritten from `Digital Basics` into `Hackathon Pathway 1 of 4: AI Hackathon Orientation`
- Course `211` kept the same curriculum but gained additional Google-published video references across its sections
- Courses `210` and `212` were left unchanged in curriculum and structure

## Course 1 changes
- Reframed the course around:
  - what an AI hackathon is
  - what outcomes teams aim for
  - why organizations run AI hackathons
  - the role of business-focused departments
  - what learners should expect across the two-day event
- Replaced the course 1 quiz with a new orientation quiz:
  - old quiz module deleted: `cmid 1075`
  - new quiz id: `93`
  - new quiz course module id: `1103`
- Removed the stale empty section left behind by the quiz replacement so the course again has a single quiz section

## Course 3 changes
- Preserved the existing curriculum and section structure
- Added more short-form video references, prioritizing Google-published sources:
  - `Intro to AI agents`
  - `Build an AI Agent with Gemini 3`
  - `Build an AI agent with Gemini CLI and Agent Development Kit`
  - `Introduction to Vertex AI Agent Engine`
  - `Build and deploy generative AI agents using natural language with Vertex AI Agent Builder`
  - `Building AI agents on Google Cloud`

## Video sourcing notes
- Prioritized Google-owned channels where possible:
  - `Google Cloud`
  - `Google Cloud Tech`
  - `Google for Developers`
- All newly added videos are under 1 hour

## Dev sync and quiz update method
- Pathway content sync:
  - `python3 scripts/course_factory/sync_learning_pathway_via_ssm.py hackathon-first-timers-learning-path --instance-id i-0cbdd881027b14e09 --region eu-west-2`
- Course `209` quiz replacement:
  - deleted existing Moodle quiz module server-side
  - recreated the quiz through `local_novalxpapi_create_quiz`
  - reapplied completion/pass guardrails through `local_novalxpapi_apply_quiz_completion_guardrails`

## Verification summary
- Course `209` fullname is now `Hackathon Pathway 1 of 4: AI Hackathon Orientation`
- Course `209` has one quiz:
  - quiz id `93`
  - cmid `1103`
- Course `209` completion criterion points to `moduleinstance = 1103`
- Course `209` section names now match the orientation curriculum:
  - `What an AI hackathon is`
  - `What outcomes teams aim for`
  - `Why organizations run AI hackathons`
  - `The role of business-focused departments`
  - `What to expect over two days and wrap-up`
- Course `211` remains:
  - fullname `Hackathon Pathway 3 of 4: Agent Foundations`
  - pagecount `6`
  - quizcount `1`

## Notes
- To keep the pathway labels coherent, course `210` had one prerequisite text reference updated to the new course `209` title, but its curriculum and structure were not otherwise changed.
- No manual browser QA was performed for this change set.
