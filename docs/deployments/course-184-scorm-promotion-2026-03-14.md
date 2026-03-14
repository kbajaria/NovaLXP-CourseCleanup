# Course 184 SCORM Promotion Record

- Date (UTC): 2026-03-14
- Course: `184` `Finova Onboarding Programme`
- Section: `844` `Compliance Training (Mandatory)`
- Environments: `dev`, `test`, `production`

## Objective

Align the onboarding programme across environments so that:

- the compliance items in section `844` are native SCORM activities rather than legacy URL-based links
- course completion criteria reference onboarding activities directly
- all available completion-tracked onboarding activities are selected for course completion
- the outdated compliance note is removed from the section intro text

## Changes Applied

### 1. Native SCORM activities

Native SCORM activities are now used for:

- `Bribery Prevention`
- `Data Protection`
- `Display Screen Equipment`
- `Fraud Prevention`
- `Information Security`
- `Responsible Use of Social Media`

Environment-specific SCORM module ids after migration:

`dev`
- `1113`
- `1114`
- `1115`
- `1116`
- `1117`
- `1118`

`test`
- `1049`
- `1050`
- `1051`
- `1052`
- `1053`
- `1054`

`production`
- `1085`
- `1086`
- `1087`
- `1088`
- `1089`
- `1090`

### 2. Legacy URL-based compliance links removed

The old URL activities that linked to standalone compliance courses were removed from `test` and `production` after SCORM verification.

Removed URL activity ids:

- `862`
- `863`
- `864`
- `865`
- `866`
- `867`

### 3. Course completion criteria updated

Course `184` completion criteria were changed from the legacy course-based compliance model to activity-based completion criteria referencing onboarding activities.

The old `criteriatype = 8` rows pointing at courses `105` to `110` were removed.

The onboarding course now uses `criteriatype = 4` activity criteria only.

### 4. All tracked onboarding activities selected

All visible activities in course `184` with completion tracking enabled are now included in course completion criteria in all environments.

This currently includes:

- quizzes:
  - `820`
  - `824`
  - `828`
  - `832`
  - `836`
  - `840`
  - `848`
  - `852`
  - `856`
  - `860`
- page:
  - `846` `Security Overview (Open to Read)`
- SCORM:
  - `dev`: `1113` to `1118`
  - `test`: `1049` to `1054`
  - `production`: `1085` to `1090`

### 5. Section intro note removed

The outdated note about compliance courses being marked "Done" upon viewing was removed from the section `844` intro label (`label id 96`) in:

- `dev`
- `test`
- `production`

## Verification

Verified by live Moodle database inspection via AWS SSM:

- `dev`, `test`, and `production` now contain native SCORM activities in section `844`
- `test` and `production` no longer contain the old visible URL-based compliance items
- all three environments now use activity-based completion criteria for course `184`
- all currently tracked onboarding activities are included in the course completion criteria
- section `844` intro text is aligned across environments

## Supporting Artifact

Formal change write-up:

- [course-184-scorm-completion-remediation-2026-03-14.md](/Users/kamilabajaria/Projects/NovaLXP-Courses/docs/deployments/course-184-scorm-completion-remediation-2026-03-14.md)
