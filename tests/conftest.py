import pytest
import re

from .fixtures import (
    post,  # noqa: F401
    post_content,  # noqa: F401
    default_config,  # noqa: F401
    simple_w_placeholder,  # noqa: F401
    simple_wo_placeholder,  # noqa: F401
)


def normalize_html(html_string):
    """Normalize HTML by removing extra whitespace"""
    # Remove whitespace between tags
    html_string = re.sub(r">\s+<", "><", html_string.strip())
    # Normalize internal whitespace
    html_string = re.sub(r"\s+", " ", html_string)
    return html_string


@pytest.fixture
def assert_html_in_response():
    """
    Assert that an HTML fragment exists in the response, ignoring whitespace.
    Similar to Django's assertContains with html=True
    """

    def assert_html(fragment, response, status_code=200):
        assert response.status_code == status_code

        # Noremalize both the response content and the fragment
        response_content = normalize_html(response.content.decode("utf-8"))
        normalize_fragment = normalize_html(fragment)
        assert normalize_fragment in response_content, (
            f"Expected HTML fragment not found in response.\n"
            f"Fragment: {normalize_fragment}\n"
            f"Response: {response_content}"
        )

    return assert_html

@pytest.mark.django_db
def test_load_wizards():
    try:
        from cms.wizards.wizard_base import get_entries
    except (ImportError, ModuleNotFoundError):
        from cms.wizards.helpers import get_entries

    print("Registered wizards:", [wizard.title for wizard in get_entries()])

