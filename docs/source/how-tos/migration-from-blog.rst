.. _migration_from_blog:

##################################
How to migrate from djangocms-blog
##################################

djangocms-stories is the successor to djangocms-blog, redesigned for django CMS 4+. The
database migration is automated and covered by tests, but you should still treat it as a
significant change — back up first, migrate in staging, then promote to production.

Before you start
=================

Make a full database backup. The migration will move data from djangocms-blog's tables into
new djangocms-stories tables and then drop the old tables, so there is no going back without a
backup.

Also take note of any customizations you've made: custom templates, admin extensions, model
extensions, or overridden settings. These will need manual attention after the data migration.

If other packages in your project depend on djangocms-blog (custom apps that import its
models, for example), update them first or plan to update them in the same deployment.

Step 1: Install djangocms-stories alongside djangocms-blog
============================================================

Uninstall the old package and install the new one::

    pip uninstall djangocms-blog
    pip install djangocms-stories

Then add ``djangocms_stories`` to ``INSTALLED_APPS`` while keeping ``djangocms_blog`` temporarily:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'djangocms_blog',      # keep for now — the migration reads its tables
        'djangocms_stories',   # new
        # ...
    ]

Step 2: Run the data migration
================================

Run migrations for both apps::

    python manage.py migrate djangocms_blog
    python manage.py migrate djangocms_stories

The djangocms-stories migration ``0002`` reads all existing blog data — posts, categories,
configurations, plugins — copies it into the new tables, and drops the old djangocms-blog
tables.

.. warning::

    This is a one-way operation. The old tables are deleted. Make sure your backup is in place.

Step 3: Remove djangocms-blog
===============================

Once the migration succeeds, remove ``djangocms_blog`` from ``INSTALLED_APPS``. It is no longer
needed.

Step 4: Update templates
=========================

Rename your template directory and update the tag library import:

.. code-block:: bash

    mv templates/djangocms_blog templates/djangocms_stories

Inside your templates, replace the old tag library and URL namespace:

.. code-block:: html+django

    {# Old #}
    {% load blog_tags %}
    {% url 'djangocms_blog:post-detail' slug=post.slug %}

    {# New #}
    {% load djangocms_stories %}
    {% url 'djangocms_stories:post-detail' slug=post.slug %}

The model structure has also changed. In djangocms-blog, ``post`` carried both
language-independent fields (author, dates, images) and translated fields (title, slug,
abstract). In djangocms-stories these are split:

- ``post`` — the ``Post`` object with language-independent data (author, dates, categories, tags,
  images, related posts)
- ``post_content`` — the ``PostContent`` object with per-language fields (title, subtitle, slug,
  abstract, content placeholder, media placeholder) and a ``post`` back-reference

Templates that accessed ``post.title`` should now use ``post_content.title``, and templates that
accessed ``post.date_published`` from a ``PostContent`` context should use
``post_content.post.date_published``.

Step 5: Update settings
========================

All ``BLOG_*`` settings have ``STORIES_*`` equivalents:

.. code-block:: python

    # Old                              # New
    BLOG_PAGINATION = 10               STORIES_PAGINATION = 10
    BLOG_USE_ABSTRACT = True           STORIES_USE_ABSTRACT = True
    BLOG_USE_PLACEHOLDER = True        STORIES_USE_PLACEHOLDER = True
    BLOG_PERMALINK_URLS = {...}        STORIES_PERMALINK_URLS = {...}
    BLOG_URLCONF = '...'               STORIES_URLCONF = '...'
    BLOG_MULTISITE = True              STORIES_MULTISITE = True

.. note::

    For backwards compatibility, ``BLOG_*`` settings are still read as fallbacks if the
    corresponding ``STORIES_*`` setting is not defined. Rename them anyway to keep your
    settings file clear.

Step 6: Update manual URL configuration (if any)
==================================================

If you manage story URLs outside the apphook (unusual, but possible), update the import:

.. code-block:: python

    # Old
    path('blog/', include('djangocms_blog.urls')),

    # New
    path('blog/', include('djangocms_stories.urls')),

Apphook-managed URLs are migrated automatically — no action needed in the common case.

After the migration
====================

Walk through the site and verify that post detail pages, category pages, tag pages, feeds,
and the admin all work as expected. Check the apphook assignments in the CMS page settings to
confirm they point to the new ``Stories`` application.

If something looks wrong, the most common causes are:

**Missing or broken templates**
    Make sure you renamed the template directory and updated all ``{% load %}`` tags.

**Broken URLs or 404s**
    Check that URL names use the ``djangocms_stories:`` namespace and that any hardcoded paths
    have been updated.

**Missing custom fields**
    If you extended the old ``Post`` model with custom inlines or fields, recreate them against
    the new models and re-register them with ``djangocms_stories.admin.register_extension()``.

.. note::

    Community help is available on the
    `django CMS Discord server <https://www.django-cms.org/discord>`_.
