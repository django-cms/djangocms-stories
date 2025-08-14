from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, override
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import PostCategory, StoriesConfig
from .settings import get_setting

User = get_user_model()


class ConfigFormBase:
    """Base form class for all models depends on app_config."""

    @cached_property
    def app_config(self):
        """
        Return the currently selected app_config, whether it's an instance attribute or passed in the request
        """
        if getattr(self.instance, "app_config_id", None):
            return self.instance.app_config
        elif "app_config" in self.initial:
            return StoriesConfig.objects.get(pk=self.initial["app_config"])
        elif self.data.get("app_config", None):
            return StoriesConfig.objects.get(pk=self.data["app_config"])
        return None


class CategoryAdminForm(ConfigFormBase, TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields["meta_description"].validators = [MaxLengthValidator(get_setting("META_DESCRIPTION_LENGTH"))]
        original_attrs = self.base_fields["meta_description"].widget.attrs
        if "cols" in original_attrs:
            del original_attrs["cols"]
        if "rows" in original_attrs:
            del original_attrs["rows"]
        original_attrs["maxlength"] = get_setting("META_DESCRIPTION_LENGTH")
        self.base_fields["meta_description"].widget = forms.TextInput(original_attrs)
        super().__init__(*args, **kwargs)

        if "parent" in self.fields:
            qs = self.fields["parent"].queryset
            if self.instance.pk:
                qs = qs.exclude(pk__in=[self.instance.pk] + [child.pk for child in self.instance.descendants()])
            config = None
            if getattr(self.instance, "app_config_id", None):
                qs = qs.filter(app_config__namespace=self.instance.app_config.namespace)
            elif "app_config" in self.initial:
                config = StoriesConfig.objects.get(pk=self.initial["app_config"])
            elif self.data.get("app_config", None):
                config = StoriesConfig.objects.get(pk=self.data["app_config"])
            if config:
                qs = qs.filter(app_config__namespace=config.namespace)
            self.fields["parent"].queryset = qs

    class Meta:
        model = PostCategory
        fields = "__all__"


class BlogPluginForm(forms.ModelForm):
    """Base plugin form to inject the list of configured template folders from STORIES_PLUGIN_TEMPLATE_FOLDERS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "template_folder" in self.fields:
            self.fields["template_folder"].choices = get_setting("PLUGIN_TEMPLATE_FOLDERS")


class LatestEntriesForm(BlogPluginForm):
    """Custom forms for BlogLatestEntriesPlugin to properly load taggit-autosuggest."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].widget = TagAutoSuggest("taggit.Tag")

    class Media:
        css = {"all": ("djangocms_stories/css/djangocms_stories_admin.css",)}


class AuthorPostsForm(BlogPluginForm):
    """Custom form for BlogAuthorPostsPlugin to apply distinct to the list of authors in plugin changeform."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # apply distinct due to django issue #11707
        self.fields["authors"].queryset = User.objects.filter(djangocms_stories_post_author__publish=True).distinct()


class AppConfigForm(forms.Form):
    app_config = forms.ModelChoiceField(
        queryset=StoriesConfig.objects.all(),
        label=_("App Config"),
        required=True,
        help_text=_("Select the app config to apply to the new post."),
    )
    language = forms.CharField(widget=forms.HiddenInput(), required=False)

    fieldsets = [(None, {"fields": ("app_config", "language")})]


class StoriesConfigForm(TranslatableModelForm):
    """Form for StoriesConfig model."""

    class Meta:
        model = StoriesConfig
        fields = "__all__"
        widgets = {
            field: forms.Select(choices=get_setting(setting_name))
            for field, setting_name in [
                ("url_patterns", "AVAILABLE_PERMALINK_STYLES"),
                ("menu_structure", "MENU_TYPES"),
                ("sitemap_changefreq", "SITEMAP_CHANGEFREQ"),
                ("object_type", "TYPES"),
                ("og_type", "FB_TYPES"),
                ("twitter_type", "TWITTER_TYPES"),
                ("gplus_type", "SCHEMAORG_TYPES"),
            ]
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the StoriesConfigForm instance with defaults and choices.
        """
        from .cms_appconfig import config_defaults

        kwargs.setdefault("initial", {})

        # Set defaults
        for name, default in config_defaults.items():
            kwargs["initial"].setdefault(name, default)
        with override(self.language_code):
            kwargs["initial"].setdefault("app_title", force_str(get_setting("AUTO_APP_TITLE")))
            kwargs["initial"].setdefault("object_name", force_str(get_setting("DEFAULT_OBJECT_NAME")))

        # Set current saved value:
        for field in self._meta.widgets.keys():
            kwargs["initial"][field] = getattr(kwargs["instance"], field)

        super().__init__(*args, **kwargs)
