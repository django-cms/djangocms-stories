.. _home-page:

==============================================
How to attach stories apphook to the home page
==============================================

By attaching an apphook to a page, by default all child pages are swallowed by the apphook. This is normally not a problem.
If you want to attach the stories apphook to the home page, however, you need to ensure not all CMS pages are shadowed as
child pages of the home page.

This can be achieved by disallowing the slug-based permalink style for the stories apphook.

*********************************************
Remove slug permalink type from configuration
*********************************************

Permalinks must be updated to avoid stories urlconf swallowing django CMS page patterns.

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

Notice that the **slug permalink type** is no longer present, since it shadows other CMS page patterns.

Then, pick any of the three remaining permalink types in the layout section of the apphooks config
linked to the home page (at http://yoursite.com/admin/djangocms_stories/storiesconfig/).

*********************************
Add/upadete stories apphook to the home page
*********************************

* Go to the django CMS page admin: http://localhost:8000/admin/cms/page
* Edit the home page
* Go to **Advanced settings** and select Stories from the **Application** selector and create an **Application configuration**;
* Customise the Application instance name, if needed
* Publish the page
* Restart the project instance to properly load stories urls.

