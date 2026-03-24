#############
Template Tags
#############

Template tags for displaying stories and related content.

Load the template tags with::

    {% load djangocms_stories %}

.. currentmodule:: djangocms_stories.templatetags.djangocms_stories

Available Tags
==============

namespace_url
-------------

.. autofunction:: namespace_url

Reverse a URL within the stories namespace::

    {% load djangocms_stories %}
    {% namespace_url "posts-latest" as latest_url %}
    <a href="{{ latest_url }}">All stories</a>

media_plugins
-------------

.. autofunction:: media_plugins

Extract media plugins from a post's media placeholder::

    {% load djangocms_stories %}
    {% media_plugins post_content as media_content %}
    {% for plugin in media_content %}
        {% render_plugin plugin %}
    {% endfor %}

media_images
-------------

.. autofunction:: media_images

Extract image URLs from media plugins::

    {% load djangocms_stories %}
    {% media_images post_content as previews %}
    {% for preview in previews %}
        <img src="{{ preview }}" alt="Media preview" />
    {% endfor %}

absolute_url
------------

.. autoclass:: GetAbsoluteUrl

Get the absolute URL for a post content object, with toolbar-awareness::

    {% load djangocms_stories %}
    {% absolute_url post_content as post_url %}
    <a href="{{ post_url }}">{{ post_content.title }}</a>
