"""
===============================================================================
The Uncharted Route
Admin Experience Photography Routes
===============================================================================

Administrative routes for managing photography spots associated with
experiences.

Supported operations
--------------------

• List photography spots attached to an experiences
• Add a photography spot to an experiences
• Edit an experiences photography association
• Activate / deactivate a photography stop
• Feature / unfeature a photography stop
• Delete an association
• Reorder photography stops
• Bulk reorder photography stops
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

from app.forms.admin_experience_photography import (
    ExperiencePhotographyCreateForm,
    ExperiencePhotographyEditForm,
    ExperiencePhotographyReorderForm,
)

from app.models import (
    Experience,
    ExperiencePhotography,
    PhotographySpot,
)

from extensions import db


# =============================================================================
# Blueprint
# =============================================================================

admin_experience_photography = Blueprint(
    "admin_experience_photography",
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

    return Experience.query.get_or_404(
        experience_id
    )

def _get_association_or_404(
    experience_id,
    association_id,
):
    """
    Retrieve an experiences photography association belonging
    to the specified experiences.
    """

    return ExperiencePhotography.query.filter_by(
        id=association_id,
        experience_id=experience_id,
    ).first_or_404()


def _get_available_photography_spots(
    experience_id,
):
    """
    Retrieve photography spots that are not already associated
    with the experiences.

    This prevents the same PhotographySpot from being attached
    to the same experiences more than once through the admin UI.
    """

    existing_ids = {
        association.photography_spot_id
        for association in ExperiencePhotography.query.filter_by(
            experience_id=experience_id
        ).all()
    }

    query = PhotographySpot.query

    if existing_ids:
        query = query.filter(
            ~PhotographySpot.id.in_(existing_ids)
        )

    return query.order_by(
        PhotographySpot.name.asc()
    ).all()

def _populate_spot_choices(
    form,
    experience_id,
    include_spot_id=None,
):
    """
    Populate the photography spot select field.

    During editing, the currently selected photography spot is included
    even though it is already attached to the experiences.
    """

    spots = _get_available_photography_spots(
        experience_id
    )

    if include_spot_id is not None:
        current_spot = db.session.get(
            PhotographySpot,
            include_spot_id,
        )

        if current_spot is not None:
            spots.append(current_spot)

    spots = sorted(
        {
            spot.id: spot
            for spot in spots
        }.values(),
        key=lambda spot: spot.name.lower(),
    )

    form.photography_spot_id.choices = [
        (
            spot.id,
            spot.name,
        )
        for spot in spots
    ]


# =============================================================================
# Index
# =============================================================================

@admin_experience_photography.route(
    "/<int:experience_id>/photography",
)
#@login_required
def index(experience_id):
    """
    Display photography spots associated with an experiences.

    Supports optional filtering by status.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    status = request.args.get(
        "status",
        "active",
    ).strip().lower()

    if status not in {
        "active",
        "inactive",
        "all",
    }:
        flash(
            "Invalid photography status filter.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_photography.index",
                experience_id=experience.id,
            )
        )

    query = ExperiencePhotography.query.filter_by(
        experience_id=experience.id
    )

    if status == "active":
        query = query.filter_by(
            active=True
        )

    elif status == "inactive":
        query = query.filter_by(
            active=False
        )

    associations = query.order_by(
        ExperiencePhotography.stop_order.asc(),
        ExperiencePhotography.id.asc(),
    ).all()

    total_count = ExperiencePhotography.query.filter_by(
        experience_id=experience.id
    ).count()

    active_count = ExperiencePhotography.query.filter_by(
        experience_id=experience.id,
        active=True,
    ).count()

    inactive_count = (
        total_count - active_count
    )

    featured_count = ExperiencePhotography.query.filter_by(
        experience_id=experience.id,
        featured=True,
        active=True,
    ).count()

    return render_template(
        "admin/experiences/experience_photography/index.html",
        experience=experience,
        associations=associations,
        photography_items=associations,
        selected_status=status,
        total_count=total_count,
        active_count=active_count,
        inactive_count=inactive_count,
        featured_count=featured_count,
    )


# =============================================================================
# Create
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/create",
    methods=["GET", "POST"],
)
#@login_required
def create(experience_id):
    """
    Add a photography spot to an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperiencePhotographyCreateForm()

    _populate_spot_choices(
        form,
        experience.id,
    )

    if form.validate_on_submit():

        photography_spot = db.session.get(
            PhotographySpot,
            form.photography_spot_id.data,
        )

        if photography_spot is None:
            flash(
                "Photography spot not found.",
                "danger",
            )

        else:

            existing = ExperiencePhotography.query.filter_by(
                experience_id=experience.id,
                photography_spot_id=photography_spot.id,
            ).first()

            if existing:
                flash(
                    "This photography spot is already attached "
                    "to this experiences.",
                    "warning",
                )

                return redirect(
                    url_for(
                        "admin_experience_photography.index",
                        experience_id=experience.id,
                    )
                )

            association = ExperiencePhotography(
                experience_id=experience.id,
                photography_spot_id=photography_spot.id,
                stop_order=form.stop_order.data,
                featured=form.featured.data,
                active=form.active.data,
                notes=form.notes.data.strip()
                if form.notes.data
                else None,
            )

            db.session.add(
                association
            )

            db.session.commit()

            flash(
                f'Photography spot "{photography_spot.name}" '
                "was added successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_photography.index",
                    experience_id=experience.id,
                )
            )

    return render_template(
        "admin/experiences/experience_photography/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================

@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/edit",
    methods=["GET", "POST"],
)
#@login_required
def edit(
    experience_id,
    association_id,
):
    """
    Edit an existing experiences photography association.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    form = ExperiencePhotographyEditForm(
        obj=association
    )

    if request.method == "GET":
        form.stop_order.data = association.stop_order
        form.featured.data = association.featured
        form.active.data = association.active
        form.notes.data = association.notes

    if form.validate_on_submit():

        association.stop_order = (
            form.stop_order.data
        )

        association.featured = (
            form.featured.data
        )

        association.active = (
            form.active.data
        )

        association.notes = (
            form.notes.data.strip()
            if form.notes.data
            else None
        )

        db.session.commit()

        flash(
            "Photography association updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_experience_photography.index",
                experience_id=experience.id,
            )
        )

    return render_template(
        "admin/experiences/experience_photography/edit.html",
        experience=experience,
        association=association,
        photography=association,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/activate",
    methods=["POST"],
)
#@login_required
def activate(
    experience_id,
    association_id,
):
    """
    Activate a photography stop.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    association.active = True

    db.session.commit()

    flash(
        f'"{association.spot.name}" has been activated.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/deactivate",
    methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    association_id,
):
    """
    Deactivate a photography stop without deleting it.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    association.active = False

    db.session.commit()

    flash(
        f'"{association.spot.name}" has been deactivated.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Toggle Status
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/toggle",
    methods=["POST"],)
#@login_required
def toggle(
    experience_id,
    association_id,
):
    """
    Toggle the active status of a photography stop.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    association.active = not association.active

    db.session.commit()

    state = (
        "activated"
        if association.active
        else "deactivated"
    )

    flash(
        f'"{association.spot.name}" has been {state}.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Feature
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/feature",
    methods=["POST"],
)
#@login_required
def feature(
    experience_id,
    association_id,
):
    """
    Mark a photography stop as featured.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    association.featured = True

    db.session.commit()

    flash(
        f'"{association.spot.name}" has been featured.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )

# =============================================================================
# Unfeature
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/unfeature",
    methods=["POST"],
)
#@login_required
def unfeature(
    experience_id,
    association_id,
):
    """
    Remove the featured status from a photography stop.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    association.featured = False

    db.session.commit()

    flash(
        f'"{association.spot.name}" is no longer featured.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Reorder Single
# =============================================================================
@admin_experience_photography.route("/<int:experience_id>/photography/<int:association_id>/reorder",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    association_id,
):
    """
    Change the display order of a single photography stop.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    form = ExperiencePhotographyReorderForm()

    if form.validate_on_submit():

        association.stop_order = (
            form.stop_order.data
        )

        db.session.commit()

        flash(
            "Photography stop order updated successfully.",
            "success",
        )

    else:

        for field_errors in form.errors.values():
            for error in field_errors:
                flash(
                    error,
                    "danger",
                )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Bulk Reorder
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/reorder",
    methods=["POST"],)
#@login_required
def reorder_bulk(experience_id):
    """
    Reorder multiple photography stops.

    Expected form input:

        association_ids[]

    containing association IDs in their desired order.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association_ids = request.form.getlist(
        "association_ids[]"
    )

    if not association_ids:
        association_ids = request.form.getlist(
            "association_ids"
        )

    try:

        ordered_ids = [
            int(association_id)
            for association_id in association_ids
        ]

    except (TypeError, ValueError):

        flash(
            "Invalid photography stop order.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_photography.index",
                experience_id=experience.id,
            )
        )

    associations = ExperiencePhotography.query.filter(
        ExperiencePhotography.experience_id == experience.id,
        ExperiencePhotography.id.in_(ordered_ids),
    ).all()

    associations_by_id = {
        association.id: association
        for association in associations
    }

    for position, association_id in enumerate(
        ordered_ids
    ):

        association = associations_by_id.get(
            association_id
        )

        if association:
            association.stop_order = position

    db.session.commit()

    flash(
        "Photography stops reordered successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_experience_photography.route(
    "/<int:experience_id>/photography/<int:association_id>/delete",
    methods=["POST"],
)
#@login_required
def delete(
    experience_id,
    association_id,
):
    """
    Permanently remove a photography spot from an experiences.

    This deletes only the association. The underlying PhotographySpot
    remains available for other experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    association = _get_association_or_404(
        experience.id,
        association_id,
    )

    spot_name = association.spot.name

    db.session.delete(
        association
    )

    db.session.commit()

    flash(
        f'"{spot_name}" was removed from this experiences.',
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_photography.index",
            experience_id=experience.id,
        )
    )