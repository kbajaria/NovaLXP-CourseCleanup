#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  package_moodle_course_factory_bundle.sh [--output-dir DIR]
EOF
}

OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/deployment-bundles/course-factory/.dist}"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
cp -R "$ROOT_DIR/moodle/local_novalxpcoursefactory" "$OUT_DIR/"
cp "$ROOT_DIR/patches/local_novalxpapi-course-factory-guardrails.patch" "$OUT_DIR/"
cp "$ROOT_DIR/docs/deploy-course-factory.md" "$ROOT_DIR/docs/deploy-course-factory-dev.md" "$ROOT_DIR/docs/deploy-course-factory-promotion.md" "$ROOT_DIR/docs/course-factory-release-checklist.md" "$OUT_DIR/"

echo "Packaged Moodle deployment bundle in $OUT_DIR"
