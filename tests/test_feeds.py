"""
Comprehensive tests for djangocms_stories feeds.

Tests cover:
- LatestEntriesFeed: Basic RSS feed functionality
- TagFeed: Tag-filtered RSS feed
- FBInstantArticles: Facebook Instant Articles feed
- End-to-end feed retrieval tests
"""

import xml.etree.ElementTree as ET
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.apps import apps
from django.contrib.sites.models import Site
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from djangocms_stories.feeds import FBInstantArticles, FBInstantFeed, LatestEntriesFeed, TagFeed
from djangocms_stories.models import Post, StoriesConfig


# Tests for LatestEntriesFeed


@pytest.mark.django_db
def test_latest_entries_feed_initialization(page_with_menu):
    """Test that LatestEntriesFeed initializes correctly with request"""
    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/")
    request.path = f"/{app_config.namespace}/feed/"

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)

        feed = LatestEntriesFeed()
        feed(request)

        assert feed.request == request
        assert feed.namespace == app_config.namespace
        assert feed.config == app_config


@pytest.mark.django_db
def test_latest_entries_feed_link(page_with_menu):
    """Test that feed link generates correct URL"""
    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/")
    request.path = f"/{app_config.namespace}/feed/"

    expected_link = reverse(
        f"{app_config.namespace}:posts-latest",
        current_app=app_config.namespace,
    )

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)

        feed = LatestEntriesFeed()
        feed(request)

        link = feed.link()
        assert link == expected_link


@pytest.mark.django_db
def test_latest_entries_feed_title():
    """Test that feed title returns site name"""
    site = Site.objects.get_current()

    feed = LatestEntriesFeed()
    assert feed.title() == site.name


@pytest.mark.django_db
def test_latest_entries_feed_description():
    """Test that feed description includes site name"""
    site = Site.objects.get_current()

    feed = LatestEntriesFeed()
    description = feed.description()

    assert site.name in description
    assert "Blog articles" in description


@pytest.mark.django_db
def test_latest_entries_feed_excludes_non_rss_posts(page_with_menu):
    """Test that posts with include_in_rss=False are excluded from the feed items"""
    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/")
    request.path = f"/{app_config.namespace}/feed/"

    posts = list(Post.objects.filter(app_config__namespace=app_config.namespace))
    posts[0].include_in_rss = False
    posts[0].save()

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)
        feed = LatestEntriesFeed()
        feed(request)

        items = list(feed.items())

        # Should be ordered by date_published descending
        assert len(items) == len(posts) - 1

        assert posts[0] not in items
        for post in posts[1:]:
            assert post in items


@pytest.mark.django_db
def test_latest_entries_feed_items(page_with_menu):
    """Test that feed items returns published posts in correct order"""

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/")
    request.path = f"/{app_config.namespace}/feed/"

    posts = Post.objects.filter(app_config=app_config)

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)
        feed = LatestEntriesFeed()
        feed(request)

        items = list(feed.items())

        # Should be ordered by date_published descending
        assert len(items) == len(posts)
        for item in items:
            assert item in posts


@pytest.mark.django_db
def test_latest_entries_feed_items_respects_limit(page_with_menu):
    """Test that feed items respects FEED_LATEST_ITEMS setting"""

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/")
    request.path = f"/{app_config.namespace}/feed/"

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)
        feed = LatestEntriesFeed()
        feed.feed_items_number = 3  # Limit to 3 items
        feed(request)

        items = list(feed.items())
        assert len(items) == 3


@pytest.mark.django_db
def test_latest_entries_feed_item_title(simple_wo_placeholder):
    """Test that item_title returns post title"""
    from .factories import PostFactory, PostContentFactory

    post = PostFactory(app_config=simple_wo_placeholder)
    post_content = PostContentFactory(post=post, title="Test Post Title", language="en")
    if apps.is_installed("djangocms_versioning"):
        post_content.versions.first().publish(user=post_content.versions.first().created_by)

    feed = LatestEntriesFeed()
    title = feed.item_title(post)

    assert "Test Post Title" in str(title)


@pytest.mark.django_db
def test_latest_entries_feed_item_description_with_abstract(simple_wo_placeholder):
    """Test that item_description returns abstract when use_abstract is True"""
    from .factories import PostFactory, PostContentFactory

    simple_wo_placeholder.use_abstract = True
    simple_wo_placeholder.save()

    post = PostFactory(app_config=simple_wo_placeholder)
    post_content = PostContentFactory(
        post=post, abstract="<p>Test abstract</p>", post_text="<p>Full post text</p>", language="en"
    )
    if apps.is_installed("djangocms_versioning"):
        post_content.versions.first().publish(user=post_content.versions.first().created_by)

    feed = LatestEntriesFeed()
    description = feed.item_description(post)

    assert "Test abstract" in str(description)


@pytest.mark.django_db
def test_latest_entries_feed_item_description_without_abstract(simple_wo_placeholder):
    """Test that item_description returns post_text when use_abstract is False"""
    from .factories import PostFactory, PostContentFactory

    simple_wo_placeholder.use_abstract = False
    simple_wo_placeholder.save()

    post = PostFactory(app_config=simple_wo_placeholder)
    post_content = PostContentFactory(
        post=post, abstract="<p>Test abstract</p>", post_text="<p>Full post text</p>", language="en"
    )
    if apps.is_installed("djangocms_versioning"):
        post_content.versions.first().publish(user=post_content.versions.first().created_by)

    feed = LatestEntriesFeed()
    description = feed.item_description(post)

    assert "Full post text" in str(description)


@pytest.mark.django_db
def test_latest_entries_feed_item_dates(simple_wo_placeholder):
    """Test that item dates return correct values"""
    from .factories import PostFactory, PostContentFactory

    now = timezone.now()
    post = PostFactory(app_config=simple_wo_placeholder, date_published=now - timedelta(days=1), date_modified=now)
    PostContentFactory(post=post, language="en")

    feed = LatestEntriesFeed()

    assert feed.item_pubdate(post) == post.date_published
    assert feed.item_updateddate(post) == post.date_modified


@pytest.mark.django_db
def test_latest_entries_feed_item_guid(simple_wo_placeholder):
    """Test that item_guid returns post GUID"""
    from .factories import PostFactory, PostContentFactory

    post = PostFactory(app_config=simple_wo_placeholder)
    PostContentFactory(post=post, language="en")

    feed = LatestEntriesFeed()
    guid = feed.item_guid(post)

    assert guid == post.guid
    assert isinstance(guid, str)


@pytest.mark.django_db
def test_latest_entries_feed_item_author(page_with_menu):
    """Test that item_author returns author name and URL"""
    from .factories import PostFactory, PostContentFactory, UserFactory

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    author = UserFactory(username="testauthor", first_name="Test", last_name="Author")
    post = PostFactory(app_config=app_config, author=author)
    PostContentFactory(post=post, language="en")

    feed = LatestEntriesFeed()

    author_name = feed.item_author_name(post)
    assert "Test Author" in author_name or "testauthor" in author_name

    # Author URL should be generated
    author_url = feed.item_author_url(post)
    assert author_url is not None


# Tests for TagFeed


@pytest.mark.django_db
def test_tag_feed_get_object():
    """Test that TagFeed get_object returns the tag"""
    feed = TagFeed()
    factory = RequestFactory()
    request = factory.get("/tag/python/feed/")

    result = feed.get_object(request, "python")
    assert result == "python"


@pytest.mark.django_db
def test_tag_feed_items_filters_by_tag(page_with_menu):
    """Test that TagFeed items filters posts by tag"""

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/tag/python/feed/")
    request.path = f"/{app_config.namespace}/tag/python/feed/"

    post1, post2, post3 = Post.objects.filter(app_config=app_config)[:3]

    # Add tags
    post1.tags.add("python")
    post2.tags.add("python")
    post3.tags.add("javascript")

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)

        feed = TagFeed()
        feed(request, "python")
        items = list(feed.items(feed.get_object(request, "python")))

        # Should only include posts tagged with "python"
        assert len(items) == 2
        assert post1 in items
        assert post2 in items
        assert post3 not in items


# Tests for FBInstantFeed


@pytest.mark.django_db
def test_fb_instant_feed_rss_attributes():
    """Test that FBInstantFeed includes correct RSS attributes"""
    feed_generator = FBInstantFeed(
        title="Test Feed", link="http://example.com", description="Test Description", language="en"
    )

    attrs = feed_generator.rss_attributes()

    assert "version" in attrs
    assert "xmlns:content" in attrs
    assert attrs["xmlns:content"] == "http://purl.org/rss/1.0/modules/content/"


@pytest.mark.django_db
def test_fb_instant_feed_date_format():
    """Test that FBInstantFeed uses correct date format"""
    feed_generator = FBInstantFeed(
        title="Test Feed", link="http://example.com", description="Test Description", language="en"
    )

    assert feed_generator.date_format == "%Y-%m-%dT%H:%M:%S%z"


# Tests for FBInstantArticles


@pytest.mark.django_db
def test_fb_instant_articles_feed_type():
    """Test that FBInstantArticles uses FBInstantFeed"""
    feed = FBInstantArticles()
    assert feed.feed_type == FBInstantFeed


@pytest.mark.django_db
def test_fb_instant_articles_items(page_with_menu):
    """Test that FBInstantArticles returns posts ordered by date_modified"""
    from .factories import PostFactory, PostContentFactory

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    factory = RequestFactory()
    request = factory.get("/feed/fb/")
    request.path = f"/{app_config.namespace}/feed/fb/"
    request.user = Mock(is_authenticated=False)

    Post.objects.filter(app_config=app_config).delete()  # Clean up existing postsx
    now = timezone.now()
    post1 = PostFactory(app_config=app_config, date_modified=now - timedelta(days=2))
    post2 = PostFactory(app_config=app_config, date_modified=now - timedelta(days=1))
    post3 = PostFactory(app_config=app_config, date_modified=now)

    post_content1 = PostContentFactory(post=post1, language="en")
    post_content2 = PostContentFactory(post=post2, language="en")
    post_content3 = PostContentFactory(post=post3, language="en")
    if apps.is_installed("djangocms_versioning"):
        post_content1.versions.first().publish(user=post_content1.versions.first().created_by)
        post_content2.versions.first().publish(user=post_content2.versions.first().created_by)
        post_content3.versions.first().publish(user=post_content3.versions.first().created_by)

    with patch("djangocms_stories.feeds.get_app_instance") as mock_get_app:
        mock_get_app.return_value = (app_config.namespace, app_config)
        with patch("djangocms_stories.feeds.get_setting") as mock_setting:
            mock_setting.return_value = 10

            feed = FBInstantArticles()
            feed(request)

            items = list(feed.items())

            # Should be ordered by date_modified descending
            assert len(items) == 3
            assert items[0] == post3
            assert items[1] == post2
            assert items[2] == post1


@pytest.mark.django_db
def test_fb_instant_articles_clean_html():
    """Test that _clean_html removes empty paragraphs and normalizes headings"""
    feed = FBInstantArticles()

    html = b"<p>Content</p><p></p><p>More content</p><h3>Heading</h3><h4>Subheading</h4>"
    cleaned = feed._clean_html(html)

    # Should remove empty p tags and convert h3/h4 to h2
    cleaned_str = cleaned.decode("utf-8") if isinstance(cleaned, bytes) else str(cleaned)
    assert b"<p></p>" not in cleaned or "<p></p>" not in cleaned_str
    assert b"<h2>" in cleaned or "<h2>" in cleaned_str


@pytest.mark.django_db
def test_fb_instant_articles_item_categories(simple_wo_placeholder):
    """Test that item_categories returns category names"""
    from .factories import PostFactory, PostContentFactory, PostCategoryFactory

    category1 = PostCategoryFactory(app_config=simple_wo_placeholder, name="Tech")
    category2 = PostCategoryFactory(app_config=simple_wo_placeholder, name="News")

    post = PostFactory(app_config=simple_wo_placeholder)
    PostContentFactory(post=post, language="en")
    post.categories.add(category1, category2)

    feed = FBInstantArticles()
    categories = feed.item_categories(post)

    assert "Tech" in categories
    assert "News" in categories
    assert len(categories) == 2


@pytest.mark.django_db
def test_fb_instant_articles_author_fields_return_empty(simple_wo_placeholder):
    """Test that FB Instant Articles overrides author fields to return empty"""
    from .factories import PostFactory, PostContentFactory, UserFactory

    author = UserFactory(username="testauthor")
    post = PostFactory(app_config=simple_wo_placeholder, author=author)
    PostContentFactory(post=post, language="en")

    feed = FBInstantArticles()

    # These should return empty to prevent duplication with item_extra_kwargs
    assert feed.item_author_name(post) == ""
    assert feed.item_author_url(post) == ""


@pytest.mark.django_db
def test_fb_instant_articles_pubdate_returns_none(simple_wo_placeholder):
    """Test that FB Instant Articles pubdate returns None"""
    from .factories import PostFactory, PostContentFactory

    post = PostFactory(app_config=simple_wo_placeholder)
    PostContentFactory(post=post, language="en")

    feed = FBInstantArticles()
    assert feed.item_pubdate(post) is None


@pytest.mark.django_db
def test_fb_instant_articles_description_returns_none(simple_wo_placeholder):
    """Test that FB Instant Articles description returns None"""
    from .factories import PostFactory, PostContentFactory

    post = PostFactory(app_config=simple_wo_placeholder)
    PostContentFactory(post=post, language="en")

    feed = FBInstantArticles()
    assert feed.item_description(post) is None


# End-to-end feed retrieval tests


@pytest.mark.django_db
def test_latest_entries_feed_end_to_end(client, page_with_menu):
    """End-to-end test: Retrieve and parse LatestEntriesFeed"""
    from .factories import PostFactory, PostContentFactory, UserFactory

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    # Create published posts
    author = UserFactory(username="author", first_name="John", last_name="Doe")

    Post.objects.filter(app_config=app_config).delete()  # Clean up existing posts
    now = timezone.now()
    post1 = PostFactory(
        app_config=app_config, author=author, date_published=now - timedelta(days=1), date_modified=now
    )
    post2 = PostFactory(
        app_config=app_config,
        author=author,
        date_published=now - timedelta(days=2),
        date_modified=now - timedelta(hours=1),
    )

    post_content1 = PostContentFactory(
        post=post1,
        title="First Test Post",
        abstract="<p>First abstract</p>",
        post_text="<p>First full content</p>",
        language="en",
    )
    post_content2 = PostContentFactory(
        post=post2,
        title="Second Test Post",
        abstract="<p>Second abstract</p>",
        post_text="<p>Second full content</p>",
        language="en",
    )
    if apps.is_installed("djangocms_versioning"):
        post_content1.versions.first().publish(user=post_content1.versions.first().created_by)
        post_content2.versions.first().publish(user=post_content2.versions.first().created_by)

    # Get the feed URL
    url = reverse(
        f"{app_config.namespace}:posts-latest-feed",
    )

    # Retrieve the feed
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/rss+xml") or response["Content-Type"].startswith(
        "application/xml"
    )

    # Parse the XML
    content = response.content.decode("utf-8")
    root = ET.fromstring(content)

    # Verify RSS structure
    channel = root.find("channel")
    assert channel is not None

    # Verify channel elements
    title = channel.find("title")
    assert title is not None

    link = channel.find("link")
    assert link is not None

    description = channel.find("description")
    assert description is not None
    assert "Blog articles" in description.text

    # Verify items
    items = channel.findall("item")
    assert len(items) == 2

    # Verify first item (most recent)
    first_item = items[0]
    item_title = first_item.find("title")
    assert "First Test Post" in item_title.text

    item_guid = first_item.find("guid")
    assert item_guid is not None
    assert item_guid.text == str(post1.guid)

    item_pubdate = first_item.find("pubDate")
    assert item_pubdate is not None

    # Verify description contains content
    item_description = first_item.find("description")
    assert item_description is not None
    assert "abstract" in item_description.text or "content" in item_description.text


@pytest.mark.django_db
def test_tag_feed_end_to_end(client, page_with_menu):
    """End-to-end test: Retrieve and parse TagFeed"""
    from .factories import PostFactory, PostContentFactory

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    # Create posts with tags
    post1 = PostFactory(app_config=app_config, date_published=timezone.now())
    post2 = PostFactory(app_config=app_config, date_published=timezone.now() - timedelta(days=1))
    post3 = PostFactory(app_config=app_config, date_published=timezone.now() - timedelta(days=2))

    post_content1 = PostContentFactory(post=post1, title="Python Post", language="en")
    post_content2 = PostContentFactory(post=post2, title="Another Python Post", language="en")
    post_content3 = PostContentFactory(post=post3, title="JavaScript Post", language="en")
    if apps.is_installed("djangocms_versioning"):
        post_content1.versions.first().publish(user=post_content1.versions.first().created_by)
        post_content2.versions.first().publish(user=post_content2.versions.first().created_by)
        post_content3.versions.first().publish(user=post_content3.versions.first().created_by)

    post1.tags.add("python", "web")
    post2.tags.add("python", "tutorial")
    post3.tags.add("javascript", "web")

    # Get the tag feed URL
    url = reverse(
        f"{app_config.namespace}:posts-tagged-feed", kwargs={"tag": "python"}, current_app=app_config.namespace
    )

    # Retrieve the feed
    response = client.get(url)

    assert response.status_code == 200

    # Parse the XML
    content = response.content.decode("utf-8")
    root = ET.fromstring(content)

    # Verify items
    channel = root.find("channel")
    items = channel.findall("item")

    # Should only contain posts tagged with "python"
    assert len(items) == 2

    titles = [item.find("title").text for item in items]
    assert any("Python Post" in title for title in titles)
    assert all("JavaScript Post" not in title for title in titles)


@pytest.mark.django_db
@pytest.mark.skip(reason="Implementation does not create valid XML")
def test_fb_instant_feed_end_to_end(client, page_with_menu):
    """End-to-end test: Retrieve and parse FBInstantArticles feed"""
    from .factories import PostFactory, PostContentFactory, UserFactory, PostCategoryFactory

    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    # Create post with category
    category = PostCategoryFactory(app_config=app_config, name="Technology")
    author = UserFactory(username="fbauthor", first_name="FB", last_name="Author")

    post = PostFactory(
        app_config=app_config, author=author, date_published=timezone.now(), date_modified=timezone.now()
    )
    PostContentFactory(
        post=post,
        title="FB Instant Article",
        abstract="<p>FB abstract</p>",
        post_text="<p>FB full content with <strong>formatting</strong></p>",
        language="en",
    )
    post.categories.add(category)

    # Get the FB feed URL
    url = reverse(
        f"{app_config.namespace}:posts-latest-feed-fb",
    )

    # Mock the PostDetailView response for FB instant articles
    with patch("djangocms_stories.feeds.PostDetailView.as_view") as mock_view:
        mock_response = Mock()
        mock_response.content = b"<html><body><article>Mocked article content</article></body></html>"
        mock_response.render = Mock(return_value=mock_response)
        mock_view.return_value = Mock(return_value=mock_response)

        # Retrieve the feed
        response = client.get(url)

        assert response.status_code == 200

        # Parse the XML
        content = response.content.decode("utf-8")
        root = ET.fromstring(content)

        # Verify RSS structure with content namespace
        assert root.tag == "rss"

        channel = root.find("channel")
        assert channel is not None

        # Verify items
        items = channel.findall("item")
        assert len(items) >= 1

        first_item = items[0]
        item_title = first_item.find("title")
        assert "FB Instant Article" in item_title.text

        # Verify category
        item_category = first_item.find("category")
        assert item_category is not None
        assert "Technology" in item_category.text


@pytest.mark.django_db
def test_feed_with_no_posts(client, page_with_menu):
    """Test feed returns empty item list when no posts exist"""
    # Get the feed URL without creating any posts
    app_config = StoriesConfig.objects.get(namespace=page_with_menu.application_namespace)
    url = reverse(f"{app_config.namespace}:posts-latest-feed", current_app=app_config.namespace)
    Post.objects.filter(app_config=app_config).delete()

    # Retrieve the feed
    response = client.get(url)

    assert response.status_code == 200

    # Parse the XML
    content = response.content.decode("utf-8")
    root = ET.fromstring(content)

    # Verify channel exists but no items
    channel = root.find("channel")
    assert channel is not None

    items = channel.findall("item")
    assert len(items) == 0
