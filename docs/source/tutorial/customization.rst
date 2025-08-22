####################
Customizing Stories
####################

Templates
=========

djangocms-stories comes with minimal templates without any styling. You can override these templates in the classical
Django way (see the `Django template loading documentation <https://docs.djangoproject.com/en/stable/topics/templates/#template-loading>`_)
by placing your own versions in your project's ``templates/djangocms_stories/`` directory.
This allows you to add your own markup and styling to customize the appearance of your stories.

Story List Template
-------------------

Create ``templates/djangocms_stories/post_list.html``::

    {% extends "base.html" %}
    {% load i18n cms_tags %}

    {% block content %}
        <h1>{% trans "Stories" %}</h1>
        {% for post in post_list %}
            <article>
                <h2><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h2>
                <p>{{ post.abstract }}</p>
                <time>{{ post.date_published }}</time>
            </article>
        {% endfor %}
    {% endblock %}

Story Detail Template
----------------------

Create ``templates/djangocms_stories/post_detail.html``::

    {% extends "base.html" %}
    {% load i18n cms_tags %}

    {% block content %}
        <article>
            <h1>{{ post.title }}</h1>
            <time>{{ post.date_published }}</time>
            <div class="content">
                {% render_placeholder post.content %}
            </div>
            <div class="tags">
                {% for tag in post.tags.all %}
                    <span class="tag">{{ tag.name }}</span>
                {% endfor %}
            </div>
        </article>
    {% endblock %}


.. seealso::

    For more detailed information on creating your own templates, refer
    to the :ref:`custom_templates` chapter.


Settings Configuration
======================

Customize behavior through Django settings:

Story Configuration
-------------------

::

    # Number of stories per page
    STORIES_PAGINATE_BY = 10

    # Default template for stories
    STORIES_TEMPLATE_PREFIX = 'my_stories'

    # Enable/disable features
    STORIES_USE_ABSTRACT = True
    STORIES_USE_TAGS = True
    STORIES_USE_CATEGORIES = True

.. seealso::

    For more detailed information on available settings, refer
    to the :ref:`settings` chapter.
