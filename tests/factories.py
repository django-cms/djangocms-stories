import factory
from factory.django import DjangoModelFactory

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from datetime import timezone

from djangocms_stories.settings import PERMALINK_TYPE_FULL_DATE
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post, PostContent, PostCategory
import uuid


default_site = Site.objects.get(pk=1)  # Assuming you have a default site with pk=1


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.LazyFunction(lambda: str(uuid.uuid4()))
    email = factory.Faker("email")
    first_name = factory.Faker("word")
    last_name = factory.Faker("word")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")  # Set a default password


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = "sites.Site"

    domain = factory.Faker("domain_name")
    name = factory.Faker("company")


class StoriesConfigFactory(DjangoModelFactory):
    class Meta:
        model = StoriesConfig

    namespace = factory.LazyFunction(lambda: str(uuid.uuid4()))
    use_placeholder = True  # Assuming default value, adjust as necessary
    url_patterns = PERMALINK_TYPE_FULL_DATE


class PostCategoryFactory(DjangoModelFactory):
    class Meta:
        model = PostCategory

    app_config = factory.SubFactory(StoriesConfigFactory)
    name = factory.Faker("word")
    slug = factory.LazyFunction(lambda: str(uuid.uuid4()))
    priority = factory.Faker("random_int", min=1, max=10)


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    app_config = factory.SubFactory(StoriesConfigFactory)
    author = factory.SubFactory(UserFactory)
    categories = factory.RelatedFactoryList(
        PostCategoryFactory,
        size=2,  # Adjust the number of categories as needed
    )
    date_published = factory.Faker("date_time_this_decade", tzinfo=timezone.utc)
    date_published_end = factory.Faker("date_time_this_decade", tzinfo=timezone.utc)
    date_featured = factory.Faker("date_time_this_decade", tzinfo=timezone.utc)


class PostContentFactory(DjangoModelFactory):
    class Meta:
        model = PostContent

    post = factory.SubFactory(PostFactory)
    language = "en"
    title = factory.Faker("sentence", nb_words=4)
    subtitle = factory.Faker("sentence", nb_words=6)
    meta_title = factory.Faker("sentence", nb_words=4)
    meta_description = factory.Faker("sentence", nb_words=10)
    post_text = factory.Faker("paragraph", nb_sentences=3)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        if apps.is_installed("djangocms_versioning"):
            # Add version object
            from djangocms_versioning.constants import DRAFT
            from djangocms_versioning.models import Version

            Version.objects.create(content=obj, state=DRAFT, created_by=UserFactory(is_superuser=True))
