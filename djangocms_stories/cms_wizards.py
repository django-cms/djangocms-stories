from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from cms.api import add_plugin
from cms.utils.permissions import get_current_user
from cms.wizards.wizard_base import Wizard

from .cms_appconfig import StoriesConfig
from .fields import slugify
from .models import Post, PostContent
from .settings import get_setting


class PostWizardForm(forms.ModelForm):
    """
    Form for the post wizard.
    It is used to create a new post with the required fields.
    """

    default_appconfig = None

    app_config = forms.IntegerField(
        label=_("app. config"),
        required=True,
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        if "initial" not in kwargs or not kwargs.get("initial", False):
            kwargs["initial"] = {}
        if "data" in kwargs and kwargs["data"] is not None:
            data = kwargs["data"].copy()
            data["1-app_config"] = self.default_appconfig
            kwargs["data"] = data
        super().__init__(*args, **kwargs)

    class Meta:
        model = PostContent
        fields = [
            "title",
            "abstract",
            "post_text",
        ]

    def save(self, commit=True):
        if self.errors:
            return super().save(commit)

        post = Post(
            app_config=self.cleaned_data["app_config"],
        )
        user = get_current_user()
        post._set_default_author(user)
        post.save()

        autocreate_plugin = commit and self.cleaned_data["app_config"].use_placeholder
        post_text = self.instance.post_text

        instance_dict = forms.model_to_dict(self.instance)
        instance_dict["post"] = post
        instance_dict["language"] = self.language_code
        instance_dict["slug"] = self.create_slug()
        if autocreate_plugin:
            del instance_dict["post_text"]  # Create a plugin later
        self.instance = self.Meta.model.objects.with_user(user).create(**instance_dict)
        if autocreate_plugin:
            self.add_plugin(post_text)  # Create plugin now
        return self.instance

    def create_slug(self):
        """
        Generate a valid slug, in case the given one is taken
        """
        source = self.cleaned_data.get("slug", "")
        lang_choice = self.language_code
        if not source:
            source = slugify(self.cleaned_data.get("title", ""))
        qs = PostContent.admin_manager.latest_content(language=lang_choice)
        used = list(qs.values_list("slug", flat=True))
        slug = source
        i = 2
        while slug in used:
            slug = f"{source}-{i}"
            i += 1
        return slug

    def clean_app_config(self):
        try:
            pk = int(self.cleaned_data.get("app_config", self.default_appconfig))
            config = StoriesConfig.objects.get(pk=pk)
        except (ValueError, TypeError, ObjectDoesNotExist):
            self.add_error(None, _("Selected story not available any more. Close wizard."))
            return 0  # Invalid PK
        return config

    def add_plugin(self, text: str) -> None:
        """
        Add text field content as text plugin to the post.
        """
        if text:
            plugin_type = get_setting("WIZARD_CONTENT_PLUGIN")
            plugin_body = get_setting("WIZARD_CONTENT_PLUGIN_BODY")
            opts = {
                "placeholder": self.instance.content,
                "plugin_type": plugin_type,
                "language": self.language_code,
                plugin_body: text,
            }
            add_plugin(**opts)


class PostWizard(Wizard):
    pass
