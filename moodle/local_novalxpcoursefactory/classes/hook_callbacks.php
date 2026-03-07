<?php
namespace local_novalxpcoursefactory;

defined('MOODLE_INTERNAL') || die();

use core\hook\output\before_footer_html_generation;

/**
 * Hook callbacks for local_novalxpcoursefactory.
 */
class hook_callbacks {
    /**
     * Inject the front-page featured-pane replacement script for logged-in learners.
     *
     * @param before_footer_html_generation $hook
     */
    public static function before_footer_html_generation(before_footer_html_generation $hook): void {
        global $PAGE;

        if (!isloggedin() || isguestuser()) {
            return;
        }

        if ((int)get_config('local_novalxpcoursefactory', 'enabled') !== 1) {
            return;
        }

        $path = '';
        if (!empty($PAGE->url)) {
            $path = (string)$PAGE->url->get_path();
        }

        $isfrontpage = $PAGE->pagelayout === 'frontpage'
            || $PAGE->pagetype === 'site-index'
            || $path === '/'
            || $path === '/index.php';

        if (!$isfrontpage) {
            return;
        }

        $PAGE->requires->js_call_amd('local_novalxpcoursefactory/frontpage_factory', 'init', [[
            'endpoint' => (new \moodle_url('/local/novalxpcoursefactory/course_factory.php'))->out(false),
            'statusEndpoint' => (new \moodle_url('/local/novalxpcoursefactory/job_status.php'))->out(false),
            'sesskey' => sesskey(),
            'placeholder' => (string)get_config('local_novalxpcoursefactory', 'placeholdertext'),
            'buttonText' => (string)get_config('local_novalxpcoursefactory', 'buttontext'),
            'submitLabel' => get_string('submitlabel', 'local_novalxpcoursefactory'),
            'submittingText' => get_string('submitting', 'local_novalxpcoursefactory'),
            'successPrefix' => get_string('successprefix', 'local_novalxpcoursefactory'),
        ]]);
    }
}
