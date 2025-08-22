##############
Content Model
##############

Understanding the content model helps you work effectively with djangocms-stories.

Post Model Structure
====================

The content model separates concerns between posts and their content:

**Post Model**
  Contains non-translatable fields:
  - Publication status and dates
  - Author information
  - Configuration references
  - Technical metadata

**PostContent Model**
  Contains translatable fields:
  - Title and slug
  - Abstract and meta descriptions
  - Content placeholders
  - SEO-specific fields

This separation allows:
- Efficient translation management
- Language-independent scheduling
- Consistent metadata across languages

Content Relationships
=====================

**Categories**
  - Hierarchical structure with parent/child relationships
  - Many-to-many relationship with posts
  - Translatable names and descriptions
  - URL-friendly slugs per language

**Tags**
  - Flat tag structure using django-taggit
  - Automatic suggestion and completion
  - Tag clouds and filtering
  - Cross-language tag sharing

**Authors**
  - Integration with Django's User model
  - Multiple authors per post support
  - Author profile extensions possible

Content Lifecycle
==================

**Draft State**
  - Posts start as drafts
  - Preview functionality available
  - Editorial workflow support

**Publication**
  - Scheduled publishing support
  - Publication date ranges
  - Automatic publication/expiration

**Archiving**
  - Soft deletion with archive states
  - Historical content preservation
  - SEO-friendly redirects

Placeholder System
==================

Content uses Django CMS placeholders:

**Main Content**
  - Rich text editor integration
  - Image and media management
  - Plugin-based content blocks

**Structured Content**
  - Reusable content components
  - Consistent formatting
  - Template-driven layouts

**Custom Placeholders**
  - Extensible placeholder system
  - Template-specific content areas
  - Plugin restrictions possible

SEO and Metadata
=================

**Automatic Meta Generation**
  - Title tag optimization
  - Meta description from abstract
  - Open Graph and Twitter Cards
  - Canonical URL management

**Custom Meta Fields**
  - Override automatic generation
  - Per-language customization
  - Social media optimization

**Structured Data**
  - JSON-LD markup support
  - Rich snippets compatibility
  - Search engine optimization

Content Versioning
===================

**Language Versions**
  - Independent content per language
  - Fallback language support
  - Translation status tracking

**Publication Versions**
  - Draft and published content separation
  - Preview functionality
  - Rollback capabilities (future feature)

**Content History**
  - Audit trail for changes
  - Author attribution
  - Timestamp tracking

Media Management
================

**Image Handling**
  - Integration with django-filer
  - Automatic thumbnail generation
  - Responsive image support

**File Attachments**
  - Document management
  - Download tracking possible
  - Access control integration

**Rich Media**
  - Video and audio support
  - Embed functionality
  - Gallery creation

Content Validation
==================

**Required Fields**
  - Title validation
  - Slug uniqueness per language
  - Publication date validation

**Content Guidelines**
  - Abstract length recommendations
  - SEO title optimization
  - Image alt-text requirements

**Editorial Workflow**
  - Status tracking
  - Review processes
  - Quality assurance

Search and Filtering
====================

**Built-in Search**
  - Title and content search
  - Category filtering
  - Tag-based filtering
  - Date range queries

**Advanced Search**
  - Full-text search integration possible
  - Faceted search support
  - Search result ranking

**Performance Optimization**
  - Database indexes
  - Query optimization
  - Caching strategies
