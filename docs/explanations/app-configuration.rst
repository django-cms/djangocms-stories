##################
App Configuration
##################

djangocms-stories can power more than one content section on a site. A single installation
might serve a company blog, a news feed, and an internal knowledge base — each with its own
URL structure, templates, pagination, and editorial defaults. The mechanism that makes this
possible is the ``StoriesConfig`` model.

What a StoriesConfig represents
================================

A ``StoriesConfig`` is a named bundle of settings that controls how a group of posts behaves.
It is the stories equivalent of what django CMS calls an "apphook configuration": a way to
attach the same application to multiple pages with different parameters.

Every ``StoriesConfig`` has a **namespace** — a short identifier like ``blog`` or ``news`` that
appears in URL names and is used internally to route requests to the right configuration.
Namespaces are permanent: once set, they cannot be changed, because URLs, bookmarks, and
search engine indexes depend on them.

Beyond the namespace, a configuration controls:

- **Permalink style** — whether post URLs include the full date, a short date, a category
  prefix, or just the slug.
- **Content editing mode** — whether post bodies use django CMS placeholders (with plugins) or
  a simpler rich-text field.
- **Pagination** — how many posts appear per page in list views.
- **Menu structure** — whether categories, posts, both, or neither appear in the django CMS
  navigation.
- **Template prefix** — an alternative directory from which templates are loaded, allowing each
  configuration to have a completely different visual design.
- **SEO and social defaults** — Open Graph type, Twitter Card type, Schema.org type, sitemap
  priority, and other metadata defaults.

All of these can differ between configurations on the same site.

How configurations relate to pages
====================================

Each ``StoriesConfig`` is attached to a django CMS page through the apphook mechanism. The page
determines the base URL: if the "Blog" configuration is attached to a page at ``/blog/``, all
posts in that configuration live under ``/blog/``. A "News" configuration attached to ``/news/``
gets its own URL space.

This means the CMS page tree controls where each content section appears in the site structure,
while the ``StoriesConfig`` controls how it behaves once you're inside it. Editors manage the
page tree as usual; developers configure the behaviour through the admin or settings.

A page can host only one configuration, and a configuration should be attached to only one page
per site. If you need the same content to appear at two different URLs, create two
configurations (each with its own posts) rather than attaching one configuration to two pages.

Posts belong to one configuration
==================================

Every post is assigned to exactly one ``StoriesConfig``. This assignment determines which page
the post appears under, which templates render it, and which feeds include it. Moving a post to
a different configuration changes all of these at once.

There is no built-in way to share a single post across configurations. This is intentional:
each configuration may have different audiences, different editorial standards, and different
publication schedules. If you find yourself wanting to share content, consider whether a single
configuration with categories might be a better fit than multiple configurations.
