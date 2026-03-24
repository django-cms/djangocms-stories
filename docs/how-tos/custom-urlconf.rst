.. _custom-urlconf:

################################
How to customize the URL layout
################################

djangocms-stories ships with a default URL configuration that covers the most common patterns:
post lists, category pages, tag filters, author pages, archives, and feeds. In most cases
you won't need to change anything — the permalink style (full date, short date, category, or
slug) is configurable per ``StoriesConfig`` without touching URL files.

However, if you need to add extra views, change URL prefixes, or restructure the routing
entirely, you can replace the default urlconf with your own.

Providing a custom URLConf
===========================

Point the ``STORIES_URLCONF`` setting to your custom module:

.. code-block:: python

    STORIES_URLCONF = 'my_project.stories_urls'

Then create that module by copying the default ``djangocms_stories/urls.py`` as a starting point:

.. code-block:: bash

    cp $(python -c "import djangocms_stories; print(djangocms_stories.__path__[0])")/urls.py \
       my_project/stories_urls.py

Edit the copy to suit your needs — add views, rename patterns, or remove routes you don't use.
The file follows standard Django URL configuration, so any pattern that works in a normal
``urls.py`` will work here.

.. note::

    The custom urlconf applies to **all** ``StoriesConfig`` instances. If you need different URL
    layouts per configuration, you can branch inside your views or use multiple Django apps
    instead.
