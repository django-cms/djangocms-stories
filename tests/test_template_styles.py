import pytest
from unittest.mock import patch
from django.test import TestCase
from djangocms_stories.cms_appconfig import StoriesConfig



class TestGetTemplateStyleChoices(TestCase):
    def test_returns_default_when_setting_not_defined(self):
        from djangocms_stories.cms_appconfig import get_template_style_choices

        with patch("djangocms_stories.cms_appconfig.settings") as mock_settings:
            del mock_settings.STORIES_TEMPLATE_STYLES  
            mock_settings.configure_mock(spec=[])
            choices = get_template_style_choices()
            self.assertEqual(choices, (("Default", "djangocms_stories"),))

    def test_returns_custom_styles_from_settings(self):
        from djangocms_stories.cms_appconfig import get_template_style_choices

        custom_styles = (
            ("Bootstrap 5", "bootstrap_5"),
            ("Default", "djangocms_stories"),
        )
        with patch("djangocms_stories.cms_appconfig.settings") as mock_settings:
            mock_settings.STORIES_TEMPLATE_STYLES = custom_styles
            choices = get_template_style_choices()
            self.assertEqual(choices, custom_styles)


class TestStoriesConfigTemplateStyle(TestCase):
    def _make_config(self, template_style=""):
        from djangocms_stories.cms_appconfig import StoriesConfig
        config = StoriesConfig.__new__(StoriesConfig)
        config.template_style = template_style
        return config

    def test_get_template_style_returns_set_value(self):
        config = self._make_config(template_style="bootstrap_5")
        self.assertEqual(config.get_template_style(), "bootstrap_5")

    def test_get_template_style_falls_back_when_empty(self):
        config = self._make_config(template_style="")
        style = config.get_template_style()
        self.assertIsInstance(style, str)
        self.assertTrue(len(style) > 0)

    def test_get_template_style_falls_back_to_last_in_list(self):

        config = self._make_config(template_style="")
        custom_styles = (
            ("Bootstrap 5", "bootstrap_5"),
            ("Default", "djangocms_stories"),
        )
        with patch("djangocms_stories.cms_appconfig.get_template_style_choices", return_value=custom_styles):
            style = config.get_template_style()
            self.assertEqual(style, "djangocms_stories")  

    def test_template_style_field_exists_on_model(self):
        field_names = [f.name for f in StoriesConfig._meta.get_fields()]
        self.assertIn("template_style", field_names)

    def test_template_style_field_defaults_to_empty_string(self):
        field = StoriesConfig._meta.get_field("template_style")
        self.assertEqual(field.default, "")
        self.assertTrue(field.blank)