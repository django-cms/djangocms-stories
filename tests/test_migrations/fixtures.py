from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.models import Post, PostContent


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


def generate_blog(config, **wkargs):
    post = Post.objects.create(
        app_config=config,
        **wkargs,
    )
    increase_pk(Post)
    post_en = PostContent.admin_manager.create(
        post=post,
        language="en",
        title="Test Post 1",
        slug="test-post-1",
    )
    increase_pk(PostContent)
    post_fr = PostContent.admin_manager.create(
        post=post,
        language="fr",
        title="Test Post 1 (FR)",
        slug="test-post-1",
    )
    increase_pk(PostContent)
    return post, post_en, post_fr


def generate_config(**kwargs):
    return BlogConfig.objects.create(app_title="Test Blog", object_name="Article", **kwargs)
    increase_pk(BlogConfig)
