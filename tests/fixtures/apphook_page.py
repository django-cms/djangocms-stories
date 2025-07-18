import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory


@pytest.fixture
def many_posts(simple_w_placeholder):
    from djangocms_stories.models import PostCategory

    from ..factories import PostContentFactory

    batch = PostContentFactory.create_batch(10, post__app_config=simple_w_placeholder)
    category = PostCategory.objects.create(name="Test Category", slug="test-category", app_config=simple_w_placeholder)
    for post in batch:
        post.categories.add(category)
    if apps.is_installed("djangocms_versioning"):
        for post_content in batch[:5]:
            post_content.versions.first().publish(user=post_content.versions.first().created_by)
    return batch


@pytest.fixture
def page_with_menu(many_posts, simple_w_placeholder):
    from cms import api

    from tests.factories import UserFactory

    user = UserFactory(is_superuser=True, is_staff=True)
    page = api.create_page(
        title="Test Page",
        template="base.html",
        language="en",
        slug="test-page",
        created_by=user,
    )
    page.application_urls = "StoriesApp"
    page.application_namespace = simple_w_placeholder.namespace
    page.navigation_extenders = "PostCategoryMenu"
    page.save()
    if apps.is_installed("djangocms_versioning"):
        page_content = page.pagecontent_set(manager="admin_manager").first()
        version = page_content.versions.first()
        version.publish(user=user)
    return page


@pytest.fixture
def category_request():
    request = RequestFactory().get("/blog/category/test-category/")
    request.user = AnonymousUser()
    return request
