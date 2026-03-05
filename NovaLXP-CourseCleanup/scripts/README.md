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
