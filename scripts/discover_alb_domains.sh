#!/usr/bin/env bash
set -euo pipefail

REGION="${1:-eu-west-2}"

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI not found" >&2
  exit 1
fi

if ! aws sts get-caller-identity >/dev/null 2>&1; then
  echo "AWS credentials are not configured. Run your org login flow (for example: aws login)." >&2
  exit 1
fi

echo "Discovering ALBs in region: ${REGION}"
printf "%-35s %-12s %-20s %s\n" "ALB_NAME" "ENV" "APPLICATION" "DNS_NAME"
printf "%-35s %-12s %-20s %s\n" "--------" "---" "-----------" "--------"

aws elbv2 describe-load-balancers \
  --region "${REGION}" \
  --query 'LoadBalancers[?Type==`application`].[LoadBalancerName,DNSName,LoadBalancerArn]' \
  --output text | while read -r NAME DNS ARN; do
    ENV=$(aws elbv2 describe-tags \
      --region "${REGION}" \
      --resource-arns "${ARN}" \
      --query "TagDescriptions[0].Tags[?Key=='Environment'].Value | [0]" \
      --output text)

    APP=$(aws elbv2 describe-tags \
      --region "${REGION}" \
      --resource-arns "${ARN}" \
      --query "TagDescriptions[0].Tags[?Key=='Application'].Value | [0]" \
      --output text)

    [ "${ENV}" = "None" ] && ENV="unknown"
    [ "${APP}" = "None" ] && APP="unknown"

    printf "%-35s %-12s %-20s %s\n" "${NAME}" "${ENV}" "${APP}" "${DNS}"
  done
