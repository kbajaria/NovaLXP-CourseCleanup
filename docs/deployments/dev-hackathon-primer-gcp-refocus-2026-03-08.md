# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Category: `Hackathon Primer` (`id=15`)

## Change applied
Refocused the beginner hackathon primer content on Google Cloud Platform, with explicit emphasis on Google Cloud Console and GCP Cloud Workstations instead of local-editor workflows such as VS Code.

## Source changes
- Updated learner-facing pathway copy so course 2 is now named `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
- Updated pathway navigation copy in adjacent courses so the sequence consistently references the Cloud Workstations course by name
- Updated course 2 page content to teach browser-based terminal use, Google Cloud Console navigation, Cloud Workstations, repo usage inside the workstation, and GCP project/environment context
- Updated course 2 quiz naming to match the new Cloud Workstations framing
- Retained the previously-audited YouTube source rules:
  - all linked videos are under 1 hour
  - sources are attributable to approved English-speaking geographies

## Dev sync and Moodle updates
- Synced the authored pathway content with:
  - `python3 scripts/course_factory/sync_learning_pathway_via_ssm.py hackathon-first-timers-learning-path --instance-id i-0cbdd881027b14e09 --region eu-west-2`
- Updated the existing Moodle quiz and quiz section label for course `210` to:
  - `Hackathon GCP Cloud Workstations Basics — Quiz`

## Verification summary
- Course `210` fullname is now `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
- Course `210` remains in category `Hackathon Primer` (`id=15`)
- Course `210` still has exactly one quiz:
  - quiz id `92`
  - course module id `1102`
- Course completion criterion still points to that quiz module:
  - `course_completion_criteria.criteriatype = 4`
  - `moduleinstance = 1102`
- Course `210` section names now include:
  - `Cloud Workstations and project folders`
  - `Repos, README-driven work, and staying inside the workstation`
  - `Hackathon GCP Cloud Workstations Basics — Quiz`

## Notes
- File names in the authored source still include one legacy internal filename, `section-02-vscode-and-folders.md`, but its learner-facing content and section title are now Cloud Workstations-specific.
- No manual browser QA was performed for this change set.
