import pytest
from django.core.exceptions import ValidationError
from djangocms_stories.models import PostCategory


@pytest.mark.django_db
def test_create_post_category():
    from .factories import PostCategoryFactory

    category = PostCategoryFactory(name="Tech", slug="tech", app_config__namespace="djangocms_stories")
    assert category.name == "Tech"
    assert category.slug == "tech"
    assert PostCategory.objects.count() == 1
    assert category.get_absolute_url() == f"/en/blog/category/{category.slug}/"
    assert category.get_absolute_url(lang="en") == f"/en/blog/category/{category.slug}/"
    assert category.get_full_url() == f"http://example.com/en/blog/category/{category.slug}/"


@pytest.mark.django_db
def test_post_category_str():
    category = PostCategory.objects.create(name="Science", slug="science")
    assert str(category) == "Science"


@pytest.mark.django_db
def test_post_category_unique_slug():
    PostCategory.objects.create(name="Health", slug="health")
    with pytest.raises(Exception):
        PostCategory.objects.create(name="Health 2", slug="health")


@pytest.mark.django_db
def test_post_category_blank_name():
    category = PostCategory(name="", slug="empty")
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_post_category_blank_slug():
    category = PostCategory(name="NoSlug", slug="")
    with pytest.raises(ValidationError):
        category.full_clean()


@pytest.mark.django_db
def test_post_category_hierarchy():
    from .factories import PostCategoryFactory

    parent = PostCategoryFactory(name="Parent Category", slug="parent", priority=1)
    child_1 = PostCategoryFactory(parent=parent, priority=1)
    child_2 = PostCategoryFactory(parent=parent, priority=1)
    grandchild = PostCategoryFactory(parent=child_1, priority=1)

    expected_descendants = [child_1, child_2, grandchild]

    assert parent.get_descendants() == expected_descendants


@pytest.mark.django_db
def test_category_description():
    from .factories import PostCategoryFactory

    category = PostCategoryFactory(
        name="Test Category",
        meta_description="<p>This is a <b>test</b> description.</p>",
        abstract="<p>This is a <b>test</b> abstract.</p>",
    )

    assert category.meta_description == "<p>This is a <b>test</b> description.</p>"
    assert category.get_description() == "This is a test description."

    assert category.abstract == "<p>This is a <b>test</b> abstract.</p>"
    assert category.name == "Test Category"
    assert category.get_title() == "Test Category"
