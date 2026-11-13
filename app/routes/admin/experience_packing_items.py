"""
===============================================================================
The Uncharted Route
Admin Experience Packing Items
===============================================================================

Administrative routes for managing packing items belonging to experiences.

Responsibilities:

- List packing items
- Create packing items
- Edit packing items
- Activate packing items
- Deactivate packing items
- Delete packing items
- Reorder packing items

All business logic is delegated to the
ExperiencePackingItemService.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from flask_login import (
    login_required,
)

from app.forms.admin_experience_packing_items import (
    ExperiencePackingItemCreateForm,
    ExperiencePackingItemEditForm,
)

from app.models import (
    Experience,
    ExperiencePackingItem,
)

from app.services.experiences.experience_packing_item_service import (
    ExperiencePackingItemService,
)


# =============================================================================
# Blueprint
# =============================================================================

experience_packing_items_bp = Blueprint(
    "admin_experience_packing_items",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Helpers
# =============================================================================

def _get_experience_or_404(experience_id):
    """
    Retrieve an experiences or raise a 404 response.
    """

    from flask import abort

    experience = Experience.query.get_or_404(
        experience_id
    )

    return experience


def _get_packing_item_for_experience_or_404(
    experience_id,
    item_id,
):
    """
    Retrieve a packing item and ensure it belongs
    to the supplied experiences.
    """

    from flask import abort

    item = ExperiencePackingItem.query.filter_by(
        id=item_id,
        experience_id=experience_id,
    ).first()

    if item is None:
        abort(404)

    return item


# =============================================================================
# INDEX
# =============================================================================
@experience_packing_items_bp.route(
    "/<int:experience_id>/packing-items")
#@login_required
def index(experience_id):
    """
    Display all packing items belonging to an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_items = (
        ExperiencePackingItemService
        .get_experience_packing_items(
            experience_id,
            active_only=False,
        )
    )

    return render_template(
        "admin/experiences/experience_packing_items/index.html",
        experience=experience,
        packing_items=packing_items,)

# =============================================================================
# CREATE
# =============================================================================
@experience_packing_items_bp.route(
    "/<int:experience_id>/packing-items/create",
    methods=["GET", "POST"],
)
#@login_required
def create(experience_id):
    """
    Create a new packing item for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperiencePackingItemCreateForm()

    if form.validate_on_submit():

        try:
            ExperiencePackingItemService.create_packing_item(
                experience_id=experience.id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data or "backpack",
                recommended=form.recommended.data,
                required=form.required.data,
                display_order=form.display_order.data or 0,
                active=form.active.data,
            )

            flash(
                "Packing item created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_packing_items.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_packing_items/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# EDIT
# =============================================================================
@experience_packing_items_bp.route(
    "/<int:experience_id>/packing-items/<int:item_id>/edit",
    methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    item_id,
):
    """
    Edit an existing packing item.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    form = ExperiencePackingItemEditForm(
        obj=packing_item
    )

    if form.validate_on_submit():

        try:

            ExperiencePackingItemService.update_packing_item(
                packing_item.id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data or "backpack",
                recommended=form.recommended.data,
                required=form.required.data,
                display_order=form.display_order.data or 0,
                active=form.active.data,
            )

            flash(
                "Packing item updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_packing_items.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_packing_items/edit.html",
        experience=experience,
        packing_item=packing_item,
        form=form,
    )


# =============================================================================
# ACTIVATE
# =============================================================================
@experience_packing_items_bp.route("/<int:experience_id>/packing-items/<int:item_id>/activate",methods=["POST"],)
#@login_required
def activate(
    experience_id,
    item_id,
):
    """
    Activate a packing item.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    ExperiencePackingItemService.activate(
        packing_item.id
    )

    flash(
        "Packing item activated.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_packing_items.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# DEACTIVATE
# =============================================================================
@experience_packing_items_bp.route("/<int:experience_id>/packing-items/<int:item_id>/deactivate",methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    item_id,
):
    """
    Deactivate a packing item.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    ExperiencePackingItemService.deactivate(
        packing_item.id
    )

    flash(
        "Packing item deactivated.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_packing_items.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# DELETE
# =============================================================================
@experience_packing_items_bp.route("/<int:experience_id>/packing-items/<int:item_id>/delete",methods=["POST"],)
#@login_required
def delete(
    experience_id,
    item_id,
):
    """
    Permanently delete a packing item.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    ExperiencePackingItemService.delete_packing_item(
        packing_item.id
    )

    flash(
        "Packing item deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_packing_items.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# MARK REQUIRED
# =============================================================================
@experience_packing_items_bp.route("/<int:experience_id>/packing-items/<int:item_id>/required",methods=["POST"],)
#@login_required
def mark_required(
    experience_id,
    item_id,
):
    """
    Mark a packing item as required.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    ExperiencePackingItemService.mark_required(
        packing_item.id
    )

    flash(
        "Packing item marked as required.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_packing_items.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# MARK OPTIONAL
# =============================================================================
@experience_packing_items_bp.route("/<int:experience_id>/packing-items/<int:item_id>/optional",methods=["POST"],)
#@login_required
def mark_optional(
    experience_id,
    item_id,
):
    """
    Mark a packing item as optional.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    packing_item = (
        _get_packing_item_for_experience_or_404(
            experience_id,
            item_id,
        )
    )

    ExperiencePackingItemService.mark_optional(
        packing_item.id
    )

    flash(
        "Packing item marked as optional.",
        "success",
    )

    return redirect(
        url_for(
            "admin_experience_packing_items.index",
            experience_id=experience.id,
        )
    )