from cms.app_base import CMSAppConfig
from cms.models import Placeholder, PlaceholderRelationField
from django.apps import apps
from django.conf import settings

from .models import PostContent
from .views import ToolbarDetailView

djangocms_versioning_installed = apps.is_installed("djangocms_versioning")


class StoriesCMSConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(PostContent, ToolbarDetailView.as_view())]
    djangocms_versioning_enabled = (
        getattr(settings, "VERSIONING_BLOG_MODELS_ENABLED", True) and djangocms_versioning_installed
    )

    if djangocms_versioning_enabled:
        from packaging.version import Version as PackageVersion
        from cms.utils.i18n import get_language_tuple
        from djangocms_versioning import __version__ as djangocms_versioning_version
        from djangocms_versioning.datastructures import default_copy, VersionableItem

        if PackageVersion(djangocms_versioning_version) < PackageVersion("2.3"):  # pragma: no cover
            raise ImportError(
                "djangocms_versioning >= 2.3.0 is required for djangocms_stories to work properly."
                " Please upgrade djangocms_versioning."
            )

        versioning = [
            VersionableItem(
                content_model=PostContent,
                grouper_field_name="post",
                extra_grouping_fields=["language"],
                version_list_filter_lookups={"language": get_language_tuple},
                grouper_selector_option_label=lambda obj, lang: obj.get_title(lang),
                copy_function=default_copy,
            ),
        ]
