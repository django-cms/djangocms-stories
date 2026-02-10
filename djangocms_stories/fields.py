from django import forms
from django.utils.text import slugify as django_slugify

from .settings import get_setting

__all__ = ["slugify", "LanguageSelector"]


def slugify(base):
    return django_slugify(base, allow_unicode=get_setting("ALLOW_UNICODE_SLUGS"))


class LanguageSelector(forms.Select):
    class Media:
        js = (
            "admin/js/jquery.init.js",
            "djangocms_stories/js/language-selector.js",
        )

    def __init__(self, *args, **kwargs):
        kwargs.update({"attrs": {**kwargs.get("attrs", {}), **{"class": "js-language-selector"}}})
        super().__init__(*args, **kwargs)
