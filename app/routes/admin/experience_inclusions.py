"""
===============================================================================
The Uncharted Route
Admin Experience Inclusion Routes
===============================================================================

Administration routes for managing experiences inclusions.

Supported operations:

- List inclusions
- Search inclusions
- Create inclusions
- Edit inclusions
- Activate inclusions
- Deactivate inclusions
- Delete inclusions
- Reorder inclusions

All database operations are delegated to the
Experience Inclusion service layer.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.forms.admin_experience_inclusions import (
    ExperienceInclusionCreateForm,
    ExperienceInclusionEditForm,
)

from app.models import Experience
from app.services.experiences.experience_inclusion_service import (
    create_inclusion,
    delete_inclusion,
    get_experience_inclusions,
    get_inclusion,
    inclusion_belongs_to_experience,
    reorder_experience_inclusions,
    update_inclusion,
    activate_inclusion,
    deactivate_inclusion,
)

from extensions import db

# =============================================================================
# Blueprint
# =============================================================================


experience_inclusions_bp = Blueprint(
    "experience_inclusions",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Helpers
# =============================================================================


def _get_experience_or_404(experience_id):
    """
    Retrieve an experiences or return a 404 response.
    """

    experience = db.session.get(
        Experience,
        experience_id,
    )

    if experience is None:
        from flask import abort

        abort(404)

    return experience


def _get_inclusion_for_experience_or_404(
    experience_id,
    inclusion_id,
):
    """
    Retrieve an inclusion and ensure that it belongs
    to the requested experiences.
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        from flask import abort

        abort(404)

    if not inclusion_belongs_to_experience(
        inclusion_id,
        experience_id,
    ):
        from flask import abort

        abort(404)

    return inclusion


# =============================================================================
# Index
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions",
    methods=["GET"],
)
def index(experience_id):
    """
    Display all inclusions belonging to an experiences.

    Supports optional search and inactive inclusion display.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    search_query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    show_inactive = request.args.get(
        "show_inactive",
        "0",
    ) == "1"

    if search_query:

        from app.services.experiences.experience_inclusion_service import (
            search_inclusions,
        )

        inclusions = search_inclusions(
            experience_id=experience_id,
            search_term=search_query,
            active_only=not show_inactive,
        )

    else:

        inclusions = get_experience_inclusions(
            experience_id=experience_id,
            active_only=not show_inactive,
        )

    return render_template(
        "admin/experiences/experience_inclusions/index.html",
        experience=experience,
        inclusions=inclusions,
        search_query=search_query,
        show_inactive=show_inactive,
    )


# =============================================================================
# Create
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/create",
    methods=["GET", "POST"],
)
def create(experience_id):
    """
    Create a new inclusion for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceInclusionCreateForm()

    if form.validate_on_submit():

        try:

            inclusion = create_inclusion(
                experience_id=experience_id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

            flash(
                f'Inclusion "{inclusion.title}" created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "experience_inclusions.index",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_inclusions/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/<int:inclusion_id>/edit",
    methods=["GET", "POST"],
)
def edit(
    experience_id,
    inclusion_id,
):
    """
    Edit an existing inclusion.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    inclusion = _get_inclusion_for_experience_or_404(
        experience_id,
        inclusion_id,
    )

    form = ExperienceInclusionEditForm(
        obj=inclusion
    )

    if form.validate_on_submit():

        try:

            update_inclusion(
                inclusion_id,
                title=form.title.data,
                description=form.description.data,
                icon=form.icon.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

            flash(
                f'Inclusion "{inclusion.title}" updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "experience_inclusions.index",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_inclusions/edit.html",
        experience=experience,
        inclusion=inclusion,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/<int:inclusion_id>/activate",
    methods=["POST"],
)
def activate(
    experience_id,
    inclusion_id,
):
    """
    Activate an inclusion.
    """

    _get_experience_or_404(
        experience_id
    )

    inclusion = _get_inclusion_for_experience_or_404(
        experience_id,
        inclusion_id,
    )

    activate_inclusion(
        inclusion_id
    )

    flash(
        f'Inclusion "{inclusion.title}" activated.',
        "success",
    )

    return redirect(
        url_for(
            "experience_inclusions.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/<int:inclusion_id>/deactivate",
    methods=["POST"],
)
def deactivate(
    experience_id,
    inclusion_id,
):
    """
    Deactivate an inclusion.
    """

    _get_experience_or_404(
        experience_id
    )

    inclusion = _get_inclusion_for_experience_or_404(
        experience_id,
        inclusion_id,
    )

    deactivate_inclusion(
        inclusion_id
    )

    flash(
        f'Inclusion "{inclusion.title}" deactivated.',
        "success",
    )

    return redirect(
        url_for(
            "experience_inclusions.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/<int:inclusion_id>/delete",
    methods=["POST"],
)
def delete(
    experience_id,
    inclusion_id,
):
    """
    Permanently delete an inclusion.
    """

    _get_experience_or_404(
        experience_id
    )

    inclusion = _get_inclusion_for_experience_or_404(
        experience_id,
        inclusion_id,
    )

    title = inclusion.title

    if delete_inclusion(
        inclusion_id
    ):

        flash(
            f'Inclusion "{title}" deleted successfully.',
            "success",
        )

    else:

        flash(
            "The inclusion could not be deleted.",
            "danger",
        )

    return redirect(
        url_for(
            "experience_inclusions.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Reorder
# =============================================================================


@experience_inclusions_bp.route(
    "/<int:experience_id>/inclusions/reorder",
    methods=["POST"],
)
def reorder(experience_id):
    """
    Reorder inclusions belonging to an experiences.

    Expected POST data:

        inclusion_ids[]

    The IDs are supplied in their desired display order.
    """

    _get_experience_or_404(
        experience_id
    )

    inclusion_ids = request.form.getlist(
        "inclusion_ids[]"
    )

    if not inclusion_ids:
        inclusion_ids = request.form.getlist(
            "inclusion_ids"
        )

    try:

        inclusion_ids = [
            int(inclusion_id)
            for inclusion_id in inclusion_ids
        ]

    except (TypeError, ValueError):

        flash(
            "Invalid inclusion ordering data.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_inclusions.index",
                experience_id=experience_id,
            )
        )

    reorder_experience_inclusions(
        experience_id=experience_id,
        inclusion_ids=inclusion_ids,
    )

    flash(
        "Inclusion order updated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "experience_inclusions.index",
            experience_id=experience_id,
        )
    )