import pytest


@pytest.fixture
@pytest.mark.django_db
def post(db, default_config):
    from djangocms_stories.models import Post

    return Post.objects.using(db).create(
        app_config=default_config,
    )


@pytest.fixture
@pytest.mark.django_db
def post_content(db, post):
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
    if post.app_config.use_placeholder:
        from cms.api import add_plugin
        from cms.models import Placeholder

        placeholder = Placeholder.objects.using(db).create(
            slot="content",
            source=post_content,
        )
        add_plugin(placeholder, "TextPlugin", "en", body="This is a test placeholder content.")
    return post_content
