import pytest

from djangocms_stories.admin import register_extension, unregister_extension


def test_registering_extension_admins():
    from tests.test_utils.admin import PostExtensionInline

    register_extension(PostExtensionInline)
    with pytest.raises(Exception):
        # Attempt to register the same inline again should raise an error
        register_extension(PostExtensionInline)

    unregister_extension(PostExtensionInline)
    with pytest.raises(ValueError):
        # Attempt to unregister a non-registered inline should raise an error
        unregister_extension(PostExtensionInline)


@pytest.mark.django_db
def test_registering_extension_models():
    from tests.test_utils.models import MyPostExtension
    from .factories import PostFactory

    with pytest.warns(DeprecationWarning):
        register_extension(MyPostExtension)
    with pytest.raises(Exception), pytest.warns(DeprecationWarning):
        # Attempt to register the same inline again should raise an error
        register_extension(MyPostExtension)

    initial_ext = MyPostExtension.objects.count()
    post = PostFactory()
    assert MyPostExtension.objects.count() == initial_ext + 1
    assert post.my_extension.custom_field == "test"

    unregister_extension(MyPostExtension)
    with pytest.raises(Exception):
        unregister_extension(MyPostExtension)


def test_registering_other_obj_fails():
    class NotAModelOrAdmin:
        pass

    with pytest.raises(Exception):
        register_extension(NotAModelOrAdmin)

    with pytest.raises(Exception):
        unregister_extension(NotAModelOrAdmin)
