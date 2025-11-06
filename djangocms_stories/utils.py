from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_versioning_enabled = None if "djangocms_versioning" in settings.INSTALLED_APPS else False


def is_versioning_enabled():
    global _versioning_enabled

    if _versioning_enabled is None:
        from .models import PostContent

        try:
            app_config = apps.get_app_config("djangocms_versioning")
            _versioning_enabled = app_config.cms_extension.is_content_model_versioned(PostContent)
        except LookupError:
            _versioning_enabled = False
    return _versioning_enabled


def site_compatibility_decorator(func):
    """
    A decorator to provide compatibility for django CMS versions
    that do not support request-aware get_current_site calls.
    """

    try:
        func(None)
    except TypeError:
        return lambda request: func()
    except ImproperlyConfigured:
        return func
    return func
