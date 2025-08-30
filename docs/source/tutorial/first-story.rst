##############################
Creating Your First Story Blog
##############################

This guide will walk you through creating your first blog with djangocms-stories.

Setting up a Stories Page
==========================

1. In the Django CMS admin, create a new page
2. Go to the "Advanced settings" of the newly created page
3. Choose "Stories" in the "Application" field
4. Select your story config (see :ref:`create_a_stories_config`)
5. Publish the page (if you are using versioning) to make it visible.
6. Depending on your project configuration, you might need to restart the server to let Django know about the new application hook.

Creating a Story
=================

1. Navigate to the stories page
2. Click "Add Story" in the toolbar
3. Fill in the required fields:
   - Title
   - Abstract (optional)
   - Content
4. Add categories and tags as needed
5. Save and publish

Adding Content with Plugins
============================

Stories support Django CMS plugins for rich content:

1. Edit your story
2. Click on the content placeholder
3. Add plugins like:
   - Text
   - Images
   - Videos
   - Links

Working with Categories
=======================

Categories help organize your stories:

1. Go to Stories → Categories in the admin
2. Create new categories
3. Assign stories to categories
4. Use categories for navigation and filtering

Publishing
==========

djangocms-stories integrates with djangocms-versioning for publication and version management.
The experience is similar to the publication process for pages.

If you want to schedule a story, we recommend **djangocms-timed-publication** as a addon for
djangocms-versioning.
