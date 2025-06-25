from django.apps import apps
from django.contrib import admin


if apps.is_installed("djangocms_stories"):
    # Do not declare models if the migration test is running
    # This is to avoid circular imports during migrations
    from tests.test_utils.models import MyPostExtension

    class PostExtensionInline(admin.TabularInline):
        model = MyPostExtension
        fields = ["custom_field"]
        classes = ["collapse"]
        extra = 1
        can_delete = False
        verbose_name = "My Post Extention"
        verbose_name_plural = "My Post Extensions"
