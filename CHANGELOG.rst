=========
Changelog
=========

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
