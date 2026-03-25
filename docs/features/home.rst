.. _blog-home-page:

==================================
Attaching stories to the home page
==================================

************************************
Add stories apphook to the home page
************************************

* Go to the django CMS page admin
* Edit the home page
* Go to **Page settings** and select **Stories** from the **Application** selector and create an **Application configuration**
* Customise the Application instance name if desired
* Publish the page

*******************
Amend configuration
*******************

Permalinks must be updated to avoid the stories urlconf swallowing django CMS page patterns.

To avoid this add the following settings to your project:

.. code-block:: python

    STORIES_AVAILABLE_PERMALINK_STYLES = (
        ('full_date', _('Full date')),
        ('short_date', _('Year /  Month')),
        ('category', _('Category')),
    )
    STORIES_PERMALINK_URLS = {
        "full_date": "<int:year>/<int:month>/<int:day>/<str:slug>/",
        "short_date": "<int:year>/<int:month>/<str:slug>/",
        "category": "<str:category>/<str:slug>/",
    }

Notice that the ``slug`` permalink type is no longer present.

Then, pick any of the three remaining permalink types in the layout section of the apphook config
linked to the home page (at ``http://yoursite.com/admin/djangocms_stories/storiesconfig/``).
