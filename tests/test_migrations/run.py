from django.core.management import execute_from_command_line
from django.utils.translation import activate


def test_apphook_migration():
    from cms.models import Page

    assert not Page.objects.filter(application_urls="BlogConfig").exists(), (
        "BlogConfig apphook should not exist in the database"
    )
    assert Page.objects.filter(application_urls="StoriesConfig").exists(), (
        "StoriesConfig apphook should exist in the database"
    )

    page = Page.objects.get(application_urls="StoriesConfig", application_namespace="blog1")
    assert page.get_admin_content("en").title == "Test Page", "The page title should be 'Test Page'"


def test_post_content_migration():
    from djangocms_stories.models import Post
    from fixtures import POST_CONTENT_DATA

    story1, story2 = Post.objects.all()[:2]

    assert story1.postcontent_set.count() == 1, "The first story should have one published post contents"
    assert story1.postcontent_set(manager="admin_manager").count() == 2, (
        "The first story should have two post contents"
    )

    content1en = POST_CONTENT_DATA["post_en1"]
    assert story1.get_title("en") == content1en["meta_title"], (
        f"The first story title should be '{content1en['meta_title']}', not '{story1.get_title('en')}'"
    )
    assert story1.get_description("en") == content1en["meta_description"], (
        f"The first story description should be '{content1en['meta_description']}', not '{story1.get_descrition('en')}'"
    )

    assert story1.get_content("fr", show_draft_content=True).language == "fr"

    assert story1.get_title("fr") == content1en["meta_title"], (
        f"The first story title should be '{content1en['meta_title']}', not '{story1.get_title('fr')}'"
    )
    assert story1.get_description("fr") == content1en["meta_description"], (
        f"The first story description should be '{content1en['meta_description']}', not '{story1.get_descrition('fr')}'"
    )

    assert story2.postcontent_set.count() == 0, "The second story should have onnoe published post contents"
    assert story2.postcontent_set(manager="admin_manager").count() == 2, (
        "The second story should have two post contents"
    )


def setup_blog_testproj():
    from cms import api
    from django.apps import apps
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    from fixtures import generate_config, generate_blog, POST_CONTENT_DATA

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

    config1 = generate_config(namespace="blog1", use_placeholder=True)
    config2 = generate_config(namespace="blog2", use_placeholder=False)

    post1, post_en1, post_fr1 = generate_blog(config1, user, author=user)
    post_en1.__dict__.update(POST_CONTENT_DATA["post_en1"])
    post_fr1.__dict__.update(POST_CONTENT_DATA["post_fr1"])
    post_en1.save()
    post_fr1.save()
    post2, post_en2, post_fr2 = generate_blog(config2, user, author=user)

    page = api.create_page(
        title="Test Page",
        template="base.html",
        language="en",
        slug="test-page",
        created_by=user,
    )
    from cms.models import PageContent

    assert PageContent.admin_manager.count() == 1, "There should be one page content created"
    page.application_urls = "BlogApp"
    page.application_namespace = config1.namespace
    page.save()

    execute_from_command_line(["manage.py", "create_versions", "--userid", str(user.id)])

    post_en1.versions.first().publish(user=user)

    return config1, config2, post1, post_en1, post_fr1, post2, post_en2, post_fr2


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

    if len(sys.argv) != 2 or sys.argv[1] not in ("--phase1", "--phase2"):
        print(f"This script is meant to be run with '{sys.argv[0]} --phase<1/2>'")
        sys.exit(1)
    if sys.argv[1] == "--phase1":
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migrations.pre"
        django.setup()
        if os.path.exists(db_path):
            os.remove(db_path)
        activate("en")

        setup_blog_testproj()
    else:
        if not os.path.exists(db_path):
            print(f"Database file {db_path} does not exist. Aborting.")
            sys.exit(1)

        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migrations.post"
        django.setup()
        print("Running migrations...")
        assert django.apps.apps.is_installed("djangocms_stories"), "djangocms_stories is not installed"
        assert django.apps.apps.is_installed("djangocms_blog"), "djangocms_blog is not installed"
        execute_from_command_line(["manage.py", "migrate", "--noinput"])
        print(80 * "=")
        print("Running tests...")
        activate("en")
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
