.. _custom-urlconf:

################
How to further customize the URLs
################

************************
Provide a custom URLConf
************************

In cases the available URL configurations are not sufficient, you can create a custom URL configuration for djangocms-stories.
To this end, you set ``STORIES_URLCONF`` to the dotted path of your custom urlconf.

Example:

.. code-block:: python

    STORIES_URLCONF = 'my_project.stories_urls'

The custom urlconf can be created by copying the existing urlconf in ``djangocms_stories/urls.py``,
saving it to a new file ``my_project.stories_urls.py`` and editing it according to the custom needs.
