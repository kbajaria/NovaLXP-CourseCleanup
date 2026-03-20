define([], function() {
    var STYLE_ID = 'local-novalxpcoursemigration-style';
    var PANE_SELECTOR = '#feature-pane-3';
    var LEGACY_CARD_SELECTOR = '.featured-carousel .item-1-3 .item-inner';
    var POLL_INTERVAL_MS = 3000;
    var POLL_TIMEOUT_MS = 60000;

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        var style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = [
            '.novalxp-coursemigration-shell{position:relative;display:flex;flex-direction:column;border-radius:24px;background:linear-gradient(180deg,#fff9ee 0%,#eef6ff 100%);box-shadow:0 18px 36px rgba(20,40,90,.12);overflow:hidden;}',
            '.novalxp-coursemigration-shell::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at top right,rgba(28,113,216,.12),transparent 40%);pointer-events:none;}',
            '.novalxp-coursemigration-body{position:relative;padding:28px;display:flex;flex-direction:column;gap:16px;}',
            '.novalxp-coursemigration-eyebrow{font-size:12px;line-height:1.2;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9a3412;}',
            '.novalxp-coursemigration-title{margin:0;font-size:34px;line-height:1.1;color:#0f172a;}',
            '.novalxp-coursemigration-copy{margin:0;color:#334155;font-size:16px;line-height:1.7;max-width:980px;}',
            '.novalxp-coursemigration-form{display:flex;flex-direction:column;gap:14px;}',
            '.novalxp-coursemigration-label{display:block;font-size:14px;font-weight:700;color:#0f172a;}',
            '.novalxp-coursemigration-search{width:100%;border:1px solid #cbd5e1;border-radius:18px;padding:15px 18px;font-size:16px;line-height:1.4;color:#0f172a;background:#fff;}',
            '.novalxp-coursemigration-search:focus,.novalxp-coursemigration-reason:focus,.novalxp-coursemigration-results:focus{outline:2px solid rgba(28,113,216,.25);border-color:#1c71d8;}',
            '.novalxp-coursemigration-results-wrap{display:flex;flex-direction:column;gap:8px;}',
            '.novalxp-coursemigration-results{width:100%;min-height:180px;border:1px solid #cbd5e1;border-radius:24px !important;padding:18px 20px;background:#fff;color:#0f172a;box-shadow:inset 0 1px 2px rgba(15,23,42,.04);appearance:none;-webkit-appearance:none;}',
            '.novalxp-coursemigration-selection{font-size:13px;line-height:1.5;color:#475569;}',
            '.novalxp-coursemigration-reason{width:100%;min-height:140px;resize:vertical;border:1px solid #cbd5e1;border-radius:20px;padding:18px 20px;font-size:16px;line-height:1.6;color:#0f172a;background:#fff;box-shadow:inset 0 1px 2px rgba(15,23,42,.04);}',
            '.novalxp-coursemigration-actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap;}',
            '.novalxp-coursemigration-submit{border:0;border-radius:999px;padding:16px 28px;background:#5f71c2;color:#fff;font-weight:700;font-size:16px;cursor:pointer;box-shadow:0 16px 30px rgba(95,113,194,.24);}',
            '.novalxp-coursemigration-submit[disabled]{opacity:.65;cursor:wait;}',
            '.novalxp-coursemigration-status{font-size:13px;line-height:1.5;color:#334155;}',
            '.novalxp-coursemigration-status.is-error{color:#b42318;}',
            '.novalxp-coursemigration-status.is-success{color:#0f766e;}',
            '.novalxp-coursemigration-empty{padding:18px;border:1px dashed #cbd5e1;border-radius:18px;background:rgba(255,255,255,.8);color:#475569;}',
            '.novalxp-coursemigration-pane > :not(.novalxp-coursemigration-shell){display:none !important;}',
            '@media (max-width: 767px){.novalxp-coursemigration-body{padding:20px;}.novalxp-coursemigration-title{font-size:26px;}.novalxp-coursemigration-copy{font-size:15px;}.novalxp-coursemigration-submit{width:100%;justify-content:center;}}'
        ].join('');
        document.head.appendChild(style);
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function setStatus(node, text, className) {
        node.className = 'novalxp-coursemigration-status' + (className ? ' ' + className : '');
        node.textContent = text || '';
    }

    function normaliseCatalog(config) {
        if (!config || !Array.isArray(config.catalog)) {
            return [];
        }
        return config.catalog.filter(function(item) {
            return item && item.id && item.title;
        });
    }

    function buildShell(config) {
        var wrapper = document.createElement('div');
        var catalog = normaliseCatalog(config);
        wrapper.className = 'novalxp-coursemigration-shell';

        if (!catalog.length) {
            wrapper.innerHTML = [
                '<div class="novalxp-coursemigration-body">',
                '<div class="novalxp-coursemigration-eyebrow">Course continuity</div>',
                '<h3 class="novalxp-coursemigration-title">Request a TalentLMS course in NovaLXP</h3>',
                '<p class="novalxp-coursemigration-copy">We can queue learner requests for TalentLMS courses that still need a home in NovaLXP after the old platform is retired.</p>',
                '<div class="novalxp-coursemigration-empty">' + escapeHtml(config.emptyCatalogText || 'No TalentLMS catalog has been seeded yet.') + '</div>',
                '</div>'
            ].join('');
            return wrapper;
        }

        wrapper.innerHTML = [
            '<div class="novalxp-coursemigration-body">',
            '<div class="novalxp-coursemigration-eyebrow">Course continuity</div>',
            '<h3 class="novalxp-coursemigration-title">Request a TalentLMS course in NovaLXP</h3>',
            '<p class="novalxp-coursemigration-copy">Search the seeded TalentLMS catalog, pick the course you still need, and tell us why it matters. We will send the request to the NovaLXP roadmap feedback queue for review.</p>',
            '<form class="novalxp-coursemigration-form">',
            '<label class="novalxp-coursemigration-label" for="novalxp-coursemigration-search">' + escapeHtml(config.searchLabel || 'Search TalentLMS courses') + '</label>',
            '<input id="novalxp-coursemigration-search" class="novalxp-coursemigration-search" type="search" autocomplete="off" />',
            '<div class="novalxp-coursemigration-results-wrap">',
            '<div class="novalxp-coursemigration-label">' + escapeHtml(config.resultsHeading || 'Matching TalentLMS courses') + '</div>',
            '<select class="novalxp-coursemigration-results" size="6" aria-label="' + escapeHtml(config.selectPrompt || 'Select a course') + '"></select>',
            '<div class="novalxp-coursemigration-selection"></div>',
            '</div>',
            '<label class="novalxp-coursemigration-label" for="novalxp-coursemigration-reason">' + escapeHtml(config.reasonLabel || 'Why do you need this course in NovaLXP?') + '</label>',
            '<textarea id="novalxp-coursemigration-reason" class="novalxp-coursemigration-reason" name="reason"></textarea>',
            '<div class="novalxp-coursemigration-actions">',
            '<button class="novalxp-coursemigration-submit" type="submit"></button>',
            '<div class="novalxp-coursemigration-status" aria-live="polite"></div>',
            '</div>',
            '</form>',
            '</div>'
        ].join('');

        wrapper.querySelector('.novalxp-coursemigration-search').placeholder = config.searchPlaceholder || '';
        wrapper.querySelector('.novalxp-coursemigration-reason').placeholder = config.reasonPlaceholder || '';
        wrapper.querySelector('.novalxp-coursemigration-submit').textContent = config.buttonText || 'Request this migration';
        return wrapper;
    }

    function extractErrorMessage(error) {
        if (!error) {
            return '';
        }
        if (typeof error === 'string') {
            return error;
        }
        if (error.message) {
            return error.message;
        }
        return '';
    }

    function renderResults(select, selectionNode, catalog, query, config) {
        var filtered = catalog.filter(function(item) {
            var haystack = [item.title, item.category, item.summary].join(' ').toLowerCase();
            return haystack.indexOf(query.toLowerCase()) !== -1;
        }).slice(0, 100);

        select.innerHTML = '';
        filtered.forEach(function(item, index) {
            var option = document.createElement('option');
            var parts = [item.title];
            if (item.category) {
                parts.push('(' + item.category + ')');
            }
            option.value = item.id;
            option.textContent = parts.join(' ');
            option.dataset.title = item.title || '';
            option.dataset.category = item.category || '';
            if (index === 0) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        if (!filtered.length) {
            selectionNode.textContent = config.emptyCatalogText || '';
            return [];
        }

        updateSelectionSummary(select, selectionNode, config);
        return filtered;
    }

    function updateSelectionSummary(select, selectionNode, config) {
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

    async function submit(config, payload) {
        var body = new URLSearchParams();
        body.append('sesskey', config.sesskey || '');
        body.append('sourcecourseid', payload.sourcecourseid);
        body.append('reason', payload.reason);

        var response = await fetch(config.endpoint, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: body.toString()
        });

        var text = await response.text();
        var parsed = JSON.parse(text);
        if (!response.ok || !parsed || !parsed.status) {
            throw new Error(parsed && parsed.message ? parsed.message : 'Migration request failed.');
        }
        return parsed;
    }

    async function fetchJobStatus(config, requestId) {
        var url = new URL(config.statusEndpoint, window.location.origin);
        url.searchParams.set('requestid', requestId);

        var response = await fetch(url.toString(), {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        var text = await response.text();
        var payload = JSON.parse(text);
        if (!response.ok || !payload || !payload.status) {
            throw new Error((payload && payload.message) ? payload.message : 'Could not read migration request status.');
        }
        return payload;
    }

    function wait(ms) {
        return new Promise(function(resolve) {
            window.setTimeout(resolve, ms);
        });
    }

    async function pollForCompletion(config, requestId, statusNode) {
        var startedAt = Date.now();

        while ((Date.now() - startedAt) < POLL_TIMEOUT_MS) {
            var job = await fetchJobStatus(config, requestId);
            if (job.state === 'complete') {
                return job;
            }
            if (job.state === 'failed') {
                throw new Error(job.message || 'Migration request failed.');
            }

            setStatus(statusNode, job.message || config.submittingText || 'Submitting your TalentLMS migration request...', '');
            await wait(POLL_INTERVAL_MS);
        }

        throw new Error('The migration request is taking longer than expected. Please refresh shortly to check again.');
    }

    function replaceCardContent(target, shell) {
        target.innerHTML = '';
        target.appendChild(shell);
        var decor = target.parentNode.parentNode.querySelector('.item-decor');
        if (decor) {
            decor.style.display = 'none';
        }
    }

    function replacePaneContent(target, shell) {
        target.classList.add('novalxp-coursemigration-pane');
        target.innerHTML = '';
        target.appendChild(shell);
    }

    function findTarget() {
        var pane = document.querySelector(PANE_SELECTOR);
        if (pane) {
            return {
                mode: 'pane',
                node: pane
            };
        }

        var legacyCard = document.querySelector(LEGACY_CARD_SELECTOR);
        if (legacyCard) {
            return {
                mode: 'card',
                node: legacyCard
            };
        }

        return null;
    }

    function bindForm(shell, config) {
        var form = shell.querySelector('form');
        if (!form) {
            return;
        }

        var catalog = normaliseCatalog(config);
        var search = shell.querySelector('.novalxp-coursemigration-search');
        var select = shell.querySelector('.novalxp-coursemigration-results');
        var selection = shell.querySelector('.novalxp-coursemigration-selection');
        var reason = shell.querySelector('.novalxp-coursemigration-reason');
        var button = shell.querySelector('.novalxp-coursemigration-submit');
        var status = shell.querySelector('.novalxp-coursemigration-status');

        renderResults(select, selection, catalog, '', config);

        search.addEventListener('input', function() {
            renderResults(select, selection, catalog, search.value || '', config);
        });

        select.addEventListener('change', function() {
            updateSelectionSummary(select, selection, config);
        });

        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            if (!select.options.length) {
                setStatus(status, config.emptyCatalogText || 'No TalentLMS catalog has been seeded yet.', 'is-error');
                return;
            }

            var sourcecourseid = String(select.value || '').trim();
            var reasonText = String(reason.value || '').trim();
            if (!sourcecourseid || !reasonText) {
                setStatus(status, 'Choose a course and tell us why you need it in NovaLXP.', 'is-error');
                if (!sourcecourseid) {
                    select.focus();
                } else {
                    reason.focus();
                }
                return;
            }

            button.disabled = true;
            setStatus(status, config.submittingText || 'Submitting your TalentLMS migration request...', '');

            try {
                var started = await submit(config, {
                    sourcecourseid: sourcecourseid,
                    reason: reasonText
                });
                await pollForCompletion(config, started.requestid, status);
                setStatus(status, config.successMessage || 'Your request has been logged for review and added to the NovaLXP roadmap feedback queue.', 'is-success');
                reason.value = '';
            } catch (error) {
                setStatus(status, extractErrorMessage(error) || 'Migration request failed.', 'is-error');
            } finally {
                button.disabled = false;
            }
        });
    }

    function init(config) {
        injectStyle();

        var target = findTarget();
        if (!target || !config || !config.endpoint || !config.statusEndpoint || !config.sesskey) {
            return;
        }

        var shell = buildShell(config);
        if (target.mode === 'pane') {
            replacePaneContent(target.node, shell);
        } else {
            replaceCardContent(target.node, shell);
        }
        bindForm(shell, config);
    }

    return {
        init: init
    };
});
