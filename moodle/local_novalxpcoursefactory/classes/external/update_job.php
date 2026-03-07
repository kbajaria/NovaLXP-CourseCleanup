<?php
namespace local_novalxpcoursefactory\external;

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;

defined('MOODLE_INTERNAL') || die();

/**
 * Token-authenticated callback for Lambda to update async job state.
 */
class update_job extends external_api {
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'requestid' => new external_value(PARAM_ALPHANUMEXT, 'Course factory request id', VALUE_REQUIRED),
            'state' => new external_value(PARAM_ALPHA, 'queued, processing, complete, or failed', VALUE_REQUIRED),
            'message' => new external_value(PARAM_TEXT, 'Status message', VALUE_DEFAULT, ''),
            'courseid' => new external_value(PARAM_INT, 'Created course id', VALUE_DEFAULT, 0),
            'coursetitle' => new external_value(PARAM_TEXT, 'Created course title', VALUE_DEFAULT, ''),
            'courseurl' => new external_value(PARAM_URL, 'Created course URL', VALUE_DEFAULT, ''),
        ]);
    }

    public static function execute(
        string $requestid,
        string $state,
        string $message = '',
        int $courseid = 0,
        string $coursetitle = '',
        string $courseurl = ''
    ): array {
        $params = self::validate_parameters(self::execute_parameters(), [
            'requestid' => $requestid,
            'state' => $state,
            'message' => $message,
            'courseid' => $courseid,
            'coursetitle' => $coursetitle,
            'courseurl' => $courseurl,
        ]);

        $result = \local_novalxpcoursefactory\service::update_job(
            $params['requestid'],
            $params['state'],
            $params['message'],
            (int)$params['courseid'],
            $params['coursetitle'],
            $params['courseurl']
        );

        return [
            'status' => !empty($result['ok']),
        ];
    }

    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'status' => new external_value(PARAM_BOOL, 'Whether the job update succeeded'),
        ]);
    }
}
