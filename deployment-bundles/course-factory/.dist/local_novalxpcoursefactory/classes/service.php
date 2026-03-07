<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

/**
 * Orchestrates course factory requests from Moodle to backend.
 */
class service {
    /**
     * @param string $message
     * @return void
     */
    private static function log(string $message): void {
        debugging($message, DEBUG_DEVELOPER);
        error_log('[NovaLXPCourseFactory] ' . $message);
    }

    /**
     * @param string $brief
     * @return array
     */
    public static function create_course(string $brief): array {
        $enabled = (int)get_config('local_novalxpcoursefactory', 'enabled');
        $functionname = trim((string)get_config('local_novalxpcoursefactory', 'lambdafunctionname'));
        $region = trim((string)get_config('local_novalxpcoursefactory', 'lambdaregion'));
        $timeout = (int)get_config('local_novalxpcoursefactory', 'requesttimeout');

        if ($enabled !== 1 || $functionname === '' || $region === '') {
            return [
                'ok' => false,
                'error' => get_string('missingconfig', 'local_novalxpcoursefactory'),
                'status' => 500,
            ];
        }

        $payload = payload_builder::build($brief);
        $requestid = isset($payload['request_id']) ? (string)$payload['request_id'] : 'unknown';
        self::log(
            "request_id={$requestid} service_start user_id=" . (string)($payload['user']['id'] ?? '') .
            " brief_length=" . strlen((string)($payload['query']['course_brief'] ?? ''))
        );
        $backendresponse = client::create_course($functionname, $region, $payload, max(15, $timeout));
        $formatted = response_formatter::format($backendresponse);
        self::log(
            "request_id={$requestid} service_complete ok=" . (!empty($formatted['ok']) ? 'true' : 'false') .
            (!empty($formatted['course_id']) ? " course_id=" . (int)$formatted['course_id'] : '') .
            (!empty($formatted['request_id']) ? " lambda_request_id=" . (string)$formatted['request_id'] : '')
        );
        return $formatted;
    }
}
