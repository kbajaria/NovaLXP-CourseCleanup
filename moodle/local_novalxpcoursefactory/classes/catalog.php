<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

/**
 * Seeded TalentLMS catalog helpers.
 */
class catalog {
    /**
     * @return array
     */
    public static function all(): array {
        $raw = trim((string)get_config('local_novalxpcoursefactory', 'talentlmscatalogjson'));
        if ($raw === '') {
            return [];
        }

        // Some pasted seed files carry a UTF-8 BOM, which breaks json_decode().
        $raw = preg_replace('/^\xEF\xBB\xBF/', '', $raw);

        $decoded = json_decode($raw, true);
        if (!is_array($decoded)) {
            return [];
        }

        $courses = [];
        foreach ($decoded as $index => $row) {
            if (!is_array($row)) {
                continue;
            }

            $id = trim((string)($row['id'] ?? $row['courseid'] ?? $row['course_id'] ?? ''));
            $title = trim((string)($row['title'] ?? $row['name'] ?? $row['course_title'] ?? ''));
            if ($id === '' || $title === '') {
                continue;
            }

            $courses[] = [
                'id' => clean_param($id, PARAM_ALPHANUMEXT),
                'title' => clean_param($title, PARAM_TEXT),
                'url' => clean_param((string)($row['url'] ?? $row['course_url'] ?? ''), PARAM_URL),
                'category' => clean_param((string)($row['category'] ?? ''), PARAM_TEXT),
                'summary' => clean_param((string)($row['summary'] ?? $row['description'] ?? ''), PARAM_TEXT),
                'position' => $index,
            ];
        }

        usort($courses, static function(array $left, array $right): int {
            return strcmp(\core_text::strtolower($left['title']), \core_text::strtolower($right['title']));
        });

        return $courses;
    }

    /**
     * @param string $courseid
     * @return array|null
     */
    public static function find(string $courseid): ?array {
        $cleanid = clean_param($courseid, PARAM_ALPHANUMEXT);
        if ($cleanid === '') {
            return null;
        }

        foreach (self::all() as $course) {
            if ((string)$course['id'] === $cleanid) {
                return $course;
            }
        }

        return null;
    }
}
