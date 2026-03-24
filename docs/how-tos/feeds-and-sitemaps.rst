################################
How to set up feeds and sitemaps
################################

Good content deserves to be found. djangocms-stories ships with RSS feeds and integrates with
Django's sitemap framework so search engines and feed readers can discover your posts
automatically.

RSS feeds
=========

Feeds are included in the default URL configuration and start working as soon as you attach
the apphook to a page. Three feed endpoints are available out of the box:

- ``feed/`` — the latest entries across all categories (``LatestEntriesFeed``)
- ``feed/fb/`` — a Facebook Instant Articles feed (``FBInstantArticles``)
- ``tag/<slug>/feed/`` — a per-tag feed so readers can subscribe to specific topics (``TagFeed``)

No extra URL wiring is needed if you use the standard apphook setup. The feeds respect the
``STORIES_FEED_LATEST_ITEMS``, ``STORIES_FEED_TAGS_ITEMS``, and ``STORIES_FEED_INSTANT_ITEMS``
settings to control how many items appear.

Helping browsers discover your feeds
--------------------------------------

Add a ``<link>`` tag to your base template so browsers and feed readers can auto-discover the
RSS endpoint:

.. code-block:: html+django

    <head>
        <link rel="alternate" type="application/rss+xml"
              title="RSS Feed"
              href="{% url 'djangocms_stories:posts-latest-feed' %}">
    </head>

Customizing feeds
------------------

If the defaults don't fit, subclass the feed classes. For example, to change the title and
limit items:

.. code-block:: python

    from djangocms_stories.feeds import LatestEntriesFeed

    class CustomFeed(LatestEntriesFeed):
        title = "My Stories"
        description = "Hand-picked stories from our team"

        def items(self):
            return super().items()[:5]

Register the subclass in your own URL configuration alongside — or instead of — the default
feeds.

Feed caching
--------------

Feeds are cached for one hour by default. Adjust ``STORIES_FEED_CACHE_TIMEOUT`` (in seconds) to
change this. On high-traffic sites a longer timeout reduces database load; on sites where
freshness matters, lower it.

Sitemaps
========

Sitemaps tell search engines which pages exist and how often they change. djangocms-stories
provides a ``StoriesSitemap`` that lists every published post in every available language,
together with the ``changefreq`` and ``priority`` values you configure per ``StoriesConfig``.

To enable it, register the sitemap in your project's ``urls.py``:

.. code-block:: python

    from django.contrib.sitemaps.views import sitemap
    from cms.sitemaps import CMSSitemap
    from djangocms_stories.sitemaps import StoriesSitemap

    sitemaps = {
        'cmspages': CMSSitemap,
        'stories': StoriesSitemap,
    }

    urlpatterns = [
        # ... other URLs
        path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
             name='django.contrib.sitemaps.views.sitemap'),
    ]

Once the sitemap is live, add its URL to your ``robots.txt`` so crawlers find it:

.. code-block:: text

    Sitemap: https://yoursite.com/sitemap.xml

You can also submit the URL directly in Google Search Console or Bing Webmaster Tools for
faster indexing.
