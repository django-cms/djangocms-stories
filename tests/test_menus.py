import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from parler.utils.context import smart_override

from djangocms_stories.cms_appconfig import StoriesConfig


@pytest.fixture
def many_posts(simple_w_placeholder):
    from djangocms_stories.models import PostCategory

    from .factories import PostContentFactory

    batch = PostContentFactory.create_batch(10, post__app_config=simple_w_placeholder)
    category = PostCategory.objects.create(name="Test Category", slug="test-category", app_config=simple_w_placeholder)
    for post in batch:
        post.categories.add(category)
    if apps.is_installed("djangocms_versioning"):
        for post_content in batch[:5]:
            post_content.versions.first().publish(user=post_content.versions.first().created_by)
    return batch


@pytest.fixture
def page_with_menu(many_posts):
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
    page.application_namespace = StoriesConfig.objects.first().namespace
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


@pytest.mark.django_db
def test_menu_registered(page_with_menu):
    from menus.menu_pool import menu_pool

    assert f"PostCategoryMenu:{page_with_menu.pk}" in menu_pool.get_registered_menus()


@pytest.mark.django_db
def test_menu_cache_clear_blogconfig(category_request, page_with_menu):
    """
    Tests if menu cache is cleared after config deletion
    """

    from django.core.cache import cache
    from menus.menu_pool import menu_pool
    from menus.models import CacheKey

    app_config_test = StoriesConfig.objects.create(namespace="test_config")
    app_config_test.app_title = "appx"
    app_config_test.object_name = "Blogx"
    app_config_test.save()
    lang = "en"
    with smart_override(lang):
        renderer = menu_pool.get_renderer(category_request)
        renderer.get_nodes(category_request)
        keys = CacheKey.objects.get_keys().distinct().values_list("key", flat=True)
        assert cache.get_many(keys)
        app_config_test.delete()
        assert not (cache.get_many(keys))


@pytest.mark.django_db
def test_menu_cache_clear_category(category_request, page_with_menu):
    """
    Tests if menu cache is cleared after category deletion
    """

    from django.core.cache import cache
    from menus.menu_pool import menu_pool
    from menus.models import CacheKey

    from djangocms_stories.models import PostCategory

    lang = "en"
    with smart_override(lang):
        renderer = menu_pool.get_renderer(category_request)
        renderer.get_nodes(category_request)
        keys = CacheKey.objects.get_keys().distinct().values_list("key", flat=True)
        assert cache.get_many(keys)
        category_test = PostCategory.objects.create(name="category test", app_config=StoriesConfig.objects.first())
        category_test.set_current_language("it", initialize=True)
        category_test.name = "categoria test"
        category_test.save()
        assert not (cache.get_many(keys))
        renderer = menu_pool.get_renderer(category_request)
        renderer.get_nodes(category_request)
        keys = CacheKey.objects.get_keys().distinct().values_list("key", flat=True)
        assert cache.get_many(keys)
        category_test.delete()
        assert not (cache.get_many(keys))
        keys = CacheKey.objects.get_keys().distinct().values_list("key", flat=True)
        assert not keys


@pytest.mark.django_db
def test_menu_nodes(page_with_menu, many_posts):
    """
    Tests if all categories are present in the menu
    """
    from menus.menu_pool import menu_pool

    request = RequestFactory().get(page_with_menu.get_absolute_url())
    request.user = AnonymousUser()
    renderer = menu_pool.get_renderer(request)
    nodes = renderer.get_nodes(request)

    if apps.is_installed("djangocms_versioning"):
        # If versioning is installed, we have one more node for the page
        assert len(nodes) == len(many_posts) // 2 + 1 + 1  # +1 for the page and the category
        # The // 2 accounts for the fact that only half of the posts are published
    else:
        assert len(nodes) == len(many_posts) + 1 + 1  # +1 for the page and the category
