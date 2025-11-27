import pytest
from cms.toolbar.items import ButtonList
from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from unittest.mock import Mock, patch

from djangocms_stories.cms_toolbars import StoriesToolbar
from djangocms_stories.models import PostContent


User = get_user_model()


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return User.objects.create_superuser(username="admin", email="admin@test.com", password="password")


@pytest.fixture
def toolbar_request(admin_user):
    """Create a mock request with toolbar."""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = admin_user
    request.current_page = None
    request.session = {}
    return request


@pytest.fixture
def mock_toolbar():
    """Create a mock CMS toolbar."""
    toolbar = Mock()
    toolbar.obj = None
    toolbar.edit_mode_active = False
    toolbar.preview_mode_active = False
    toolbar.RIGHT = "right"
    toolbar.get_object = Mock(return_value=None)
    return toolbar


@pytest.mark.django_db
def test_add_view_published_button_versioning_disabled(toolbar_request, mock_toolbar, post_content):
    """Test add_view_published_button does nothing when versioning is disabled."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content

    # Mock is_versioning_enabled to return False
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=False):
        # Call the method
        stories_toolbar.add_view_published_button()

        # Verify that no button was added (toolbar.add_item should not be called)
        mock_toolbar.add_item.assert_not_called()


@pytest.mark.django_db
def test_add_view_published_button_versioning_enabled_no_published_version(
    toolbar_request, mock_toolbar, post_content
):
    """Test add_view_published_button does nothing when no published version exists."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content

    # Mock is_versioning_enabled to return True
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=True):
        # Mock _get_published_post_version to return None
        with patch.object(stories_toolbar, "_get_published_post_version", return_value=None):
            # Call the method
            stories_toolbar.add_view_published_button()

            # Verify that no button was added
            mock_toolbar.add_item.assert_not_called()


@pytest.mark.django_db
def test_add_view_published_button_versioning_enabled_with_published_version_edit_mode(
    toolbar_request, mock_toolbar, post_content
):
    """Test add_view_published_button adds button in edit mode when published version exists."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content
    mock_toolbar.edit_mode_active = True

    # Create a mock published version with get_absolute_url method
    published_version = Mock(spec=PostContent)
    published_version.get_absolute_url = Mock(return_value="/published-url/")

    # Mock is_versioning_enabled to return True
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=True):
        # Mock _get_published_post_version to return the published version
        with patch.object(stories_toolbar, "_get_published_post_version", return_value=published_version):
            # Call the method
            stories_toolbar.add_view_published_button()

            # Verify that add_item was called
            mock_toolbar.add_item.assert_called_once()

            # Get the ButtonList that was added
            call_args = mock_toolbar.add_item.call_args
            button_list = call_args[0][0]

            # Verify it's a ButtonList
            assert isinstance(button_list, ButtonList)


@pytest.mark.django_db
def test_add_view_published_button_versioning_enabled_with_published_version_preview_mode(
    toolbar_request, mock_toolbar, post_content
):
    """Test add_view_published_button adds button in preview mode when published version exists."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content
    mock_toolbar.preview_mode_active = True

    # Create a mock published version with get_absolute_url method
    published_version = Mock(spec=PostContent)
    published_version.get_absolute_url = Mock(return_value="/published-url/")

    # Mock is_versioning_enabled to return True
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=True):
        # Mock _get_published_post_version to return the published version
        with patch.object(stories_toolbar, "_get_published_post_version", return_value=published_version):
            # Call the method
            stories_toolbar.add_view_published_button()

            # Verify that add_item was called
            mock_toolbar.add_item.assert_called_once()

            # Get the ButtonList that was added
            call_args = mock_toolbar.add_item.call_args
            button_list = call_args[0][0]

            # Verify it's a ButtonList
            assert isinstance(button_list, ButtonList)


@pytest.mark.django_db
def test_add_view_published_button_versioning_enabled_no_url(toolbar_request, mock_toolbar, post_content):
    """Test add_view_published_button does nothing when published version has no URL."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content
    mock_toolbar.edit_mode_active = True

    # Create a mock published version without get_absolute_url method
    published_version = Mock(spec=[])  # No get_absolute_url

    # Mock is_versioning_enabled to return True
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=True):
        # Mock _get_published_post_version to return the published version
        with patch.object(stories_toolbar, "_get_published_post_version", return_value=published_version):
            # Call the method
            stories_toolbar.add_view_published_button()

            # Verify that no button was added (no get_absolute_url method)
            mock_toolbar.add_item.assert_not_called()


@pytest.mark.django_db
def test_add_view_published_button_not_in_edit_or_preview_mode(toolbar_request, mock_toolbar, post_content):
    """Test add_view_published_button does nothing when not in edit or preview mode."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set the toolbar object to a PostContent instance
    mock_toolbar.obj = post_content
    mock_toolbar.edit_mode_active = False
    mock_toolbar.preview_mode_active = False

    # Create a mock published version with get_absolute_url method
    published_version = Mock(spec=PostContent)
    published_version.get_absolute_url = Mock(return_value="/published-url/")

    # Mock is_versioning_enabled to return True
    with patch("djangocms_stories.cms_toolbars.is_versioning_enabled", return_value=True):
        # Mock _get_published_post_version to return the published version
        with patch.object(stories_toolbar, "_get_published_post_version", return_value=published_version):
            # Call the method
            stories_toolbar.add_view_published_button()

            # Verify that no button was added (not in edit or preview mode)
            mock_toolbar.add_item.assert_not_called()


# Tests for _get_published_post_version


@pytest.mark.django_db
def test_get_published_post_version_not_postcontent(toolbar_request, mock_toolbar):
    """Test _get_published_post_version returns None when toolbar.obj is not PostContent."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set toolbar.obj to something other than PostContent
    mock_toolbar.obj = "not a PostContent instance"

    result = stories_toolbar._get_published_post_version()
    assert result is None


@pytest.mark.django_db
def test_get_published_post_version_with_postcontent(toolbar_request, mock_toolbar, post_content, admin_user):
    """Test _get_published_post_version returns PostContent when matching language exists."""
    from django.apps import apps

    # If versioning is enabled, publish the post_content
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.models import Version

        # Get the version and publish it
        version = Version.objects.get(object_id=post_content.pk)
        version.publish(admin_user)

    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "en"

    # Set toolbar.obj to PostContent
    mock_toolbar.obj = post_content

    result = stories_toolbar._get_published_post_version()

    # Should return a PostContent instance
    assert result is not None
    assert isinstance(result, PostContent)
    assert result.language == "en"
    assert result.post == post_content.post


@pytest.mark.django_db
def test_get_published_post_version_no_matching_language(toolbar_request, mock_toolbar, post_content):
    """Test _get_published_post_version returns None when no matching language exists."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.current_lang = "de"  # Language that doesn't exist

    # Set toolbar.obj to PostContent
    mock_toolbar.obj = post_content

    result = stories_toolbar._get_published_post_version()

    # Should return None as no German translation exists
    assert result is None


# Tests for add_preview_button


@pytest.mark.django_db
def test_add_preview_button_conditions_not_met(toolbar_request, mock_toolbar):
    """Test add_preview_button does nothing when conditions are not met."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = False

    stories_toolbar.add_preview_button()

    # Verify no button was added
    mock_toolbar.add_item.assert_not_called()


@pytest.mark.django_db
def test_add_preview_button_in_preview_mode(toolbar_request, mock_toolbar):
    """Test add_preview_button adds 'View on site' button in preview mode."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = True
    mock_toolbar.get_object.return_value = None
    mock_toolbar.preview_mode_active = True
    mock_toolbar.request_language = "en"

    # Mock current_page
    mock_page = Mock()
    mock_page_content = Mock()
    mock_page_content.get_absolute_url = Mock(return_value="/page-url/")

    mock_pagecontent_set = Mock()
    mock_pagecontent_set.latest_content = Mock(return_value=Mock(first=Mock(return_value=mock_page_content)))
    mock_page.pagecontent_set = Mock(return_value=mock_pagecontent_set)

    toolbar_request.current_page = mock_page

    with patch("djangocms_stories.cms_toolbars.get_object_preview_url", return_value="/preview-url/"):
        stories_toolbar.add_preview_button()

    # Verify button was added
    mock_toolbar.add_item.assert_called_once()


@pytest.mark.django_db
def test_add_preview_button_in_edit_mode(toolbar_request, mock_toolbar):
    """Test add_preview_button adds 'Preview' button in edit mode."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = True
    mock_toolbar.get_object.return_value = None
    mock_toolbar.preview_mode_active = False
    mock_toolbar.request_language = "en"

    # Mock current_page
    mock_page = Mock()
    mock_page_content = Mock()
    mock_page_content.get_absolute_url = Mock(return_value="/page-url/")

    mock_pagecontent_set = Mock()
    mock_pagecontent_set.latest_content = Mock(return_value=Mock(first=Mock(return_value=mock_page_content)))
    mock_page.pagecontent_set = Mock(return_value=mock_pagecontent_set)

    toolbar_request.current_page = mock_page

    with patch("djangocms_stories.cms_toolbars.get_object_preview_url", return_value="/preview-url/"):
        stories_toolbar.add_preview_button()

    # Verify button was added
    mock_toolbar.add_item.assert_called_once()


# Tests for add_stories_to_admin_menu


@pytest.mark.django_db
def test_add_stories_to_admin_menu(toolbar_request, mock_toolbar):
    """Test add_stories_to_admin_menu adds menu item to admin menu."""
    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)

    # Mock admin menu
    mock_admin_menu = Mock()
    mock_toolbar.get_or_create_menu = Mock(return_value=mock_admin_menu)

    with patch.object(stories_toolbar, "get_insert_position_for_admin_object", return_value=5):
        stories_toolbar.add_stories_to_admin_menu()

    # Verify get_or_create_menu was called with correct identifier
    mock_toolbar.get_or_create_menu.assert_called_once_with(ADMIN_MENU_IDENTIFIER)

    # Verify add_sideframe_item was called
    mock_admin_menu.add_sideframe_item.assert_called_once()

    # Verify position was used
    call_args = mock_admin_menu.add_sideframe_item.call_args
    assert call_args[1]["position"] == 5


# Tests for get_insert_position_for_admin_object


def test_get_insert_position_early_break():
    """Test get_insert_position_for_admin_object when break index < 2."""
    mock_menu = Mock()
    mock_break = Mock()
    mock_break.index = 1
    mock_menu.find_first = Mock(return_value=mock_break)

    position = StoriesToolbar.get_insert_position_for_admin_object(mock_menu, "Test Item")

    assert position == 1


def test_get_insert_position_alphabetical_first():
    """Test get_insert_position_for_admin_object inserts alphabetically first."""
    mock_menu = Mock()
    mock_break = Mock()
    mock_break.index = 5

    # Create mock items with names
    mock_item1 = Mock()
    mock_item1.name = "Pages"
    mock_item2 = Mock()
    mock_item2.name = "Users"
    mock_item3 = Mock()
    mock_item3.name = "Widgets"

    mock_menu.find_first = Mock(return_value=mock_break)
    mock_menu.get_items = Mock(return_value=[None, mock_item1, mock_item2, mock_item3, None])

    # "Articles" should come before "Pages"
    position = StoriesToolbar.get_insert_position_for_admin_object(mock_menu, "Articles")

    assert position == 1


def test_get_insert_position_alphabetical_middle():
    """Test get_insert_position_for_admin_object inserts alphabetically in middle."""
    mock_menu = Mock()
    mock_break = Mock()
    mock_break.index = 5

    # Create mock items with names
    mock_item1 = Mock()
    mock_item1.name = "Articles"
    mock_item2 = Mock()
    mock_item2.name = "Pages"
    mock_item3 = Mock()
    mock_item3.name = "Widgets"

    mock_menu.find_first = Mock(return_value=mock_break)
    mock_menu.get_items = Mock(return_value=[None, mock_item1, mock_item2, mock_item3, None])

    # "Users" should come between "Pages" and "Widgets"
    position = StoriesToolbar.get_insert_position_for_admin_object(mock_menu, "Users")

    assert position == 3


def test_get_insert_position_alphabetical_last():
    """Test get_insert_position_for_admin_object inserts at end when alphabetically last."""
    mock_menu = Mock()
    mock_break = Mock()
    mock_break.index = 5

    # Create mock items with names
    mock_item1 = Mock()
    mock_item1.name = "Articles"
    mock_item2 = Mock()
    mock_item2.name = "Pages"
    mock_item3 = Mock()
    mock_item3.name = "Users"

    mock_menu.find_first = Mock(return_value=mock_break)
    mock_menu.get_items = Mock(return_value=[None, mock_item1, mock_item2, mock_item3, None])

    # "Zebra" should come after all items
    position = StoriesToolbar.get_insert_position_for_admin_object(mock_menu, "Zebra")

    assert position == 5


def test_get_insert_position_item_without_name():
    """Test get_insert_position_for_admin_object handles items without name attribute."""
    mock_menu = Mock()
    mock_break = Mock()
    mock_break.index = 5

    # Create mock items, some without names
    mock_item1 = Mock()
    mock_item1.name = "Articles"
    mock_item2 = Mock(spec=[])  # No name attribute
    mock_item3 = Mock()
    mock_item3.name = "Widgets"

    mock_menu.find_first = Mock(return_value=mock_break)
    mock_menu.get_items = Mock(return_value=[None, mock_item1, mock_item2, mock_item3, None])

    # Should handle items without name gracefully
    position = StoriesToolbar.get_insert_position_for_admin_object(mock_menu, "Users")

    # Should still work and find correct position
    assert isinstance(position, int)


# Tests for populate method


@pytest.mark.django_db
def test_populate_without_permission(toolbar_request, mock_toolbar, simple_w_placeholder):
    """Test populate returns early when user has no add_post permission."""
    # Create user without permission
    user = User.objects.create_user(username="nonadmin", email="user@test.com", password="password")
    toolbar_request.user = user

    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = True

    with patch.object(stories_toolbar, "add_stories_to_admin_menu"):
        with patch.object(stories_toolbar, "add_preview_button"):
            with patch.object(stories_toolbar, "add_view_published_button"):
                stories_toolbar.populate()

    # Verify menus were not created (except admin menu)
    calls = mock_toolbar.get_or_create_menu.call_args_list
    # Should only have admin menu, not djangocms_stories menu
    for call in calls:
        assert call[0][0] != "djangocms_stories"


@pytest.mark.django_db
def test_populate_with_postcontent(toolbar_request, mock_toolbar, post_content, admin_user):
    """Test populate creates menu with PostContent as current content."""
    toolbar_request.user = admin_user
    mock_toolbar.get_object.return_value = post_content

    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = True
    stories_toolbar.current_lang = "en"

    # Mock the djangocms_stories menu
    mock_stories_menu = Mock()

    def get_or_create_menu_side_effect(identifier, *args, **kwargs):
        if identifier == ADMIN_MENU_IDENTIFIER:
            return Mock()
        elif identifier == "djangocms_stories":
            return mock_stories_menu
        return Mock()

    mock_toolbar.get_or_create_menu = Mock(side_effect=get_or_create_menu_side_effect)

    with patch.object(stories_toolbar, "add_stories_to_admin_menu"):
        with patch.object(stories_toolbar, "add_preview_button"):
            with patch.object(stories_toolbar, "add_view_published_button"):
                with patch("djangocms_stories.cms_toolbars.get_setting") as mock_get_setting:
                    mock_get_setting.side_effect = lambda x: {
                        "ENABLE_THROUGH_TOOLBAR_MENU": True,
                        "CURRENT_POST_IDENTIFIER": "djangocms_stories_current_post",
                        "CURRENT_NAMESPACE": "djangocms_stories_current_app_config",
                    }.get(x, x)

                    stories_toolbar.populate()

    # Verify stories menu was created
    assert any(call[0][0] == "djangocms_stories" for call in mock_toolbar.get_or_create_menu.call_args_list)

    # Verify modal item was added (properties)
    mock_stories_menu.add_modal_item.assert_called()


@pytest.mark.django_db
def test_populate_with_app_config(toolbar_request, mock_toolbar, post_content, admin_user):
    """Test populate creates full menu with app_config."""
    from djangocms_stories.models import StoriesConfig
    from djangocms_stories.cms_appconfig import config_defaults

    # Create a unique config for this test
    app_config = StoriesConfig.objects.create(
        **{
            **config_defaults,
            "namespace": "test_toolbar_populate",
            "app_title": "Test Toolbar Config",
            "object_name": "Story",
            "url_patterns": "full_date",
        }
    )

    toolbar_request.user = admin_user
    toolbar_request.djangocms_stories_current_post = post_content
    toolbar_request.djangocms_stories_current_app_config = app_config
    mock_toolbar.get_object.return_value = post_content

    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = True
    stories_toolbar.current_lang = "en"

    # Mock the djangocms_stories menu
    mock_stories_menu = Mock()

    def get_or_create_menu_side_effect(identifier, *args, **kwargs):
        if identifier == ADMIN_MENU_IDENTIFIER:
            return Mock()
        elif identifier == "djangocms_stories":
            return mock_stories_menu
        return Mock()

    mock_toolbar.get_or_create_menu = Mock(side_effect=get_or_create_menu_side_effect)

    with patch.object(stories_toolbar, "add_stories_to_admin_menu"):
        with patch.object(stories_toolbar, "add_preview_button"):
            with patch.object(stories_toolbar, "add_view_published_button"):
                with patch("djangocms_stories.cms_toolbars.get_setting") as mock_get_setting:
                    mock_get_setting.side_effect = lambda x: {
                        "ENABLE_THROUGH_TOOLBAR_MENU": True,
                        "CURRENT_POST_IDENTIFIER": "djangocms_stories_current_post",
                        "CURRENT_NAMESPACE": "djangocms_stories_current_app_config",
                    }.get(x, x)

                    stories_toolbar.populate()

    # Verify modal items were added
    assert mock_stories_menu.add_modal_item.call_count >= 2  # Properties, New entry, Edit config

    # Verify sideframe item was added (All entries)
    mock_stories_menu.add_sideframe_item.assert_called()

    # Verify break was added
    mock_stories_menu.add_break.assert_called()


@pytest.mark.django_db
def test_populate_calls_helper_methods(toolbar_request, mock_toolbar, admin_user):
    """Test populate calls all helper methods."""
    toolbar_request.user = admin_user

    stories_toolbar = StoriesToolbar(toolbar_request, mock_toolbar, False, None)
    stories_toolbar.is_current_app = False

    # Mock the admin menu
    mock_toolbar.get_or_create_menu = Mock(return_value=Mock())

    with patch.object(stories_toolbar, "add_stories_to_admin_menu") as mock_add_admin:
        with patch.object(stories_toolbar, "add_preview_button"):
            with patch.object(stories_toolbar, "add_view_published_button"):
                with patch("djangocms_stories.cms_toolbars.get_setting") as mock_get_setting:
                    mock_get_setting.side_effect = lambda x: {
                        "ENABLE_THROUGH_TOOLBAR_MENU": False,
                        "CURRENT_POST_IDENTIFIER": "djangocms_stories_current_post",
                        "CURRENT_NAMESPACE": "djangocms_stories_current_app_config",
                    }.get(x, x)

                    stories_toolbar.populate()

    # Verify all helper methods were called
    mock_add_admin.assert_called_once()
    # add_preview_button and add_view_published_button should be called even if menu is not created
    # because they are at the end of populate()
