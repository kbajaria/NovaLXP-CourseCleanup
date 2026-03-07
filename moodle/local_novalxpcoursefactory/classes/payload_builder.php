<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

/**
 * Builds payloads for the course factory backend.
 */
class payload_builder {
    /**
     * @param string $brief
     * @return array
     */
    public static function build(string $brief): array {
        global $USER, $PAGE;

        $trimmedbrief = trim($brief);

        return [
            'request_id' => self::request_id(),
            'tenant_id' => 'novalxp',
            'user' => [
                'id' => (string)$USER->id,
                'role' => 'student',
                'locale' => current_language(),
            ],
            'context' => [
                'page_type' => (string)$PAGE->pagetype,
                'current_url' => $PAGE->url->out(false),
            ],
            'query' => [
                'course_brief' => $trimmedbrief,
            ],
        ];
    }

    /**
     * @return string
     */
    private static function request_id(): string {
        return bin2hex(random_bytes(16));
    }
}
