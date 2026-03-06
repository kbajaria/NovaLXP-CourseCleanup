# Dev Deployment Record

- Date (UTC): 2026-03-06
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Theme: `Edutor`
- Setting area: `Frontpage Featured Section`
- Pane: `1`

## Change applied
Replaced existing course configuration in **Frontpage Featured Section Pane 1** with approved existing Moodle courses.

Previous Pane 1 configuration:
- Course IDs: `7, 5, 6, 8, 43, 42`
- Notes: Blocks 1-6 previously populated; blocks 7-10 were empty.

New Pane 1 configuration:
- Course IDs (ordered): `184, 198, 195, 105, 106, 107, 108, 109, 110`
- Course names (ordered):
  - `Finova Onboarding Programme`
  - `Aha! Roadmaps for Beginners: Create Your First Roadmap`
  - `Google Workspaces for MS Office Users`
  - `Bribery Prevention Refresher`
  - `Data Protection`
  - `Display Screen Equipment`
  - `Fraud Prevention`
  - `Information Security`
  - `Responsible Use of Social Media`

Pane 1 image configuration:
- Block 1 / course `184`: course overview image (`Change_the_manager_in__subject_1__to_be_of_African_descent_.png`)
- Block 2 / course `198`: fallback image (`ai.png`)
- Block 3 / course `195`: course overview image (`Remove_the_text_from_the_digital_screen_and_replace_it_with_a_clean__modern_Google_logo__Maintain_th.png`)
- Block 4 / course `105`: fallback image (`Risk_Compliance.png`)
- Block 5 / course `106`: fallback image (`Risk_Compliance.png`)
- Block 6 / course `107`: fallback image (`Onboarding.png`)
- Block 7 / course `108`: fallback image (`Risk_Compliance.png`)
- Block 8 / course `109`: fallback image (`Risk_Compliance.png`)
- Block 9 / course `110`: fallback image (`fintech.png`)

## Verification checks
- Pane 1 shows only the new configured courses.
- Card order matches configured order.
- Pane 1 blocks 1-9 resolve non-empty `theme_edutor` image URLs (`pluginfile.php/.../theme_edutor/pane1blockNimage/...`).
- Each course card links to expected URL:
  - `/course/view.php?id=184`
  - `/course/view.php?id=198`
  - `/course/view.php?id=195`
  - `/course/view.php?id=105`
  - `/course/view.php?id=106`
  - `/course/view.php?id=107`
  - `/course/view.php?id=108`
  - `/course/view.php?id=109`
  - `/course/view.php?id=110`
- Verified as learner-role user.
- Caches purged after config save.

## Execution method
- Moodle admin UI update in dev.
- Theme cache purge via Moodle admin (`Purge all caches`).

## Follow-up
- If dev validation passes, apply same course IDs/order to `test`, then `production`.

## Follow-up fix (images rendering dark/blank)
- Symptom observed in dev UI: Pane 1 image areas appeared dark/blank despite configured image URLs.
- Applied dev-only theme SCSS override in `theme_edutor` setting `scss`:
  - Forced explicit Pane 1 background-image URLs to public `/course_images/*` assets for blocks 1-9.
  - Disabled hover opacity dimming for `.featured-carousel .thumb-holder-inner`.
  - Set lighter fallback background on `.featured-carousel .thumb-holder`.
- Purged Moodle caches after SCSS update.

## Follow-up fix (course 195 image correction)
- User review identified incorrect image on Pane 1 block 3 (course `195`).
- Updated Pane 1 block 3 image mapping in theme SCSS override to:
  - `.featured-carousel .item-1-3 .thumb-holder-inner { background-image: url("/course_images/course195-google.png") !important; }`
- Exported the current course-195 Google image to:
  - `/var/www/moodle/public/course_images/course195-google.png`
- Purged Moodle caches after the update.
