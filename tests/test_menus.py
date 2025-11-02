import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from djangocms_blog.settings import MENU_TYPE_CATEGORIES, MENU_TYPE_NONE
from djangocms_stories.cms_menus import PostCategoryMenu, PostCategoryNavModifier


@pytest.mark.django_db
def test_nav_modifier_with_invalid_path(page_with_menu):
    """
    Tests that PostCategoryNavModifier does not fail with invalid request paths
    """
    from menus.menu_pool import menu_pool

    request = RequestFactory().get("/nonexistent/path/")
    request.user = AnonymousUser()
    request.current_page = page_with_menu

    renderer = menu_pool.get_renderer(request)
    modifier = PostCategoryNavModifier(renderer)
    nodes = []

    # Should not raise an exception
    try:
        modifier.modify(request, nodes, namespace=None, root_id=None, post_cut=False, breadcrumb=False)
    except Exception as e:
        pytest.fail(f"PostCategoryNavModifier raised an exception with invalid path: {e}")


@pytest.mark.django_db
def test_menu_nodes(page_with_menu, many_posts):
    """
    Tests if all categories are present in the menu
    """
    from menus.menu_pool import menu_pool

    request = RequestFactory().get(page_with_menu.get_absolute_url())
    request.user = AnonymousUser()
    menu_pool.clear(all=True)
    renderer = menu_pool.get_renderer(request)
    nodes = renderer.get_nodes(request)

    if apps.is_installed("djangocms_versioning"):
        # If versioning is installed, we have one more node for the page
        assert len(nodes) == len(many_posts) // 2 + 1 + 1  # +1 for the page and the category
        # The // 2 accounts for the fact that only half of the posts are published
    else:
        assert len(nodes) == len(many_posts) + 1 + 1  # +1 for the page and the category


def test_menu_configs(page_with_menu, default_config):
    from menus.menu_pool import menu_pool

    request = RequestFactory().get(page_with_menu.get_absolute_url())
    request.user = AnonymousUser()

    # Set the menu type category
    for menu in menu_pool.menus.values():
        if issubclass(menu, PostCategoryMenu):
            menu._config[default_config.namespace].menu_structure = MENU_TYPE_CATEGORIES

    # Clear all caches
    menu_pool.clear(all=True)

    renderer = menu_pool.get_renderer(request)
    nodes = renderer.get_nodes(request)
    assert len(nodes) == 2  # Only the category and the page should be present

    # Set the menu type category
    for menu in menu_pool.menus.values():
        if issubclass(menu, PostCategoryMenu):
            menu._config[default_config.namespace].menu_structure = MENU_TYPE_NONE

    # Clear all caches
    menu_pool.clear(all=True)

    renderer = menu_pool.get_renderer(request)
    nodes = renderer.get_nodes(request)
    assert len(nodes) == 1  # Only the page should be present
