<?php
defined('MOODLE_INTERNAL') || die();

$functions = [
    'local_novalxpcoursefactory_create_course' => [
        'classname' => 'local_novalxpcoursefactory\\external\\create_course',
        'methodname' => 'execute',
        'description' => 'Create an AI-generated Moodle course from a learner brief.',
        'type' => 'write',
        'capabilities' => '',
        'ajax' => true,
    ],
    'local_novalxpcoursefactory_update_job' => [
        'classname' => 'local_novalxpcoursefactory\\external\\update_job',
        'methodname' => 'execute',
        'description' => 'Update async AI course factory job state from Lambda.',
        'type' => 'write',
        'capabilities' => '',
        'ajax' => false,
    ],
];
