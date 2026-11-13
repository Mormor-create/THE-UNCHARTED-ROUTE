"""
===============================================================================
The Uncharted Route
Admin Experience Tag Routes
===============================================================================

Administrative routes for managing experiences tags.

Responsibilities
----------------

• List experiences tags
• Search experiences tags
• Create experiences tags
• Edit experiences tags
• Activate / deactivate tags
• Feature / unfeature tags
• Reorder tags
• Delete tags

Business logic is delegated to the experiences tag service so that route
handlers remain responsible primarily for HTTP concerns, permissions,
forms, redirects, and user feedback.
===============================================================================
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,)
from flask_login import (
    login_required,)

from app.decorators.admin import admin_required
from app.forms.admin_experience_tags import (
    ExperienceTagForm,)
from app.services.experiences.experience_tag_service import (
    create_tag,
    get_tag,
    get_all_tags,
    search_tags,
    update_tag,
    activate_tag,
    deactivate_tag,
    feature_tag,
    unfeature_tag,
    reorder_tag,
    delete_tag,
)


# =============================================================================
# Blueprint
# =============================================================================
admin_experience_tags_bp = Blueprint(
    "admin_experience_tags",
    __name__,
    url_prefix="/admin/experiences-tags",)

@admin_experience_tags_bp.route("/")
@admin_required
@login_required
def index():
    search_term = request.args.get("q", "", type=str).strip()
    active_filter = request.args.get("active", "", type=str).strip().lower()

    if search_term:
        tags = search_tags(search_term, active_only=False)
    else:
        tags = get_all_tags(active_only=False)

    if active_filter == "active":
        tags = [tag for tag in tags if tag.active]
    elif active_filter == "inactive":
        tags = [tag for tag in tags if not tag.active]

    experience_id = request.args.get("experience_id", type=int)
    experience = None

    if experience_id:
        from app.models import Experience
        experience = Experience.query.get_or_404(experience_id)

    return render_template(
        "admin/experiences/experience_tags/index.html",
        tags=tags,
        search_term=search_term,
        active_filter=active_filter,
        experience=experience,
    )

# =============================================================================
# Create
# =============================================================================
@admin_experience_tags_bp.route("/create",methods=["GET", "POST"],)
@admin_required
@login_required
def create():
    """
    Create a new experiences tag.
    """

    form = ExperienceTagForm()

    if form.validate_on_submit():

        data = {
            "name": form.name.data,
            "slug": form.slug.data,
            "description": form.description.data,
            "color": form.color.data,
            "icon": form.icon.data,
            "featured": form.featured.data,
            "meta_title": form.meta_title.data,
            "meta_description": form.meta_description.data,
            "active": form.active.data,
            "sort_order": form.sort_order.data,
        }

        try:
            tag = create_tag(data)

            flash(
                f'Experience tag "{tag.name}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_tags.index"
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_tags/create.html",
        form=form,)

# =============================================================================
# Edit
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/edit",methods=["GET", "POST"],)
@admin_required
@login_required
def edit(tag_id):
    """
    Edit an existing experiences tag.
    """

    tag = get_tag(tag_id)

    if tag is None:
        flash(
            "Experience tag not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_tags.index"
            )
        )

    form = ExperienceTagForm(
        obj=tag
    )

    if form.validate_on_submit():

        data = {
            "name": form.name.data,
            "slug": form.slug.data,
            "description": form.description.data,
            "color": form.color.data,
            "icon": form.icon.data,
            "featured": form.featured.data,
            "meta_title": form.meta_title.data,
            "meta_description": form.meta_description.data,
            "active": form.active.data,
            "sort_order": form.sort_order.data,
        }

        try:
            update_tag(
                tag_id,
                data,
            )

            flash(
                f'Experience tag "{tag.name}" was updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_tags.index"
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_tags/edit.html",
        form=form,
        tag=tag,)

# =============================================================================
# Activate
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/activate",methods=["POST"],)
@admin_required
@login_required
def activate(tag_id):
    """
    Activate an experiences tag.
    """

    try:
        tag = activate_tag(tag_id)

        flash(
            f'Experience tag "{tag.name}" was activated.',
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_tags.index"))


# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/deactivate",methods=["POST"],)
@admin_required
@login_required
def deactivate(tag_id):
    """
    Deactivate an experiences tag.
    """

    try:
        tag = deactivate_tag(tag_id)

        flash(
            f'Experience tag "{tag.name}" was deactivated.',
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_experience_tags.index"))

# =============================================================================
# Feature
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/feature",methods=["POST"],)
@admin_required
@login_required
def feature(tag_id):
    """
    Mark an experiences tag as featured.
    """
    try:
        tag = feature_tag(tag_id)
        flash(f'Experience tag "{tag.name}" is now featured.',"success",)
    except ValueError as exc:
        flash(
            str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_experience_tags.index"))

# =============================================================================
# Unfeature
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/unfeature",methods=["POST"],)
@admin_required
@login_required
def unfeature(tag_id):
    """
    Remove a tag from featured status.
    """

    try:
        tag = unfeature_tag(tag_id)

        flash(
            f'Experience tag "{tag.name}" was removed from featured tags.',
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_tags.index"
        )
    )


# =============================================================================
# Reorder
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/reorder",methods=["POST"],)
@admin_required
@login_required
def reorder(tag_id):
    """
    Change the display order of an experiences tag.
    """
    sort_order = request.form.get(
        "sort_order",
        type=int,)

    if sort_order is None:
        flash(
            "A valid sort order is required.","danger",)

        return redirect(
            request.referrer
            or url_for("admin_experience_tags.index"))

    try:
        tag = reorder_tag(
            tag_id,
            sort_order,)

        flash(f'Experience tag "{tag.name}" was reordered successfully.',"success",)

    except ValueError as exc:
        flash(
            str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_experience_tags.index"))

# =============================================================================
# Delete
# =============================================================================
@admin_experience_tags_bp.route("/<int:tag_id>/delete",methods=["POST"],)
@admin_required
@login_required
def delete(tag_id):
    """
    Permanently delete an experiences tag.
    """

    tag = get_tag(tag_id)

    if tag is None:
        flash("Experience tag not found.","danger",)
        return redirect(
            url_for("admin_experience_tags.index"))
    tag_name = tag.name

    try:
        delete_tag(tag_id)
        flash(f'Experience tag "{tag_name}" was deleted successfully.',"success",)

    except ValueError as exc:
        flash(
            str(exc),
            "danger",)

    return redirect(
        url_for("admin_experience_tags.index"))