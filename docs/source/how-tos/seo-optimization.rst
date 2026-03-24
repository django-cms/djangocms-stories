########################
How to optimize for SEO
########################

djangocms-stories integrates with `django-meta <https://github.com/nephila/django-meta>`_ to
generate social and search-engine meta tags automatically. Most of the heavy lifting happens
behind the scenes, but a few configuration steps ensure everything works correctly.

Enabling meta tags
==================

Start by enabling the meta tag protocols you need in your project settings:

.. code-block:: python

    META_SITE_PROTOCOL = 'https'
    META_USE_SITES = True
    META_USE_OG_PROPERTIES = True        # Facebook / Open Graph
    META_USE_TWITTER_PROPERTIES = True   # Twitter Cards
    META_USE_SCHEMAORG_PROPERTIES = True # Schema.org / Google

Then include the meta template in the ``<head>`` of your base template so the tags actually
render:

.. code-block:: html+django

    <head>
        {% include "meta/meta.html" %}
    </head>

With this in place, every story detail page will emit ``<meta>`` tags for the title,
description, Open Graph image, Twitter Card, and canonical URL — all derived from the post's
fields.

See :ref:`meta` for alternative integration approaches, especially if you also use
``djangocms-page-meta``.

Configuring defaults
====================

Default values for Open Graph type, Twitter Card type, and Schema.org type can be set globally
or per ``StoriesConfig``. The global settings act as fallbacks:

.. code-block:: python

    STORIES_FB_TYPE = "Article"
    STORIES_TWITTER_TYPE = "summary"
    STORIES_SCHEMAORG_TYPE = "Blog"

Per-apphook overrides live in the ``StoriesConfig`` admin under the **Open Graph**, **Twitter**,
and **Schema.org** sections. This is useful when one configuration is a blog (type "Blog") and
another is a news section (type "NewsArticle").

Adding structured data
======================

Search engines increasingly rely on structured data to understand content. You can add a
JSON-LD block to your ``post_detail.html`` template for richer search results:

.. code-block:: html+django

    {% block extra_head %}
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "{{ post_content.title }}",
        "author": {
            "@type": "Person",
            "name": "{{ post_content.post.author.get_full_name }}"
        },
        "datePublished": "{{ post_content.post.date_published|date:'c' }}",
        "dateModified": "{{ post_content.post.date_modified|date:'c' }}",
        "description": "{{ post_content.abstract }}"
    }
    </script>
    {% endblock %}

SEO-friendly URLs
=================

djangocms-stories generates clean, human-readable URLs by default. Unicode slugs are enabled
via ``STORIES_ALLOW_UNICODE_SLUGS``, so titles in non-Latin scripts produce readable URLs
rather than percent-encoded noise.

Choose a permalink style that fits your content: date-based permalinks
(``2025/03/my-post/``) work well for news and time-sensitive content, while slug-only
permalinks (``my-post/``) keep URLs short for evergreen articles.

Sitemaps
========

A sitemap helps search engines discover all your published content. See
:doc:`feeds-and-sitemaps` for setup instructions.

Writing for discoverability
============================

No amount of meta tags compensates for thin content. A few editorial habits make a real
difference:

- Keep titles between 50 and 60 characters so they display fully in search results.
- Write meta descriptions up to 320 characters (the ``STORIES_META_DESCRIPTION_LENGTH``
  default) — this is the snippet Google shows beneath your title.
- Use a single ``<h1>`` per page (the post title) and structure sub-sections with ``<h2>``
  and ``<h3>`` tags.
- Fill in the abstract field: it doubles as the meta description when no explicit one is set.
