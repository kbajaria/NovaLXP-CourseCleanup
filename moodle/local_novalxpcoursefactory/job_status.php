<?php
define('AJAX_SCRIPT', true);
define('NO_DEBUG_DISPLAY', true);

ob_start();

require_once(__DIR__ . '/../../config.php');

$PAGE->set_url(new moodle_url('/local/novalxpcoursefactory/job_status.php'));

require_login();

$requestid = trim((string)optional_param('requestid', '', PARAM_ALPHANUMEXT));

/**
 * @param array $payload
 * @param int $statuscode
 * @return void
 */
function local_novalxpcoursefactory_emit_status_json(array $payload, int $statuscode = 200): void {
    while (ob_get_level() > 0) {
        ob_end_clean();
    }
    http_response_code($statuscode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload);
    exit;
}

if ($requestid === '') {
    local_novalxpcoursefactory_emit_status_json([
        'status' => false,
        'message' => get_string('invalidrequest', 'local_novalxpcoursefactory'),
    ], 400);
}

$record = \local_novalxpcoursefactory\job_store::get($requestid);
if ($record === null || (int)($record['userid'] ?? 0) !== (int)$USER->id) {
    local_novalxpcoursefactory_emit_status_json([
        'status' => false,
        'message' => get_string('jobnotfound', 'local_novalxpcoursefactory'),
    ], 404);
}

local_novalxpcoursefactory_emit_status_json([
    'status' => true,
    'state' => (string)($record['state'] ?? 'queued'),
    'message' => (string)($record['message'] ?? ''),
    'courseid' => (int)($record['courseid'] ?? 0),
    'coursetitle' => (string)($record['coursetitle'] ?? ''),
    'courseurl' => (string)($record['courseurl'] ?? ''),
]);
