.. _migration_from_blog:

##################################
How to migrate from djangocms-blog
##################################

This guide helps you migrate from djangocms-blog to djangocms-stories.

Pre-migration Checklist
========================

Before starting the migration:

1. **Backup your database** - Create a full backup
2. **Document customizations** - Note any custom templates, fields, or modifications
3. **Test environment** - Perform migration in a staging environment first
4. **Dependencies** - Check for other packages that depend on djangocms-blog

Installation Steps
==================

1. Uninstall djangocms-blog::

    pip uninstall djangocms-blog

2. Install djangocms-stories::

    pip install djangocms-stories

3. Add to INSTALLED_APPS (keep djangocms_blog for now)::

    INSTALLED_APPS = [
        # ... other apps
        'djangocms_blog',  # Keep temporarily
        'djangocms_stories',  # Add new
        # ... dependencies
    ]

4. Migrate data by running migrations::

    python manage.py migrate djangocms_blog
    python manage.py migrate djangocms_stories

   .. warning::

        The migration process will move existing data from djangocms-blog's
        database table to the new djangocms-stories tables **and delete the old tables**.
        Be sure to have made a backup.

5. Remove djangocms_blog from INSTALLED_APPS::

    INSTALLED_APPS = [
        # ... other apps
        'djangocms_stories',  # Keep new
        # ... dependencies
    ]

Template Migration
==================

Update your templates to use the new namespace:

1. Rename template directories::

    mv templates/djangocms_blog templates/djangocms_stories

2. Update template tags in templates::

    # Old
    {% load blog_tags %}

    # New
    {% load stories_tags %}

3. Update URL names::

    # Old
    {% url 'djangocms_blog:post-detail' slug=post.slug %}

    # New
    {% url 'djangocms_stories:post-detail' slug=post.slug %}

Settings Migration
==================

Update your Django settings::

    # Replace blog settings with stories equivalents

    # Old
    BLOG_PAGINATE_BY = 10
    BLOG_USE_ABSTRACT = True

    # New
    STORIES_PAGINATE_BY = 10
    STORIES_USE_ABSTRACT = True

URL Configuration
=================

Normally, URL configurations are migrated automatically. Only if you
manage your blog / stories URLs manually, update your URL patterns::

    # Old
    path('blog/', include('djangocms_blog.urls')),

    # New
    path('blog/', include('djangocms_stories.urls')),

Post-migration Steps
====================

1. **Test thoroughly** - Verify all functionality works
2. **Update internal links** - Update any hardcoded URLs
3. **Clean up** - Remove old templates and unused code

Troubleshooting
===============


.. note::
    Community help is available on our
    `Discord server <https://www.django-cms.org/discord>`_.

Common issues and solutions:

**Missing templates**
    Copy and rename your blog templates to stories

**Broken URLs**
    Update all URL references and set up redirects

**Custom fields**
    Recreate custom fields in the new models

**Permissions**
    Review and update user permissions for the new app

