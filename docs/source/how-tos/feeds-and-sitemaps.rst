##############################
How to set up feeds and sitemaps
##############################

djangocms-stories provides RSS/Atom feeds and XML sitemaps for better content distribution and SEO.

RSS Feeds Setup
===============

Enable RSS feeds in your URL configuration::

    # urls.py
    from djangocms_stories.feeds import LatestPostsFeed, TaggedPostsFeed, CategoryPostsFeed

    urlpatterns = [
        # ... other URLs
        path('stories/', include('djangocms_stories.urls')),

        # RSS feeds
        path('feed/latest/', LatestPostsFeed(), name='stories-latest-feed'),
        path('feed/category/<slug:category>/', CategoryPostsFeed(), name='stories-category-feed'),
        path('feed/tag/<slug:tag>/', TaggedPostsFeed(), name='stories-tag-feed'),
    ]

Custom Feed Configuration
=========================

Customize feed content by subclassing the feed classes::

    # feeds.py
    from djangocms_stories.feeds import LatestPostsFeed

    class CustomPostsFeed(LatestPostsFeed):
        title = "My Custom Stories Feed"
        description = "Latest stories from my website"

        def items(self):
            return super().items()[:10]  # Limit to 10 items

        def item_description(self, item):
            return item.abstract or item.title

Feed Discovery
==============

Add feed discovery to your templates::

    {% load stories_tags %}

    <head>
        {% get_feed_url as feed_url %}
        <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="{{ feed_url }}">
    </head>

Sitemaps Configuration
======================

Enable sitemaps for better SEO::

    # urls.py
    from django.contrib.sitemaps.views import sitemap
    from djangocms_stories.sitemaps import StoriesSitemap, CategoriesSitemap

    sitemaps = {
        'stories': StoriesSitemap,
        'categories': CategoriesSitemap,
    }

    urlpatterns = [
        # ... other URLs
        path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    ]

Custom Sitemap Options
======================

Customize sitemap behavior::

    # sitemaps.py
    from djangocms_stories.sitemaps import StoriesSitemap

    class CustomStoriesSitemap(StoriesSitemap):
        changefreq = "weekly"
        priority = 0.8

        def items(self):
            # Only include published stories from last year
            from datetime import datetime, timedelta
            last_year = datetime.now() - timedelta(days=365)
            return super().items().filter(date_published__gte=last_year)

Multi-language Feeds
====================

For multi-language sites, create language-specific feeds::

    # feeds.py
    from djangocms_stories.feeds import LatestPostsFeed
    from django.utils.translation import get_language

    class LanguagePostsFeed(LatestPostsFeed):
        def get_object(self, request):
            return get_language()

        def items(self, language):
            from djangocms_stories.models import Post
            return Post.objects.published().language(language)

Feed Templates
==============

Customize feed templates by creating::

    templates/
        feeds/
            stories_title.html
            stories_description.html
            stories_item_title.html
            stories_item_description.html

Example ``stories_item_description.html``::

    {{ obj.abstract|default:obj.title|striptags|safe }}

Adding Feed Links to Templates
===============================

Add feed links to your story templates::

    {% load stories_tags %}

    <div class="feed-links">
        <a href="{% url 'stories-latest-feed' %}">
            <i class="icon-rss"></i> Subscribe to RSS
        </a>

        {% if category %}
            <a href="{% url 'stories-category-feed' category=category.slug %}">
                <i class="icon-rss"></i> {{ category.name }} RSS
            </a>
        {% endif %}
    </div>

Podcast Feeds
=============

For audio content, create podcast feeds::

    # feeds.py
    from djangocms_stories.feeds import LatestPostsFeed

    class PodcastFeed(LatestPostsFeed):
        feed_type = 'application/rss+xml'
        title = "My Podcast"
        description = "Audio stories and episodes"

        def items(self):
            # Only posts with audio content
            return super().items().filter(content__cmsplugin__plugin_type='AudioPlugin')

        def item_enclosure_url(self, item):
            # Return audio file URL
            audio_plugin = item.content.cmsplugin_set.filter(plugin_type='AudioPlugin').first()
            if audio_plugin:
                return audio_plugin.get_plugin_instance()[0].audio_file.url
            return None

Search Engine Submission
=========================

Submit your sitemap to search engines:

1. **Google Search Console**
   - Add your sitemap URL: ``https://yoursite.com/sitemap.xml``

2. **Bing Webmaster Tools**
   - Submit sitemap in the Sitemaps section

3. **robots.txt**
   Add sitemap location::

    User-agent: *
    Allow: /

    Sitemap: https://yoursite.com/sitemap.xml

Monitoring and Analytics
========================

Track feed usage:

1. **Server logs** - Monitor feed URL access
2. **Analytics** - Track feed subscriber behavior
3. **Feed validation** - Use tools like W3C Feed Validator
4. **Performance** - Monitor feed generation time

Feed Caching
============

Improve performance with caching::

    # settings.py
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
        }
    }

    # Cache feeds for 1 hour
    STORIES_FEED_CACHE_TIMEOUT = 3600
