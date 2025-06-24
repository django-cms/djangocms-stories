=================
djangocms-stories
=================

| |PyPiVersion| |TestCoverage| |License|
| |PyVersion| |DjVersion| |CmsVersion|

**django CMS stories application - Tell your story in multilingual posts, using the full
power of django CMS placeholders.**

djangocms-stories provides a lean foundation for storytelling that can be composed with
other specialized django CMS applications, such as djangocms-versioning or djangocms-moderation.

********
Features
********

* Frontend editing using django CMS frontend editor
* Placeholder or optionally simpler TextField-based content editing
* Multilingual support using django-parler
* Multisite (posts can be visible in one or more Django sites on the same project)
* Hooks into your page tree anywhere
* Configurable permalinks, user navigation, template sets, ...
* Multiple instaces per site (e.g., blog, news, stories)
* Django sitemap framework
* django CMS Wizard integration
* Supports djangocms-versioning and djangocms-moderation

************
Installation
************

To install the latest version directly from GitHub, run:

.. code-block:: bash

    pip install git+https://github.com/fsbraun/djangocms-stories.git

Add ``djangocms_stories`` to your ``INSTALLED_APPS`` in your Django project's ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'djangocms_stories',
        'parler',  # if not already included
        'sortedm2m',  # if not already included

        # For now, but probably not needed in the future
        'taggit',
        'taggit_autosuggest',
        'meta',
        # ...
    ]

To use taggit's autosuggest feature, add their URLS in ``urls.py``:

.. code-block:: python

    url_patterns += [path('taggit_autosuggest/', include('taggit_autosuggest.urls'))]



*****************************
Migrating from djangocms-blog
*****************************

Migrate from djangocms-blog by following the steps below (at your own risk - the migration is
under development). Be sure to backup your database before.

1. Uninstall djangocsms-blog: ``pip uninstall djangocms-blog``
2. Install djangocms-stories ``pip install git+https://github.com/fsbraun/djangocms-stories.git``
3. Add ``"djangocms_stories"`` to your installed apps. Do **not** remove djangocms-blog.
4. Run ``./manage.py migrate djangocms_stories``. This in migration 0002 will move existing content
   from djangocms-blog to djangocms-stories and delete djangocms-blogs database tables.
5. Remove ``"djangocms_blog"`` from your installed apps.

**Custom templates will need manual updating**, since the underlying model structure has changed:

* ``post`` contains the following fields: ``related``, ``main_image``, ``author``, ``date``, ``categories``, ``tags``
* ``post_content`` contiains the following per-language fields:
  ``title``, ``subtitle``, ``slug``, ``content``, ``media``, and ``post``, the reference
  to the ``Post`` object.


************
Contributing
************

Because this is a an open-source project, we welcome everyone to
`get involved in the project <https://www.django-cms.org/en/contribute/>`_ and
`receive a reward <https://www.django-cms.org/en/bounty-program/>`_ for their contribution.
Become part of a fantastic community and help us make django CMS the best CMS in the world.

We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

The project makes use of git pre-commit hooks to maintain code quality.
Please follow the installation steps to get `pre-commit <https://pre-commit.com/#installation>`_
setup in your development environment.

We're grateful to all contributors who have helped create and maintain
this package. Contributors are listed at the `contributors
<https://github.com/fsbraun/djangocms-stories/graphs/contributors>`_
section.

One of the easiest contributions you can make is helping to translate this addon on
`Transifex <https://www.transifex.com/divio/djangocms-stories/dashboard/>`_.

*******
Credits
*******

djangocms-stories is inspired by `Nephila's <https://github.com/nephila>`_ excellent
`djangocms-blog <https://github.com/nephila/djangocms-blog>`_, with the intent to bring
to align it with django CMS's new philosophy since version 4: "The design philosophy of
django CMS is to solve something complex with many simple things."

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/djangocms-stories.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-stories
    :alt: Latest PyPI version

.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/djangocms-stories.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-stories
    :alt: Python versions

.. |DjVersion| image:: https://img.shields.io/pypi/frameworkversions/django/djangocms-stories.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-stories
    :alt: Django versions

.. |CmsVersion| image:: https://img.shields.io/pypi/frameworkversions/django-cms/djangocms-stories.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-stories
    :alt: django CMS versions

.. |TestCoverage| image:: https://codecov.io/gh/fsbraun/djangocms-stories/graph/badge.svg?token=O64yNt6pgo
    :target: https://codecov.io/gh/fsbraun/djangocms-stories
    :alt: Test coverage

.. |License| image:: https://img.shields.io/github/license/fsbraun/djangocms-stories.svg?style=flat-square
   :target: https://pypi.python.org/pypi/djangocms-stories/
    :alt: License
