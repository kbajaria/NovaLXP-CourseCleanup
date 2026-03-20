<?php
define('CLI_SCRIPT', true);

require '/var/www/moodle/config.php';

set_config('tab3name', 'TalentLMS', 'theme_edutor');
set_config('pane3title', 'Request a TalentLMS course', 'theme_edutor');
set_config(
    'pane3intro',
    '<p>Search the seeded TalentLMS catalog and request any course that still needs to be migrated into NovaLXP.</p>',
    'theme_edutor'
);
set_config('usepane3blocks', 0, 'theme_edutor');

purge_all_caches();

echo "Updated theme_edutor pane 3 fallback copy and label for TalentLMS.\n";
