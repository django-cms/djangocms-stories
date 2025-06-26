import hashlib

from cms.models import CMSPlugin, PlaceholderRelationField
from cms.utils.placeholder import get_placeholder_from_slot
from django.apps import apps
from django.conf import settings as dj_settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import NoReverseMatch, reverse
from django.utils import translation
from django.utils.encoding import force_bytes, force_str
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils.translation import get_language, gettext, gettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField
from filer.models import ThumbnailOption
from menus.menu_pool import menu_pool
from meta.models import ModelMeta
from parler.models import TranslatableModel, TranslatedFields
from sortedm2m.fields import SortedManyToManyField
from taggit_autosuggest.managers import TaggableManager

from .cms_appconfig import StoriesConfig
from .fields import slugify
from .managers import AdminManager, GenericDateTaggedManager, SiteManager
from .settings import get_setting

BLOG_CURRENT_POST_IDENTIFIER = get_setting("CURRENT_POST_IDENTIFIER")
BLOG_CURRENT_NAMESPACE = get_setting("CURRENT_NAMESPACE")
BLOG_PLUGIN_TEMPLATE_FOLDERS = get_setting("PLUGIN_TEMPLATE_FOLDERS")
BLOG_ALLOW_UNICODE_SLUGS = get_setting("ALLOW_UNICODE_SLUGS")


thumbnail_model = f"{ThumbnailOption._meta.app_label}.{ThumbnailOption.__name__}"


# HTMLField is a custom field that allows to use a rich text editor
# Probe for djangocms_text first, then for djangocms_text_ckeditor
# and finally fallback to a simple textarea
if apps.is_installed("djangocms_text"):
    from djangocms_text.fields import HTMLField
elif apps.is_installed("djangocms_text_ckeditor"):  # pragma: no cover
    from djangocms_text_ckeditor.fields import HTMLField
else:  # pragma: no cover
    from django import forms

    class HTMLField(models.TextField):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("widget", forms.Textarea)
            super().__init__(*args, **kwargs)


def _get_language(instance, language):
    available_languages = instance.get_available_languages()
    if language and language in available_languages:
        return language
    language = translation.get_language()
    if language and language in available_languages:
        return language
    language = instance.get_current_language()
    if language and language in available_languages:
        return language
    if get_setting("USE_FALLBACK_LANGUAGE_IN_URL"):
        for fallback_language in instance.get_fallback_languages():
            if fallback_language in available_languages:
                return fallback_language
    return language


class PostMetaMixin:
    def get_meta_attribute(self, param):
        """
        Retrieves django-meta attributes from apphook config instance
        :param param: django-meta attribute passed as key
        """
        return self._get_meta_value(param, getattr(self.app_config, param)) or ""

    def get_full_url(self):
        """
        Return the url with protocol and domain url
        """
        return self.build_absolute_uri(self.get_absolute_url())


class PostCategory(PostMetaMixin, ModelMeta, TranslatableModel):
    """
    Post category allows to structure content in a hierarchy of categories.
    """

    parent = models.ForeignKey(
        "self", verbose_name=_("parent"), null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(_("created at"), auto_now_add=True)
    date_modified = models.DateTimeField(_("modified at"), auto_now=True)
    app_config = models.ForeignKey(
        StoriesConfig,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("app. config"),
        help_text=_("When selecting a value, the form is reloaded to get the updated default"),
    )
    priority = models.IntegerField(_("priority"), blank=True, null=True)
    main_image = FilerImageField(
        verbose_name=_("main image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="djangocms_category_image",
    )
    main_image_thumbnail = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image thumbnail"),
        related_name="djangocms_category_thumbnail",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    main_image_full = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image full"),
        related_name="djangocms_category_full",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=752),
        slug=models.SlugField(
            _("slug"),
            max_length=752,
            blank=True,
            db_index=True,
            allow_unicode=BLOG_ALLOW_UNICODE_SLUGS,
        ),
        meta_description=models.TextField(verbose_name=_("category meta description"), blank=True, default=""),
        meta={"unique_together": (("language_code", "slug"),)},
        abstract=HTMLField(_("abstract"), blank=True, default="", configuration="BLOG_ABSTRACT_CKEDITOR"),
    )

    _metadata = {
        "title": "get_title",
        "description": "get_description",
        "og_description": "get_description",
        "twitter_description": "get_description",
        "schemaorg_description": "get_description",
        "schemaorg_type": "get_meta_attribute",
        "locale": "get_locale",
        "object_type": "get_meta_attribute",
        "og_type": "get_meta_attribute",
        "og_app_id": "get_meta_attribute",
        "og_profile_id": "get_meta_attribute",
        "og_publisher": "get_meta_attribute",
        "og_author_url": "get_meta_attribute",
        "og_author": "get_meta_attribute",
        "twitter_type": "get_meta_attribute",
        "twitter_site": "get_meta_attribute",
        "twitter_author": "get_meta_attribute",
        "url": "get_absolute_url",
    }

    class Meta:
        verbose_name = _("post category")
        verbose_name_plural = _("post categories")
        ordering = (F("priority").asc(nulls_last=True),)

    def descendants(self):  # pragma: no cover
        import warnings

        warnings.warn(
            "The `descendants` method is deprecated and will be removed in future versions. "
            "Use `get_descendants` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_descendants()

    def get_descendants(self):
        children = []
        if self.children.exists():
            children.extend(self.children.all())
            for child in self.children.all():
                children.extend(child.get_descendants())
        return children

    @cached_property
    def linked_posts(self):
        """returns all linked posts in the same appconfig namespace"""
        return self.posts.filter(app_config=self.app_config)

    @cached_property
    def count(self):
        return self.linked_posts.filter(Q(sites__isnull=True) | Q(sites=Site.objects.get_current())).count()

    @cached_property
    def count_all_sites(self):
        return self.linked_posts.count()

    def get_absolute_url(self, lang=None):
        lang = _get_language(self, lang)
        if self.has_translation(lang):
            slug = self.safe_translation_getter("slug", language_code=lang)
            return reverse(
                "%s:posts-category" % self.app_config.namespace,
                kwargs={"category": slug},
                current_app=self.app_config.namespace,
            )
        # in case category doesn't exist in this language, gracefully fallback
        # to posts-latest
        return reverse("%s:posts-latest" % self.app_config.namespace, current_app=self.app_config.namespace)

    def __str__(self):
        default = gettext("PostCategory (no translation)")
        return self.safe_translation_getter("name", any_language=True, default=default)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        menu_pool.clear(all=True)
        for lang in self.get_available_languages():
            self.set_current_language(lang)
            if not self.slug and self.name:
                self.slug = slugify(force_str(self.name))
        self.save_translations()

    def delete(self, *args, **kwargs):
        menu_pool.clear(all=True)
        return super().delete(*args, **kwargs)

    def get_title(self):
        title = self.safe_translation_getter("name", any_language=True)
        return title.strip()

    def get_description(self):
        description = self.safe_translation_getter("meta_description", any_language=True)
        return strip_tags(description).strip()


class Post(models.Model):
    """
    Posts
    """

    author = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        blank=True,
        related_name="djangocms_stories_post_author",
        on_delete=models.PROTECT,
    )

    date_created = models.DateTimeField(_("created"), auto_now_add=True)
    date_modified = models.DateTimeField(_("last modified"), auto_now=True)
    date_published = models.DateTimeField(_("published since"), null=True, blank=True)
    date_published_end = models.DateTimeField(_("published until"), null=True, blank=True)
    date_featured = models.DateTimeField(_("featured date"), null=True, blank=True)
    include_in_rss = models.BooleanField(_("include in RSS feed"), default=True)
    categories = models.ManyToManyField(
        "djangocms_stories.PostCategory", verbose_name=_("category"), related_name="posts", blank=True
    )
    main_image = FilerImageField(
        verbose_name=_("main image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="djangocms_stories_post_image",
    )
    main_image_thumbnail = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image thumbnail"),
        related_name="djangocms_stories_post_thumbnail",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    main_image_full = models.ForeignKey(
        thumbnail_model,
        verbose_name=_("main image full"),
        related_name="djangocms_stories_post_full",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    enable_comments = models.BooleanField(
        verbose_name=_("enable comments on post"), default=get_setting("ENABLE_COMMENTS")
    )
    sites = models.ManyToManyField(
        "sites.Site",
        verbose_name=_("Site(s)"),
        blank=True,
        help_text=_(
            "Select sites in which to show the post. If none is set it will be visible in all the configured sites."
        ),
    )
    app_config = models.ForeignKey(
        StoriesConfig,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("app. config"),
        help_text=_("When selecting a value, the form is reloaded to get the updated default"),
    )

    tags = TaggableManager(
        blank=True,
        related_name="djangocms_stories_tags",
        help_text=_("Type a tag and hit tab, or start typing and select from autocomplete list."),
    )

    related = SortedManyToManyField("self", verbose_name=_("Related Posts"), blank=True, symmetrical=False)

    objects = GenericDateTaggedManager()

    _metadata = {
        "title": "get_title",
        "description": "get_description",
        "keywords": "get_keywords",
        "og_description": "get_description",
        "twitter_description": "get_description",
        "schemaorg_description": "get_description",
        "locale": "get_locale",
        "image": "get_image_full_url",
        "image_width": "get_image_width",
        "image_height": "get_image_height",
        "object_type": "get_meta_attribute",
        "og_type": "get_meta_attribute",
        "og_app_id": "get_meta_attribute",
        "og_profile_id": "get_meta_attribute",
        "og_publisher": "get_meta_attribute",
        "og_author_url": "get_meta_attribute",
        "og_author": "get_meta_attribute",
        "twitter_type": "get_meta_attribute",
        "twitter_site": "get_meta_attribute",
        "twitter_author": "get_meta_attribute",
        "schemaorg_type": "get_meta_attribute",
        "published_time": "date_published",
        "modified_time": "date_modified",
        "expiration_time": "date_published_end",
        "tag": "get_tags",
        "url": "get_absolute_url",
    }

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ("-date_published", "-date_created")
        get_latest_by = "date_published"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content_cache = {}
        self._language_cache = None

    def __str__(self):
        default = gettext("Post (no translation)")
        return self.safe_translation_getter("title", any_language=True, default=default)

    @admin.display(boolean=True)
    def featured(self):
        if not self.date_featured:
            return False
        return bool(self.date_featured <= now())

    def get_content(self, language=None, show_draft_content=False):
        if not language:
            language = translation.get_language()

        key = f"{language}_{'latest' if show_draft_content else 'public'}"

        try:
            return self._content_cache[key]
        except KeyError:
            if show_draft_content:
                qs = self.postcontent_set(manager="admin_manager").current_content()
            else:
                qs = self.postcontent_set
            qs = qs.prefetch_related(
                "placeholders",
                "post__categories",
            ).filter(language=language)

            self._content_cache[key] = qs.first()
            return self._content_cache[key]

    def safe_translation_getter(
        self, field, default=None, language_code=None, any_language=False, show_draft_content=False
    ):
        """
        Fetch a content property, and return a default value
        when both the translation and fallback language are missing.

        When ``any_language=True`` is used, the function also looks
        into other languages to find a suitable value. This feature can be useful
        for "title" attributes for example, to make sure there is at least something being displayed.
        Also consider using ``field = TranslatedField(any_language=True)`` in the model itself,
        to make this behavior the default for the given field.
        """

        content_obj = self.get_content(language_code, show_draft_content=show_draft_content)
        if content_obj is None and any_language and self.get_available_languages():
            content_obj = self.get_content(self.get_available_languages()[0], show_draft_content=show_draft_content)
        return getattr(content_obj, field, default)

    @property
    def guid(self):
        language = get_language()
        slug = self.safe_translation_getter("slug", language_code=language, any_language=True)
        base_string = f"-{language}-{slug}-{self.app_config.namespace}-"
        return hashlib.sha256(force_bytes(base_string)).hexdigest()

    @property
    def date(self):
        if self.date_featured:
            return self.date_featured
        return self.date_published or self.date_created

    def get_available_languages(self):
        if not (self._language_cache):
            self._language_cache = list(self.postcontent_set.all().values_list("language", flat=True))
        return self._language_cache

    def get_absolute_url(self, language=None):
        lang = language or translation.get_language()
        with translation.override(lang):
            category = self.categories.first()
            kwargs = {}
            current_date = self.date
            urlconf = get_setting("PERMALINK_URLS")[self.app_config.url_patterns]
            if "<int:year>" in urlconf:
                kwargs["year"] = current_date.year
            if "<int:month>" in urlconf:
                kwargs["month"] = "%02d" % current_date.month
            if "<int:day>" in urlconf:
                kwargs["day"] = "%02d" % current_date.day
            if "<str:slug>" in urlconf or "<slug:slug>" in urlconf:
                kwargs["slug"] = self.safe_translation_getter("slug", language_code=lang, any_language=True)  # NOQA
            if "<slug:category>" in urlconf or "<str:category>" in urlconf:
                kwargs["category"] = category.safe_translation_getter("slug", language_code=lang, any_language=True)  # NOQA
            try:
                return reverse(
                    "%s:post-detail" % self.app_config.namespace, kwargs=kwargs, current_app=self.app_config.namespace
                )
            except NoReverseMatch:
                return ""

    def get_title(self, language=None):
        title = self.safe_translation_getter("meta_title", language_code=language, any_language=True)
        if not title:
            title = self.safe_translation_getter("title", language_code=language, any_language=True) or _("No title")
        return title.strip()

    def get_keywords(self, language=None):
        """
        Returns the list of keywords (as python list)
        :return: list
        """
        keywords = self.safe_translation_getter("meta_keywords", language_code=language, any_language=True).strip()
        if "".join(keywords) == "":
            return []
        return [keyword.strip() for keyword in keywords.split(",")]

    def get_description(self, language=None):
        description = self.safe_translation_getter("meta_description", language_code=language, any_language=True)
        if not description:
            description = self.safe_translation_getter("abstract", any_language=True)
        return strip_tags(description).strip()

    def get_image_full_url(self):
        if self.main_image:
            if thumbnail_options := get_setting("META_IMAGE_SIZE"):
                thumbnail_url = get_thumbnailer(self.main_image).get_thumbnail(thumbnail_options).url
                return self.build_absolute_uri(thumbnail_url)
            return self.build_absolute_uri(self.main_image.url)
        return ""

    def get_image_width(self):
        if self.main_image:
            thumbnail_options = get_setting("META_IMAGE_SIZE")
            if thumbnail_options:
                return get_thumbnailer(self.main_image).get_thumbnail(thumbnail_options).width
            return self.main_image.width

    def get_image_height(self):
        if self.main_image:
            thumbnail_options = get_setting("META_IMAGE_SIZE")
            if thumbnail_options:
                return get_thumbnailer(self.main_image).get_thumbnail(thumbnail_options).height
            return self.main_image.height

    def get_tags(self):
        """
        Returns the list of object tags as comma separated list
        """
        taglist = [tag.name for tag in self.tags.all()]
        return ",".join(taglist)

    def get_author(self):
        """
        Return the author (user) objects
        """
        return self.author

    def _set_default_author(self, current_user):
        if not self.author_id and self.app_config.set_author:
            if get_setting("AUTHOR_DEFAULT") is True:
                user = current_user
            else:
                user = get_user_model().objects.get(username=get_setting("AUTHOR_DEFAULT"))
            self.author = user

    def thumbnail_options(self):
        if self.main_image_thumbnail_id:
            return self.main_image_thumbnail.as_dict
        else:
            return get_setting("IMAGE_THUMBNAIL_SIZE")

    def full_image_options(self):
        if self.main_image_full_id:
            return self.main_image_full.as_dict
        else:
            return get_setting("IMAGE_FULL_SIZE")

    def get_cache_key(self, language, prefix):
        return f"djangocms-stories:{prefix}:{language}:{self.guid}"


class PostContent(PostMetaMixin, ModelMeta, models.Model):
    structure_template = "post_detail.html"
    no_structure_template = "no_post_structure.html"

    class Meta:
        verbose_name = _("post content")
        verbose_name_plural = _("post contents")
        ordering = ("-post__date_published", "-post__date_created")
        get_latest_by = "date_published"

    # Gruping fields
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=15, db_index=True)
    # Content fields (by post and language
    title = models.CharField(_("title"), max_length=752)
    slug = models.SlugField(
        _("slug"),
        max_length=752,
        blank=True,
        db_index=True,
        allow_unicode=BLOG_ALLOW_UNICODE_SLUGS,
    )
    subtitle = models.CharField(verbose_name=_("subtitle"), max_length=767, blank=True, default="")
    abstract = HTMLField(_("abstract"), blank=True, default="", configuration="BLOG_ABSTRACT_CKEDITOR")
    meta_description = models.TextField(verbose_name=_("post meta description"), blank=True, default="")
    meta_keywords = models.TextField(verbose_name=_("post meta keywords"), blank=True, default="")
    meta_title = models.CharField(
        verbose_name=_("post meta title"),
        help_text=_("used in title tag and social sharing"),
        max_length=2000,
        blank=True,
        default="",
    )
    post_text = HTMLField(_("text"), default="", blank=True, configuration="BLOG_POST_TEXT_CKEDITOR")
    placeholders = PlaceholderRelationField()

    objects = SiteManager()
    admin_manager = AdminManager()
    # objects = GenericDateTaggedManager()
    # admin_manager = AdminDateTaggedManager()

    @property
    def author(self):
        return self.post.author

    @property
    def date_published(self):
        return self.post.date_published

    @property
    def date_published_end(self):
        return self.post.date_published_end

    @property
    def app_config(self):
        return self.post.app_config

    @property
    def categories(self):
        return self.post.categories

    @cached_property
    def media(self):
        return get_placeholder_from_slot(self.placeholders, "media")

    @cached_property
    def content(self):
        return get_placeholder_from_slot(self.placeholders, "content")

    def save(self, *args, **kwargs):
        """
        Handle some auto-configuration during save
        """
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self, language=None):
        return self.post.get_absolute_url(language=language)

    def get_template(self):
        # Used for the cms structure endpoint
        if self.app_config and self.app_config.template_prefix:
            folder = self.app_config.template_prefix
        else:
            folder = self._meta.app_label
        # Use the structure template if the app_config is not set or if it requests structure mode
        if not self.app_config or self.app_config.use_placeholder:
            return f"{folder}/{self.structure_template}"
        else:
            return f"{folder}/{self.no_structure_template}"

    def __str__(self):
        return self.title or _("Untitled")


class BasePostPlugin(CMSPlugin):
    app_config = models.ForeignKey(
        StoriesConfig,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("app. config"),
        help_text=_("When selecting a value, the form is reloaded to get the updated default"),
    )
    current_site = models.BooleanField(
        _("current site"), default=True, help_text=_("Select items from the current site only")
    )
    template_folder = models.CharField(
        max_length=200,
        verbose_name=_("Plugin layout"),
        help_text=_("Select plugin layout to load for this instance"),
        default=BLOG_PLUGIN_TEMPLATE_FOLDERS[0][0],
        choices=BLOG_PLUGIN_TEMPLATE_FOLDERS,
    )

    class Meta:
        abstract = True

    def optimize(self, qs):
        """
        Apply select_related / prefetch_related to optimize the view queries
        :param qs: queryset to optimize
        :return: optimized queryset
        """
        return qs.select_related("post", "post__app_config").prefetch_related(
            "post__categories", "post__categories__translations", "post__categories__app_config"
        )

    def post_content_queryset(self, request=None, selected_posts=None):
        language = translation.get_language()
        if request and getattr(request, "toolbar", False) and request.toolbar.edit_mode_active:
            post_contents = PostContent.admin_manager.latest_content()
        else:
            post_contents = PostContent.objects.all()
        if self.app_config:
            post_contents = post_contents.filter(post__app_config=self.app_config)
        if self.current_site:
            post_contents = post_contents.on_site(get_current_site(request))
        if selected_posts:
            post_contents = post_contents.filter(post__in=selected_posts)
        post_contents = post_contents.prefetch_related("post").filter(language=language)
        return self.optimize(post_contents)


class LatestPostsPlugin(BasePostPlugin):
    latest_posts = models.IntegerField(
        _("entries"),
        default=get_setting("LATEST_POSTS"),
        help_text=_("The number of latests entries to be displayed."),
    )
    tags = TaggableManager(
        _("filter by tag"),
        blank=True,
        help_text=_("Show only the entries tagged with chosen tags."),
        related_name="djangocms_stories_latest_post",
    )
    categories = models.ManyToManyField(
        "djangocms_stories.PostCategory",
        blank=True,
        verbose_name=_("filter by category"),
        help_text=_("Show only the posts of the chosen categories."),
    )

    def __str__(self):
        return force_str(_("%s latest posts by tag") % self.latest_posts)

    def copy_relations(self, old_instance):
        for tag in old_instance.tags.all():
            self.tags.add(tag)
        for category in old_instance.categories.all():
            self.categories.add(category)

    def get_post_contents(self, request):
        post_contents = self.post_content_queryset(request)
        if self.tags.exists():
            post_contents = post_contents.filter(post__tags__in=list(self.tags.all()))
        if self.categories.exists():
            post_contents = post_contents.filter(post__categories__in=list(self.categories.all()))
        return self.optimize(post_contents.distinct())[: self.latest_posts]


class AuthorEntriesPlugin(BasePostPlugin):
    authors = models.ManyToManyField(
        dj_settings.AUTH_USER_MODEL,
        verbose_name=_("authors"),
    )
    latest_posts = models.IntegerField(
        _("entries"),
        default=get_setting("LATEST_POSTS"),
        help_text=_("The number of author entries to be displayed."),
    )

    def __str__(self):
        return force_str(_("%s latest entries by author") % self.latest_posts)

    def copy_relations(self, oldinstance):
        self.authors.set(oldinstance.authors.all())

    def get_post_contents(self, request):
        return self.post_content_queryset(request)

    def get_authors(self, request):
        authors = self.authors.all()
        for author in authors:
            qs = self.get_post_contents(request).filter(post__author=author)
            # total nb of posts
            author.count = qs.count()
            # "the number of author posts to be displayed"
            author.post_contents = qs[: self.latest_posts]
        return authors


class FeaturedPostsPlugin(BasePostPlugin):
    posts = SortedManyToManyField(Post, verbose_name=_("Featured posts"))

    def __str__(self):
        return force_str(_("Featured posts"))

    def copy_relations(self, oldinstance):
        self.posts.set(oldinstance.posts.all())

    def get_posts(
        self,
        request,
    ):
        return self.post_content_queryset(request, selected_posts=self.posts.all())


class GenericBlogPlugin(BasePostPlugin):
    class Meta:
        abstract = False

    def __str__(self):
        return force_str(_("generic blog plugin"))


@receiver(pre_delete, sender=Post)
def pre_delete_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, "feed")
        cache.delete(key)


@receiver(post_save, sender=Post)
def post_save_post(sender, instance, **kwargs):
    for language in instance.get_available_languages():
        key = instance.get_cache_key(language, "feed")
        cache.delete(key)
