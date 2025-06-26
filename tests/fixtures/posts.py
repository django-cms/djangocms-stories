import pytest

from django.apps import apps


@pytest.fixture
@pytest.mark.django_db
def post(db, default_config):
    from djangocms_stories.models import Post

    return Post.objects.using(db).create(
        app_config=default_config,
    )


@pytest.fixture
@pytest.mark.django_db
def post_content(db, post, admin_user):
    from djangocms_stories.models import PostContent

    post_content = PostContent.objects.using(db).create(
        post=post,
        language="en",
        title="Test Post",
        subtitle="This is a test post subtitle",
        meta_title="Test Post Meta Title",
        meta_description="This is a test post meta description.",
        post_text="<p>This is a test post content.</p>",
    )
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.constants import DRAFT
        from djangocms_versioning.models import Version

        Version.objects.using(db).create(
            content=post_content,
            created_by=admin_user,
        )
    if post.app_config.use_placeholder:
        from cms.api import add_plugin
        from cms.models import Placeholder

        Placeholder.objects.using(db).create(
            slot="media",
            source=post_content,
        )
        placeholder = Placeholder.objects.using(db).create(
            slot="content",
            source=post_content,
        )
        add_plugin(placeholder, "TextPlugin", "en", body="This is a test placeholder content.")
    return post_content
