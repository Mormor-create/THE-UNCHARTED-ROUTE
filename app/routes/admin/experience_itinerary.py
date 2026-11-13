"""
===============================================================================
The Uncharted Route
Admin Experience Itinerary Routes
===============================================================================

Administrative routes for managing itinerary items belonging to experiences.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import login_required
from app.forms.admin_experience_itinerary import (
    ExperienceItineraryForm,
)
from app.services.experiences.experience_itinerary_service import (
    create_itinerary_item,
    get_itinerary_item,
    get_experience_itinerary,
    update_itinerary_item,
    delete_itinerary_item,
    reorder_itinerary_item,
)

from app.services.experiences.experience_service import (
    get_experience_by_id,
)


experience_itinerary_admin = Blueprint(
    "experience_itinerary_admin",
    __name__,
    url_prefix="/admin/experience_itinerary",
)

# =============================================================================
# INDEX
# =============================================================================
@experience_itinerary_admin.route(
    "/<int:experience_id>/itinerary")
#@login_required
def index(experience_id):
    """
    Display all itinerary items belonging to an experiences.
    """

    experience = get_experience_by_id(
        experience_id
    )

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_admin.index"
            )
        )

    itinerary = get_experience_itinerary(
        experience_id
    )

    return render_template(
        "admin/experiences/experience_itinerary/index.html",
        experience=experience,
        itinerary=itinerary,
    )


# =============================================================================
# CREATE
# =============================================================================
@experience_itinerary_admin.route("/<int:experience_id>/itinerary/create",methods=["GET", "POST"],)
#@login_required
def create(experience_id):
    """
    Create a new itinerary item.
    """

    experience = get_experience_by_id(
        experience_id
    )

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_admin.index"
            )
        )

    form = ExperienceItineraryForm()

    if form.validate_on_submit():

        create_itinerary_item(
            experience_id=experience.id,
            day_number=form.day_number.data,
            title=form.title.data,
            activity_time=form.activity_time.data,
            description=form.description.data,
            display_order=form.display_order.data or 0,
        )

        flash(
            "Itinerary item created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "experience_itinerary_admin.index",
                experience_id=experience.id,
            )
        )

    return render_template(
        "admin/experiences/experience_itinerary/create.html",
        experience=experience,
        form=form,)

# =============================================================================
# EDIT
# =============================================================================
@experience_itinerary_admin.route("/<int:experience_id>/itinerary/<int:item_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    item_id,
):
    """
    Edit an itinerary item.
    """

    experience = get_experience_by_id(
        experience_id
    )

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_admin.index"
            )
        )

    item = get_itinerary_item(
        item_id
    )

    if item is None or item.experience_id != experience.id:
        flash(
            "Itinerary item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_itinerary_admin.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceItineraryForm(
        obj=item
    )

    if form.validate_on_submit():

        update_itinerary_item(
            item_id,
            day_number=form.day_number.data,
            title=form.title.data,
            activity_time=form.activity_time.data,
            description=form.description.data,
            display_order=form.display_order.data or 0,
        )

        flash(
            "Itinerary item updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "experience_itinerary_admin.index",
                experience_id=experience.id,
            )
        )

    return render_template(
        "admin/experiences/experience_itinerary/edit.html",
        experience=experience,
        item=item,
        form=form,
    )


# =============================================================================
# DELETE
# =============================================================================
@experience_itinerary_admin.route("/<int:experience_id>/itinerary/<int:item_id>/delete",methods=["POST"],)
#@login_required
def delete(
    experience_id,
    item_id,
):
    """
    Delete an itinerary item.
    """

    experience = get_experience_by_id(
        experience_id
    )

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_admin.index"
            )
        )

    item = get_itinerary_item(
        item_id
    )

    if item is None or item.experience_id != experience.id:
        flash(
            "Itinerary item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_itinerary_admin.index",
                experience_id=experience.id,
            )
        )

    delete_itinerary_item(
        item_id
    )

    flash(
        "Itinerary item deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "experience_itinerary_admin.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# REORDER
# =============================================================================
@experience_itinerary_admin.route("/<int:experience_id>/itinerary/<int:item_id>/order/<int:display_order>",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    item_id,
    display_order,
):
    """
    Update the display order of an itinerary item.
    """

    experience = get_experience_by_id(
        experience_id
    )

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_admin.index"
            )
        )

    item = get_itinerary_item(
        item_id
    )

    if item is None or item.experience_id != experience.id:
        flash(
            "Itinerary item not found.",
            "danger",
        )

        return redirect(
            url_for(
                "experience_itinerary_admin.index",
                experience_id=experience.id,
            )
        )

    reorder_itinerary_item(
        item_id,
        display_order,
    )

    flash(
        "Itinerary order updated.",
        "success",
    )

    return redirect(
        url_for(
            "experience_itinerary_admin.index",
            experience_id=experience.id,
        )
    )