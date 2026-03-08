# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`

## Change applied
Refreshed the YouTube links used in the hackathon primer pathway content.

## Selection changes
- Removed long-form links over 1 hour
- Removed the MCP playlist link and replaced it with a single video
- Replaced several creator links with shorter videos from channels attributable to approved English-speaking sources
- Synced the updated page content into the existing dev pathway courses

## Guardrails now met
- No linked YouTube video in the pathway source exceeds 1 hour
- Current selected channels are attributed to approved sources in the US or other approved English-speaking geographies

## Source artifacts updated
- `hackathon-first-timers-learning-path/`
- `hackathon-first-timers-learning-path/video-source-audit.md`

## Dev sync method
- `scripts/course_factory/sync_learning_pathway_via_ssm.py`

## Verification summary
- Updated course content synced successfully to course ids `209` to `213`
- Long links removed, including:
  - Google Cloud full course (`4+` hours)
  - MCP playlist (`2+` hours total)
- Video audit file records selected channel, duration, and rationale
