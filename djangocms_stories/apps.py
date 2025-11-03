from django.apps import AppConfig
from django.core.checks import Warning, register
from django.utils.translation import gettext_lazy as _


class BlogAppConfig(AppConfig):
    name = "djangocms_stories"
    verbose_name = _("Stories")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        register(check_settings)
        return super().ready()


def check_settings(*args, **kwargs):  # pragma: no cover
    from django.conf import settings
    from .settings import params

    warnings = []
    blog_settings = {setting: f"STORIES_{setting[5:]}" for setting in dir(settings) if setting.startswith("BLOG_")}
    if "BLOG_ABSTRACT_CKEDITOR" in blog_settings:
        blog_settings["BLOG_ABSTRACT_CKEDITOR"] = "STORIES_ABSTRACT_EDITOR_CONFIG"
    if "BLOG_POST_TEXT_CKEDITOR" in blog_settings:
        blog_settings["BLOG_POST_TEXT_CKEDITOR"] = "STORIES_POST_TEXT_EDITOR_CONFIG"
    if "VERSIONING_BLOG_MODELS_ENABLED" in blog_settings:
        blog_settings["VERSIONING_BLOG_MODELS_ENABLED"] = "STORIES_VERSIONING_ENABLED"

    for setting, stories_setting in blog_settings.items():
        if stories_setting in params:
            warnings.append(
                Warning(
                    f"{setting} has been renamed and is now deprecated for djangocms-stories",
                    hint=f"Use {stories_setting} instead.",
                    obj=f"settings.{setting}",
                    id="djangocms_stories.W001",
                )
            )
    return warnings
