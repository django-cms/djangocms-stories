from datetime import timedelta
from django.utils.timezone import now
import pytest
from django.apps import apps
from django.test import RequestFactory
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import now

from djangocms_stories.cms_appconfig import get_app_instance

from .utils import publish_if_necessary


@pytest.mark.django_db
def test_post_detail_view(client, admin_user, post_content, assert_html_in_response):
    from .factories import PostContentFactory

    related_post = PostContentFactory()
    post_content.post.related.add(related_post.post)
    publish_if_necessary([post_content, related_post], admin_user)

    url = reverse("djangocms_stories:post-detail", kwargs={"slug": post_content.slug})
    response = client.get(url)

    assert_html_in_response(f'<article id="post-{post_content.slug}" class="post-item post-detail">', response)
    assert_html_in_response(f"<h2>{post_content.title}</h2>", response)  # Title appears in the post detail
    assert_html_in_response('<section class="post-detail-list">', response)
    assert_html_in_response(
        f"<h4>{related_post.subtitle}</h4>", response
    )  # Subtitle appears in the related posts section
    # meta:
    assert_html_in_response(f'<meta property="og:title" content="{post_content.meta_title}">', response)
    assert_html_in_response(f'<meta name="description" content="{post_content.meta_description}">', response)


@pytest.mark.django_db
def test_post_detail_endpoint(admin_client, admin_user, post_content):
    from cms.toolbar.utils import get_object_preview_url

    from .factories import PostContentFactory

    related_post = PostContentFactory()
    post_content.post.related.add(related_post.post)
    publish_if_necessary([related_post], admin_user)

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
    assert qs.count() == 0 if apps.is_installed("djangocms_versioning") else 5


@pytest.mark.django_db
def test_post_list_view(admin_client, admin_user, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    publish_if_necessary(post_contents, admin_user)

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
def test_post_list_view_filters_by_publication_date_end(client, admin_user, default_config):
    """
    Test the PostListView returns a list of posts within the date_published and date_published_end window.
    """
    from .factories import PostContentFactory

    current_time = now()

    visible_post = PostContentFactory(
        title="Visible Post",
        post__app_config=default_config,
        post__date_published=current_time - timedelta(days=2),
    )

    expired_post = PostContentFactory(
        title="Expired Post",
        post__app_config=default_config,
        post__date_published=current_time - timedelta(days=10),
        post__date_published_end=current_time - timedelta(days=1),
    )

    future_post = PostContentFactory(
        title="Future Post",
        post__app_config=default_config,
        post__date_published=current_time + timedelta(days=10),
    )

    publish_if_necessary([visible_post, expired_post, future_post], admin_user)

    url = reverse("djangocms_stories:posts-latest")

    # Use client to simulate public visitor.
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert visible_post.title in content
    assert expired_post.title not in content
    assert future_post.title not in content


@pytest.mark.django_db
def test_post_list_view_ordering_fallback(client, admin_user, default_config):
    """
    Test that posts without date_published fall back to date_created for sorting.
    """
    from .factories import PostContentFactory

    # Post published one day ago from now.
    post_a = PostContentFactory(
        title="Post A",
        post__app_config=default_config,
        post__date_published=now() - timedelta(days=1),
    )

    # Post without published date, created 5 days ago from now.
    post_b = PostContentFactory(
        title="Post B",
        post__app_config=default_config,
        post__date_published=None,
        post__date_created=now() - timedelta(days=5),
    )

    publish_if_necessary([post_a, post_b], admin_user)

    url = reverse("djangocms_stories:posts-latest")
    response = client.get(url)
    content = response.content.decode("utf-8")

    assert "Post A" in content
    assert "Post B" in content
    assert content.find("Post B") < content.find("Post A")


@pytest.mark.django_db
def test_post_archive_view(admin_client, admin_user, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    publish_if_necessary(post_contents, admin_user)

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
def test_post_tagged_view(client, admin_user, default_config, assert_html_in_response):
    """
    Test the PostTaggedView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(3, post__app_config=default_config)
    post_contents[0].post.tags.add("other")
    post_contents[1].post.tags.add("test tag")
    publish_if_necessary(post_contents, admin_user)

    url = reverse("djangocms_stories:posts-tagged", kwargs={"tag": "test-tag"})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")

    assert '<section class="blog-list">' in content

    assert_html_in_response("<h2> Tag &ndash; Test-tag </h2>", response)
    assert post_contents[0].title not in content
    assert post_contents[1].title in content
    assert post_contents[2].title not in content


@pytest.mark.django_db
def test_post_author_view(admin_client, admin_user, default_config, assert_html_in_response):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    author = post_contents[0].post.author
    post_contents[-1].post.author = author
    post_contents[-1].post.save()
    publish_if_necessary(post_contents, admin_user)

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
def test_post_category_view(client, admin_user, default_config):
    """
    Test the PostListView returns a list of posts and renders expected content.
    """
    from .factories import PostCategoryFactory, PostContentFactory

    post_contents = PostContentFactory.create_batch(5, post__app_config=default_config)
    category = PostCategoryFactory(app_config=default_config)
    for post_content in post_contents:
        post_content.post.categories.add(category)
    publish_if_necessary(post_contents, admin_user)

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
    # meta:
    assert f'<meta property="og:title" content="{category.name}">' in content
    assert f'<meta name="description" content="{category.meta_description}">' in content


@pytest.mark.django_db
def test_post_category_view_404(client, default_config):
    url = reverse("djangocms_stories:posts-category", kwargs={"category": "This-Category-Does-Not-Exist"})
    response = client.get(url)
    assert response.status_code == 404


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


@pytest.mark.django_db
def test_post_detail_view_same_slug_different_languages(client, admin_user, default_config):
    """
    Two PostContent objects with the same slug but different languages
    should each return the correct content for their respective language.
    """
    from djangocms_stories.models import Post

    from .factories import PostContentFactory, UserFactory

    post = Post.objects.create(
        app_config=default_config,
        author=UserFactory(),
        date_published=now(),
    )

    en_content = PostContentFactory(
        post=post,
        language="en",
        title="English Title",
        subtitle="English Subtitle",
        slug="shared-slug",
        meta_title="English Meta Title",
        meta_description="English meta description.",
    )
    fr_content = PostContentFactory(
        post=post,
        language="fr",
        title="Titre Français",
        subtitle="Sous-titre Français",
        slug="shared-slug",
        meta_title="Titre Méta Français",
        meta_description="Description méta française.",
    )

    publish_if_necessary([en_content, fr_content], admin_user)

    # Build URL using the post's date and the shared slug
    date = post.date
    url_kwargs = {
        "year": date.year,
        "month": "%02d" % date.month,
        "day": "%02d" % date.day,
        "slug": "shared-slug",
    }

    # Request the English version (reverse with 'en' language gives /en/blog/...)
    with translation.override("en"):
        en_url = reverse("djangocms_stories:post-detail", kwargs=url_kwargs)
    en_response = client.get(en_url)
    assert en_response.status_code == 200
    en_body = en_response.content.decode("utf-8")
    assert "English Title" in en_body
    assert "Titre Français" not in en_body

    # Request the French version
    with translation.override("fr"):
        fr_url = reverse("djangocms_stories:post-detail", kwargs=url_kwargs)
    fr_response = client.get(fr_url)
    assert fr_response.status_code == 200
    fr_body = fr_response.content.decode("utf-8")
    assert "Titre Français" in fr_body
    assert "English Title" not in fr_body
