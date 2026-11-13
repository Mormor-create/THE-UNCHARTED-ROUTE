"""
===============================================================================
The Uncharted Route — Public Blog Routes
===============================================================================

Handles all public-facing blog functionality.

Public Routes
-------------

    /blog/
        Blog homepage / catalogue

    /blog/search
        Search published blog posts

    /blog/category/<slug>
        Display posts belonging to a category

    /blog/<slug>
        Display a single published blog post

Business logic is delegated to:

    BlogService
    BlogCategoryService

This module should contain only public-facing behaviour.
Administrative blog management belongs in:

    app/routes/admin_blog.py

===============================================================================
"""

from flask import (
    Blueprint,
    abort,
    render_template,
    request, url_for,
)

from app.models import BlogPost

from app.services.blog.blog_service import (
    BlogService,
)

from app.services.blog.blog_category_service import (
    BlogCategoryService,
)

from app.services.page_hero_service import (
    PageHeroService,
)


# =============================================================================
# Blueprint
# =============================================================================

blog_bp = Blueprint(
    "blog",
    __name__,
    url_prefix="/blog",
)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_PER_PAGE = 12
SEARCH_PER_PAGE = 12
CATEGORY_PER_PAGE = 12


# =============================================================================
# Internal Helpers
# =============================================================================

def _get_page(default=1):
    """
    Safely retrieve the requested pagination page.

    Prevents invalid or negative page numbers from reaching
    the service/query layer.
    """

    page = request.args.get(
        "page",
        default,
        type=int,
    )

    if page is None or page < 1:
        return 1

    return page


def _get_per_page(default=DEFAULT_PER_PAGE):
    """
    Safely retrieve the requested page size.

    Keeps the public blog within sensible limits so a visitor
    cannot request an excessively large result set.
    """

    per_page = request.args.get(
        "per_page",
        default,
        type=int,
    )

    if per_page not in {6, 12, 18, 24}:
        return default

    return per_page


def _get_active_categories():
    """
    Return active blog categories for public navigation.
    """

    return BlogCategoryService.get_all(
        active_only=True,
    )


def _paginate(items, page, per_page):
    """
    Lightweight pagination helper.

    The BlogService currently returns query objects for its
    catalogue methods, so pagination can be applied without
    changing the service layer.

    Returns
    -------
    tuple
        (items, pagination)
    """

    try:
        pagination = items.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        return pagination.items, pagination

    except AttributeError:
        # Defensive fallback if a service method eventually
        # returns a normal list instead of a SQLAlchemy query.

        total = len(items)

        start = (page - 1) * per_page
        end = start + per_page

        sliced_items = items[start:end]

        class SimplePagination:
            def __init__(
                self,
                page,
                per_page,
                total,
            ):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (
                    (total + per_page - 1) // per_page
                    if total
                    else 0
                )

            @property
            def has_prev(self):
                return self.page > 1

            @property
            def has_next(self):
                return self.page < self.pages

            @property
            def prev_num(self):
                return self.page - 1 if self.has_prev else None

            @property
            def next_num(self):
                return self.page + 1 if self.has_next else None

            @property
            def iter_pages(self):
                return range(1, self.pages + 1)

        pagination = SimplePagination(
            page,
            per_page,
            total,
        )

        return sliced_items, pagination


# =============================================================================
# Blog Catalogue
# =============================================================================

@blog_bp.route(
    "/",
    methods=["GET"],
)
def index():
    """
    Display the public blog catalogue.

    Includes:

    - Pinned published posts
    - Featured published posts
    - Latest published posts
    - Active categories
    - Pagination
    """

    page = _get_page()
    per_page = _get_per_page()

    # -------------------------------------------------------------------------
    # Featured content
    # -------------------------------------------------------------------------

    pinned_posts = BlogService.get_pinned(
        published_only=True,
    )

    featured_posts = BlogService.get_featured(
        published_only=True,
    )

    # -------------------------------------------------------------------------
    # Latest posts
    # -------------------------------------------------------------------------

    published_query = BlogService.get_published()

    posts, pagination = _paginate(
        published_query,
        page,
        per_page,
    )

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    categories = _get_active_categories()

    # -------------------------------------------------------------------------
    # Page Hero
    # -------------------------------------------------------------------------

    page_hero = PageHeroService.get_by_page_key(
        "blog",
    )

    return render_template(
        "blog/index.html",
        posts=posts,
        featured_posts=featured_posts,
        pinned_posts=pinned_posts,
        categories=categories,
        pagination=pagination,
        page=page,
        per_page=per_page,
        page_hero=page_hero,
    )


# =============================================================================
# Blog Search
# =============================================================================

@blog_bp.route(
    "/search",
    methods=["GET"],
)
def search():
    """
    Search published blog posts.

    Query parameter
    ---------------

    q:
        Search phrase.

    page:
        Pagination page.

    per_page:
        Number of results per page.
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    page = _get_page()

    per_page = _get_per_page(
        SEARCH_PER_PAGE,
    )

    posts = []
    pagination = None

    if query:
        search_query = BlogService.search(
            query_text=query,
            published_only=True,
        )

        posts, pagination = _paginate(
            search_query,
            page,
            per_page,
        )

    categories = _get_active_categories()

    return render_template(
        "blog/search.html",
        posts=posts,
        query=query,
        categories=categories,
        pagination=pagination,
        page=page,
        per_page=per_page,
    )

def _blog_public_media_url(value):
    """Resolve CMS browser URLs and continue supporting legacy static paths."""
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    if value.startswith(("https://", "http://", "/")):
        return value
    return url_for("static", filename=value)

# =============================================================================
# Blog Category
# =============================================================================
@blog_bp.route("/category/<slug>", methods=["GET"])
def category(slug):
    """Display published blog posts belonging to an active category."""
    category_obj = BlogCategoryService.get_by_slug(slug)
    if category_obj is None or not category_obj.active:
        abort(404)

    page = _get_page()
    per_page = _get_per_page(CATEGORY_PER_PAGE)
    posts_query = BlogService.get_published(category_id=category_obj.id)
    posts, pagination = _paginate(posts_query, page, per_page)
    categories = _get_active_categories()

    # banner_image is saved from the selected Blog Categories Media CMS asset.
    category_banner_url = _blog_public_media_url(
        getattr(category_obj, "banner_image", None)
    )
    # Each post's featured image may also be a MediaAsset.browser_url.
    for item in posts:
        item.public_featured_image_url = _blog_public_media_url(
            getattr(item, "featured_image", None)
        )

    return render_template(
        "blog/category.html",
        category=category_obj,
        posts=posts,
        categories=categories,
        pagination=pagination,
        page=page,
        per_page=per_page,
        category_banner_url=category_banner_url,
    )


# =============================================================================
# Blog Detail
# =============================================================================
@blog_bp.route("/<slug>", methods=["GET"])
def detail(slug):
    """Display a published blog post and register its view."""
    post = BlogService.get_by_slug(slug)
    if post is None or not post.is_published:
        abort(404)

    BlogService.increment_views(post.id)
    categories = _get_active_categories()
    related_posts = []

    if post.category_id:
        related_query = BlogService.get_published(category_id=post.category_id)
        try:
            related_posts = (
                related_query.filter(BlogPost.id != post.id).limit(4).all()
            )
        except Exception:
            # Support service implementations that return a list.
            related_posts = [
                item for item in related_query if item.id != post.id
            ][:4]

    featured_image_url = _blog_public_media_url(
        getattr(post, "featured_image", None)
    )
    author_photo_url = _blog_public_media_url(
        getattr(post, "author_photo", None)
    )
    for item in related_posts:
        item.public_featured_image_url = _blog_public_media_url(
            getattr(item, "featured_image", None)
        )

    return render_template(
        "blog/detail.html",
        post=post,
        categories=categories,
        related_posts=related_posts,
        featured_image_url=featured_image_url,
        author_photo_url=author_photo_url,
    )