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
            'submittingText' => get_string('submitting', 'local_novalxpcoursefactory'),
            'successPrefix' => get_string('successprefix', 'local_novalxpcoursefactory'),
            'successSuffix' => get_string('successsuffix', 'local_novalxpcoursefactory'),
            'migrationConfig' => [
                'endpoint' => (new \moodle_url('/local/novalxpcoursefactory/migration_request.php'))->out(false),
                'statusEndpoint' => (new \moodle_url('/local/novalxpcoursefactory/job_status.php'))->out(false),
                'sesskey' => sesskey(),
                'reasonPlaceholder' => get_string('migrationreasonplaceholder', 'local_novalxpcoursefactory'),
                'buttonText' => get_string('migrationbuttondefault', 'local_novalxpcoursefactory'),
                'catalog' => catalog::all(),
                'searchLabel' => get_string('searchlabel', 'local_novalxpcoursefactory'),
                'reasonLabel' => get_string('reasonlabel', 'local_novalxpcoursefactory'),
                'submittingText' => get_string('migrationsubmitting', 'local_novalxpcoursefactory'),
                'successMessage' => get_string('migrationsuccess', 'local_novalxpcoursefactory'),
                'emptyCatalogText' => get_string('emptycatalog', 'local_novalxpcoursefactory'),
                'searchPlaceholder' => get_string('searchplaceholder', 'local_novalxpcoursefactory'),
                'resultsHeading' => get_string('resultsheading', 'local_novalxpcoursefactory'),
                'selectPrompt' => get_string('selectprompt', 'local_novalxpcoursefactory'),
                'selectionSummaryPrefix' => get_string('selectionsummaryprefix', 'local_novalxpcoursefactory'),
            ],
        ]]);

        $migrationconfig = [
            'endpoint' => (new \moodle_url('/local/novalxpcoursefactory/migration_request.php'))->out(false),
            'statusEndpoint' => (new \moodle_url('/local/novalxpcoursefactory/job_status.php'))->out(false),
            'sesskey' => sesskey(),
            'reasonPlaceholder' => get_string('migrationreasonplaceholder', 'local_novalxpcoursefactory'),
            'buttonText' => get_string('migrationbuttondefault', 'local_novalxpcoursefactory'),
            'catalog' => catalog::all(),
            'searchLabel' => get_string('searchlabel', 'local_novalxpcoursefactory'),
            'reasonLabel' => get_string('reasonlabel', 'local_novalxpcoursefactory'),
            'submittingText' => get_string('migrationsubmitting', 'local_novalxpcoursefactory'),
            'successMessage' => get_string('migrationsuccess', 'local_novalxpcoursefactory'),
            'emptyCatalogText' => get_string('emptycatalog', 'local_novalxpcoursefactory'),
            'searchPlaceholder' => get_string('searchplaceholder', 'local_novalxpcoursefactory'),
            'resultsHeading' => get_string('resultsheading', 'local_novalxpcoursefactory'),
            'selectPrompt' => get_string('selectprompt', 'local_novalxpcoursefactory'),
            'selectionSummaryPrefix' => get_string('selectionsummaryprefix', 'local_novalxpcoursefactory'),
        ];
        $migrationjson = json_encode($migrationconfig, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT);
        $fallbackjs = <<<JS
(function() {
    var config = {$migrationjson};
    var styleId = 'local-novalxpcoursemigration-inline-style';
    var applied = false;

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function injectStyle() {
        if (document.getElementById(styleId)) {
            return;
        }
        var style = document.createElement('style');
        style.id = styleId;
        style.textContent = '.novalxp-coursemigration-shell{position:relative;display:flex;flex-direction:column;border-radius:24px;background:linear-gradient(180deg,#fff9ee 0%,#eef6ff 100%);box-shadow:0 18px 36px rgba(20,40,90,.12);overflow:hidden;}.novalxp-coursemigration-body{position:relative;padding:28px;display:flex;flex-direction:column;gap:16px;}.novalxp-coursemigration-eyebrow{font-size:12px;line-height:1.2;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9a3412;}.novalxp-coursemigration-title{margin:0;font-size:34px;line-height:1.1;color:#0f172a;}.novalxp-coursemigration-copy{margin:0;color:#334155;font-size:16px;line-height:1.7;max-width:980px;}.novalxp-coursemigration-form{display:flex;flex-direction:column;gap:14px;}.novalxp-coursemigration-label{display:block;font-size:14px;font-weight:700;color:#0f172a;}.novalxp-coursemigration-search{width:100%;border:1px solid #cbd5e1;border-radius:18px;padding:15px 18px;font-size:16px;line-height:1.4;color:#0f172a;background:#fff;}.novalxp-coursemigration-results-wrap{display:flex;flex-direction:column;gap:8px;}.novalxp-coursemigration-results{width:100%;min-height:180px;border:1px solid #cbd5e1;border-radius:24px !important;padding:18px 20px;background:#fff;color:#0f172a;box-shadow:inset 0 1px 2px rgba(15,23,42,.04);appearance:none;-webkit-appearance:none;}.novalxp-coursemigration-selection{font-size:13px;line-height:1.5;color:#475569;}.novalxp-coursemigration-reason{width:100%;min-height:140px;resize:vertical;border:1px solid #cbd5e1;border-radius:20px;padding:18px 20px;font-size:16px;line-height:1.6;color:#0f172a;background:#fff;}.novalxp-coursemigration-actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap;}.novalxp-coursemigration-submit{border:0;border-radius:999px;padding:16px 28px;background:#5f71c2;color:#fff;font-weight:700;font-size:16px;cursor:pointer;}.novalxp-coursemigration-status{font-size:13px;line-height:1.5;color:#334155;}.novalxp-coursemigration-status.is-error{color:#b42318;}.novalxp-coursemigration-status.is-success{color:#0f766e;}.novalxp-coursemigration-empty{padding:18px;border:1px dashed #cbd5e1;border-radius:18px;background:rgba(255,255,255,.8);color:#475569;}';
        document.head.appendChild(style);
    }

    function renderResults(select, selectionNode, catalog, query) {
        var filtered = catalog.filter(function(item) {
            var haystack = [item.title, item.category, item.summary].join(' ').toLowerCase();
            return haystack.indexOf(String(query || '').toLowerCase()) !== -1;
        }).slice(0, 100);
        select.innerHTML = '';
        filtered.forEach(function(item, index) {
            var option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.category ? item.title + ' (' + item.category + ')' : item.title;
            option.dataset.title = item.title || '';
            option.dataset.category = item.category || '';
            if (index === 0) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        if (!filtered.length) {
            selectionNode.textContent = config.emptyCatalogText || '';
            return;
        }
        updateSelection(select, selectionNode);
    }

    function updateSelection(select, selectionNode) {
        if (!select.options.length) {
            selectionNode.textContent = '';
            return;
        }
        var option = select.options[select.selectedIndex];
        var summary = option.dataset.title || option.textContent || '';
        if (option.dataset.category) {
            summary += ' | ' + option.dataset.category;
        }
        selectionNode.textContent = (config.selectionSummaryPrefix || 'Selected course:') + ' ' + summary;
    }

    async function postForm(sourcecourseid, reason) {
        var body = new URLSearchParams();
        body.append('sesskey', config.sesskey || '');
        body.append('sourcecourseid', sourcecourseid);
        body.append('reason', reason);
        var response = await fetch(config.endpoint, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest'},
            body: body.toString()
        });
        var payload = JSON.parse(await response.text());
        if (!response.ok || !payload || !payload.status) {
            throw new Error(payload && payload.message ? payload.message : 'Migration request failed.');
        }
        return payload;
    }

    async function pollStatus(requestid) {
        var startedAt = Date.now();
        while ((Date.now() - startedAt) < 60000) {
            var url = new URL(config.statusEndpoint, window.location.origin);
            url.searchParams.set('requestid', requestid);
            var response = await fetch(url.toString(), {
                method: 'GET',
                credentials: 'same-origin',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            var payload = JSON.parse(await response.text());
            if (!response.ok || !payload || !payload.status) {
                throw new Error(payload && payload.message ? payload.message : 'Could not read migration request status.');
            }
            if (payload.state === 'complete') {
                return payload;
            }
            if (payload.state === 'failed') {
                throw new Error(payload.message || 'Migration request failed.');
            }
            await new Promise(function(resolve) { window.setTimeout(resolve, 3000); });
        }
        throw new Error('The migration request is taking longer than expected. Please refresh shortly to check again.');
    }

    function applyFallback() {
        if (applied) {
            return true;
        }
        var pane = document.querySelector('#feature-pane-3');
        if (!pane || !config || !config.endpoint || !config.statusEndpoint || !config.sesskey) {
            return false;
        }
        injectStyle();
        var catalog = Array.isArray(config.catalog) ? config.catalog.filter(function(item) { return item && item.id && item.title; }) : [];
        var html = '';
        if (!catalog.length) {
            html = '<div class="novalxp-coursemigration-shell"><div class="novalxp-coursemigration-body"><div class="novalxp-coursemigration-eyebrow">Course continuity</div><h3 class="novalxp-coursemigration-title">Request a TalentLMS course in NovaLXP</h3><p class="novalxp-coursemigration-copy">We can queue learner requests for TalentLMS courses that still need a home in NovaLXP after the old platform is retired.</p><div class="novalxp-coursemigration-empty">' + escapeHtml(config.emptyCatalogText || 'No TalentLMS catalog has been seeded yet.') + '</div></div></div>';
        } else {
            html = '<div class="novalxp-coursemigration-shell"><div class="novalxp-coursemigration-body"><div class="novalxp-coursemigration-eyebrow">Course continuity</div><h3 class="novalxp-coursemigration-title">Request a TalentLMS course in NovaLXP</h3><p class="novalxp-coursemigration-copy">Search the seeded TalentLMS catalog, pick the course you still need, and tell us why it matters. We will send the request to the NovaLXP roadmap feedback queue for review.</p><form class="novalxp-coursemigration-form"><label class="novalxp-coursemigration-label" for="novalxp-inline-migration-search">' + escapeHtml(config.searchLabel || 'Search TalentLMS courses') + '</label><input id="novalxp-inline-migration-search" class="novalxp-coursemigration-search" type="search" autocomplete="off" /><div class="novalxp-coursemigration-results-wrap"><div class="novalxp-coursemigration-label">' + escapeHtml(config.resultsHeading || 'Matching TalentLMS courses') + '</div><select class="novalxp-coursemigration-results" size="6" aria-label="' + escapeHtml(config.selectPrompt || 'Select a course') + '"></select><div class="novalxp-coursemigration-selection"></div></div><label class="novalxp-coursemigration-label" for="novalxp-inline-migration-reason">' + escapeHtml(config.reasonLabel || 'Why do you need this course in NovaLXP?') + '</label><textarea id="novalxp-inline-migration-reason" class="novalxp-coursemigration-reason" name="reason"></textarea><div class="novalxp-coursemigration-actions"><button class="novalxp-coursemigration-submit" type="submit">' + escapeHtml(config.buttonText || 'Request this migration') + '</button><div class="novalxp-coursemigration-status" aria-live="polite"></div></div></form></div></div>';
        }
        pane.innerHTML = html;
        applied = true;

        var form = pane.querySelector('form');
        if (!form) {
            return true;
        }
        var search = pane.querySelector('.novalxp-coursemigration-search');
        var select = pane.querySelector('.novalxp-coursemigration-results');
        var selection = pane.querySelector('.novalxp-coursemigration-selection');
        var reason = pane.querySelector('.novalxp-coursemigration-reason');
        var status = pane.querySelector('.novalxp-coursemigration-status');
        var button = pane.querySelector('.novalxp-coursemigration-submit');
        search.placeholder = config.searchPlaceholder || '';
        reason.placeholder = config.reasonPlaceholder || '';
        renderResults(select, selection, catalog, '');
        search.addEventListener('input', function() { renderResults(select, selection, catalog, search.value || ''); });
        select.addEventListener('change', function() { updateSelection(select, selection); });
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            if (!select.options.length) {
                status.className = 'novalxp-coursemigration-status is-error';
                status.textContent = config.emptyCatalogText || 'No TalentLMS catalog has been seeded yet.';
                return;
            }
            var sourcecourseid = String(select.value || '').trim();
            var reasonText = String(reason.value || '').trim();
            if (!sourcecourseid || !reasonText) {
                status.className = 'novalxp-coursemigration-status is-error';
                status.textContent = 'Choose a course and tell us why you need it in NovaLXP.';
                return;
            }
            button.disabled = true;
            status.className = 'novalxp-coursemigration-status';
            status.textContent = config.submittingText || 'Submitting your TalentLMS migration request...';
            try {
                var started = await postForm(sourcecourseid, reasonText);
                await pollStatus(started.requestid);
                status.className = 'novalxp-coursemigration-status is-success';
                status.textContent = config.successMessage || 'Your request has been logged for review and added to the NovaLXP roadmap feedback queue.';
                reason.value = '';
            } catch (error) {
                status.className = 'novalxp-coursemigration-status is-error';
                status.textContent = error && error.message ? error.message : 'Migration request failed.';
            } finally {
                button.disabled = false;
            }
        });
        return true;
    }

    function start() {
        if (applyFallback()) {
            return;
        }
        var attempts = 0;
        var timer = window.setInterval(function() {
            attempts += 1;
            if (applyFallback() || attempts >= 40) {
                window.clearInterval(timer);
            }
        }, 500);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
    window.addEventListener('load', start);
})();
JS;
        $PAGE->requires->js_init_code($fallbackjs);
    }
}
