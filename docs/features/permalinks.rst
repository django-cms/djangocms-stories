.. _permalinks:

#######################
Configurable permalinks
#######################

djangocms-stories comes with four different styles of permalinks:

* Full date: ``YYYY/MM/DD/SLUG``
* Year / Month: ``YYYY/MM/SLUG``
* Category: ``CATEGORY/SLUG``
* Just slug: ``SLUG``

As all the styles are loaded in the urlconf, the latter two do not allow
you to have CMS pages beneath the page the stories are attached to. If you want to
do this, you have to override the default urlconfs by setting something
like the following in the project settings:

.. code-block:: python

    STORIES_PERMALINK_URLS = {
        "full_date": "<int:year>/<int:month>/<int:day>/<str:slug>/",
        "short_date": "<int:year>/<int:month>/<str:slug>/",
        "category": "<str:category>/<str:slug>/",
        "slug": "<str:slug>/",
    }

And change the URL patterns as desired.
