# Dev Deployment Record

- Date (UTC): 2026-03-08
- Environment: dev
- Host: `i-0cbdd881027b14e09` (`dev-moodle-app`)
- Moodle wwwroot: `https://dev.novalxp.co.uk`
- Category: `Hackathon Primer` (`id=15`)

## Change applied
Applied the Finova Labs 2026 image as the course image for all five hackathon primer courses created in this iteration.

## Source asset
- User-provided image:
  - `/Users/kamilabajaria/Downloads/Finova_Labs_Logo_2026.png`
- Optimized course-card image created locally:
  - `output/imagegen/Finova_Labs_Logo_2026_courseimage.png`
- Crop-safe padded variant created locally:
  - `output/imagegen/Finova_Labs_Logo_2026_courseimage_safe_opt.png`
- Final crop-safe `BG` variant created locally:
  - `output/imagegen/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
- Repo copy of optimized asset:
  - `hackathon-first-timers-learning-path/shared-media/Finova_Labs_Logo_2026_courseimage.png`
- Repo copy of crop-safe asset:
  - `hackathon-first-timers-learning-path/shared-media/Finova_Labs_Logo_2026_courseimage_safe.png`
- Repo copy of final `BG` crop-safe asset:
  - `hackathon-first-timers-learning-path/shared-media/Finova_Labs_Logo_2026_BG_courseimage_safe.png`

## Moodle implementation
- Uploaded the optimized PNG into each course context under:
  - component `course`
  - filearea `overviewfiles`
  - itemid `0`
- Existing overview files for these courses were cleared before the new image was uploaded.

## Courses updated
- `209` `Hackathon Pathway 1 of 4: AI Hackathon Orientation`
- `210` `Hackathon Pathway 2 of 4: GCP Cloud Workstations Basics`
- `211` `Hackathon Pathway 3 of 4: Agent Foundations`
- `212` `Hackathon Pathway 4 of 4: Data and Integration Foundations`
- `213` `Start Here: First-Time Hackathon Pathway`

## Verification summary
- Verified each course now has overview files in Moodle and a pluginfile URL for the uploaded image:
  - `209` `https://dev.novalxp.co.uk/pluginfile.php/2092/course/overviewfiles/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
  - `210` `https://dev.novalxp.co.uk/pluginfile.php/2101/course/overviewfiles/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
  - `211` `https://dev.novalxp.co.uk/pluginfile.php/2110/course/overviewfiles/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
  - `212` `https://dev.novalxp.co.uk/pluginfile.php/2119/course/overviewfiles/Finova_Labs_Logo_2026_BG_courseimage_safe.png`
  - `213` `https://dev.novalxp.co.uk/pluginfile.php/2128/course/overviewfiles/Finova_Labs_Logo_2026_BG_courseimage_safe.png`

## Notes
 - The original source image was first resized and optimized, then replaced with a crop-safe padded variant, and finally replaced again with a crop-safe derivative built from `Finova_Labs_Logo_2026_BG.png` after observing theme cropping in the rendered course cards.
- No manual browser QA was performed on the front page, course catalog, or dashboard card rendering after upload.
