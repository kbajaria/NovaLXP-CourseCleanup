<?php
defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage(
        'local_novalxpcoursefactory',
        get_string('pluginname', 'local_novalxpcoursefactory')
    );

    $settings->add(new admin_setting_heading(
        'local_novalxpcoursefactory/settingsheading',
        get_string('settingsheading', 'local_novalxpcoursefactory'),
        ''
    ));

    $settings->add(new admin_setting_configcheckbox(
        'local_novalxpcoursefactory/enabled',
        get_string('enabled', 'local_novalxpcoursefactory'),
        get_string('enabled_desc', 'local_novalxpcoursefactory'),
        1
    ));

    $settings->add(new admin_setting_configtext(
        'local_novalxpcoursefactory/lambdafunctionname',
        get_string('lambdafunctionname', 'local_novalxpcoursefactory'),
        get_string('lambdafunctionname_desc', 'local_novalxpcoursefactory'),
        'novalxp-course-factory-dev',
        PARAM_TEXT
    ));

    $settings->add(new admin_setting_configtext(
        'local_novalxpcoursefactory/lambdaregion',
        get_string('lambdaregion', 'local_novalxpcoursefactory'),
        get_string('lambdaregion_desc', 'local_novalxpcoursefactory'),
        'eu-west-2',
        PARAM_TEXT
    ));

    $settings->add(new admin_setting_configtext(
        'local_novalxpcoursefactory/requesttimeout',
        get_string('requesttimeout', 'local_novalxpcoursefactory'),
        get_string('requesttimeout_desc', 'local_novalxpcoursefactory'),
        60,
        PARAM_INT
    ));

    $settings->add(new admin_setting_configtext(
        'local_novalxpcoursefactory/placeholdertext',
        get_string('placeholdertext', 'local_novalxpcoursefactory'),
        get_string('placeholdertext_desc', 'local_novalxpcoursefactory'),
        get_string('placeholderdefault', 'local_novalxpcoursefactory'),
        PARAM_TEXT
    ));

    $settings->add(new admin_setting_configtext(
        'local_novalxpcoursefactory/buttontext',
        get_string('buttontext', 'local_novalxpcoursefactory'),
        get_string('buttontext_desc', 'local_novalxpcoursefactory'),
        get_string('buttondefault', 'local_novalxpcoursefactory'),
        PARAM_TEXT
    ));

    $ADMIN->add('localplugins', $settings);
}
