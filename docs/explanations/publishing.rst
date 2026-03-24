##########
Publishing
##########

djangocms-stories does not manage publication workflows itself. Instead, it delegates this
responsibility to external packages — most commonly
`djangocms-versioning <https://github.com/django-cms/djangocms-versioning>`_. This is the same
approach django CMS takes for pages: the page model defines the content, and versioning
provides the editorial workflow around it.

If you already know how versioning works for CMS pages, you know how it works for stories.
The same toolbar buttons, the same draft/published distinction, and the same version history
apply. A story behaves like a page in this regard — it has drafts that editors can work on
privately, and published versions that visitors see.

How djangocms-stories integrates
=================================

When djangocms-versioning is installed and ``STORIES_VERSIONING_ENABLED`` is ``True`` (the
default), djangocms-stories registers its ``PostContent`` model as a versionable content type.
From that point on, versioning takes over:

Creating a new story produces a **draft** version. The draft is visible to editors in the
toolbar but not to the public. Editors can revise the draft as many times as needed — adding
plugins, editing text, changing the abstract — without affecting what visitors see.

When the editor is satisfied, they **publish** the draft. This creates a frozen snapshot of the
content that becomes the live version. If the editor later wants to make changes, they create a
**new draft** from the published version. The published version remains live until the new draft
is explicitly published.

Previous versions are preserved. Editors can compare versions, review change history, and
revert to an earlier state if something goes wrong. This is identical to how page versions work
in django CMS.

If djangocms-versioning is not installed, stories are created and saved directly without any
draft/publish distinction — every save is immediately live. This simpler mode is useful during
development or for sites that don't need editorial review.

The grouper-content split
==========================

djangocms-stories uses the same grouper-content architecture that django CMS uses for pages.
The ``Post`` model is the **grouper**: it holds language-independent data like the author,
publication date, categories, tags, and main image. The ``PostContent`` model is the
**content**: it holds per-language data like the title, slug, abstract, and the content
placeholder.

Versioning operates on the content model, not the grouper. When you create a new draft, you
get a new ``PostContent`` instance linked to the same ``Post``. This means that
language-independent fields (author, dates, categories) are shared across versions, while
translated fields (title, text) are versioned independently per language.

This split is why templates work with ``post_content`` for display and ``post_content.post`` for
metadata — it mirrors the ``page_content`` / ``page`` relationship in django CMS itself.

Beyond versioning
==================

Because djangocms-stories uses the standard django CMS content architecture, it also works with
other packages that build on it:

- `djangocms-moderation <https://github.com/django-cms/djangocms-moderation>`_ adds approval
  workflows, so drafts can require sign-off before publication.
- `djangocms-timed-publishing <https://github.com/fsbraun/djangocms-timed-publishing>`_ adds
  scheduled publishing, so a draft can go live at a future date automatically.

These packages work with stories the same way they work with pages — no special configuration
is needed beyond installing them and enabling their features.
