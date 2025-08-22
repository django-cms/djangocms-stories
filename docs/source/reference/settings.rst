########
Settings
########

Configuration options for djangocms-stories.

All settings are optional and have sensible defaults.

Core Settings
=============

.. automodule:: djangocms_stories.settings
   :members:
   :undoc-members:

App Configuration
=================

Settings that can be configured per Stories app configuration:

**STORIES_PAGINATE_BY**
  Number of stories to show per page in list views.

  Default: ``10``

**STORIES_USE_ABSTRACT**
  Enable/disable abstract field for stories.

  Default: ``True``

**STORIES_USE_TAGS**
  Enable/disable tagging functionality.

  Default: ``True``

**STORIES_USE_CATEGORIES**
  Enable/disable category functionality.

  Default: ``True``

**STORIES_USE_RELATED**
  Enable/disable related posts functionality.

  Default: ``True``

Template Settings
=================

**STORIES_TEMPLATE_PREFIX**
  Prefix for template names, allows custom template sets.

  Default: ``'djangocms_stories'``

**STORIES_DETAIL_TEMPLATE**
  Template name for story detail view.

  Default: ``'djangocms_stories/post_detail.html'``

**STORIES_LIST_TEMPLATE**
  Template name for story list view.

  Default: ``'djangocms_stories/post_list.html'``

SEO Settings
============

**STORIES_META_DESCRIPTION_LENGTH**
  Maximum length for auto-generated meta descriptions.

  Default: ``155``

**STORIES_META_TITLE_LENGTH**
  Maximum length for auto-generated meta titles.

  Default: ``60``

**STORIES_SITEMAP_CHANGEFREQ**
  Change frequency for sitemap entries.

  Default: ``'weekly'``

**STORIES_SITEMAP_PRIORITY**
  Priority for sitemap entries.

  Default: ``0.5``

Feed Settings
=============

**STORIES_FEED_LATEST_ITEMS**
  Number of items in RSS feeds.

  Default: ``20``

**STORIES_FEED_CACHE_TIMEOUT**
  Cache timeout for RSS feeds in seconds.

  Default: ``3600`` (1 hour)

Performance Settings
====================

**STORIES_CACHE_TIMEOUT**
  Default cache timeout for story content.

  Default: ``3600`` (1 hour)

**STORIES_MENU_CACHE_TIMEOUT**
  Cache timeout for menu generation.

  Default: ``3600`` (1 hour)

**STORIES_RELATED_POSTS_COUNT**
  Number of related posts to show.

  Default: ``3``

Advanced Settings
=================

**STORIES_WORKFLOW_ENABLED**
  Enable advanced editorial workflow features.

  Default: ``False``

**STORIES_VERSIONING_ENABLED**
  Enable content versioning (requires django-cms versioning).

  Default: ``True``

**STORIES_SEARCH_ENABLED**
  Enable full-text search functionality.

  Default: ``False``

**STORIES_COMMENTS_ENABLED**
  Enable comment functionality (requires django-contrib-comments).

  Default: ``False``

Example Configuration
=====================

Complete settings example::

    # djangocms-stories settings
    STORIES_PAGINATE_BY = 12
    STORIES_USE_ABSTRACT = True
    STORIES_USE_TAGS = True
    STORIES_USE_CATEGORIES = True
    STORIES_USE_RELATED = True

    # Template customization
    STORIES_TEMPLATE_PREFIX = 'my_stories'

    # SEO optimization
    STORIES_META_DESCRIPTION_LENGTH = 160
    STORIES_SITEMAP_CHANGEFREQ = 'daily'
    STORIES_SITEMAP_PRIORITY = 0.8

    # Performance tuning
    STORIES_CACHE_TIMEOUT = 7200  # 2 hours
    STORIES_FEED_CACHE_TIMEOUT = 1800  # 30 minutes

    # Advanced features
    STORIES_WORKFLOW_ENABLED = True
    STORIES_SEARCH_ENABLED = True
