from django import forms
from django.db.backends.utils import truncate_name
from django.utils.text import slugify as django_slugify
from parler.models import TranslatedFields as ParlerTranslatedFields, create_translations_model

from .settings import get_setting

__all__ = ["slugify", "LanguageSelector", "TranslatedFields"]


class TranslatedFields(ParlerTranslatedFields):
    """Keep generated translation constraint names within 30 characters."""

    def contribute_to_class(self, cls, name, **kwargs):
        self.name = name
        options = create_translations_model(cls, name, self.meta, **self.fields)._meta
        for constraint in options.constraints:
            constraint.name = truncate_name(constraint.name, 30)
        # Keep the migration state consistent with the constraints used by the model.
        options.original_attrs["constraints"] = options.constraints


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
