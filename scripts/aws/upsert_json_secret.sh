#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  upsert_json_secret.sh --profile PROFILE --region REGION --secret-name NAME --secret-file FILE
EOF
}

PROFILE=""
REGION=""
SECRET_NAME=""
SECRET_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --secret-name) SECRET_NAME="$2"; shift 2 ;;
    --secret-file) SECRET_FILE="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

[[ -n "$PROFILE" && -n "$REGION" && -n "$SECRET_NAME" && -n "$SECRET_FILE" ]] || { usage; exit 1; }
[[ -f "$SECRET_FILE" ]] || { echo "Secret file not found: $SECRET_FILE" >&2; exit 1; }

if AWS_PROFILE="$PROFILE" aws secretsmanager describe-secret --region "$REGION" --secret-id "$SECRET_NAME" >/dev/null 2>&1; then
  AWS_PROFILE="$PROFILE" aws secretsmanager put-secret-value \
    --region "$REGION" \
    --secret-id "$SECRET_NAME" \
    --secret-string "file://$SECRET_FILE" >/dev/null
else
  AWS_PROFILE="$PROFILE" aws secretsmanager create-secret \
    --region "$REGION" \
    --name "$SECRET_NAME" \
    --secret-string "file://$SECRET_FILE" >/dev/null
fi

AWS_PROFILE="$PROFILE" aws secretsmanager describe-secret \
  --region "$REGION" \
  --secret-id "$SECRET_NAME" \
  --query 'ARN' \
  --output text
