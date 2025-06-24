import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client


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
