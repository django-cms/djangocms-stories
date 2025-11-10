import datetime
import hashlib

import pytest
from django.apps import apps
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
    assert post.full_image_options() == {"crop": True, "size": "640x360", "upscale": False}

    if apps.is_installed("djangocms_versioning"):
        assert post.get_content(language="en", show_draft_content=False) is None
    else:
        # Some post properties access the content and are only available if the content is published
        assert str(post_content.post) == "Test Post"
        assert post.guid == hashlib.sha256(force_bytes(f"-en-test-post-{post.app_config.namespace}-")).hexdigest()
        assert post.get_content(language="en", show_draft_content=False) == post_content

    # PostContent properties
    assert post_content.date_modified is post_content.post.date_modified
    assert post_content.get_image_full_url() == ""
    assert post_content.get_image_width() is None
    assert post_content.get_image_height() is None
    assert post_content.get_keywords() == []
    assert post_content.get_tags() == ""


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

    assert post_content_1.get_description() == "This is a test description."
    assert post_content_2.get_description() == "This is a test abstract."


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

    assert post_content_1.get_keywords() == []
    assert post_content_2.get_keywords() == [
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


@pytest.mark.django_db
def test_get_image_full_url_no_image(db):
    """Test get_image_full_url returns empty string when no image is set."""
    from .factories import PostContentFactory, PostFactory

    post = PostFactory(main_image=None)
    post_content = PostContentFactory(post=post)

    assert post.get_image_full_url() == ""
    assert post_content.get_image_full_url() == ""


@pytest.mark.django_db
def test_get_image_width_no_image(db):
    """Test get_image_width returns None when no image is set."""
    from .factories import PostContentFactory, PostFactory

    post = PostFactory(main_image=None)
    post_content = PostContentFactory(post=post)

    assert post.get_image_width() is None
    assert post_content.get_image_width() is None


@pytest.mark.django_db
def test_get_image_height_no_image(db):
    """Test get_image_height returns None when no image is set."""
    from .factories import PostContentFactory, PostFactory

    post = PostFactory(main_image=None)
    post_content = PostContentFactory(post=post)

    assert post.get_image_height() is None
    assert post_content.get_image_height() is None


@pytest.mark.django_db
def test_get_image_full_url_with_image(db):
    """Test get_image_full_url returns correct URL when image is set."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from filer.models import Image
    from PIL import Image as PILImage

    from .factories import PostContentFactory, PostFactory

    # Create a simple test image
    image_file = BytesIO()
    image = PILImage.new("RGB", (800, 600), color="red")
    image.save(image_file, "JPEG")
    image_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="test_image.jpg",
        content=image_file.read(),
        content_type="image/jpeg",
    )

    # Create a filer Image object
    filer_image = Image.objects.create(
        file=uploaded_file,
        original_filename="test_image.jpg",
    )

    post = PostFactory(main_image=filer_image)
    post_content = PostContentFactory(post=post)

    # Mock build_absolute_uri for testing
    # The method should return a non-empty string with the image path
    def mock_build_absolute_uri(path):
        return f"http://example.com{path}"

    post.build_absolute_uri = mock_build_absolute_uri
    post_content.build_absolute_uri = mock_build_absolute_uri

    # Without META_IMAGE_SIZE setting, should return the original image URL
    url = post.get_image_full_url()
    assert url != ""
    assert "test_image" in url
    assert url.startswith("http")  # build_absolute_uri should add domain

    # PostContent should delegate to Post
    assert post_content.get_image_full_url() == url


@pytest.mark.django_db
def test_get_image_width_with_image(db):
    """Test get_image_width returns correct width when image is set."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from filer.models import Image
    from PIL import Image as PILImage

    from .factories import PostContentFactory, PostFactory

    # Create a test image with specific dimensions
    image_file = BytesIO()
    image = PILImage.new("RGB", (800, 600), color="blue")
    image.save(image_file, "JPEG")
    image_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="test_width.jpg",
        content=image_file.read(),
        content_type="image/jpeg",
    )

    # Create a filer Image object
    filer_image = Image.objects.create(
        file=uploaded_file,
        original_filename="test_width.jpg",
    )

    post = PostFactory(main_image=filer_image)
    post_content = PostContentFactory(post=post)

    # Without META_IMAGE_SIZE setting, should return the original image width
    assert post.get_image_width() == 800
    assert post_content.get_image_width() == 800


@pytest.mark.django_db
def test_get_image_height_with_image(db):
    """Test get_image_height returns correct height when image is set."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from filer.models import Image
    from PIL import Image as PILImage

    from .factories import PostContentFactory, PostFactory

    # Create a test image with specific dimensions
    image_file = BytesIO()
    image = PILImage.new("RGB", (800, 600), color="green")
    image.save(image_file, "JPEG")
    image_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="test_height.jpg",
        content=image_file.read(),
        content_type="image/jpeg",
    )

    # Create a filer Image object
    filer_image = Image.objects.create(
        file=uploaded_file,
        original_filename="test_height.jpg",
    )

    post = PostFactory(main_image=filer_image)
    post_content = PostContentFactory(post=post)

    # Without META_IMAGE_SIZE setting, should return the original image height
    assert post.get_image_height() == 600
    assert post_content.get_image_height() == 600


@pytest.mark.django_db
def test_get_image_methods_with_thumbnail_settings(db, settings):
    """Test image methods with META_IMAGE_SIZE setting configured."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from filer.models import Image
    from PIL import Image as PILImage

    from .factories import PostContentFactory, PostFactory

    # Configure META_IMAGE_SIZE setting to create thumbnails
    # Set both possible setting names to ensure it works
    settings.STORIES_META_IMAGE_SIZE = {"size": (400, 300), "crop": True}
    settings.DJANGOCMS_BLOG_META_IMAGE_SIZE = {"size": (400, 300), "crop": True}

    # Create a test image larger than the thumbnail size
    image_file = BytesIO()
    image = PILImage.new("RGB", (800, 600), color="yellow")
    image.save(image_file, "JPEG")
    image_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="test_thumbnail.jpg",
        content=image_file.read(),
        content_type="image/jpeg",
    )

    # Create a filer Image object
    filer_image = Image.objects.create(
        file=uploaded_file,
        original_filename="test_thumbnail.jpg",
    )

    post = PostFactory(main_image=filer_image)
    post_content = PostContentFactory(post=post)

    # Mock build_absolute_uri for testing
    def mock_build_absolute_uri(path):
        return f"http://example.com{path}"

    post.build_absolute_uri = mock_build_absolute_uri
    post_content.build_absolute_uri = mock_build_absolute_uri

    # With META_IMAGE_SIZE setting, should use thumbnail dimensions
    url = post.get_image_full_url()
    assert url != ""
    assert url.startswith("http")

    # Thumbnail dimensions should be used
    width = post.get_image_width()
    height = post.get_image_height()
    assert width == 400
    assert height == 300

    # PostContent should return same values
    assert post_content.get_image_width() == 400
    assert post_content.get_image_height() == 300
    assert post_content.get_image_full_url() == url


@pytest.mark.django_db
def test_get_image_methods_different_image_formats(db):
    """Test image methods work with different image formats."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from filer.models import Image
    from PIL import Image as PILImage

    from .factories import PostFactory

    # Mock build_absolute_uri for testing
    def mock_build_absolute_uri(path):
        return f"http://example.com{path}"

    # Test with PNG format
    png_file = BytesIO()
    png_image = PILImage.new("RGBA", (400, 300), color=(255, 0, 0, 128))
    png_image.save(png_file, "PNG")
    png_file.seek(0)

    png_uploaded = SimpleUploadedFile(
        name="test.png",
        content=png_file.read(),
        content_type="image/png",
    )

    filer_png = Image.objects.create(
        file=png_uploaded,
        original_filename="test.png",
    )

    post_png = PostFactory(main_image=filer_png)
    post_png.build_absolute_uri = mock_build_absolute_uri
    assert post_png.get_image_full_url() != ""
    assert post_png.get_image_width() == 400
    assert post_png.get_image_height() == 300

    # Test with GIF format
    gif_file = BytesIO()
    gif_image = PILImage.new("RGB", (200, 150), color="blue")
    gif_image.save(gif_file, "GIF")
    gif_file.seek(0)

    gif_uploaded = SimpleUploadedFile(
        name="test.gif",
        content=gif_file.read(),
        content_type="image/gif",
    )

    filer_gif = Image.objects.create(
        file=gif_uploaded,
        original_filename="test.gif",
    )

    post_gif = PostFactory(main_image=filer_gif)
    post_gif.build_absolute_uri = mock_build_absolute_uri
    assert post_gif.get_image_full_url() != ""
    assert post_gif.get_image_width() == 200
    assert post_gif.get_image_height() == 150
