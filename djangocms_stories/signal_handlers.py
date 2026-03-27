from django.utils.timezone import now
from djangocms_versioning.constants import OPERATION_PUBLISH, OPERATION_UNPUBLISH
from .models import PostContent


def handle_version_operation(sender, obj, operation, **kwargs):
    """
    When a post is published for the first time, record the date. When it's unpublished, record that date too.
    """
    if not hasattr(obj, 'content') or not isinstance(obj.content, PostContent):
        return  

    post = obj.content.post

    if operation == OPERATION_PUBLISH and not post.date_published:
        post.date_published = now()
        post.save(update_fields=["date_published"])

    elif operation == OPERATION_UNPUBLISH:
        post.date_published_end = now()
        post.save(update_fields=["date_published_end"])