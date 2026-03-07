# Course Factory AWS Deployment Usage

## One-command deployment per environment

Use:

```bash
scripts/aws/deploy_course_factory_stack.sh \
  --profile <aws-profile> \
  --region eu-west-2 \
  --env <dev|test|production> \
  --moodle-role-name MoodleCombinedSSMAndBedrockRole \
  --moodle-base-url <env-url> \
  --moodle-token <env-token> \
  --openai-api-key <openai-key>
```

## Examples

### Dev

```bash
scripts/aws/deploy_course_factory_stack.sh \
  --profile default \
  --region eu-west-2 \
  --env dev \
  --moodle-role-name MoodleCombinedSSMAndBedrockRole \
  --moodle-base-url https://dev.novalxp.co.uk \
  --moodle-token '<dev-token>' \
  --openai-api-key '<openai-key>'
```

### Test

```bash
scripts/aws/deploy_course_factory_stack.sh \
  --profile default \
  --region eu-west-2 \
  --env test \
  --moodle-role-name MoodleCombinedSSMAndBedrockRole \
  --moodle-base-url https://test.novalxp.co.uk \
  --moodle-token '<test-token>' \
  --openai-api-key '<openai-key>'
```

### Production

```bash
scripts/aws/deploy_course_factory_stack.sh \
  --profile default \
  --region eu-west-2 \
  --env production \
  --moodle-role-name MoodleCombinedSSMAndBedrockRole \
  --moodle-base-url https://learn.novalxp.co.uk \
  --moodle-token '<prod-token>' \
  --openai-api-key '<openai-key>'
```
