from unittest.mock import patch

import pytest
from django import forms
from django.contrib.auth import get_user_model

from djangocms_stories.forms import (
    AppConfigForm,
    BlogPluginForm,
    CategoryAdminForm,
    StoriesConfigForm,
)
from djangocms_stories.models import StoriesConfig

User = get_user_model()


# Tests for BlogPluginForm


@pytest.mark.django_db
def test_blog_plugin_form_init_with_template_folder_field():
    """Test that BlogPluginForm initializes template_folder choices correctly"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = [
            ("default", "Default"),
            ("custom", "Custom"),
            ("special", "Special"),
        ]

        class TestPluginForm(BlogPluginForm):
            template_folder = forms.ChoiceField()

            class Meta:
                model = StoriesConfig
                fields = ["template_folder"]

        form = TestPluginForm()

        assert "template_folder" in form.fields
        assert form.fields["template_folder"].choices == [
            ("default", "Default"),
            ("custom", "Custom"),
            ("special", "Special"),
        ]
        mock_get_setting.assert_called_once_with("PLUGIN_TEMPLATE_FOLDERS")


@pytest.mark.django_db
def test_blog_plugin_form_init_without_template_folder_field():
    """Test that BlogPluginForm works when template_folder field is not present"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:

        class TestPluginFormNoTemplate(BlogPluginForm):
            class Meta:
                model = StoriesConfig
                fields = ["namespace"]

        form = TestPluginFormNoTemplate()

        assert "template_folder" not in form.fields
        # get_setting should not be called if field doesn't exist
        mock_get_setting.assert_not_called()


# Tests for LatestEntriesForm


@pytest.mark.django_db
def test_latest_entries_form_init_sets_tag_widget(simple_wo_placeholder):
    """Test that LatestEntriesForm sets TagAutoSuggest widget for tags field"""
    from djangocms_stories.models import LatestPostsPlugin
    from taggit_autosuggest.widgets import TagAutoSuggest

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = [("default", "Default")]

        # Dynamically add Meta class for testing
        # In production, this is added by Django CMS Plugin framework
        from djangocms_stories.forms import LatestEntriesForm

        if not hasattr(LatestEntriesForm, "_meta") or LatestEntriesForm._meta.model is None:

            class TestLatestEntriesForm(LatestEntriesForm):
                class Meta:
                    model = LatestPostsPlugin
                    fields = "__all__"

            form = TestLatestEntriesForm()
        else:
            form = LatestEntriesForm()

        assert "tags" in form.fields
        assert isinstance(form.fields["tags"].widget, TagAutoSuggest)


@pytest.mark.django_db
def test_latest_entries_form_has_custom_css(simple_wo_placeholder):
    """Test that LatestEntriesForm includes custom CSS in Media"""
    from djangocms_stories.models import LatestPostsPlugin

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = [("default", "Default")]

        # Dynamically add Meta class for testing
        from djangocms_stories.forms import LatestEntriesForm

        if not hasattr(LatestEntriesForm, "_meta") or LatestEntriesForm._meta.model is None:

            class TestLatestEntriesForm(LatestEntriesForm):
                class Meta:
                    model = LatestPostsPlugin
                    fields = "__all__"

            form = TestLatestEntriesForm()
        else:
            form = LatestEntriesForm()

        assert hasattr(form, "media")
        assert "djangocms_stories/css/djangocms_stories_admin.css" in str(form.media)


# Tests for AuthorPostsForm


@pytest.mark.django_db
def test_author_posts_form_filters_to_actual_authors(simple_wo_placeholder):
    """Test that AuthorPostsForm only includes users who are authors"""
    from djangocms_stories.models import AuthorEntriesPlugin

    from .factories import PostContentFactory, UserFactory

    # Create users - some are authors, some are not
    author1 = UserFactory(username="author1")
    author2 = UserFactory(username="author2")
    non_author = UserFactory(username="not_an_author")

    # Create posts with authors to make them actual authors
    PostContentFactory(post__author=author1, post__app_config=simple_wo_placeholder)
    PostContentFactory(post__author=author2, post__app_config=simple_wo_placeholder)
    # non_author has no posts

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = [("default", "Default")]

        # Dynamically add Meta class for testing
        from djangocms_stories.forms import AuthorPostsForm

        if not hasattr(AuthorPostsForm, "_meta") or AuthorPostsForm._meta.model is None:

            class TestAuthorPostsForm(AuthorPostsForm):
                class Meta:
                    model = AuthorEntriesPlugin
                    fields = "__all__"

            form = TestAuthorPostsForm()
        else:
            form = AuthorPostsForm()

        assert "authors" in form.fields
        author_ids = list(form.fields["authors"].queryset.values_list("id", flat=True))

        # Should include authors with posts
        assert author1.id in author_ids
        assert author2.id in author_ids

        # Should not include users without posts
        assert non_author.id not in author_ids


@pytest.mark.django_db
def test_author_posts_form_empty_queryset_when_no_authors(simple_wo_placeholder):
    """Test that AuthorPostsForm handles case with no authors gracefully"""
    from djangocms_stories.models import AuthorEntriesPlugin

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = [("default", "Default")]

        # Dynamically add Meta class for testing
        from djangocms_stories.forms import AuthorPostsForm

        if not hasattr(AuthorPostsForm, "_meta") or AuthorPostsForm._meta.model is None:

            class TestAuthorPostsForm(AuthorPostsForm):
                class Meta:
                    model = AuthorEntriesPlugin
                    fields = "__all__"

            form = TestAuthorPostsForm()
        else:
            form = AuthorPostsForm()

        assert "authors" in form.fields
        assert form.fields["authors"].queryset.count() == 0


# Tests for CategoryAdminForm


@pytest.mark.django_db
def test_category_admin_form_init_sets_meta_description_validators(simple_wo_placeholder):
    """Test that CategoryAdminForm sets correct validators for meta_description"""
    from django.core.validators import MaxLengthValidator

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm()

        assert "meta_description" in form.base_fields
        validators = form.base_fields["meta_description"].validators
        max_length_validators = [v for v in validators if isinstance(v, MaxLengthValidator)]
        assert len(max_length_validators) > 0
        assert max_length_validators[0].limit_value == 160


@pytest.mark.django_db
def test_category_admin_form_meta_description_widget_is_text_input(simple_wo_placeholder):
    """Test that CategoryAdminForm uses TextInput widget for meta_description"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm()

        assert isinstance(form.base_fields["meta_description"].widget, forms.TextInput)
        assert "maxlength" in form.base_fields["meta_description"].widget.attrs
        assert form.base_fields["meta_description"].widget.attrs["maxlength"] == 160


@pytest.mark.django_db
def test_category_admin_form_removes_cols_and_rows_attrs():
    """Test that CategoryAdminForm removes cols and rows from widget attrs"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        # Manually set cols and rows in base_fields before form creation
        CategoryAdminForm.base_fields["meta_description"].widget.attrs = {"cols": 40, "rows": 10}

        form = CategoryAdminForm()

        assert "cols" not in form.base_fields["meta_description"].widget.attrs
        assert "rows" not in form.base_fields["meta_description"].widget.attrs


@pytest.mark.django_db
def test_category_admin_form_parent_queryset_filters_by_app_config(simple_wo_placeholder):
    """Test that CategoryAdminForm filters parent field by app_config"""
    from .factories import PostCategoryFactory, StoriesConfigFactory

    # Create categories in different configs
    cat1 = PostCategoryFactory(app_config=simple_wo_placeholder)
    cat2 = PostCategoryFactory(app_config=simple_wo_placeholder)

    other_config = StoriesConfigFactory(namespace="other-config", type="Article")
    cat_other = PostCategoryFactory(app_config=other_config)

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        # Test with instance that has app_config
        form = CategoryAdminForm(instance=cat1)

        if "parent" in form.fields:
            parent_ids = list(form.fields["parent"].queryset.values_list("id", flat=True))
            assert cat2.id in parent_ids
            assert cat_other.id not in parent_ids
            assert cat1.id not in parent_ids  # Should exclude self


@pytest.mark.django_db
def test_category_admin_form_parent_excludes_descendants(simple_wo_placeholder):
    """Test that CategoryAdminForm excludes instance and its descendants from parent choices"""
    from .factories import PostCategoryFactory

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        # Create hierarchy: parent -> child -> grandchild
        parent = PostCategoryFactory(app_config=simple_wo_placeholder)
        child = PostCategoryFactory(app_config=simple_wo_placeholder, parent=parent)
        grandchild = PostCategoryFactory(app_config=simple_wo_placeholder, parent=child)
        other = PostCategoryFactory(app_config=simple_wo_placeholder)

        # Edit the child - should exclude self and descendants
        form = CategoryAdminForm(instance=child)

        if "parent" in form.fields:
            parent_ids = list(form.fields["parent"].queryset.values_list("id", flat=True))
            assert parent.id in parent_ids  # Parent is valid
            assert other.id in parent_ids  # Sibling is valid
            assert child.id not in parent_ids  # Self excluded
            assert grandchild.id not in parent_ids  # Descendant excluded


@pytest.mark.django_db
def test_category_admin_form_parent_with_initial_app_config(simple_wo_placeholder):
    """Test that CategoryAdminForm filters parent by app_config from initial data"""
    from .factories import PostCategoryFactory

    cat1 = PostCategoryFactory(app_config=simple_wo_placeholder)
    cat2 = PostCategoryFactory(app_config=simple_wo_placeholder)

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm(initial={"app_config": simple_wo_placeholder.pk})

        if "parent" in form.fields:
            parent_ids = list(form.fields["parent"].queryset.values_list("id", flat=True))
            assert cat1.id in parent_ids
            assert cat2.id in parent_ids


@pytest.mark.django_db
def test_category_admin_form_parent_with_data_app_config(simple_wo_placeholder):
    """Test that CategoryAdminForm filters parent by app_config from POST data"""
    from .factories import PostCategoryFactory

    cat1 = PostCategoryFactory(app_config=simple_wo_placeholder)

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm(data={"app_config": simple_wo_placeholder.pk})

        if "parent" in form.fields:
            parent_ids = list(form.fields["parent"].queryset.values_list("id", flat=True))
            assert cat1.id in parent_ids


# Tests for AppConfigForm


@pytest.mark.django_db
def test_app_config_form_has_required_fields(simple_wo_placeholder):
    """Test that AppConfigForm has all required fields"""
    form = AppConfigForm()

    assert "app_config" in form.fields
    assert "language" in form.fields
    assert form.fields["app_config"].required is True
    assert form.fields["language"].required is False


@pytest.mark.django_db
def test_app_config_form_language_is_hidden(simple_wo_placeholder):
    """Test that language field uses HiddenInput widget"""
    form = AppConfigForm()

    assert isinstance(form.fields["language"].widget, forms.HiddenInput)


@pytest.mark.django_db
def test_app_config_form_queryset_includes_all_configs(simple_wo_placeholder):
    """Test that app_config field includes all StoriesConfig instances"""
    from .factories import StoriesConfigFactory

    other_config = StoriesConfigFactory(namespace="another-config", type="Article")

    form = AppConfigForm()

    config_ids = list(form.fields["app_config"].queryset.values_list("id", flat=True))
    assert simple_wo_placeholder.id in config_ids
    assert other_config.id in config_ids


# Tests for StoriesConfigForm


@pytest.mark.django_db
def test_stories_config_form_init_sets_defaults():
    """Test that StoriesConfigForm sets default values from config_defaults"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        # Mock all the get_setting calls
        def get_setting_side_effect(key):
            settings_map = {
                "AVAILABLE_PERMALINK_STYLES": [("full", "Full"), ("short", "Short")],
                "MENU_TYPES": [("complete", "Complete")],
                "SITEMAP_CHANGEFREQ": [("weekly", "Weekly")],
                "TYPES": [("Article", "Article")],
                "FB_TYPES": [("article", "Article")],
                "TWITTER_TYPES": [("summary", "Summary")],
                "SCHEMAORG_TYPES": [("Article", "Article")],
                "AUTO_APP_TITLE": "Blog",
                "DEFAULT_OBJECT_NAME": "Post",
                "USE_PLACEHOLDER": True,
                "USE_ABSTRACT": True,
                "USE_RELATED": 1,
                "AUTHOR_DEFAULT": True,
                "PAGINATION": 10,
                "MENU_EMPTY_CATEGORIES": False,
                "SITEMAP_CHANGEFREQ_DEFAULT": "weekly",
                "SITEMAP_PRIORITY_DEFAULT": "0.5",
                "TYPE": "Article",
                "FB_TYPE": "article",
                "FB_PROFILE_ID": "",
                "FB_PUBLISHER": "",
                "FB_AUTHOR_URL": "",
                "FB_AUTHOR": "",
                "TWITTER_TYPE": "summary",
                "TWITTER_SITE": "",
                "TWITTER_AUTHOR": "",
                "SCHEMAORG_TYPE": "Article",
                "SCHEMAORG_AUTHOR": "",
            }
            return settings_map.get(key, "")

        mock_get_setting.side_effect = get_setting_side_effect

        form = StoriesConfigForm()

        # Check that initial values are set
        assert form.initial.get("app_title") == "Blog"
        assert form.initial.get("object_name") == "Post"
        assert form.initial.get("use_placeholder") is True
        assert form.initial.get("use_abstract") is True


@pytest.mark.django_db
def test_stories_config_form_init_with_instance_overrides_defaults(simple_wo_placeholder):
    """Test that StoriesConfigForm uses instance values when provided"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:

        def get_setting_side_effect(key):
            settings_map = {
                "AVAILABLE_PERMALINK_STYLES": [("full", "Full")],
                "MENU_TYPES": [("complete", "Complete")],
                "SITEMAP_CHANGEFREQ": [("weekly", "Weekly"), ("monthly", "Monthly")],
                "TYPES": [("Article", "Article")],
                "FB_TYPES": [("article", "Article")],
                "TWITTER_TYPES": [("summary", "Summary")],
                "SCHEMAORG_TYPES": [("Article", "Article")],
                "AUTO_APP_TITLE": "Blog",
                "DEFAULT_OBJECT_NAME": "Post",
            }
            return settings_map.get(key, "")

        mock_get_setting.side_effect = get_setting_side_effect

        # Create form with instance
        form = StoriesConfigForm(instance=simple_wo_placeholder)

        # Should use instance's saved values
        assert form.initial.get("sitemap_changefreq") == simple_wo_placeholder.sitemap_changefreq


@pytest.mark.django_db
def test_stories_config_form_widgets_use_select():
    """Test that StoriesConfigForm uses Select widgets for choice fields"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:

        def get_setting_side_effect(key):
            settings_map = {
                "AVAILABLE_PERMALINK_STYLES": [("full", "Full"), ("short", "Short")],
                "MENU_TYPES": [("complete", "Complete"), ("categories", "Categories")],
                "SITEMAP_CHANGEFREQ": [("weekly", "Weekly"), ("daily", "Daily")],
                "TYPES": [("Article", "Article"), ("Post", "Post")],
                "FB_TYPES": [("article", "Article"), ("website", "Website")],
                "TWITTER_TYPES": [("summary", "Summary"), ("card", "Card")],
                "SCHEMAORG_TYPES": [("Article", "Article"), ("BlogPosting", "BlogPosting")],
                "AUTO_APP_TITLE": "Blog",
                "DEFAULT_OBJECT_NAME": "Post",
            }
            return settings_map.get(key, "")

        mock_get_setting.side_effect = get_setting_side_effect

        form = StoriesConfigForm()

        # Check that select widgets are used for choice fields
        choice_fields = [
            "url_patterns",
            "menu_structure",
            "sitemap_changefreq",
            "object_type",
            "og_type",
            "twitter_type",
            "gplus_type",
        ]
        for field_name in choice_fields:
            if field_name in form.fields:
                assert isinstance(form.fields[field_name].widget, forms.Select)


# Tests for ConfigFormBase (via CategoryAdminForm)


@pytest.mark.django_db
def test_config_form_base_app_config_from_instance(simple_wo_placeholder):
    """Test that app_config property returns value from instance"""
    from .factories import PostCategoryFactory

    category = PostCategoryFactory(app_config=simple_wo_placeholder)

    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm(instance=category)

        assert form.app_config == simple_wo_placeholder


@pytest.mark.django_db
def test_config_form_base_app_config_from_initial(simple_wo_placeholder):
    """Test that app_config property returns value from initial data"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm(initial={"app_config": simple_wo_placeholder.pk})

        assert form.app_config == simple_wo_placeholder


@pytest.mark.django_db
def test_config_form_base_app_config_from_data(simple_wo_placeholder):
    """Test that app_config property returns value from POST data"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm(data={"app_config": str(simple_wo_placeholder.pk)})

        assert form.app_config == simple_wo_placeholder


@pytest.mark.django_db
def test_config_form_base_app_config_returns_none_when_not_available():
    """Test that app_config property returns None when no config is available"""
    with patch("djangocms_stories.forms.get_setting") as mock_get_setting:
        mock_get_setting.return_value = 160

        form = CategoryAdminForm()

        assert form.app_config is None
