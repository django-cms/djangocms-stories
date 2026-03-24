.. _home-page:

==============================================
How to attach stories apphook to the home page
==============================================

Attaching the stories apphook to the home page turns your site's root URL into a blog or
news feed — visitors land directly on the latest posts instead of a static page. This works
well for content-driven sites, but requires one small configuration tweak to avoid URL
conflicts.

Why a tweak is needed
=====================

When an apphook is attached to a page, django CMS routes all URLs beneath that page through
the apphook's urlconf. For most pages this is fine, but the home page is the parent of
*every* other page in the tree. If the stories urlconf includes a catch-all slug pattern
(``<str:slug>/``), it will swallow URLs meant for child pages like ``/about/`` or ``/contact/``.

The fix is straightforward: remove the slug-only permalink style so that post URLs always
contain a date or category prefix, leaving bare slugs free for CMS pages.

Step 1: Restrict permalink styles
==================================

Add the following to your project settings to remove the slug-only option:

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

With these settings, post URLs will always start with a date or category segment, and CMS
pages beneath the home page will resolve normally.

Then open the ``StoriesConfig`` admin and pick one of the three remaining permalink styles in
the **Layout** section.

Step 2: Attach the apphook
============================

Open the home page in the django CMS admin, go to **Page settings**, select **Stories** from
the **Application** dropdown, and choose your configuration. Publish the page — your home page
is now a stories listing.
