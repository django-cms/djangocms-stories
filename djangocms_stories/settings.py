"""
List of settings that can be set in project django settings.
"""

from django.utils.translation import gettext_lazy as _
from meta import settings as meta_settings

MENU_TYPE_COMPLETE = "complete"
MENU_TYPE_CATEGORIES = "categories"
MENU_TYPE_POSTS = "posts"
MENU_TYPE_NONE = "none"
DATE_FORMAT = "%a %d %b %Y %H:%M"

PERMALINK_TYPE_FULL_DATE = "full_date"
PERMALINK_TYPE_SHORT_DATE = "short_date"
PERMALINK_TYPE_CATEGORY = "category"
PERMALINK_TYPE_SLUG = "slug"

STORIES_VERSIONING_ENABLED = True
"""
.. _VERSIONING_ENABLED:

Enable versioning for stories (defaults to True) - only effective if djangocms-versioning is installed.
"""

PERMALINKS = (  # noqa
    (PERMALINK_TYPE_FULL_DATE, _("Full date")),
    (PERMALINK_TYPE_SHORT_DATE, _("Year /  Month")),
    (PERMALINK_TYPE_CATEGORY, _("Category")),
    (PERMALINK_TYPE_SLUG, _("Just slug")),
)
"""
.. _PERMALINKS:

Permalinks styles.
"""

STORIES_UNICODE_SLUGS = True
"""
.. _UNICODE_SLUGS:

Allow unicode chars in auto-generated slugs.
"""


PERMALINKS_URLS = {  # noqa
    PERMALINK_TYPE_FULL_DATE: "<int:year>/<int:month>/<int:day>/<str:slug>/",
    PERMALINK_TYPE_SHORT_DATE: "<int:year>/<int:month>/<str:slug>/",
    PERMALINK_TYPE_CATEGORY: "<str:category>/<str:slug>/",
    PERMALINK_TYPE_SLUG: "<str:slug>/",
}

"""
.. _PERMALINKS_URLS:

Permalinks urlconfs.
"""

MENU_TYPES = (  # noqa
    (MENU_TYPE_COMPLETE, _("Categories and posts")),
    (MENU_TYPE_CATEGORIES, _("Categories only")),
    (MENU_TYPE_POSTS, _("Posts only")),
    (MENU_TYPE_NONE, _("None")),
)
"""
.. _DEFAULT_MENU_TYPES:

Types of menu structure.
"""

SITEMAP_CHANGEFREQ_LIST = (  # noqa
    ("always", _("always")),
    ("hourly", _("hourly")),
    ("daily", _("daily")),
    ("weekly", _("weekly")),
    ("monthly", _("monthly")),
    ("yearly", _("yearly")),
    ("never", _("never")),
)
"""
.. _SITEMAP_CHANGEFREQ_LIST:

List of changefreqs defined in sitemaps.
"""

STORIES_IMAGE_THUMBNAIL_SIZE = {"size": "120x120", "crop": True, "upscale": False}
"""
.. _IMAGE_THUMBNAIL_SIZE:

Easy-thumbnail alias configuration for the post main image when shown on the post lists;
it's a dictionary with ``size``, ``crop`` and ``upscale`` keys.
"""

STORIES_IMAGE_FULL_SIZE = {"size": "640x360", "crop": True, "upscale": False}
"""
.. _IMAGE_FULL_SIZE:

Easy-thumbnail alias configuration for the post main image when shown on the post detail;
it's a dictionary with ``size``, ``crop`` and ``upscale`` keys.
"""

STORIES_META_IMAGE_SIZE = None
"""
.. _META_IMAGE_SIZE:

Easy-thumbnail alias configuration for the post meta image;
it's a dictionary with ``size``, ``crop`` and ``upscale`` keys.
Recommended values are {"size": (1200, 630), "crop": True, "upscale": False}
"""

STORIES_URLCONF = "djangocms_stories.urls"
"""
.. _URLCONF:

Standard Apphook URLConf.
"""

STORIES_PAGINATION = 20
"""
.. _PAGINATION:

Number of post per page.
"""

STORIES_LATEST_POSTS = 5
"""
.. _LATEST_POSTS:

Default number of post in the **Latest post** plugin.
"""

STORIES_POSTS_LIST_TRUNCWORDS_COUNT = 100
"""
.. _POSTS_LIST_TRUNCWORDS_COUNT:

Default number of words shown for abstract in the post list.
"""

STORIES_ALLOW_UNICODE_SLUGS = True
"""
.. _ALLOW_UNICODE_SLUGS:

Typically slugs can contain unicode characters. Set to False to only allow ASCII-based slugs.
"""

STORIES_META_DESCRIPTION_LENGTH = 320
"""
.. _META_DESCRIPTION_LENGTH:

Maximum length for the Meta description field.
"""

STORIES_META_TITLE_LENGTH = 70
"""
.. _META_TITLE_LENGTH:

Maximum length for the Meta title field.
"""

STORIES_MENU_TYPES = MENU_TYPES
"""
.. _MENU_TYPES:

List of available menu types.
"""

STORIES_MENU_EMPTY_CATEGORIES = True
"""
.. _MENU_EMPTY_CATEGORIES:

Flag to show / hide categories without posts attached from the menu.
"""

STORIES_TYPE = "Article"
"""
.. _TYPE:

Generic type for the post object.
"""

STORIES_TYPES = meta_settings.OBJECT_TYPES
"""
.. _TYPES:

Choices of available blog types.

Available values are defined in to ``META_OBJECT_TYPES`` defined in `django-meta settings`_.
"""

STORIES_FB_TYPE = "Article"
"""
.. _FB_TYPE:

Open Graph type for the post object.
"""

STORIES_FB_TYPES = meta_settings.FB_TYPES
"""
.. _FB_TYPES:

Choices of available blog types.

Available values are defined in to ``META_FB_TYPES`` defined in `django-meta settings`_.
"""

STORIES_FB_APPID = meta_settings.get_setting("FB_APPID")
"""
.. _FB_APPID:

Facebook Application ID.

Default from ``FB_APPID`` defined in `django-meta settings`_.
"""

STORIES_FB_PROFILE_ID = meta_settings.get_setting("FB_PROFILE_ID")
"""
.. _FB_PROFILE_ID:

Facebook profile ID of the post author.

Default from ``FB_PROFILE_ID`` defined in `django-meta settings`_.
"""

STORIES_FB_PUBLISHER = meta_settings.get_setting("FB_PUBLISHER")
"""
.. _FB_PUBLISHER:

Facebook URL of the blog publisher.

Default from ``FB_PUBLISHER`` defined in `django-meta settings`_.
"""

STORIES_FB_AUTHOR_URL = "get_author_url"
"""
.. _FB_AUTHOR_URL:

Facebook profile URL of the post author.
"""

STORIES_FB_AUTHOR = "get_author_name"
"""
.. _FB_AUTHOR:

Facebook profile URL of the post author.
"""

STORIES_TWITTER_TYPE = "summary"
"""
.. _TWITTER_TYPE:

Twitter Card type for the post object.
"""

STORIES_TWITTER_TYPES = meta_settings.TWITTER_TYPES
"""
.. _TWITTER_TYPES:

Choices of available blog types for twitter.

Default from ``TWITTER_TYPES`` defined in `django-meta settings`_.
"""

STORIES_TWITTER_SITE = meta_settings.get_setting("TWITTER_SITE")
"""
.. _TWITTER_SITE:

Twitter account of the site.

Default from ``TWITTER_SITE`` defined in `django-meta settings`_.
"""

STORIES_TWITTER_AUTHOR = "get_author_twitter"
"""
.. _TWITTER_AUTHOR:

Twitter account of the post author.
"""

STORIES_SCHEMAORG_TYPE = "Blog"
"""
.. _SCHEMAORG_TYPE:

Schema.org type for the post object.
"""

STORIES_SCHEMAORG_TYPES = meta_settings.SCHEMAORG_TYPES
"""
.. _SCHEMAORG_TYPES:

Choices of available Schema.org types.

Default from ``SCHEMAORG_TYPES`` defined in `django-meta settings`_.
"""

STORIES_SCHEMAORG_AUTHOR = "get_author_schemaorg"
"""
.. _SCHEMAORG_AUTHOR:

Google+ account of the post author (deprecated).
"""

STORIES_ENABLE_COMMENTS = True
"""
.. _ENABLE_COMMENTS:

Whether to enable comments by default on posts

While ``djangocms_stories`` does not ship any comment system, this flag
can be used to control the chosen comments framework.
"""

STORIES_USE_ABSTRACT = True
"""
.. _USE_ABSTRACT:

Use an abstract field for the post.

If ``False`` no abstract field is available for posts.
"""

STORIES_USE_PLACEHOLDER = True
"""
.. _USE_PLACEHOLDER:

Post content is managed via placeholder

If ``False`` a HTMLField is provided instead.
"""

STORIES_USE_RELATED = True
"""
.. _USE_RELATED:

Enable related posts to link one post to others.
"""

STORIES_MULTISITE = True
"""
.. _MULTISITE:

Add support for multisite setup.
"""

STORIES_AUTHOR_DEFAULT = True
"""
.. _AUTHOR_DEFAULT:

Use a default if not specified:

* ``True``: the current user is set as the default author;
* ``False``: no default author is set;
* any other string: the user with the provided username is used;
"""

STORIES_ADMIN_POST_FIELDSET_FILTER = False
"""
.. _ADMIN_POST_FIELDSET_FILTER:

Callable function to change (add or filter) fields to fieldsets for admin post edit form.

See :ref:`admin_filter_function` for more details.
"""

STORIES_AVAILABLE_PERMALINK_STYLES = PERMALINKS
"""
.. _AVAILABLE_PERMALINK_STYLES:

Choices of permalinks styles.
"""

STORIES_PERMALINK_URLS = PERMALINKS_URLS
"""
.. _PERMALINK_URLS:

URLConf corresponding to :ref:`STORIES_AVAILABLE_PERMALINK_STYLES <AVAILABLE_PERMALINK_STYLES>`.
"""

STORIES_DEFAULT_OBJECT_NAME = _("Article")
"""
.. _DEFAULT_OBJECT_NAME:

Default label for Blog item (used in django CMS Wizard).
"""

STORIES_AUTO_SETUP = True
"""
.. _AUTO_SETUP:

Enable the blog :ref:`auto_setup` feature.
"""

STORIES_AUTO_HOME_TITLE = "Home"
"""
.. _AUTO_HOME_TITLE:

Title of the home page created by :ref:`auto_setup`.
"""

STORIES_AUTO_BLOG_TITLE = _("Blog")
"""
.. _AUTO_STORIES_TITLE:

Title of the blog page created by :ref:`auto_setup`.
"""

STORIES_AUTO_APP_TITLE = _("Blog")
"""
.. _AUTO_APP_TITLE:

Title of the ``BlogConfig`` instance created by :ref:`auto_setup`.
"""

STORIES_AUTO_NAMESPACE = "blog"
"""
.. _AUTO_NAMESPACE:

Namespace of the ``BlogConfig`` instance created by :ref:`auto_setup`.
"""

STORIES_SITEMAP_PRIORITY_DEFAULT = "0.5"
"""
.. _SITEMAP_PRIORITY_DEFAULT:

Default priority for sitemap items.
"""

STORIES_SITEMAP_CHANGEFREQ = SITEMAP_CHANGEFREQ_LIST
"""
.. _SITEMAP_CHANGEFREQ:

List for available changefreqs for sitemap items.
"""

STORIES_SITEMAP_CHANGEFREQ_DEFAULT = "monthly"
"""
.. _SITEMAP_CHANGEFREQ_DEFAULT:

Default changefreq for sitemap items.
"""

STORIES_ABSTRACT_EDITOR_CONFIG = True
"""
.. _ABSTRACT_EDITOR_CONFIG:

Configuration for the CKEditor of the abstract field.

See https://github.com/divio/djangocms-text-ckeditor/#customizing-htmlfield-editor for details.
"""

STORIES_POST_TEXT_EDITOR_CONFIG = True
"""
.. _POST_TEXT_EDITOR_CONFIG:

Configuration for the CKEditor of the post content field.

See https://github.com/divio/djangocms-text-ckeditor/#customizing-htmlfield-editor for details.
"""

STORIES_ENABLE_SEARCH = True
"""
.. _ENABLE_SEARCH:

Enable ``aldryn-search`` (i.e.: ``django-haystack``) indexes.
"""

STORIES_CURRENT_POST_IDENTIFIER = "djangocms_postcontent_current"
"""
.. _CURRENT_POST_IDENTIFIER:

Current post identifier in request.

Name of the request attribute used in :py:class:`djangocms_stories.cms_toolbars.BlogToolbar` to detect if
request match a post detail.
"""

STORIES_CURRENT_NAMESPACE = "djangocms_post_current_config"
"""
.. _CURRENT_NAMESPACE:

Current post config identifier in request.

Name of the request attribute used in :py:class:`djangocms_stories.cms_toolbars.BlogToolbar` to detect the
current apphook namespace.
"""

STORIES_ENABLE_THROUGH_TOOLBAR_MENU = False
"""
.. _ENABLE_THROUGH_TOOLBAR_MENU:

Show djangocms-blog toolbar in any page, even when outside the blog apphooks.
"""

STORIES_PLUGIN_MODULE_NAME = _("Blog")
"""
.. _PLUGIN_MODULE_NAME:

Name of the djangocms-blog plugins module (group).
"""

STORIES_LATEST_ENTRIES_PLUGIN_NAME = _("Latest Blog Articles")
"""
.. _LATEST_ENTRIES_PLUGIN_NAME:

Name of the plugin showing the list of latest posts.
"""

STORIES_LATEST_ENTRIES_PLUGIN_NAME_CACHED = _("Latest Blog Articles - Cache")
"""
.. _LATEST_ENTRIES_PLUGIN_NAME_CACHED:

Name of the plugin showing the list of latest posts (cached version).
"""

STORIES_AUTHOR_POSTS_PLUGIN_NAME = _("Author Blog Articles")
"""
.. _AUTHOR_POSTS_PLUGIN_NAME:

Name of the plugin showing the list of blog posts authors.
"""

STORIES_AUTHOR_POSTS_LIST_PLUGIN_NAME = _("Author Blog Articles List")
"""
.. _AUTHOR_POSTS_LIST_PLUGIN_NAME:

Name of the plugin showing the list of posts per authors.
"""

STORIES_TAGS_PLUGIN_NAME = _("Tags")
"""
.. _TAGS_PLUGIN_NAME:

Name of the plugin showing the tag blog cloud.
"""

STORIES_CATEGORY_PLUGIN_NAME = _("Categories")
"""
.. _CATEGORY_PLUGIN_NAME:

Name of the plugin showing the list of blog categories.
"""

STORIES_ARCHIVE_PLUGIN_NAME = _("Archive")
"""
.. _ARCHIVE_PLUGIN_NAME:

Name of the plugin showing the blog archive index.
"""

STORIES_FEATURED_POSTS_PLUGIN_NAME = _("Featured Posts")
"""
.. _FEATURED_POSTS_PLUGIN_NAME:

Name of the plugin showing the selected posts.
"""

STORIES_FEATURED_POSTS_PLUGIN_NAME_CACHED = _("Featured Posts - Cache")
"""
.. _FEATURED_POSTS_PLUGIN_NAME_CACHED:

Name of the plugin showing the selected posts (cached version).
"""

STORIES_FEED_CACHE_TIMEOUT = 3600
"""
.. _FEED_CACHE_TIMEOUT:

Cache timeout for RSS feeds.
"""

STORIES_FEED_INSTANT_ITEMS = 50
"""
.. _FEED_INSTANT_ITEMS:

Number of items in Instant Article feed.
"""

STORIES_FEED_LATEST_ITEMS = 10
"""
.. _FEED_LATEST_ITEMS:

Number of items in latest items feed.
"""

STORIES_FEED_TAGS_ITEMS = 10
"""
.. _FEED_TAGS_ITEMS:

Number of items in per tags feed.
"""

STORIES_PLUGIN_TEMPLATE_FOLDERS = (("plugins", _("Default template")),)
"""
.. _PLUGIN_TEMPLATE_FOLDERS:

(Sub-)folder from which the plugin templates are loaded.

The default folder is ``plugins``.

See :ref:`plugin_templates` for more details.
"""

STORIES_USE_FALLBACK_LANGUAGE_IN_URL = False
"""
.. _USE_FALLBACK_LANGUAGE_IN_URL:

When displaying URL, prefer URL in the fallback language if an article or category is not available in the
current language.
"""

STORIES_WIZARD_CONTENT_PLUGIN = "TextPlugin"
"""
.. _WIZARD_CONTENT_PLUGIN:

Name of the plugin created by wizard for the text content.
"""

STORIES_WIZARD_CONTENT_PLUGIN_BODY = "body"
"""
.. _WIZARD_CONTENT_PLUGIN_BODY:

Name of the plugin field to add wizard text.
"""

params = {param: value for param, value in locals().items() if param.startswith("STORIES_")}

"""
.. _django-meta settings: https://github.com/nephila/django-meta#settings
"""


def get_setting(name):
    """Get setting value from django settings with fallback to globals defaults."""
    from django.conf import settings

    return getattr(
        settings,
        f"STORIES_{name}",  # First, look for STORIES_* settings
        getattr(settings, f"BLOG_{name}", params[f"STORIES_{name}"]),  # Fallback to BLOG_* settings, or default
    )
