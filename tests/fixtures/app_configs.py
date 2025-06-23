import pytest

from djangocms_stories.cms_appconfig import StoriesConfig


PERMALINK_TYPE_FULL_DATE = "full_date"
PERMALINK_TYPE_SHORT_DATE = "short_date"
PERMALINK_TYPE_CATEGORY = "category"
PERMALINK_TYPE_SLUG = "slug"


@pytest.fixture
@pytest.mark.django_db
def simple_w_placeholder(db):
    return StoriesConfig.objects.using(db).create(
        namespace="test_ns",
        url_patterns=PERMALINK_TYPE_FULL_DATE,
        use_placeholder=True,
    )


@pytest.fixture
@pytest.mark.django_db
def simple_wo_placeholder(db):
    return StoriesConfig.objects.using(db).create(
        namespace="test_ns_wo_placeholder",
        url_patterns=PERMALINK_TYPE_FULL_DATE,
        use_placeholder=False,
    )


default_config = simple_w_placeholder
