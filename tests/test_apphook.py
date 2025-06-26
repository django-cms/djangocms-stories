from django.urls import resolve, reverse

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.utils import lorem_ipsum
from djangocms_stories.cms_appconfig import get_app_instance

from .utils import publish_if_necessary


def test_apphook(admin_client, simple_wo_placeholder, assert_html_in_response):
    from cms import api
    from cms.toolbar.utils import get_object_preview_url
    from cms.utils.apphook_reload import reload_urlconf

    from .factories import UserFactory, PostContentFactory

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
