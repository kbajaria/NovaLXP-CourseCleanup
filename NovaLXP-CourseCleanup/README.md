# NovaLXP Course Cleanup and Maintenance

Artifacts and scripts for ongoing Moodle course-catalog cleanup in NovaLXP.

## Purpose
Use this workspace to build and run repeatable cleanup/maintenance tasks such as:
- identifying stale or duplicate course records
- validating required metadata and category placement
- preparing bulk update payloads and change logs
- documenting run outcomes per environment (`dev`, `test`, `production`)

## Structure
- `scripts/` executable cleanup and maintenance scripts
- `runbooks/` process guides and safe execution steps
- `samples/` example inputs/outputs for script development
- `logs/` local run logs (git-ignored)

## Working approach
1. Build and test scripts in `dev` first.
2. Capture assumptions, dry-run behavior, and rollback notes in `runbooks/`.
3. Promote validated workflow to `test` and then `production`.
4. Record each operational run with timestamped notes in `runbooks/`.

## Script standards
- Prefer idempotent operations and explicit `--dry-run` modes.
- Require explicit environment targeting (`--env dev|test|production`).
- Write structured output (CSV/JSON) for traceability.
- Never hardcode credentials or secrets.

## Next additions
- Add first script in `scripts/` (for example, duplicate-course detection).
- Add a runbook template per script in `runbooks/`.
