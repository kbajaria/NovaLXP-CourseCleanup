#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  create_lambda_role.sh --profile PROFILE --role-name NAME
EOF
}

PROFILE=""
ROLE_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --role-name) ROLE_NAME="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

[[ -n "$PROFILE" && -n "$ROLE_NAME" ]] || { usage; exit 1; }

TRUST_FILE="$(mktemp)"
cat > "$TRUST_FILE" <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

if ! AWS_PROFILE="$PROFILE" aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  AWS_PROFILE="$PROFILE" aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document "file://$TRUST_FILE" >/dev/null
  sleep 5
fi

AWS_PROFILE="$PROFILE" aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole >/dev/null

rm -f "$TRUST_FILE"
AWS_PROFILE="$PROFILE" aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text
