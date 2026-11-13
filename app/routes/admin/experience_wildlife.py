"""
===============================================================================
The Uncharted Route
Admin Experience Wildlife Routes
===============================================================================

Administrative routes for managing wildlife associated with experiences.

These routes handle:

• Listing experience wildlife
• Adding wildlife to an experience
• Editing wildlife information
• Activating / deactivating wildlife associations
• Featuring / unfeaturing wildlife
• Reordering wildlife
• Deleting wildlife associations

Business logic is delegated to ExperienceWildlifeService.
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

from flask_login import (
    login_required,
)
from app.forms.admin_experience_wildlife import (
    ExperienceWildlifeForm,)
from app.models import (
    ExperienceWildlife,)
from app.services.experiences.experience_wildlife_service import (
    ExperienceWildlifeService,
)

# =============================================================================
# Blueprint
# =============================================================================
experience_wildlife_bp = Blueprint(
    "admin_experience_wildlife",
    __name__,
    url_prefix="/admin/experience-wildlife",
)

# =============================================================================
# Index
# =============================================================================
@experience_wildlife_bp.route("/")
#@login_required
def index():
    """
    Display wildlife associated with an experience.

    Optional query parameters:

    experience_id
        Filter wildlife by experience.

    status
        Filter by active/inactive status.

    featured
        Filter featured wildlife.
    """

    experience_id = request.args.get(
        "experience_id",
        type=int,
    )

    status = request.args.get(
        "status",
        "active",
    )

    featured = request.args.get(
        "featured",
    )

    query = ExperienceWildlife.query
    experience_id = request.args.get("experience_id", type=int)
    experience = None

    if experience_id:
        from app.models import Experience
        experience = Experience.query.get_or_404(experience_id)

    # -------------------------------------------------------------------------
    # Experience filter
    # -------------------------------------------------------------------------

    if experience_id:
        query = query.filter(
            ExperienceWildlife.experience_id
            == experience_id
        )

    # -------------------------------------------------------------------------
    # Status filter
    # -------------------------------------------------------------------------

    if status == "active":
        query = query.filter(
            ExperienceWildlife.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            ExperienceWildlife.active.is_(False)
        )

    # -------------------------------------------------------------------------
    # Featured filter
    # -------------------------------------------------------------------------

    if featured == "yes":
        query = query.filter(
            ExperienceWildlife.featured.is_(True)
        )

    elif featured == "no":
        query = query.filter(
            ExperienceWildlife.featured.is_(False)
        )

    wildlife = query.order_by(
        ExperienceWildlife.display_order.asc(),
        ExperienceWildlife.id.asc(),
    ).all()

    return render_template(
        "admin/experiences/experience_wildlife/index.html",
        wildlife=wildlife,
        selected_experience_id=experience_id,
        selected_status=status,
        selected_featured=featured,
        experience=experience,
    )


# =============================================================================
# Create
# =============================================================================

@experience_wildlife_bp.route(
    "/create",
    methods=["GET", "POST"],
)
#@login_required
def create():
    """
    Add a wildlife species to an experience.
    """

    form = ExperienceWildlifeForm()

    form.load_choices()

    if form.validate_on_submit():

        try:

            wildlife = ExperienceWildlifeService.add_wildlife(
                experience_id=form.experience_id.data,
                species_id=form.species_id.data,
                sighting_probability=(
                    form.sighting_probability.data
                ),
                best_season=form.best_season.data,
                best_time_of_day=(
                    form.best_time_of_day.data
                ),
                guide_notes=form.guide_notes.data,
                photography_notes=(
                    form.photography_notes.data
                ),
                featured=form.featured.data,
                display_order=(
                    form.display_order.data or 0
                ),
                active=form.active.data,
            )

            flash(
                (
                    f"{wildlife.species.common_name} "
                    "was successfully added to the experience."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_wildlife.index",
                    experience_id=wildlife.experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_wildlife/create.html",
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@experience_wildlife_bp.route(
    "/<int:wildlife_id>/edit",
    methods=["GET", "POST"],
)
#@login_required
def edit(wildlife_id):
    """
    Edit an existing experience wildlife association.
    """

    wildlife = ExperienceWildlifeService.get_by_id(
        wildlife_id
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    form = ExperienceWildlifeForm()

    form.load_choices(
        selected_experience_id=wildlife.experience_id,
        selected_species_id=wildlife.species_id,
    )

    if request.method == "GET":

        form.experience_id.data = (
            wildlife.experience_id
        )

        form.species_id.data = (
            wildlife.species_id
        )

        form.sighting_probability.data = (
            wildlife.sighting_probability
        )

        form.best_season.data = (
            wildlife.best_season
        )

        form.best_time_of_day.data = (
            wildlife.best_time_of_day
        )

        form.guide_notes.data = (
            wildlife.guide_notes
        )

        form.photography_notes.data = (
            wildlife.photography_notes
        )

        form.featured.data = (
            wildlife.featured
        )

        form.display_order.data = (
            wildlife.display_order
        )

        form.active.data = (
            wildlife.active
        )

    if form.validate_on_submit():

        try:

            updated = ExperienceWildlifeService.update(
                wildlife_id=wildlife.id,
                sighting_probability=(
                    form.sighting_probability.data
                ),
                best_season=form.best_season.data,
                best_time_of_day=(
                    form.best_time_of_day.data
                ),
                guide_notes=form.guide_notes.data,
                photography_notes=(
                    form.photography_notes.data
                ),
                featured=form.featured.data,
                display_order=(
                    form.display_order.data or 0
                ),
                active=form.active.data,
            )

            if updated is None:

                flash(
                    "Experience wildlife record not found.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "admin_experience_wildlife.index"
                    )
                )

            flash(
                "Experience wildlife information updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_wildlife.index",
                    experience_id=updated.experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_wildlife/edit.html",
        form=form,
        wildlife=wildlife,
    )


# =============================================================================
# Activate
# =============================================================================
@experience_wildlife_bp.route(
    "/<int:wildlife_id>/activate",
    methods=["POST"],
)
#@login_required
def activate(wildlife_id):
    """
    Activate an experience wildlife association.
    """

    wildlife = ExperienceWildlifeService.activate(
        wildlife_id
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    flash(
        "Wildlife association activated successfully.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_wildlife.index"
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@experience_wildlife_bp.route(
    "/<int:wildlife_id>/deactivate",
    methods=["POST"],)
#@login_required
def deactivate(wildlife_id):
    """
    Deactivate an experience wildlife association.
    """

    wildlife = ExperienceWildlifeService.deactivate(
        wildlife_id
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    flash(
        "Wildlife association deactivated successfully.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_wildlife.index"
        )
    )


# =============================================================================
# Feature
# =============================================================================
@experience_wildlife_bp.route(
    "/<int:wildlife_id>/feature",
    methods=["POST"],)
#@login_required
def feature(wildlife_id):
    """
    Mark an experience wildlife association as featured.
    """

    wildlife = ExperienceWildlifeService.set_featured(
        wildlife_id,
        featured=True,
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    flash(
        "Wildlife marked as featured.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_wildlife.index"
        )
    )


# =============================================================================
# Unfeature
# =============================================================================
@experience_wildlife_bp.route(
    "/<int:wildlife_id>/unfeature",
    methods=["POST"],)
#@login_required
def unfeature(wildlife_id):
    """
    Remove featured status from an experience wildlife association.
    """

    wildlife = ExperienceWildlifeService.set_featured(
        wildlife_id,
        featured=False,
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    flash(
        "Wildlife removed from featured status.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_experience_wildlife.index"
        )
    )


# =============================================================================
# Reorder
# =============================================================================
@experience_wildlife_bp.route("/reorder",methods=["POST"],)
#@login_required
def reorder():
    """
    Reorder wildlife associations for an experience.

    Expects form data containing:

        experience_id
        wildlife_ids[]

    where wildlife_ids are supplied in the desired display order.
    """

    experience_id = request.form.get(
        "experience_id",
        type=int,
    )

    wildlife_ids = request.form.getlist(
        "wildlife_ids[]",
        type=int,
    )

    if not experience_id:

        flash(
            "Experience is required for reordering.",
            "danger",
        )

        return redirect(
            request.referrer
            or url_for(
                "admin_experience_wildlife.index"
            )
        )

    try:

        ExperienceWildlifeService.reorder(
            experience_id=experience_id,
            wildlife_ids=wildlife_ids,
        )

        flash(
            "Wildlife display order updated successfully.",
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
            "admin_experience_wildlife.index",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@experience_wildlife_bp.route("/<int:wildlife_id>/delete",methods=["POST"],)
#@login_required
def delete(wildlife_id):
    """
    Permanently delete an experience wildlife association.
    """

    wildlife = ExperienceWildlifeService.get_by_id(
        wildlife_id
    )

    if wildlife is None:

        flash(
            "Experience wildlife record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_wildlife.index"
            )
        )

    experience_id = wildlife.experience_id

    deleted = ExperienceWildlifeService.delete(
        wildlife_id
    )

    if deleted:

        flash(
            "Wildlife association deleted successfully.",
            "success",
        )

    else:

        flash(
            "Unable to delete wildlife association.",
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_wildlife.index",
            experience_id=experience_id,
        )
    )