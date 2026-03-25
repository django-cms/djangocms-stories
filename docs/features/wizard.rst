.. _cms-wizard:

##################
django CMS Wizard
##################

django CMS provides a content creation wizard that allows to quickly create supported
content types, such as stories / blog posts.

For each configured Apphook (``StoriesConfig``), a content type is added to the wizard.

Wizard can create story content by filling the ``Text`` form field. You can control the text plugin used for
content creation by editing two settings:

* ``STORIES_WIZARD_CONTENT_PLUGIN``: name of the plugin to use (default: ``TextPlugin``)
* ``STORIES_WIZARD_CONTENT_PLUGIN_BODY``: name of the plugin field to add text to (default: ``body``)

.. warning:: The plugin used must only have the text field required; all additional fields must be optional, otherwise
             the wizard will fail.
