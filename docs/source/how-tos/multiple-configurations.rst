################################
How to set up multiple configurations
################################

You can run multiple story configurations on the same site, for example separate blogs for different departments or topics.

Creating Multiple Configurations
=================================

1. In Django admin, go to Stories → Configurations
2. Create a new configuration with:
   - Unique namespace (e.g., "tech-blog", "news")
   - App title (e.g., "Tech Blog", "Company News")
   - Object name (e.g., "Article", "News Item")

Setting up Pages
=================

1. Create separate pages for each configuration
2. Assign the respective configuration to each page
3. Set different URL patterns if needed

URL Configuration
=================

For multiple configurations, use namespaced URLs::

    urlpatterns = [
        path('tech/', include('djangocms_stories.urls', namespace='tech-blog')),
        path('news/', include('djangocms_stories.urls', namespace='news')),
    ]

Template Customization
=======================

Create configuration-specific templates::

    templates/
        djangocms_stories/
            tech-blog/
                post_list.html
                post_detail.html
            news/
                post_list.html
                post_detail.html

Navigation Menus
================

Each configuration can have its own menu structure:

1. Configure menu settings per app config
2. Choose between:
   - No menu items
   - Categories only
   - Posts only
   - Complete menu (categories + posts)

Permissions
===========

Set different permissions per configuration:

1. Create user groups per configuration
2. Assign appropriate permissions
3. Use the Stories Config permissions to control access
