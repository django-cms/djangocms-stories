import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils.translation import override


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
    return user


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


def test_config_admin(admin_client, default_config, assert_html_in_response):
    url = reverse("admin:djangocms_stories_storiesconfig_change", args=[default_config.pk])
    response = admin_client.get(url)
    parler_language_selector = """
        <div class="parler-language-tabs">
        <input type="hidden" class="language_button selected" name="en" /><span class="current">English</span>
        <span class="empty">
            <a href="?language=it">Italiano</a></span><span class="empty">
            <a href="?language=fr">French</a>
        </span></div>"""
    namespace_is_readonly = f'<div class="readonly">{default_config.namespace}</div>'

    assert_html_in_response(parler_language_selector, response)
    assert_html_in_response(namespace_is_readonly, response)


def test_post_model_is_listed_in_admin(admin_client):
    url = reverse("admin:index")
    response = admin_client.get(url)
    assert response.status_code == 200
    # Post model should be listed
    assert "Post" in response.content.decode()
    # PostContent model should NOT be listed
    assert "Post Content" not in response.content.decode()


def test_postcontentadmin_change_view_get_redirects_to_grouper(admin_client, db):
    # Create a Post and PostContent
    from .factories import PostFactory, PostContentFactory

    post = PostFactory()
    post_content = PostContentFactory(post=post, language="en", title="Test", post_text="Text")
    # Get the PostContentAdmin change view URL
    url = reverse("admin:djangocms_stories_postcontent_change", args=[post_content.pk])
    response = admin_client.get(url)
    # Should redirect (302) to the Post change view (grouper)
    assert response.status_code == 302
    assert reverse("admin:djangocms_stories_post_change", args=[post.pk]) in response["Location"]


def test_postcontentadmin_change_view_post_raises_404(admin_client, db):
    # Create a Post and PostContent
    from .factories import PostFactory, PostContentFactory

    post = PostFactory()
    post_content = PostContentFactory(post=post, language="en", title="Test", post_text="Text")
    url = reverse("admin:djangocms_stories_postcontent_change", args=[post_content.pk])
    # POST request should raise 404
    response = admin_client.post(url, data={})
    assert response.status_code == 404


def test_postadmin_change_list_view(admin_client, assert_html_in_response):
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(20)

    url = reverse("admin:djangocms_stories_post_changelist")
    response = admin_client.get(url)

    for post_content in post_contents:
        change_url = reverse(
            "admin:djangocms_stories_post_change",
            args=[post_content.post.pk],
        )
        assert_html_in_response(
            f'<a href="{change_url}?language=en&amp;_changelist_filters=language%3Den">{post_content.title}</a>',
            response,
        )


def test_postadmin_change_list_view_other_lang(admin_client, default_config, assert_html_in_response):
    from .factories import PostContentFactory

    with override("it"):
        # Create post contents in Italian
        assert default_config.object_name == "Story"
        assert "en" in default_config.get_available_languages()

    PostContentFactory.create_batch(20)
    post_contents = PostContentFactory.create_batch(2, post__app_config=default_config)

    url = reverse("admin:djangocms_stories_post_changelist") + "?language=it"
    response = admin_client.get(url)

    for post_content in post_contents:
        change_url = reverse(
            "admin:djangocms_stories_post_change",
            args=[post_content.post.pk],
        )
        assert_html_in_response(
            f'<a href="{change_url}?_changelist_filters=language%3Dit&amp;language=it">Empty</a>', response
        )


@pytest.mark.django_db
def test_postadmin_bulk_enable_comments(admin_client, default_config, assert_html_in_response):
    # Create some posts
    from .factories import PostFactory

    posts = PostFactory.create_batch(4, enable_comments=False, app_config=default_config)
    # All posts should have enable_comments=False by default
    for post in posts:
        assert not post.enable_comments

    # Bulk enable comments
    url = reverse("admin:djangocms_stories_post_changelist")
    data = {
        "action": "enable_comments",
        "_selected_action": [post.pk for post in posts],
    }
    response = admin_client.post(url, data, follow=True)
    assert_html_in_response(
        '<ul class="messagelist"><li class="info">Comments for 4 entries enabled</li></ul>', response
    )
    # Refresh from db and check
    for post in posts:
        post.refresh_from_db()
        assert post.enable_comments is True


def test_postadmin_bulk_disable_comments(admin_client, default_config, assert_html_in_response):
    # Create some posts with enable_comments=True
    from .factories import PostFactory

    posts = PostFactory.create_batch(4, enable_comments=True, app_config=default_config)
    for post in posts:
        assert post.enable_comments

    # Bulk disable comments
    url = reverse("admin:djangocms_stories_post_changelist")
    data = {
        "action": "disable_comments",
        "_selected_action": [post.pk for post in posts],
    }
    response = admin_client.post(url, data, follow=True)
    assert_html_in_response(
        '<ul class="messagelist"><li class="info">Comments for 4 entries disabled.</li></ul>', response
    )
    # Refresh from db and check
    for post in posts:
        post.refresh_from_db()
        assert post.enable_comments is False


def test_post_change_admin(admin_client, default_config, assert_html_in_response):
    from .factories import PostFactory

    post = PostFactory(app_config=default_config)

    url = reverse("admin:djangocms_stories_post_change", args=[post.pk])
    response = admin_client.get(url)

    # django CMS activated the language selector
    assert_html_in_response('<script src="/static/cms/js/admin/language-selector.js">', response)
    assert_html_in_response(
        """
        <input type="button" data-url="en" class="language_button selected" id="enbutton" name="en" value="English"/>
        <input type="button" data-url="it" class="language_button notfilled" id="itbutton" name="it" value="Italiano"/>
        <input type="button" data-url="fr" class="language_button notfilled" id="frbutton" name="fr" value="French"/>
        """,
        response,
    )

    # Ensure the language field is present for post content
    assert_html_in_response(
        '<input type="hidden" name="content__language" value="en" id="id_content__language">', response
    )

    # Both post and post content fields are present
    assert_html_in_response('<label class="inline" for="id_author">Author:</label>', response)  # Post author field
    assert_html_in_response(
        '<label class="required" for="id_content__title">Title (English):</label>', response
    )  # PostContent title field
