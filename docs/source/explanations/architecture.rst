############
Architecture
############

Understanding the architecture of djangocms-stories helps you make the most of its features and customize it effectively.

Core Components
===============

djangocms-stories is built on several key components:

**Models Layer**
  - ``Post`` - The main story model
  - ``PostContent`` - Translatable content using django-parler
  - ``PostCategory`` - Hierarchical categories
  - ``StoriesConfig`` - Application configuration

**Views Layer**
  - Class-based views for list and detail pages
  - Category and tag filtering views
  - Archive views by date

**Templates**
  - Customizable template system
  - Plugin-based content rendering
  - Multi-configuration support

App Hooks and Configuration
============================

djangocms-stories uses Django CMS app hooks for tight integration:

**StoriesConfig Model**
  Each configuration defines:
  - Namespace for URL reversing
  - Template prefixes
  - Menu behavior
  - SEO settings
  - Pagination options

**Multiple Configurations**
  You can run multiple story configurations:
  - Different templates per configuration
  - Separate content management
  - Independent settings

Plugin Architecture
===================

Content is managed through Django CMS plugins:

**Placeholder Integration**
  - Stories use Django CMS placeholders for content
  - Full plugin ecosystem available
  - Rich content editing experience

**Custom Plugins**
  - Story-specific plugins for common content types
  - Integration with existing CMS plugins
  - Extensible plugin system

Database Design
===============

The database schema is designed for flexibility and performance:

**Normalized Structure**
  - Separate models for posts and content
  - Many-to-many relationships for categories and tags
  - Optimized queries with select_related and prefetch_related

**Translation Support**
  - django-parler for field-level translations
  - Fallback language support
  - Translation-aware queries

URL Structure
=============

URLs are designed to be SEO-friendly and flexible:

**Hierarchical URLs**
  - ``/stories/`` - Story list
  - ``/stories/category/tech/`` - Category view
  - ``/stories/2024/03/my-story/`` - Date-based URLs (optional)
  - ``/stories/tag/django/`` - Tag-based filtering

**Namespaced URLs**
  - Support for multiple configurations
  - Reversible URLs with namespace support
  - Integration with Django CMS page structure

Caching Strategy
================

Performance is optimized through strategic caching:

**Query Optimization**
  - select_related for foreign keys
  - prefetch_related for many-to-many relationships
  - Efficient pagination queries

**Template Fragment Caching**
  - Cache story lists
  - Cache navigation menus
  - Cache-friendly template design

**Full-Page Caching**
  - Compatible with Django CMS caching
  - Vary headers for language support
  - Cache invalidation on content updates

Integration Points
==================

djangocms-stories integrates with the Django ecosystem:

**Django CMS Integration**
  - App hooks for page attachment
  - Toolbar integration for content management
  - Permission system integration

**Third-Party Packages**
  - django-parler for translations
  - django-taggit for tagging
  - django-meta for SEO
  - easy-thumbnails for images

**Extensibility**
  - Model inheritance for custom fields
  - Signal system for custom behavior
  - Template override system
