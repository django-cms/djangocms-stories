
.. _content-wizard:

##################
Wizard Integration
##################

django CMS includes a content creation wizard — the "+" button in the toolbar — that lets
editors create new content without visiting the Django admin. djangocms-stories hooks into this
system so that creating a new story is as quick as creating a new page.

How it works
============

For each ``StoriesConfig`` you define, djangocms-stories automatically registers a wizard entry.
If your site has two configurations — say "Blog" and "News" — editors will see both in the
wizard dropdown, each creating a post in the right section.

The wizard form asks for a title and, optionally, a text body. When the editor submits the
form, djangocms-stories creates a new ``Post`` and its initial ``PostContent``, generates a slug
from the title, and — if the configuration uses placeholders — wraps the body text in a text
plugin and attaches it to the content placeholder.

If djangocms-versioning is active, the new post starts as a draft. The editor can then refine
it in the frontend editor before publishing.

Configuring the text plugin
============================

By default the wizard uses ``TextPlugin`` and writes the body into its ``body`` field. If your
project uses a different text plugin, change these two settings:

.. code-block:: python

    STORIES_WIZARD_CONTENT_PLUGIN = 'TextPlugin'      # plugin class name
    STORIES_WIZARD_CONTENT_PLUGIN_BODY = 'body'        # field name on that plugin

The plugin you choose must work with only the body field filled in — all other fields must be
optional. If the plugin requires additional mandatory fields, the wizard will fail to create
the post.

When the wizard is not enough
==============================

The wizard is intentionally minimal. It covers the most common case — "I want to start writing
a new post right now" — but it doesn't expose every field. For full control over categories,
tags, images, SEO fields, and publication dates, editors should use the Django admin or the
toolbar's post properties panel after creating the initial draft.
