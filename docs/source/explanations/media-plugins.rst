########################
Media Plugins & Podcasting
########################

Understanding the media plugin system for vlogs, podcasts, and multimedia content.

Media Plugin Architecture
=========================

djangocms-stories provides a comprehensive media plugin system designed for multimedia content publishing. This system is particularly useful for vlogs and podcasts that require more introspection on plugin contents than is generally available to standard Django CMS plugins.

**Core Media Concepts**
  - **Media Attachment Plugins** - Plugins that can be introspected for metadata
  - **Media Placeholder** - Dedicated ``media`` placeholder added to the Post model
  - **Media Introspection** - Automatic extraction of media metadata from external platforms
  - **Template Integration** - Specialized template tags for media handling

**Design Philosophy**
  djangocms-stories provides only a generic interface to introspect media plugins but does not include plugins for specific media platforms, as these would be difficult to maintain as platforms change. The examples provided work at the time of writing but may require updates.

**Supported Media Types**
  - Video platforms (Vimeo, YouTube, custom players)
  - Audio content (podcasts, music, soundtracks)
  - Interactive media (360° videos, VR content)
  - Social media embeds with poster images

Base Classes and Mixins
=======================

**MediaAttachmentPluginMixin**
  The foundation for creating media plugins:

  ::

      from djangocms_stories.media.base import MediaAttachmentPluginMixin
      from cms.models import CMSPlugin

      class VimeoPlugin(MediaAttachmentPluginMixin, CMSPlugin):
          url = models.URLField('Video URL')

          _media_autoconfiguration = {
              'params': [
                  re.compile(r'^https://vimeo.com/(?P<media_id>[-0-9]+)$'),
              ],
              'thumb_url': '%(thumb_url)s',
              'main_url': '%(main_url)s',
              'callable': 'vimeo_data',
          }

**Required Implementation**
  Every media plugin must implement the ``media_url`` property:

  ::

      @property
      def media_url(self):
          """Return the primary media URL"""
          return self.url

**Template Tags**
  djangocms-stories provides template tags for media handling:

  - ``media_images`` - Extract cover images from media plugins
  - ``media_plugins`` - Retrieve media plugins from placeholders

Building Media Plugins
======================

**Step-by-Step Process**

1. **Create Plugin Model**
   Inherit from ``CMSPlugin`` and add ``MediaAttachmentPluginMixin``:

   ::

       class VimeoPlugin(MediaAttachmentPluginMixin, CMSPlugin):
           url = models.URLField('Video URL')

2. **Configure Media Autoconfiguration**
   Define how to extract media information:

   ::

       _media_autoconfiguration = {
           'params': [
               re.compile(r'^https://vimeo.com/(?P<media_id>[-0-9]+)$'),
           ],
           'thumb_url': '%(thumb_url)s',
           'main_url': '%(main_url)s',
           'callable': 'vimeo_data',
       }

3. **Implement Required Properties**
   Provide media_url and any additional properties:

   ::

       @property
       def media_url(self):
           return self.url

       @property
       def media_id(self):
           try:
               return self.media_params['id']
           except KeyError:
               return None

       @property
       def media_title(self):
           try:
               return self.media_params['title']
           except KeyError:
               return None

**Complete Vimeo Example**

::

    import re
    import requests
    from cms.models import CMSPlugin
    from djangocms_stories.media.base import MediaAttachmentPluginMixin

    class VimeoPlugin(MediaAttachmentPluginMixin, CMSPlugin):
        url = models.URLField('Video URL')

        _media_autoconfiguration = {
            'params': [
                re.compile(r'^https://vimeo.com/(?P<media_id>[-0-9]+)$'),
            ],
            'thumb_url': '%(thumb_url)s',
            'main_url': '%(main_url)s',
            'callable': 'vimeo_data',
        }

        def __str__(self):
            return self.url

        @property
        def media_id(self):
            try:
                return self.media_params['id']
            except KeyError:
                return None

        @property
        def media_title(self):
            try:
                return self.media_params['title']
            except KeyError:
                return None

        @property
        def media_url(self):
            return self.url

        def vimeo_data(self, media_id):
            """Fetch video metadata from Vimeo API"""
            response = requests.get(
                f'https://vimeo.com/api/v2/video/{media_id}.json'
            )
            json_data = response.json()
            data = {}
            if json_data:
                data = json_data[0]
                data.update({
                    'main_url': data['thumbnail_large'],
                    'thumb_url': data['thumbnail_medium'],
                })
            return data

Plugin Registration
===================

**CMS Plugin Class**
  Register the plugin with Django CMS:

  ::

      from cms.plugin_pool import plugin_pool
      from cms.plugin_base import CMSPluginBase

      @plugin_pool.register_plugin
      class VimeoPlugin(CMSPluginBase):
          model = VimeoPlugin
          module = 'Media'
          name = 'Vimeo'
          render_template = 'media_app/vimeo.html'

**Plugin Template**
  Create the rendering template:

  ::

      <!-- media_app/vimeo.html -->
      {% if instance.media_id %}
          <iframe
              src="https://player.vimeo.com/video/{{ instance.media_id }}?badge=0&autopause=0&player_id=0&app_id=2221"
              width="1920"
              height="1080"
              frameborder="0"
              title="{{ instance.media_title }}"
              allow="autoplay; fullscreen"
              allowfullscreen>
          </iframe>
      {% endif %}

Template Integration
====================

**Media Placeholder Usage**
  The ``media`` placeholder must be rendered in templates to allow plugin addition:

  ::

      <!-- post_detail.html -->
      {% if not post.main_image_id %}
          <div class="blog-visual">
              {% render_placeholder post.media %}
          </div>
      {% else %}
          <!-- Regular image display -->
      {% endif %}

**Media Images in Post Lists**
  Use the ``media_images`` template tag to show cover images:

  ::

      <!-- post_list.html -->
      {% load djangocms_stories %}

      {% for post in postcontent_list %}
          {% media_images post as previews %}
          <article class="post-item">
              <div class="blog-visual">
                  {% for preview in previews %}
                      <img src="{{ preview }}" alt="Media preview" />
                  {% endfor %}
              </div>
              <h3><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h3>
          </article>
      {% endfor %}

**Media Plugins Access**
  Retrieve media plugins programmatically:

  ::

      <!-- Template usage -->
      {% media_plugins post as media_content %}
      {% for plugin in media_content %}
          <div class="media-item" data-type="{{ plugin.plugin_type }}">
              {% render_plugin plugin %}
          </div>
      {% endfor %}

Podcast Integration
==================

**Podcast Episode Plugin**
  Create specialized podcast plugins:

  ::

      class PodcastEpisodePlugin(MediaAttachmentPluginMixin, CMSPlugin):
          episode_title = models.CharField(max_length=200)
          episode_number = models.PositiveIntegerField()
          audio_url = models.URLField()
          duration = models.DurationField()
          transcript_url = models.URLField(blank=True)

          _media_autoconfiguration = {
              'thumb_url': '%(cover_image)s',
              'main_url': '%(audio_url)s',
              'callable': 'get_podcast_metadata',
          }

          def get_podcast_metadata(self):
              return {
                  'title': self.episode_title,
                  'duration': str(self.duration),
                  'cover_image': self.get_cover_image_url(),
                  'audio_url': self.audio_url,
              }

**Podcast Player Template**
  Rich audio player interface:

  ::

      <!-- podcast_player.html -->
      <div class="podcast-player">
          <div class="episode-info">
              <h4>{{ instance.episode_title }}</h4>
              <span class="episode-meta">Episode {{ instance.episode_number }}</span>
              <span class="duration">{{ instance.duration }}</span>
          </div>

          <audio controls preload="metadata">
              <source src="{{ instance.audio_url }}" type="audio/mpeg">
              Your browser does not support the audio element.
          </audio>

          {% if instance.transcript_url %}
              <a href="{{ instance.transcript_url }}" class="transcript-link">
                  View Transcript
              </a>
          {% endif %}
      </div>

djangocms-video Support
=======================

**Poster Attribute Integration**
  djangocms-video ``poster`` attributes are automatically supported:

  ::

      # The poster field from djangocms-video plugins
      # is automatically detected and included in media_images

      {% media_images post as previews %}
      <!-- This will include both custom media plugin images
           and djangocms-video poster images -->

**Video Plugin Enhancement**
  Extend djangocms-video with media attachment capabilities:

  ::

      from djangocms_video.models import VideoPlayer

      class EnhancedVideoPlayer(MediaAttachmentPluginMixin, VideoPlayer):
          """Enhanced video player with media attachment features"""

          _media_autoconfiguration = {
              'thumb_url': '%(poster)s',  # Use existing poster field
              'main_url': '%(movie_url)s',
          }

          @property
          def media_url(self):
              return self.movie_url or self.movie.url
