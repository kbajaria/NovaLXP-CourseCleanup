<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

/**
 * Stores asynchronous course factory job state in shared moodledata.
 */
class job_store {
    /**
     * @return string
     */
    private static function jobs_dir(): string {
        global $CFG;

        $dir = $CFG->dataroot . '/local_novalxpcoursefactory/jobs';
        if (!is_dir($dir)) {
            mkdir($dir, $CFG->directorypermissions, true);
        }
        return $dir;
    }

    /**
     * @param string $requestid
     * @return string
     */
    private static function job_path(string $requestid): string {
        return self::jobs_dir() . '/' . clean_param($requestid, PARAM_ALPHANUMEXT) . '.json';
    }

    /**
     * @param string $requestid
     * @param array $record
     * @return void
     */
    private static function write_record(string $requestid, array $record): void {
        file_put_contents(self::job_path($requestid), json_encode($record), LOCK_EX);
    }

    /**
     * @param string $requestid
     * @return array|null
     */
    public static function get(string $requestid): ?array {
        $path = self::job_path($requestid);
        if (!is_file($path)) {
            return null;
        }

        $raw = file_get_contents($path);
        if ($raw === false) {
            return null;
        }

        $decoded = json_decode($raw, true);
        return is_array($decoded) ? $decoded : null;
    }

    /**
     * @param string $requestid
     * @param int $userid
     * @param array $details
     * @return array
     */
    public static function create(string $requestid, int $userid, array $details): array {
        $record = [
            'requestid' => $requestid,
            'userid' => $userid,
            'requesttype' => (string)($details['requesttype'] ?? 'talentlms_migration'),
            'brief' => (string)($details['brief'] ?? ''),
            'reason' => (string)($details['reason'] ?? ''),
            'sourcecourseid' => (string)($details['sourcecourseid'] ?? ''),
            'sourcecoursetitle' => (string)($details['sourcecoursetitle'] ?? ''),
            'sourcecourseurl' => (string)($details['sourcecourseurl'] ?? ''),
            'state' => 'queued',
            'message' => (string)($details['requesttype'] ?? '') === 'ai_course_factory'
                ? get_string('jobqueued', 'local_novalxpcoursefactory')
                : get_string('migrationjobqueued', 'local_novalxpcoursefactory'),
            'courseid' => 0,
            'coursetitle' => '',
            'courseurl' => '',
            'timecreated' => time(),
            'timemodified' => time(),
        ];
        self::write_record($requestid, $record);
        return $record;
    }

    /**
     * @param string $requestid
     * @param array $changes
     * @return array|null
     */
    public static function update(string $requestid, array $changes): ?array {
        $record = self::get($requestid);
        if ($record === null) {
            return null;
        }

        $updated = array_merge($record, $changes, [
            'timemodified' => time(),
        ]);
        self::write_record($requestid, $updated);
        return $updated;
    }
}
