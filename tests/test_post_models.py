import datetime
import hashlib
from django.apps import apps
import pytest

from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.timezone import now

from tests.utils import assert_num_queries

from .utils import publish_if_necessary


@pytest.mark.django_db
def test_base_fixture(post_content):
    """This is a placeholder test to ensure pytest is set up correctly."""
    assert post_content.title == "Test Post"
    assert post_content.slug == "test-post"
    assert post_content.subtitle == "This is a test post subtitle"
    assert post_content.meta_title == "Test Post Meta Title"
    assert post_content.meta_description == "This is a test post meta description."
    assert "<p>This is a test post content.</p>" in post_content.post_text
    assert post_content.get_template() == "djangocms_stories/post_detail.html"
    assert post_content.content.cmsplugin_set.filter(language="en").count() == 1
    assert post_content.media.cmsplugin_set.filter(language="en").count() == 0

    # Post properties
    post = post_content.post
    assert post.featured() is False
    assert post.date == post.date_created  # No date_published or date_featured set, so date_created is used
    assert post.get_content(language="en", show_draft_content=True) == post_content
    assert post.get_image_full_url() == ""
    assert post.get_image_width() is None
    assert post.get_image_height() is None
    assert post.thumbnail_options() == {"crop": True, "size": "120x120", "upscale": False}
    assert post.full_image_options() == {"crop": True, "size": "640", "upscale": False}

    if apps.is_installed("djangocms_versioning"):
        assert post.get_content(language="en", show_draft_content=False) is None
    else:
        # Some post properties access the content and are only available if the content is published
        assert str(post_content.post) == "Test Post"
        assert post.guid == hashlib.sha256(force_bytes(f"-en-test-post-{post.app_config.namespace}-")).hexdigest()
        assert post.get_content(language="en", show_draft_content=False) == post_content


@pytest.mark.django_db
def test_post_content_compatibility_stubs(db, default_config):
    from .factories import PostCategoryFactory, PostContentFactory, SiteFactory

    categories = [PostCategoryFactory(app_config=default_config), PostCategoryFactory(app_config=default_config)]
    post_content = PostContentFactory(post__app_config=default_config)
    other_post_content = PostContentFactory(post__app_config=default_config)
    other_post_content.post.sites.add(SiteFactory())

    post_content.post.categories.set(categories)
    other_post_content.post.categories.set(categories[0:1])

    assert post_content.post.author == post_content.author
    assert post_content.post.date_published == post_content.date_published
    assert post_content.post.date_published_end == post_content.date_published_end
    assert set(post_content.post.categories.all()) == set(post_content.categories.all())
    assert post_content.get_absolute_url() == post_content.post.get_absolute_url()
    assert str(post_content) == post_content.title
    assert categories[0].count == 1
    assert categories[1].count == 1
    assert categories[0].count_all_sites == 2
    assert categories[1].count_all_sites == 1


@pytest.mark.django_db
def test_date_property(db):
    """Test the date property of the Post model: Corresponds to date_published if present."""
    from .factories import PostFactory

    post = PostFactory()
    if post.date_published == post.date_featured:
        post.date_published = None
    assert post.date == post.date_featured


@pytest.mark.django_db
def test_post_unicode_slug(db, post, admin_user):
    """Test the unicode slug of the Post model."""
    from djangocms_stories.models import PostContent

    post_content = PostContent.objects.using(db).create(
        post=post,
        language="fr",
        title="Accentué",
        subtitle="This is a test post subtitle",
        meta_title="Meta Accentué",
        meta_description="This is a test post meta description.",
        post_text="<p>This is a test post content.</p>",
    )
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.constants import PUBLISHED
        from djangocms_versioning.models import Version

        Version.objects.using(db).create(content=post_content, created_by=admin_user, state=PUBLISHED)

    assert post_content.slug == "accentué"

    # Change the language and check the __str__ method
    with translation.override("fr"):
        assert str(post_content.post) == "Accentué"
        assert post.get_title() == "Meta Accentué"
        assert post.get_title(language="fr") == "Meta Accentué"
        assert post.get_title(language="en") == "Meta Accentué"
        post_content.meta_title = ""
        post_content.save()
        post._content_cache = {}  # Clear the cache to force re-fetching
        assert post.get_title(language="fr") == "Accentué"
        assert post.get_title(language="en") == "Accentué"
        assert post.guid == hashlib.sha256(force_bytes(f"-fr-accentué-{post.app_config.namespace}-")).hexdigest()
        fr_cache_key = post.get_cache_key(prefix="", language="fr")

    assert post.get_cache_key(prefix="", language="en") != fr_cache_key


@pytest.mark.django_db
def test_get_description(db):
    from .factories import PostContentFactory

    post_content_1 = PostContentFactory(meta_description="<p>This is a <b>test</b> description.</p>", abstract="")
    post_content_2 = PostContentFactory(meta_description="", abstract="<p>This is a <b>test</b> abstract.</p>")
    publish_if_necessary([post_content_1, post_content_2], post_content_1.post.author)

    assert post_content_1.post.get_description() == "This is a test description."
    assert post_content_2.post.get_description() == "This is a test abstract."


@pytest.mark.django_db
def test_get_keywords(db):
    from .factories import PostContentFactory

    post_content_1 = PostContentFactory(meta_keywords="")
    post_content_2 = PostContentFactory(meta_keywords="test, are these key words, or not")
    publish_if_necessary([post_content_1, post_content_2], post_content_1.post.author)

    assert post_content_1.post.get_keywords() == []
    assert post_content_2.post.get_keywords() == [
        "test",
        "are these key words",
        "or not",
    ]


@pytest.mark.django_db
def test_featured_property(db):
    """Test the featured property of the Post model."""
    from .factories import PostFactory

    post = PostFactory(date_featured=None)
    assert not post.featured()

    post.date_featured = now() - datetime.timedelta(days=1)
    assert post.featured()


@pytest.mark.django_db
def test_get_author(db):
    from .factories import PostContentFactory, UserFactory

    user = UserFactory(username="testuser")
    post_content = PostContentFactory(post__author=user)

    assert post_content.post.get_author() == user


@pytest.mark.django_db
def test_get_content_caches(post_content):
    """Test that get_content caches the result."""
    post = post_content.post
    post_content = post.get_content(language="en", show_draft_content=True)
    with assert_num_queries(0):
        # This should hit the cache
        assert post.get_content(language="en", show_draft_content=True) is post_content


@pytest.mark.django_db
def test_get_template(simple_w_placeholder, simple_wo_placeholder):
    """Test that get_template returns the correct template based on the app config."""
    from .factories import PostContentFactory, StoriesConfigFactory

    template_config = StoriesConfigFactory(
        namespace="test_template_config",
        use_placeholder=True,
        template_prefix="my-tempaltes",
    )
    post_content_with_placeholder = PostContentFactory(post__app_config=simple_w_placeholder)
    post_content_without_placeholder = PostContentFactory(post__app_config=simple_wo_placeholder)
    post_content_without_config = PostContentFactory(post__app_config=None)
    post_content_with_template_config = PostContentFactory(post__app_config=template_config)

    assert post_content_with_placeholder.get_template() == "djangocms_stories/post_detail.html"
    assert post_content_without_placeholder.get_template() == "djangocms_stories/no_post_structure.html"
    assert post_content_without_config.get_template() == "djangocms_stories/post_detail.html"
    assert post_content_with_template_config.get_template() == "my-tempaltes/post_detail.html"
