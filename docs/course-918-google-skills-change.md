# Change Runbook: Course Section 918 (Google Skills Linkout)

## Scope
Add a **new final section** in the course that includes:
- clear text that this launches an external Google Skills course,
- a button styled with existing Moodle/NovaLXP button styles,
- guidance to return to NovaLXP after completion,
- learner-controlled manual completion.

## Target
- Course section editor URL: `course/section.php?id=918`
- External course URL: `https://www.skills.google/course_templates/779`

## Environment strategy
1. Apply in `dev` first (`dev.novalxp.co.uk`).
2. Validate with learner test account.
3. Repeat in `test`.
4. Repeat in `production`.

## Discovered ALBs (AWS eu-west-2)
- `dev-novalxp-alb`: `dev-novalxp-alb-1221185513.eu-west-2.elb.amazonaws.com`
- `test-novalxp-alb`: `test-novalxp-alb-1337136894.eu-west-2.elb.amazonaws.com`
- `prod-novalxp-alb`: `prod-novalxp-alb-1974695819.eu-west-2.elb.amazonaws.com`

## Relative URL policy
- Use **relative URLs** for links back into NovaLXP, e.g. `/course/view.php?id=<courseid>`.
- For this change, use `/course/section.php?id=918` as the return link.
- External Google Skills link remains absolute (`https://...`) because it leaves NovaLXP.

## Implementation steps in Moodle UI
1. Open the course and turn editing on.
2. Add a new section at the end (title suggested: `External Google Skills Course`).
3. In the section summary, paste content from:
   - `templates/course-918-section-summary.html`
4. Add an activity in this section named `Mark this section complete`.
5. Use a simple activity type that supports manual completion (recommended: `Page`):
   - Description: `Use this after you finish the Google Skills course.`
6. In the activity `Completion tracking` settings:
   - Set `Completion tracking` to `Show activity as complete when conditions are met`.
   - Set condition to `Students can manually mark the activity as completed`.
7. Save and return to course.
8. Confirm the section shows:
   - External launch button,
   - Return guidance,
   - A manual completion checkbox/button for the learner activity.

## Acceptance checks
- Launch button opens `https://www.skills.google/course_templates/779`.
- Section text explains external handoff and return instruction.
- Internal return link uses a relative path.
- Learner can manually mark completion in Moodle.

## Rollback
- Delete the added section (or hide it) in the affected environment.

## Notes
- Learner SSO to Google Skills is expected via existing Finova/Google Workspace setup.
- If completion tracking is disabled at course level, enable it before step 7.
