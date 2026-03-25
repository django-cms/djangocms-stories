.. _blog-custom-urlconf:

################
Customizing URLs
################

************************
Provide a custom URLConf
************************

It's possible to completely customize the urlconf by setting ``STORIES_URLCONF`` to the dotted path of
the new urlconf.

Example:

.. code-block:: python

    STORIES_URLCONF = 'my_project.stories_urls'

The custom urlconf can be created by copying the existing urlconf in ``djangocms_stories/urls.py``,
saving it to a new file ``my_project/stories_urls.py`` and editing it according to the custom needs.
