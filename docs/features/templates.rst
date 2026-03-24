.. _templates:

#########
Templates
#########

To ease the template customisations a ``djangocms_stories/base.html`` template is
used by all the stories templates; the template itself extends a ``base.html``
template; content is pulled in the ``content`` block.
If you need to define a different base template, or if your base template does
not define a ``content`` block, copy in your template directory
``djangocms_stories/base.html`` and customise it according to your needs; the
other application templates will use the newly created base template and
will ignore the bundled one.

.. _templates_set:

*************
Templates set
*************

You can provide a different set of templates for the whole ``djangocms-stories`` application by configuring
the ``StoriesConfig`` accordingly.

This would require you to customize **all** the templates shipped in ``djangocms_stories/templates/djangocms_stories``; the easiest
way would be to copy the **content** of ``djangocms_stories/templates/djangocms_stories`` into another folder in the ``templates``
folder in your project
(e.g., something like ``cp -a djangocms_stories/templates/djangocms_stories/* /path/my/project/templates/my_stories``).

To use the new templates set, go to the ``StoriesConfig`` admin
(something like ``http://localhost:8000/en/admin/djangocms_stories/storiesconfig/1/change``) and enter a directory name in the
**Template prefix** field in the **Apphook configuration** admin (in the *Layout* section): it will be the
root of your custom templates set; following the example above, you should enter ``my_stories`` as directory name.

For more instruction regarding template override, please read Django documentation: `Overriding templates`_ (for your version of Django).

.. _plugin_templates:

****************
Plugin Templates
****************

You can have different layouts for each plugin (i.e.: ``Latest Blog Articles``, ``Author Blog Articles List`` etc), by
having multiple templates for each plugin.
Default plugin templates are located in the ``plugins`` folder of the folder specified by the **Template prefix**;
by default they are located in ``templates/djangocms_stories``.

By defining the setting ``STORIES_PLUGIN_TEMPLATE_FOLDERS`` you can allow multiple sets of
plugin templates allowing for different views per plugin instance. You could, for example,
have a plugin displaying latest posts as a list, a table or in masonry style.

New templates have the same names as the standard templates in the ``plugins`` folder
(e.g: ``latest_entries.html``, ``authors.html``, ``tags.html``, ``categories.html``, ``archive.html``).

When using this feature you **must** provide **all** the templates for the available plugins.

To use this feature define ``STORIES_PLUGIN_TEMPLATE_FOLDERS`` as a list of available templates.
Each item of this list itself is a tuple of the form ``('[folder_name]', '[verbose name]')``.

Example:

.. code-block:: python

    STORIES_PLUGIN_TEMPLATE_FOLDERS = (
        ('plugins', _('Default template')),    # reads from templates/djangocms_stories/plugins/
        ('timeline', _('Vertical timeline')),  # reads from templates/djangocms_stories/timeline/
        ('masonry', _('Masonry style')),       # reads from templates/djangocms_stories/masonry/
    )

Once defined, the plugin admin interface will allow content managers to select which template the plugin will use.


.. _overriding templates: https://docs.djangoproject.com/en/dev/howto/overriding-templates/#overriding-templates
