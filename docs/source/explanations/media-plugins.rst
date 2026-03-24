##########################
Media Plugins & Podcasting
##########################

Publishing a vlog or podcast requires knowing more about embedded content than a typical CMS
plugin provides. A standard video plugin renders an iframe and nothing else — but a post
listing page needs a thumbnail, a podcast feed needs a duration, and a media player needs a
URL it can stream from. djangocms-stories addresses this with a media plugin system that makes
embedded content introspectable.

The media placeholder
=====================

Every ``PostContent`` has a dedicated ``media`` placeholder alongside the regular ``content``
placeholder. This separation exists so that media attachments — the video of a vlog episode, the
audio file of a podcast — can be handled differently from the body text. Templates can
render the media placeholder independently, extract thumbnails from it for listing pages, or
skip it entirely for text-only posts.

To add media to a post, editors add plugins to the media placeholder in the frontend editor,
just as they would add plugins to the content area.

The MediaAttachmentPluginMixin
===============================

The core of the system is ``MediaAttachmentPluginMixin``, a mixin you add to your plugin
models. It provides a standard interface for extracting metadata from media content:

.. code-block:: python

    from djangocms_stories.media.base import MediaAttachmentPluginMixin
    from cms.models import CMSPlugin

    class VimeoPlugin(MediaAttachmentPluginMixin, CMSPlugin):
        url = models.URLField('Video URL')

        _media_autoconfiguration = {
            'params': [
                re.compile(r'^https://vimeo.com/(?P<media_id>[-0-9]+)$'),
            ],
            'thumb_url': '%(thumb_url)s',
            'main_url': '%(main_url)s',
            'callable': 'vimeo_data',
        }

        @property
        def media_url(self):
            return self.url

The ``_media_autoconfiguration`` dictionary tells the mixin how to extract parameters from the
media URL (via regex), how to build thumbnail and main-image URLs from those parameters, and
optionally which method to call for fetching additional metadata from an external API.

Every media plugin must implement the ``media_url`` property — this is the canonical URL of the
media resource. Beyond that, you can add whatever properties your templates need:
``media_id``, ``media_title``, ``duration``, and so on.

djangocms-stories deliberately does **not** ship plugins for specific platforms like YouTube or
Vimeo. Platform APIs change frequently, and maintaining wrappers for each one would be a
burden. Instead, the mixin gives you the building blocks to create your own plugins tailored to
the platforms you actually use.

Template tags for media
========================

Two template tags abstract away the django CMS placeholder machinery and let you work with
media content directly:

``{% media_images post_content %}`` extracts thumbnail URLs from all media plugins in the
media placeholder. This is useful on listing pages where you want a preview image for each
post without rendering the full plugin:

.. code-block:: html+django

    {% load djangocms_stories %}
    {% media_images post_content as previews %}
    {% for preview in previews %}
        <img src="{{ preview }}" alt="Preview" />
    {% endfor %}

``{% media_plugins post_content %}`` retrieves the actual plugin instances, which you can then
render individually or inspect for metadata:

.. code-block:: html+django

    {% media_plugins post_content as media_items %}
    {% for plugin in media_items %}
        {% render_plugin plugin %}
    {% endfor %}

In the detail template, you'll typically render the entire media placeholder at once using
``{% render_placeholder post_content.media %}``. The template tags are most useful on listing
pages and in feeds where full rendering isn't appropriate.

djangocms-video support
========================

If you use ``djangocms-video``, its ``poster`` field is automatically recognized by
``media_images``. Adding a ``djangocms-video`` plugin to the media placeholder makes its poster
image available as a preview thumbnail alongside any custom media plugins.

Podcasting
===========

There is nothing special about podcast support in djangocms-stories — it follows the same
pattern as any other media type. Create a plugin model with ``MediaAttachmentPluginMixin``
that holds your audio URL, episode number, duration, and transcript link. Register it as a CMS
plugin. Add it to the media placeholder of your posts.

The built-in RSS feed classes (``LatestEntriesFeed``, ``TagFeed``) can serve as the basis for a
podcast feed: subclass one and add the ``<enclosure>`` and iTunes-specific XML elements your
podcast directory requires. The media plugin's introspectable properties give you access to
the audio URL and metadata you need to populate the feed entries.
