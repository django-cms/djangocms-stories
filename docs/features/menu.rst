.. _menu:

####
Menu
####

``djangocms_stories`` provides support for the django CMS menu framework.

By default all the categories and posts are added to the menu, in a hierarchical structure.

It is possible to configure per Apphook whether the menu includes posts and categories
(the default), only categories, only posts, or no items.

If "posts and categories" or "only categories" are set, all the posts not associated with a
category are not added to the menu.

.. _sitemap:

#######
Sitemap
#######

``djangocms_stories`` provides a sitemap for improved SEO indexing.
Sitemap returns all the published posts in all the languages each post is available.

The changefreq and priority is configurable per-apphook (see ``STORIES_SITEMAP_*`` in
:ref:`settings`).

To add the stories Sitemap, add the following code to the project ``urls.py``:

.. code-block:: python

    from django.contrib.sitemaps.views import sitemap
    from cms.sitemaps import CMSSitemap
    from djangocms_stories.sitemaps import StoriesSitemap


    urlpatterns = [
        ...
        path('sitemap.xml', sitemap,
            {'sitemaps': {
                'cmspages': CMSSitemap, 'stories': StoriesSitemap,
            }
        }),
    ]
