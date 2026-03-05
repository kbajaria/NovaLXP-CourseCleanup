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
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes.py --env dev --csv course_changes.csv --execute --aws-secret-id <secret-id>`

Environment base URL resolution:
- `--base-url` (highest priority)
- `NOVALXP_<ENV>_BASE_URL` (`NOVALXP_DEV_BASE_URL`, `NOVALXP_TEST_BASE_URL`, `NOVALXP_PRODUCTION_BASE_URL`)
- fallback for `dev`: `https://dev.novalxp.co.uk`

Token resolution when `--execute` is used:
- `--token` or `NOVALXP_MOODLE_TOKEN`
- `--aws-secret-id` (or `NOVALXP_<ENV>_MOODLE_TOKEN_SECRET_ID`, then `NOVALXP_MOODLE_TOKEN_SECRET_ID`)
- optional `--aws-secret-key` when SecretString is JSON
- AWS region from `--aws-region` (default `AWS_REGION` or `eu-west-2`)

## Token bootstrap script
- `store-moodle-token-secret.py`: creates or updates an environment secret in AWS Secrets Manager and prints the secret ARN.

Usage:
- `./NovaLXP-CourseCleanup/scripts/store-moodle-token-secret.py --env dev`
  - prompts for token securely (hidden input)
- `./NovaLXP-CourseCleanup/scripts/store-moodle-token-secret.py --env dev --token '<token>'`
- `./NovaLXP-CourseCleanup/scripts/store-moodle-token-secret.py --env production --region eu-west-2`

Defaults:
- secret name: `novalxp/<env>/moodle/webservice-token`
- payload format: JSON with `token` field

Then run maintenance:
- `./NovaLXP-CourseCleanup/scripts/apply-course-changes.py --env dev --csv course_changes.csv --execute --aws-secret-id novalxp/dev/moodle/webservice-token`

## SSM execution script (API-key fallback)
- `apply-course-changes-ssm.py`: reads the same CSV and executes changes directly on Moodle app EC2 over AWS SSM.
- `Delete` uses `admin/cli/delete_course.php --non-interactive --disablerecyclebin`
- `Hide` uses Moodle PHP `course_change_visibility(<id>, false)`

Usage:
- Dry-run:
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes-ssm.py --env dev --csv course_changes.csv`
- Execute in dev:
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes-ssm.py --env dev --csv course_changes.csv --execute`
- Override target instance:
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes-ssm.py --env dev --instance-id i-xxxxxxxx --csv course_changes.csv --execute`
- Write a specific log file:
  - `./NovaLXP-CourseCleanup/scripts/apply-course-changes-ssm.py --env dev --csv course_changes.csv --execute --log-file NovaLXP-CourseCleanup/logs/dev-run.csv`

Logging and failure classification:
- default log path: `NovaLXP-CourseCleanup/logs/ssm-course-changes-<timestamp>.csv`
- each row includes `status`, `failure_type`, `ssm_status`, `ssm_command_id`, and full detail
- current failure types include:
  - `COURSE_NOT_FOUND` (already deleted/missing)
  - `MOODLE_CODE_EXCEPTION` (delete process error inside Moodle code)
  - `MOODLE_EXCEPTION`, `SSM_TIMEOUT`, `SSM_COMMAND_ERROR`, `SSM_REMOTE_FAILURE`, `AWS_CLI_ERROR`, `UNKNOWN_FAILURE`
