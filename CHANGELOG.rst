=========
Changelog
=========

0.7.5 (2025-12-03)
------------------

* fix: Stories config form instead of current values always presented initial values
* fix: Migration from djangocms-blog version 2.0.1 or later by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/41
* fix: Adjust quote chars for sql statements to db vendor by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/42
* fix: Menus failed on 404 pages by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/49
* fix: Features post plugin stayed empty by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/50
* fix: Authors plugin did throw an exception by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/51
* fix: feeds raised exceptions by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/52
* fix: Allow for request-based site detection by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/56
* fix: Metadata for PostContent by @wfehr in https://github.com/django-cms/djangocms-stories/pull/48
* fix: Only initialize config form, if new configs are created by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/58
* fix: Archive plugin by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/61
* fix: Category admin form sometimes did not initialize correctly by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/62
* fix: 2-stage blog add form by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/63
* chore: Add tests for template tags by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/53
* chore: Improve coverage by adding admin and model tests by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/57
* chore: Prepare release 0.7.5 by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/59


**Full Changelog**: https://github.com/django-cms/djangocms-stories/compare/0.7.3...0.7.5
0.7.4 (2025-09-17)
------------------

* fix: Adjust quote chars for sql statements to db vendor in migration from djangocms-blog by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/42
* fix: Migration from version 2.0.1 or later by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/41


0.7.3 (2025-09-09)
------------------

* fix: Toolbar failed on non-post content toolbar objects by @corentinbettiol in https://github.com/django-cms/djangocms-stories/pull/38

**New Contributors**

* @corentinbettiol made their first contribution in https://github.com/django-cms/djangocms-stories/pull/38


0.7.2 (2025-09-04)
------------------

* fix: Adding a new stories config raised a server error

0.7.1 (2025-08-28)
------------------

* fix: Migrate navigation extenders by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/19
* fix: Filter lookup allowed must not require request argument for Django 4.2 by @fsbraun in https://github.com/django-cms/djangocms-stories/pull/28
* fix missing admin-form dropdowns by @wfehr in https://github.com/django-cms/djangocms-stories/pull/23

0.7.0 (2025-08-08)
------------------

**Fixed**

* Migration of app hook config
* No migrations due to app config defaults
* Avoid custom settings to trigger migrations

**Changed**

* Updated README
* Naming of settings to start with `STORIES_*` instead of `BLOG_*`

**Added**

* Additional tests for improved coverage

0.6.2 (2025-07-18)
------------------

**Added**

* Menu tests for better test coverage

**Fixed**

* Migration of related posts failed
* Added urlpattern stub for djangocms_blog
* Catch programming error on postgres

**Changed**

* Updated README.rst

0.6.1 (2025-07-01)
------------------

**Fixed**

* Lazy cms_wizards implementation

0.6.0 (2025-07-01)
------------------

**Added**

* Added back wizards (new style)

**Changed**

* Moved from hatchling to setuptools build system
* Cleaned up configuration

0.5.0 (2025-06-27)
------------------

**Added**

* Initial stable feature set
* Basic blog functionality for django CMS 4+
* Post and category management
* Multi-language support with django-parler
* Template system
* RSS feeds
* SEO optimization with django-meta
* Tagging support with django-taggit
* Versioning tests
* Migration tests
