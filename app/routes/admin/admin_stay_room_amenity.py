from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_stay_room_amenity import AdminStayRoomAmenityForm
from app.services.admin.admin_stay_room_amenity_service import (
    activate_stay_room_amenity,
    create_stay_room_amenity,
    deactivate_stay_room_amenity,
    delete_stay_room_amenity,
    get_stay_room_amenity,
    get_stay_room_amenities,
    set_stay_room_amenity_featured,
    update_stay_room_amenity,
)
from app.services.admin.admin_stay_room_service import get_stay_room

stay_room_amenity_bp = Blueprint(
    "admin_stay_room_amenity",
    __name__,
    url_prefix="/admin/stays",
)

# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------
@stay_room_amenity_bp.route("/rooms/<int:room_id>/amenities/")
#@admin_required
def index(room_id):
    room = get_stay_room(room_id)

    if room is None:
        flash("Room not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    amenities = get_stay_room_amenities(room_id=room.id)

    return render_template(
        "admin/stays/rooms/amenities/index.html",
        room=room,
        stay=room.stay,
        amenities=amenities,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
@stay_room_amenity_bp.route("/rooms/<int:room_id>/amenities/create",methods=["GET", "POST"],)
#@admin_required
def create(room_id):
    room = get_stay_room(room_id)

    if room is None:
        flash("Room not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayRoomAmenityForm()

    if form.validate_on_submit():
        try:
            amenity = create_stay_room_amenity(
                acting_admin=current_user,
                room_id=room.id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data,
                active=form.active.data,
                featured=form.featured.data,
                display_order=form.display_order.data,
            )

            flash(
                f'Room amenity "{amenity.name}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_room_amenity.index",
                    room_id=room.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/rooms/amenities/create.html",
        form=form,
        room=room,
        stay=room.stay,
    )

# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------
@stay_room_amenity_bp.route("/rooms/amenities/<int:amenity_id>")
#@admin_required
def detail(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    return render_template(
        "admin/stays/rooms/amenities/detail.html",
        amenity=amenity,
        room=amenity.room,
        stay=amenity.room.stay,
    )


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/edit",
    methods=["GET", "POST"],
)
#@admin_required
def edit(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayRoomAmenityForm(obj=amenity)

    if form.validate_on_submit():
        try:
            update_stay_room_amenity(
                acting_admin=current_user,
                amenity=amenity,
                room_id=amenity.room_id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data,
                active=form.active.data,
                featured=form.featured.data,
                display_order=form.display_order.data,
            )

            flash(
                f'Room amenity "{amenity.name}" was updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_room_amenity.detail",
                    amenity_id=amenity.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/rooms/amenities/edit.html",
        form=form,
        amenity=amenity,
        room=amenity.room,
        stay=amenity.room.stay,
    )

# ---------------------------------------------------------------------------
# Activate
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/activate",
    methods=["POST"],
)
#@admin_required
def activate(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        activate_stay_room_amenity(
            acting_admin=current_user,
            amenity=amenity,
        )

        flash(
            "Room amenity was activated.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_room_amenity.detail",
            amenity_id=amenity.id,
        )
    )


# ---------------------------------------------------------------------------
# Deactivate
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/deactivate",
    methods=["POST"],
)
#@admin_required
def deactivate(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        deactivate_stay_room_amenity(
            acting_admin=current_user,
            amenity=amenity,
        )

        flash(
            "Room amenity was deactivated.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_room_amenity.detail",
            amenity_id=amenity.id,
        )
    )


# ---------------------------------------------------------------------------
# Feature
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/feature",
    methods=["POST"],
)
#@admin_required
def feature(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_room_amenity_featured(
            acting_admin=current_user,
            amenity=amenity,
            featured=True,
        )

        flash(
            "Room amenity was featured.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_room_amenity.detail",
            amenity_id=amenity.id,
        )
    )


# ---------------------------------------------------------------------------
# Unfeature
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/unfeature",
    methods=["POST"],
)
#@admin_required
def unfeature(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_room_amenity_featured(
            acting_admin=current_user,
            amenity=amenity,
            featured=False,
        )

        flash(
            "Room amenity was unfeatured.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_room_amenity.detail",
            amenity_id=amenity.id,
        )
    )


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@stay_room_amenity_bp.route(
    "/rooms/amenities/<int:amenity_id>/delete",
    methods=["POST"],
)
#@admin_required
def delete(amenity_id):
    amenity = get_stay_room_amenity(amenity_id)

    if amenity is None:
        flash("Room amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    room_id = amenity.room_id

    try:
        delete_stay_room_amenity(
            acting_admin=current_user,
            amenity=amenity,
        )

        flash(
            "Room amenity was deleted.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_room_amenity.index",
            room_id=room_id,
        )
    )