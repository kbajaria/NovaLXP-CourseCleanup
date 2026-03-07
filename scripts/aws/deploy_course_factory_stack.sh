#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy_course_factory_stack.sh \
    --profile PROFILE \
    --region REGION \
    --env dev|test|production \
    --moodle-role-name ROLE \
    --moodle-base-url URL \
    --moodle-token TOKEN \
    --openai-api-key KEY \
    [--openai-model MODEL] \
    [--category-id ID] \
    [--category-name NAME] \
    [--course-pass-mark N]
EOF
}

PROFILE=""
REGION=""
ENV_NAME=""
MOODLE_ROLE_NAME=""
MOODLE_BASE_URL=""
MOODLE_TOKEN=""
OPENAI_API_KEY=""
OPENAI_MODEL="gpt-5-mini"
CATEGORY_ID="5"
CATEGORY_NAME="AI-Generated"
COURSE_PASS_MARK="80"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --env) ENV_NAME="$2"; shift 2 ;;
    --moodle-role-name) MOODLE_ROLE_NAME="$2"; shift 2 ;;
    --moodle-base-url) MOODLE_BASE_URL="$2"; shift 2 ;;
    --moodle-token) MOODLE_TOKEN="$2"; shift 2 ;;
    --openai-api-key) OPENAI_API_KEY="$2"; shift 2 ;;
    --openai-model) OPENAI_MODEL="$2"; shift 2 ;;
    --category-id) CATEGORY_ID="$2"; shift 2 ;;
    --category-name) CATEGORY_NAME="$2"; shift 2 ;;
    --course-pass-mark) COURSE_PASS_MARK="$2"; shift 2 ;;
    *) usage; exit 1 ;;
  esac
done

[[ -n "$PROFILE" && -n "$REGION" && -n "$ENV_NAME" && -n "$MOODLE_ROLE_NAME" && -n "$MOODLE_BASE_URL" && -n "$MOODLE_TOKEN" && -n "$OPENAI_API_KEY" ]] || { usage; exit 1; }

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FUNCTION_NAME="novalxp-course-factory-$ENV_NAME"
ROLE_NAME="novalxp-course-factory-$ENV_NAME-lambda-role"
MOODLE_SECRET_NAME="novalxp/course-factory/$ENV_NAME/moodle-api"
OPENAI_SECRET_NAME="novalxp/course-factory/$ENV_NAME/openai"

MOODLE_SECRET_FILE="$(mktemp)"
OPENAI_SECRET_FILE="$(mktemp)"
cat > "$MOODLE_SECRET_FILE" <<EOF
{"MOODLE_TOKEN":"$MOODLE_TOKEN","MOODLE_BASE_URL":"$MOODLE_BASE_URL"}
EOF
cat > "$OPENAI_SECRET_FILE" <<EOF
{"OPENAI_API_KEY":"$OPENAI_API_KEY"}
EOF

ROLE_ARN="$("$ROOT_DIR/scripts/aws/create_lambda_role.sh" \
  --profile "$PROFILE" \
  --role-name "$ROLE_NAME")"

MOODLE_SECRET_ARN="$("$ROOT_DIR/scripts/aws/upsert_json_secret.sh" \
  --profile "$PROFILE" \
  --region "$REGION" \
  --secret-name "$MOODLE_SECRET_NAME" \
  --secret-file "$MOODLE_SECRET_FILE")"

OPENAI_SECRET_ARN="$("$ROOT_DIR/scripts/aws/upsert_json_secret.sh" \
  --profile "$PROFILE" \
  --region "$REGION" \
  --secret-name "$OPENAI_SECRET_NAME" \
  --secret-file "$OPENAI_SECRET_FILE")"

"$ROOT_DIR/scripts/aws/attach_lambda_secret_policy.sh" \
  --profile "$PROFILE" \
  --role-name "$ROLE_NAME" \
  --policy-name "NovaLXPCourseFactoryReadMoodleSecret" \
  --secret-arn "$MOODLE_SECRET_ARN"

"$ROOT_DIR/scripts/aws/attach_lambda_secret_policy.sh" \
  --profile "$PROFILE" \
  --role-name "$ROLE_NAME" \
  --policy-name "NovaLXPCourseFactoryReadOpenAISecret" \
  --secret-arn "$OPENAI_SECRET_ARN"

"$ROOT_DIR/scripts/aws/deploy_course_factory_lambda.sh" \
  --profile "$PROFILE" \
  --region "$REGION" \
  --function-name "$FUNCTION_NAME" \
  --role-arn "$ROLE_ARN" \
  --moodle-secret-arn "$MOODLE_SECRET_ARN" \
  --openai-secret-arn "$OPENAI_SECRET_ARN" \
  --openai-model "$OPENAI_MODEL" \
  --moodle-base-url "$MOODLE_BASE_URL" \
  --category-id "$CATEGORY_ID" \
  --category-name "$CATEGORY_NAME" \
  --course-pass-mark "$COURSE_PASS_MARK"

"$ROOT_DIR/scripts/aws/attach_moodle_invoke_policy.sh" \
  --profile "$PROFILE" \
  --role-name "$MOODLE_ROLE_NAME" \
  --region "$REGION" \
  --function-name "$FUNCTION_NAME"

rm -f "$MOODLE_SECRET_FILE" "$OPENAI_SECRET_FILE"

echo "Course factory stack deployed for environment: $ENV_NAME"
echo "Lambda function: $FUNCTION_NAME"
echo "Lambda role: $ROLE_NAME"
echo "Moodle secret ARN: $MOODLE_SECRET_ARN"
echo "OpenAI secret ARN: $OPENAI_SECRET_ARN"
