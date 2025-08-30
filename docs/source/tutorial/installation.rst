############
Installation
############

.. note::

    If you are migrating from `djangocms-blog <https://github.com/nephila/djangocms-blog>`_
    please see the :ref:`migration_from_blog` guide.

Installing djangocms-stories
=============================

Install using pip::

    pip install djangocms-stories

Add to your Django settings
============================

Add ``djangocms_stories`` and some dependent apps to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        # ... other apps
        'djangocms_stories',
        'parler',
        'taggit',
        'taggit_autosuggest',
        'sortedm2m',
        'meta',
        'filer',
        'easy_thumbnails',
    ]

This contains some dependencies, some of which might not be necessary in the future:

* ``django_parler`` manages translations
* ``django_taggit`` and ``django_taggit_autosuggest`` manage tagging
* ``django_sortedm2m`` provides a sorted many-to-many field for ordering related posts by their significance
* ``django_meta`` adds metadata support for your stories
* ``django_filer`` and ``easy_thumbnails`` handle file uploads and image thumbnails


URL Configuration
=================

In the typical use case, no URL configuration is necessary. One or even multiple instances of the application can be attached
to the Django CMS page tree using Stories Configurations from within the Django admin.

Only if you do **not** want to manage the blog URLs using the Django CMS page tree, add the stories URLs to your main ``urls.py``::

    from django.urls import path, include

    urlpatterns = [
        # ... other URLs
        path('stories/', include('djangocms_stories.urls')),
    ]

Run migrations
==============

Run the database migrations::

    python manage.py migrate djangocms_stories


.. _create_a_stories_config:

Create a Stories Config
=======================

In the Django admin, create a new Stories Config to configure your story application. In the simplest case you enter
a namespace, e.g. ``blog`` and the name of a document, e.g. ``Article``. The namespace cannot be changed later.

That's it! You're ready to start creating stories.
