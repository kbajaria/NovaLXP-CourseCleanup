import { GetSecretValueCommand, SecretsManagerClient } from '@aws-sdk/client-secrets-manager';
import OpenAI from 'openai';

const requiredEnv = [
  'OPENAI_MODEL',
  'MOODLE_BASE_URL',
];

const secretsClient = new SecretsManagerClient({});
let cachedMoodleSecret;
let cachedOpenAiSecret;

const log = (stage, details = {}) => {
  const payload = {
    component: 'novalxp-course-factory',
    stage,
    ...details,
  };
  console.log(JSON.stringify(payload));
};

const json = (statusCode, body) => ({
  statusCode,
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(body)
});

const isHttpEvent = (event) => !!event?.requestContext || typeof event?.body !== 'undefined';

const parseBody = (event) => {
  if (!isHttpEvent(event)) {
    return event;
  }

  if (!event.body) {
    return null;
  }

  const body = event.isBase64Encoded
    ? Buffer.from(event.body, 'base64').toString('utf8')
    : event.body;

  return JSON.parse(body);
};

const validateEnv = () => {
  for (const name of requiredEnv) {
    if (!process.env[name]) {
      throw new Error(`Missing required environment variable: ${name}`);
    }
  }

  if (!process.env.OPENAI_API_KEY && !process.env.OPENAI_SECRET_ARN) {
    throw new Error('Missing OpenAI credentials: set OPENAI_API_KEY or OPENAI_SECRET_ARN');
  }
  if (!process.env.MOODLE_TOKEN && !process.env.MOODLE_SECRET_ARN) {
    throw new Error('Missing Moodle credentials: set MOODLE_TOKEN or MOODLE_SECRET_ARN');
  }
};

const getOpenAiSecret = async () => {
  if (cachedOpenAiSecret) {
    return cachedOpenAiSecret;
  }

  if (!process.env.OPENAI_SECRET_ARN) {
    cachedOpenAiSecret = {};
    return cachedOpenAiSecret;
  }

  const response = await secretsClient.send(new GetSecretValueCommand({
    SecretId: process.env.OPENAI_SECRET_ARN
  }));

  if (!response.SecretString) {
    throw new Error('OpenAI secret did not contain SecretString');
  }

  const secret = JSON.parse(response.SecretString);
  cachedOpenAiSecret = {
    openAiApiKey: secret.OPENAI_API_KEY || secret.openAiApiKey || secret.apiKey || '',
  };
  return cachedOpenAiSecret;
};

const getResolvedOpenAiConfig = async () => {
  const secret = await getOpenAiSecret();
  return {
    openAiApiKey: process.env.OPENAI_API_KEY || secret.openAiApiKey || '',
  };
};

const getMoodleSecret = async () => {
  if (cachedMoodleSecret) {
    return cachedMoodleSecret;
  }

  if (!process.env.MOODLE_SECRET_ARN) {
    cachedMoodleSecret = {};
    return cachedMoodleSecret;
  }

  const response = await secretsClient.send(new GetSecretValueCommand({
    SecretId: process.env.MOODLE_SECRET_ARN
  }));

  if (!response.SecretString) {
    throw new Error('Moodle secret did not contain SecretString');
  }

  const secret = JSON.parse(response.SecretString);
  cachedMoodleSecret = {
    moodleToken: secret.MOODLE_TOKEN || secret.moodleToken || secret.token || '',
    moodleBaseUrl: secret.MOODLE_BASE_URL || secret.moodleBaseUrl || secret.baseUrl || '',
  };
  return cachedMoodleSecret;
};

const getResolvedMoodleConfig = async () => {
  const secret = await getMoodleSecret();
  return {
    moodleToken: process.env.MOODLE_TOKEN || secret.moodleToken || '',
    moodleBaseUrl: process.env.MOODLE_BASE_URL || secret.moodleBaseUrl || '',
  };
};

const courseFactorySchema = {
  name: 'novalxp_course_factory',
  strict: true,
  schema: {
    type: 'object',
    additionalProperties: false,
    required: ['title', 'summary', 'sections', 'quiz'],
    properties: {
      title: { type: 'string' },
      summary: { type: 'string' },
      sections: {
        type: 'array',
        minItems: 1,
        maxItems: 5,
        items: {
          type: 'object',
          additionalProperties: false,
          required: ['title', 'content'],
          properties: {
            title: { type: 'string' },
            content: { type: 'string', minLength: 500 }
          }
        }
      },
      quiz: {
        type: 'object',
        additionalProperties: false,
        required: ['title', 'questions'],
        properties: {
          title: { type: 'string' },
          questions: {
            type: 'array',
            minItems: 5,
            maxItems: 5,
            items: {
              type: 'object',
              additionalProperties: false,
              required: ['prompt', 'options', 'correct_index', 'explanation'],
              properties: {
                prompt: { type: 'string' },
                options: {
                  type: 'array',
                  minItems: 4,
                  maxItems: 4,
                  items: { type: 'string' }
                },
                correct_index: { type: 'integer', minimum: 0, maximum: 3 },
                explanation: { type: 'string' }
              }
            }
          }
        }
      }
    }
  }
};

const MIN_SECTION_WORDS = 120;
const MIN_SECTION_PARAGRAPHS = 3;
const MAX_GENERATION_ATTEMPTS = 2;

const buildPrompt = (brief, retryReason = '') => [
  'You are generating a Moodle course for NovaLXP.',
  'Return valid JSON only matching the schema.',
  'Requirements:',
  '- Produce a concise but substantial learner-facing course.',
  '- Use no more than 5 sections.',
  '- Include exactly 5 multiple-choice quiz questions.',
  '- Make the quiz assess whether the learner can do the outcome described in the brief.',
  '- Passing the quiz is the course completion rule.',
  '- Every section content field must contain at least 3 full paragraphs of narrative teaching.',
  '- Every section should usually be 120 to 220 words.',
  '- Do not write one-sentence summaries or bullet-only sections.',
  '- Each section should explain the concept, give practical guidance, and include at least one concrete example or scenario.',
  '- Separate paragraphs with blank lines so Moodle renders them as multiple paragraphs.',
  '',
  retryReason ? `Revision note: ${retryReason}` : '',
  retryReason ? '' : '',
  'Learner brief:',
  brief.trim(),
].filter(Boolean).join('\n');

const countWords = (value) => String(value || '')
  .trim()
  .split(/\s+/)
  .filter(Boolean)
  .length;

const countParagraphs = (value) => String(value || '')
  .split(/\n\s*\n/)
  .map((part) => part.trim())
  .filter(Boolean)
  .length;

const validateSpec = (spec) => {
  if (!spec || !Array.isArray(spec.sections) || spec.sections.length === 0) {
    throw new Error('Generated course did not contain any sections');
  }

  const issues = [];
  spec.sections.forEach((section, index) => {
    const words = countWords(section.content);
    const paragraphs = countParagraphs(section.content);
    if (paragraphs < MIN_SECTION_PARAGRAPHS) {
      issues.push(`section ${index + 1} "${section.title}" has ${paragraphs} paragraphs`);
    }
    if (words < MIN_SECTION_WORDS) {
      issues.push(`section ${index + 1} "${section.title}" has only ${words} words`);
    }
  });

  if (issues.length > 0) {
    throw new Error(`Generated sections were too short: ${issues.join('; ')}`);
  }

  return spec;
};

const escapeHtml = (value) => String(value || '')
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const cleanGiftText = (value) => String(value || '')
  .replace(/[{}~=#:]/g, ' ')
  .replace(/\s+/g, ' ')
  .trim();

const toGift = (spec) => {
  const blocks = [];
  for (const question of spec.quiz.questions) {
    const lines = [];
    const prompt = cleanGiftText(question.prompt);
    lines.push(`::${prompt.slice(0, 40)}::${prompt}{`);
    for (let index = 0; index < question.options.length; index++) {
      const prefix = index === question.correct_index ? '=' : '~';
      lines.push(`${prefix}${cleanGiftText(question.options[index])}#${cleanGiftText(question.explanation)}`);
    }
    lines.push('}');
    blocks.push(lines.join('\n'));
  }
  return blocks.join('\n\n');
};

const callMoodle = async (wsfunction, params) => {
  const { moodleToken, moodleBaseUrl } = await getResolvedMoodleConfig();

  if (!moodleToken) {
    throw new Error('No Moodle token available');
  }
  if (!moodleBaseUrl) {
    throw new Error('No Moodle base URL available');
  }

  const form = new URLSearchParams();
  form.set('wstoken', moodleToken);
  form.set('wsfunction', wsfunction);
  form.set('moodlewsrestformat', 'json');

  for (const [key, value] of Object.entries(params || {})) {
    if (value !== undefined && value !== null && value !== '') {
      form.set(key, String(value));
    }
  }

  log('moodle_ws_call_start', {
    wsfunction,
    courseid: params && params.courseid ? Number(params.courseid) : undefined,
    quizid: params && params.quizid ? Number(params.quizid) : undefined,
    quizcmid: params && params.quizcmid ? Number(params.quizcmid) : undefined,
  });

  const response = await fetch(`${moodleBaseUrl.replace(/\/$/, '')}/webservice/rest/server.php`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: form.toString(),
  });

  const text = await response.text();
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error(`Moodle API returned non-JSON: ${text}`);
  }

  if (!response.ok) {
    throw new Error(`Moodle API returned HTTP ${response.status}`);
  }

  if (parsed && parsed.exception) {
    log('moodle_ws_call_error', {
      wsfunction,
      message: parsed.message || parsed.exception,
    });
    throw new Error(parsed.message || parsed.exception);
  }

  log('moodle_ws_call_complete', {
    wsfunction,
    statusCode: response.status,
  });

  return parsed;
};

const generateSpec = async (brief) => {
  const { openAiApiKey } = await getResolvedOpenAiConfig();
  if (!openAiApiKey) {
    throw new Error('No OpenAI API key available');
  }

  const client = new OpenAI({
    apiKey: openAiApiKey,
  });

  log('openai_generation_start', {
    briefLength: String(brief || '').length,
  });

  let lastError;
  for (let attempt = 1; attempt <= MAX_GENERATION_ATTEMPTS; attempt++) {
    const response = await client.responses.create({
      model: process.env.OPENAI_MODEL,
      input: buildPrompt(brief, attempt > 1 && lastError ? lastError.message : ''),
      text: {
        format: {
          type: 'json_schema',
          name: courseFactorySchema.name,
          strict: true,
          schema: courseFactorySchema.schema,
        }
      }
    });

    const text = String(response.output_text || '').trim();
    if (!text) {
      lastError = new Error('OpenAI returned an empty response');
      continue;
    }

    try {
      const parsed = validateSpec(JSON.parse(text));
      log('openai_generation_complete', {
        attempt,
        sectionCount: Array.isArray(parsed.sections) ? parsed.sections.length : 0,
        quizQuestionCount: parsed && parsed.quiz && Array.isArray(parsed.quiz.questions) ? parsed.quiz.questions.length : 0,
        title: parsed && parsed.title ? parsed.title : '',
      });
      return parsed;
    } catch (error) {
      lastError = error;
      log('openai_generation_retry', {
        attempt,
        message: error.message,
      });
    }
  }

  throw lastError || new Error('OpenAI generation failed');
};

const buildShortName = (title, requestId = '') => {
  const slug = String(title || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 36);
  const suffix = String(requestId || Date.now())
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '')
    .slice(-10);
  return `ai-${slug || 'course'}-${suffix || Date.now()}`;
};

const buildSectionHtml = (section) => {
  const paragraphs = String(section.content || '')
    .split(/\n+/)
    .map((line) => escapeHtml(line.trim()))
    .filter(Boolean);
  return `<div>${paragraphs.map((line) => `<p>${line}</p>`).join('')}</div>`;
};

const provisionCourse = async (payload, spec) => {
  const { moodleBaseUrl } = await getResolvedMoodleConfig();
  const categoryId = Number(process.env.MOODLE_AI_GENERATED_CATEGORY_ID || 5);
  log('provision_start', {
    requestId: payload.request_id || '',
    title: spec.title,
    categoryId,
    sectionCount: spec.sections.length,
  });
  const createCourseResult = await callMoodle('local_novalxpapi_create_course', {
    fullname: spec.title,
    shortname: buildShortName(spec.title, payload.request_id),
    categoryid: categoryId,
    summary: spec.summary,
  });
  const courseId = Number(createCourseResult);
  log('course_created', {
    requestId: payload.request_id || '',
    courseId,
    title: spec.title,
  });

  const sectionIds = [];
  for (const section of spec.sections) {
    const sectionId = await callMoodle('local_novalxpapi_add_section', {
      courseid: courseId,
      name: section.title,
    });
    sectionIds.push(Number(sectionId));
    log('section_created', {
      requestId: payload.request_id || '',
      courseId,
      sectionId: Number(sectionId),
      sectionTitle: section.title,
    });

    await callMoodle('local_novalxpapi_add_page', {
      courseid: courseId,
      section: Number(sectionId),
      title: section.title,
      content: buildSectionHtml(section),
      visible: 1,
    });
    log('section_page_created', {
      requestId: payload.request_id || '',
      courseId,
      sectionId: Number(sectionId),
      title: section.title,
    });
  }

  const quizSectionId = await callMoodle('local_novalxpapi_add_section', {
    courseid: courseId,
    name: spec.quiz.title,
  });

  const quiz = await callMoodle('local_novalxpapi_create_quiz', {
    courseid: courseId,
    section: Number(quizSectionId),
    quizname: spec.quiz.title,
    intro: '<p>Pass this quiz to complete the course.</p>',
    visible: 1,
    gifttext: toGift(spec),
    sectionname: spec.quiz.title,
  });
  log('quiz_created', {
    requestId: payload.request_id || '',
    courseId,
    quizId: Number(quiz.quizid || 0),
    quizCmId: Number(quiz.cmid || 0),
    questionsParsed: Number(quiz.questionsparsed || 0),
    questionsAdded: Number(quiz.questionsadded || 0),
  });

  const guardrails = await callMoodle('local_novalxpapi_apply_quiz_completion_guardrails', {
    courseid: courseId,
    quizcmid: Number(quiz.cmid || 0),
    quizid: Number(quiz.quizid || 0),
    passmark: Number(process.env.COURSE_PASS_MARK || 80),
    shuffleanswers: 1,
  });
  log('guardrails_applied', {
    requestId: payload.request_id || '',
    courseId,
    quizId: Number(quiz.quizid || 0),
    quizCmId: Number(quiz.cmid || 0),
    guardrailsReady: Boolean(guardrails.guardrailsready || false),
  });

  return {
    courseid: courseId,
    coursetitle: spec.title,
    courseurl: `${moodleBaseUrl.replace(/\/$/, '')}/course/view.php?id=${courseId}`,
    quizcmid: Number(quiz.cmid || 0),
    quizid: Number(quiz.quizid || 0),
    guardrailsready: Boolean(guardrails.guardrailsready || false),
    sectionids: sectionIds.concat([Number(quizSectionId)]),
    requestid: payload.request_id || '',
    category: process.env.MOODLE_AI_GENERATED_CATEGORY_NAME || 'AI-Generated',
  };
};

const updateJob = async (payload, state, details = {}) => {
  if (!payload || !payload.request_id) {
    return;
  }

  await callMoodle('local_novalxpcoursefactory_update_job', {
    requestid: payload.request_id,
    state,
    message: details.message || '',
    courseid: details.courseid || 0,
    coursetitle: details.coursetitle || '',
    courseurl: details.courseurl || '',
  });
};

export const handler = async (event) => {
  let payload = null;
  try {
    validateEnv();
    payload = parseBody(event);
    const requestId = payload && payload.request_id ? payload.request_id : '';

    log('request_start', {
      requestId,
      tenantId: payload && payload.tenant_id ? payload.tenant_id : '',
      userId: payload && payload.user && payload.user.id ? payload.user.id : '',
    });

    if (!payload || typeof payload.query?.course_brief !== 'string' || payload.query.course_brief.trim() === '') {
      return isHttpEvent(event)
        ? json(400, { status: false, message: 'Missing course brief' })
        : { status: false, message: 'Missing course brief' };
    }

    await updateJob(payload, 'processing', {
      message: 'Your course request is being processed.',
    });

    const spec = await generateSpec(payload.query.course_brief);
    const provisioned = await provisionCourse(payload, spec);

    const success = {
      status: true,
      requestid: provisioned.requestid,
      courseid: provisioned.courseid,
      coursetitle: provisioned.coursetitle,
      courseurl: provisioned.courseurl,
      category: provisioned.category,
      quizid: provisioned.quizid,
      quizcmid: provisioned.quizcmid,
      guardrailsready: provisioned.guardrailsready,
      generatedcourse: spec,
      message: `Generated ${spec.sections.length} sections and ${spec.quiz.questions.length} quiz questions.`,
    };

    log('request_complete', {
      requestId,
      courseId: provisioned.courseid,
      quizId: provisioned.quizid,
      guardrailsReady: provisioned.guardrailsready,
    });

    await updateJob(payload, 'complete', {
      message: success.message,
      courseid: provisioned.courseid,
      coursetitle: provisioned.coursetitle,
      courseurl: provisioned.courseurl,
    });

    return isHttpEvent(event) ? json(200, success) : success;
  } catch (error) {
    log('request_error', {
      message: error && error.message ? error.message : 'Internal server error',
      stack: error && error.stack ? error.stack : '',
    });
    try {
      await updateJob(payload, 'failed', {
        message: error && error.message ? error.message : 'Internal server error',
      });
    } catch (callbackError) {
      log('job_update_error', {
        message: callbackError && callbackError.message ? callbackError.message : 'Unknown job update failure',
      });
    }
    return isHttpEvent(event)
      ? json(500, { status: false, message: error && error.message ? error.message : 'Internal server error' })
      : { status: false, message: error && error.message ? error.message : 'Internal server error' };
  }
};
