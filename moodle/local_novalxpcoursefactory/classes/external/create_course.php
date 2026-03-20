<?php
namespace local_novalxpcoursefactory\external;

use context_system;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;
use moodle_exception;

defined('MOODLE_INTERNAL') || die();

/**
 * AJAX external function for front-page AI course requests.
 */
class create_course extends external_api {
    /**
     * @param string $message
     * @return void
     */
    private static function log(string $message): void {
        error_log('[NovaLXPCourseFactory] ' . $message);
    }

    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'brief' => new external_value(PARAM_RAW_TRIMMED, 'Learner course brief', VALUE_REQUIRED),
        ]);
    }

    public static function execute(string $brief): array {
        global $USER;

        $params = self::validate_parameters(self::execute_parameters(), ['brief' => $brief]);
        self::validate_context(context_system::instance());
        require_login();

        $brief = trim($params['brief']);
        if ($brief === '') {
            throw new moodle_exception('invalidrequest', 'local_novalxpcoursefactory');
        }

        self::log('ajax_request_start user_id=' . $USER->id . ' request_type=ai_course_factory brief_length=' . strlen($brief));
        $result = \local_novalxpcoursefactory\service::queue_course($brief);
        if (empty($result['ok'])) {
            self::log('ajax_request_failed user_id=' . $USER->id . ' error=' . (string)($result['error'] ?? 'unknown'));
            throw new moodle_exception(
                'serviceerror',
                'local_novalxpcoursefactory',
                '',
                null,
                (string)($result['error'] ?? '')
            );
        }

        self::log(
            'ajax_request_complete user_id=' . $USER->id .
            ' request_id=' . (string)$result['request_id']
        );

        return [
            'status' => true,
            'requesttype' => 'ai_course_factory',
            'requestid' => (string)$result['request_id'],
            'message' => (string)$result['summary'],
        ];
    }

    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'status' => new external_value(PARAM_BOOL, 'Whether the course request was queued successfully'),
            'requesttype' => new external_value(PARAM_ALPHANUMEXT, 'Queued request type'),
            'requestid' => new external_value(PARAM_ALPHANUMEXT, 'Queued request id'),
            'message' => new external_value(PARAM_TEXT, 'User-facing status message'),
        ]);
    }
}
