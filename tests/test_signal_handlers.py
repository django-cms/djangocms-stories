import pytest
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now, timedelta


pytestmark = pytest.mark.skipif(
    not apps.is_installed("djangocms_versioning"),
    reason="djangocms-versioning is not installed",
)


def get_version(post_content):
    """Return the Version object for a given PostContent instance."""
    from djangocms_versioning.models import Version

    ct = ContentType.objects.get_for_model(post_content)
    return Version.objects.get(content_type=ct, object_id=post_content.pk)



@pytest.mark.django_db
def test_publish_sets_date_published(default_config, admin_user):
    """First publish sets date_published on the Post."""
    from tests.factories import PostContentFactory

    post_content = PostContentFactory(
        post__app_config=default_config, post__date_published=None
    )
    post = post_content.post
    assert post.date_published is None

    get_version(post_content).publish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published is not None


@pytest.mark.django_db
def test_publish_does_not_overwrite_existing_date_published(default_config, admin_user):
    """Republishing a new version keeps the original date_published."""
    from tests.factories import PostContentFactory

    post_content = PostContentFactory(
        post__app_config=default_config, post__date_published=None
    )
    post = post_content.post

    version = get_version(post_content)
    version.publish(user=admin_user)
    post.refresh_from_db()
    original_date = post.date_published
    assert original_date is not None

    version.unpublish(user=admin_user)

    new_version = get_version(PostContentFactory(post=post))
    new_version.publish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published == original_date




@pytest.mark.django_db
def test_unpublish_sets_date_published_end(default_config, admin_user):
    """Unpublishing records date_published_end on the Post."""
    from tests.factories import PostContentFactory

    post_content = PostContentFactory(
        post__app_config=default_config, post__date_published_end=None
    )
    post = post_content.post

    version = get_version(post_content)
    version.publish(user=admin_user)
    version.unpublish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published_end is not None



@pytest.mark.django_db
def test_republish_clears_date_published_end(default_config, admin_user):
    """ republished clears date_published_end (Published since)"""
    from tests.factories import PostContentFactory

    post_content = PostContentFactory(
        post__app_config=default_config, post__date_published_end=None
    )
    post = post_content.post

    version = get_version(post_content)
    version.publish(user=admin_user)
    version.unpublish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published_end is not None  

    new_version = get_version(PostContentFactory(post=post))
    new_version.publish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published_end is None


@pytest.mark.django_db
def test_republish_keeps_future_date_published_end(default_config, admin_user):
    """
    If it is set to a future date republishing a new version must not clear it.
    """
    from tests.factories import PostContentFactory

    future = now() + timedelta(days=30)
    post_content = PostContentFactory(
        post__app_config=default_config, post__date_published_end=future
    )
    post = post_content.post

    version = get_version(post_content)
    version.publish(user=admin_user)

    post.refresh_from_db()
    assert post.date_published_end == future  