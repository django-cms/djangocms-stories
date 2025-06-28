from django.core.management import execute_from_command_line
from django.utils.translation import activate, override


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


def test_post_category_hierachy():
    from djangocms_stories.models import PostCategory

    cat1, cat2, cat3 = PostCategory.objects.all()[:3]

    assert cat1.parent_id == cat3.pk
    assert cat2.parent_id == cat1.pk
    assert cat3.parent is None


def test_post_category_assignment():
    from djangocms_stories.models import Post, PostCategory

    story1, story2 = Post.objects.all()[:2]
    cat1, cat2, cat3 = PostCategory.objects.all()[:3]

    assert set(story1.categories.all()) == {cat2, cat3}
    assert set(story2.categories.all()) == {cat1}


def test_tag_assignment():
    from djangocms_stories.models import Post

    story1, story2 = Post.objects.all()[:2]
    assert set(story1.tags.names()) == {"tag1"}
    assert set(story2.tags.names()) == {"tag1", "tag2"}


def test_post_content_placeholder_moved():
    from djangocms_stories.models import Post

    story1, story2 = Post.objects.all()[:2]

    content1, content2 = (
        story1.get_content("en", show_draft_content=True),
        story1.get_content("fr", show_draft_content=True),
    )
    empty1, empty2 = (
        story2.get_content("en", show_draft_content=True),
        story2.get_content("fr", show_draft_content=True),
    )

    assert content1 and content2, "Both content objects should exist"

    assert content1.placeholders.count() == 1, "Content in English should have one placeholder"
    assert content2.placeholders.count() == 1, "Content in French should have one placeholder"

    assert empty1.placeholders.count() == 0, "Content in English should have no placeholders"
    assert empty2.placeholders.count() == 0, "Content in French should have no placeholders"


def setup_blog_testproj():
    from cms import api
    from django.apps import apps
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    from fixtures import (
        generate_config,
        generate_blog,
        generate_category,
        generate_placeholder_content,
        POST_CONTENT_DATA,
    )

    assert apps.is_installed("djangocms_blog"), "djangocms_blog is not installed"

    # Migrate djangocms_blog to the specific migration
    execute_from_command_line(["manage.py", "migrate", "cms", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "menus", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "sessions", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "contenttypes", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "sites", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "admin", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "auth", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "taggit", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "easy_thumbnails", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "filer", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_blog", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_text", "--noinput"])
    execute_from_command_line(["manage.py", "migrate", "djangocms_video", "--noinput"])
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

    cat1 = generate_category(config2, name="Category 1", slug="category-1")
    cat2 = generate_category(config2, name="Category 2", slug="category-2")
    with override("fr"):
        cat3 = generate_category(config2, name="Catégorie 3", slug="categorie-3")

    cat1.parent = cat3
    cat2.parent = cat1
    cat1.save()
    cat2.save()

    post1.categories.add(cat2)
    post1.categories.add(cat3)
    post2.categories.add(cat1)

    post1.tags.add("tag1")
    post2.tags.add("tag1", "tag2")

    generate_placeholder_content(post_en1, "en", body="<p>This is the content of the first post in English.</p>")
    generate_placeholder_content(post_fr1, "fr", body="<p>Ceci est le contenu du premier article en français.</p>")

    page = api.create_page(
        title="Test Page",
        template="base.html",
        language="en",
        slug="test-page",
        created_by=user,
    )
    page.application_urls = "BlogApp"
    page.application_namespace = config1.namespace
    page.save()

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
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migrations.settings_pre"
        django.setup()
        if os.path.exists(db_path):
            os.remove(db_path)
        activate("en")

        setup_blog_testproj()
    else:
        if not os.path.exists(db_path):
            print(f"Database file {db_path} does not exist. Aborting.")
            sys.exit(1)

        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_migrations.settings_post"
        django.setup()
        print("Running migrations...")
        assert django.apps.apps.is_installed("djangocms_stories"), "djangocms_stories is not installed"
        assert django.apps.apps.is_installed("djangocms_blog"), "djangocms_blog is not installed"
        execute_from_command_line(["manage.py", "migrate", "--noinput"])
        print("\n")
        print("Running tests...")
        print(80 * "=")
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
