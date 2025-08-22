#######
Signals
#######

Django signals for extending stories functionality.

.. currentmodule:: djangocms_stories.signals

Post Signals
============

.. autodata:: post_published

.. autodata:: post_unpublished

.. autodata:: post_created

.. autodata:: post_updated

.. autodata:: post_deleted

Category Signals
================

.. autodata:: category_created

.. autodata:: category_updated

.. autodata:: category_deleted

Comment Signals
===============

.. autodata:: comment_posted

.. autodata:: comment_approved

.. autodata:: comment_deleted

Signal Handlers
===============

Example signal handlers::

    from django.dispatch import receiver
    from djangocms_stories.signals import post_published

    @receiver(post_published)
    def notify_on_publish(sender, instance, **kwargs):
        # Send notification email
        # Update search index
        # Clear caches
        pass

    @receiver(post_created)
    def setup_new_post(sender, instance, **kwargs):
        # Set default categories
        # Initialize SEO fields
        # Create audit log entry
        pass

Usage Examples
==============

Cache invalidation::

    from django.core.cache import cache
    from django.dispatch import receiver
    from djangocms_stories.signals import post_published, post_unpublished

    @receiver([post_published, post_unpublished])
    def invalidate_story_cache(sender, instance, **kwargs):
        cache_keys = [
            f'story_list_{instance.app_config.namespace}',
            f'story_detail_{instance.pk}',
            f'category_posts_{instance.categories.first().pk}' if instance.categories.exists() else None,
        ]
        cache.delete_many([key for key in cache_keys if key])

Search index updates::

    from django.dispatch import receiver
    from djangocms_stories.signals import post_published, post_unpublished

    @receiver(post_published)
    def add_to_search_index(sender, instance, **kwargs):
        # Add to search index
        if hasattr(instance, 'search_index'):
            instance.search_index.update()

    @receiver(post_unpublished)
    def remove_from_search_index(sender, instance, **kwargs):
        # Remove from search index
        if hasattr(instance, 'search_index'):
            instance.search_index.delete()

Social media integration::

    from django.dispatch import receiver
    from djangocms_stories.signals import post_published

    @receiver(post_published)
    def share_on_social_media(sender, instance, **kwargs):
        # Post to Twitter, Facebook, etc.
        from .tasks import post_to_social_media
        post_to_social_media.delay(instance.pk)

Analytics tracking::

    from django.dispatch import receiver
    from djangocms_stories.signals import post_created, post_published

    @receiver(post_created)
    def track_post_creation(sender, instance, **kwargs):
        # Track in analytics
        import analytics
        analytics.track(instance.author.pk, 'Story Created', {
            'story_id': instance.pk,
            'title': instance.title,
            'category': instance.categories.first().name if instance.categories.exists() else None
        })

    @receiver(post_published)
    def track_post_publication(sender, instance, **kwargs):
        # Track publication event
        import analytics
        analytics.track(instance.author.pk, 'Story Published', {
            'story_id': instance.pk,
            'title': instance.title,
        })
