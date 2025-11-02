from unittest.mock import Mock, patch

import pytest
from django.test import RequestFactory
from django.urls import Resolver404
from djangocms_stories.models import StoriesConfig

from djangocms_stories.cms_appconfig import (
    config_defaults,
    get_app_instance,
    get_namespace_from_request,
)


@pytest.mark.django_db
def test_stories_config_str_returns_expected_string():
    config = StoriesConfig(namespace="ns", app_title="My App", object_name="Story")
    assert str(config) == "ns: My App / Story"


@pytest.mark.django_db
def test_stories_config_str_handles_exception():
    config = StoriesConfig(**config_defaults, namespace="ns")
    # Unsaved config does not have object_name, str access should handle that gracefully
    result = str(config)
    assert isinstance(result, str)


def test_stories_config_get_app_title_returns_app_title():
    config = StoriesConfig(**config_defaults, app_title="My App")
    assert config.get_app_title() == "My App"


def test_stories_config_get_app_title_returns_default():
    config = StoriesConfig()
    # Remove app_title to trigger default
    if hasattr(config, "app_title"):
        delattr(config, "app_title")
    assert config.get_app_title() == "untitled"


def test_stories_config_schemaorg_type_property():
    config = StoriesConfig(gplus_type="Article")
    assert config.schemaorg_type == "Article"


@pytest.mark.django_db
def test_stories_config_save_clears_menu_cache():
    config = StoriesConfig(**config_defaults, namespace="test")
    with patch("menus.menu_pool.menu_pool.clear") as mock_clear:
        config.save()
        mock_clear.assert_called_once_with(all=True)


@pytest.mark.django_db
def test_stories_config_delete_clears_menu_cache():
    config = StoriesConfig(**config_defaults, namespace="hero")
    config.save()
    with patch("menus.menu_pool.menu_pool.clear") as mock_clear:
        config.delete()
        mock_clear.assert_called_once_with(all=True)


# Tests for get_namespace_from_request function


def test_get_namespace_from_valid_path(simple_wo_placeholder):
    """Test getting namespace from a valid request path"""
    request = RequestFactory().get("/en/stories/")

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.return_value = Mock(namespace="test-namespace")

        result = get_namespace_from_request(request)

        assert result == "test-namespace"
        mock_resolve.assert_called_once_with(request.path_info)


def test_get_namespace_from_toolbar_request_path():
    """Test getting namespace from toolbar request_path (CMS v4)"""
    request = RequestFactory().get("/en/stories/")
    request.toolbar = Mock()
    request.toolbar.request_path = "/en/custom-path/"

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.return_value = Mock(namespace="toolbar-namespace")

        result = get_namespace_from_request(request)

        assert result == "toolbar-namespace"
        # Should use toolbar.request_path, not request.path_info
        mock_resolve.assert_called_once_with("/en/custom-path/")


def test_get_namespace_handles_resolver404():
    """Test that function returns None when path cannot be resolved (404)"""
    request = RequestFactory().get("/nonexistent/path/")

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.side_effect = Resolver404("URL not found")

        result = get_namespace_from_request(request)

        assert result is None
        mock_resolve.assert_called_once_with(request.path_info)


def test_get_namespace_handles_resolver404_with_toolbar():
    """Test that function returns None on 404 even with toolbar present"""
    request = RequestFactory().get("/nonexistent/path/")
    request.toolbar = Mock()
    request.toolbar.request_path = "/invalid/toolbar/path/"

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.side_effect = Resolver404("URL not found")

        result = get_namespace_from_request(request)

        assert result is None
        mock_resolve.assert_called_once_with("/invalid/toolbar/path/")


def test_get_namespace_without_toolbar_attribute():
    """Test getting namespace when request has no toolbar attribute"""
    request = RequestFactory().get("/en/stories/")
    # Explicitly ensure no toolbar attribute
    assert not hasattr(request, "toolbar")

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.return_value = Mock(namespace="no-toolbar-namespace")

        result = get_namespace_from_request(request)

        assert result == "no-toolbar-namespace"
        mock_resolve.assert_called_once_with(request.path_info)


def test_get_namespace_with_toolbar_but_no_request_path():
    """Test getting namespace when toolbar exists but has no request_path"""
    request = RequestFactory().get("/en/stories/")
    request.toolbar = Mock(spec=[])  # Mock without request_path attribute

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.return_value = Mock(namespace="fallback-namespace")

        result = get_namespace_from_request(request)

        assert result == "fallback-namespace"
        # Should fall back to path_info
        mock_resolve.assert_called_once_with(request.path_info)


# Tests for get_app_instance function


@pytest.mark.django_db
def test_get_app_instance_returns_none_on_404():
    """Test that get_app_instance handles 404 gracefully"""
    request = RequestFactory().get("/nonexistent/path/")

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        mock_get_namespace.return_value = None

        namespace, config = get_app_instance(request)

        assert namespace is None
        assert config is None


@pytest.mark.django_db
def test_get_app_instance_without_current_page(simple_wo_placeholder):
    """Test get_app_instance when request has no current_page"""
    request = RequestFactory().get("/en/stories/")

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        with patch("djangocms_stories.cms_appconfig.StoriesConfig.objects.get") as mock_get_config:
            mock_get_namespace.return_value = "test-namespace"
            mock_get_config.return_value = simple_wo_placeholder

            namespace, config = get_app_instance(request)

            assert namespace == "test-namespace"
            assert config == simple_wo_placeholder
            mock_get_config.assert_called_once_with(namespace="test-namespace")


@pytest.mark.django_db
def test_get_app_instance_config_does_not_exist():
    """Test get_app_instance when config doesn't exist in database"""

    request = RequestFactory().get("/en/stories/")

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        mock_get_namespace.return_value = "nonexistent-namespace"

        namespace, config = get_app_instance(request)

        assert namespace == "nonexistent-namespace"
        assert config is None


@pytest.mark.django_db
def test_get_app_instance_multiple_configs_returned(simple_wo_placeholder):
    """Test get_app_instance when multiple configs match (should return None)"""

    request = RequestFactory().get("/en/stories/")

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        with patch("djangocms_stories.cms_appconfig.StoriesConfig.objects.get") as mock_get_config:
            mock_get_namespace.return_value = "duplicate-namespace"
            mock_get_config.side_effect = StoriesConfig.MultipleObjectsReturned()

            namespace, config = get_app_instance(request)

            assert namespace == "duplicate-namespace"
            assert config is None


@pytest.mark.django_db
def test_get_app_instance_with_cms_page_and_apphook(simple_wo_placeholder):
    """Test get_app_instance when request has a CMS page with apphook"""

    request = RequestFactory().get("/en/stories/")

    # Create a mock page with application_urls
    mock_page = Mock()
    mock_page.application_urls = "StoriesApp"
    request.current_page = mock_page

    # Mock the apphook
    mock_app = Mock()
    mock_app.app_config = True
    mock_app.get_config.return_value = simple_wo_placeholder

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        with patch("djangocms_stories.cms_appconfig.apphook_pool.get_apphook") as mock_get_apphook:
            mock_get_namespace.return_value = "test-namespace"
            mock_get_apphook.return_value = mock_app

            namespace, config = get_app_instance(request)

            assert namespace == "test-namespace"
            assert config == simple_wo_placeholder
            mock_app.get_config.assert_called_once_with("test-namespace")


@pytest.mark.django_db
def test_get_app_instance_with_page_but_no_apphook():
    """Test get_app_instance when page exists but has no application_urls"""
    request = RequestFactory().get("/en/stories/")

    # Create a mock page without application_urls
    mock_page = Mock()
    mock_page.application_urls = True  # Some truthy value
    request.current_page = mock_page

    with patch("djangocms_stories.cms_appconfig.get_namespace_from_request") as mock_get_namespace:
        with patch("djangocms_stories.cms_appconfig.StoriesConfig.objects.get") as mock_get_config:
            mock_get_namespace.return_value = "test-namespace"
            mock_get_config.side_effect = Exception("Should not be called")

            namespace, config = get_app_instance(request)

            # Since application_urls is falsy, should not attempt to get config
            assert namespace == "test-namespace"
            assert config is None


@pytest.mark.django_db
def test_get_app_instance_resolver404_during_namespace_retrieval():
    """Test that get_app_instance handles 404 during namespace retrieval"""
    request = RequestFactory().get("/nonexistent/path/")

    with patch("djangocms_stories.cms_appconfig.resolve") as mock_resolve:
        mock_resolve.side_effect = Resolver404("URL not found")

        namespace, config = get_app_instance(request)

        # Should handle the 404 gracefully
        assert namespace is None
        assert config is None
