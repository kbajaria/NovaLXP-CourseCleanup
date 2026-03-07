# Course Factory Deployment Bundle

This folder groups the Moodle-side artifacts that must be applied to a target environment:

- `local_novalxpcoursefactory` from:
  - [/Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory](/Users/kamilabajaria/Projects/NovaLXP-Courses/moodle/local_novalxpcoursefactory)
- `local_novalxpapi` update via:
  - [/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch](/Users/kamilabajaria/Projects/NovaLXP-Courses/patches/local_novalxpapi-course-factory-guardrails.patch)

Target deployment order:

1. update `local_novalxpapi`
2. run Moodle upgrade and purge caches
3. install/update `local_novalxpcoursefactory`
4. run Moodle upgrade and purge caches
5. configure plugin settings in admin
