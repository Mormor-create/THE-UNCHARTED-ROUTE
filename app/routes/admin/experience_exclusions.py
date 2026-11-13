"""
===============================================================================
The Uncharted Route
Admin Experience Exclusion Routes
===============================================================================

Administrative routes for managing experiences exclusions.

Responsibilities:

- List exclusions belonging to an experiences
- Search exclusions
- Create exclusions
- Edit exclusions
- Activate / deactivate exclusions
- Delete exclusions

All database manipulation is delegated to the
Experience Exclusion service layer.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    login_required,
)

from app.forms.admin_experience_exclusions import (
    ExperienceExclusionCreateForm,
    ExperienceExclusionEditForm,
)
from app.models import Experience

from app.services.experiences.experience_exclusion_service import (
    create_exclusion,
    delete_exclusion,
    exclusion_belongs_to_experience,
    get_exclusion,
    get_experience_exclusions,
    search_exclusions,
    update_exclusion,
    activate_exclusion,
    deactivate_exclusion,
)


# =============================================================================
# Blueprint
# =============================================================================

experience_exclusions_bp = Blueprint(
    "experience_exclusions",
    __name__,
    url_prefix="/admin/experiences",
)

# =============================================================================
# Index
# =============================================================================

@experience_exclusions_bp.route(
    "/<int:experience_id>/exclusions",
    methods=["GET"],
)
# @login_required
def index(experience_id):
    """
    Display all exclusions belonging to an experience.

    Supports optional searching through the query string:
        ?q=park

    Inactive exclusions can also be displayed using:
        ?show_inactive=1
    """

    # -------------------------------------------------------------------------
    # Retrieve the parent experience
    # -------------------------------------------------------------------------
    # Ensure Experience is imported from your existing models module.
    experience = Experience.query.get_or_404(experience_id)

    # -------------------------------------------------------------------------
    # Read search and filter parameters
    # -------------------------------------------------------------------------
    search_query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    show_inactive = request.args.get(
        "show_inactive",
        "0",
    ) == "1"

    active_only = not show_inactive

    # -------------------------------------------------------------------------
    # Retrieve exclusions
    # -------------------------------------------------------------------------
    if search_query:
        exclusions = search_exclusions(
            experience_id=experience_id,
            search_term=search_query,
            active_only=active_only,
        )
    else:
        exclusions = get_experience_exclusions(
            experience_id=experience_id,
            active_only=active_only,
        )

    # -------------------------------------------------------------------------
    # Render template
    # -------------------------------------------------------------------------
    return render_template(
        "admin/experiences/experience_exclusion/index.html",
        experience=experience,
        experience_id=experience_id,
        exclusions=exclusions,
        search_query=search_query,
        show_inactive=show_inactive,
    )

# =============================================================================
# Create
# =============================================================================
@experience_exclusions_bp.route(
    "/<int:experience_id>/exclusions/create",
    methods=["GET", "POST"],
)
#@login_required
def create(experience_id):
    """
    Create a new exclusion for an experiences.
    """

    form = ExperienceExclusionCreateForm()

    if form.validate_on_submit():

        try:
            exclusion = create_exclusion(
                experience_id=experience_id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                display_order=form.display_order.data or 0,
                active=form.active.data,
            )

            flash(
                f'Exclusion "{exclusion.title}" created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "experience_exclusions.index",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_exclusion/create.html",
        form=form,
        experience_id=experience_id,
    )


# =============================================================================
# Edit
# =============================================================================
@experience_exclusions_bp.route(
    "/<int:experience_id>/exclusions/<int:exclusion_id>/edit",
    methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    exclusion_id,
):
    """
    Edit an existing exclusion.

    The exclusion must belong to the supplied experiences.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        flash(
            "Experience exclusion not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    if not exclusion_belongs_to_experience(
        exclusion_id=exclusion_id,
        experience_id=experience_id,
    ):
        flash(
            "This exclusion does not belong to the selected experiences.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    form = ExperienceExclusionEditForm(
        obj=exclusion
    )

    if form.validate_on_submit():

        try:
            update_exclusion(
                exclusion_id=exclusion.id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                display_order=form.display_order.data or 0,
                active=form.active.data,
            )

            flash(
                f'Exclusion "{exclusion.title}" updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "experience_exclusions.index",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_exclusion/edit.html",
        form=form,
        exclusion=exclusion,
        experience_id=experience_id,
    )


# =============================================================================
# Activate
# =============================================================================
@experience_exclusions_bp.route("/<int:experience_id>/exclusions/<int:exclusion_id>/activate",methods=["POST"],)
#@login_required
def activate(
    experience_id,
    exclusion_id,
):
    """
    Activate an exclusion.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        flash(
            "Experience exclusion not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    if not exclusion_belongs_to_experience(
        exclusion_id=exclusion_id,
        experience_id=experience_id,
    ):
        flash(
            "This exclusion does not belong to the selected experiences.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    try:
        activate_exclusion(
            exclusion_id
        )

        flash(
            f'Exclusion "{exclusion.title}" activated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_exclusions.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@experience_exclusions_bp.route("/<int:experience_id>/exclusions/<int:exclusion_id>/deactivate",methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    exclusion_id,
):
    """
    Deactivate an exclusion.

    The record remains in the database.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        flash(
            "Experience exclusion not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    if not exclusion_belongs_to_experience(
        exclusion_id=exclusion_id,
        experience_id=experience_id,
    ):
        flash(
            "This exclusion does not belong to the selected experiences.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    try:
        deactivate_exclusion(
            exclusion_id
        )

        flash(
            f'Exclusion "{exclusion.title}" deactivated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_exclusions.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@experience_exclusions_bp.route("/<int:experience_id>/exclusions/<int:exclusion_id>/delete",methods=["POST"],)
#@login_required
def delete(
    experience_id,
    exclusion_id,
):
    """
    Permanently delete an exclusion.

    The exclusion must belong to the supplied experiences.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        flash(
            "Experience exclusion not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    if not exclusion_belongs_to_experience(
        exclusion_id=exclusion_id,
        experience_id=experience_id,
    ):
        flash(
            "This exclusion does not belong to the selected experiences.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_exclusions.index",
                experience_id=experience_id,
            )
        )

    exclusion_title = exclusion.title

    try:
        deleted = delete_exclusion(
            exclusion_id
        )

        if deleted:
            flash(
                f'Exclusion "{exclusion_title}" deleted successfully.',
                "success",
            )
        else:
            flash(
                "The exclusion could not be deleted.",
                "danger",
            )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_exclusions.index",
            experience_id=experience_id,
        )
    )