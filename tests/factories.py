import factory
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model
from datetime import timezone

from djangocms_stories.settings import PERMALINK_TYPE_FULL_DATE
from djangocms_stories.cms_appconfig import StoriesConfig
from djangocms_stories.models import Post, PostContent, PostCategory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")  # Set a default password


class PostCategoryFactory(DjangoModelFactory):
    class Meta:
        model = PostCategory

    name = factory.Faker("word")
    slug = factory.Faker("slug")


class StoriesConfigFactory(DjangoModelFactory):
    class Meta:
        model = StoriesConfig

    namespace = factory.Faker("slug")
    use_placeholder = True  # Assuming default value, adjust as necessary
    url_patterns = PERMALINK_TYPE_FULL_DATE


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
