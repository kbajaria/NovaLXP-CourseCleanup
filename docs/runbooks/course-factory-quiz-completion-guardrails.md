# Course Factory Guardrails: Quiz Completion + Passing Score

This runbook captures the exact Moodle settings that made course completion behave correctly for quiz-driven courses.

## Why these guardrails exist
Without these settings, we saw the following failures in NovaLXP:
- Learners passed the quiz, but course progress stayed at `0%`.
- Correct answer stayed in option `A` across attempts.
- Quiz submission failed in some environments due to message processor errors.

## Required guardrails for every new quiz-based course

### 1) Activity completion must be pass-grade based on the quiz module
Set on the course module (`course_modules`) for the quiz:
- `completion = 2`
- `completionpassgrade = 1`
- `completiongradeitemnumber = 0`

### 2) Course completion must be activity-based (not course-grade-based)
In `course_completion_criteria`:
- Required: activity criterion for the quiz module (`criteriatype = 4`, tied to quiz `cmid`)
- Remove: course-grade criterion (`criteriatype = 6`) for this course

Reason: this avoids course-total aggregation edge cases that can leave learner progress at `0%` despite a passing quiz.

### 3) Quiz and question answer shuffling must both be enabled
- Quiz-level: `quiz.shuffleanswers = 1`
- Question-level: `qtype_multichoice_options.shuffleanswers = 1` for all quiz-context multichoice questions

### 4) Quiz pass mark must be set
Set quiz grade-item pass mark in `grade_items.gradepass` to your target (default `80`).

### 5) Course completion tracking must be enabled
- `course.enablecompletion = 1`

## Reusable script (verify/apply)
Use:
- [/Users/kamilabajaria/Projects/NovaLXP-Courses/scripts/course_factory/moodle_quiz_guardrails.php](/Users/kamilabajaria/Projects/NovaLXP-Courses/scripts/course_factory/moodle_quiz_guardrails.php)

### Stage the script on the Moodle host
```bash
sudo cp /path/to/repo/scripts/course_factory/moodle_quiz_guardrails.php /tmp/moodle_quiz_guardrails.php
sudo chown apache:apache /tmp/moodle_quiz_guardrails.php
```

### Verify only
```bash
sudo -u apache php /tmp/moodle_quiz_guardrails.php \
  --courseid=198
```

### Apply guardrails
```bash
sudo -u apache php /tmp/moodle_quiz_guardrails.php \
  --courseid=198 \
  --quizname='Aha! Roadmaps for Beginners — Quiz' \
  --passmark=80 \
  --apply
```

### Optional mitigation for known message-processor failure
Use only if quiz submission throws `Message was not sent` stack traces:
```bash
sudo -u apache php /tmp/moodle_quiz_guardrails.php \
  --courseid=198 \
  --apply \
  --disable-email-processor=1
```

## Deployment sequence
1. Deploy course content and quiz in `dev`.
2. Run guardrail script in `verify` mode.
3. Run guardrail script in `apply` mode.
4. Purge Moodle caches:
   - `sudo -u apache php /var/www/moodle/public/admin/cli/purge_caches.php`
5. Validate as a learner:
   - Attempt quiz and pass.
   - Confirm quiz shows complete.
   - Confirm course progress updates to complete.
6. Repeat in `test`, then `production`.

## Notes
- Do not force learner completion rows in test/prod when validating normal behavior.
- This runbook is for courses where quiz pass is the completion criterion.
