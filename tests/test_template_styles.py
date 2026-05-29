from unittest.mock import patch
from django.test import TestCase
from djangocms_stories.cms_appconfig import StoriesConfig, DEFAULT_TEMPLATE_STYLE, DEFAULT_TEMPLATE_STYLES


class TestDefaultTemplateStyleConstants(TestCase):
    def test_default_template_style_is_string(self):
        self.assertIsInstance(DEFAULT_TEMPLATE_STYLE, str)
        self.assertTrue(len(DEFAULT_TEMPLATE_STYLE) > 0)

    def test_default_template_styles_is_not_empty(self):
        self.assertTrue(len(DEFAULT_TEMPLATE_STYLES) > 0)

    def test_default_template_style_matches_last_entry(self):
        expected = DEFAULT_TEMPLATE_STYLES[-1][1] if DEFAULT_TEMPLATE_STYLES else "djangocms_stories"
        self.assertEqual(DEFAULT_TEMPLATE_STYLE, expected)


class TestStoriesConfigTemplateStyle(TestCase):
    def _make_config(self, template_style=""):
        config = StoriesConfig.__new__(StoriesConfig)
        config.template_style = template_style
        return config

    def test_get_template_style_returns_set_value(self):
        config = self._make_config(template_style="djangocms_stories_bootstrap_5")
        self.assertEqual(config.get_template_style(), "djangocms_stories_bootstrap_5")

    def test_get_template_style_falls_back_when_empty(self):
        config = self._make_config(template_style="")
        style = config.get_template_style()
        self.assertEqual(style, DEFAULT_TEMPLATE_STYLE)

    def test_get_template_style_falls_back_to_default_constant(self):
        config = self._make_config(template_style="")
        with patch("djangocms_stories.cms_appconfig.DEFAULT_TEMPLATE_STYLE", "djangocms_stories"):
            style = config.get_template_style()
            self.assertEqual(style, "djangocms_stories")

    def test_template_style_field_exists_on_model(self):
        field_names = [f.name for f in StoriesConfig._meta.get_fields()]
        self.assertIn("template_style", field_names)

    def test_template_style_field_default_matches_constant(self):
        field = StoriesConfig._meta.get_field("template_style")
        self.assertEqual(field.default, DEFAULT_TEMPLATE_STYLE)
        self.assertTrue(field.blank)