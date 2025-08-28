##########
Versioning
##########

djangocms-stories uses the versioning capabilities of
`djangocms-versioning <https://github.com/django-cms/djangocms-versioning>`_
for publication management and editorial workflows.

To this end, it also uses extensions like `djangocms-moderation <https://github.com/django-cms/djangocms-moderation>`_,
or `djangocms-timed-publishing <https://github.com/fsbraun/djangocms-timed-publishing>`_

Versioning Architecture
=======================

**Django CMS Versioning Integration**
  - Seamless integration with django-cms versioning
  - Draft and published content separation
  - Version history tracking
  - Rollback capabilities

**Content Versioning**
  - Each edit creates a new content version
  - Publish workflow for content approval
  - Version comparison tools
  - Audit trail for all changes

Version States
==============

**Draft State**
  - Editable working version
  - Not visible to public users
  - Can have multiple draft versions
  - Author workspace for content creation

**Published State**
  - Live content visible to users
  - Read-only for content editors
  - SEO and caching optimized
  - Stable reference for links

**Unpublished State**
  - Historical versions
  - Preserved for compliance
  - Reference for content recovery
  - Audit trail maintenance

**Archived State**
  - No previously published historic versions
  - Preserved for editor convenience
