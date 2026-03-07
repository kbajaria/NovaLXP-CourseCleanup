define([], function() {
    var STYLE_ID = 'local-novalxpcoursefactory-style';
    var PANE_SELECTOR = '#feature-pane-4';
    var LEGACY_CARD_SELECTOR = '.featured-carousel .item-1-4 .item-inner';
    var POLL_INTERVAL_MS = 5000;
    var POLL_TIMEOUT_MS = 180000;

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        var style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = [
            '.novalxp-coursefactory-shell{position:relative;display:flex;flex-direction:column;border-radius:24px;background:linear-gradient(180deg,#f8fafc 0%,#eef4ff 100%);box-shadow:0 18px 36px rgba(20,40,90,.12);overflow:hidden;}',
            '.novalxp-coursefactory-shell::before{content:\"\";position:absolute;inset:0;background:radial-gradient(circle at top right,rgba(47,109,246,.14),transparent 42%);pointer-events:none;}',
            '.novalxp-coursefactory-body{position:relative;padding:28px;display:flex;flex-direction:column;gap:16px;}',
            '.novalxp-coursefactory-eyebrow{font-size:12px;line-height:1.2;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#2f5fd7;}',
            '.novalxp-coursefactory-title{margin:0;font-size:34px;line-height:1.1;color:#0f172a;}',
            '.novalxp-coursefactory-copy{margin:0;color:#334155;font-size:16px;line-height:1.7;max-width:980px;}',
            '.novalxp-coursefactory-form{display:flex;flex-direction:column;gap:14px;}',
            '.novalxp-coursefactory-form textarea{width:100%;min-height:220px;resize:vertical;border:1px solid #cbd5e1;border-radius:20px;padding:18px 20px;font-size:16px;line-height:1.6;color:#0f172a;background:#fff;box-shadow:inset 0 1px 2px rgba(15,23,42,.04);}',
            '.novalxp-coursefactory-form textarea:focus{outline:2px solid rgba(47,95,215,.3);outline-offset:0;border-color:#2f5fd7;}',
            '.novalxp-coursefactory-actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap;}',
            '.novalxp-coursefactory-submit{border:0;border-radius:999px;padding:16px 28px;background:#5f74c8;color:#fff;font-weight:700;font-size:16px;cursor:pointer;box-shadow:0 16px 30px rgba(95,116,200,.28);}',
            '.novalxp-coursefactory-submit[disabled]{opacity:.65;cursor:wait;}',
            '.novalxp-coursefactory-status{font-size:13px;line-height:1.5;color:#334155;}',
            '.novalxp-coursefactory-status.is-error{color:#b42318;}',
            '.novalxp-coursefactory-status.is-success{color:#0f766e;}',
            '.novalxp-coursefactory-pane > :not(.novalxp-coursefactory-shell){display:none !important;}',
            '@media (max-width: 767px){.novalxp-coursefactory-body{padding:20px;}.novalxp-coursefactory-title{font-size:26px;}.novalxp-coursefactory-copy{font-size:15px;}.novalxp-coursefactory-form textarea{min-height:180px;padding:16px;}.novalxp-coursefactory-submit{width:100%;justify-content:center;}}'
        ].join('');
        document.head.appendChild(style);
    }

    function setStatus(node, text, className) {
        node.className = 'novalxp-coursefactory-status' + (className ? ' ' + className : '');
        node.textContent = text || '';
    }

    function buildShell(config) {
        var wrapper = document.createElement('div');
        wrapper.className = 'novalxp-coursefactory-shell';
        wrapper.innerHTML = [
            '<div class="novalxp-coursefactory-body">',
            '<div class="novalxp-coursefactory-eyebrow">AI-generated learning</div>',
            '<h3 class="novalxp-coursefactory-title">Describe the course you want us to build</h3>',
            '<p class="novalxp-coursefactory-copy">Be descriptive. Tell us what you want to be able to do after passing the course, what level it should start at, and any scenarios the course should cover. We will turn your brief into a NovaLXP course with up to five sections and a five-question quiz. Passing the quiz will be the completion rule. It usually takes about a minute to produce.</p>',
            '<form class="novalxp-coursefactory-form">',
            '<label class="sr-only" for="novalxp-coursefactory-brief">' + escapeHtml(config.submitLabel || 'Course description') + '</label>',
            '<textarea id="novalxp-coursefactory-brief" name="brief"></textarea>',
            '<div class="novalxp-coursefactory-actions">',
            '<button class="novalxp-coursefactory-submit" type="submit"></button>',
            '<div class="novalxp-coursefactory-status" aria-live="polite"></div>',
            '</div>',
            '</form>',
            '</div>'
        ].join('');

        var textarea = wrapper.querySelector('textarea');
        var button = wrapper.querySelector('button');
        textarea.placeholder = config.placeholder || '';
        button.textContent = config.buttonText || 'Create my course';
        return wrapper;
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
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

        if (error.error && error.error.message) {
            return error.error.message;
        }

        if (error.response && error.response.message) {
            return error.response.message;
        }

        return '';
    }

    async function submit(config, brief) {
        var body = new URLSearchParams();
        body.append('sesskey', config.sesskey || '');
        body.append('brief', brief);

        var response = await fetch(config.endpoint, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: body.toString()
        });

        var text = '';
        try {
            text = await response.text();
        } catch (parseError) {
            throw new Error('Course creation failed. The server returned an invalid response.');
        }

        var payload = null;
        try {
            payload = JSON.parse(text);
        } catch (parseError) {
            var message = String(text || '').trim();
            if (message) {
                throw new Error(message);
            }
            throw new Error('Course creation failed. The server returned an invalid response.');
        }

        if (!response.ok || !payload || !payload.status) {
            throw new Error((payload && payload.message) ? payload.message : 'Course creation failed.');
        }

        return payload;
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
            throw new Error((payload && payload.message) ? payload.message : 'Could not read course creation status.');
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
                throw new Error(job.message || 'Course creation failed.');
            }

            setStatus(statusNode, job.message || config.submittingText || 'Creating your course...', '');
            await wait(POLL_INTERVAL_MS);
        }

        throw new Error('Course creation is taking longer than expected. Please refresh shortly to check again.');
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
        target.classList.add('novalxp-coursefactory-pane');
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
        var textarea = shell.querySelector('textarea');
        var button = shell.querySelector('button');
        var status = shell.querySelector('.novalxp-coursefactory-status');

        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            var brief = String(textarea.value || '').trim();
            if (!brief) {
                setStatus(status, 'Enter a course description before submitting.', 'is-error');
                textarea.focus();
                return;
            }

            button.disabled = true;
            setStatus(status, config.submittingText || 'Creating your course...', '');

            try {
                var started = await submit(config, brief);
                var payload = await pollForCompletion(config, started.requestid, status);
                var summary = payload && payload.message ? ' ' + payload.message : '';
                var linkText = payload && payload.coursetitle ? payload.coursetitle : 'Open your new course';
                var href = payload && payload.courseurl ? payload.courseurl : '#';
                status.className = 'novalxp-coursefactory-status is-success';
                status.innerHTML = escapeHtml(config.successPrefix || 'Your AI-generated course is ready.') +
                    ' <a href="' + escapeHtml(href) + '">' + escapeHtml(linkText) + '</a>.' +
                    escapeHtml(summary);
                textarea.value = '';
            } catch (error) {
                setStatus(status, extractErrorMessage(error) || 'Course creation failed.', 'is-error');
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
