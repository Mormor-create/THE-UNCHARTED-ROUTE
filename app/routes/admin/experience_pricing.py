"""
===============================================================================
The Uncharted Route
Administrative Experience Pricing Routes
===============================================================================
Protected administrative routes for managing pricing tiers belonging to
experiences.
Architecture
    Route → Form → Service → Model
Pricing belongs to an Experience and is managed independently of the
parent Experience record.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,)
from app.decorators.admin import admin_required
from app.forms.admin_experience_pricing import (
    AdminExperiencePricingForm,)
from app.services.experiences.experience_pricing_service import (
    get_pricing,
    create_pricing,
    update_pricing,
    delete_pricing,
    activate_pricing,
    deactivate_pricing,)
from app.services.experiences.experience_service import (
    get_experience_by_id,)
# =============================================================================
# Blueprint
# =============================================================================
experience_pricing_bp = Blueprint(
    "admin_experience_pricing",
    __name__,
    url_prefix="/admin/experiences/<int:experience_id>/pricing",)

# =============================================================================
# Pricing List
# =============================================================================
@experience_pricing_bp.route("/")
@admin_required
def index(experience_id):
    """
    Display all pricing tiers belonging to an experiences.
    """
    experience = get_experience_by_id(experience_id)
    if experience is None:
        flash("Experience not found.","danger",)

        return redirect(
            url_for("admin_experiences.index"))
    pricing_options = get_pricing(
        experience_id=experience_id,
        active_only=False,)

    return render_template(
        "admin/experiences/experience_pricing/index.html",
        experience=experience,
        pricing_options=pricing_options,)

# =============================================================================
# Create Pricing
# =============================================================================
@experience_pricing_bp.route("/create",methods=["GET", "POST"],)
@admin_required
def create(experience_id):
    """
    Create a new pricing tier for an experiences.
    """
    experience = get_experience_by_id(experience_id)
    if experience is None:
        flash("Experience not found.","danger",)
        return redirect(
            url_for("admin_experiences.index"))
    form = AdminExperiencePricingForm()
    if form.validate_on_submit():

        try:
            pricing = create_pricing(
                experience_id=experience_id,
                experience_level=form.experience_level.data,
                price=form.price.data,
                minimum_people=form.minimum_people.data,
                maximum_people=form.maximum_people.data,
                currency=form.currency.data,
                notes=form.notes.data,
                display_order=form.display_order.data,
                active=form.active.data,)

        except ValueError as exc:
            flash(str(exc),"danger",)

            return render_template(
                "admin/experiences/experience_pricing/create.html",
                form=form,
                experience=experience,)

        flash("Pricing tier created successfully.","success",)
        return redirect(
            url_for(
                "admin_experience_pricing.index",
                experience_id=experience_id,))

    return render_template(
        "admin/experiences/experience_pricing/create.html",
        form=form,
        experience=experience,)

# =============================================================================
# Edit Pricing
# =============================================================================
@experience_pricing_bp.route("/<int:pricing_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(experience_id,pricing_id,):
    """
    Edit an existing pricing tier.
    """
    experience = get_experience_by_id(experience_id)
    if experience is None:
        flash("Experience not found.","danger",)
        return redirect(
            url_for("admin_experiences.index"))
    pricing = experience_pricing_bp.service.get_by_id(
        pricing_id) if False else None

    from app.services.experiences.experience_pricing_service import (experience_pricing_service,)
    pricing = experience_pricing_service.get_by_id(pricing_id)
    if pricing is None or pricing.experience_id != experience_id:
        flash("Pricing tier not found.","danger",)

        return redirect(
            url_for("admin_experience_pricing.index",experience_id=experience_id,))

    form = AdminExperiencePricingForm(obj=pricing)
    if form.validate_on_submit():

        try:

            update_pricing(
                pricing_id,
                experience_level=form.experience_level.data,
                price=form.price.data,
                minimum_people=form.minimum_people.data,
                maximum_people=form.maximum_people.data,
                currency=form.currency.data,
                notes=form.notes.data,
                display_order=form.display_order.data,
                active=form.active.data,)

        except ValueError as exc:
            flash(str(exc),"danger",)
            return render_template(
                "admin/experiences/experience_pricing/edit.html",
                form=form,
                experience=experience,
                pricing=pricing,)

        flash("Pricing tier updated successfully.","success",)
        return redirect(
            url_for("admin_experience_pricing.index",experience_id=experience_id,))

    return render_template(
        "admin/experiences/experience_pricing/edit.html",
        form=form,
        experience=experience,
        pricing=pricing,)

# =============================================================================
# Activate Pricing
# =============================================================================
@experience_pricing_bp.route("/<int:pricing_id>/activate",methods=["POST"],)
@admin_required
def activate(experience_id,pricing_id,):
    """
    Activate a pricing tier.
    """
    from app.services.experiences.experience_pricing_service import experience_pricing_service
    pricing = experience_pricing_service.get_by_id(pricing_id)

    if pricing is None or pricing.experience_id != experience_id:
        flash("Pricing tier not found.","danger",)
        return redirect(
            url_for(
                "admin_experience_pricing.index",
                experience_id=experience_id,))

    activate_pricing(pricing_id)

    flash("Pricing tier activated.","success",)
    return redirect(
        url_for("admin_experience_pricing.index",experience_id=experience_id,))

# =============================================================================
# Deactivate Pricing
# =============================================================================
@experience_pricing_bp.route("/<int:pricing_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate(
    experience_id,
    pricing_id,):
    """
    Deactivate a pricing tier without deleting it.
    """
    from app.services.experiences.experience_pricing_service import (experience_pricing_service,)
    pricing = experience_pricing_service.get_by_id(pricing_id)
    if pricing is None or pricing.experience_id != experience_id:
        flash("Pricing tier not found.","danger",)
        return redirect(
            url_for(
                "admin_experience_pricing.index",
                experience_id=experience_id,))

    deactivate_pricing(
        pricing_id)

    flash("Pricing tier deactivated.","success",)

    return redirect(
        url_for(
            "admin_experience_pricing.index",
            experience_id=experience_id,))

# =============================================================================
# Delete Pricing
# =============================================================================
@experience_pricing_bp.route("/<int:pricing_id>/delete",methods=["POST"],)
@admin_required
def delete(experience_id,pricing_id,):
    """
    Permanently delete a pricing tier.
    """
    from app.services.experiences.experience_pricing_service import (
        experience_pricing_service,)
    pricing = experience_pricing_service.get_by_id(pricing_id)
    if pricing is None or pricing.experience_id != experience_id:
        flash("Pricing tier not found.","danger",)

        return redirect(
            url_for(
                "admin_experience_pricing.index",
                experience_id=experience_id,))

    delete_pricing(pricing_id)
    flash("Pricing tier deleted successfully.","success",)

    return redirect(
        url_for(
            "admin_experience_pricing.index",
            experience_id=experience_id,))

# =============================================================================
# Public API
# =============================================================================
__all__ = ["experience_pricing_bp",]