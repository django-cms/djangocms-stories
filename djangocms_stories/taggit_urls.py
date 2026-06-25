# This file is used on divio cloud only during automatic setup
from django.urls import include, path  # pragma: no cover

urlpatterns = [  # pragma: no cover
    path("", include("djangocms_stories.tag_autosuggest")),
]
