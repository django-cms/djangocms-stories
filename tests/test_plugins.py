import pytest

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.lorem_ipsum import words

from cms.toolbar.utils import get_object_preview_url

from .utils import publish_if_necessary


@pytest.fixture
@pytest.mark.django_db
def page_content(admin_user):
    from cms import api
    from cms.models import PageContent

    page = api.create_page(
        title="Test Page",
        template="base.html",
        language="en",
    )
    page_content = PageContent.admin_manager.get(page=page, language="en")
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.models import Version

        Version.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_content),
            object_id=page_content.pk,
            created_by=admin_user,
        )
    return page_content


@pytest.fixture
@pytest.mark.django_db
def placeholder(page_content):
    from cms.api import add_plugin
    from cms.models import Placeholder

    placeholder, _ = Placeholder.objects.get_or_create(slot="content")
    placeholder.source = page_content
    placeholder.save()
    placeholder.clear()  # Clear existing plugins
    add_plugin(placeholder, "TextPlugin", "en", body="<p>TextPlugin works.</p>")
    return placeholder


@pytest.mark.django_db
def test_blog_latest_entries_plugin(
    placeholder, admin_client, admin_user, simple_w_placeholder, assert_html_in_response
):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)
    assert_html_in_response('<p class="blog-empty">No article found.</p>', response)

    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)
    publish_if_necessary(batch, admin_user)
    response = admin_client.get(url)
    for post_content in batch:
        assert_html_in_response(
            post_content.title,
            response,
        )
        assert_html_in_response(
            post_content.abstract,
            response,
        )


@pytest.mark.django_db
def test_blog_featured_posts_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    import random
    from .factories import PostContentFactory

    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)

    plugin = api.add_plugin(
        placeholder,
        "BlogFeaturedPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.posts.add(*[post_content.post for post_content in batch if random.choice([True, False])])
    instance.posts.add(batch[0].post)  # Ensure at least one post is featured
    featured = instance.posts.all()

    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)

    for post_content in batch:
        if post_content in featured:
            assert_html_in_response(
                post_content.title,
                response,
            )
            assert_html_in_response(
                post_content.abstract,
                response,
            )
        else:
            assert post_content.title not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_blog_author_posts_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)
    authors = [batch[0].author, batch[1].author]

    plugin = api.add_plugin(
        placeholder,
        "BlogAuthorPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.authors.add(batch[0].author)
    instance.authors.add(batch[1].author)

    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)

    for author in authors:
        assert_html_in_response(author.get_full_name(), response)
        assert_html_in_response(authors[0].username, response)


@pytest.mark.django_db
def test_blog_author_post_list_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)
    authors = [batch[0].author, batch[1].author]

    plugin = api.add_plugin(
        placeholder,
        "BlogAuthorPostsListPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.authors.add(batch[0].author)
    instance.authors.add(batch[1].author)

    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)

    assert_html_in_response(
        f"<h3>Articles by {authors[0].get_full_name()}</h3>",
        response,
    )
    assert_html_in_response(
        authors[1].get_full_name(),
        response,
    )


@pytest.mark.django_db
def test_blog_tags_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)
    tags = {"test-tag": len(batch)}
    for post_content in batch:
        word = words(1, common=False)
        tags[word] = tags.get(word, 0) + 1
        post_content.post.tags.add("test-tag", word)

    api.add_plugin(
        placeholder,
        "BlogTagsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )

    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)

    for tag, count in tags.items():
        assert_html_in_response(
            f"""<a href="{reverse("djangocms_stories:posts-tagged", args=[tag])}" class="blog-tag-{count}">
               {tag} <span> ({count} article{"s" if count != 1 else ""}) </span>
            </a>""",
            response,
        )


@pytest.mark.django_db
def test_blog_category_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostCategoryFactory

    batch = PostCategoryFactory.create_batch(5, app_config=simple_w_placeholder)

    api.add_plugin(
        placeholder,
        "BlogCategoryPlugin",
        "en",
        app_config=simple_w_placeholder,
    )

    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)

    for category in batch:
        assert_html_in_response(
            reverse("djangocms_stories:posts-category", args=[category.slug]),
            response,
        )
        assert category.name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_blog_archive_plugin(placeholder, admin_client, simple_w_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from .factories import PostContentFactory

    api.add_plugin(
        placeholder,
        "BlogArchivePlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    url = get_object_preview_url(placeholder.source)

    response = admin_client.get(url)
    assert_html_in_response("<p>TextPlugin works.</p>", response)
    assert_html_in_response("<p>No article found.</p>", response)

    post_content = PostContentFactory(language="en", post__app_config=simple_w_placeholder)
    post = post_content.post
    response = admin_client.get(url)

    assert_html_in_response(f'<a href="/en/blog/{post.date_featured.year}/{post.date_featured.month}/">', response)
    assert_html_in_response("<span>( 1 article )</span>", response)
