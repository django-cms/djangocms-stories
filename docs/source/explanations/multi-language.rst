###############
Multi-language
###############

djangocms-stories provides comprehensive multi-language support through django-parler integration.

Translation Architecture
=========================

**Field-Level Translations**
  - Only translatable fields are stored per language
  - Non-translatable fields shared across languages
  - Efficient database storage

**Language Fallbacks**
  - Configurable fallback chains
  - Graceful degradation for missing translations
  - Default language as ultimate fallback

**Translation Status**
  - Track completion status per language
  - Identify missing translations
  - Editorial workflow support

Translatable Content
====================

**Post Content Fields**
  Translatable fields include:
  - Title and slug
  - Abstract
  - Meta title and description
  - Content placeholders

**Category Fields**
  - Category names
  - Descriptions
  - SEO metadata

**Non-Translatable Fields**
  Shared across languages:
  - Publication dates
  - Author information
  - Technical settings

Language Configuration
======================

**Django Settings**
  Configure languages in settings::

    LANGUAGES = [
        ('en', 'English'),
        ('de', 'German'),
        ('fr', 'French'),
    ]

    PARLER_LANGUAGES = {
        None: (
            {'code': 'en'},
            {'code': 'de'},
            {'code': 'fr'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    }

**Per-Site Configuration**
  Different language sets per site::

    PARLER_LANGUAGES = {
        1: (  # Site ID 1
            {'code': 'en'},
            {'code': 'de'},
        ),
        2: (  # Site ID 2
            {'code': 'fr'},
            {'code': 'es'},
        ),
    }

URL Patterns
============

**Language Prefixes**
  URLs include language codes::

    /en/stories/my-post/
    /de/stories/mein-beitrag/
    /fr/stories/mon-article/

**Language-Specific Slugs**
  - Slugs can be translated
  - SEO-friendly URLs per language
  - Automatic slug generation

Content Management
==================

**Admin Interface**
  - Tabbed interface for languages
  - Translation status indicators
  - Bulk translation tools

**Frontend Editing**
  - Django CMS toolbar integration
  - In-place translation editing
  - Language switching

**Translation Workflow**
  - Mark content for translation
  - Track translation progress
  - Quality assurance processes

Template Considerations
=======================

**Language-Aware Templates**
  Access current language::

    {% load i18n %}
    {% get_current_language as LANGUAGE_CODE %}

    <html lang="{{ LANGUAGE_CODE }}">

**Translation Links**
  Provide language switching::

    {% load parler_tags %}
    {% get_available_languages post as languages %}

    {% for language in languages %}
        <a href="{{ post.get_absolute_url }}?language={{ language.code }}">
            {{ language.name }}
        </a>
    {% endfor %}

**Fallback Handling**
  Handle missing translations gracefully::

    {% load parler_tags %}

    {% if post.title %}
        <h1>{{ post.title }}</h1>
    {% else %}
        {% get_fallback_languages as fallback_languages %}
        {% for lang in fallback_languages %}
            {% if post.safe_translation_getter "title" language_code=lang %}
                <h1>{{ post.safe_translation_getter:"title":lang }}</h1>
                <p class="translation-notice">
                    Content not available in {{ LANGUAGE_CODE }}, showing {{ lang }} version.
                </p>
                {% break %}
            {% endif %}
        {% endfor %}
    {% endif %}

SEO and Multi-language
=======================

**Hreflang Tags**
  Indicate language alternatives::

    {% load parler_tags %}
    {% get_available_languages post as languages %}

    {% for language in languages %}
        <link rel="alternate"
              hreflang="{{ language.code }}"
              href="{{ post.get_absolute_url }}?language={{ language.code }}">
    {% endfor %}

**Language-Specific Sitemaps**
  Generate sitemaps per language::

    # sitemaps.py
    from djangocms_stories.sitemaps import StoriesSitemap

    class LanguageStoriesSitemap(StoriesSitemap):
        def __init__(self, language):
            self.language = language

        def items(self):
            return super().items().language(self.language)

**Canonical URLs**
  Set proper canonical URLs::

    <link rel="canonical" href="{{ post.get_absolute_url }}">

Performance Optimization
=========================

**Query Optimization**
  Minimize database queries::

    # Efficient translation queries
    posts = Post.objects.published().prefetch_related(
        'translations',
        'categories__translations'
    )

**Translation Caching**
  Cache translated content::

    {% load cache %}
    {% cache 3600 post_content post.pk LANGUAGE_CODE %}
        {{ post.title }}
        {{ post.content }}
    {% endcache %}

**Lazy Loading**
  Load translations on demand::

    # Only load when needed
    post.safe_translation_getter('title', any_language=True)

Common Patterns
===============

**Translation Status**
  Check if content is translated::

    {% if post.has_translation %}
        {{ post.title }}
    {% else %}
        <span class="untranslated">{{ post.safe_translation_getter:"title" }}</span>
    {% endif %}

**Language-Specific Content**
  Show content only for specific languages::

    {% if LANGUAGE_CODE == 'de' %}
        <div class="german-only-content">
            <!-- German-specific content -->
        </div>
    {% endif %}

**Translation Management**
  Provide translation tools::

    {% if user.is_staff %}
        <div class="translation-tools">
            <a href="{% url 'admin:myapp_post_change' post.pk %}">
                Edit translations
            </a>
        </div>
    {% endif %}
