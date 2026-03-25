.. _custom_templates:

###############################
How to create custom templates
###############################

djangocms-stories ships with minimal, unstyled templates that render every field but leave
visual design to you. This guide explains how to override individual templates, create
complete template sets, and build plugin-specific layouts.

How template loading works
===========================

All story templates extend ``djangocms_stories/base.html``, which in turn extends your site's
``base.html`` and pulls content into a ``content`` block. The hierarchy looks like this:

.. code-block:: text

    your_site/base.html
    └── djangocms_stories/base.html
        ├── djangocms_stories/post_list.html
        ├── djangocms_stories/post_detail.html
        ├── djangocms_stories/category_list.html
        └── ...

Because Django's template loader checks your project's ``templates/`` directory before the
app's built-in templates, you can override any single file by placing a file with the same
path in your project. There is no need to copy all templates — override only what you want to
change.

Overriding the base template
==============================

If your site's ``base.html`` doesn't define a ``content`` block, or you want a different
wrapper around story pages, create your own base template:

**templates/djangocms_stories/base.html:**

.. code-block:: html+django

    {% extends "base.html" %}
    {% load static %}

    {% block content %}
        <div class="stories-wrapper">
            {% block content_blog %}{% endblock %}
        </div>
    {% endblock %}

Every other story template extends this file, so changing it once affects all views.

Complete template sets
========================

Sometimes a single override isn't enough — you want an entirely different look for a section
of the site. djangocms-stories supports this through **template prefixes**: a directory name
that the app prepends to every template path.

To set one up:

1. Copy the default templates into a new directory:

   .. code-block:: bash

       cp -a djangocms_stories/templates/djangocms_stories/* \
            your_project/templates/my_stories/

2. Open the ``StoriesConfig`` admin and enter ``my_stories`` in the **Template prefix** field.

3. Edit the copied templates to your liking.

From now on, that configuration will load ``my_stories/post_list.html`` instead of
``djangocms_stories/post_list.html``. If a template is missing from the custom set, the
default is used as a fallback, so you only need to include files you've actually changed.

This is especially useful with :doc:`multiple-configurations`: the tech blog can use a
card-based grid while the company news uses a traditional list, each driven by its own
template prefix.

Plugin template folders
========================

Plugins like "Latest Blog Articles" or "Categories" also support multiple template variants.
By defining ``STORIES_PLUGIN_TEMPLATE_FOLDERS`` in your settings, you give editors a choice of
layout per plugin instance:

.. code-block:: python

    from django.utils.translation import gettext_lazy as _

    STORIES_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default')),
        ('timeline', _('Timeline')),
        ('cards', _('Card grid')),
    )

Each entry names a sub-folder inside the current template prefix. When an editor adds a
"Latest Blog Articles" plugin, they can pick "Timeline" from a dropdown, and the plugin will
render using ``my_stories/timeline/latest_entries.html`` instead of
``my_stories/plugins/latest_entries.html``.

You must provide **all** plugin templates for each folder you define — the app won't mix
templates from different folders within a single plugin instance.

Template resolution order
==========================

When djangocms-stories looks for a template, it checks these locations in order:

1. ``your_project/templates/<prefix>/post_list.html`` — project templates (highest priority)
2. ``djangocms_stories/templates/<prefix>/post_list.html`` — app templates with prefix
3. ``djangocms_stories/templates/djangocms_stories/post_list.html`` — default app templates

This means you can start with the defaults, override one or two files in your project, and
only create a full set when you truly need it.

Tips
====

- **Start by copying.** Don't write templates from scratch — copy a default, then modify it.
  This avoids missing context variables or block names.
- **Use ``post_content`` in templates.** The detail and list views pass ``PostContent`` objects
  (translated content). Access language-independent data like the author or publication date
  through ``post_content.post``.
- **Choose between placeholders and rich text.** If ``use_placeholder`` is enabled in the
  configuration, use ``{% placeholder "content" %}`` in the detail template. Otherwise, render
  the ``post_text`` field with ``{% render_model post_content "post_text" %}``.
