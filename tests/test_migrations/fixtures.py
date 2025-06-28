from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.models import Post, PostContent


POST_CONTENT_DATA = {
    "post_en1": {
        "title": "Test Post 1",
        "slug": "test-post-1",
        "meta_description": "Test Post 1 Description",
        "meta_keywords": "test, post, 1",
        "meta_title": "Test Post 1 Meta Title",
        "abstract": "This is a test post 1 abstract.",
    },
    "post_fr1": {
        "title": "Test Post 1 FR",
        "slug": "test-post-1-fr",
        "meta_description": "Test Post 1 Description FR",
        "meta_keywords": "test, post, 1, fr",
        "meta_title": "Test Post 1 Meta Title FR",
        "abstract": "<p>Ceci <b>est</b> un résumé de l'article de test 1 en français.</p>",
    },
}


def increase_pk(model):
    """Generate non-consecutive primary keys for the given model."""
    import random
    from django.db import connection

    with connection.cursor() as cursor:
        table = model._meta.db_table
        pk_column = model._meta.pk.column
        cursor.execute(f"SELECT MAX({pk_column}) FROM {table}")
        max_pk = cursor.fetchone()[0] or 0
        increment = random.randint(0, 10)
        new_pk = max_pk + increment
        if connection.vendor == "sqlite":
            cursor.execute(f"UPDATE sqlite_sequence SET seq = {new_pk} WHERE name = '{table}'")


def generate_blog(config, user, **wkargs):
    post = Post.objects.create(
        app_config=config,
        **wkargs,
    )
    post.sites.add(1)  # Assuming site ID 1 is the default site
    increase_pk(Post)
    post_en = PostContent.objects.with_user(user).create(
        post=post,
        language="en",
        title="Test Post 1",
        slug="test-post-1",
    )
    increase_pk(PostContent)
    post_fr = PostContent.objects.with_user(user).create(
        post=post,
        language="fr",
        title="Test Post 1 (FR)",
        slug="test-post-1",
    )
    increase_pk(PostContent)
    return post, post_en, post_fr


def generate_config(**kwargs):
    config = BlogConfig.objects.create(app_title="Test Blog", object_name="Article", **kwargs)
    increase_pk(BlogConfig)
    return config


def generate_category(config, **kwargs):
    from djangocms_blog.models import BlogCategory

    category = BlogCategory.objects.create(app_config=config, **kwargs)
    increase_pk(BlogCategory)
    return category


def generate_placeholder_content(source, language, **kwargs):
    from cms.api import add_plugin
    from cms.models import Placeholder

    placeholder = Placeholder.objects.create(slot="content", source=source)
    increase_pk(Placeholder)

    content = add_plugin(
        placeholder,
        "TextPlugin",
        language,
        **kwargs,
    )
    return content
