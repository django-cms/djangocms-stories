
import pytest

try:
    from cms.wizards.wizard_base import get_entries
except (ImportError, ModuleNotFoundError):
    from cms.wizards.helpers import get_entries


@pytest.mark.django_db
def test_wizard_registered(default_config):
    """
    Test that Blog wizard is present and contains all items
    """
    from django.apps import apps

    cms_config = apps.get_app_config("djangocms_stories").cms_config
    wizard_entries = cms_config.cms_wizards
    assert any(wizard.title == "New Story" for wizard in wizard_entries), "Post wizard not found"


def test_wizard_form(admin_client, admin_user, simple_w_placeholder, simple_wo_placeholder):
    from django.apps import apps
    from djangocms_stories.models import PostContent
    from djangocms_text.models import Text
    from cms.utils.permissions import set_current_user

    cms_config = apps.get_app_config("djangocms_stories").cms_config
    wizs = [entry for entry in cms_config.cms_wizards if entry.model == PostContent]

    set_current_user(admin_user)
    for index, wiz in enumerate(wizs):
        form = wiz.form()
        app_config_pk = form.default_appconfig

        form = wiz.form(
            data={
                    "1-title": "title{}".format(index),
                    "1-abstract": "abstract{}".format(index),
                    "1-post_text": "Random text",
                },
            prefix=1,
        )
        form.language_code = "en"

        assert form.is_valid()
        assert form.cleaned_data["app_config"], app_config_pk

        instance = form.save()
        assert instance.slug == f"title{index}"
        if form.cleaned_data["app_config"].use_placeholder:
            assert instance.post_text == ""  # post_text moved to placeholder
            assert instance.content.get_plugins().filter(plugin_type="TextPlugin").count() == 1  # TextPlugin created
            plugin = Text.objects.get(pk=instance.content.get_plugins().get(plugin_type="TextPlugin").pk)
            assert plugin.body == "Random text"
        else:
            assert instance.content.get_plugins().filter(plugin_type="TextPlugin").count() == 0  # TextPlugin not created
            assert instance.post_text == "Random text"  # post_text remains in model

        form = wiz.form(
            data={
                    "1-title": "title{}".format(index),
                    "1-abstract": "abstract{}".format(index),
                    "1-post_text": "",  # Do never create a empty TextPlugin
                },
            prefix=1,
        )
        form.language_code = "en"
        instance = form.save()

        assert instance.slug == f"title{index}-2"
        if form.cleaned_data["app_config"].use_placeholder:
            assert instance.content.get_plugins().filter(plugin_type="TextPlugin").count() == 0  # TextPlugin not created
        else:
            assert instance.post_text == ""  # post_text remains in model
