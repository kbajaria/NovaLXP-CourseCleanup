# Course 184 SCORM Completion Remediation

- Date (UTC): 2026-03-14
- Course: `184` `Finova Onboarding Programme`
- Section: `844` `Compliance Training (Mandatory)`
- Environments updated: `dev`, `test`, `production`

## Summary

This change corrected how compliance SCORM modules in the Finova Onboarding Programme are tracked for completion.

Under the previous Moodle course completion behavior, a compliance SCORM activity could appear as "done" after the learner viewed it, even if the learner had not yet passed the associated compliance quiz inside the SCORM package. This was a limitation of the previous version of the Moodle course completion plugin in relation to SCORM completion tracking.

Importantly, this did **not** allow a learner to complete the overall Onboarding Programme without passing the required compliance quizzes. The programme-level completion logic still required completion of the relevant compliance requirements. The incorrect behavior was at the activity display level: individual compliance modules could show as "done" too early.

We have now deployed a newer version of the Moodle course completion plugin and aligned course configuration to use native SCORM activities and activity-based course completion criteria. With the new plugin version and the configuration changes completed on 2026-03-14, compliance SCORM modules are no longer marked "done" simply by being viewed. They are now treated as complete only when the associated SCORM completion condition has been satisfied, which in this implementation is tied to successful completion of the relevant compliance assessment.

## Original Behavior

Before remediation:

- The onboarding course included a compliance section that historically depended on older URL-based compliance links and legacy course-level completion relationships.
- In practice, compliance items in the onboarding course could display as completed once viewed.
- This created the impression that a learner had completed the compliance module even when the embedded quiz or assessment had not yet been passed.

At the same time:

- The learner could **not** complete the full Onboarding Programme without satisfying the required compliance conditions.
- The defect therefore affected the visible completion status of the compliance modules, not the integrity of the programme-level pass requirement.

## Root Cause

The behavior was caused by a combination of legacy configuration and an older completion-tracking implementation for SCORM activities:

1. The previous course completion setup relied on older course-level completion relationships and legacy URL-based compliance links rather than fully native SCORM activities inside the onboarding course.
2. The previous plugin behavior did not correctly enforce the desired SCORM completion semantics for these onboarding compliance modules.
3. As a result, the compliance activity could be shown as complete when viewed, even though the associated SCORM quiz had not yet been passed.

This was a limitation of the previous Moodle course completion plugin version, not a case where the onboarding programme itself could be passed without meeting the compliance assessment requirement.

## Remediation Performed

The following remediation was completed:

### 1. Compliance content was migrated to native SCORM activities

The compliance items in section `844` were aligned to use real SCORM activities rather than the older URL-based setup.

The following SCORM activities are now present as native SCORM modules:

- `Bribery Prevention`
- `Data Protection`
- `Display Screen Equipment`
- `Fraud Prevention`
- `Information Security`
- `Responsible Use of Social Media`

### 2. Legacy URL-based compliance items were removed

The old URL-based compliance items were first hidden and then deleted in non-dev environments after verification, so learners now interact only with the SCORM activities.

### 3. Course completion criteria were updated

The onboarding course completion criteria were moved away from the old course-based compliance dependency model and updated to use activity-based completion criteria.

The completion criteria now reference the actual tracked onboarding activities, including the compliance SCORM modules.

### 4. All available completion-tracked activities were selected for course completion

Following the later change request on 2026-03-14, all activities in course `184` that have completion tracking enabled are now included in the course completion criteria.

This includes:

- the knowledge check quizzes
- the tracked security page activity
- the six compliance SCORM modules

### 5. Section messaging was corrected

The following note was removed from section `844`:

> Note: Compliance courses will be marked "Done" upon viewing. However, you must achieve a passing grade on all exams in order for your overall Onboarding Programme to be marked complete.

That message no longer reflects the system behavior after the plugin upgrade and remediation work.

## Final Behavior After Fix

After the plugin upgrade and the remediation changes:

- Compliance SCORM modules in the Onboarding Programme are no longer marked "done" simply because a learner viewed them.
- The visible completion status of each compliance SCORM activity now aligns with successful completion of the module's required SCORM condition.
- The overall Onboarding Programme completion criteria now reference the onboarding course's actual tracked activities rather than the old standalone compliance-course relationship.
- The user-facing messaging in the compliance section now matches the actual system behavior.

## Assurance Statement

At no point did the earlier issue allow a learner to complete the full Finova Onboarding Programme without first passing all required compliance quizzes. The issue was limited to the way individual compliance modules could appear as completed in the UI under the previous plugin behavior.

The current implementation resolves that inconsistency. The compliance SCORM modules now behave as expected, and the onboarding programme's completion logic is aligned with the actual tracked compliance activities.

## Environments

The remediation has been completed in:

- `dev`
- `test`
- `production`
