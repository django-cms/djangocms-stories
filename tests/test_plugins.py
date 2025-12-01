import pytest
from cms.toolbar.utils import get_object_preview_url
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.lorem_ipsum import words

from .utils import publish_if_necessary


@pytest.fixture
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
        from djangocms_versioning.constants import PUBLISHED

        version, _ = Version.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_content),
            object_id=page_content.pk,
            created_by=admin_user,
            state=PUBLISHED,
        )
    return page_content


@pytest.fixture
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
    import random

    from cms import api

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
        if post_content.post in featured:
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

    if apps.is_installed("djangocms_versioning"):
        from django.test import Client

        # No posts are published yet, so the featured posts should not appear on the site
        url = placeholder.source.get_absolute_url("en")
        response = Client().get(url)

        assert response.status_code == 200
        assert_html_in_response('<p class="blog-empty">No article found.</p>', response)
        for post_content in batch:
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


@pytest.mark.django_db
def test_latest_posts_plugin_str(placeholder, simple_w_placeholder):
    """Test __str__ method of LatestPostsPlugin."""
    from cms import api

    plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=10,
    )
    instance = plugin.get_plugin_instance()[0]
    assert str(instance) == "10 latest posts by tag"


@pytest.mark.django_db
def test_latest_posts_plugin_copy_relations(placeholder, simple_w_placeholder):
    """Test copy_relations method of LatestPostsPlugin."""
    from cms import api

    from .factories import PostCategoryFactory, PostContentFactory

    # Create categories and posts
    categories = PostCategoryFactory.create_batch(3, app_config=simple_w_placeholder)
    PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)

    # Create original plugin with tags and categories
    plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=5,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.tags.add("test-tag", "another-tag", "third-tag")
    instance.categories.add(*categories)

    # Verify original instance has tags and categories
    assert instance.tags.count() == 3
    assert instance.categories.count() == 3

    # Create new plugin and copy relations
    new_plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=5,
    )
    new_instance = new_plugin.get_plugin_instance()[0]
    new_instance.copy_relations(instance)

    # Verify new instance has same tags and categories
    assert new_instance.tags.count() == 3
    assert set(new_instance.tags.names()) == set(instance.tags.names())
    assert new_instance.categories.count() == 3
    assert set(new_instance.categories.all()) == set(instance.categories.all())


@pytest.mark.django_db
def test_author_entries_plugin_str(placeholder, simple_w_placeholder):
    """Test __str__ method of AuthorEntriesPlugin."""
    from cms import api

    plugin = api.add_plugin(
        placeholder,
        "BlogAuthorPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=7,
    )
    instance = plugin.get_plugin_instance()[0]
    assert str(instance) == "7 latest entries by author"


@pytest.mark.django_db
def test_author_entries_plugin_copy_relations(placeholder, simple_w_placeholder, admin_user):
    """Test copy_relations method of AuthorEntriesPlugin."""
    from cms import api
    from django.contrib.auth import get_user_model

    from .factories import PostContentFactory

    User = get_user_model()

    # Create additional users
    users = [User.objects.create_user(username=f"user{i}", email=f"user{i}@example.com") for i in range(3)]
    users.append(admin_user)

    # Create posts by different authors (set author on Post, not PostContent)
    for user in users:
        PostContentFactory.create_batch(2, language="en", post__app_config=simple_w_placeholder, post__author=user)

    # Create original plugin with authors
    plugin = api.add_plugin(
        placeholder,
        "BlogAuthorPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=5,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.authors.add(*users[:2])

    # Verify original instance has authors
    assert instance.authors.count() == 2

    # Create new plugin and copy relations
    new_plugin = api.add_plugin(
        placeholder,
        "BlogAuthorPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
        latest_posts=5,
    )
    new_instance = new_plugin.get_plugin_instance()[0]
    new_instance.copy_relations(instance)

    # Verify new instance has same authors
    assert new_instance.authors.count() == 2
    assert set(new_instance.authors.all()) == set(instance.authors.all())


@pytest.mark.django_db
def test_featured_posts_plugin_str(placeholder, simple_w_placeholder):
    """Test __str__ method of FeaturedPostsPlugin."""
    from cms import api

    plugin = api.add_plugin(
        placeholder,
        "BlogFeaturedPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    assert str(instance) == "Featured posts"


@pytest.mark.django_db
def test_featured_posts_plugin_copy_relations(placeholder, simple_w_placeholder):
    """Test copy_relations method of FeaturedPostsPlugin."""
    from cms import api

    from .factories import PostContentFactory

    # Create posts
    batch = PostContentFactory.create_batch(5, language="en", post__app_config=simple_w_placeholder)
    posts = [post_content.post for post_content in batch]

    # Create original plugin with featured posts
    plugin = api.add_plugin(
        placeholder,
        "BlogFeaturedPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    instance.posts.add(*posts[:3])

    # Verify original instance has posts
    assert instance.posts.count() == 3

    # Create new plugin and copy relations
    new_plugin = api.add_plugin(
        placeholder,
        "BlogFeaturedPostsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    new_instance = new_plugin.get_plugin_instance()[0]
    new_instance.copy_relations(instance)

    # Verify new instance has same posts
    assert new_instance.posts.count() == 3
    assert set(new_instance.posts.all()) == set(instance.posts.all())


@pytest.mark.django_db
def test_generic_blog_plugin_str(placeholder, simple_w_placeholder):
    """Test __str__ method of GenericBlogPlugin."""
    from cms import api

    plugin = api.add_plugin(
        placeholder,
        "BlogTagsPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    assert str(instance) == "generic blog plugin"


@pytest.mark.django_db
def test_stories_plugin_get_fields_single_template_folder(placeholder, simple_w_placeholder):
    """Test get_fields doesn't add template_folder when only one folder configured."""
    from cms import api
    from djangocms_stories.cms_plugins import BlogLatestEntriesPlugin
    from django.test import RequestFactory
    from unittest.mock import patch

    plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    plugin_class = BlogLatestEntriesPlugin(instance.get_plugin_class(), instance)
    request = RequestFactory().get("/")

    # Mock get_setting to return single template folder
    with patch("djangocms_stories.cms_plugins.get_setting") as mock_get_setting:
        mock_get_setting.return_value = ["default"]
        fields = plugin_class.get_fields(request, instance)

        # template_folder should not be in fields
        assert "template_folder" not in fields
        assert "app_config" in fields


@pytest.mark.django_db
def test_stories_plugin_get_fields_multiple_template_folders(placeholder, simple_w_placeholder):
    """Test get_fields adds template_folder when multiple folders configured."""
    from cms import api
    from djangocms_stories.cms_plugins import BlogLatestEntriesPlugin
    from django.test import RequestFactory
    from unittest.mock import patch

    plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    plugin_class = BlogLatestEntriesPlugin(instance.get_plugin_class(), instance)
    request = RequestFactory().get("/")

    # Mock get_setting to return multiple template folders
    with patch("djangocms_stories.cms_plugins.get_setting") as mock_get_setting:
        mock_get_setting.return_value = ["default", "custom"]
        fields = plugin_class.get_fields(request, instance)

        # template_folder should be in fields
        assert "template_folder" in fields
        assert "app_config" in fields


@pytest.mark.django_db
def test_stories_plugin_get_fields_repeated_calls(placeholder, simple_w_placeholder):
    """Test that repeated calls to get_fields don't add template_folder multiple times."""
    from cms import api
    from djangocms_stories.cms_plugins import BlogLatestEntriesPlugin
    from django.test import RequestFactory
    from unittest.mock import patch

    plugin = api.add_plugin(
        placeholder,
        "BlogLatestEntriesPlugin",
        "en",
        app_config=simple_w_placeholder,
    )
    instance = plugin.get_plugin_instance()[0]
    plugin_class = BlogLatestEntriesPlugin(instance.get_plugin_class(), instance)
    request = RequestFactory().get("/")

    # Mock get_setting to return multiple template folders
    with patch("djangocms_stories.cms_plugins.get_setting") as mock_get_setting:
        mock_get_setting.return_value = ["default", "custom"]

        # Call get_fields multiple times
        fields1 = plugin_class.get_fields(request, instance)
        fields2 = plugin_class.get_fields(request, instance)
        fields3 = plugin_class.get_fields(request, instance)

        # All calls should return the same result
        assert fields1 == fields2 == fields3

        # Count how many times template_folder appears in the result
        template_folder_count = fields3.count("template_folder")
        assert template_folder_count == 1, f"template_folder appears {template_folder_count} times, expected 1"

        # Verify all expected fields are present
        assert "app_config" in fields1
        assert "latest_posts" in fields1
        assert "tags" in fields1
        assert "categories" in fields1
        assert "template_folder" in fields1
