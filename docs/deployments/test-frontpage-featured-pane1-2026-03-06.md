# Test Deployment Record

- Date (UTC): 2026-03-06
- Environment: test
- Host: `i-00c24ea634d4728ba` (`test-moodle-app`)
- Moodle wwwroot: `https://test.novalxp.co.uk`
- Theme: `Edutor`
- Setting area: `Frontpage Featured Section`
- Pane: `1`

## Change applied
Aligned test Featured Pane 1 to the same target configuration validated in dev.

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
Applied same image mapping pattern as dev:
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
- Updated Edutor SCSS override segment (`NOVALXP_PANE1_IMAGE_FIX_*`) to enforce visible image rendering.
- Updated `theme_edutor` stored-file image areas `pane1block1image` through `pane1block9image`.

## Verification checks
- Frontpage renders expected links for blocks 1-9.
- `Google Workspaces for MS Office Users` appears in block 3 with Google image override.
- Last card (`course 110`) renders with image (`fintech.png`).
- Image assets return `HTTP 200` from test host.

## Execution method
- AWS SSM (`AWS-RunShellScript`) on test Moodle app instance.
- Moodle cache purge via `admin/cli/purge_caches.php`.
