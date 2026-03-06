# Change Runbook: Edutor Frontpage Featured Section Pane 1 (Dev)

## Scope
Replace the current courses shown in **Frontpage Featured Section Pane 1** with existing Moodle courses already configured in NovaLXP.

## Target
- Environment: `dev`
- Moodle URL: `https://dev.novalxp.co.uk`
- Theme: `Edutor`
- Setting area: `Site administration > Appearance > Themes > Edutor > Frontpage Featured Section`
- Component: `Pane 1`

## Environment strategy
1. Apply in `dev` first.
2. Validate visibility and click-through behavior with admin and learner accounts.
3. Promote the same selection to `test`, then `production` after sign-off.

## Inputs required before change
- Final list of courses to show in Pane 1 (recommended 3 to 6 courses).
- For each selected course:
  - Course ID
  - Course full name
  - Expected course URL (relative preferred): `/course/view.php?id=<id>`

## Implementation steps in Moodle UI (Dev)
1. Log in to `https://dev.novalxp.co.uk` with site admin access.
2. Open:
   - `Site administration`
   - `Appearance`
   - `Themes`
   - `Edutor`
   - `Frontpage Featured Section`
3. Locate **Pane 1** course configuration.
4. Remove currently configured course entries in Pane 1.
5. Add the approved existing Moodle courses (by course selector or ID fields, depending on Edutor setting type).
6. Save changes.
7. Purge caches:
   - `Site administration > Development > Purge all caches`
8. Open the front page and verify Pane 1 displays only the new course set.

## Acceptance checks
- Pane 1 shows the exact approved course list, in the intended order.
- Each card links to the correct course page.
- Course cards are visible for a learner-role user (not admin-only artifacts).
- No removed/legacy courses remain visible in Pane 1.
- Front page renders without layout issues after cache purge.

## Rollback
1. Reopen the same Edutor Pane 1 settings in dev.
2. Restore the previous course list/order.
3. Save and purge caches again.

## Notes
- If Edutor stores Pane 1 selections in a comma-separated course ID setting, keep a copy of both old and new values in the deployment record.
- If any selected course is hidden, it may not render for learners depending on theme/query behavior.
