####################
Customizing Stories
####################

Templates
=========

djangocms-stories comes with minimal templates without any styling. You can override these templates in the classical
Django way (see the `Django template loading documentation <https://docs.djangoproject.com/en/stable/topics/templates/#template-loading>`_)
by placing your own versions in your project's ``templates/djangocms_stories/`` directory.
This allows you to add your own markup and styling to customize the appearance of your stories.

Default template directory structure
------------------------------------

    djangocms_stories/
        templates/
            djangocms_stories/
                base.html
                post_archive.html
                post_detail.html
                post_list.html
                category_list.html
                post_author_list.html
                includes/
                    post_meta.html
                    post_header.html
                    post_footer.html

Story List Template
-------------------

Create your custom ``templates/djangocms_stories/post_list.html`` based on the
default example::

    {% extends "djangocms_stories/base.html" %}
    {% load i18n easy_thumbnails_tags cms_tags %}

    {% block content_blog %}
    <section class="blog-list">
        {% block blog_title %}
        <header>
            <h2>
            {% if author %}{% trans "Articles by" %} {{ author.get_full_name }}
            {% elif archive_date %}{% trans "Archive" %} &ndash; {% if month %}{{ archive_date|date:'F' }} {% endif %}{{ year }}
            {% elif tagged_entries %}{% trans "Tag" %} &ndash; {{ tagged_entries|capfirst }}
            {% elif category %}{% trans "Category" %} &ndash; {% render_model category "name" %}{% endif %}
            </h2>
        </header>
        {% endblock %}

        {% for post_content in postcontent_list %}
            <article class="post-item">
                <h3><a href="{{ post_content.get_absolute_url }}">{{ post_content.title }}</a></h3>
                <p>{{ post_content.abstract }}</p>
                <time>{{ post_content.post.date_published }}</time>
                {% if post_content.post.main_image %}
                    {% thumbnail post_content.post.main_image "300x200" crop upscale as thumb %}
                    <img src="{{ thumb.url }}" alt="{{ post_content.title }}" />
                {% endif %}
            </article>
        {% empty %}
            <p class="blog-empty">{% trans "No article found." %}</p>
        {% endfor %}

        {% if is_paginated %}
        <nav class="pagination">
            {% if page_obj.has_previous %}
                <a href="?{{ view.page_kwarg }}={{ page_obj.previous_page_number }}">&laquo; {% trans "previous" %}</a>
            {% endif %}
            <span class="current">
                {% trans "Page" %} {{ page_obj.number }} {% trans "of" %} {{ paginator.num_pages }}
            </span>
            {% if page_obj.has_next %}
                <a href="?{{ view.page_kwarg }}={{ page_obj.next_page_number }}">{% trans "next" %} &raquo;</a>
            {% endif %}
        </nav>
        {% endif %}
    </section>
    {% endblock %}

These are the context variables available in the **Story List Template (post_list.html)**

- ``postcontent_list`` - List of PostContent objects (translated content)
- ``page_obj`` - Pagination object when paginated
- ``paginator`` - Paginator instance
- ``is_paginated`` - Boolean indicating if content is paginated
- ``author`` - Author object when filtering by author
- ``archive_date`` - Date object when viewing archives
- ``year``, ``month`` - Integer values for archive filtering
- ``tagged_entries`` - Tag name when filtering by tag
- ``category`` - Category object when filtering by category


Story Detail Template
----------------------

Create ``templates/djangocms_stories/post_detail.html``::

    {% extends "djangocms_stories/base.html" %}
    {% load i18n easy_thumbnails_tags cms_tags %}

    {% block title %}{{ post_content.title }}{% endblock %}

    {% block content_blog %}
    <article id="post-{{ post_content.slug }}" class="post-item post-detail">
        <header>
            <h2>{% render_model post_content "title" "title" %}</h2>
            {% if post_content.subtitle %}
                <h3>{% render_model post_content "subtitle" "subtitle" %}</h3>
            {% endif %}
            {% block post_meta %}
                <div class="blog-meta">
                    <time>{{ post_content.post.date_published }}</time>
                    {% if post_content.post.author %}
                        <span class="author">{{ post_content.post.author.get_full_name }}</span>
                    {% endif %}
                </div>
            {% endblock %}
        </header>

        {% if post_content.post.main_image %}
            <div class="blog-visual">
                {% thumbnail post_content.post.main_image "800x400" crop upscale as main_image %}
                <img src="{{ main_image.url }}" alt="{{ post_content.post.main_image.default_alt_text }}"
                     width="{{ main_image.width }}" height="{{ main_image.height }}" />
            </div>
        {% endif %}

        {% if post_content.post.app_config.use_placeholder and post_content.content %}
            <div class="blog-content">{% placeholder "content" %}</div>
        {% else %}
            <div class="blog-content">{% render_model post_content "post_text" "post_text" "" "safe" %}</div>
        {% endif %}

        {% if post_content.post.tags.exists %}
            <div class="tags">
                {% for tag in post_content.post.tags.all %}
                    <span class="tag">{{ tag.name }}</span>
                {% endfor %}
            </div>
        {% endif %}

        {% if post_content.post.related.exists %}
            <section class="related-posts">
                <h3>{% trans "Related Stories" %}</h3>
                {% for related in post_content.post.related.all %}
                    <article class="related-item">
                        <h4><a href="{{ related.get_content.get_absolute_url }}">{{ related.get_content.title }}</a></h4>
                    </article>
                {% endfor %}
            </section>
        {% endif %}
    </article>
    {% endblock %}

These are the context variables available in the **Story Detail Template (post_detail.html)**

- ``post_content`` - PostContent object (translated content)
- ``meta`` - Meta object with SEO information
- ``TRUNCWORDS_COUNT`` - Number of words for truncation

.. seealso::

    For more detailed information on creating your own templates, refer
    to the :ref:`custom_templates` chapter.

Important Template Notes
------------------------

:class:`~djangocms_stories.models.PostContent` vs :class:`~djangocms_stories.models.Post` Objects**

djangocms-stories uses django CMS' `grouper-content structure <https://docs.django-cms.org/en/stable/how_to/16-grouper-admin.html>`_ for
multi-language architecture where:

- :class:`~djangocms_stories.models.Post` - The main model containing language-independent data (dates, author, images, etc.)
- :class:`~djangocms_stories.models.PostContent` - Contains translated content (title, subtitle, abstract, post_text, etc.)

In templates, you typically work with ``post_content`` objects and access the underlying ``Post`` via ``post_content.post``.

**Placeholder vs Rich Text Fields**

Content can be rendered in two ways depending on the ``use_placeholder`` setting:

- **Placeholders**: ``{% placeholder "content" %}`` - Allows CMS plugins
- **Rich Text**: ``{% render_model post_content "post_text" %}`` - Simple rich text field

**Template Inheritance**

Templates can extend ``djangocms_stories/base.html`` which provides the basic structure and common blocks like ``content_blog``.
It may also be customized according to your needs by overriding specific blocks or adding new ones.

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
