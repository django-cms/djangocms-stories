.. _installation:

############
Installation
############

djangocms-stories assumes a **completely set up and working django CMS 4+ project**.
See the `django CMS installation docs <https://docs.django-cms.org/en/latest/>`_ for reference.

If you are not familiar with django CMS you are **strongly encouraged** to read the django CMS documentation before
installing djangocms-stories, as setting it up and adding content requires django CMS features which are not described
in this documentation.


*********************
Installation steps
*********************

.. note:: If you are migrating from djangocms-blog, see the :ref:`migration guide <migration_from_blog>` instead.

* Install djangocms-stories:

  .. code-block:: bash

      pip install djangocms-stories djangocms-text

* Add ``djangocms_stories`` and its dependencies to INSTALLED_APPS:

  .. code-block:: python

        INSTALLED_APPS = [
            ...
            'filer',
            'easy_thumbnails',
            'parler',
            'taggit',
            'taggit_autosuggest',
            'meta',
            'sortedm2m',
            'djangocms_text',
            'djangocms_stories',
            ...
        ]


.. note:: The following are minimal defaults to get the stories running; they may not be
          suited for your deployment.

* Add the following settings to your project:

  .. code-block:: python

        THUMBNAIL_PROCESSORS = (
            'easy_thumbnails.processors.colorspace',
            'easy_thumbnails.processors.autocrop',
            'filer.thumbnail_processors.scale_and_crop_with_subject_location',
            'easy_thumbnails.processors.filters',
        )
        META_SITE_PROTOCOL = 'https'  # set 'http' for non ssl enabled websites
        META_USE_SITES = True

* For meta tags support enable the needed types:

  .. code-block:: python

        META_USE_OG_PROPERTIES = True
        META_USE_TWITTER_PROPERTIES = True
        META_USE_SCHEMAORG_PROPERTIES = True

* Configure parler according to your languages:

  .. code-block:: python

        PARLER_LANGUAGES = {
            1: (
                {'code': 'en',},
                {'code': 'it',},
                {'code': 'fr',},
            ),
            'default': {
                'fallbacks': ['en', 'it', 'fr'],
            }
        }

  .. note:: Since parler 1.6 this can be skipped if the language configuration is the same as ``CMS_LANGUAGES``.

* Add the following to your ``urls.py``:

  .. code-block:: python

        urlpatterns += [path('taggit_autosuggest/', include('taggit_autosuggest.urls'))]

* Apply the migrations:

  .. code-block:: bash

        python manage.py migrate

* Add the stories application (see :ref:`attach` below).

.. _modify_templates:

***********************
Modify templates
***********************

For standard djangocms-stories templates to work you must ensure a ``content`` block is available in the django CMS
template used by the page djangocms-stories is attached to.

For example, in case the page uses the ``base.html`` template, you must ensure that something like the following is
in the template:

.. code-block:: html+django
    :name: base.html

    ...
    {% block content %}
        {% placeholder "page_content" %}
    {% endblock content %}
    ...

Alternatively you can override ``djangocms_stories/base.html`` and extend a different block:

.. code-block:: html+django
    :name: djangocms_stories/base.html

    ...
    {% block my_block %}
    <div class="app app-stories">
        {% block content_stories %}{% endblock %}
    </div>
    {% endblock my_block %}
    ...


.. _attach:

*****************************
Attach the stories to a page
*****************************

* Use `AppHooks from django CMS <https://docs.django-cms.org/en/latest/how_to/apphooks.html>`_
  to add the stories to a django CMS page:

  * Create a new django CMS page
  * Go to **Page settings** and select **Stories** from the **Application** selector and
    create an **Application configuration**
  * Customise the Application instance name if desired
  * Publish the page

  Check the :ref:`blog-home-page` section to attach the stories to the website home page.

.. warning:: After adding the apphook to the page you **cannot** change the **Instance Namespace**
             field for the defined configuration; if you want to change it, create a new one
             with the correct namespace, go in the CMS page settings and switch to the
             new **Application configuration**.

* Add and edit stories by creating them in the admin or using the toolbar,
  and use the django CMS frontend editor to edit the story content:

  * Create a new story in django admin backend or from the toolbar
  * Click on "view on site" button to view the story detail page
  * Edit the story via the django CMS frontend by adding / editing plugins
  * If djangocms-versioning is installed, publish the story by creating a new published version

.. note:: By default djangocms-stories uses django CMS plugins for content, this means you will **not** have a text
          field in the story admin, but you will have to visit the frontend story page (hit "View on site" button)
          and add django CMS plugins on the frontend.

.. _external_applications:

***********************************
Further configuration
***********************************

As django CMS relies on external applications to provide its features, you may also want to check
the documentation of external packages.

Please refer to each application's documentation for details.

* django-cms (framework and content plugins): https://docs.django-cms.org/en/latest/
* django-filer (image handling): https://django-filer.readthedocs.io
* django-meta (meta tag handling): https://github.com/nephila/django-meta#installation
* django-parler (multi language support): https://django-parler.readthedocs.io/en/latest/quickstart.html#configuration
