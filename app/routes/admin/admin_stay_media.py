"""
===============================================================================
The Uncharted Route
Admin Stay Media Routes
===============================================================================

Administrative routes for managing media assigned to Stay records and
individual StayRoom records.

Responsibilities
-----------------
• Display Stay media
• Create Stay media assignments
• Edit Stay media assignments
• Activate/deactivate Stay media
• Delete Stay media assignments
• Display room media
• Create room media assignments
• Edit room media assignments
• Activate/deactivate room media
• Delete room media assignments

Media-folder scoping
--------------------
Stay media is restricted to the Stay's assigned property media folder.

Room media is restricted to the StayRoom's assigned room media folder.

The form layer applies the folder restriction to selectable MediaAssets,
while the service layer independently validates the selected MediaAsset
before saving.

The route layer additionally builds a preview map for the assets available
in the exact assigned folder.
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
from app.forms.admin_stay_media import AdminStayMediaForm
from app.forms.admin_stay_room_media import AdminStayRoomMediaForm
from app.services.media_service import get_cms_media_assets
from app.services.admin.admin_stay_media_service import (
    activate_stay_media,
    create_stay_media,
    deactivate_stay_media,
    delete_stay_media,
    get_stay_media,
    get_stay_media_items,
    update_stay_media,)
from app.services.admin.admin_stay_room_media_service import (
    activate_stay_room_media,
    create_stay_room_media,
    deactivate_stay_room_media,
    delete_stay_room_media,
    get_room_media,
    get_stay_room_media,
    update_stay_room_media,)
from app.services.admin.admin_stay_room_service import get_stay_room
from app.services.admin.admin_stay_service import get_stay

stay_media_bp = Blueprint(
    "admin_stay_media",
    __name__,
    url_prefix="/admin/stays",)

# =============================================================================
# Preview Helpers
# =============================================================================
def _build_media_asset_preview_map(folder_id):
    """
    Build the preview data used by Stay and StayRoom media forms.

    Only active image/video assets directly belonging to the supplied folder
    are included.

    Descendant folders are intentionally excluded.

    The returned structure is keyed by MediaAsset ID so the frontend can
    immediately resolve the selected asset when the selector changes.

    Example:

        {
            "42": {
                "url": "...",
                "title": "Fairmont Exterior",
                "media_type": "image",
            }
        }
    """

    if not folder_id:
        return {}

    assets = get_cms_media_assets(
        folder_id=folder_id,
        include_descendants=False,
        media_type=None,
        active_only=True,)
    preview_map = {}

    for asset in assets:
        media_type = getattr(
            asset,
            "media_type",
            None,
        )

        if media_type not in ("image", "video"):
            continue

        title = (
            getattr(
                asset,
                "title",
                None,
            )
            or getattr(
                asset,
                "original_filename",
                None,
            )
            or getattr(
                asset,
                "filename",
                None,
            )
            or f"Media Asset #{asset.id}"
        )

        browser_url = getattr(
            asset,
            "browser_url",
            None,
        )

        if not browser_url:
            continue

        preview_map[str(asset.id)] = {
            "url": browser_url,
            "title": title,
            "media_type": media_type,
        }

    return preview_map


# =============================================================================
# Stay Media
# =============================================================================

@stay_media_bp.route(
    "/<int:stay_id>/media/",
    methods=["GET"],
)
@admin_required
def index(stay_id):
    """
    Display all media assignments for a Stay.
    """

    stay = get_stay(stay_id)

    if stay is None:
        flash(
            "Stay not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    media_items = get_stay_media_items(
        stay_id=stay.id,
    )

    return render_template(
        "admin/stays/media/index.html",
        stay=stay,
        media_items=media_items,
    )


# =============================================================================
# Stay Media Create
# =============================================================================
@stay_media_bp.route("/<int:stay_id>/media/create",methods=["GET", "POST"],)
@admin_required
def create(stay_id):
    """
    Create a media assignment for a specific Stay.
    """

    stay = get_stay(stay_id)

    if stay is None:
        flash(
            "Stay not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayMediaForm()

    # -------------------------------------------------------------------------
    # Folder-scoped media choices
    # -------------------------------------------------------------------------
    #
    # The form owns the selector choices. Only assets directly belonging to
    # the Stay's assigned property folder are exposed.
    #
    # Descendant room folders are intentionally excluded.
    # -------------------------------------------------------------------------

    form.set_media_choices(
        stay.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Preview data
    # -------------------------------------------------------------------------

    media_asset_preview_map = _build_media_asset_preview_map(
        stay.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    if form.validate_on_submit():
        try:
            create_stay_media(
                acting_admin=current_user,
                stay_id=stay.id,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,
            )

            flash(
                "Stay media was added successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_media.index",
                    stay_id=stay.id,
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/stays/media/create.html",
        form=form,
        stay=stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Stay Media Detail
# =============================================================================
@stay_media_bp.route("/media/<int:media_id>",methods=["GET"],)
@admin_required
def detail(media_id):
    """
    Display a single StayMedia assignment.
    """

    media = get_stay_media(media_id)

    if media is None:
        flash(
            "Stay media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    return render_template(
        "admin/stays/media/detail.html",
        media=media,
        stay=media.stay,
    )


# =============================================================================
# Stay Media Edit
# =============================================================================

@stay_media_bp.route(
    "/media/<int:media_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(media_id):
    """
    Edit an existing StayMedia assignment.
    """

    media = get_stay_media(media_id)

    if media is None:
        flash(
            "Stay media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    stay = media.stay

    if stay is None:
        flash(
            "The Stay associated with this media could not be found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayMediaForm(
        obj=media,
    )

    # -------------------------------------------------------------------------
    # Folder-scoped media choices
    # -------------------------------------------------------------------------

    form.set_media_choices(
        stay.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Preview data
    # -------------------------------------------------------------------------

    media_asset_preview_map = _build_media_asset_preview_map(
        stay.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    if form.validate_on_submit():
        try:
            update_stay_media(
                acting_admin=current_user,
                media=media,
                stay_id=stay.id,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,
            )

            flash(
                "Stay media was updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_media.detail",
                    media_id=media.id,
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/stays/media/edit.html",
        form=form,
        media=media,
        stay=stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Stay Media Activate
# =============================================================================

@stay_media_bp.route(
    "/media/<int:media_id>/activate",
    methods=["POST"],
)
@admin_required
def activate(media_id):
    """
    Activate a StayMedia assignment.
    """

    media = get_stay_media(media_id)

    if media is None:
        flash(
            "Stay media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    try:
        activate_stay_media(
            acting_admin=current_user,
            media=media,
        )

        flash(
            "Stay media was activated.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_media.detail",
            media_id=media.id,
        )
    )


# =============================================================================
# Stay Media Deactivate
# =============================================================================

@stay_media_bp.route(
    "/media/<int:media_id>/deactivate",
    methods=["POST"],
)
@admin_required
def deactivate(media_id):
    """
    Deactivate a StayMedia assignment.
    """

    media = get_stay_media(media_id)

    if media is None:
        flash(
            "Stay media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    try:
        deactivate_stay_media(
            acting_admin=current_user,
            media=media,
        )

        flash(
            "Stay media was deactivated.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_media.detail",
            media_id=media.id,
        )
    )


# =============================================================================
# Stay Media Delete
# =============================================================================

@stay_media_bp.route(
    "/media/<int:media_id>/delete",
    methods=["POST"],
)
@admin_required
def delete(media_id):
    """
    Delete a StayMedia relationship.

    The underlying MediaAsset remains in the Media Library.
    """

    media = get_stay_media(media_id)

    if media is None:
        flash(
            "Stay media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    stay_id = media.stay_id

    try:
        delete_stay_media(
            acting_admin=current_user,
            media=media,
        )

        flash(
            "Stay media was deleted.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_media.index",
            stay_id=stay_id,
        )
    )


# =============================================================================
# Room Media
# =============================================================================

@stay_media_bp.route(
    "/rooms/<int:room_id>/media/",
    methods=["GET"],
)
@admin_required
def room_index(room_id):
    """
    Display all media assignments for a specific StayRoom.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Room not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    media_items = get_room_media(
        room_id=room.id,
        active_only=False,
    )

    return render_template(
        "admin/stays/rooms/media/index.html",
        room=room,
        stay=room.stay,
        media_items=media_items,
    )


# =============================================================================
# Room Media Create
# =============================================================================

@stay_media_bp.route(
    "/rooms/<int:room_id>/media/create",
    methods=["GET", "POST"],
)
@admin_required
def room_create(room_id):
    """
    Create a media assignment for a specific StayRoom.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Room not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayRoomMediaForm()

    # -------------------------------------------------------------------------
    # Folder-scoped media choices
    # -------------------------------------------------------------------------

    form.set_media_choices(
        room.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Preview data
    # -------------------------------------------------------------------------

    media_asset_preview_map = _build_media_asset_preview_map(
        room.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    if form.validate_on_submit():
        try:
            create_stay_room_media(
                acting_admin=current_user,
                room_id=room.id,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,
            )

            flash(
                "Room media was added successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_media.room_index",
                    room_id=room.id,
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/stays/rooms/media/create.html",
        form=form,
        room=room,
        stay=room.stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Room Media Edit
# =============================================================================

@stay_media_bp.route(
    "/rooms/media/<int:room_media_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def room_edit(room_media_id):
    """
    Edit an existing StayRoomMedia assignment.
    """

    media = get_stay_room_media(
        room_media_id,
    )

    if media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    room = media.room

    if room is None:
        flash(
            "The room associated with this media could not be found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayRoomMediaForm(
        obj=media,
    )

    # -------------------------------------------------------------------------
    # Folder-scoped media choices
    # -------------------------------------------------------------------------

    form.set_media_choices(
        room.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Preview data
    # -------------------------------------------------------------------------

    media_asset_preview_map = _build_media_asset_preview_map(
        room.media_folder_id
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    if form.validate_on_submit():
        try:
            update_stay_room_media(
                acting_admin=current_user,
                room_media=media,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,
            )

            flash(
                "Room media was updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_media.room_detail",
                    room_media_id=media.id,
                )
            )

        except ValueError as exc:
            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/stays/rooms/media/edit.html",
        form=form,
        media=media,
        room=room,
        stay=room.stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Room Media Detail
# =============================================================================

@stay_media_bp.route(
    "/rooms/media/<int:room_media_id>",
    methods=["GET"],
)
@admin_required
def room_detail(room_media_id):
    """
    Display a single StayRoomMedia assignment.
    """

    media = get_stay_room_media(
        room_media_id,
    )

    if media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    room = media.room

    if room is None:
        flash(
            "The room associated with this media could not be found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    stay = room.stay

    if stay is None:
        flash(
            "The property associated with this room could not be found.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_stay_room.detail",
                room_id=room.id,
            )
        )

    return render_template(
        "admin/stays/rooms/media/detail.html",
        media=media,
        room=room,
        stay=stay,
    )


# =============================================================================
# Room Media Activate
# =============================================================================

@stay_media_bp.route(
    "/rooms/media/<int:room_media_id>/activate",
    methods=["POST"],
)
@admin_required
def room_activate(room_media_id):
    """
    Activate a StayRoomMedia assignment.
    """

    media = get_stay_room_media(room_media_id,)
    if media is None:
        flash("Room media not found.","danger",)
        return redirect(url_for("admin_stay.index"))

    try:
        activate_stay_room_media(
            acting_admin=current_user,
            room_media=media,)

        flash("Room media was activated.","success",)

    except ValueError as exc:
        flash(str(exc),"danger",)

    return redirect(
        url_for("admin_stay_media.room_detail",room_media_id=media.id,))

# =============================================================================
# Room Media Deactivate
# =============================================================================
@stay_media_bp.route("/rooms/media/<int:room_media_id>/deactivate",methods=["POST"],)
@admin_required
def room_deactivate(room_media_id):
    """
    Deactivate a StayRoomMedia assignment.
    """
    media = get_stay_room_media(room_media_id,)

    if media is None:
        flash("Room media not found.","danger",)
        return redirect(url_for("admin_stay.index"))

    try:
        deactivate_stay_room_media(
            acting_admin=current_user,
            room_media=media,)

        flash("Room media was deactivated.","success",)

    except ValueError as exc:
        flash(str(exc),"danger",)

    return redirect(
        url_for("admin_stay_media.room_detail",room_media_id=media.id,))

# =============================================================================
# Room Media Delete
# =============================================================================
@stay_media_bp.route("/rooms/media/<int:room_media_id>/delete",methods=["POST"],)
@admin_required
def room_delete(room_media_id):
    """
    Delete a StayRoomMedia relationship.
    The underlying MediaAsset remains safely in the central Media Library.
    """

    media = get_stay_room_media(room_media_id,)
    if media is None:
        flash(
            "Room media not found.","danger",)
        return redirect(url_for("admin_stay.index"))
    room_id = media.room_id

    try:
        delete_stay_room_media(
            acting_admin=current_user,
            room_media=media,)
        flash("Room media was deleted.","success",)

    except ValueError as exc:
        flash(str(exc),"danger",)

    return redirect(
        url_for(
            "admin_stay_media.room_index",
            room_id=room_id,))