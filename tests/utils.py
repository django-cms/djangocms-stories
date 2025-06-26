from contextlib import contextmanager

from django.apps import apps
from django.db import connection
from django.test.utils import CaptureQueriesContext


@contextmanager
def assert_num_queries(expected_num):
    with CaptureQueriesContext(connection) as ctx:
        yield
        actual_num = len(ctx)
        assert actual_num == expected_num, f"Expected {expected_num} queries, but got {actual_num}"


def publish_if_necessary(post_contents, user):
    if apps.is_installed("djangocms_versioning"):
        from djangocms_versioning.models import Version

        for post_content in post_contents:
            Version.objects.get_for_content(post_content).publish(user)
