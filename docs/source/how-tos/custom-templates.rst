.. _custom_templates:


###########################
How to create custom templates
###########################

This guide shows how to create and customize templates for your stories, including complete template sets and plugin templates.

Base Template Structure
=======================

djangocms-stories uses a base template system for easy customization. All story templates extend a ``djangocms_stories/base.html`` template, which in turn extends your site's ``base.html`` template.

**Template hierarchy:**

::

    your_site/base.html
    └── djangocms_stories/base.html
        ├── djangocms_stories/post_list.html
        ├── djangocms_stories/post_detail.html
        ├── djangocms_stories/category_list.html
        └── other story templates...

Creating a Custom Base Template
================================

If your site's ``base.html`` doesn't have a ``content`` block, or you need different structure, create your own base template:

**templates/djangocms_stories/base.html:**

::

    {% extends "base.html" %}
    {% load cms_tags %}

    {% block title %}{{ block.super }}{% endblock %}

    {% block content %}
        <div class="stories-wrapper">
            {% block stories_content %}{% endblock %}
        </div>
    {% endblock %}

    {% block extra_css %}
        {{ block.super }}
        <link rel="stylesheet" href="{% static 'css/stories-custom.css' %}">
    {% endblock %}

Complete Template Sets
======================

You can create a complete custom template set for different looks or configurations.

Setting Up Template Sets
-------------------------

1. **Create template directory structure:**

   ::

       templates/
           my_stories/                 # Custom template set
               base.html
               post_list.html
               post_detail.html
               category_list.html
               tag_list.html
               plugins/
                   latest_entries.html
                   categories.html
                   tags.html
                   archive.html

2. **Configure in Stories Config:**

   In Django admin, go to **Stories → Configurations** and set:
   - **Template prefix:** ``my_stories``

3. **Copy and customize templates:**

   Start by copying the default templates:

   ::

       cp -a djangocms_stories/templates/djangocms_stories/* /path/to/your/project/templates/my_stories/

Custom Story List Template
===========================

Create a customized story list view:

**templates/my_stories/post_list.html:**

::

    {% extends "my_stories/base.html" %}
    {% load i18n cms_tags stories_tags thumbnail %}

    {% block title %}{{ view.get_title }} - {{ block.super }}{% endblock %}

    {% block stories_content %}
        <div class="stories-container">
            <!-- Header Section -->
            <header class="stories-header">
                <h1 class="stories-title">{{ view.get_title }}</h1>

                {% if category %}
                    <p class="category-description">{{ category.description }}</p>
                    <div class="breadcrumbs">
                        <a href="{% url 'djangocms_stories:posts-latest' %}">{% trans "All Stories" %}</a>
                        → {{ category.name }}
                    </div>
                {% endif %}
            </header>

            <!-- Filter Bar -->
            <div class="stories-filters">
                {% get_categories as all_categories %}
                <div class="filter-categories">
                    <span class="filter-label">{% trans "Categories:" %}</span>
                    <a href="{% url 'djangocms_stories:posts-latest' %}"
                       class="filter-link{% if not category %} active{% endif %}">
                        {% trans "All" %}
                    </a>
                    {% for cat in all_categories %}
                        <a href="{{ cat.get_absolute_url }}"
                           class="filter-link{% if category == cat %} active{% endif %}">
                            {{ cat.name }} ({{ cat.post_count }})
                        </a>
                    {% endfor %}
                </div>
            </div>

            <!-- Stories Grid -->
            <div class="stories-grid">
                {% for post in post_list %}
                    <article class="story-card">
                        {% if post.main_image %}
                            <div class="story-image">
                                {% thumbnail post.main_image 400x250 crop quality=95 as thumb %}
                                <img src="{{ thumb.url }}" alt="{{ post.title }}" loading="lazy">
                                <div class="image-overlay">
                                    {% if post.categories.exists %}
                                        {% for cat in post.categories.all %}
                                            <span class="category-badge">{{ cat.name }}</span>
                                        {% endfor %}
                                    {% endif %}
                                </div>
                            </div>
                        {% endif %}

                        <div class="story-content">
                            <h2 class="story-title">
                                <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
                            </h2>

                            {% if post.abstract %}
                                <p class="story-abstract">{{ post.abstract|truncatewords:25 }}</p>
                            {% endif %}

                            <div class="story-meta">
                                <time datetime="{{ post.date_published|date:'c' }}" class="story-date">
                                    {{ post.date_published|date:'F j, Y' }}
                                </time>

                                {% if post.author %}
                                    <span class="story-author">
                                        {% trans "by" %} {{ post.author.get_full_name|default:post.author.username }}
                                    </span>
                                {% endif %}

                                <span class="reading-time">{{ post.content|story_reading_time }} min read</span>
                            </div>

                            {% if post.tags.exists %}
                                <div class="story-tags">
                                    {% for tag in post.tags.all|slice:":3" %}
                                        <a href="{% url 'djangocms_stories:posts-tagged' tag=tag.slug %}"
                                           class="tag-link">#{{ tag.name }}</a>
                                    {% endfor %}
                                </div>
                            {% endif %}
                        </div>
                    </article>
                {% endfor %}
            </div>

            <!-- Pagination -->
            {% if is_paginated %}
                <nav class="pagination" aria-label="{% trans 'Stories pagination' %}">
                    <div class="pagination-info">
                        {% blocktrans with current=page_obj.number total=page_obj.paginator.num_pages %}
                            Page {{ current }} of {{ total }}
                        {% endblocktrans %}
                    </div>

                    <div class="pagination-links">
                        {% if page_obj.has_previous %}
                            <a href="?page=1" class="pagination-link first">
                                {% trans "First" %}
                            </a>
                            <a href="?page={{ page_obj.previous_page_number }}" class="pagination-link prev">
                                ← {% trans "Previous" %}
                            </a>
                        {% endif %}

                        {% for num in page_obj.paginator.page_range %}
                            {% if page_obj.number == num %}
                                <span class="pagination-link current">{{ num }}</span>
                            {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                                <a href="?page={{ num }}" class="pagination-link">{{ num }}</a>
                            {% endif %}
                        {% endfor %}

                        {% if page_obj.has_next %}
                            <a href="?page={{ page_obj.next_page_number }}" class="pagination-link next">
                                {% trans "Next" %} →
                            </a>
                            <a href="?page={{ page_obj.paginator.num_pages }}" class="pagination-link last">
                                {% trans "Last" %}
                            </a>
                        {% endif %}
                    </div>
                </nav>
            {% endif %}
        </div>
    {% endblock %}

Custom Story Detail Template
=============================

Create an enhanced story detail view:

**templates/my_stories/post_detail.html:**

::

    {% extends "my_stories/base.html" %}
    {% load i18n cms_tags stories_tags meta_tags thumbnail %}

    {% block title %}{{ post.title }} - {{ block.super }}{% endblock %}
    {% block meta %}{{ post.as_meta }}{% endblock %}

    {% block extra_head %}
        <!-- Structured Data -->
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": "{{ post.title|escapejs }}",
            "author": {
                "@type": "Person",
                "name": "{{ post.author.get_full_name|default:post.author.username|escapejs }}"
            },
            "datePublished": "{{ post.date_published|date:'c' }}",
            "dateModified": "{{ post.date_modified|date:'c' }}",
            "description": "{{ post.abstract|default:post.title|escapejs }}",
            {% if post.main_image %}
                "image": "{{ request.scheme }}://{{ request.get_host }}{{ post.main_image.url }}",
            {% endif %}
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": "{{ request.build_absolute_uri }}"
            }
        }
        </script>
    {% endblock %}

    {% block stories_content %}
        <article class="story-detail">
            <!-- Story Header -->
            <header class="story-header">
                {% if post.categories.exists %}
                    <div class="story-categories">
                        {% for category in post.categories.all %}
                            <a href="{{ category.get_absolute_url }}" class="category-link">
                                {{ category.name }}
                            </a>
                        {% endfor %}
                    </div>
                {% endif %}

                <h1 class="story-title">{{ post.title }}</h1>

                {% if post.abstract %}
                    <p class="story-abstract">{{ post.abstract }}</p>
                {% endif %}

                <div class="story-meta">
                    <div class="meta-row">
                        <time datetime="{{ post.date_published|date:'c' }}" class="story-date">
                            {{ post.date_published|date:'F j, Y' }}
                        </time>

                        {% if post.author %}
                            <div class="story-author">
                                <span>{% trans "by" %}</span>
                                <strong>{{ post.author.get_full_name|default:post.author.username }}</strong>
                            </div>
                        {% endif %}

                        <span class="reading-time">{{ post.content|story_reading_time }} min read</span>
                    </div>
                </div>

                {% if post.main_image %}
                    <div class="story-featured-image">
                        {% thumbnail post.main_image 1200x600 crop quality=95 as thumb %}
                        <img src="{{ thumb.url }}" alt="{{ post.title }}">
                    </div>
                {% endif %}
            </header>

            <!-- Story Content -->
            <div class="story-content">
                {% render_placeholder post.content %}
            </div>

            <!-- Story Footer -->
            <footer class="story-footer">
                {% if post.tags.exists %}
                    <div class="story-tags">
                        <h4>{% trans "Tags" %}</h4>
                        <div class="tag-list">
                            {% for tag in post.tags.all %}
                                <a href="{% url 'djangocms_stories:posts-tagged' tag=tag.slug %}"
                                   class="tag-link">#{{ tag.name }}</a>
                            {% endfor %}
                        </div>
                    </div>
                {% endif %}

                <!-- Social Sharing -->
                <div class="social-sharing">
                    <h4>{% trans "Share this story" %}</h4>
                    <div class="share-buttons">
                        <a href="https://twitter.com/intent/tweet?url={{ request.build_absolute_uri|urlencode }}&text={{ post.title|urlencode }}"
                           target="_blank" class="share-twitter">Twitter</a>
                        <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.build_absolute_uri|urlencode }}"
                           target="_blank" class="share-facebook">Facebook</a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={{ request.build_absolute_uri|urlencode }}"
                           target="_blank" class="share-linkedin">LinkedIn</a>
                    </div>
                </div>
            </footer>
        </article>

        <!-- Related Stories -->
        {% get_related_posts post as related_posts %}
        {% if related_posts %}
            <section class="related-stories">
                <h2>{% trans "Related Stories" %}</h2>
                <div class="related-grid">
                    {% for related in related_posts %}
                        <article class="related-card">
                            {% if related.main_image %}
                                {% thumbnail related.main_image 300x200 crop as thumb %}
                                <img src="{{ thumb.url }}" alt="{{ related.title }}">
                            {% endif %}
                            <div class="related-content">
                                <h3><a href="{{ related.get_absolute_url }}">{{ related.title }}</a></h3>
                                <time>{{ related.date_published|date:'M j, Y' }}</time>
                            </div>
                        </article>
                    {% endfor %}
                </div>
            </section>
        {% endif %}
    {% endblock %}

Plugin Templates
================

Create custom templates for story plugins to match your design.

Custom Latest Entries Plugin
-----------------------------

**templates/my_stories/plugins/latest_entries.html:**

::

    {% load i18n cms_tags stories_tags thumbnail %}

    <div class="latest-stories-plugin">
        {% if instance.template_folder_name %}
            <h3 class="plugin-title">{{ instance.title|default:_("Latest Stories") }}</h3>
        {% endif %}

        <div class="latest-stories-list">
            {% for post in posts_list %}
                <article class="latest-story-item">
                    {% if post.main_image and instance.image %}
                        <div class="story-thumbnail">
                            {% thumbnail post.main_image 150x100 crop as thumb %}
                            <a href="{{ post.get_absolute_url }}">
                                <img src="{{ thumb.url }}" alt="{{ post.title }}">
                            </a>
                        </div>
                    {% endif %}

                    <div class="story-info">
                        <h4 class="story-title">
                            <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
                        </h4>

                        {% if instance.abstract %}
                            <p class="story-excerpt">{{ post.abstract|truncatewords:15 }}</p>
                        {% endif %}

                        <div class="story-date">
                            {{ post.date_published|date:'M j, Y' }}
                        </div>
                    </div>
                </article>
            {% endfor %}
        </div>

        {% if instance.more %}
            <div class="plugin-footer">
                <a href="{% url 'djangocms_stories:posts-latest' %}" class="view-all-link">
                    {% trans "View all stories" %} →
                </a>
            </div>
        {% endif %}
    </div>

Template Sets with STORIES_PLUGIN_TEMPLATE_FOLDERS
===================================================

Define multiple template sets for different plugin layouts:

**settings.py:**

::

    STORIES_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default template')),      # templates/my_stories/plugins/
        ('timeline', _('Timeline layout')),      # templates/my_stories/timeline/
        ('cards', _('Card layout')),             # templates/my_stories/cards/
        ('minimal', _('Minimal layout')),        # templates/my_stories/minimal/
    )

**Timeline Layout Example:**

**templates/my_stories/timeline/latest_entries.html:**

::

    {% load i18n cms_tags stories_tags %}

    <div class="timeline-stories">
        <div class="timeline-line"></div>
        {% for post in posts_list %}
            <div class="timeline-item {% cycle 'left' 'right' %}">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <time class="timeline-date">{{ post.date_published|date:'M Y' }}</time>
                    <h4><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h4>
                    {% if instance.abstract %}
                        <p>{{ post.abstract|truncatewords:20 }}</p>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    </div>

CSS for Custom Templates
=========================

Add styles to support your custom templates:

**static/css/stories-custom.css:**

::

    /* Stories Container */
    .stories-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }

    /* Stories Grid */
    .stories-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    /* Story Cards */
    .story-card {
        background: #fff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .story-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    /* Story Images */
    .story-image {
        position: relative;
        height: 250px;
        overflow: hidden;
    }

    .story-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .image-overlay {
        position: absolute;
        top: 1rem;
        left: 1rem;
    }

    .category-badge {
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        margin-right: 0.5rem;
    }

    /* Story Content */
    .story-content {
        padding: 1.5rem;
    }

    .story-title a {
        color: #2c3e50;
        text-decoration: none;
        font-weight: 600;
        line-height: 1.3;
    }

    .story-title a:hover {
        color: #3498db;
    }

    .story-abstract {
        color: #7f8c8d;
        margin: 1rem 0;
        line-height: 1.6;
    }

    /* Story Meta */
    .story-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.875rem;
        color: #95a5a6;
        margin: 1rem 0;
    }

    .story-meta time {
        font-weight: 500;
    }

    /* Tags */
    .story-tags, .tag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }

    .tag-link {
        background: #ecf0f1;
        color: #2c3e50;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        text-decoration: none;
        font-size: 0.875rem;
        transition: background-color 0.2s;
    }

    .tag-link:hover {
        background: #3498db;
        color: white;
    }

    /* Pagination */
    .pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 3rem 0;
        padding: 2rem 0;
        border-top: 1px solid #ecf0f1;
    }

    .pagination-links {
        display: flex;
        gap: 0.5rem;
    }

    .pagination-link {
        padding: 0.75rem 1rem;
        background: #ecf0f1;
        color: #2c3e50;
        text-decoration: none;
        border-radius: 6px;
        transition: all 0.2s;
    }

    .pagination-link:hover,
    .pagination-link.current {
        background: #3498db;
        color: white;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .stories-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }

        .story-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .pagination {
            flex-direction: column;
            gap: 1rem;
        }
    }

Template Override Priority
==========================

Template resolution follows this order:

1. **Project templates** (highest priority)
   ``your_project/templates/my_stories/post_list.html``

2. **App templates with prefix**
   ``djangocms_stories/templates/my_stories/post_list.html``

3. **Default app templates** (lowest priority)
   ``djangocms_stories/templates/djangocms_stories/post_list.html``

This allows you to override only specific templates while using defaults for others.

Best Practices
==============

1. **Start with copies** - Copy default templates and modify incrementally
2. **Use semantic CSS classes** - Make your templates maintainable
3. **Test responsive design** - Ensure templates work on all devices
4. **Optimize images** - Use appropriate thumbnail sizes
5. **Consider accessibility** - Add proper ARIA labels and semantic HTML
