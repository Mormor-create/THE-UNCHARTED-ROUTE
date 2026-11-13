"""
===============================================================================
The Uncharted Route
Admin Experience Highlight Routes
===============================================================================

Administrative routes for managing highlights attached to experiences.

Supported operations
--------------------

- List highlights
- Search highlights
- Filter highlights by type
- Filter highlights by status
- Create highlights
- Edit highlights
- Activate highlights
- Deactivate highlights
- Toggle highlight status
- Feature highlights
- Unfeature highlights
- Toggle featured status
- Delete highlights
- Reorder individual highlights
- Bulk reorder highlights
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import login_required

from app.forms.admin_experience_highlights import (
    ExperienceHighlightCreateForm,
    ExperienceHighlightEditForm,
    HIGHLIGHT_TYPE_CHOICES,
)

from app.models import (
    Experience,
    ExperienceHighlight,
)

from app.services.experiences.experience_highlight_service import (
    create_highlight,
    delete_highlight,
    get_experience_highlights,
    get_highlights_by_type,
    get_highlight,
    get_highlight_count,
    search_highlights,
    update_highlight,
    activate_highlight,
    deactivate_highlight,
    feature_highlight,
    unfeature_highlight,
    reorder_highlight,
    reorder_experience_highlights,
)


# =============================================================================
# Blueprint
# =============================================================================

admin_experience_highlights = Blueprint(
    "admin_experience_highlights",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Constants
# =============================================================================

HIGHLIGHT_TYPE_VALUES = dict(
    HIGHLIGHT_TYPE_CHOICES
)


# =============================================================================
# Experience Helper
# =============================================================================

def _get_experience_or_404(experience_id):
    """
    Retrieve an experiences or return a 404 response.
    """

    return Experience.query.get_or_404(
        experience_id
    )


# =============================================================================
# Highlight Helper
# =============================================================================

def _get_highlight_for_experience(
    experience_id,
    highlight_id,
):
    """
    Retrieve a highlight and ensure it belongs to the specified experiences.
    """

    highlight = get_highlight(
        highlight_id
    )

    if (
        highlight is None
        or highlight.experience_id != experience_id
    ):
        return None

    return highlight


# =============================================================================
# Index
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights")
#@login_required
def index(experience_id):
    """
    Display highlights belonging to an experiences.

    Supports optional filtering by:

    - search
    - highlight type
    - status
    """

    experience = _get_experience_or_404(
        experience_id
    )

    search_term = request.args.get(
        "search",
        "",
    ).strip()

    highlight_type = request.args.get(
        "highlight_type",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    # -------------------------------------------------------------------------
    # Validate status
    # -------------------------------------------------------------------------

    valid_statuses = {
        "active",
        "inactive",
        "all",
    }

    if status not in valid_statuses:
        flash(
            "Invalid highlight status.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    # -------------------------------------------------------------------------
    # Validate highlight type
    # -------------------------------------------------------------------------

    if highlight_type:
        if highlight_type not in HIGHLIGHT_TYPE_VALUES:
            flash(
                "Invalid highlight type.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_experience_highlights.index",
                    experience_id=experience.id,
                )
            )

    # -------------------------------------------------------------------------
    # Retrieve highlights
    # -------------------------------------------------------------------------

    active_only = status != "all"

    if search_term:

        highlights = search_highlights(
            experience.id,
            search_term,
            active_only=active_only,
        )

    elif highlight_type:

        highlights = get_highlights_by_type(
            experience.id,
            highlight_type,
            active_only=active_only,
        )

    else:

        highlights = get_experience_highlights(
            experience.id,
            active_only=active_only,
        )

    # -------------------------------------------------------------------------
    # Status filtering
    #
    # The service methods support active_only, but when status is explicitly
    # inactive we retrieve all records and filter the inactive records here.
    # -------------------------------------------------------------------------

    if status == "inactive":

        highlights = [
            highlight
            for highlight in highlights
            if not highlight.active
        ]

    elif status == "active":

        highlights = [
            highlight
            for highlight in highlights
            if highlight.active
        ]

    # -------------------------------------------------------------------------
    # Counts
    # -------------------------------------------------------------------------

    total_count = get_highlight_count(
        experience.id,
        active_only=False,
    )

    active_count = get_highlight_count(
        experience.id,
        active_only=True,
    )

    inactive_count = (
        total_count - active_count
    )

    featured_count = sum(
        1
        for highlight in get_experience_highlights(
            experience.id,
            active_only=True,
        )
        if highlight.featured
    )

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------

    return render_template(
        "admin/experiences/experience_highlights/index.html",
        experience=experience,
        highlights=highlights,
        highlight_types=HIGHLIGHT_TYPE_CHOICES,
        selected_type=highlight_type,
        selected_status=status,
        search_term=search_term,
        total_count=total_count,
        active_count=active_count,
        inactive_count=inactive_count,
        featured_count=featured_count,
    )

# =============================================================================
# Create
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/create",methods=["GET", "POST"],)
#@login_required
def create(experience_id):
    """
    Create a new highlight for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceHighlightCreateForm()

    if form.validate_on_submit():

        try:

            highlight = create_highlight(
                experience_id=experience.id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                highlight_type=form.highlight_type.data,
                display_order=form.display_order.data or 0,
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                f'Highlight "{highlight.title}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_highlights.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_highlights/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    highlight_id,
):
    """
    Edit an existing experiences highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceHighlightEditForm(
        obj=highlight
    )

    if form.validate_on_submit():

        try:

            update_highlight(
                highlight.id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                highlight_type=form.highlight_type.data,
                display_order=form.display_order.data or 0,
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                "Highlight updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_highlights.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_highlights/edit.html",
        experience=experience,
        highlight=highlight,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/activate",methods=["POST"],)
#@login_required
def activate(
    experience_id,
    highlight_id,
):
    """
    Activate a highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    result = activate_highlight(
        highlight.id
    )

    if result is None:

        flash(
            "Highlight could not be activated.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" has been activated.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )

# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/deactivate",methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    highlight_id,
):
    """
    Deactivate a highlight without deleting it.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    result = deactivate_highlight(
        highlight.id
    )

    if result is None:

        flash(
            "Highlight could not be deactivated.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" has been deactivated.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Feature
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/feature",methods=["POST"],)
#@login_required
def feature(
    experience_id,
    highlight_id,
):
    """
    Mark a highlight as featured.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    result = feature_highlight(
        highlight.id
    )

    if result is None:

        flash(
            "Highlight could not be featured.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" is now featured.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Unfeature
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/unfeature",methods=["POST"],)
#@login_required
def unfeature(
    experience_id,
    highlight_id,
):
    """
    Remove the featured status from a highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    result = unfeature_highlight(
        highlight.id
    )

    if result is None:

        flash(
            "Highlight could not be unfeatured.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" is no longer featured.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Toggle Featured
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/toggle-featured",methods=["POST"],)
#@login_required
def toggle_featured(
    experience_id,
    highlight_id,
):
    """
    Toggle the featured state of a highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    if highlight.featured:

        result = unfeature_highlight(
            highlight.id
        )

        action = "removed from featured highlights"

    else:

        result = feature_highlight(
            highlight.id
        )

        action = "marked as featured"

    if result is None:

        flash(
            "Highlight status could not be updated.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" has been {action}.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Toggle Active
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/toggle",methods=["POST"],)
#@login_required
def toggle(
    experience_id,
    highlight_id,
):
    """
    Toggle the active state of a highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    if highlight.active:

        result = deactivate_highlight(
            highlight.id
        )

        action = "deactivated"

    else:

        result = activate_highlight(
            highlight.id
        )

        action = "activated"

    if result is None:

        flash(
            "Highlight status could not be updated.",
            "danger",
        )

    else:

        flash(
            f'Highlight "{highlight.title}" has been {action}.',
            "success",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/delete",methods=["POST"],)
#@login_required
def delete(
    experience_id,
    highlight_id,
):
    """
    Permanently delete a highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    highlight_title = highlight.title

    result = delete_highlight(
        highlight.id
    )

    if result:

        flash(
            f'Highlight "{highlight_title}" was deleted.',
            "success",
        )

    else:

        flash(
            "Highlight could not be deleted.",
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Reorder Single Highlight
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/<int:highlight_id>/reorder",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    highlight_id,
):
    """
    Change the display order of a single highlight.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight = _get_highlight_for_experience(
        experience.id,
        highlight_id,
    )

    if highlight is None:

        flash(
            "Highlight not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    try:

        display_order = int(
            request.form.get(
                "display_order",
                0,
            )
        )

        if display_order < 0:
            raise ValueError(
                "Display order cannot be negative."
            )

        result = reorder_highlight(
            highlight.id,
            display_order,
        )

        if result is None:
            raise ValueError(
                "Highlight could not be reordered."
            )

        flash(
            "Highlight order updated successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Bulk Reorder
# =============================================================================
@admin_experience_highlights.route("/<int:experience_id>/highlights/reorder",methods=["POST"],)
#@login_required
def reorder_bulk(experience_id):
    """
    Reorder multiple highlights.

    Expected form input:

        highlight_ids[]

    containing highlight IDs in their desired order.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    highlight_ids = request.form.getlist(
        "highlight_ids[]"
    )

    if not highlight_ids:

        highlight_ids = request.form.getlist(
            "highlight_ids"
        )

    if not highlight_ids:

        flash(
            "No highlight order was submitted.",
            "warning",
        )

        return redirect(
            url_for(
                "admin_experience_highlights.index",
                experience_id=experience.id,
            )
        )

    try:

        ordered_highlight_ids = [
            int(highlight_id)
            for highlight_id in highlight_ids
        ]

        reorder_experience_highlights(
            experience.id,
            ordered_highlight_ids,
        )

        flash(
            "Highlights reordered successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_highlights.index",
            experience_id=experience.id,
        )
    )