import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from djangocms_blog.settings import MENU_TYPE_CATEGORIES


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


def test_menu_configs(page_with_menu, simple_w_placeholder):
    from menus.menu_pool import menu_pool

    simple_w_placeholder.menu_structure = MENU_TYPE_CATEGORIES
    simple_w_placeholder.menu_empty_categories = False
    simple_w_placeholder.save()

    request = RequestFactory().get(page_with_menu.get_absolute_url())
    request.user = AnonymousUser()
    menu_pool.clear(all=True)
    renderer = menu_pool.get_renderer(request)
    nodes = renderer.get_nodes(request)
    assert len(nodes) == 2  # Only the category and the page should be present
