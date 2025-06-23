from contextlib import contextmanager

from django.db import connection
from django.test.utils import CaptureQueriesContext


@contextmanager
def assert_num_queries(expected_num):
    with CaptureQueriesContext(connection) as ctx:
        yield
        actual_num = len(ctx)
        assert actual_num == expected_num, f"Expected {expected_num} queries, but got {actual_num}"
