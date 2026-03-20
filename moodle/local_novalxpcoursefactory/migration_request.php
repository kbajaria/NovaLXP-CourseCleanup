<?php
define('AJAX_SCRIPT', true);
define('NO_DEBUG_DISPLAY', true);

ob_start();

require_once(__DIR__ . '/../../config.php');

$PAGE->set_url(new moodle_url('/local/novalxpcoursefactory/migration_request.php'));

require_login();
require_sesskey();

$sourcecourseid = trim((string)optional_param('sourcecourseid', '', PARAM_ALPHANUMEXT));
$reason = trim((string)optional_param('reason', '', PARAM_RAW_TRIMMED));

/**
 * Emit a clean JSON response even if upstream code wrote debug text.
 *
 * @param array $payload
 * @param int $statuscode
 * @return void
 */
function local_novalxpcoursefactory_emit_migration_json(array $payload, int $statuscode = 200): void {
    $buffer = '';
    while (ob_get_level() > 0) {
        $chunk = ob_get_contents();
        if ($chunk !== false) {
            $buffer .= $chunk;
        }
        ob_end_clean();
    }

    if (trim($buffer) !== '') {
        error_log('[NovaLXPCourseFactory] suppressed_output=' . trim($buffer));
    }

    http_response_code($statuscode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload);
    exit;
}

if ($sourcecourseid === '' || $reason === '') {
    local_novalxpcoursefactory_emit_migration_json([
        'status' => false,
        'message' => get_string('invalidmigrationrequest', 'local_novalxpcoursefactory'),
    ], 400);
}

$result = \local_novalxpcoursefactory\service::queue_migration_request($sourcecourseid, $reason);

if (empty($result['ok'])) {
    local_novalxpcoursefactory_emit_migration_json([
        'status' => false,
        'message' => (string)($result['error'] ?? get_string('serviceerror', 'local_novalxpcoursefactory')),
    ], 500);
}

local_novalxpcoursefactory_emit_migration_json([
    'status' => true,
    'requesttype' => 'talentlms_migration',
    'requestid' => (string)$result['request_id'],
    'message' => (string)$result['summary'],
]);
