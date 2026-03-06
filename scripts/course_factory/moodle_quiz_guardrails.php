<?php
// NovaLXP course-factory guardrails for Moodle quiz completion and answer shuffling.
define('CLI_SCRIPT', true);

$configcandidates = [
    '/var/www/moodle/public/config.php',
    __DIR__ . '/../../../../public/config.php',
    __DIR__ . '/../../../../config.php',
];

$configpath = null;
foreach ($configcandidates as $candidate) {
    if (file_exists($candidate)) {
        $configpath = $candidate;
        break;
    }
}

if (!$configpath) {
    fwrite(STDERR, "Unable to locate Moodle config.php.\n");
    exit(1);
}

require_once($configpath);
require_once($CFG->libdir . '/clilib.php');

[$options, $unrecognized] = cli_get_params(
    [
        'help' => false,
        'apply' => false,
        'courseid' => null,
        'quizname' => null,
        'passmark' => 80,
        'disable-email-processor' => 0,
    ],
    [
        'h' => 'help',
    ]
);

if (!empty($unrecognized)) {
    cli_error('Unknown options: ' . implode(', ', $unrecognized));
}

if ($options['help'] || empty($options['courseid'])) {
    $help = <<<HELP
NovaLXP Moodle quiz guardrails

Options:
  --courseid=ID                    Required course id.
  --quizname="Name"                Optional quiz name. Required only if multiple quizzes exist.
  --passmark=80                    Pass mark to enforce on quiz grade item (default 80).
  --apply                          Apply changes. If omitted, script only verifies and reports.
  --disable-email-processor=0|1    If 1 and --apply is used, disable global email message processor.
  -h, --help                       Show this help.

Examples:
  php moodle_quiz_guardrails.php --courseid=198
  php moodle_quiz_guardrails.php --courseid=198 --apply --disable-email-processor=1
HELP;
    echo $help . PHP_EOL;
    exit(0);
}

$courseid = (int)$options['courseid'];
$quizname = is_null($options['quizname']) ? null : trim((string)$options['quizname']);
$passmark = (float)$options['passmark'];
$apply = (bool)$options['apply'];
$disableemail = ((int)$options['disable-email-processor']) === 1;

$course = $DB->get_record('course', ['id' => $courseid], '*', IGNORE_MISSING);
if (!$course) {
    cli_error("Course not found: {$courseid}");
}

$quiz = null;
if (!empty($quizname)) {
    $quiz = $DB->get_record('quiz', ['course' => $courseid, 'name' => $quizname], '*', IGNORE_MISSING);
    if (!$quiz) {
        cli_error("Quiz not found in course {$courseid} with name '{$quizname}'");
    }
} else {
    $quizzes = $DB->get_records('quiz', ['course' => $courseid], 'id ASC');
    if (count($quizzes) !== 1) {
        cli_error('Course has ' . count($quizzes) . ' quizzes. Provide --quizname to disambiguate.');
    }
    $quiz = reset($quizzes);
}

$quizmodule = $DB->get_record('modules', ['name' => 'quiz'], '*', MUST_EXIST);
$cm = $DB->get_record('course_modules', [
    'course' => $courseid,
    'module' => $quizmodule->id,
    'instance' => $quiz->id,
], '*', MUST_EXIST);

function collect_state(moodle_database $DB, stdClass $course, stdClass $quiz, stdClass $cm, int $quizmoduleid): array {
    $gradeitem = $DB->get_record('grade_items', [
        'courseid' => $course->id,
        'itemmodule' => 'quiz',
        'iteminstance' => $quiz->id,
    ], '*', IGNORE_MISSING);

    $criteriaactivity = $DB->record_exists_select(
        'course_completion_criteria',
        'course = :course AND criteriatype = 4 AND moduleinstance = :moduleinstance',
        ['course' => $course->id, 'moduleinstance' => $cm->id]
    );

    $criteriagradecount = $DB->count_records('course_completion_criteria', [
        'course' => $course->id,
        'criteriatype' => 6,
    ]);

    $quizcontext = $DB->get_record('context', [
        'contextlevel' => CONTEXT_MODULE,
        'instanceid' => $cm->id,
    ], '*', IGNORE_MISSING);

    $mcTotal = 0;
    $mcShuffled = 0;
    if ($quizcontext) {
        $mcTotal = (int)$DB->count_records_select(
            'question',
            'contextid = :contextid AND qtype = :qtype',
            ['contextid' => $quizcontext->id, 'qtype' => 'multichoice']
        );

        $mcShuffled = (int)$DB->count_records_sql(
            "SELECT COUNT(1)
               FROM {question} q
               JOIN {qtype_multichoice_options} mco ON mco.questionid = q.id
              WHERE q.contextid = :contextid
                AND q.qtype = 'multichoice'
                AND mco.shuffleanswers = 1",
            ['contextid' => $quizcontext->id]
        );
    }

    $emailprocessor = $DB->get_record('message_processors', ['name' => 'email'], '*', IGNORE_MISSING);

    return [
        'courseid' => (int)$course->id,
        'coursename' => $course->fullname,
        'quizid' => (int)$quiz->id,
        'quizname' => $quiz->name,
        'cmid' => (int)$cm->id,
        'course_enablecompletion' => (int)$course->enablecompletion,
        'cm_completion' => (int)$cm->completion,
        'cm_completionpassgrade' => (int)$cm->completionpassgrade,
        'cm_completiongradeitemnumber' => isset($cm->completiongradeitemnumber) ? (int)$cm->completiongradeitemnumber : null,
        'quiz_shuffleanswers' => (int)$quiz->shuffleanswers,
        'quiz_gradepass' => $gradeitem ? (float)$gradeitem->gradepass : null,
        'activity_criterion_present' => $criteriaactivity,
        'course_grade_criterion_count' => $criteriagradecount,
        'multichoice_total' => $mcTotal,
        'multichoice_shuffled' => $mcShuffled,
        'email_processor_enabled' => $emailprocessor ? (int)$emailprocessor->enabled : null,
        'quiz_module_id' => $quizmoduleid,
    ];
}

$before = collect_state($DB, $course, $quiz, $cm, (int)$quizmodule->id);

$actions = [];
if ($apply) {
    $transaction = $DB->start_delegated_transaction();

    if ((int)$course->enablecompletion !== 1) {
        $course->enablecompletion = 1;
        $DB->update_record('course', $course);
        $actions[] = 'enabled_course_completion';
    }

    $cmupdate = (object)[
        'id' => $cm->id,
        'completion' => 2,
        'completionpassgrade' => 1,
        'completiongradeitemnumber' => 0,
    ];
    $DB->update_record('course_modules', $cmupdate);
    $actions[] = 'set_quiz_activity_completion_passgrade';

    $gradeitem = $DB->get_record('grade_items', [
        'courseid' => $courseid,
        'itemmodule' => 'quiz',
        'iteminstance' => $quiz->id,
    ], '*', IGNORE_MISSING);
    if ($gradeitem) {
        $gradeitem->gradepass = $passmark;
        $DB->update_record('grade_items', $gradeitem);
        $actions[] = 'set_quiz_gradepass';
    } else {
        $actions[] = 'quiz_grade_item_not_found';
    }

    $criteriaexists = $DB->record_exists_select(
        'course_completion_criteria',
        'course = :course AND criteriatype = 4 AND moduleinstance = :moduleinstance',
        ['course' => $courseid, 'moduleinstance' => $cm->id]
    );

    if (!$criteriaexists) {
        $columns = $DB->get_columns('course_completion_criteria');
        $criterion = (object)[
            'course' => $courseid,
            'criteriatype' => 4,
            'moduleinstance' => $cm->id,
        ];

        if (isset($columns['module'])) {
            $criterion->module = $quizmodule->id;
        }
        if (isset($columns['courseinstance'])) {
            $criterion->courseinstance = 0;
        }
        if (isset($columns['enrolperiod'])) {
            $criterion->enrolperiod = 0;
        }
        if (isset($columns['timeend'])) {
            $criterion->timeend = 0;
        }
        if (isset($columns['gradepass'])) {
            $criterion->gradepass = null;
        }
        if (isset($columns['role'])) {
            $criterion->role = null;
        }

        $DB->insert_record('course_completion_criteria', $criterion);
        $actions[] = 'added_activity_completion_criterion';
    }

    $DB->delete_records('course_completion_criteria', [
        'course' => $courseid,
        'criteriatype' => 6,
    ]);
    $actions[] = 'removed_course_grade_criteria';

    if ((int)$quiz->shuffleanswers !== 1) {
        $quizupdate = (object)[
            'id' => $quiz->id,
            'shuffleanswers' => 1,
        ];
        $DB->update_record('quiz', $quizupdate);
    }
    $actions[] = 'enabled_quiz_shuffleanswers';

    $quizcontext = $DB->get_record('context', [
        'contextlevel' => CONTEXT_MODULE,
        'instanceid' => $cm->id,
    ], '*', IGNORE_MISSING);

    if ($quizcontext) {
        $DB->execute(
            "UPDATE {qtype_multichoice_options}
                SET shuffleanswers = 1
              WHERE questionid IN (
                    SELECT id
                      FROM {question}
                     WHERE contextid = :contextid
                       AND qtype = 'multichoice'
               )",
            ['contextid' => $quizcontext->id]
        );
        $actions[] = 'enabled_multichoice_shuffleanswers';
    } else {
        $actions[] = 'quiz_context_not_found';
    }

    if ($disableemail) {
        $email = $DB->get_record('message_processors', ['name' => 'email'], '*', IGNORE_MISSING);
        if ($email && (int)$email->enabled !== 0) {
            $email->enabled = 0;
            $DB->update_record('message_processors', $email);
        }
        $actions[] = 'disabled_email_message_processor';
    }

    $transaction->allow_commit();

    // Refresh objects for post-state.
    $course = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
    $quiz = $DB->get_record('quiz', ['id' => $quiz->id], '*', MUST_EXIST);
    $cm = $DB->get_record('course_modules', ['id' => $cm->id], '*', MUST_EXIST);
}

$after = collect_state($DB, $course, $quiz, $cm, (int)$quizmodule->id);

$ready = (
    $after['course_enablecompletion'] === 1 &&
    $after['cm_completion'] === 2 &&
    $after['cm_completionpassgrade'] === 1 &&
    $after['cm_completiongradeitemnumber'] === 0 &&
    $after['activity_criterion_present'] === true &&
    $after['course_grade_criterion_count'] === 0 &&
    $after['quiz_shuffleanswers'] === 1 &&
    $after['multichoice_total'] === $after['multichoice_shuffled']
);

$result = [
    'mode' => $apply ? 'apply' : 'verify',
    'passmark_target' => $passmark,
    'guardrails_ready' => $ready,
    'actions' => $actions,
    'before' => $before,
    'after' => $after,
];

echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
