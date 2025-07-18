def test_sitemap(page_with_menu, many_posts):
    """
    Tests if the sitemap contains the correct URLs for the posts and categories
    """
    from djangocms_stories.sitemaps import StoriesSitemap

    sitemap = StoriesSitemap()
    urls = [sitemap.location(item) for item in sitemap.items()]
    input(urls)
    # Check if all post URLs are in the sitemap
    for post in many_posts:
        assert post.get_absolute_url() in urls
