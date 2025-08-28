from cms.app_base import CMSAppConfig
from django.apps import apps
from django.db import DatabaseError

from django.contrib.sites.shortcuts import get_current_site
from cms.utils.i18n import get_language_tuple

from .settings import get_setting
from .models import PostContent
from .views import ToolbarDetailView


djangocms_versioning_installed = apps.is_installed("djangocms_versioning")


class StoriesCMSConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(PostContent, ToolbarDetailView.as_view(), "post")]
    djangocms_versioning_enabled = get_setting("VERSIONING_ENABLED") and djangocms_versioning_installed
    if djangocms_versioning_enabled:
        from packaging.version import Version as PackageVersion
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
                version_list_filter_lookups={
                    "language": lambda *args: get_language_tuple(
                        site_id=get_current_site(args[0] if len(args) > 0 else None).pk
                    )
                },
                grouper_selector_option_label=lambda obj, lang: obj.get_title(lang),
                copy_function=default_copy,
            ),
        ]

    @property
    def cms_wizards(self):
        from django.utils.translation import gettext
        from django.utils.functional import lazy

        from .cms_appconfig import StoriesConfig
        from .cms_wizards import PostWizard, PostWizardForm

        def generator():
            try:
                for item, config in enumerate(StoriesConfig.objects.all().order_by("namespace"), start=1):
                    seed = f"Story{item}Wizard"
                    new_wizard = type(str(seed), (PostWizard,), {})
                    new_form = type(f"{seed}Form", (PostWizardForm,), {"default_appconfig": config.pk})
                    yield new_wizard(
                        title=lazy(lambda config=config: gettext("New {0}").format(config.object_name), str)(),
                        weight=200,
                        form=new_form,
                        model=PostContent,
                        description=lazy(
                            lambda config=config: gettext("Create a new {0} in {1}").format(
                                config.object_name, config.app_title
                            ),
                            str,
                        )(),
                    )
            except DatabaseError:  # pragma: no cover
                # This can happen if, e.g., migrations have not been executed yet.
                # In that case, we return an empty list.
                return []

        return lazy(generator, list)()
