import pytest
from filer.models import ThumbnailOption


@pytest.fixture
def default_full(db):
    return ThumbnailOption.objects.using(db).create(
        name="Story thumbnail",
        width=120,
        height=120,
        crop=True,
        upscale=True,
    )


@pytest.fixture
def default_thumbnail(db):
    return ThumbnailOption.objects.using(db).create(
        name="Story image",
        width=800,
        height=200,
        crop=True,
        upscale=True,
    )
