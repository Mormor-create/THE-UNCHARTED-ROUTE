"""
===============================================================================
The Uncharted Route — Admin Blog Management Routes
===============================================================================

Administrative management of blog posts and blog categories.

Public blog routes live in:
    app/routes/blogs.py

Administrative blog routes live under:
    /admin/blog/

Post Routes
-----------
    /admin/blog/
    /admin/blog/create
    /admin/blog/<id>
    /admin/blog/<id>/edit
    /admin/blog/<id>/publish
    /admin/blog/<id>/schedule
    /admin/blog/<id>/submit-review
    /admin/blog/<id>/archive
    /admin/blog/<id>/restore
    /admin/blog/<id>/feature
    /admin/blog/<id>/unfeature
    /admin/blog/<id>/pin
    /admin/blog/<id>/unpin
    /admin/blog/<id>/seo
    /admin/blog/<id>/cta
    /admin/blog/<id>/delete

Category Routes
---------------
    /admin/blog/categories/
    /admin/blog/categories/create
    /admin/blog/categories/<id>
    /admin/blog/categories/<id>/edit
    /admin/blog/categories/<id>/activate
    /admin/blog/categories/<id>/deactivate
    /admin/blog/categories/<id>/feature
    /admin/blog/categories/<id>/unfeature
    /admin/blog/categories/<id>/sort
    /admin/blog/categories/<id>/delete

Business logic is delegated to:

    BlogService
    BlogCategoryService

Authorization
-------------

Administrative authorization is intentionally disabled at this stage.

The centralized admin decorator is retained in commented form so that
permissions can be enabled later without restructuring the blueprint.

===============================================================================
"""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app, )
from app.decorators.admin import admin_required
from app.forms.blog import (
    BlogCategoryFilterForm,
    BlogCategoryForm,
    BlogCategorySortForm,
    BlogCategoryDeleteForm,
    BlogPostCTAForm,
    BlogPostDeleteForm,
    BlogPostFilterForm,
    BlogPostForm,
    BlogPostPublishForm,
    BlogPostScheduleForm,
    BlogPostSEOForm,
    BlogPostStatusForm, BlogReviewForm, BlogPostFeatureForm, BlogPostPinForm, BlogPostRestoreForm,
    BlogPostArchiveForm, )
from app.models.blog_category import BlogCategory
from app.models.blog_post import BlogPost
from app.models.destination import Destination
from app.models.experience import Experience
from app.services.blog.blog_category_service import (
    BlogCategoryService,)
from app.services.blog.blog_service import (
    BlogService,)
from extensions import db
from app.models.media_asset import MediaAsset

# =============================================================================
# Blueprint
# =============================================================================
admin_blog_bp = Blueprint(
    "admin_blog",
    __name__,
    url_prefix="/admin/blog",)

# =============================================================================
# Constants
# =============================================================================
POST_STATUSES = {
    "Draft",
    "Review",
    "Scheduled",
    "Published",
    "Archived",}

# =============================================================================
# Choice Helpers
# =============================================================================
def _category_choices(include_inactive=True):
    """
    Build category choices for post forms.
    """
    categories = BlogCategoryService.get_all(active_only=not include_inactive,)
    choices = [(0, "— Select category —"),]
    for category in categories:
        label = category.name
        if not category.active:
            label += " (Inactive)"
        choices.append(
            (category.id,label,))

    return choices

def _experience_choices():
    """Return choices for the related experience field."""

    experiences = (
        Experience.query
        .order_by(
            Experience.title.asc()
        ).all())

    return [(0, "None")] + [
        (experience.id, experience.title)for experience in experiences]

def _destination_choices():
    """
    Build destination choices for related-content fields.
    """
    destinations = (
        Destination.query
        .order_by(
            Destination.name.asc()
        ).all())
    choices = [(0, "— No related destination —"),]
    for destination in destinations:
        choices.append(
            (
                destination.id,
                destination.name,))
    return choices

def _populate_post_form(form):
    """
    Populate dynamic BlogPost form choices.

    QuerySelectField is deliberately not used so the project
    does not require an additional WTForms-SQLAlchemy dependency.
    """

    if hasattr(form, "category_id"):

        form.category_id.choices = _category_choices(
            include_inactive=True,
        )

    if hasattr(form, "related_experience_id"):

        form.related_experience_id.choices = (
            _experience_choices()
        )

    if hasattr(form, "related_destination_id"):

        form.related_destination_id.choices = (
            _destination_choices()
        )

# =============================================================================
# Form Helpers
# =============================================================================
def _selected_media_asset(form, field_name):
    """Return a selected MediaAsset only if it is one of this form's choices."""
    field = getattr(form, field_name, None)
    asset_id = field.data if field is not None else None
    if not asset_id:
        return None

    allowed_ids = {
        str(value)
        for value, _label in (getattr(field, "choices", None) or [])
        if value not in (None, "")
    }
    if str(asset_id) not in allowed_ids:
        current_app.logger.warning(
            "Rejected media asset ID %r for selector %s because it is not an allowed choice.",
            asset_id,
            field_name,
        )
        return None

    try:
        return db.session.get(MediaAsset, int(asset_id))
    except (TypeError, ValueError):
        current_app.logger.warning(
            "Invalid MediaAsset ID %r received for selector %s.",
            asset_id,
            field_name,
        )
        return None


def _selected_media_url(form, field_name):
    """Resolve a selected MediaAsset ID to its Media CMS browser URL."""
    asset = _selected_media_asset(form, field_name)
    if asset is None:
        return None

    url = getattr(asset, "browser_url", None)
    if not url:
        current_app.logger.warning(
            "Selected MediaAsset %s has no browser_url.",
            getattr(asset, "id", None),
        )
    return url


def _selected_media_alt(form, field_name):
    """Resolve useful alt text from the selected MediaAsset."""
    asset = _selected_media_asset(form, field_name)
    if asset is None:
        return None

    for attribute in ("alt_text", "alt", "title", "original_filename", "filename"):
        value = getattr(asset, attribute, None)
        if value:
            return str(value).strip()
    return None


def _apply_post_form_to_data(form):
    """Convert BlogPostForm values into the fields accepted by BlogService."""
    import json

    def clean(field_name):
        field = getattr(form, field_name, None)
        if field is None or field.data is None:
            return None
        value = field.data
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    gallery = None
    gallery_text = clean("gallery")
    if gallery_text:
        try:
            gallery = json.loads(gallery_text)
        except (TypeError, ValueError):
            # Keep malformed optional gallery data from breaking post saves.
            current_app.logger.warning(
                "Blog gallery field was not valid JSON; saving an empty gallery."
            )

    featured_image = (
        _selected_media_url(form, "featured_media_asset_id")
        or clean("featured_image")
    )
    social_image = (
        _selected_media_url(form, "social_media_asset_id")
        or clean("social_image")
        or featured_image
    )

    return {
        "category_id": form.category_id.data,
        "title": clean("title"),
        "slug": clean("slug"),
        "subtitle": clean("subtitle"),
        "excerpt": clean("excerpt"),
        "content": form.content.data or "",
        "author": clean("author"),
        "author_title": clean("author_title"),
        "author_photo": clean("author_photo"),
        "featured_image": featured_image,
        "featured_image_alt": (
            _selected_media_alt(form, "featured_media_asset_id")
            or clean("featured_image_alt")
        ),
        "cover_video": clean("cover_video"),
        "gallery": gallery,
        "reading_time": form.reading_time.data,
        "word_count": form.word_count.data,
        "status": form.status.data,
        "published_at": form.published_at.data,
        "scheduled_for": form.scheduled_for.data,
        "featured": bool(form.featured.data),
        "pinned": bool(form.pinned.data),
        "allow_comments": bool(form.allow_comments.data),
        "related_experience_id": form.related_experience_id.data or None,
        "related_destination_id": form.related_destination_id.data or None,
        "cta_title": clean("cta_title"),
        "cta_text": clean("cta_text"),
        "cta_button_text": clean("cta_button_text"),
        "cta_button_url": clean("cta_button_url"),
        "meta_title": clean("meta_title"),
        "meta_description": clean("meta_description"),
        "meta_keywords": clean("meta_keywords"),
        "canonical_url": clean("canonical_url"),
        "social_title": clean("social_title"),
        "social_description": clean("social_description"),
        "social_image": social_image,
    }


def _select_media_id_for_url(form, field_name, url, assets):
    """Select the MediaAsset that matches a record's stored browser URL."""
    field = getattr(form, field_name, None)
    if field is None or not url:
        return

    for asset in assets or []:
        asset_url = getattr(asset, "browser_url", None)
        if asset_url and str(asset_url) == str(url):
            field.data = str(asset.id)
            return


def _populate_post_form_from_model(form, post):
    """Populate the post form from an existing BlogPost record."""
    import json

    fields = (
        "category_id", "title", "slug", "subtitle", "excerpt", "content",
        "author", "author_title", "author_photo", "featured_image",
        "featured_image_alt", "cover_video", "reading_time", "word_count",
        "status", "published_at", "scheduled_for", "featured", "pinned",
        "allow_comments", "cta_title", "cta_text", "cta_button_text",
        "cta_button_url", "meta_title", "meta_description", "meta_keywords",
        "canonical_url", "social_title", "social_description", "social_image",
    )
    for field_name in fields:
        field = getattr(form, field_name, None)
        if field is not None:
            field.data = getattr(post, field_name, None)

    form.related_experience_id.data = post.related_experience_id or 0
    form.related_destination_id.data = post.related_destination_id or 0

    gallery = getattr(post, "gallery", None)
    if gallery:
        form.gallery.data = json.dumps(gallery, indent=2)
    else:
        form.gallery.data = ""

    assets = getattr(form, "_post_media_assets", [])
    _select_media_id_for_url(
        form, "featured_media_asset_id",
        getattr(post, "featured_image", None), assets,
    )
    _select_media_id_for_url(
        form, "social_media_asset_id",
        getattr(post, "social_image", None), assets,
    )


def _selected_category_banner_url(form):
    """Use the selected Blog Categories asset, then preserve legacy URL input."""
    return (
        _selected_media_url(form, "banner_media_asset_id")
        or (
            (form.banner_image.data or "").strip()
            if getattr(form, "banner_image", None)
            else None
        )
    )


def _populate_category_form_from_model(form, category):
    """Populate category fields and match the current banner to a MediaAsset."""
    for field_name in (
        "name", "slug", "description", "icon", "color", "banner_image",
        "meta_title", "meta_description", "meta_keywords", "featured",
        "active", "sort_order",
    ):
        field = getattr(form, field_name, None)
        if field is not None:
            field.data = getattr(category, field_name, None)

    _select_media_id_for_url(
        form,
        "banner_media_asset_id",
        getattr(category, "banner_image", None),
        getattr(form, "_category_media_assets", []),
    )


# =============================================================================
# POST MANAGEMENT
# =============================================================================
# -----------------------------------------------------------------------------
# Blog Dashboard
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/",methods=["GET"],)
@admin_required
def index():
    """
    Display the Blog CMS dashboard.

    Supports:

    - Search
    - Status filtering
    - Category filtering
    - Featured filtering
    - Pinned filtering
    - Newsletter status
    - Search-index status
    """

    form = BlogPostFilterForm(request.args,)
    if hasattr(form, "category_id"):
        form.category_id.choices = _category_choices(
            include_inactive=True,)
    query = request.args.get(
        "q","",type=str,).strip()
    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()

    category_id = request.args.get(
        "category_id",0,type=int,)
    featured = request.args.get(
        "featured","",type=str,)
    pinned = request.args.get(
        "pinned","",type=str,)
    newsletter_sent = request.args.get(
        "newsletter_sent","",type=str,)
    search_indexed = request.args.get(
        "search_indexed","",type=str,)

    # -------------------------------------------------------------------------
    # Query
    # -------------------------------------------------------------------------
    if query:
        posts_query = BlogService.search(
            query_text=query,
            published_only=False,
            category_id=(
                category_id
                if category_id
                else None),)

        if status:
            posts_query = posts_query.filter(
                BlogPost.status == status)

    else:
        posts_query = BlogService.get_all(
            status=status or None,
            category_id=(
                category_id
                if category_id
                else None),
            featured_only=featured == "1",
            pinned_only=pinned == "1",)

    # -------------------------------------------------------------------------
    # Additional filters
    # -------------------------------------------------------------------------
    if newsletter_sent in {"0", "1"}:
        posts_query = posts_query.filter(
            BlogPost.newsletter_sent
            == (newsletter_sent == "1"))
    if search_indexed in {"0", "1"}:
        posts_query = posts_query.filter(
            BlogPost.search_indexed
            == (search_indexed == "1")
        )

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    page = request.args.get("page",1,type=int,)
    if page < 1:
        page = 1

    per_page = request.args.get("per_page",15,type=int,)
    if per_page not in {
        10,
        15,
        25,
        50,}:
        per_page = 15

    try:
        pagination = posts_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,)
        posts = pagination.items
    except AttributeError:
        posts = list(posts_query)
        total = len(posts)
        start = (
            (page - 1)
            * per_page
        )

        end = start + per_page

        posts = posts[
            start:end
        ]

        pagination = None

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    statistics = BlogService.get_statistics()
    categories = BlogCategoryService.get_all(active_only=False,)
    return render_template(
        "admin/blog/index.html",
        posts=posts,
        pagination=pagination,
        form=form,
        statistics=statistics,
        categories=categories,)

# -----------------------------------------------------------------------------
# Create Post
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    """Create a blog post using Blog Posts media only."""
    form = BlogPostForm()
    _populate_post_form(form)
    form.set_media_choices()

    if form.validate_on_submit():
        try:
            data = _apply_post_form_to_data(form)
            post = BlogService.create_post(**data)

            flash("Blog post created successfully.", "success")

            return redirect(
                url_for(
                    "admin_blog.detail",
                    post_id=post.id,
                )
            )

        except Exception:
            current_app.logger.exception(
                "Failed to create blog post."
            )
            db.session.rollback()
            flash(
                "The blog post could not be saved. Please review "
                "the form and try again.",
                "danger",
            )

    return render_template(
        "admin/blog/create.html",
        form=form,
    )

# -----------------------------------------------------------------------------
# Post Detail
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>", methods=["GET"])
@admin_required
def detail(post_id):
    """Display a blog post in the admin CMS."""
    post = BlogService.get_by_id(post_id)

    if post is None:
        abort(404)

    return render_template(
        "admin/blog/detail.html",
        post=post,
        publish_form=BlogPostPublishForm(),
        review_form=BlogReviewForm(),
        feature_form=BlogPostFeatureForm(),
        pin_form=BlogPostPinForm(),
        restore_form=BlogPostRestoreForm(),
        archive_form=BlogPostArchiveForm(),
        delete_form=BlogCategoryDeleteForm(),
    )

# -----------------------------------------------------------------------------
# Edit Post
# -----------------------------------------------------------------------------
@admin_blog_bp.route(
    "/<int:post_id>/edit",
    methods=["GET", "POST"],)
@admin_required
def edit(post_id):
    """Edit a blog post using Blog Posts media only."""
    post = BlogService.get_by_id(post_id)

    if post is None:
        abort(404)

    form = BlogPostForm()
    _populate_post_form(form)
    form.set_media_choices()

    if request.method == "GET":
        _populate_post_form_from_model(form, post)

    if form.validate_on_submit():
        try:
            data = _apply_post_form_to_data(form)
            updated_post = BlogService.update_post(
                post_id,
                **data,
            )

            flash("Blog post updated successfully.", "success")

            return redirect(
                url_for(
                    "admin_blog.detail",
                    post_id=updated_post.id,
                )
            )

        except Exception:
            current_app.logger.exception(
                "Failed to update blog post."
            )
            db.session.rollback()
            flash(
                "The blog post could not be updated. Please try again.",
                "danger",
            )

    return render_template(
        "admin/blog/edit.html",
        form=form,
        post=post,
    )

# -----------------------------------------------------------------------------
# Submit for Review
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/submit-review",methods=["POST"],)
# @admin_required
def submit_review(post_id):
    """
    Submit a draft blog post for editorial review.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    try:
        BlogService.submit_for_review(post_id,)
        flash("Blog post submitted for review.","success",)

    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.detail",
            post_id=post_id,))

# -----------------------------------------------------------------------------
# Publish
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/publish",methods=["GET", "POST"],)
@admin_required
def publish(post_id):
    """
    Publish a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    form = BlogPostPublishForm()
    if form.validate_on_submit():

        try:
            published_at = (
                form.published_at.data
                if getattr(
                    form,"published_at",
                    None,)else None)

            BlogService.publish(
                post_id,
                published_at=published_at,)
            flash("Blog post published successfully.","success",)
            return redirect(
                url_for(
                    "admin_blog.detail",
                    post_id=post_id,))
        except Exception as exc:
            flash(
                str(exc),"danger",)

    return render_template( "admin/blog/publish.html",
        form=form,post=post,)

# -----------------------------------------------------------------------------
# Schedule
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/schedule",methods=["GET", "POST"],)
@admin_required
def schedule(post_id):
    """
    Schedule a blog post for future publication.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    form = BlogPostScheduleForm()
    if request.method == "GET":
        form.scheduled_for.data = post.scheduled_for
    if form.validate_on_submit():
        try:
            BlogService.schedule(
                post_id,form.scheduled_for.data,)

            flash(
                "Blog post scheduled successfully.",
                "success",
            )

            return redirect(
                url_for("admin_blog.detail",
                    post_id=post_id,))

        except Exception as exc:
            flash(str(exc),"danger",)

    return render_template("admin/blog/schedule.html",form=form,post=post,)

# -----------------------------------------------------------------------------
# Status
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/status",methods=["POST"],)
@admin_required
def status(post_id):
    """
    Change the status of a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    form = BlogPostStatusForm()
    if form.validate_on_submit():
        new_status = form.status.data
        if new_status not in POST_STATUSES:
            flash("Invalid blog post status.","danger",)

            return redirect(
                request.referrer
                or url_for(
                    "admin_blog.detail",post_id=post_id,))

        try:

            BlogService.update_post(
                post_id,status=new_status,)

            flash(f"Blog post status changed to {new_status}.","success",)

        except Exception as exc:
            flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for(
            "admin_blog.detail",post_id=post_id,))

# -----------------------------------------------------------------------------
# Archive
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/archive",methods=["POST"],)
@admin_required
def archive(post_id):
    """
    Archive a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:abort(404)
    try:
        BlogService.archive(post_id,)
        flash("Blog post archived.","success",)

    except Exception as exc:
        flash(str(exc), "danger",)

    return redirect(
        request.referrer
        or url_for(
            "admin_blog.detail",
            post_id=post_id,))

# -----------------------------------------------------------------------------
# Restore
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/restore",methods=["POST"],)
@admin_required
def restore(post_id):
    """
    Restore an archived blog post to Draft.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:abort(404)

    try:
        BlogService.restore_to_draft(post_id,)
        flash("Blog post restored to draft.","success",)
    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for(
            "admin_blog.detail",
            post_id=post_id,))

# -----------------------------------------------------------------------------
# Feature
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/feature",methods=["POST"],)
@admin_required
def feature(post_id):
    """
    Mark a blog post as featured.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    try:
        BlogService.feature(post_id,)
        flash("Blog post featured.","success",)
    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.detail",post_id=post_id,))

# -----------------------------------------------------------------------------
# Unfeature
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/unfeature", methods=["POST"],)
@admin_required
def unfeature(post_id):
    """
    Remove featured status from a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)
    try:

        BlogService.unfeature(post_id,)
        flash("Blog post removed from featured content.","success",)

    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.detail",
            post_id=post_id,))

# -----------------------------------------------------------------------------
# Pin
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/pin",methods=["POST"],)
@admin_required
def pin(post_id):
    """
    Pin a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    try:
        BlogService.pin(post_id,)
        flash("Blog post pinned.","success",)
    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.detail",post_id=post_id,))

# -----------------------------------------------------------------------------
# Unpin
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/unpin",methods=["POST"],)
@admin_required
def unpin(post_id):
    """
    Remove pinned status from a blog post.
    """
    post = BlogService.get_by_id(post_id,)

    if post is None:
        abort(404)

    try:
        BlogService.unpin(post_id,)
        flash("Blog post unpinned.","success",)

    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.detail",post_id=post_id,))

# -----------------------------------------------------------------------------
# SEO
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/seo",methods=["GET", "POST"],)
@admin_required
def seo(post_id):
    """
    Manage blog post SEO information.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    form = BlogPostSEOForm()
    form.set_media_choices()

    if request.method == "GET":
        form.meta_title.data = post.meta_title
        form.meta_description.data = post.meta_description
        form.meta_keywords.data = post.meta_keywords
        form.canonical_url.data = post.canonical_url
        form.social_title.data = post.social_title
        form.social_description.data = post.social_description
        form.social_image.data = post.social_image
        _select_media_id_for_url(
            form,
            "social_media_asset_id",
            post.social_image,
            getattr(form, "_post_media_assets", []),
        )

    if form.validate_on_submit():
        try:
            selected_social_image = (
                _selected_media_url(form, "social_media_asset_id")
                or (form.social_image.data or "").strip()
                or None
            )
            BlogService.update_seo(
                post_id,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                meta_keywords=form.meta_keywords.data,
                canonical_url=form.canonical_url.data,
                social_title=form.social_title.data,
                social_description=form.social_description.data,
                social_image=selected_social_image,
            )

            flash("Blog SEO information updated.","success",)
            return redirect(
                url_for("admin_blog.detail",post_id=post_id,))

        except Exception as exc:
            flash(str(exc),"danger",)

    return render_template("admin/blog/seo.html",
        form=form,post=post,)

# -----------------------------------------------------------------------------
# CTA
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/cta",methods=["GET", "POST"],)
@admin_required
def cta(post_id):
    """
    Manage the marketing call-to-action attached to a post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)

    form = BlogPostCTAForm()
    if request.method == "GET":
        form.cta_title.data = post.cta_title
        form.cta_text.data = post.cta_text
        form.cta_button_text.data = post.cta_button_text
        form.cta_button_url.data = post.cta_button_url

    if form.validate_on_submit():
        try:
            BlogService.update_cta(
                post_id,
                cta_title=form.cta_title.data,
                cta_text=form.cta_text.data,
                cta_button_text=form.cta_button_text.data,
                cta_button_url=form.cta_button_url.data,)
            flash("Blog call-to-action updated.","success",)
            return redirect(
                url_for("admin_blog.detail",post_id=post_id,))

        except Exception as exc:
            flash(str(exc),"danger",)

    return render_template("admin/blog/cta.html",
        form=form,post=post,)

# -----------------------------------------------------------------------------
# Delete Post
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/<int:post_id>/delete",methods=["POST"],)
@admin_required
def delete(post_id):
    """
    Permanently delete a blog post.
    """
    post = BlogService.get_by_id(post_id,)
    if post is None:
        abort(404)
    form = BlogPostDeleteForm()
    if not form.validate_on_submit():
        flash("Invalid delete request.","danger",)

        return redirect(
            request.referrer
            or url_for("admin_blog.index",))

    try:
        BlogService.delete(post_id,)
        flash(
            "Blog post permanently deleted.",
            "success",)

    except Exception as exc:
        flash(
            str(exc),"danger",)

    return redirect(
        url_for("admin_blog.index",))

# =============================================================================
# CATEGORY MANAGEMENT
# =============================================================================
# -----------------------------------------------------------------------------
# Category Index
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/",methods=["GET"],)
@admin_required
def categories():
    """
    Display all blog categories.
    """
    form = BlogCategoryFilterForm(request.args,)
    query = request.args.get("q","",type=str,).strip()
    active = request.args.get("active","",type=str,)
    featured = request.args.get("featured","",type=str,)
    if query:
        category_list = BlogCategoryService.search(
            query_text=query,
            active_only=False,
            featured_only=featured == "1",)

    else:
        category_list = BlogCategoryService.get_all(
            active_only=active == "1",
            featured_only=featured == "1",)

    # -------------------------------------------------------------------------
    # Optional active filter
    # -------------------------------------------------------------------------
    if active == "0":
        category_list = [
            category
            for category in category_list
            if not category.active]

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    page = request.args.get("page",1,type=int,)
    if page < 1:
        page = 1
    per_page = request.args.get("per_page",20,type=int,)
    if per_page not in {
        10,
        20,
        50,}:

        per_page = 20
    total = len(category_list)
    start = ((page - 1)* per_page)
    end = start + per_page
    paginated_categories = category_list[start:end]
    total_pages = ((total+ per_page- 1)
        // per_page
        if total
        else 0)

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": (
            page - 1
            if page > 1
            else None),
        "next_num": (
            page + 1
            if page < total_pages
            else None),}

    statistics = (BlogCategoryService.get_statistics())
    return render_template(
        "admin/blog/categories/index.html",
        categories=paginated_categories,
        pagination=pagination,
        form=form,
        statistics=statistics,)

# -----------------------------------------------------------------------------
# Create Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/create", methods=["GET", "POST"])
@admin_required
def create_category():
    """Create a blog category using Blog Categories media only."""
    form = BlogCategoryForm()

    # Load active image choices from Blog Categories and its descendants.
    form.set_media_choices()

    if form.validate_on_submit():
        try:
            category = BlogCategoryService.create_category(
                name=form.name.data.strip(),
                slug=form.slug.data.strip(),
                description=form.description.data,
                icon=form.icon.data,
                color=form.color.data,
                banner_image=_selected_category_banner_url(form),
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                meta_keywords=form.meta_keywords.data,
                featured=form.featured.data,
                active=form.active.data,
                sort_order=form.sort_order.data,
            )

            flash("Blog category created successfully.", "success")

            return redirect(
                url_for(
                    "admin_blog.category_detail",
                    category_id=category.id,
                )
            )

        except Exception:
            current_app.logger.exception(
                "Failed to create blog category."
            )
            db.session.rollback()
            flash(
                "The blog category could not be saved. Please review "
                "the form and try again.",
                "danger",
            )

    return render_template(
        "admin/blog/categories/create.html",
        form=form,
    )


# -----------------------------------------------------------------------------
# Category Detail
# -----------------------------------------------------------------------------
@admin_blog_bp.route(
    "/categories/<int:category_id>",
    methods=["GET"],
)
# @admin_required
def category_detail(category_id):
    """Display a category and its associated posts."""
    category = BlogCategoryService.get_by_id(category_id)

    if category is None:
        abort(404)

    posts = BlogService.get_all(category_id=category.id)

    return render_template(
        "admin/blog/categories/detail.html",
        category=category,
        posts=posts,
        sort_form=BlogCategorySortForm(),
        delete_form=BlogCategoryDeleteForm(),
    )


# -----------------------------------------------------------------------------
# Edit Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route(
    "/categories/<int:category_id>/edit",
    methods=["GET", "POST"],)
@admin_required
def edit_category(category_id):
    """Edit a blog category using Blog Categories media only."""
    category = BlogCategoryService.get_by_id(category_id)

    if category is None:
        abort(404)

    form = BlogCategoryForm()

    # Load the permitted media choices before GET population and POST validation.
    form.set_media_choices()

    if request.method == "GET":
        _populate_category_form_from_model(form, category)

    if form.validate_on_submit():
        try:
            updated_category = BlogCategoryService.update_category(
                category.id,
                name=form.name.data.strip(),
                slug=form.slug.data.strip(),
                description=form.description.data,
                icon=form.icon.data,
                color=form.color.data,
                banner_image=_selected_category_banner_url(form),
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                meta_keywords=form.meta_keywords.data,
                featured=form.featured.data,
                active=form.active.data,
                sort_order=form.sort_order.data,
            )

            flash("Blog category updated successfully.", "success")

            return redirect(
                url_for(
                    "admin_blog.category_detail",
                    category_id=updated_category.id,
                )
            )

        except Exception:
            current_app.logger.exception(
                "Failed to update blog category."
            )
            db.session.rollback()
            flash(
                "The blog category could not be updated. Please try again.",
                "danger",
            )

    return render_template(
        "admin/blog/categories/edit.html",
        form=form,
        category=category,
    )

# -----------------------------------------------------------------------------
# Activate Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/activate",methods=["POST"],)
@admin_required
def activate_category(category_id):
    """
    Activate a blog category.
    """
    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:
        abort(404)

    try:
        BlogCategoryService.activate(category_id,)
        flash(
            "Blog category activated.",
            "success",
        )

    except Exception as exc:

        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.categories",))

# -----------------------------------------------------------------------------
# Deactivate Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate_category(category_id):
    """
    Deactivate a blog category.
    """
    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:
        abort(404)

    try:
        BlogCategoryService.deactivate(category_id,)
        flash("Blog category deactivated.","success",)
    except Exception as exc:

        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.categories",))

# -----------------------------------------------------------------------------
# Feature Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/feature",methods=["POST"],)
@admin_required
def feature_category(category_id):
    """
    Mark a category as featured.
    """
    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:
        abort(404)

    try:

        BlogCategoryService.feature(category_id,)
        flash("Blog category featured.","success",)

    except Exception as exc:
        flash(
            str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.categories",))

# -----------------------------------------------------------------------------
# Unfeature Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/unfeature",methods=["POST"],)
@admin_required
def unfeature_category(category_id):
    """
    Remove featured status from a category.
    """
    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:
        abort(404)

    try:
        BlogCategoryService.unfeature(category_id,)
        flash("Blog category removed from featured content.","success",)
    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_blog.categories",))

# -----------------------------------------------------------------------------
# Sort Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/sort",methods=["POST"],)
@admin_required
def sort_category(category_id):
    """
    Update category display order.
    """
    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:abort(404)
    form = BlogCategorySortForm()
    if form.validate_on_submit():
        try:
            BlogCategoryService.update_sort_order(category_id,form.sort_order.data,)

            flash("Category display order updated.","success",)

        except Exception as exc:
            flash(str(exc),"danger",)

    return redirect(request.referrer
        or url_for("admin_blog.categories",))

# -----------------------------------------------------------------------------
# Delete Category
# -----------------------------------------------------------------------------
@admin_blog_bp.route("/categories/<int:category_id>/delete",methods=["POST"],)
@admin_required
def delete_category(category_id):
    """
    Permanently delete a blog category.
    IMPORTANT
    ---------
    BlogCategory.posts uses:
        cascade="all, delete-orphan"
    Therefore, deleting a category with posts would also
    permanently delete those posts.
    For safety, deletion is blocked while posts exist.
    """

    category = BlogCategoryService.get_by_id(category_id,)
    if category is None:
        abort(404)

    # -------------------------------------------------------------------------
    # Protect posts from accidental cascade deletion
    # -------------------------------------------------------------------------
    post_count = category.post_count
    if post_count > 0:
        flash(
            (
                f"Cannot delete '{category.name}' because "
                f"it contains {post_count} blog post"
                f"{'s' if post_count != 1 else ''}. "
                "Move or delete the posts first."
            ),
            "warning",
        )

        return redirect(request.referrer
            or url_for("admin_blog.categories",))

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------
    try:
        BlogCategoryService.delete(category_id,)
        flash("Blog category permanently deleted.","success",)

    except Exception as exc:
        flash(str(exc),"danger",)

    return redirect(url_for("admin_blog.categories",))

# =============================================================================
# Error Handlers
# =============================================================================
@admin_blog_bp.errorhandler(403)
def forbidden(error):
    """
    Blog CMS authorization error.
    """
    return render_template(
        "admin/errors/403.html",), 403

@admin_blog_bp.errorhandler(404)
def not_found(error):
    """
    Blog CMS resource not found.
    """
    return render_template(
        "admin/errors/404.html",), 404
