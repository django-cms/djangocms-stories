# flake8: noqa

from ..settings import *

UNINSTALL_APPS = ("djangocms_stories",)

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in UNINSTALL_APPS] + [
    "djangocms_blog",
    "djangocms_versioning",
]

ROOT_URLCONF = "tests.test_migrations.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_db.sqlite3",
    }
}
