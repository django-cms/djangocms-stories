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


@pytest.mark.django_db
@pytest.mark.parametrize("bulk_action", [True, False])
def test_menu_updates_after_featuring(page_with_menu, admin_user, admin_client, default_config, bulk_action):
    """Bulk actions and direct saves update an already cached public menu."""
    import datetime

    from django.urls import reverse
    from django.utils.timezone import now
    from menus.menu_pool import menu_pool

    from djangocms_stories.models import PostCategory

    from tests.factories import PostContentFactory
    from tests.utils import publish_if_necessary

    category = PostCategory.objects.active_translations(slug="test-category").get()
    older, newer = (
        PostContentFactory(
            language="en",
            post__app_config=default_config,
            post__date_published=now() - datetime.timedelta(days=days),
            post__date_featured=None,
        )
        for days in (20, 10)
    )
    for post_content in (older, newer):
        post_content.post.categories.add(category)
    publish_if_necessary([older, newer], admin_user)

    def menu_titles():
        request = RequestFactory().get(page_with_menu.get_absolute_url())
        request.user = AnonymousUser()
        return [node.title for node in menu_pool.get_renderer(request).get_nodes(request)]

    menu_pool.clear(all=True)
    titles = menu_titles()
    assert titles.index(newer.title) < titles.index(older.title)

    url = reverse("admin:djangocms_stories_post_changelist")
    for action, first, second in (("feature", older, newer), ("unfeature", newer, older)):
        if bulk_action:
            response = admin_client.post(url, {"action": action, "_selected_action": [older.post_id]})
            assert response.status_code == 302
        else:
            older.post.date_featured = now() if action == "feature" else None
            older.post.save(update_fields=["date_featured"])
        titles = menu_titles()
        assert titles.index(first.title) < titles.index(second.title)


@pytest.mark.django_db
@pytest.mark.parametrize("menu_timeout", [3600, None])
def test_menu_cache_expires_before_scheduled_featuring(
    page_with_menu, admin_user, default_config, monkeypatch, settings, menu_timeout
):
    from datetime import timedelta
    from unittest.mock import patch

    from cms.utils.conf import get_cms_setting
    from django.db.models import Value
    from django.db.models.functions import Now
    from django.utils.timezone import now
    from menus.menu_pool import menu_pool

    from djangocms_stories.models import PostCategory

    from .factories import PostContentFactory
    from .utils import publish_if_necessary

    settings.CMS_CACHE_DURATIONS = {**get_cms_setting("CACHE_DURATIONS"), "menus": menu_timeout}
    current = now()
    category = PostCategory.objects.active_translations(slug="test-category").get()
    older, newer = (
        PostContentFactory(
            language="en",
            post__app_config=default_config,
            post__date_published=current - timedelta(days=days),
            post__date_featured=None,
        )
        for days in (20, 10)
    )
    for content in (older, newer):
        content.post.categories.add(category)
    publish_if_necessary([older, newer], admin_user)
    older.post.date_featured = current + timedelta(minutes=1)
    older.post.save()

    monkeypatch.setattr("time.time", lambda: current.timestamp())
    monkeypatch.setattr("djangocms_stories.cms_menus.now", lambda: current)
    monkeypatch.setattr(
        Now, "as_sqlite", lambda self, compiler, connection, **kwargs: compiler.compile(Value(current))
    )

    def menu_titles():
        request = RequestFactory().get(page_with_menu.get_absolute_url())
        request.user = AnonymousUser()
        return [node.title for node in menu_pool.get_renderer(request).get_nodes()]

    menu_pool.clear(all=True)
    with patch.object(PostCategoryMenu, "get_nodes", autospec=True, side_effect=PostCategoryMenu.get_nodes) as build:
        titles = menu_titles()
        assert titles.index(newer.title) < titles.index(older.title)
        builds = build.call_count
        current += timedelta(seconds=30)
        assert menu_titles() == titles
        assert build.call_count == builds  # Keep using the cache before the scheduled date.
        current += timedelta(seconds=31)
        titles = menu_titles()
        assert titles.index(older.title) < titles.index(newer.title)
        assert build.call_count > builds


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
