<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

/**
 * Normalizes backend responses for frontend rendering.
 */
class response_formatter {
    /**
     * @param array $backendresponse
     * @return array
     */
    public static function format(array $backendresponse): array {
        $body = $backendresponse['body'] ?? [];

        if (!($backendresponse['ok'] ?? false)) {
            $error = $body['message'] ??
                ($body['error']['message'] ??
                ($backendresponse['error'] ?? get_string('serviceerror', 'local_novalxpcoursefactory')));
            return [
                'ok' => false,
                'error' => $error,
                'status' => (int)($backendresponse['status'] ?? 0),
            ];
        }

        return [
            'ok' => true,
            'course_id' => (int)($body['courseid'] ?? 0),
            'course_title' => (string)($body['coursetitle'] ?? ''),
            'course_url' => (string)($body['courseurl'] ?? ''),
            'summary' => (string)($body['message'] ?? get_string('successprefix', 'local_novalxpcoursefactory')),
            'category' => (string)($body['category'] ?? ''),
            'request_id' => (string)($body['requestid'] ?? ''),
        ];
    }
}
