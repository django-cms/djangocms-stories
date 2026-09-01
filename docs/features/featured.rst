.. _featured_posts:

##############
Featured posts
##############

Any post can be **featured** to lift it above the regular date order: featured posts are
listed before all other posts, most recently featured first. Featuring is controlled by the
post's **featured date** (``date_featured``) in the *Info* section of the post admin:

* **empty** - the post is listed in the regular order by publication date,
* **in the past** - the post is featured and listed first,
* **in the future** - the post is featured from that date on, and stays in the regular order
  until then.

To feature or unfeature several posts at once, select them in the post list and use the
*Feature selection* or *Remove selection from featured* bulk action. The *featured* column of
the post list shows which posts are currently featured.

Where featuring applies
=======================

Featured posts head the post list, the category, tag and author lists, the menu and the
*Latest posts* plugin.

Featuring is deliberately **not** applied where a strict chronology is expected:

* the **archive views** and the archive plugin,
* the **RSS feeds** - otherwise a featured post would stay at the top of the feed forever.

The *Latest posts* plugin can opt out as well by unchecking **featured posts first**. Careful:
if you feature as many posts as the plugin shows, no recent post will be displayed any more.

Featured date and permalinks
============================

The featured date only affects ordering. The date a post is filed under - the one used by
date-based :ref:`permalinks <permalinks>` and by the archives - is its publication date, or its
creation date if it has not been published yet.

.. note::

    Up to djangocms-stories 0.9 the featured date replaced the publication date in date-based
    permalinks and in the archive month list. If your posts use date-based permalinks and have a
    featured date set, their URLs change accordingly.

Featured posts vs. the featured posts plugin
============================================

The **Featured posts plugin** is unrelated to the featured date: it renders a hand-picked,
sortable selection of posts, no matter whether they are featured or not.
