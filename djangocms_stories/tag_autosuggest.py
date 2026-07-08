"""Native tag autocomplete, replacing the ``django-taggit-autosuggest`` dependency.

This module provides a small, self-contained drop-in for the tag suggestion
feature that ``taggit-autosuggest`` used to give us:

* :class:`TaggableManager` -- a thin subclass of taggit's manager whose form
  field defaults to the :class:`TagAutoSuggest` widget (mirroring the old
  ``taggit_autosuggest.managers.TaggableManager``).
* :class:`TagAutoSuggest` -- a widget that enhances taggit's comma-separated
  tag field with the Select2 library that already ships with Django's admin,
  fed by a tiny JSON endpoint. It degrades to a plain multi-select when
  JavaScript is unavailable.
* :func:`tag_suggestions` -- the JSON endpoint returning matching tag names,
  wired up in ``urlpatterns`` under the name ``djangocms_stories_tag_autosuggest``.

No third-party package is required beyond ``django-taggit`` itself.
"""

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import NoReverseMatch, path, reverse
from django.utils.translation import gettext_lazy as _
from taggit.forms import TagField
from taggit.managers import TaggableManager as BaseTaggableManager
from taggit.models import Tag
from taggit.utils import parse_tags

#: How many suggestions the endpoint returns at most.
MAX_SUGGESTIONS = 20


class TagAutoSuggest(forms.SelectMultiple):
    """Comma-separated tag widget enhanced with the admin's bundled Select2.

    The widget renders as a ``<select multiple>`` so it works without any
    JavaScript, while the accompanying script turns it into a Select2 field
    with free tagging and AJAX-backed suggestions. The submitted value is
    normalised back into the comma-separated string that
    :class:`taggit.forms.TagField` expects.
    """

    allow_multiple_selected = True

    class Media:
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.min.css",
                "admin/css/autocomplete.css",
            )
        }
        js = (
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/vendor/select2/select2.full.min.js",
            "admin/js/jquery.init.js",
            "djangocms_stories/js/tag_autosuggest.js",
        )

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "djangocms-stories-tag-autosuggest",
            "data-placeholder": _("Type a tag and hit enter"),
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        """Return the value as a flat list of tag-name strings."""
        if value is None:
            return []
        if isinstance(value, str):
            return list(parse_tags(value))
        return [getattr(tag, "name", tag) for tag in value]

    def optgroups(self, name, value, attrs=None):
        # ``value`` arrives already formatted as a list of tag names. Expose
        # each selected tag as an <option> so Select2 renders it on load.
        self.choices = [(tag, tag) for tag in value]
        return super().optgroups(name, value, attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        try:
            context["widget"]["attrs"]["data-ajax-url"] = reverse("djangocms_stories_tag_autosuggest")
        except NoReverseMatch:
            # The suggestion endpoint isn't routed; Select2 still works as a
            # free-tagging field, just without server-side suggestions.
            pass
        return context

    def value_from_datadict(self, data, files, name):
        if hasattr(data, "getlist"):
            values = data.getlist(name)
        else:
            values = data.get(name, [])
        if isinstance(values, str):
            return values
        return ",".join(str(value) for value in values)


class TaggableManager(BaseTaggableManager):
    """Taggit manager whose form field uses :class:`TagAutoSuggest` by default."""

    def formfield(self, form_class=TagField, **kwargs):
        kwargs.setdefault("widget", TagAutoSuggest())
        return super().formfield(form_class=form_class, **kwargs)


@staff_member_required
def tag_suggestions(request):
    """Return tag names matching the ``q`` query parameter as JSON.

    Restricted to staff users since it is only used from admin/plugin forms
    and exposes the full tag vocabulary.
    """
    query = request.GET.get("q", "").strip()
    tags = Tag.objects.all()
    if query:
        tags = tags.filter(name__icontains=query)
    names = list(tags.order_by("name").values_list("name", flat=True)[:MAX_SUGGESTIONS])
    return JsonResponse({"results": names})


urlpatterns = [
    path("tag-autosuggest/", tag_suggestions, name="djangocms_stories_tag_autosuggest"),
]
