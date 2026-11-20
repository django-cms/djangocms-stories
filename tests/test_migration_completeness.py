import pytest
from django.apps import apps
from django.core.management import call_command
from io import StringIO


@pytest.mark.django_db
def test_no_missing_migrations(settings):
    """Test that there are no missing migrations by running makemigrations --check."""
    # The test suite runs with --nomigrations, which makes makemigrations refuse to run
    settings.MIGRATION_MODULES = {}
    out = StringIO()
    try:
        call_command("makemigrations", "djangocms_stories", "--check", "--dry-run", stdout=out, stderr=out)
        result_returncode = 0
    except SystemExit as e:
        result_returncode = e.code
    result_output = out.getvalue()
    assert result_returncode == 0, "There are missing migrations:\n" + result_output


@pytest.mark.parametrize("model_name", ["PostCategoryTranslation", "StoriesConfigTranslation"])
def test_translation_constraint_names_fit_database_limits(model_name):
    model = apps.get_model("djangocms_stories", model_name)
    assert model._meta.constraints
    assert all(len(constraint.name) <= 30 for constraint in model._meta.constraints)
