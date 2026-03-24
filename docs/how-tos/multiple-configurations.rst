######################################
How to set up multiple configurations
######################################

djangocms-stories supports running multiple independent story configurations on the same site.
This is useful when your project needs distinct content sections — for example, a company blog,
a news feed, and a knowledge base — each with its own URL structure, templates, and editorial
settings.

Understanding configurations
=============================

A ``StoriesConfig`` is an apphook configuration that controls how a group of posts behaves:
which permalink style is used, how many posts per page, which menu items appear, and so on.
Each configuration gets its own namespace (like ``blog`` or ``news``), and each CMS page can
host exactly one configuration.

Posts belong to a single configuration. This means a post published under the "Tech Blog"
configuration will only appear on the Tech Blog page and its feeds — it won't show up
under "Company News" unless you create a separate post there.

Creating a new configuration
=============================

Open the Django admin and navigate to **Stories > Configurations**. Create a new entry with:

- A **namespace** that will appear in URLs and must be unique (e.g. ``tech-blog``). This
  cannot be changed later, so choose carefully.
- An **app title** that editors will see in the toolbar and admin (e.g. "Tech Blog").
- An **object name** that labels individual items in the wizard and admin (e.g. "Article" or
  "News Item").

You can also configure the permalink style, pagination, menu structure, and SEO defaults
independently for each configuration.

Attaching configurations to pages
===================================

Each configuration needs a CMS page to live on. Create a new page for each section, open
its **Page settings**, choose **Stories** as the application, and select the matching
configuration.

Because the page determines the base URL, you get natural URL separation: ``/blog/my-post/``
vs. ``/news/my-post/``. If you prefer, you can also use different permalink styles per
configuration — dates for the blog, categories for news.

After publishing the page, the configuration is live.

Using different templates per configuration
============================================

Each configuration can load templates from a different directory by setting the
**Template prefix** field in the configuration admin. For example, if you set the prefix to
``news``, djangocms-stories will look for templates in ``templates/news/`` before falling back
to the defaults.

This means you can have a card-based layout for one section and a traditional list for another,
without any template logic branching on the namespace:

.. code-block:: text

    templates/
        djangocms_stories/      # default templates
            post_list.html
            post_detail.html
        news/                   # templates for the "news" config
            post_list.html
            post_detail.html

Menu and navigation
====================

Each configuration has its own menu structure setting. The "Tech Blog" might show a full
category-and-post tree in the navigation, while "Company News" shows only posts without
categories, and "Knowledge Base" shows categories only.

Configure this in the **Menu structure** field of each ``StoriesConfig``.

Sharing content across configurations
=======================================

There is no automatic content sharing between configurations. If you need the same article to
appear in two sections, you'll need to create it twice — once per configuration. This is by
design: each section may have different audiences, different editorial workflows, and different
publication schedules.

In practice, this is rarely needed. If you find yourself duplicating content frequently,
consider whether a single configuration with categories might serve your needs better than
multiple configurations.
