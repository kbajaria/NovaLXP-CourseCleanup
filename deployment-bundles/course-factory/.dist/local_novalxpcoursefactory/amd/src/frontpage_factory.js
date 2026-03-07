define(['core/ajax', 'core/notification'], function(Ajax, Notification) {
    var STYLE_ID = 'local-novalxpcoursefactory-style';
    var TARGET_SELECTOR = '.featured-carousel .item-1-4 .item-inner';

    function injectStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }

        var style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = [
            '.novalxp-coursefactory-shell{position:relative;display:flex;flex-direction:column;height:100%;border-radius:20px;background:linear-gradient(180deg,#f8fafc 0%,#eef4ff 100%);box-shadow:0 18px 36px rgba(20,40,90,.12);overflow:hidden;}',
            '.novalxp-coursefactory-shell::before{content:\"\";position:absolute;inset:0;background:radial-gradient(circle at top right,rgba(47,109,246,.14),transparent 42%);pointer-events:none;}',
            '.novalxp-coursefactory-body{position:relative;padding:22px;display:flex;flex-direction:column;gap:14px;min-height:100%;}',
            '.novalxp-coursefactory-eyebrow{font-size:12px;line-height:1.2;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#2f5fd7;}',
            '.novalxp-coursefactory-title{margin:0;font-size:26px;line-height:1.15;color:#0f172a;}',
            '.novalxp-coursefactory-copy{margin:0;color:#334155;font-size:14px;line-height:1.6;}',
            '.novalxp-coursefactory-form{display:flex;flex-direction:column;gap:12px;margin-top:auto;}',
            '.novalxp-coursefactory-form textarea{min-height:168px;resize:vertical;border:1px solid #cbd5e1;border-radius:16px;padding:14px 16px;font-size:14px;line-height:1.5;color:#0f172a;background:#fff;box-shadow:inset 0 1px 2px rgba(15,23,42,.04);}',
            '.novalxp-coursefactory-form textarea:focus{outline:2px solid rgba(47,95,215,.3);outline-offset:0;border-color:#2f5fd7;}',
            '.novalxp-coursefactory-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}',
            '.novalxp-coursefactory-submit{border:0;border-radius:999px;padding:11px 18px;background:#0f172a;color:#fff;font-weight:700;cursor:pointer;}',
            '.novalxp-coursefactory-submit[disabled]{opacity:.65;cursor:wait;}',
            '.novalxp-coursefactory-status{font-size:13px;line-height:1.5;color:#334155;}',
            '.novalxp-coursefactory-status.is-error{color:#b42318;}',
            '.novalxp-coursefactory-status.is-success{color:#0f766e;}',
            '@media (max-width: 767px){.novalxp-coursefactory-body{padding:18px;}.novalxp-coursefactory-title{font-size:22px;}.novalxp-coursefactory-form textarea{min-height:144px;}}'
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
            '<p class="novalxp-coursefactory-copy">Tell us the outcome you want. We will turn your brief into a short Moodle course with up to five sections and a five-question quiz. Passing the quiz will be the completion rule.</p>',
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

    function submit(methodName, brief) {
        return Ajax.call([{
            methodname: methodName,
            args: {
                brief: brief
            }
        }])[0];
    }

    function replaceCardContent(target, shell) {
        target.innerHTML = '';
        target.appendChild(shell);
        var decor = target.parentNode.parentNode.querySelector('.item-decor');
        if (decor) {
            decor.style.display = 'none';
        }
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
                var payload = await submit(config.methodName, brief);
                var summary = payload && payload.message ? ' ' + payload.message : '';
                var linkText = payload && payload.coursetitle ? payload.coursetitle : 'Open your new course';
                var href = payload && payload.courseurl ? payload.courseurl : '#';
                status.className = 'novalxp-coursefactory-status is-success';
                status.innerHTML = escapeHtml(config.successPrefix || 'Your AI-generated course is ready.') +
                    ' <a href="' + escapeHtml(href) + '">' + escapeHtml(linkText) + '</a>.' +
                    escapeHtml(summary);
                textarea.value = '';
            } catch (error) {
                setStatus(status, error && error.message ? error.message : 'Course creation failed.', 'is-error');
                Notification.exception(error);
            } finally {
                button.disabled = false;
            }
        });
    }

    function init(config) {
        injectStyle();

        var target = document.querySelector(TARGET_SELECTOR);
        if (!target || !config || !config.methodName) {
            return;
        }

        var shell = buildShell(config);
        replaceCardContent(target, shell);
        bindForm(shell, config);
    }

    return {
        init: init
    };
});
