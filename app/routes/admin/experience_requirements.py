"""
===============================================================================
The Uncharted Route
Admin Experience Requirement Routes
===============================================================================

Administrative routes for managing participation requirements attached to
experiences.

Supported operations
--------------------

- List requirements
- Create requirements
- Edit requirements
- Activate requirements
- Deactivate requirements
- Mark requirements as mandatory
- Mark requirements as optional
- Delete requirements
- Reorder requirements
- Bulk reorder requirements
- Filter requirements by status
- Filter requirements by mandatory/optional status
===============================================================================
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

from app.forms.admin_experience_requirements import (
    ExperienceRequirementCreateForm,
    ExperienceRequirementEditForm,
    REQUIREMENT_CATEGORY_CHOICES,
)

from app.models import (
    Experience,
    ExperienceRequirement,
)

from app.services.experiences.experience_requirement_service import (
    ExperienceRequirementService,
)


# =============================================================================
# Blueprint
# =============================================================================
admin_experience_requirements = Blueprint(
    "admin_experience_requirements",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Service
# =============================================================================

requirement_service = ExperienceRequirementService


# =============================================================================
# Constants
# =============================================================================
REQUIREMENT_CATEGORIES = dict(
    REQUIREMENT_CATEGORY_CHOICES
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
# Requirement Helper
# =============================================================================

def _get_requirement_for_experience_or_none(
    experience_id,
    requirement_id,
):
    """
    Retrieve a requirement and ensure that it belongs to the requested
    experiences.
    """

    requirement = requirement_service.get_requirement(
        requirement_id
    )

    if requirement is None:
        return None

    if requirement.experience_id != experience_id:
        return None

    return requirement


# =============================================================================
# Index
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements")
#@login_required
def index(experience_id):
    """
    Display all participation requirements belonging to an experiences.

    Supports optional filtering by:

    - status
    - mandatory / optional
    - category
    """

    experience = _get_experience_or_404(
        experience_id
    )

    status = request.args.get(
        "status",
        "active",
    ).strip().lower()

    requirement_type = request.args.get(
        "type",
        "all",
    ).strip().lower()

    category = request.args.get(
        "category",
        "",
    ).strip()

    # -------------------------------------------------------------------------
    # Retrieve requirements
    # -------------------------------------------------------------------------

    requirements = requirement_service.get_experience_requirements(
        experience.id,
        active_only=False,
        mandatory_only=False,
    )

    # -------------------------------------------------------------------------
    # Status filtering
    # -------------------------------------------------------------------------

    if status == "active":

        requirements = [
            requirement
            for requirement in requirements
            if requirement.active
        ]

    elif status == "inactive":

        requirements = [
            requirement
            for requirement in requirements
            if not requirement.active
        ]

    elif status != "all":

        flash(
            "Invalid requirement status filter.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    # -------------------------------------------------------------------------
    # Mandatory / Optional filtering
    # -------------------------------------------------------------------------

    if requirement_type == "mandatory":

        requirements = [
            requirement
            for requirement in requirements
            if requirement.mandatory
        ]

    elif requirement_type == "optional":

        requirements = [
            requirement
            for requirement in requirements
            if not requirement.mandatory
        ]

    elif requirement_type != "all":

        flash(
            "Invalid requirement type filter.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    # -------------------------------------------------------------------------
    # Category filtering
    # -------------------------------------------------------------------------

    if category:

        if category not in REQUIREMENT_CATEGORIES:

            flash(
                "Invalid requirement category.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_experience_requirements.index",
                    experience_id=experience.id,
                )
            )

        requirements = [
            requirement
            for requirement in requirements
            if requirement.category == category
        ]

    # -------------------------------------------------------------------------
    # Counts
    # -------------------------------------------------------------------------

    total_count = requirement_service.count_requirements(
        experience.id,
        active_only=False,
    )

    active_count = requirement_service.count_requirements(
        experience.id,
        active_only=True,
    )

    mandatory_count = (
        requirement_service.count_mandatory_requirements(
            experience.id
        )
    )

    inactive_count = (
        total_count - active_count
    )

    optional_count = (
        active_count - mandatory_count
    )

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------

    return render_template(
        "admin/experiences/experience_requirements/index.html",
        experience=experience,
        requirements=requirements,
        categories=REQUIREMENT_CATEGORY_CHOICES,
        selected_status=status,
        selected_type=requirement_type,
        selected_category=category,
        total_count=total_count,
        active_count=active_count,
        inactive_count=inactive_count,
        mandatory_count=mandatory_count,
        optional_count=optional_count,
    )


# =============================================================================
# Create
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/create",methods=["GET", "POST"],)
#@login_required
def create(experience_id):
    """
    Create a new participation requirement for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceRequirementCreateForm()

    if form.validate_on_submit():

        try:

            requirement = (
                requirement_service.create_requirement(
                    experience_id=experience.id,
                    title=form.title.data,
                    description=form.description.data,
                    category=form.category.data,
                    mandatory=form.mandatory.data,
                    icon=form.icon.data,
                    display_order=form.display_order.data,
                    active=form.active.data,
                )
            )

            flash(
                (
                    f'Requirement "{requirement.title}" '
                    "was created successfully."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_requirements.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_requirements/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    requirement_id,
):
    """
    Edit an existing participation requirement.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceRequirementEditForm(
        obj=requirement
    )

    if form.validate_on_submit():

        try:

            requirement_service.update_requirement(
                requirement_id=requirement.id,
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                mandatory=form.mandatory.data,
                icon=form.icon.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

            flash(
                "Requirement updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_requirements.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_requirements/edit.html",
        experience=experience,
        requirement=requirement,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/activate",methods=["POST"],)
#@]login_required
def activate(
    experience_id,
    requirement_id,
):
    """
    Activate a participation requirement.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    try:

        requirement_service.activate_requirement(
            requirement.id
        )

        flash(
            (
                f'Requirement "{requirement.title}" '
                "has been activated."
            ),
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/deactivate",methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    requirement_id,
):
    """
    Deactivate a participation requirement without deleting it.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    try:

        requirement_service.deactivate_requirement(
            requirement.id
        )

        flash(
            (
                f'Requirement "{requirement.title}" '
                "has been deactivated."
            ),
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Make Mandatory
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/mandatory",methods=["POST"],)
#@login_required
def make_mandatory(
    experience_id,
    requirement_id,
):
    """
    Mark a requirement as mandatory.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    try:

        requirement_service.make_mandatory(
            requirement.id
        )

        flash(
            (
                f'Requirement "{requirement.title}" '
                "is now mandatory."
            ),
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Make Optional
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/optional",methods=["POST"],)
#@login_required
def make_optional(
    experience_id,
    requirement_id,
):
    """
    Mark a requirement as optional.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    try:

        requirement_service.make_optional(
            requirement.id
        )

        flash(
            (
                f'Requirement "{requirement.title}" '
                "is now optional."
            ),
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Reorder Single Requirement
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/<int:requirement_id>/reorder",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    requirement_id,
):
    """
    Change the display order of a single requirement.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
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

        requirement_service.reorder_requirement(
            requirement.id,
            display_order,
        )

        flash(
            "Requirement order updated successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Bulk Reorder
# =============================================================================
@admin_experience_requirements.route("/<int:experience_id>/requirements/reorder",methods=["POST"],)
#@login_required
def reorder_bulk(experience_id):
    """
    Reorder multiple requirements.
    Expected form input:
        requirement_ids[]
    containing requirement IDs in their desired order.
    """

    experience = _get_experience_or_404(
        experience_id
    )
    requirement_ids = request.form.getlist(
        "requirement_ids[]"
    )

    if not requirement_ids:

        requirement_ids = request.form.getlist(
            "requirement_ids"
        )

    try:

        ordered_ids = [
            int(requirement_id)
            for requirement_id in requirement_ids
        ]

        requirement_orders = {
            requirement_id: position
            for position, requirement_id
            in enumerate(ordered_ids)
        }

        requirement_service.bulk_reorder(
            requirement_orders
        )

        flash(
            "Requirements reordered successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_experience_requirements.route(
    "/<int:experience_id>/requirements/<int:requirement_id>/delete",
    methods=["POST"],
)
#@login_required
def delete(
    experience_id,
    requirement_id,
):
    """
    Permanently delete a participation requirement.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    requirement = (
        _get_requirement_for_experience_or_none(
            experience.id,
            requirement_id,
        )
    )

    if requirement is None:

        flash(
            "Requirement not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_requirements.index",
                experience_id=experience.id,
            )
        )

    requirement_title = requirement.title

    try:

        requirement_service.delete_requirement(
            requirement.id
        )

        flash(
            (
                f'Requirement "{requirement_title}" '
                "was deleted successfully."
            ),
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_requirements.index",
            experience_id=experience.id,
        )
    )