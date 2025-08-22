############
Template Tags
############

Template tags for displaying stories and related content.

.. currentmodule:: djangocms_stories.templatetags.stories_tags

Story Tags
==========

.. autofunction:: get_posts

.. autofunction:: get_recent_posts

.. autofunction:: get_featured_posts

.. autofunction:: get_related_posts

.. autofunction:: get_post_categories

.. autofunction:: get_post_tags

Category Tags
=============

.. autofunction:: get_categories

.. autofunction:: get_category_posts

.. autofunction:: get_category_tree

.. autofunction:: render_category_menu

Archive Tags
============

.. autofunction:: get_archive_dates

.. autofunction:: get_posts_by_date

.. autofunction:: render_archive_menu

Utility Tags
============

.. autofunction:: get_app_config

.. autofunction:: get_current_post

.. autofunction:: get_post_url

.. autofunction:: get_category_url

URL Tags
========

.. autofunction:: stories_url

.. autofunction:: category_url

.. autofunction:: tag_url

.. autofunction:: author_url

Filters
=======

.. autofunction:: story_excerpt

.. autofunction:: story_tags

.. autofunction:: story_reading_time

.. autofunction:: story_word_count

Usage Examples
==============

Basic story listing::

    {% load stories_tags %}

    {% get_recent_posts 5 as recent_posts %}
    {% for post in recent_posts %}
        <h3><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h3>
        <p>{{ post.abstract }}</p>
    {% endfor %}

Category navigation::

    {% load stories_tags %}

    {% get_categories as categories %}
    <ul class="category-menu">
    {% for category in categories %}
        <li><a href="{{ category.get_absolute_url }}">{{ category.name }}</a></li>
    {% endfor %}
    </ul>

Related posts::

    {% load stories_tags %}

    {% get_related_posts post as related %}
    {% if related %}
        <h4>Related Stories</h4>
        {% for related_post in related %}
            <a href="{{ related_post.get_absolute_url }}">{{ related_post.title }}</a>
        {% endfor %}
    {% endif %}
