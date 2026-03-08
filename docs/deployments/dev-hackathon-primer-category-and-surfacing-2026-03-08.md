# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Theme: `Edutor`

## Change applied
Adjusted the first-time hackathon pathway so it is surfaced as a visible primer experience in dev:

1. Created a dedicated course category:
   - Category id `15`
   - Name: `Hackathon Primer`

2. Moved the five hackathon-primer courses into category `15`:
   - `209` `Hackathon Pathway 1 of 4: Digital Basics`
   - `210` `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
   - `211` `Hackathon Pathway 3 of 4: Agent Foundations`
   - `212` `Hackathon Pathway 4 of 4: Data and Integration Foundations`
   - `213` `Start Here: First-Time Hackathon Pathway`

3. Updated Edutor front-page featured carousel Pane 1 block 2:
   - Title: `Start Here: First-Time Hackathon Pathway`
   - URL: `/course/view.php?id=213`
   - Image: `/ai.png`
   - Summary text updated to describe the four-course primer

4. Updated the default dashboard featured HTML block:
   - Added a new button for course `213`
   - Kept the existing Google Workspaces button as a second option
   - Adjusted the heading from singular to plural (`Featured courses`)

5. Reset student dashboards after updating the default dashboard source:
   - Student dashboards reset: `73`

6. Purged Moodle caches after the change.

## Verification summary
- Category `Hackathon Primer` exists and is visible.
- Courses `209` to `213` all point to category `15`.
- `theme_edutor` Pane 1 block 2 now points to course `213`.
- The system-context default dashboard featured HTML block now contains the primer button and the existing Google Workspaces button.

## Execution method
- Host-side Moodle PHP update executed over AWS SSM on the dev app instance
- Dashboard reset performed through Moodle library function `my_reset_page(...)` for student-role users only
- Cache purge executed with:
  - `php /var/www/moodle/admin/cli/purge_caches.php`

## Notes
- This change resets dashboard layout/content for student-role users, not every site user.
- The front-page featured carousel update changes block 2 only; the rest of the Pane 1 ordering remains unchanged.
