# Pathway Badge Rollup Fix

- Date (UTC): 2026-03-08
- Scope: dev, test, production
- Learning path: `hackathon-first-timers-learning-path`

## Problem
The original badge configuration awarded the badge after course 1 completed. That was incorrect for the pathway design because the badge should represent completion of the full four-course sequence.

## Change applied
Moved the badge criterion from the orientation course to the pathway hub course in all three environments and renamed the badge to reflect pathway-level completion:

- New badge name: `First-Time Hackathon Pathway Completion Badge`
- Dev hub course: `213`
- Test hub course: `206`
- Production hub course: `211`

## Environment results
- Dev:
  - badge id `3`
  - moved from course `209` to course `213`
  - criterion changed from `course_209 = 209` to `course_213 = 213`
  - removed `1` incorrect issued badge row and `2` related `badge_criteria_met` rows
- Test:
  - badge id `2`
  - moved from course `202` to course `206`
  - criterion changed from `course_202 = 202` to `course_206 = 206`
  - no badge issuances needed cleanup
- Production:
  - badge id `2`
  - moved from course `207` to course `211`
  - criterion changed from `course_207 = 207` to `course_211 = 211`
  - no badge issuances needed cleanup

## Verification summary
- Dev badge now points to course `213` and has `0` issued records
- Test badge now points to course `206` and has `0` issued records
- Production badge now points to course `211` and has `0` issued records
- Each hub course still has `4` completion dependency criteria, one for each child course

## Deployment method
- Added helper script:
  - `scripts/course_factory/rehome_badge_to_pathway_hub_via_ssm.py`
- Applied with AWS SSM against each Moodle host

## Notes
- The badge image asset was not changed in this fix.
- No manual browser QA was performed after the badge reconfiguration.
