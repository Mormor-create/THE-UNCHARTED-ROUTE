"""
===============================================================================
The Uncharted Route
Admin Stay Room Routes
===============================================================================
"""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,)
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_stay_room import AdminStayRoomForm
from app.models import Stay
from app.services.admin.admin_stay_room_service import (
    activate_stay_room,
    create_stay_room,
    deactivate_stay_room,
    delete_stay_room,
    set_stay_room_featured,
    get_stay_room,
    get_stay_rooms,
    update_stay_room,)
from app.services.admin.admin_stay_service import get_stay
from app.services.media_service import get_all_media_folders
from extensions import db

stay_room_bp = Blueprint(
    "admin_stay_room",
    __name__,
    url_prefix="/admin/stays",)

# =============================================================================
# MEDIA FOLDER HELPERS
# =============================================================================
# ---------------------------------------------------------------------------
# Media Folder Helpers
# ---------------------------------------------------------------------------

def _get_stay_room_media_folder_choices(root_name):
    """
    Build media-folder choices from a specific Stay Rooms
    media-library tree.

    The root folder itself is not selectable.
    All child folders and their descendants are included,
    preserving the folder hierarchy visually.
    """
    folders = get_all_media_folders(active=True)

    root_folder = next(
        (
            folder
            for folder in folders
            if (
                folder.name
                and folder.name.strip().lower()
                == root_name.strip().lower()
                and folder.parent_id is None
            )
        ),
        None,
    )

    if root_folder is None:
        return []

    children_by_parent = {}

    for folder in folders:
        children_by_parent.setdefault(
            folder.parent_id,
            [],
        ).append(folder)

    for children in children_by_parent.values():
        children.sort(
            key=lambda folder: (
                folder.display_order,
                folder.name.lower(),
            )
        )

    choices = []

    def append_children(parent_id, depth):
        for folder in children_by_parent.get(
            parent_id,
            [],
        ):
            choices.append(
                (
                    folder.id,
                    f'{"— " * depth}{folder.name}',
                )
            )

            append_children(
                folder.id,
                depth + 1,
            )

    append_children(
        root_folder.id,
        0,
    )

    return choices


def _populate_stay_room_media_folder_choices(form):
    form.media_folder_id.choices = (
        _get_stay_room_media_folder_choices(
            "Stay Rooms"))

# =============================================================================
# INDEX
# =============================================================================
@stay_room_bp.get("/<int:stay_id>/rooms")
@admin_required
def index(stay_id):
    """
    List all rooms belonging to a Stay.
    """
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(
            url_for("admin_stay.index")
        )

    rooms = get_stay_rooms(
        stay_id=stay.id,)

    return render_template(
        "admin/stays/rooms/index.html",
        stay=stay,
        rooms=rooms,)

# =============================================================================
# CREATE
# =============================================================================
@stay_room_bp.route("/<int:stay_id>/rooms/create",methods=["GET", "POST"],)
@admin_required
def create(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayRoomForm()

    _populate_stay_room_media_folder_choices(form)

    if form.validate_on_submit():
        try:
            room = create_stay_room(
                acting_admin=current_user,
                stay_id=stay_id,
                room_code=form.room_code.data,
                name=form.name.data,
                slug=form.slug.data,
                room_type=form.room_type.data,
                short_description=form.short_description.data,
                description=form.description.data,
                maximum_guests=form.maximum_guests.data,
                maximum_adults=form.maximum_adults.data,
                maximum_children=form.maximum_children.data,
                minimum_guests=form.minimum_guests.data,
                total_units=form.total_units.data,
                nightly_rate=form.nightly_rate.data,
                currency=form.currency.data,
                meal_plan=form.meal_plan.data,
                bed_configuration=form.bed_configuration.data,
                floor=form.floor.data,
                size_description=form.size_description.data,
                availability_status=form.availability_status.data,
                featured=form.featured.data,
                active=form.active.data,
                display_order=form.display_order.data,
                media_folder_id=form.media_folder_id.data,
            )

            flash(
                f'Room "{room.name}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_room.detail",
                    stay_id=stay.id,
                    room_id=room.id,))

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/rooms/create.html",
        form=form,
        stay=stay,
        stay_id=stay_id,)

# =============================================================================
# DETAIL
# =============================================================================
@stay_room_bp.get("/rooms/<int:room_id>")
@admin_required
def detail(room_id):
    """
    View a Stay Room.
    """
    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    stay = get_stay(room.stay_id)

    if stay is None:
        flash(
            "The Stay associated with this room could not be found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    return render_template(
        "admin/stays/rooms/detail.html",
        room=room,
        stay=stay,)

# =============================================================================
# EDIT
# =============================================================================
@stay_room_bp.route(
    "/<int:stay_id>/rooms/<int:room_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(stay_id, room_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(
            url_for("admin_stay.index")
        )

    room = get_stay_room(room_id)

    if room is None or room.stay_id != stay.id:
        flash("Room not found.", "danger")
        return redirect(
            url_for(
                "admin_stay.detail",
                stay_id=stay.id,
            )
        )

    form = AdminStayRoomForm(obj=room)

    _populate_stay_room_media_folder_choices(form)

    if form.validate_on_submit():
        try:
            update_stay_room(
                acting_admin=current_user,
                room=room,
                room_code=form.room_code.data,
                name=form.name.data,
                slug=form.slug.data,
                room_type=form.room_type.data,
                short_description=form.short_description.data,
                description=form.description.data,
                maximum_guests=form.maximum_guests.data,
                maximum_adults=form.maximum_adults.data,
                maximum_children=form.maximum_children.data,
                minimum_guests=form.minimum_guests.data,
                total_units=form.total_units.data,
                nightly_rate=form.nightly_rate.data,
                currency=form.currency.data,
                meal_plan=form.meal_plan.data,
                bed_configuration=form.bed_configuration.data,
                floor=form.floor.data,
                size_description=form.size_description.data,
                availability_status=form.availability_status.data,
                featured=form.featured.data,
                active=form.active.data,
                display_order=form.display_order.data,
                media_folder_id=form.media_folder_id.data,
            )

            flash(
                f'Room "{room.name}" was updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_room.detail",
                    stay_id=stay.id,
                    room_id=room.id,
                ))

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/rooms/edit.html",
        form=form,
        stay=stay,
        room=room,)
# =============================================================================
# ACTIVATE
# =============================================================================
@stay_room_bp.post("/rooms/<int:room_id>/activate")
@admin_required
def activate(room_id):
    """
    Activate a Stay Room.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    activate_stay_room(
        room,
        user_id=(
            current_user.id
            if current_user.is_authenticated
            else None
        ),
    )

    flash(
        "Stay room activated.",
        "success",
    )

    return redirect(
        url_for(
            "admin_stay_room.detail",
            room_id=room.id,
        )
    )


# =============================================================================
# DEACTIVATE
# =============================================================================
@stay_room_bp.post("/rooms/<int:room_id>/deactivate")
@admin_required
def deactivate(room_id):
    """
    Deactivate a Stay Room.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    deactivate_stay_room(
        room,
        user_id=(
            current_user.id
            if current_user.is_authenticated
            else None
        ),
    )

    flash(
        "Stay room deactivated.",
        "success",
    )

    return redirect(
        url_for(
            "admin_stay_room.detail",
            room_id=room.id,
        )
    )


# =============================================================================
# FEATURE
# =============================================================================
@stay_room_bp.post("/rooms/<int:room_id>/feature")
@admin_required
def feature(room_id):
    """
    Feature a Stay Room.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    set_stay_room_featured(
        room,
        user_id=(
            current_user.id
            if current_user.is_authenticated
            else None
        ),
    )

    flash(
        "Stay room featured.",
        "success",
    )

    return redirect(
        url_for(
            "admin_stay_room.detail",
            room_id=room.id,
        )
    )


# =============================================================================
# UNFEATURE
# =============================================================================
@stay_room_bp.post("/rooms/<int:room_id>/unfeature")
@admin_required
def unfeature(room_id):
    """
    Remove featured status from a Stay Room.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for(
                "admin_stay.index",
            )
        )

    set_stay_room_featured(
        room,
        user_id=(
            current_user.id
            if current_user.is_authenticated
else None),)

    flash(
        "Stay room removed from featured rooms.",
        "success",
    )

    return redirect(
        url_for(
            "admin_stay_room.detail",
            room_id=room.id,
        )
    )


# =============================================================================
# DELETE
# =============================================================================
@stay_room_bp.post("/rooms/<int:room_id>/delete")
@admin_required
def delete(room_id):
    """
    Delete a Stay Room.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "error",
        )
        return redirect(
            url_for("admin_stay.index",))

    stay_id = room.stay_id

    delete_stay_room(
        room,
        user_id=(
            current_user.id
            if current_user.is_authenticated
            else None),)

    flash("Stay room deleted successfully.","success")

    return redirect(
        url_for(
            "admin_stay_room.index",
            stay_id=stay_id,))