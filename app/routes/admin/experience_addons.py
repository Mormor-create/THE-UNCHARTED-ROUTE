"""
===============================================================================
The Uncharted Route
Admin Experience Add-on Routes
===============================================================================

Administrative routes for managing optional add-ons attached to experiences.

Supported operations:

- List experience add-ons
- Create add-ons
- Edit add-ons
- Activate / deactivate add-ons
- Toggle online availability
- Delete add-ons
- Reorder add-ons

Business logic is delegated to ExperienceAddonService.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import login_required
from app.forms.admin_experience_addons import (
    ExperienceAddonCreateForm,
    ExperienceAddonEditForm,)
from app.services.experiences.experience_addon_service import (
    ExperienceAddonService,)

# =============================================================================
# Experience Add-ons Blueprint
# =============================================================================
experience_addons_bp = Blueprint(
    "experience_addons",
    __name__,
    url_prefix="/admin",
)

# =============================================================================
# Service
# =============================================================================
addon_service = ExperienceAddonService()

# =============================================================================
# Add-on Listing
# =============================================================================
@experience_addons_bp.route("/experiences/<int:experience_id>/addons",methods=["GET"],)
# @login_required
def experience_addons(experience_id):
    """Display all add-ons belonging to an experience."""

    from app.models import Experience

    experience = Experience.query.get_or_404(experience_id)

    addons = addon_service.get_all_addons(
        experience_id=experience.id,
        active_only=False,
    )

    return render_template(
        "admin/experiences/experience_addons/index.html",
        experience_id=experience.id,
        experience=experience,
        addons=addons,
    )

# =============================================================================
# Create Add-on
# =============================================================================
@experience_addons_bp.route("/experiences/<int:experience_id>/addons/create",methods=["GET", "POST"],)
#@login_required
def create_experience_addon(experience_id):
    """
    Create a new add-on for an experience.
    """

    form = ExperienceAddonCreateForm()

    if form.validate_on_submit():

        try:

            addon_service.create_addon(
                experience_id=experience_id,
                name=form.name.data,
                price=form.price.data,
                short_description=form.short_description.data,
                description=form.description.data,
                currency=form.currency.data,
                pricing_type=form.pricing_type.data,
                optional=form.optional.data,
                available_online=form.available_online.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

            flash(
                "Experience add-on created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "experience_addons.experience_addons",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_addons/create.html",
        form=form,
        experience_id=experience_id,
    )


# =============================================================================
# Edit Add-on
# =============================================================================
@experience_addons_bp.route("/experiences/<int:experience_id>/addons/<int:addon_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit_experience_addon(
    experience_id,
    addon_id,
):
    """
    Edit an existing experience add-on.
    """

    addon = addon_service.get_addon(
        addon_id
    )

    if addon is None or addon.experience_id != experience_id:

        flash(
            "Experience add-on not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    form = ExperienceAddonEditForm(
        obj=addon
    )

    if form.validate_on_submit():

        try:

            addon_service.update_addon(
                addon_id=addon_id,
                name=form.name.data,
                price=form.price.data,
                short_description=form.short_description.data,
                description=form.description.data,
                currency=form.currency.data,
                pricing_type=form.pricing_type.data,
                optional=form.optional.data,
                available_online=form.available_online.data,
                display_order=form.display_order.data,
            )

            if form.active.data:

                addon_service.activate_addon(
                    addon_id
                )

            else:

                addon_service.deactivate_addon(
                    addon_id
                )

            flash(
                "Experience add-on updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "experience_addons.experience_addons",
                    experience_id=experience_id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_addons/edit.html",
        form=form,
        addon=addon,
        experience_id=experience_id,
    )


# =============================================================================
# Activate Add-on
# =============================================================================
@experience_addons_bp.route("/experiences/<int:experience_id>/addons/<int:addon_id>/activate",methods=["POST"],)
#@login_required
def activate_experience_addon(
    experience_id,
    addon_id,
):
    """
    Activate an experience add-on.
    """

    addon = addon_service.get_addon(
        addon_id
    )

    if addon is None or addon.experience_id != experience_id:

        flash(
            "Experience add-on not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    try:

        addon_service.activate_addon(
            addon_id
        )

        flash(
            "Experience add-on activated.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_addons.experience_addons",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Deactivate Add-on
# =============================================================================
@experience_addons_bp.route(
    "/experiences/<int:experience_id>/addons/<int:addon_id>/deactivate",
    methods=["POST"],
)
#@login_required
def deactivate_experience_addon(
    experience_id,
    addon_id,
):
    """
    Deactivate an experience add-on.
    """

    addon = addon_service.get_addon(
        addon_id
    )

    if addon is None or addon.experience_id != experience_id:

        flash(
            "Experience add-on not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    try:

        addon_service.deactivate_addon(
            addon_id
        )

        flash(
            "Experience add-on deactivated.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_addons.experience_addons",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Toggle Online Availability
# =============================================================================
@experience_addons_bp.route(
    "/experiences/<int:experience_id>/addons/<int:addon_id>/online",
    methods=["POST"],
)
#@login_required
def toggle_experience_addon_online(
    experience_id,
    addon_id,
):
    """
    Toggle whether an add-on can be selected during online booking.
    """

    addon = addon_service.get_addon(
        addon_id
    )

    if addon is None or addon.experience_id != experience_id:

        flash(
            "Experience add-on not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    try:

        addon_service.set_online_availability(
            addon_id,
            available=not addon.available_online,
        )

        flash(
            "Online availability updated.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_addons.experience_addons",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Delete Add-on
# =============================================================================
@experience_addons_bp.route(
    "/experiences/<int:experience_id>/addons/<int:addon_id>/delete",
    methods=["POST"],
)
#@login_required
def delete_experience_addon(
    experience_id,
    addon_id,
):
    """
    Permanently delete an experience add-on.

    The service prevents deletion when the add-on has already
    been used by a booking.
    """

    addon = addon_service.get_addon(
        addon_id
    )

    if addon is None or addon.experience_id != experience_id:

        flash(
            "Experience add-on not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    try:

        addon_service.delete_addon(
            addon_id
        )

        flash(
            "Experience add-on deleted successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_addons.experience_addons",
            experience_id=experience_id,
        )
    )


# =============================================================================
# Reorder Add-ons
# =============================================================================
@experience_addons_bp.route(
    "/experiences/<int:experience_id>/addons/reorder",
    methods=["POST"],
)
#@login_required
def reorder_experience_addons(
    experience_id,
):
    """
    Reorder add-ons for an experience.

    Expects either:

        addon_ids[]=1&addon_ids[]=4&addon_ids[]=2

    or a JSON payload:

        {
            "addon_ids": [1, 4, 2]
        }
    """

    addon_ids = request.form.getlist(
        "addon_ids[]"
    )

    if not addon_ids:

        data = request.get_json(
            silent=True
        ) or {}

        addon_ids = data.get(
            "addon_ids",
            []
        )

    try:

        addon_ids = [
            int(addon_id)
            for addon_id in addon_ids
        ]

    except (
        TypeError,
        ValueError,
    ):

        flash(
            "Invalid add-on ordering data.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_addons.experience_addons",
                experience_id=experience_id,
            )
        )

    try:

        addon_service.reorder_addons(
            experience_id=experience_id,
            addon_ids=addon_ids,
        )

        flash(
            "Experience add-ons reordered successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "experience_addons.experience_addons",
            experience_id=experience_id,
        )
    )