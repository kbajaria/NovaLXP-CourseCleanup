#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-novalxp-course-ops}"
VISIBILITY="${2:-private}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Install gh or create the repo manually." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login" >&2
  exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
if [ "${CURRENT_BRANCH}" = "HEAD" ]; then
  CURRENT_BRANCH="main"
fi

if [ "${CURRENT_BRANCH}" != "main" ]; then
  git branch -M main
fi

gh repo create "${REPO_NAME}" --"${VISIBILITY}" --source=. --remote=origin --push

echo "Created and pushed to GitHub repo: ${REPO_NAME}"
