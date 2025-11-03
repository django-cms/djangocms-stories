"""
Comprehensive tests for djangocms_stories template tags.

Tests cover:
- namespace_url: URL generation with namespace
- media_plugins: Extract media plugins from placeholder
- media_images: Extract images from media plugins
- absolute_url (GetAbsoluteUrl): Get URL for post content in different toolbar modes

All tests include actual template rendering to ensure real-world usage works.
Uses page_with_menu fixture to ensure URL patterns are properly registered.
"""

import pytest
from cms.api import add_plugin
from cms.toolbar.toolbar import CMSToolbar
from django.template import Context, Template
from django.test import RequestFactory


# Tests for namespace_url


@pytest.mark.django_db
def test_namespace_url_basic(page_with_menu, many_posts):
    """Test basic namespace_url tag usage with registered namespace"""
    request = RequestFactory().get("/")
    post_content = many_posts[0]
    namespace = post_content.post.app_config.namespace

    template = Template("{% load djangocms_stories %}{% namespace_url 'posts-latest' namespace=namespace %}")
    context = Context({"request": request, "namespace": namespace})

    rendered = template.render(context).strip()
    # Should return a valid URL
    assert rendered.startswith("/")
    assert len(rendered) > 1


@pytest.mark.django_db
def test_namespace_url_with_args(page_with_menu, many_posts):
    """Test namespace_url with positional arguments"""
    request = RequestFactory().get("/")
    post_content = many_posts[0]
    namespace = post_content.post.app_config.namespace
    slug = post_content.slug
    year = post_content.post.date_published.year
    month = post_content.post.date_published.month
    day = post_content.post.date_published.day

    template = Template(
        "{% load djangocms_stories %}{% namespace_url 'post-detail' year month day slug namespace=namespace %}"
    )
    context = Context(
        {"request": request, "namespace": namespace, "slug": slug, "year": year, "month": month, "day": day}
    )

    rendered = template.render(context).strip()
    assert slug in rendered
    assert rendered.startswith("/")


@pytest.mark.django_db
def test_namespace_url_in_link(page_with_menu, many_posts):
    """Test namespace_url usage within an anchor tag"""
    request = RequestFactory().get("/")
    namespace = many_posts[0].post.app_config.namespace

    template = Template(
        "{% load djangocms_stories %}"
        "<a href=\"{% namespace_url 'posts-latest' namespace=namespace %}\">Latest Posts</a>"
    )
    context = Context({"request": request, "namespace": namespace})

    rendered = template.render(context).strip()
    assert "<a href=" in rendered
    assert ">Latest Posts</a>" in rendered
    assert 'href="/' in rendered


# Tests for media_plugins


@pytest.mark.django_db
def test_media_plugins_with_no_media_placeholder(page_with_menu, many_posts):
    """Test media_plugins returns empty list when post has no media placeholder"""
    request = RequestFactory().get("/")
    post_content = many_posts[0]
    # Ensure no media placeholder
    post_content.media = None
    post_content.save()

    template = Template("{% load djangocms_stories %}{% media_plugins post_content as plugins %}{{ plugins|length }}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    assert rendered == "0"


@pytest.mark.django_db
def test_media_plugins_with_empty_placeholder(page_with_menu, default_config):
    """Test media_plugins returns empty list when media placeholder has no plugins"""
    from tests.factories import PostContentFactory, PostFactory

    request = RequestFactory().get("/")
    post = PostFactory(app_config=default_config)
    post_content = PostContentFactory(post=post, language="en")

    template = Template("{% load djangocms_stories %}{% media_plugins post_content as plugins %}{{ plugins|length }}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    assert rendered == "0"


@pytest.mark.django_db
def test_media_plugins_with_plugins(page_with_menu, default_config):
    """Test media_plugins extracts plugins from media placeholder"""
    from tests.factories import PostContentFactory, PostFactory

    request = RequestFactory().get("/")
    post = PostFactory(app_config=default_config)
    post_content = PostContentFactory(post=post, language="en")

    # Add plugins to media placeholder
    add_plugin(post_content.media, "TextPlugin", "en", body="Test text")
    add_plugin(post_content.media, "TextPlugin", "en", body="Another plugin")

    template = Template("{% load djangocms_stories %}{% media_plugins post_content as plugins %}{{ plugins|length }}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    assert rendered == "2"


# Tests for media_images


@pytest.mark.django_db
def test_media_images_with_no_plugins(page_with_menu, many_posts):
    """Test media_images returns empty list when no media plugins exist"""
    request = RequestFactory().get("/")
    post_content = many_posts[0]
    post_content.media = None
    post_content.save()

    template = Template("{% load djangocms_stories %}{% media_images post_content as images %}{{ images|length }}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    assert rendered == "0"


# Tests for absolute_url (GetAbsoluteUrl)


@pytest.mark.django_db
def test_absolute_url_basic(page_with_menu, many_posts):
    """Test absolute_url tag returns post content URL"""
    request = RequestFactory().get("/")
    request.toolbar = None  # No toolbar
    post_content = many_posts[0]

    template = Template("{% load djangocms_stories %}{% absolute_url post_content %}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    # Should contain the URL path
    assert rendered
    assert "/" in rendered


@pytest.mark.django_db
def test_absolute_url_with_language(page_with_menu, many_posts):
    """Test absolute_url tag with explicit language parameter"""
    request = RequestFactory().get("/")
    request.toolbar = None
    post_content = many_posts[0]

    template = Template('{% load djangocms_stories %}{% absolute_url post_content "en" %}')
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    # Should render without error
    assert rendered
    assert "/" in rendered


@pytest.mark.django_db
def test_absolute_url_as_variable(page_with_menu, many_posts):
    """Test absolute_url tag storing result in variable"""
    request = RequestFactory().get("/")
    request.toolbar = None
    post_content = many_posts[0]

    template = Template(
        "{% load djangocms_stories %}"
        "{% absolute_url post_content as post_url %}"
        '<a href="{{ post_url }}">{{ post_content.title }}</a>'
    )
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    # Should contain link with title
    assert "<a href=" in rendered
    assert post_content.title in rendered


@pytest.mark.django_db
def test_absolute_url_with_edit_mode(page_with_menu, many_posts):
    """Test absolute_url returns admin edit URL when toolbar in edit mode"""
    from django.contrib.auth.models import AnonymousUser

    request = RequestFactory().get("/")
    request.user = AnonymousUser()  # Add user to request
    request.session = {}  # Add session
    toolbar = CMSToolbar(request)
    toolbar.edit_mode_active = True
    toolbar.preview_mode_active = False
    request.toolbar = toolbar
    post_content = many_posts[0]

    template = Template("{% load djangocms_stories %}{% absolute_url post_content %}")
    context = Context({"request": request, "post_content": post_content})

    rendered = template.render(context).strip()
    # In edit mode, should return admin URL
    assert "admin" in rendered or "cms" in rendered
    assert str(post_content.pk) in rendered


@pytest.mark.django_db
def test_absolute_url_with_none_post_content(page_with_menu):
    """Test absolute_url handles None gracefully"""
    request = RequestFactory().get("/")
    request.toolbar = None

    template = Template(
        "{% load djangocms_stories %}{% absolute_url post_content %}{% if not post_content %}EMPTY{% endif %}"
    )
    context = Context({"request": request, "post_content": None})

    rendered = template.render(context).strip()
    # Should return empty string and show EMPTY
    assert rendered.endswith("EMPTY")


# Integration tests


@pytest.mark.django_db
def test_multiple_tags_together(page_with_menu, many_posts):
    """Test using multiple template tags in the same template"""
    request = RequestFactory().get("/")
    request.toolbar = None
    post_content = many_posts[0]
    namespace = post_content.post.app_config.namespace

    template = Template(
        "{% load djangocms_stories %}"
        '<a href="{% absolute_url post_content %}">{{ post_content.title }}</a>'
        "{% media_plugins post_content as plugins %}"
        "{% media_images post_content as images %}"
        "<a href=\"{% namespace_url 'posts-latest' namespace=namespace %}\">All Posts</a>"
    )
    context = Context({"request": request, "post_content": post_content, "namespace": namespace})

    rendered = template.render(context).strip()
    # Should render all tags without conflict
    assert post_content.title in rendered
    assert "<a href=" in rendered


@pytest.mark.django_db
def test_template_tags_in_loop(page_with_menu, many_posts):
    """Test template tags work correctly within loops"""
    request = RequestFactory().get("/")
    request.toolbar = None
    post_contents = many_posts[:3]

    template = Template(
        "{% load djangocms_stories %}"
        "{% for post in posts %}"
        '<li><a href="{% absolute_url post %}">{{ post.title }}</a></li>'
        "{% endfor %}"
    )
    context = Context({"request": request, "posts": post_contents})

    rendered = template.render(context).strip()
    # Should render all posts
    for post in post_contents:
        assert post.title in rendered
    assert rendered.count("<li>") == 3
