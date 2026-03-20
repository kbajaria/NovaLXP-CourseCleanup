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
                'fullname' => fullname($USER),
                'email' => !empty($USER->email) ? (string)$USER->email : '',
                'username' => !empty($USER->username) ? (string)$USER->username : '',
            ],
            'context' => [
                'page_type' => (string)$PAGE->pagetype,
                'current_url' => $PAGE->url->out(false),
            ],
            'request_type' => 'ai_course_factory',
            'query' => [
                'course_brief' => $trimmedbrief,
            ],
        ];
    }

    /**
     * @param string $sourcecourseid
     * @param string $reason
     * @return array
     */
    public static function build_migration_request(string $sourcecourseid, string $reason): array {
        global $USER, $PAGE;

        $trimmedreason = trim($reason);
        $course = catalog::find($sourcecourseid);

        if ($course === null) {
            throw new \moodle_exception('invalidcourse', 'local_novalxpcoursefactory');
        }

        return [
            'request_id' => self::request_id(),
            'tenant_id' => 'novalxp',
            'user' => [
                'id' => (string)$USER->id,
                'role' => 'student',
                'locale' => current_language(),
                'fullname' => fullname($USER),
                'email' => !empty($USER->email) ? (string)$USER->email : '',
                'username' => !empty($USER->username) ? (string)$USER->username : '',
            ],
            'context' => [
                'page_type' => (string)$PAGE->pagetype,
                'current_url' => $PAGE->url->out(false),
            ],
            'request_type' => 'talentlms_migration',
            'migration_request' => [
                'source_system' => 'TalentLMS',
                'course' => [
                    'id' => (string)$course['id'],
                    'title' => (string)$course['title'],
                    'url' => (string)($course['url'] ?? ''),
                    'category' => (string)($course['category'] ?? ''),
                    'summary' => (string)($course['summary'] ?? ''),
                ],
                'reason' => $trimmedreason,
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
