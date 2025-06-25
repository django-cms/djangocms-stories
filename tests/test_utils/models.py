from django.apps import apps
from django.db import models

if apps.is_installed("djangocms_stories"):
    # Do not declare models if the migratin test is running

    class MyPostExtension(models.Model):
        """
        A model that extends the Post model with additional fields.
        This is a placeholder for any custom fields you might want to add.
        """

        post = models.OneToOneField(
            "djangocms_stories.Post",
            on_delete=models.CASCADE,
            related_name="my_extension",
        )
        custom_field = models.CharField(max_length=255, default="test")

        def __str__(self):
            return f"MyPostExtension for {self.post.title}" if self.post else "MyPostExtension without Post"

    class MyPostContentExtension(models.Model):
        """
        A model that extends the PostContent model with additional fields.
        This is a placeholder for any custom fields you might want to add.
        """

        post_content = models.OneToOneField(
            "djangocms_stories.PostContent",
            on_delete=models.CASCADE,
            related_name="my_content_extension",
        )
        custom_field = models.CharField(max_length=255, default="test")

        def __str__(self):
            return (
                f"MyPostContentExtension for {self.post_content.title}"
                if self.post_content
                else "MyPostContentExtension without PostContent"
            )
