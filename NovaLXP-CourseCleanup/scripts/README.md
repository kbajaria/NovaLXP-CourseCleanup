# Scripts

Store NovaLXP cleanup and maintenance scripts here.

Suggested naming:
- `audit-*.sh|py` for read-only checks
- `prepare-*.sh|py` for generated update files
- `apply-*.sh|py` for controlled write operations

Minimum script behavior:
- supports `--env` target
- supports `--dry-run` when write-capable
- prints a concise execution summary

## First maintenance script
- `apply-course-changes.py`: reads `CourseID,Action` CSV and applies:
  - `Delete` via Moodle API `core_course_delete_courses`
  - `Hide` via Moodle API `core_course_update_courses` (`visible=0`)

Usage examples:
- Dry-run (default):
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes.py --env dev --csv course_changes.csv`
- Execute changes:
  - `NOVALXP_MOODLE_TOKEN=<token> ./NovaLXP-CourseCleanup/scripts/apply-course-changes.py --env dev --csv course_changes.csv --execute`

Environment base URL resolution:
- `--base-url` (highest priority)
- `NOVALXP_<ENV>_BASE_URL` (`NOVALXP_DEV_BASE_URL`, `NOVALXP_TEST_BASE_URL`, `NOVALXP_PRODUCTION_BASE_URL`)
- fallback for `dev`: `https://dev.novalxp.co.uk`
