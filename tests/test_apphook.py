import os
from unittest.mock import Mock

import pytest
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.urls import resolve, reverse
from django.utils import lorem_ipsum

from djangocms_stories.cms_apps import StoriesApp
from djangocms_stories.cms_appconfig import get_app_instance
from djangocms_stories.views import PostListView

from .utils import publish_if_necessary


def test_apphook(admin_client, simple_wo_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from cms.utils.apphook_reload import reload_urlconf

    from .factories import PostContentFactory, UserFactory

    user = UserFactory(is_staff=True)
    batch = PostContentFactory.create_batch(
        5,
        language="en",
        post__app_config=simple_wo_placeholder,
        title=lorem_ipsum.words(3),
        post_text=lorem_ipsum.sentence(),
    )
    publish_if_necessary(batch, user)

    page = api.create_page(
        title="Test Page",
        template="base.html",
        language="en",
        apphook="StoriesApp",
        apphook_namespace=simple_wo_placeholder.namespace,
    )
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.models import Version

        page_content = page.pagecontent_set(manager="admin_manager").get(language="en")
        version = Version.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_content),
            object_id=page_content.pk,
            created_by=user,
        )[0]
        version.publish(user)

    reload_urlconf()

    # The appconfig can be retrieved from a request
    request = RequestFactory().get(page.get_absolute_url("en") + "some/path/")
    namespace, config = get_app_instance(request)

    assert namespace == simple_wo_placeholder.namespace
    assert config == simple_wo_placeholder

    # The django url resolver identifies the apphook namespace
    resolved = resolve(page.get_absolute_url("en"))
    assert resolved.namespace == simple_wo_placeholder.namespace
    assert resolved.view_name == f"{simple_wo_placeholder.namespace}:posts-latest"

    # The appohook can coexist with a django instance of stories
    assert reverse(f"{simple_wo_placeholder.namespace}:posts-latest") != reverse("djangocms_stories:posts-latest")

    url = get_object_preview_url(page.get_admin_content("en"))
    response = admin_client.get(url, follow=True)
    assert response.status_code == 200
    for post_content in batch:
        assert_html_in_response(
            post_content.title,
            response,
        )
        assert_html_in_response(
            post_content.abstract,
            response,
        )


def test_get_root_template_without_page():
    """Without a page argument the apphook returns None."""
    assert StoriesApp().get_root_template() is None
    assert StoriesApp().get_root_template(page=None) is None


@pytest.mark.django_db
def test_get_root_template_with_page_falls_back_to_default(simple_wo_placeholder):
    """An empty template_prefix falls back to the 'djangocms_stories' folder."""
    page = Mock(application_namespace=simple_wo_placeholder.namespace)

    template = StoriesApp().get_root_template(page=page)

    assert template == os.path.join("djangocms_stories", PostListView.base_template_name)


@pytest.mark.django_db
def test_get_root_template_uses_config_template_prefix(simple_wo_placeholder):
    """A configured template_prefix is used as the template folder."""
    simple_wo_placeholder.template_prefix = "custom/templates"
    simple_wo_placeholder.save()
    page = Mock(application_namespace=simple_wo_placeholder.namespace)

    template = StoriesApp().get_root_template(page=page)

    assert template == os.path.join("custom/templates", PostListView.base_template_name)


@pytest.mark.django_db
def test_get_root_template_with_unknown_namespace_falls_back_to_default():
    """An unknown namespace yields no config and falls back to the default folder."""
    page = Mock(application_namespace="does-not-exist")

    template = StoriesApp().get_root_template(page=page)

    assert template == os.path.join("djangocms_stories", PostListView.base_template_name)
