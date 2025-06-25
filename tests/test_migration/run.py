import django.conf
from django.core.management import execute_from_command_line


def increase_pk(model):
    """Generate non-consecutive primary keys for the given model."""
    import random
    from django.db import connection

    with connection.cursor() as cursor:
        table = model._meta.db_table
        pk_column = model._meta.pk.column
        cursor.execute(f"SELECT MAX({pk_column}) FROM {table}")
        max_pk = cursor.fetchone()[0] or 0
        print(max_pk, "max_pk for", table)
        increment = random.randint(0, 10)
        new_pk = max_pk + increment
        if connection.vendor == "sqlite":
            cursor.execute(f"UPDATE sqlite_sequence SET seq = {new_pk} WHERE name = '{table}'")


def setup_blog_testproj():
    from django.apps import apps
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    assert apps.is_installed("djangocms_blog"), "djangocms_blog is not installed"

    # Migrate djangocms_blog to the specific migration
    execute_from_command_line(["manage.py", "migrate", "cms", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "menus", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "sessions", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "contenttypes", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "sites", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "auth", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "taggit", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "easy_thumbnails", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "filer", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_blog", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_text", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_versioning", "--noinput"])
    # Migrate all apps except the specific one to latest
    # execute_from_command_line(["manage.py", "migrate", "--noinput"])

    User = get_user_model()
    user, _ = User.objects.get_or_create(username="staff", is_staff=True, is_superuser=False)
    group, _ = Group.objects.get_or_create(name="Editors")
    group.user_set.add(user)

    from djangocms_blog.cms_appconfig import BlogConfig
    from djangocms_blog.models import Post, PostContent

    def generate_blog(config):
        post = Post.objects.create(
            app_config=config1,
            author=user,
        )
        increase_pk(Post)
        post_en = PostContent.admin_manager.create(
            post=post1,
            language="en",
            title="Test Post 1",
            slug="test-post-1",
        )
        increase_pk(PostContent)
        post_fr = PostContent.admin_manager.create(
            post=post1,
            language="fr",
            title="Test Post 1 (FR)",
            slug="test-post-1",
        )
        increase_pk(PostContent)
        return post, post_en, post_fr

    config1 = BlogConfig.objects.create(
        namespace="testblog",
        app_title="Test Blog",
        object_name="Article",
    )
    increase_pk(BlogConfig)
    config2 = BlogConfig.objects.create(
        namespace="textonly",
        app_title="Test Blog (text only)",
        object_name="News",
        use_placeholder=False,
    )
    post1, post_en1, post_fr1 = generate_blog(config1)
    post2, post_en2, post_fr2 = generate_blog(config2)


if __name__ == "__main__":
    # Test runner for the migration tests
    import os
    import sys
    import traceback
    import types
    import django

    # Add repo root to the path
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.insert(0, BASE_DIR)
    failed = False
    db_path = os.path.join(BASE_DIR, "test_db.sqlite3")

    if len(sys.argv) != 3 or sys.argv[1] != "test_migration" or sys.argv[2] not in ("--phase1", "--phase2"):
        print(f"This script is meant to be run with '{sys.argv[0]} test_migration --phase<1/2>'")
        sys.exit(1)
    if sys.argv[2] == "--phase1":
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migration.pre"
        django.setup()
        if os.path.exists(db_path):
            os.remove(db_path)

        setup_blog_testproj()
        print(80 * "*")
    else:
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migration.post"
        django.setup()

        assert django.apps.apps.is_installed("djangocms_stories"), "djangocms_stories is not installed"
        assert django.apps.apps.is_installed("djangocms_blog"), "djangocms_blog is not installed"
        execute_from_command_line(["manage.py", "migrate", "--noinput"])

        current_module = sys.modules[__name__]
        for name in dir(current_module):
            obj = getattr(current_module, name)
            if isinstance(obj, types.FunctionType) and name.startswith("test_"):
                try:
                    obj()
                    print("OK:", name)
                except AssertionError:
                    failed = True
                    print("FAIL:", name)
                    traceback.print_exc()
                except Exception as e:
                    failed = True
                    print("ERROR:", name, e)
                    traceback.print_exc()
        print("Done")
        db_path = os.path.join(BASE_DIR, "test_db.sqlite3")

    if os.path.exists(db_path):
        os.remove(db_path)

    if failed:
        sys.exit(1)
