.. _settings_reference:

########
Settings
########

Configuration options for djangocms-stories.

All settings are optional and have sensible defaults. Settings use the ``STORIES_`` prefix.
For backwards compatibility with djangocms-blog, ``BLOG_`` prefixed settings are also accepted as
fallbacks.

Django Settings
===============

.. automodule:: djangocms_stories.settings
   :members:
   :undoc-members:

Per-Apphook Configuration
=========================

Many settings can be overridden per apphook instance via the ``StoriesConfig`` model
in the Django admin. These include:

- Permalink structure
- Placeholder vs. rich text content
- Abstract field usage
- Related posts
- Default author
- Pagination
- Template prefix
- Menu structure
- Sitemap changefreq and priority
- Social meta defaults (Open Graph, Twitter, Schema.org)

.. autoclass:: djangocms_stories.cms_appconfig.StoriesConfig
   :members:
   :undoc-members:
   :no-index:

Example Configuration
=====================

::

    # djangocms-stories settings
    STORIES_PAGINATION = 20
    STORIES_USE_ABSTRACT = True
    STORIES_USE_PLACEHOLDER = True
    STORIES_USE_RELATED = True
    STORIES_ALLOW_UNICODE_SLUGS = True

    # SEO optimization
    STORIES_META_DESCRIPTION_LENGTH = 320
    STORIES_META_TITLE_LENGTH = 70

    # Feed settings
    STORIES_FEED_CACHE_TIMEOUT = 3600
    STORIES_FEED_LATEST_ITEMS = 10
    STORIES_FEED_TAGS_ITEMS = 10

    # Plugin templates
    STORIES_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default template')),
    )

    # Versioning (requires djangocms-versioning)
    STORIES_VERSIONING_ENABLED = True
