from django.utils.timezone import now
from djangocms_versioning.constants import OPERATION_PUBLISH, OPERATION_UNPUBLISH, PUBLISHED
from djangocms_versioning.models import Version
from .models import PostContent
from django.contrib.contenttypes.models import ContentType


def set_published_dates(sender, obj, operation, **kwargs):
    """
    When a post is published for the first time, or unplished record the date. 
    And when republished clear the date_published_end.
    """
    if not isinstance(obj, Version) or not isinstance(obj.content, PostContent):
        return

    post = obj.content.post

    if operation == OPERATION_PUBLISH:
        if not post.date_published:
            post.date_published = now()
        if post.date_published_end and post.date_published_end < now():
            post.date_published_end = None
        post.save(update_fields=["date_published", "date_published_end"])

    elif operation == OPERATION_UNPUBLISH:
        content_type = ContentType.objects.get_for_model(PostContent)
        no_published_languages = (
            Version.objects.filter(
                content_type=content_type,
                object_id__in=post.postcontent_set.values_list("id", flat=True),
                state=PUBLISHED,
            )
            .exclude(pk=obj.pk) .exists()
        )

        if not no_published_languages:
            if not post.date_published_end or post.date_published_end < now():
                post.date_published_end = now()
                post.save(update_fields=["date_published_end"])