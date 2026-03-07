# local_novalxpapi Extension For Course Factory

This repo does not contain the live `local_novalxpapi` plugin source, so the Moodle-side change is packaged as a patch:

- [local_novalxpapi-course-factory-guardrails.patch](/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch)

## What the patch adds
- Registers a new web service function:
  - `local_novalxpapi_apply_quiz_completion_guardrails`
- Implements a callable Moodle API method that:
  - enables course completion
  - sets quiz activity completion to pass-grade based
  - sets quiz grade pass mark
  - adds the activity-based course completion criterion
  - removes conflicting course-grade completion criteria
  - optionally enables quiz and multichoice answer shuffling

## Expected Lambda call
The course-factory Lambda now calls this function after `local_novalxpapi_create_quiz`:

```text
local_novalxpapi_apply_quiz_completion_guardrails
```

Arguments:
- `courseid`
- `quizcmid`
- `quizid`
- `passmark`
- `shuffleanswers`

## Apply target
Apply the patch in the repo or checkout that contains the real `local/novalxpapi` plugin code.

## Remaining validation
After patching and deploying `local_novalxpapi`, validate with a generated course that:
- the quiz activity shows completion on pass
- course completion is tied to the quiz activity
- learners can self-enrol in the generated course

## Related course-factory callback requirement
The final working architecture also requires the separate `local_novalxpcoursefactory` plugin callback function:

- `local_novalxpcoursefactory_update_job`

This is not part of `local_novalxpapi`, but it must be available to the same Moodle token service that Lambda uses so the async job can move from `queued` to `processing`, `complete`, or `failed`.
