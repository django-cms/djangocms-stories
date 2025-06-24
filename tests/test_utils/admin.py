from django.contrib import admin

from tests.test_utils.models import MyPostExtension


class PostExtensionInline(admin.TabularInline):
    model = MyPostExtension
    fields = ["custom_field"]
    classes = ["collapse"]
    extra = 1
    can_delete = False
    verbose_name = "My Post Extention"
    verbose_name_plural = "My Post Extensions"
