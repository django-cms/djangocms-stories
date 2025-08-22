########################
How to optimize for SEO
########################

djangocms-stories includes built-in SEO features through django-meta integration.

Meta Tags Configuration
=======================

Stories automatically generate meta tags for:

- Title tags
- Meta descriptions
- Open Graph tags
- Twitter Cards
- Canonical URLs

Customizing Meta Data
=====================

Override meta data in your story model::

    class MyStoryConfig(StoriesConfig):
        def get_meta_description(self, post):
            return post.abstract or f"Read {post.title} on our blog"

        def get_meta_image(self, post):
            return post.main_image

Template Integration
====================

Add meta tags to your base template::

    {% load meta_tags %}

    <head>
        {% include "meta/meta.html" %}
    </head>

Structured Data
===============

Add structured data for better search engine understanding::

    {% block extra_head %}
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": "{{ post.title }}",
            "author": {
                "@type": "Person",
                "name": "{{ post.author.get_full_name }}"
            },
            "datePublished": "{{ post.date_published|date:'c' }}",
            "dateModified": "{{ post.date_modified|date:'c' }}",
            "description": "{{ post.abstract }}",
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": "{{ request.build_absolute_uri }}"
            }
        }
        </script>
    {% endblock %}

URL Optimization
================

Configure SEO-friendly URLs in your app config:

1. Use descriptive slugs
2. Include publication date in URLs (optional)
3. Set up proper redirects for changed URLs

Sitemap Integration
===================

Enable sitemaps in your main ``urls.py``::

    from djangocms_stories.sitemaps import StoriesSitemap
    from django.contrib.sitemaps.views import sitemap

    sitemaps = {
        'stories': StoriesSitemap,
    }

    urlpatterns = [
        path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    ]

Performance Optimization
========================

Optimize for better Core Web Vitals:

1. Enable image optimization with easy-thumbnails
2. Use lazy loading for images
3. Minimize template complexity
4. Enable caching for story lists

Content Guidelines
==================

For better SEO performance:

- Write descriptive titles (50-60 characters)
- Create compelling meta descriptions (150-160 characters)
- Use heading tags (H1, H2, H3) properly
- Include relevant keywords naturally
- Write quality content with good readability
