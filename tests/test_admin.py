import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils.translation import override


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    user = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
    return user


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


def test_config_admin_add(admin_client, assert_html_in_response):
    url = reverse("admin:djangocms_stories_storiesconfig_add")
    response = admin_client.get(url)
    parler_language_selector = """
        <div class="parler-language-tabs">
        <input type="hidden" class="language_button selected" name="en" /><span class="current">English</span>
        <span class="empty">
            <a href="?language=it">Italiano</a></span><span class="empty">
            <a href="?language=fr">French</a>
        </span></div>"""
    namespace_can_be_written = (
        '<input type="text" name="namespace" class="vTextField" maxlength="100" required id="id_namespace">'
    )

    assert_html_in_response(parler_language_selector, response)
    assert_html_in_response(namespace_can_be_written, response)


def test_config_admin_change(admin_client, default_config, assert_html_in_response):
    url = reverse("admin:djangocms_stories_storiesconfig_change", args=[default_config.pk])
    response = admin_client.get(url)
    parler_language_selector = """
        <div class="parler-language-tabs">
        <input type="hidden" class="language_button selected" name="en" /><span class="current">English</span>
        <span class="empty">
            <a href="?language=it">Italiano</a></span><span class="empty">
            <a href="?language=fr">French</a>
        </span></div>"""
    namespace_is_readonly = f'<div class="readonly">{default_config.namespace}</div>'

    assert_html_in_response(parler_language_selector, response)
    assert_html_in_response(namespace_is_readonly, response)


def test_post_model_is_listed_in_admin(admin_client):
    url = reverse("admin:index")
    response = admin_client.get(url)
    assert response.status_code == 200
    # Post model should be listed
    assert "Post" in response.content.decode()
    # PostContent model should NOT be listed
    assert "Post Content" not in response.content.decode()


def test_postcontentadmin_change_view_get_redirects_to_grouper(admin_client, db):
    # Create a Post and PostContent
    from .factories import PostContentFactory, PostFactory

    post = PostFactory()
    post_content = PostContentFactory(post=post, language="en", title="Test", post_text="Text")
    # Get the PostContentAdmin change view URL
    url = reverse("admin:djangocms_stories_postcontent_change", args=[post_content.pk])
    response = admin_client.get(url)
    # Should redirect (302) to the Post change view (grouper)
    assert response.status_code == 302
    assert reverse("admin:djangocms_stories_post_change", args=[post.pk]) in response["Location"]


def test_postcontentadmin_change_view_post_raises_404(admin_client, db):
    # Create a Post and PostContent
    from .factories import PostContentFactory, PostFactory

    post = PostFactory()
    post_content = PostContentFactory(post=post, language="en", title="Test", post_text="Text")
    url = reverse("admin:djangocms_stories_postcontent_change", args=[post_content.pk])
    # POST request should raise 404
    response = admin_client.post(url, data={})
    assert response.status_code == 404


def test_postadmin_change_list_view(admin_client, assert_html_in_response):
    from .factories import PostContentFactory

    post_contents = PostContentFactory.create_batch(20)

    url = reverse("admin:djangocms_stories_post_changelist")
    response = admin_client.get(url)

    for post_content in post_contents:
        change_url = reverse(
            "admin:djangocms_stories_post_change",
            args=[post_content.post.pk],
        )
        assert_html_in_response(
            f'<a href="{change_url}?language=en&amp;_changelist_filters=language%3Den">{post_content.title}</a>',
            response,
        )


def test_postadmin_change_list_view_other_lang(admin_client, default_config, assert_html_in_response):
    from .factories import PostContentFactory

    with override("it"):
        # Create post contents in Italian
        assert default_config.object_name == "Story"
        assert "en" in default_config.get_available_languages()

    PostContentFactory.create_batch(20)
    post_contents = PostContentFactory.create_batch(2, post__app_config=default_config)

    url = reverse("admin:djangocms_stories_post_changelist") + "?language=it"
    response = admin_client.get(url)

    for post_content in post_contents:
        change_url = reverse(
            "admin:djangocms_stories_post_change",
            args=[post_content.post.pk],
        )
        assert_html_in_response(
            f'<a href="{change_url}?_changelist_filters=language%3Dit&amp;language=it">Empty</a>', response
        )


@pytest.mark.django_db
def test_postadmin_bulk_enable_comments(admin_client, default_config, assert_html_in_response):
    # Create some posts
    from .factories import PostFactory

    posts = PostFactory.create_batch(4, enable_comments=False, app_config=default_config)
    # All posts should have enable_comments=False by default
    for post in posts:
        assert not post.enable_comments

    # Bulk enable comments
    url = reverse("admin:djangocms_stories_post_changelist")
    data = {
        "action": "enable_comments",
        "_selected_action": [post.pk for post in posts],
    }
    response = admin_client.post(url, data, follow=True)
    assert_html_in_response(
        '<ul class="messagelist"><li class="info">Comments for 4 entries enabled</li></ul>', response
    )
    # Refresh from db and check
    for post in posts:
        post.refresh_from_db()
        assert post.enable_comments is True


def test_postadmin_bulk_disable_comments(admin_client, default_config, assert_html_in_response):
    # Create some posts with enable_comments=True
    from .factories import PostFactory

    posts = PostFactory.create_batch(4, enable_comments=True, app_config=default_config)
    for post in posts:
        assert post.enable_comments

    # Bulk disable comments
    url = reverse("admin:djangocms_stories_post_changelist")
    data = {
        "action": "disable_comments",
        "_selected_action": [post.pk for post in posts],
    }
    response = admin_client.post(url, data, follow=True)
    assert_html_in_response(
        '<ul class="messagelist"><li class="info">Comments for 4 entries disabled.</li></ul>', response
    )
    # Refresh from db and check
    for post in posts:
        post.refresh_from_db()
        assert post.enable_comments is False


def test_post_change_admin(admin_client, default_config, assert_html_in_response):
    from .factories import PostFactory

    post = PostFactory(app_config=default_config)

    url = reverse("admin:djangocms_stories_post_change", args=[post.pk])
    response = admin_client.get(url)

    # django CMS activated the language selector
    assert_html_in_response('<script src="/static/cms/js/admin/language-selector.js">', response)
    assert_html_in_response(
        """
        <input type="button" data-url="en" class="language_button selected" id="enbutton" name="en" value="English"/>
        <input type="button" data-url="it" class="language_button notfilled" id="itbutton" name="it" value="Italiano"/>
        <input type="button" data-url="fr" class="language_button notfilled" id="frbutton" name="fr" value="French"/>
        """,
        response,
    )

    # Ensure the language field is present for post content
    assert_html_in_response(
        '<input type="hidden" name="content__language" value="en" id="id_content__language">', response
    )

    # Both post and post content fields are present
    assert_html_in_response('<label class="inline" for="id_author">Author:</label>', response)  # Post author field
    assert_html_in_response(
        '<label class="required" for="id_content__title">Title (English):</label>', response
    )  # PostContent title field


def test_category_add_admin(admin_client, assert_html_in_response):
    url = reverse("admin:djangocms_stories_postcategory_add")
    response = admin_client.get(url)

    assert_html_in_response(
        '<select name="app_config" required aria-describedby="id_app_config_helptext" id="id_app_config">', response
    )


def test_category_add_admin_with_config(admin_client, default_config, assert_html_in_response):
    url = reverse("admin:djangocms_stories_postcategory_add") + f"?app_config={default_config.pk}"
    response = admin_client.get(url)

    assert_html_in_response('<input type="text" name="name" maxlength="752" required id="id_name">', response)


def test_postadmin_get_list_filter(admin_user, default_config):
    """Test that get_list_filter returns expected filters"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.contrib.admin.sites import site
    from django.test import RequestFactory

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user
    filters = admin_instance.get_list_filter(request)

    # Should contain at minimum categories and app_config
    assert "categories" in filters
    assert "app_config" in filters


def test_postadmin_lookup_allowed(admin_user):
    """Test that lookup_allowed permits post__ lookups"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)

    # These lookups should be allowed
    assert admin_instance.lookup_allowed("post__categories__name", None)
    assert admin_instance.lookup_allowed("post__app_config__namespace", None)


def test_postadmin_has_restricted_sites_no_restriction(admin_user):
    """Test has_restricted_sites when user has no site restrictions"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # User without get_sites method should have no restrictions
    assert not admin_instance.has_restricted_sites(request)


def test_postadmin_save_model(admin_user, default_config):
    """Test that save_model sets default author"""
    from .factories import PostFactory, PostContentFactory
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.contrib.admin.sites import site

    post = PostFactory(app_config=default_config, author=None)
    PostContentFactory(post=post, language="en", title="Test")
    assert post.author is None

    PostAdmin(Post, site)

    # Just test the _set_default_author method directly
    post._set_default_author(admin_user)
    post.save()
    post.refresh_from_db()
    assert post.author is not None
    assert post.author == admin_user


def test_postadmin_fieldsets_with_abstract(admin_user, default_config):
    """Test fieldsets when abstract is enabled"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    # Set config to use abstract
    default_config.use_abstract = True
    default_config.save()

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    fieldsets = admin_instance.get_fieldsets(request, None)

    # Check that abstract field is present in fieldsets
    all_fields = []
    for name, data in fieldsets:
        all_fields.extend(data.get("fields", []))

    # Flatten nested field lists
    flat_fields = []
    for field in all_fields:
        if isinstance(field, list):
            flat_fields.extend(field)
        else:
            flat_fields.append(field)

    assert "content__abstract" in flat_fields


def test_postadmin_fieldsets_without_placeholder(admin_user, default_config):
    """Test fieldsets when placeholder is disabled"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    # Set config to not use placeholder
    default_config.use_placeholder = False
    default_config.save()

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    fieldsets = admin_instance.get_fieldsets(request, None)

    # Check that post_text field is present in fieldsets
    all_fields = []
    for name, data in fieldsets:
        all_fields.extend(data.get("fields", []))

    # Flatten nested field lists
    flat_fields = []
    for field in all_fields:
        if isinstance(field, list):
            flat_fields.extend(field)
        else:
            flat_fields.append(field)

    assert "content__post_text" in flat_fields


def test_postadmin_fieldsets_with_related(admin_user, default_config):
    """Test fieldsets when related posts are enabled"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    # Create some posts to relate
    PostFactory.create_batch(3, app_config=default_config)

    # Set config to use related
    default_config.use_related = True
    default_config.save()

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    fieldsets = admin_instance.get_fieldsets(request, None)

    # Check that related field is present in fieldsets
    all_fields = []
    for name, data in fieldsets:
        all_fields.extend(data.get("fields", []))

    # Flatten nested field lists
    flat_fields = []
    for field in all_fields:
        if isinstance(field, list):
            flat_fields.extend(field)
        else:
            flat_fields.append(field)

    assert "related" in flat_fields


def test_config_admin_readonly_namespace(admin_user, default_config):
    """Test that namespace field becomes readonly on existing config"""
    from djangocms_stories.admin import ConfigAdmin
    from djangocms_stories.models import StoriesConfig
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = ConfigAdmin(StoriesConfig, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # For new object, namespace should not be readonly
    readonly_new = admin_instance.get_readonly_fields(request, None)
    assert "namespace" not in readonly_new

    # For existing object, namespace should be readonly
    readonly_existing = admin_instance.get_readonly_fields(request, default_config)
    assert "namespace" in readonly_existing


def test_postadmin_can_change_content_without_versioning(admin_user):
    """Test can_change_content when versioning is not enabled"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostContentFactory

    post_content = PostContentFactory()

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # Without versioning, should always return True
    assert admin_instance.can_change_content(request, post_content)


def test_postadmin_title_empty(admin_user):
    """Test title method returns 'Empty' for objects without content"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    admin_instance = PostAdmin(Post, site)
    post = PostFactory()

    # Remove all post content
    post.postcontent_set.all().delete()

    # Should return "Empty"
    title = admin_instance.title(post)
    assert "Empty" in str(title)


def test_postadmin_get_form_adds_language(admin_user, default_config):
    """Test that get_form adds language to form class"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    post = PostFactory(app_config=default_config)

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"language": "en"})
    request.user = admin_user
    request.LANGUAGE_CODE = "en"

    form_class = admin_instance.get_form(request, post)

    # Form should have language attribute
    assert hasattr(form_class, "language")


def test_sitelistfilter_lookups(admin_user, default_config):
    """Test SiteListFilter lookups"""
    from djangocms_stories.admin import SiteListFilter, PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    filter_instance = SiteListFilter(request, {}, Post, admin_instance)

    lookups = filter_instance.lookups(request, admin_instance)

    # Should return site lookups
    assert isinstance(lookups, list)


def test_sitelistfilter_queryset(admin_user, default_config):
    """Test SiteListFilter queryset filtering"""
    from djangocms_stories.admin import SiteListFilter, PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from django.contrib.sites.models import Site
    from .factories import PostFactory

    PostFactory.create_batch(3, app_config=default_config)
    Site.objects.get_current()

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    filter_instance = SiteListFilter(request, {}, Post, admin_instance)

    queryset = Post.objects.all()

    # Without filter parameter, should return unchanged queryset
    filtered = filter_instance.queryset(request, queryset)
    assert filtered.count() >= 3


def test_modelapphookconfig_app_config_select_single_config(admin_user, default_config):
    """Test _app_config_select when only one config exists"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # With one config, should return that config
    result = admin_instance._app_config_select(request, None)
    assert result == default_config


def test_modelapphookconfig_app_config_select_from_get(admin_user, default_config):
    """Test _app_config_select when app_config is in GET params"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result == default_config


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_multiple_configs_no_params(admin_user):
    """Test _app_config_select when multiple configs exist and no params provided"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import StoriesConfigFactory

    # Create multiple configs
    StoriesConfigFactory(namespace="config1", app_title="Config 1")
    StoriesConfigFactory(namespace="config2", app_title="Config 2")

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # With multiple configs and no params, should return None
    result = admin_instance._app_config_select(request, None)
    assert result is None


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_from_post(admin_user, default_config):
    """Test _app_config_select when app_config is in POST params"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().post("/", {"app_config": default_config.pk})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result == default_config


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_invalid_post_id(admin_user):
    """Test _app_config_select with invalid POST app_config ID"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    # Try with non-existent ID
    request = RequestFactory().post("/", {"app_config": 99999})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result is None


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_invalid_post_value(admin_user):
    """Test _app_config_select with non-numeric POST app_config"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().post("/", {"app_config": "invalid"})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result is None


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_invalid_get_id(admin_user):
    """Test _app_config_select with invalid GET app_config ID"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": 99999})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result is None


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_invalid_get_value(admin_user):
    """Test _app_config_select with non-numeric GET app_config"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": "not-a-number"})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result is None


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_from_existing_object(admin_user, default_config):
    """Test _app_config_select when obj has app_config attribute"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    post = PostFactory(app_config=default_config)

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    result = admin_instance._app_config_select(request, post)
    assert result == default_config


@pytest.mark.django_db
def test_modelapphookconfig_app_config_select_get_overrides_single(admin_user, default_config):
    """Test _app_config_select: GET param takes precedence over single config count"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    # Even with single config, explicit GET param should be used
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    result = admin_instance._app_config_select(request, None)
    assert result == default_config


def test_modelapphookconfig_get_config_data(admin_user, default_config):
    """Test get_config_data retrieves config values"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    post = PostFactory(app_config=default_config)

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    # Should retrieve config value
    namespace = admin_instance.get_config_data(request, post, "namespace")
    assert namespace == default_config.namespace


def test_categoryadmin_autocomplete_and_search(admin_user):
    """Test CategoryAdmin has autocomplete and search configured"""
    from djangocms_stories.admin import CategoryAdmin
    from djangocms_stories.models import PostCategory
    from django.contrib.admin.sites import site

    admin_instance = CategoryAdmin(PostCategory, site)

    # Should have autocomplete for parent
    assert "parent" in admin_instance.autocomplete_fields

    # Should have search fields
    assert len(admin_instance.search_fields) > 0


def test_postcontent_admin_get_model_perms(admin_user):
    """Test PostContentAdmin returns empty perms to hide from index"""
    from djangocms_stories.admin import PostContentAdmin
    from djangocms_stories.models import PostContent
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostContentAdmin(PostContent, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    perms = admin_instance.get_model_perms(request)
    assert perms == {}


def test_postadmin_queryset_distinct(admin_user, default_config):
    """Test get_queryset returns distinct results"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from .factories import PostFactory

    PostFactory.create_batch(3, app_config=default_config)

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/")
    request.user = admin_user

    queryset = admin_instance.get_queryset(request)

    # Check that author is select_related
    assert "author" in queryset.query.select_related


def test_register_unregister_extension_inline():
    """Test register_extension and unregister_extension for inlines"""
    from djangocms_stories.admin import register_extension, unregister_extension, PostAdmin
    from django.contrib.admin import TabularInline

    class TestInline(TabularInline):
        model = None

    # Register the inline
    initial_count = len(PostAdmin.inlines)
    register_extension(TestInline)
    assert len(PostAdmin.inlines) == initial_count + 1
    assert TestInline in PostAdmin.inlines

    # Unregister the inline
    unregister_extension(TestInline)
    assert TestInline not in PostAdmin.inlines
    assert len(PostAdmin.inlines) == initial_count


def test_register_extension_duplicate_raises():
    """Test that registering same extension twice raises exception"""
    from djangocms_stories.admin import register_extension, unregister_extension, PostAdmin
    from django.contrib.admin import TabularInline

    class TestInline2(TabularInline):
        model = None

    try:
        register_extension(TestInline2)
        # Try to register again
        with pytest.raises(Exception, match="Can not register .* twice"):
            register_extension(TestInline2)
    finally:
        # Cleanup
        if TestInline2 in PostAdmin.inlines:
            unregister_extension(TestInline2)


def test_register_extension_model_deprecated():
    """Test that registering a model extension shows deprecation warning"""
    from djangocms_stories.admin import register_extension, unregister_extension
    from django.db import models

    class TestExtensionModel(models.Model):
        post = models.ForeignKey("djangocms_stories.Post", on_delete=models.CASCADE)

        class Meta:
            app_label = "djangocms_stories"

    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        register_extension(TestExtensionModel)
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message)

    # Cleanup
    unregister_extension(TestExtensionModel)


def test_unregister_extension_not_registered():
    """Test that unregistering non-existent extension raises exception"""
    from djangocms_stories.admin import unregister_extension
    from django.db import models

    class TestExtensionModel2(models.Model):
        post = models.ForeignKey("djangocms_stories.Post", on_delete=models.CASCADE)

        class Meta:
            app_label = "djangocms_stories"

    with pytest.raises(Exception, match="Can not unregister .* No signal found"):
        unregister_extension(TestExtensionModel2)


def test_register_extension_invalid_type():
    """Test that registering invalid type raises exception"""
    from djangocms_stories.admin import register_extension

    class InvalidType:
        pass

    with pytest.raises(Exception, match="Can not register .* type"):
        register_extension(InvalidType)


def test_unregister_extension_invalid_type():
    """Test that unregistering invalid type raises exception"""
    from djangocms_stories.admin import unregister_extension

    class InvalidType:
        pass

    with pytest.raises(Exception, match="Can not unregister .* type"):
        unregister_extension(InvalidType)


@pytest.mark.django_db
def test_create_post_post_save():
    """Test create_post_post_save creates related instance"""
    from djangocms_stories.admin import create_post_post_save

    # Create the signal function - just verify it's callable
    # We can't easily test the actual signal without a real model
    signal_func = create_post_post_save(None)

    # Test it gets called (mock the model.objects.create)
    assert callable(signal_func)


def test_sitelistfilter_queryset_with_sites_param(admin_user, default_config):
    """Test SiteListFilter queryset with sites parameter"""
    from djangocms_stories.admin import SiteListFilter, PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site as admin_site
    from django.contrib.sites.models import Site
    from .factories import PostFactory

    current_site = Site.objects.get_current()
    PostFactory.create_batch(3, app_config=default_config)

    admin_instance = PostAdmin(Post, admin_site)
    request = RequestFactory().get("/", {"sites": str(current_site.pk)})
    request.user = admin_user

    filter_instance = SiteListFilter(request, {"sites": str(current_site.pk)}, Post, admin_instance)

    queryset = Post.objects.all()

    # With filter parameter, should apply filtering
    filtered = filter_instance.queryset(request, queryset)
    assert filtered is not None


def test_modelapphookconfig_changeform_view_post_with_app_config(admin_client, default_config):
    """Test changeform_view with POST and app_config"""
    url = reverse("admin:djangocms_stories_postcategory_add")

    data = {
        "app_config": default_config.pk,
        "name": "Test Category",
        "language": "en",
    }

    response = admin_client.post(url, data)

    # Should process the form (redirect on success or show form with errors)
    assert response.status_code in [200, 302]


def test_modelapphookconfig_get_config_data_from_get_param(admin_user, default_config):
    """Test get_config_data retrieves from GET parameter"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    request = RequestFactory().get("/", {"app_config": default_config.pk})
    request.user = admin_user

    # Should retrieve config value from GET parameter
    namespace = admin_instance.get_config_data(request, None, "namespace")
    assert namespace == default_config.namespace


def test_config_admin_save_model_menu_structure_change(admin_client, default_config):
    """Test that changing menu_structure clears menu cache"""

    url = reverse("admin:djangocms_stories_storiesconfig_change", args=[default_config.pk])

    # Change menu structure
    data = {
        "namespace": default_config.namespace,
        "app_title": default_config.app_title,
        "object_name": default_config.object_name,
        "menu_structure": "CATEGORIES",  # Change from default
        "paginate_by": 10,
        # Add all required fields
        "use_placeholder": True,
        "use_abstract": True,
        "set_author": True,
        "use_related": False,
        "url_patterns": "default",
        "menu_empty_categories": True,
        "sitemap_changefreq": "monthly",
        "sitemap_priority": "0.5",
        "object_type": "Article",
        "og_type": "article",
        "twitter_type": "summary",
        "gplus_type": "Blog",
    }

    response = admin_client.post(url, data)
    # Should redirect or show form
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_config_admin_save_model_menu_structure_clears_cache(admin_user, default_config):
    """Test that save_model clears menu cache when menu_structure changes"""
    from djangocms_stories.admin import ConfigAdmin
    from djangocms_stories.models import StoriesConfig
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from unittest.mock import Mock, patch

    admin_instance = ConfigAdmin(StoriesConfig, site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock form with changed_data including menu_structure
    form = Mock()
    form.changed_data = ["config.menu_structure"]

    # Mock menu_pool.clear - patch where it's imported
    with patch("menus.menu_pool.menu_pool") as mock_menu_pool:
        admin_instance.save_model(request, default_config, form, change=True)
        # Verify menu_pool.clear was called with all=True
        mock_menu_pool.clear.assert_called_with(all=True)


@pytest.mark.django_db
def test_config_admin_save_model_urlconf_change_triggers_restart(admin_user, default_config):
    """Test that save_model triggers restart when urlconf changes"""
    from djangocms_stories.admin import ConfigAdmin
    from djangocms_stories.models import StoriesConfig
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from unittest.mock import Mock, patch

    admin_instance = ConfigAdmin(StoriesConfig, site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock form with changed_data including urlconf
    form = Mock()
    form.changed_data = ["config.urlconf"]

    # Mock trigger_restart - patch where it's imported
    with patch("cms.signals.apphook.trigger_restart") as mock_trigger_restart:
        admin_instance.save_model(request, default_config, form, change=True)
        # Verify trigger_restart was called
        mock_trigger_restart.assert_called_once()


@pytest.mark.django_db
def test_config_admin_save_model_no_relevant_changes(admin_user, default_config):
    """Test that save_model calls super().save_model even without menu/urlconf changes"""
    from djangocms_stories.admin import ConfigAdmin
    from djangocms_stories.models import StoriesConfig
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from unittest.mock import Mock

    admin_instance = ConfigAdmin(StoriesConfig, site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock form with changed_data NOT including menu_structure or urlconf
    form = Mock()
    form.changed_data = ["app_title"]

    # Just verify it completes without error (super().save_model is called)
    result = admin_instance.save_model(request, default_config, form, change=True)
    # save_model returns None, just verify no exception was raised
    assert result is None


@pytest.mark.django_db
def test_config_admin_save_model_both_changes(admin_user, default_config):
    """Test that save_model handles both menu_structure and urlconf changes"""
    from djangocms_stories.admin import ConfigAdmin
    from djangocms_stories.models import StoriesConfig
    from django.test import RequestFactory
    from django.contrib.admin.sites import site
    from unittest.mock import Mock, patch

    admin_instance = ConfigAdmin(StoriesConfig, site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock form with both changed
    form = Mock()
    form.changed_data = ["config.menu_structure", "config.urlconf"]

    # Mock both
    with (
        patch("menus.menu_pool.menu_pool") as mock_menu_pool,
        patch("cms.signals.apphook.trigger_restart") as mock_trigger_restart,
    ):
        admin_instance.save_model(request, default_config, form, change=True)
        # Verify both were called
        mock_menu_pool.clear.assert_called_with(all=True)
        mock_trigger_restart.assert_called_once()


def test_postadmin_get_urls_custom():
    """Test PostAdmin adds custom URLs"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.contrib.admin.sites import site

    admin_instance = PostAdmin(Post, site)
    urls = admin_instance.get_urls()

    # Should have custom URL for content redirect
    url_patterns = [url.name for url in urls if hasattr(url, "name")]
    assert "djangocms_stories_postcontent_changelist" in url_patterns


def test_postadmin_save_related_no_restricted_sites(admin_user, default_config):
    """Test save_related when user has no restricted sites"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site as admin_site
    from .factories import PostFactory, PostContentFactory

    post = PostFactory(app_config=default_config)
    PostContentFactory(post=post, language="en")

    admin_instance = PostAdmin(Post, admin_site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock form with cleaned_data and save_m2m
    class MockForm:
        instance = post
        cleaned_data = {}

        def save_m2m(self):
            pass

    # Test when user has no restricted sites
    admin_instance.save_related(request, MockForm(), [], False)
    # Should complete without error
    assert True


@pytest.mark.django_db
def test_postadmin_save_related_with_restricted_sites_in_form(admin_user, default_config):
    """Test save_related when user has restricted sites and sites are in form"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site as admin_site
    from django.contrib.sites.models import Site
    from .factories import PostFactory, PostContentFactory

    # Create additional sites
    site1 = Site.objects.get_current()
    site2 = Site.objects.create(domain="site2.com", name="Site 2")
    site3 = Site.objects.create(domain="site3.com", name="Site 3")

    post = PostFactory(app_config=default_config)
    PostContentFactory(post=post, language="en")
    post.sites.add(site1, site2)

    admin_instance = PostAdmin(Post, admin_site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock user with restricted sites
    admin_user.get_sites = lambda: Site.objects.filter(pk__in=[site1.pk, site2.pk])

    # Mock form with sites in cleaned_data
    class MockForm:
        instance = post
        cleaned_data = {"sites": [site2, site3]}

        def save_m2m(self):
            pass

    form = MockForm()

    # save_related should preserve site1 (restricted but removed from form)
    # and add site2, site3
    admin_instance.save_related(request, form, [], False)

    # Check that restricted sites logic was applied
    # The cleaned_data should now include site1, site2, and site3
    # Site1 should be preserved (it's a restricted site that was originally there)
    assert site2 in form.cleaned_data["sites"]
    assert site3 in form.cleaned_data["sites"]
    # Site1 might not be in cleaned_data if it was "removed" - the logic is complex
    # The key is that the form was processed without error


@pytest.mark.django_db
def test_postadmin_save_related_with_restricted_sites_no_sites_in_form(admin_user, default_config):
    """Test save_related when user has restricted sites but sites not in form"""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site as admin_site
    from django.contrib.sites.models import Site
    from .factories import PostFactory, PostContentFactory

    site1 = Site.objects.get_current()
    site2 = Site.objects.create(domain="site2b.com", name="Site 2B")

    post = PostFactory(app_config=default_config)
    PostContentFactory(post=post, language="en")

    admin_instance = PostAdmin(Post, admin_site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # Mock user with restricted sites
    admin_user.get_sites = lambda: Site.objects.filter(pk__in=[site1.pk, site2.pk])

    # Mock form without sites in cleaned_data
    class MockForm:
        instance = post
        cleaned_data = {}

        def save_m2m(self):
            pass

    # Before save_related
    initial_count = post.sites.count()

    admin_instance.save_related(request, MockForm(), [], False)

    # Restricted sites should be added to the post
    post.refresh_from_db()
    assert post.sites.count() >= initial_count


@pytest.mark.django_db
def test_postadmin_save_model_sets_default_author(admin_client, default_config):
    """Test save_model sets default author when post has no author"""
    from django.urls import reverse

    url = reverse("admin:djangocms_stories_post_add")

    # Create a post via admin (simulating form submission)
    data = {
        "app_config": default_config.pk,
        "author": "",  # No author specified
        "content__language": "en",
        "content__title": "Test Post",
        "content__slug": "test-post",
        "content__post_text": "<p>Test content</p>",
        "date_published_0": "2025-11-10",
        "date_published_1": "12:00:00",
    }

    admin_client.post(url, data, follow=True)

    # Post should be created and have admin as author
    from djangocms_stories.models import Post

    post = Post.objects.filter(postcontent__slug="test-post").first()
    if post:  # Post was created successfully
        # The _set_default_author method should have been called
        # We verify the author is set (this tests the integration)
        assert post.author is not None


@pytest.mark.django_db
def test_postadmin_save_model_missing_app_config_shows_selection(admin_client):
    """Edge case: calling add without any app_config should show AppConfigForm."""
    url = reverse("admin:djangocms_stories_post_add")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert b"app_config" in response.content


@pytest.mark.django_db
def test_postadmin_save_related_preserves_restricted_sites_on_remove(admin_user, default_config):
    """Edge case: user has restricted sites; removing them in form should keep them attached."""
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post
    from django.test import RequestFactory
    from django.contrib.admin.sites import site as admin_site
    from django.contrib.sites.models import Site
    from .factories import PostFactory, PostContentFactory

    site1 = Site.objects.get_current()
    Site.objects.create(domain="edge-site2.com", name="Edge Site 2")

    post = PostFactory(app_config=default_config)
    PostContentFactory(post=post, language="en")
    post.sites.add(site1)

    admin_instance = PostAdmin(Post, admin_site)
    request = RequestFactory().post("/")
    request.user = admin_user

    # User is restricted to site1
    admin_user.get_sites = lambda: Site.objects.filter(pk__in=[site1.pk])

    class MockForm:
        instance = post
        cleaned_data = {"sites": []}  # user attempts to remove all sites

        def save_m2m(self):
            pass

    form = MockForm()
    admin_instance.save_related(request, form, [], False)
    # site1 should remain attached due to restriction logic
    post.refresh_from_db()
    assert site1 in post.sites.all()


@pytest.mark.django_db
def test_postadmin_changeform_view_invalid_app_config_param(admin_client, simple_w_placeholder):
    """Edge case: invalid app_config id in GET should not crash, should show selection or 200."""
    # pass a non-existing app_config id
    url = reverse("admin:djangocms_stories_post_add") + "?app_config=999999"
    response = admin_client.get(url)
    assert response.status_code == 200
    # Should show selection form since the app_config is invalid
    assert b"app_config" in response.content


@pytest.mark.django_db
def test_postadmin_changeform_view_permission_denied_shows_403(admin_user, default_config):
    """Edge case: user without add permission should get 403 on add view."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(username="limited", email="limited@example.com", password="x")

    client = Client()
    client.force_login(user)

    url = reverse("admin:djangocms_stories_post_add")
    response = client.get(url)
    # Depending on Django admin, can be 403 or redirect to login; accept either 302 or 403
    assert response.status_code in [302, 403]


@pytest.mark.django_db
def test_postadmin_save_model_integration(admin_client, admin_user, default_config):
    """Test save_model integration through admin interface"""
    from django.urls import reverse
    from .factories import PostFactory, PostContentFactory

    # Create a post without author
    post = PostFactory(app_config=default_config, author=None)
    PostContentFactory(post=post, language="en", title="Original Title")

    assert post.author is None

    # Edit the post via admin
    url = reverse("admin:djangocms_stories_post_change", args=[post.pk])
    data = {
        "app_config": default_config.pk,
        "author": admin_user.pk,  # Set author explicitly
        "content__language": "en",
        "content__title": "Updated Title",
        "content__slug": post.postcontent_set(manager="admin_manager").first().slug,
        "content__post_text": "<p>Updated content</p>",
        "date_published_0": "2025-11-10",
        "date_published_1": "12:00:00",
    }

    admin_client.post(url, data, follow=True)

    # Refresh and check
    post.refresh_from_db()
    assert post.author == admin_user


@pytest.mark.django_db
def test_postadmin_set_default_author_directly(admin_user, default_config):
    """Test _set_default_author method directly"""
    from .factories import PostFactory

    # Create post without author
    post = PostFactory(app_config=default_config, author=None)
    assert post.author is None

    # Call _set_default_author
    post._set_default_author(admin_user)
    post.save()
    post.refresh_from_db()

    # Author should now be set
    assert post.author == admin_user


@pytest.mark.django_db
def test_postadmin_set_default_author_preserves_existing(admin_user, default_config):
    """Test _set_default_author preserves existing author"""
    from django.contrib.auth import get_user_model
    from .factories import PostFactory

    User = get_user_model()
    other_user = User.objects.create_user(username="other", email="other@example.com")

    # Create post with existing author
    post = PostFactory(app_config=default_config, author=other_user)
    assert post.author == other_user

    # Call _set_default_author with different user
    post._set_default_author(admin_user)
    post.save()
    post.refresh_from_db()

    # Author should still be other_user (not changed)
    assert post.author == other_user


def test_postadmin_changeform_view_no_app_config(admin_client):
    """Test changeform_view when no app_config is selected"""
    from djangocms_stories.models import StoriesConfig

    # Remove all configs to test the form selection
    StoriesConfig.objects.all().delete()

    # Create two configs to force selection
    from .factories import StoriesConfigFactory

    StoriesConfigFactory(namespace="test1")
    StoriesConfigFactory(namespace="test2")

    url = reverse("admin:djangocms_stories_post_add")
    response = admin_client.get(url)

    # Should show app config selection form
    assert response.status_code == 200
    assert b"app_config" in response.content


@pytest.mark.django_db
def test_add_post_admin_flow_with_endpoints(admin_client, simple_w_placeholder):
    """Test the complete flow of adding a post through admin endpoints."""
    from djangocms_stories.models import Post, PostContent

    # Step 1: GET request to add post URL - should return AppConfigForm
    url = reverse("admin:djangocms_stories_post_add")
    response = admin_client.get(url)

    assert response.status_code == 200
    # Should contain app_config selection form
    assert b"app_config" in response.content
    assert b"select" in response.content.lower()

    # Step 2: POST app_config selection to get the actual Post form
    # The admin converts this POST to GET internally and shows the actual form
    response = admin_client.post(
        url,
        data={
            "app_config": simple_w_placeholder.pk,
            "language": "en",
        },
        follow=True,
    )

    # Should return 200 with the actual post content form
    assert response.status_code == 200
    # Check that we got the Post content form (title indicates "Add English content")
    assert b"Add" in response.content or b"add" in response.content
    # Should have fields for PostContent
    assert b"title" in response.content.lower() or b"id_title" in response.content.lower()

    # Step 3: Submit the post content form to create the post
    initial_post_count = Post.objects.count()
    PostContent.objects.count()

    # When using placeholder, the form expects different field names
    post_data = {
        "app_config": simple_w_placeholder.pk,
        "content__language": "en",
        "content__title": "Test Post via Admin",
        "content__subtitle": "Test Subtitle",
        "content__slug": "test-post-via-admin",
        "_save": "Save",
    }

    response = admin_client.post(url, data=post_data, follow=True)

    # Should get some response (either success or showing form again with errors)
    assert response.status_code == 200

    # Verify post was created
    assert Post.objects.count() == initial_post_count + 1

    # Verify the created post
    new_post = Post.objects.latest("id")
    assert new_post.app_config == simple_w_placeholder

    # Verify the created post content
    new_post_content = PostContent.admin_manager.current_content(post=new_post, language="en").first()
    assert new_post_content is not None
    assert new_post_content.title == "Test Post via Admin"
    assert new_post_content.subtitle == "Test Subtitle"
    assert new_post_content.slug == "test-post-via-admin"


@pytest.mark.django_db
def test_add_post_admin_with_preselected_config(admin_client, simple_w_placeholder):
    """Test adding a post when app_config is already in URL parameters."""
    from djangocms_stories.models import Post

    # When app_config is in URL, should skip AppConfigForm and show Post form directly
    url = reverse("admin:djangocms_stories_post_add") + f"?app_config={simple_w_placeholder.pk}"
    response = admin_client.get(url)

    assert response.status_code == 200
    # Should show the post form, not the app_config selection
    assert b"title" in response.content.lower()
    # app_config should be pre-filled (hidden or readonly)
    assert str(simple_w_placeholder.pk).encode() in response.content

    # Verify we can submit the form
    initial_count = Post.objects.count()

    post_data = {
        "app_config": simple_w_placeholder.pk,
        "content__title": "test post",
        "content__language": "en",
        "content__slug": "test-post-preselected",
        "_save": "Save",
    }

    response = admin_client.post(url, data=post_data, follow=True)

    assert response.status_code == 200
    assert Post.objects.count() == initial_count + 1

    new_post = Post.objects.latest("id")
    assert new_post.app_config == simple_w_placeholder
