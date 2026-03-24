.. _extensions:

###############
Post Extensions
###############

Posts can be extended to attach arbitrary fields to a post instance.

E.g. one wants to have in a template a field or placeholder related to a post.

.. code-block:: python

    {{ post.extension.some_field }}
    {% render_placeholder post.placeholder_extension.some_placeholder %}


Define the models in your models.py

.. code-block:: python

    from cms.models import CMSPlugin, PlaceholderField

    from djangocms_stories.models import Post

    class PostExtension(models.Model):
        post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='extension')
        some_field = models.CharField(max_length=10)

    class PostPlaceholderExtension(models.Model):
        post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='placeholder_extension')
        some_placeholder = PlaceholderField('some_placeholder')


Define an inline in your admin.py

.. code-block:: python

    from .models import PostExtension

    class PostExtensionInline(admin.TabularInline):
        model = PostExtension
        fields = ['some_field']
        classes = ['collapse']
        extra = 1
        can_delete = False
        verbose_name = "PostExtension"
        verbose_name_plural = "PostExtensions"


Register the extension in djangocms_stories

.. code-block:: python

    import djangocms_stories.admin as stories_admin
    stories_admin.register_extension(PostExtensionInline)
    stories_admin.register_extension(PostPlaceholderExtension)


After this the inline will be available in the Post add and Post change admin forms and a PostPlaceholderExtension
instance will be automatically created when a post object is created.
