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
        error_log('[NovaLXPCourseFactory] ' . $message);
    }

    /**
     * @param string $brief
     * @return array
     */
    public static function queue_course(string $brief): array {
        global $USER;

        $enabled = (int)get_config('local_novalxpcoursefactory', 'enabled');
        $functionname = trim((string)get_config('local_novalxpcoursefactory', 'lambdafunctionname'));
        $region = trim((string)get_config('local_novalxpcoursefactory', 'lambdaregion'));

        if ($enabled !== 1 || $functionname === '' || $region === '') {
            return [
                'ok' => false,
                'error' => get_string('missingconfig', 'local_novalxpcoursefactory'),
                'status' => 500,
            ];
        }

        $payload = payload_builder::build($brief);
        $requestid = isset($payload['request_id']) ? (string)$payload['request_id'] : 'unknown';
        job_store::create($requestid, (int)$USER->id, $brief);
        self::log(
            "request_id={$requestid} service_start user_id=" . (string)($payload['user']['id'] ?? '') .
            " brief_length=" . strlen((string)($payload['query']['course_brief'] ?? ''))
        );
        $invokeresponse = client::invoke_async($functionname, $region, $payload);
        if (empty($invokeresponse['ok'])) {
            job_store::update($requestid, [
                'state' => 'failed',
                'message' => (string)($invokeresponse['error'] ?? get_string('invokeerror', 'local_novalxpcoursefactory')),
            ]);
            return [
                'ok' => false,
                'error' => (string)($invokeresponse['error'] ?? get_string('invokeerror', 'local_novalxpcoursefactory')),
                'status' => (int)($invokeresponse['status'] ?? 0),
            ];
        }

        return [
            'ok' => true,
            'request_id' => $requestid,
            'summary' => get_string('jobqueued', 'local_novalxpcoursefactory'),
        ];
    }

    /**
     * @param string $requestid
     * @param string $state
     * @param string $message
     * @param int $courseid
     * @param string $coursetitle
     * @param string $courseurl
     * @return array
     */
    public static function update_job(
        string $requestid,
        string $state,
        string $message,
        int $courseid = 0,
        string $coursetitle = '',
        string $courseurl = ''
    ): array {
        $allowedstates = ['queued', 'processing', 'complete', 'failed'];
        if (!in_array($state, $allowedstates, true)) {
            $state = 'failed';
        }

        $record = job_store::update($requestid, [
            'state' => $state,
            'message' => $message,
            'courseid' => $courseid,
            'coursetitle' => $coursetitle,
            'courseurl' => $courseurl,
        ]);

        if ($record === null) {
            return [
                'ok' => false,
                'error' => 'Unknown request id',
            ];
        }

        self::log(
            "request_id={$requestid} job_update state={$state}" .
            ($courseid > 0 ? " course_id={$courseid}" : '')
        );

        return [
            'ok' => true,
        ];
    }
}
