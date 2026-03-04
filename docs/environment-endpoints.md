# NovaLXP Environment Endpoints

## Confirmed domain info
- Custom domain example provided: `dev.novalxp.co.uk`
- ALB DNS names discovered from AWS (`eu-west-2`):
  - `dev-novalxp-alb-1221185513.eu-west-2.elb.amazonaws.com`
  - `test-novalxp-alb-1337136894.eu-west-2.elb.amazonaws.com`
  - `prod-novalxp-alb-1974695819.eu-west-2.elb.amazonaws.com`

## Course section target
Use relative path for all environments:
- `/course/section.php?id=918`

Examples:
- `https://dev.novalxp.co.uk/course/section.php?id=918`
- `https://<test-domain>/course/section.php?id=918`
- `https://<prod-domain>/course/section.php?id=918`

## External link target
- `https://www.skills.google/course_templates/779`

Note: external link is intentionally absolute, while internal NovaLXP links remain relative.
