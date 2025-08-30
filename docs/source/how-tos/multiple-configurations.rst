################################
How to set up multiple configurations
################################

You can run multiple story configurations, for example separate blogs or news for
different departments or topics.


Creating Multiple Configurations
=================================

1. In Django admin, go to Stories → Configurations
2. Create a new configuration with:

   - Unique namespace (e.g., "tech-blog", "news")
   - App title (e.g., "Tech Blog", "Company News")
   - Object name (e.g., "Article", "News Item")

Post Assignment to Configurations
==================================

**One Configuration per Post**

Each post belongs to exactly one configuration. When creating a post, you must select which configuration it belongs to. This determines:

- Which blog/site the post appears on
- Which templates and styling are used
- Which permissions apply
- Which menu structure includes the post

**Changing Configuration Assignment**

You can change a post's configuration assignment later:

1. Go to the post in Django admin
2. Change the "App config" field to a different configuration
3. Save the post

The post will then appear in the new configuration and disappear from the old one.

**Posts in Multiple Configurations**

If you need the same content to appear in multiple configurations, you must:

1. Create separate post instances for each configuration
2. Copy the content between posts manually
3. Maintain each copy independently

.. note::
   There is no automatic content sharing between configurations. Each post
   exists in one configuration only. To display the same article in both
   a "Tech Blog" and "Company News" section, create two separate posts.

   **Example Workflow**

   To create a post that appears in both "Tech Blog" and "Company News"::

        # Create first post
        Tech Blog Post:
        - App config: "tech-blog"
        - Title: "New Framework Release"
        - Content: [your content, potentially adjusted for a tech blog audience]

        # Create second post
        Company News Post:
        - App config: "company-news"
        - Title: "New Framework Release"
        - Content: [same content, manually copied, potentially adjusted to new audience]

Setting up Pages
=================

1. Create separate pages for each configuration to live. The page will be the "root" of that
   configuration's content.
2. Assign the respective configuration to each page
3. Publish the page to make the configuration visible
4. Set different URL patterns if needed

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
