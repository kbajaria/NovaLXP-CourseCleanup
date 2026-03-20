# local_novalxpcoursefactory

Separate Moodle local plugin for front-page course intake workflows in NovaLXP.

## Scope
- Replaces the Edutor front-page featured section pane 1 block 4 card with a learner request form.
- Supports a seeded TalentLMS course catalog so learners can search for the course they want migrated.
- Queues migration requests in Moodle and invokes AWS Lambda from the Moodle EC2 host using the instance role.
- Polls Moodle job state until the request is accepted or failed.
- Uses the Trello integration pattern already proven in `NovaLXP-Feedback`.

## Configure in Moodle
1. Install plugin in `local/novalxpcoursefactory`.
2. Match the folder name to the plugin component:
   - component: `local_novalxpcoursefactory`
   - correct Moodle folder: `local/novalxpcoursefactory`
   - incorrect folder: `local/local_novalxpcoursefactory`
3. Visit `Site administration -> Plugins -> Local plugins -> NovaLXP AI course factory`.
4. Set:
   - Lambda function name
   - Lambda region
   - optional reason/button copy
   - seeded TalentLMS catalog JSON

## Dev host path note
On the current dev host:
- `$CFG->dirroot = /var/www/moodle/public`
- Moodle admin CLI scripts are under `/var/www/moodle/admin/cli`
- the live plugin path is `/var/www/moodle/public/local/novalxpcoursefactory`

Do not assume `/var/www/moodle/local/...` is live just because it exists on disk.
The host uses a split layout where the served Moodle code lives under `/var/www/moodle/public`.

## Seed JSON note
The TalentLMS seed JSON may include a UTF-8 BOM when pasted from exported files.
The plugin now strips a leading BOM before `json_decode()` so the catalog still loads correctly.

## AWS requirement
- The Moodle EC2 instance role must be allowed to invoke the configured Lambda function with `lambda:InvokeFunction`.
- The Moodle host must have the AWS CLI available, matching the same pattern used by `NovaLXP-Feedback`.

## Moodle API requirement
The Lambda still calls:
- `local_novalxpcoursefactory_update_job`

If you also keep the AI course-generation branch in the Lambda, it may also need the existing `local_novalxpapi` functions.

## Front-page behaviour
- Only loads for logged-in non-guest users.
- Only loads on the Moodle front page.
- Replaces `.featured-carousel .item-1-4 .item-inner` in the Edutor featured section.

## Front-end flow
- `course_factory.php` queues the migration request and returns a request id immediately.
- `job_status.php` returns queued, processing, complete, or failed status.
- The AMD module polls `job_status.php` until the migration request is completed.
