#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy_course_factory_lambda.sh \
    --profile PROFILE \
    --region REGION \
    --function-name NAME \
    --role-arn ARN \
    --moodle-secret-arn ARN \
    --openai-secret-arn ARN \
    [--openai-model MODEL] \
    [--moodle-base-url URL] \
    [--category-id ID] \
    [--category-name NAME] \
    [--course-pass-mark N]
EOF
}

PROFILE=""
REGION=""
FUNCTION_NAME=""
ROLE_ARN=""
MOODLE_SECRET_ARN=""
OPENAI_SECRET_ARN=""
OPENAI_MODEL="gpt-5-mini"
MOODLE_BASE_URL=""
CATEGORY_ID="5"
CATEGORY_NAME="AI-Generated"
COURSE_PASS_MARK="80"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --function-name) FUNCTION_NAME="$2"; shift 2 ;;
    --role-arn) ROLE_ARN="$2"; shift 2 ;;
    --moodle-secret-arn) MOODLE_SECRET_ARN="$2"; shift 2 ;;
    --openai-secret-arn) OPENAI_SECRET_ARN="$2"; shift 2 ;;
    --openai-model) OPENAI_MODEL="$2"; shift 2 ;;
    --moodle-base-url) MOODLE_BASE_URL="$2"; shift 2 ;;
    --category-id) CATEGORY_ID="$2"; shift 2 ;;
    --category-name) CATEGORY_NAME="$2"; shift 2 ;;
    --course-pass-mark) COURSE_PASS_MARK="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

[[ -n "$PROFILE" && -n "$REGION" && -n "$FUNCTION_NAME" && -n "$ROLE_ARN" && -n "$MOODLE_SECRET_ARN" && -n "$OPENAI_SECRET_ARN" && -n "$MOODLE_BASE_URL" ]] || { usage; exit 1; }

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LAMBDA_DIR="$ROOT_DIR/aws/lambda-course-factory"
BUILD_DIR="$LAMBDA_DIR/.build"
ZIP_FILE="$BUILD_DIR/function.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp "$LAMBDA_DIR/index.mjs" "$LAMBDA_DIR/package.json" "$BUILD_DIR/"
pushd "$BUILD_DIR" >/dev/null
npm install --omit=dev >/dev/null
zip -qr "$ZIP_FILE" .
popd >/dev/null

if AWS_PROFILE="$PROFILE" aws lambda get-function --region "$REGION" --function-name "$FUNCTION_NAME" >/dev/null 2>&1; then
  AWS_PROFILE="$PROFILE" aws lambda update-function-code \
    --region "$REGION" \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$ZIP_FILE" >/dev/null
else
  AWS_PROFILE="$PROFILE" aws lambda create-function \
    --region "$REGION" \
    --function-name "$FUNCTION_NAME" \
    --runtime nodejs22.x \
    --handler index.handler \
    --role "$ROLE_ARN" \
    --zip-file "fileb://$ZIP_FILE" \
    --timeout 120 \
    --memory-size 512 >/dev/null
fi

AWS_PROFILE="$PROFILE" aws lambda update-function-configuration \
  --region "$REGION" \
  --function-name "$FUNCTION_NAME" \
  --environment "Variables={OPENAI_SECRET_ARN=$OPENAI_SECRET_ARN,OPENAI_MODEL=$OPENAI_MODEL,MOODLE_BASE_URL=$MOODLE_BASE_URL,MOODLE_SECRET_ARN=$MOODLE_SECRET_ARN,MOODLE_AI_GENERATED_CATEGORY_ID=$CATEGORY_ID,MOODLE_AI_GENERATED_CATEGORY_NAME=$CATEGORY_NAME,COURSE_PASS_MARK=$COURSE_PASS_MARK}" >/dev/null

echo "Deployed $FUNCTION_NAME in $REGION"
