import pytest
from django.core.management import call_command
from io import StringIO


@pytest.mark.django_db
def test_no_missing_migrations():
    """Test that there are no missing migrations by running makemigrations --check."""
    out = StringIO()
    try:
        call_command("makemigrations", "djangocms_stories", "--check", "--dry-run", stdout=out, stderr=out)
        result_returncode = 0
    except SystemExit as e:
        result_returncode = e.code
    result_output = out.getvalue()
    assert result_returncode == 0, "There are missing migrations:\n" + result_output
