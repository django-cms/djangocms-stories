
.. _cms-wizard:

##################
Wizard Integration
##################

django CMS provides a content creation wizard that allows to quickly created supported
content types, such as story posts.

For each configured Apphook, a content type is automatically added to the wizard.

Wizard can create blog post content by filling the ``Text`` form field. You can control the text plugin used for
content creation by editing two settings:

* ``STORIES_WIZARD_CONTENT_PLUGIN``: name of the plugin to use (default: ``TextPlugin``)
* ``STORIES_WIZARD_CONTENT_PLUGIN_BODY``: name of the plugin field to add text to (default: ``body``)

.. warning::

    The plugin used must only have the text field required, all additional fields must be optional, otherwise
    the wizard will fail.
