import pytest


@pytest.mark.django_db
def test_sitemap(page_with_menu, many_posts):
    """
    Tests if the sitemap contains the correct URLs for the posts and categories
    """
    from djangocms_stories.sitemaps import StoriesSitemap

    sitemap = StoriesSitemap()
    urls = [sitemap.location(item) for item in sitemap.items()]

    # Check if all post URLs are in the sitemap
    for post in many_posts:
        absolute_url = post.get_absolute_url()
        assert not absolute_url or absolute_url in urls


@pytest.mark.django_db
def test_sitemap_priority_and_changefreq(page_with_menu, many_posts):
    """Tests if the sitemap priority and changefreq are set correctly"""
    from djangocms_stories.sitemaps import StoriesSitemap

    sitemap = StoriesSitemap()
    # Check frequencies and priorities
    for item in sitemap.items():
        assert sitemap.priority(item) == item.app_config.sitemap_priority
        assert sitemap.changefreq(item) == item.app_config.sitemap_changefreq
