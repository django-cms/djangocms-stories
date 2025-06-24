import pytest
from django.urls import reverse
from django.test import RequestFactory
from djangocms_stories.cms_appconfig import get_app_instance


@pytest.mark.django_db
def test_post_detail_view(client, post_content):
    from .factories import PostContentFactory

    related_post = PostContentFactory()
    post_content.post.related.add(related_post.post)

    url = reverse("djangocms_stories:post-detail", kwargs={"slug": post_content.slug})
    response = client.get(url)
    content = response.content.decode("utf-8")
    assert response.status_code == 200
    assert f'<article id="post-{post_content.slug}" class="post-item post-detail">' in content
    assert f"<h2>{post_content.title}</h2>" in content
    assert f"<h2>{post_content.title}</h2>" in content
    assert '<section class="post-detail-list">' in content
    assert f"<h4>{related_post.subtitle}</h4>" in content  # Subtitle appears in the related posts section


@pytest.mark.django_db
def test_post_detail_endpoint(admin_client, post_content):
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    related_post = PostContentFactory()
    post_content.post.related.add(related_post.post)

    url = get_object_preview_url(post_content)
    response = admin_client.get(url)
    content = response.content.decode("utf-8")
    assert response.status_code == 200
    assert f'<article id="post-{post_content.slug}" class="post-item post-detail">' in content
    assert f"<h2>{post_content.title}</h2>" in content
    assert f"<h2>{post_content.title}</h2>" in content
    assert '<section class="post-detail-list">' in content
    assert f"<h4>{related_post.subtitle}</h4>" in content  # Subtitle appears in the related posts section


@pytest.mark.django_db
def test_post_list_view_queryset(admin_client, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from djangocms_stories.views import PostListView
    from .factories import PostContentFactory

    PostContentFactory.create_batch(5, post__app_config=default_config)

    request = RequestFactory().get(reverse("djangocms_stories:posts-latest"))
    namespace, config = get_app_instance(request)
    view = PostListView(
        request=request,
        namespace=namespace,
        config=config,
    )
    qs = view.get_queryset()
    assert qs.count() == 5


@pytest.mark.django_db
def test_post_list_view(admin_client, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)

    url = reverse("djangocms_stories:posts-latest")
    response = admin_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert '<section class="blog-list"' in content
    assert '<p class="blog-empty">No article found.</p>' not in content

    # Check that the post_content appears in the list
    for post_content in post_contents:
        absolute_url = post_content.get_absolute_url()
        assert f'<article id="post-{post_content.slug}" class="post-item">' in content
        assert f'<h3><a href="{absolute_url}">{post_content.title}</a></h3>' in content


@pytest.mark.django_db
def test_post_archive_view(admin_client, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)

    url = reverse("djangocms_stories:posts-archive", kwargs={"year": post_contents[0].post.date_published.year})
    response = admin_client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert '<section class="blog-list"' in content
    assert '<p class="blog-empty">No article found.</p>' not in content

    # Check that the post_content appears in the list
    for post_content in post_contents:
        if post_content.post.date_published.year != post_contents[0].post.date_published.year:
            assert f'<article id="post-{post_content.slug}" class="post-item">' not in content
            continue
        absolute_url = post_content.get_absolute_url()
        assert f'<article id="post-{post_content.slug}" class="post-item">' in content
        assert f'<h3><a href="{absolute_url}">{post_content.title}</a></h3>' in content


@pytest.mark.django_db
def test_post_author_view(admin_client, default_config, assert_html_in_response):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    author = post_contents[0].post.author
    post_contents[-1].post.author = author
    post_contents[-1].post.save()

    url = reverse("djangocms_stories:posts-author", kwargs={"username": author.username})
    response = admin_client.get(url)
    content = response.content.decode("utf-8")

    assert '<section class="blog-list">' in content
    assert_html_in_response(f"<h2> Articles by {author.get_full_name()} </h2>", response)
    assert '<p class="blog-empty">No article found.</p>' not in content

    # Check that the post_content appears in the list
    for post_content in post_contents:
        if post_content.post.author != author:
            assert f'<article id="post-{post_content.slug}" class="post-item">' not in content
            continue
        absolute_url = post_content.get_absolute_url()
        assert f'<article id="post-{post_content.slug}" class="post-item">' in content
        assert f'<h3><a href="{absolute_url}">{post_content.title}</a></h3>' in content


@pytest.mark.django_db
def test_post_category_view(client, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostCategoryFactory, PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    category = PostCategoryFactory(app_config=default_config)
    for post_content in post_contents:
        post_content.post.categories.add(category)

    url = reverse("djangocms_stories:posts-category", kwargs={"category": category.slug})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert '<section class="blog-list"' in content
    assert '<p class="blog-empty">No article found.</p>' not in content

    # Check that the post_content appears in the list
    for post_content in post_contents:
        absolute_url = post_content.get_absolute_url()
        assert f'<article id="post-{post_content.slug}" class="post-item">' in content
        assert f'<h3><a href="{absolute_url}">{post_content.title}</a></h3>' in content


@pytest.mark.django_db
def test_post_category_list_view(client, default_config, assert_html_in_response):
    """
    Test the PostCategoryListView returns a list of categories and renders expected content.
    """
    from .factories import PostCategoryFactory

    categories = PostCategoryFactory.create_batch(5, app_config=default_config)

    url = reverse("djangocms_stories:categories-all")
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert '<section class="blog-list">' in content
    assert '<p class="blog-empty">No article found.</p>' not in content

    # Check that the categories appear in the list
    for category in categories:
        assert_html_in_response(f'<section id="category-{category.slug}" class="category-item">', response)
        assert_html_in_response(f'<div class="category-header"><h3>{category.name}</h3></div>', response)
