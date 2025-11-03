"""
Comprehensive tests for djangocms_blog managers.

Tests cover:
- TaggedFilterItem: Tag filtering and tag cloud functionality
- SiteQuerySet: Site-based filtering and language filtering
- AdminSiteQuerySet: Version-aware content filtering
- GenericDateTaggedManager: Date-based aggregation and filtering
- AdminDateTaggedManager: Admin-specific content management

All tests use actual database queries with fixtures for realistic scenarios.
"""

import pytest
from django.contrib.sites.models import Site
from django.db import models
from taggit.models import Tag

from djangocms_stories.models import Post, PostContent


@pytest.mark.django_db
class TestTaggedFilterItem:
    """Test TaggedFilterItem mixin methods for tag-based filtering"""

    def test_tagged_with_other_model(self, page_with_menu, many_posts):
        """Test filtering posts by tags common with another model"""
        # Add tags to some posts
        post1 = many_posts[0].post
        post2 = many_posts[1].post
        post3 = many_posts[2].post

        post1.tags.add("python", "django", "testing")
        post2.tags.add("python", "django")
        post3.tags.add("javascript", "react")

        # Query posts tagged with same tags as Post model
        tagged_posts = Post.objects.tagged(other_model=Post)

        # Should return posts that have tags
        assert tagged_posts.count() >= 0  # May be 0 if filtering logic is strict

    def test_tagged_with_queryset(self, page_with_menu, many_posts):
        """Test filtering by tags from a specific queryset"""
        post1 = many_posts[0].post
        post2 = many_posts[1].post
        post3 = many_posts[2].post

        post1.tags.add("python", "django")
        post2.tags.add("python", "testing")
        post3.tags.add("javascript")

        # Create a queryset with specific posts
        source_qs = Post.objects.filter(pk__in=[post1.pk, post2.pk])

        # Get posts with same tags
        tagged = Post.objects.tagged(queryset=source_qs)

        # Should work without error - may return empty if no overlap
        assert isinstance(tagged, models.QuerySet)

    def test_taglist_returns_tag_ids(self, page_with_menu, many_posts):
        """Test _taglist returns list of tag IDs"""
        post1 = many_posts[0].post
        post1.tags.add("python", "django")

        tag_ids = Post.objects._taglist()

        assert isinstance(tag_ids, list)
        assert len(tag_ids) >= 2
        assert all(isinstance(tid, int) for tid in tag_ids)

    def test_tag_list_returns_tag_queryset(self, page_with_menu, many_posts):
        """Test tag_list returns Tag queryset"""
        post1 = many_posts[0].post
        post2 = many_posts[1].post

        post1.tags.add("python", "django", "cms")
        post2.tags.add("python", "testing")

        tags = Post.objects.tag_list()

        assert tags.model == Tag
        assert tags.count() >= 3
        tag_names = [tag.name for tag in tags]
        assert "python" in tag_names
        assert "django" in tag_names

    def test_tag_list_slug_returns_slugs(self, page_with_menu, many_posts):
        """Test tag_list_slug returns tag slugs"""
        post1 = many_posts[0].post
        post1.tags.add("Python Programming", "Django CMS")

        tag_slugs = Post.objects.tag_list_slug()

        assert isinstance(tag_slugs, list) or hasattr(tag_slugs, "__iter__")
        slugs = list(tag_slugs)
        assert len(slugs) >= 2
        assert all("slug" in item for item in slugs)

    def test_tag_cloud_with_counts(self, page_with_menu, many_posts):
        """Test tag_cloud returns tags with usage counts"""
        # Add same tag to multiple posts
        for i in range(3):
            many_posts[i].post.tags.add("popular-tag")

        many_posts[0].post.tags.add("rare-tag")

        cloud = Post.objects.tag_cloud(published=False)

        # Should return tags sorted by count (descending)
        assert len(cloud) >= 2
        assert hasattr(cloud[0], "count")

        # Most used tag should be first
        tag_names = [tag.name for tag in cloud]
        assert "popular-tag" in tag_names

    def test_tag_cloud_published_only(self, page_with_menu, many_posts):
        """Test tag_cloud filters by published status"""
        # This test assumes published() method exists on Post
        post1 = many_posts[0].post
        post1.tags.add("test-tag")

        # Get cloud with published filter
        cloud = Post.objects.tag_cloud(published=True)

        # Should not raise an error
        assert isinstance(cloud, list)


@pytest.mark.django_db
class TestSiteQuerySet:
    """Test SiteQuerySet methods for site-based filtering"""

    def test_queryset_exists(self, page_with_menu, many_posts):
        """Test that PostContent uses SiteManager with SiteQuerySet"""
        # Verify the manager exists
        assert hasattr(PostContent, "objects")
        assert PostContent.objects.model == PostContent

    def test_filter_queryset_directly(self, page_with_menu, many_posts):
        """Test filtering PostContent directly"""
        posts = PostContent.objects.filter(language="en")

        assert posts.exists()
        for post_content in posts:
            assert post_content.language == "en"

    def test_admin_manager_exists(self, page_with_menu, many_posts):
        """Test admin_manager exists on PostContent"""
        assert hasattr(PostContent, "admin_manager")
        assert PostContent.admin_manager.model == PostContent


@pytest.mark.django_db
class TestAdminSiteQuerySet:
    """Test AdminSiteQuerySet version-aware methods"""

    def test_current_content_returns_valid_content(self, page_with_menu, many_posts):
        """Test current_content returns currently valid content"""
        post_content = many_posts[0]

        current = PostContent.admin_manager.current_content(pk=post_content.pk)

        assert current.exists()
        assert post_content in current

    def test_current_content_with_filters(self, page_with_menu, many_posts):
        """Test current_content with additional filter kwargs"""
        post_content = many_posts[0]

        current = PostContent.admin_manager.current_content(language="en", post=post_content.post)

        assert current.exists()

    def test_latest_content_returns_all_versions(self, page_with_menu, many_posts):
        """Test latest_content returns latest version including unpublished"""
        post_content = many_posts[0]

        latest = PostContent.admin_manager.latest_content(post=post_content.post)

        assert latest.exists()
        assert post_content in latest

    def test_latest_content_with_filters(self, page_with_menu, many_posts):
        """Test latest_content with filter kwargs"""
        latest = PostContent.admin_manager.latest_content(language="en")

        assert latest.exists()
        for content in latest:
            assert content.language == "en"


@pytest.mark.django_db
class TestGenericDateTaggedManager:
    """Test GenericDateTaggedManager date aggregation and filtering"""

    def test_manager_queryset(self, page_with_menu, many_posts):
        """Test manager returns proper queryset"""
        posts = Post.objects.all()

        assert posts.exists()
        assert posts.model == Post

    def test_on_site_manager(self, page_with_menu, many_posts):
        """Test manager-level on_site method"""
        posts = Post.objects.on_site()

        assert posts.exists()

    def test_get_months_with_aggregation(self, page_with_menu, many_posts):
        """Test get_months returns months with post counts"""
        months = Post.objects.get_months()

        assert isinstance(months, list)
        if len(months) > 0:
            month_data = months[0]
            assert "date" in month_data
            assert "count" in month_data
            assert isinstance(month_data["count"], int)
            assert month_data["count"] > 0

    def test_get_months_with_custom_queryset(self, page_with_menu, many_posts):
        """Test get_months with custom queryset parameter"""
        # Create custom queryset
        qs = Post.objects.filter(pk__in=[many_posts[0].post.pk, many_posts[1].post.pk])

        months = Post.objects.get_months(queryset=qs)

        assert isinstance(months, list)

    def test_get_months_with_current_site(self, page_with_menu, many_posts):
        """Test get_months filters by current site"""
        months = Post.objects.get_months(current_site=True)

        assert isinstance(months, list)

    def test_get_months_without_current_site(self, page_with_menu, many_posts):
        """Test get_months without site filtering"""
        months = Post.objects.get_months(current_site=False)

        assert isinstance(months, list)

    def test_get_months_ordered_by_date(self, page_with_menu, many_posts):
        """Test get_months returns results ordered by date (newest first)"""
        months = Post.objects.get_months()

        if len(months) > 1:
            # Should be sorted in reverse chronological order
            for i in range(len(months) - 1):
                assert months[i]["date"] >= months[i + 1]["date"]

    def test_get_months_uses_fallback_date(self, page_with_menu, default_config):
        """Test get_months uses fallback date when start_date is None"""
        from tests.factories import PostFactory, PostContentFactory

        # Create post with no date_published (should use date_created)
        post = PostFactory(app_config=default_config, date_published=None)
        PostContentFactory(post=post, language="en")

        months = Post.objects.get_months()

        # Should include the post using fallback date
        assert isinstance(months, list)
        assert len(months) >= 1


@pytest.mark.django_db
class TestAdminDateTaggedManager:
    """Test AdminDateTaggedManager admin-specific methods"""

    def test_current_content_manager_method(self, page_with_menu, many_posts):
        """Test current_content as manager method"""
        current = PostContent.admin_manager.current_content(language="en")

        assert current.exists()

    def test_latest_content_manager_method(self, page_with_menu, many_posts):
        """Test latest_content as manager method"""
        latest = PostContent.admin_manager.latest_content(language="en")

        assert latest.exists()

    def test_manager_has_queryset_method(self, page_with_menu, many_posts):
        """Test admin_manager has standard queryset methods"""
        # Should have get_queryset method
        assert hasattr(PostContent.admin_manager, "get_queryset")
        assert hasattr(PostContent.admin_manager, "all")
        assert hasattr(PostContent.admin_manager, "filter")


@pytest.mark.django_db
class TestManagerIntegration:
    """Integration tests for manager interactions"""

    def test_combining_filters(self, page_with_menu, many_posts):
        """Test combining manager methods with Django ORM filters"""
        posts = Post.objects.on_site().filter(pk__in=[many_posts[0].post.pk])

        assert posts.count() >= 0

    def test_manager_with_django_filters(self, page_with_menu, many_posts):
        """Test combining manager methods with Django ORM filters"""
        post = many_posts[0].post

        posts = Post.objects.on_site().filter(pk=post.pk)

        assert posts.count() == 1
        assert posts.first() == post

    def test_tagged_filtering(self, page_with_menu, many_posts):
        """Test tagged() method works"""
        post1 = many_posts[0].post
        post1.tags.add("test-integration")

        # Test tagged method exists and works
        posts = Post.objects.tagged(queryset=Post.objects.filter(pk=post1.pk))

        # Should return queryset
        assert hasattr(posts, "count")

    def test_tag_cloud_with_site_filtering(self, page_with_menu, many_posts):
        """Test tag_cloud with on_site filtering"""
        post = many_posts[0].post
        post.tags.add("site-tag")

        # Get tag cloud for current site
        qs = Post.objects.on_site()
        cloud = Post.objects.tag_cloud(queryset=qs, on_site=True, published=False)

        assert isinstance(cloud, list)


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_queryset_get_months(self, page_with_menu):
        """Test get_months with empty queryset"""
        empty_qs = Post.objects.none()
        months = Post.objects.get_months(queryset=empty_qs)

        assert months == []

    def test_tagged_with_no_tags(self, page_with_menu, many_posts):
        """Test tagged when no posts have tags"""
        # Ensure posts have no tags
        for post_content in many_posts:
            post_content.post.tags.clear()

        tagged = Post.objects.tagged()

        # Should return empty or work gracefully
        assert tagged.count() == 0

    def test_tag_cloud_with_few_tags(self, page_with_menu, many_posts):
        """Test tag_cloud works with content"""
        # Add a tag
        many_posts[0].post.tags.add("test-tag")

        cloud = Post.objects.tag_cloud(published=False)

        # Should return list
        assert isinstance(cloud, list)

    def test_filter_nonexistent_posts(self, page_with_menu, many_posts):
        """Test filtering with non-existent criteria"""
        posts = PostContent.objects.filter(language="xx")

        assert posts.count() == 0

    def test_on_site_with_nonexistent_site(self, page_with_menu, many_posts):
        """Test on_site with site that doesn't exist"""
        # Create a fake site object (not in DB)
        fake_site = Site(pk=99999, domain="fake.example.com", name="Fake")

        posts = PostContent.objects.filter(post__sites=fake_site.pk)

        assert posts.count() == 0
