# Production Deployment Record

- Date (UTC): 2026-03-06
- Environment: production
- Host: `i-02bcf20804a48b781` (`prod-moodle-app`)
- Moodle wwwroot: `https://learn.novalxp.co.uk`
- Theme: `Edutor`
- Setting area: `Frontpage Featured Section`
- Pane: `1`

## Change applied
Applied the same final Featured Pane 1 configuration used in dev/test.

Pane 1 course configuration (ordered):
- `184` `Finova Onboarding Programme`
- `198` `Aha! Roadmaps for Beginners: Create Your First Roadmap`
- `195` `Google Workspaces for MS Office Users`
- `105` `Bribery Prevention Refresher`
- `106` `Data Protection`
- `107` `Display Screen Equipment`
- `108` `Fraud Prevention`
- `109` `Information Security`
- `110` `Responsible Use of Social Media`

Pane 1 URL configuration (ordered):
- `/course/view.php?id=184`
- `/course/view.php?id=198`
- `/course/view.php?id=195`
- `/course/view.php?id=105`
- `/course/view.php?id=106`
- `/course/view.php?id=107`
- `/course/view.php?id=108`
- `/course/view.php?id=109`
- `/course/view.php?id=110`

## Image configuration
Applied production mapping to match approved dev visual:
- Block 1 -> `/course_images/Onboarding.png`
- Block 2 -> `/course_images/ai.png`
- Block 3 (course `195`) -> `/course_images/course195-google.png`
- Block 4 -> `/course_images/Risk_Compliance.png`
- Block 5 -> `/course_images/Risk_Compliance.png`
- Block 6 -> `/course_images/Onboarding.png`
- Block 7 -> `/course_images/Risk_Compliance.png`
- Block 8 -> `/course_images/Risk_Compliance.png`
- Block 9 (course `110`) -> `/course_images/fintech.png`

Additional actions:
- Exported course `195` overview image to `/course_images/course195-google.png`.
- Updated Edutor SCSS override segment (`NOVALXP_PANE1_IMAGE_FIX_*`).
- Updated `theme_edutor` stored-file image areas `pane1block1image` through `pane1block9image`.

## Verification checks
- Homepage HTML shows expected links for blocks 1-9:
  - block 2 -> `/course/view.php?id=198`
  - block 3 -> `/course/view.php?id=195`
  - block 9 -> `/course/view.php?id=110`
- Production CSS contains expected image rules for blocks 2, 3, and 9.
- `https://learn.novalxp.co.uk/course_images/course195-google.png` returns `HTTP 200`.
- `https://learn.novalxp.co.uk/course_images/fintech.png` returns `HTTP 200`.

## Execution method
- AWS SSM (`AWS-RunShellScript`) on production Moodle app instance.
- Moodle cache purge via `admin/cli/purge_caches.php`.
