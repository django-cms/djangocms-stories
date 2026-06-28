"""Tests for the native tag autocomplete that replaces django-taggit-autosuggest."""

import json

import pytest
from django.urls import reverse
from taggit.models import Tag

from djangocms_stories.tag_autosuggest import TagAutoSuggest


@pytest.mark.django_db
def test_tag_suggestions_endpoint_filters_for_staff(admin_client):
    Tag.objects.create(name="django")
    Tag.objects.create(name="djangocms")
    Tag.objects.create(name="python")

    url = reverse("djangocms_stories_tag_autosuggest")
    response = admin_client.get(url, {"q": "django"})

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {"results": ["django", "djangocms"]}


@pytest.mark.django_db
def test_tag_suggestions_endpoint_returns_all_without_query(admin_client):
    Tag.objects.create(name="alpha")
    Tag.objects.create(name="beta")

    url = reverse("djangocms_stories_tag_autosuggest")
    response = admin_client.get(url)

    assert response.status_code == 200
    assert json.loads(response.content) == {"results": ["alpha", "beta"]}


@pytest.mark.django_db
def test_tag_suggestions_endpoint_requires_staff(client):
    url = reverse("djangocms_stories_tag_autosuggest")
    response = client.get(url)

    # staff_member_required redirects anonymous users to the admin login.
    assert response.status_code == 302
    assert "login" in response["Location"]


def test_widget_renders_select2_attributes():
    widget = TagAutoSuggest()
    html = widget.render("tags", ["alpha", "beta"])

    assert 'class="djangocms-stories-tag-autosuggest"' in html
    assert "data-ajax-url" in html
    assert reverse("djangocms_stories_tag_autosuggest") in html
    # Selected tags are rendered as options so Select2 shows them on load.
    assert html.count("selected") == 2


def test_widget_value_from_datadict_normalises_to_comma_string():
    from django.http import QueryDict

    widget = TagAutoSuggest()
    data = QueryDict(mutable=True)
    data.setlist("tags", ["one", "two", "three"])

    assert widget.value_from_datadict(data, {}, "tags") == "one,two,three"


def test_widget_value_from_datadict_passes_through_plain_string():
    widget = TagAutoSuggest()
    assert widget.value_from_datadict({"tags": "one,two"}, {}, "tags") == "one,two"
