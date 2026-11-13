"""
===============================================================================
The Uncharted Route
Admin Stay Room Media Routes
===============================================================================

Administrative routes for managing media assigned to individual StayRoom
records.

Blueprint prefix:
    /admin/stay-room-media

Media-folder scoping
--------------------
Each StayRoom may have its own dedicated media folder.

The media selector therefore loads assets only from the room's exact
media_folder_id. Descendant folders are deliberately excluded.

The form layer restricts the available choices before validation.
The service layer independently validates the selected MediaAsset before
saving.

The route layer additionally builds a preview map for the active image/video
assets available in the room's exact assigned folder.
===============================================================================
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from flask_login import current_user

from app.decorators.admin import admin_required
from app.forms.admin_stay_room_media import (
    AdminStayRoomMediaForm,
)
from app.models import MediaFolder
from app.services.media_service import (
    get_cms_media_assets,
)
from app.services.admin.admin_stay_room_service import (
    get_stay_room,
)
from app.services.admin.admin_stay_room_media_service import (
    activate_stay_room_media,
    create_stay_room_media,
    deactivate_stay_room_media,
    delete_stay_room_media,
    get_room_media,
    get_stay_room_media,
    update_stay_room_media,
)
from extensions import db

stay_room_media_bp = Blueprint(
    "admin_stay_room_media",
    __name__,
    url_prefix="/admin/stay-room-media",
)


# =============================================================================
# Preview Helpers
# =============================================================================

def _build_media_asset_preview_map(folder_id):
    """
    Build the preview data used by the room media forms.

    Only active image/video assets directly belonging to the supplied folder
    are included.

    Descendant folders are intentionally excluded.

    The returned structure is keyed by MediaAsset ID so the frontend can
    immediately resolve the selected asset when the selector changes.

    Example:

        {
            "42": {
                "url": "...",
                "title": "Manor Junior Suite",
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
        active_only=True,
    )

    preview_map = {}

    for asset in assets:
        media_type = getattr(
            asset,
            "media_type",
            None,
        )

        if media_type not in (
            "image",
            "video",
        ):
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
# Index
# =============================================================================

@stay_room_media_bp.route(
    "/room/<int:room_id>/",
    methods=["GET"],
)
@admin_required
def index(room_id):
    """
    Display all media assignments for a specific StayRoom.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    room_media_items = get_room_media(
        room_id=room.id,
        active_only=False,
    )

    return render_template(
        "admin/stays/rooms/media/index.html",
        room=room,
        stay=room.stay,
        room_media_items=room_media_items,
    )


# =============================================================================
# Create
# =============================================================================

@stay_room_media_bp.route(
    "/room/<int:room_id>/create",
    methods=["GET", "POST"],
)
@admin_required
def create(room_id):
    """
    Create a media assignment for a specific StayRoom.
    """

    room = get_stay_room(room_id)

    if room is None:
        flash(
            "Stay room not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    form = AdminStayRoomMediaForm()

    # -------------------------------------------------------------------------
    # Folder-scoped media choices
    # -------------------------------------------------------------------------
    #
    # The form owns the media selector choices.
    #
    # Only assets directly belonging to this room's assigned folder are
    # available. Descendant folders are intentionally excluded.
    # -------------------------------------------------------------------------
    form.set_media_choices(room.media_folder_id)

    # -------------------------------------------------------------------------
    # Preview data
    # -------------------------------------------------------------------------
    media_asset_preview_map = _build_media_asset_preview_map(room.media_folder_id)

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------
    if form.validate_on_submit():
        try:
            room_media = create_stay_room_media(
                acting_admin=current_user,
                room_id=room.id,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,)

            flash("Room media added successfully.","success",)
            return redirect(
                url_for(
                    "admin_stay_room_media.detail",
                    media_id=room_media.id,))

        except ValueError as exc:
            flash(str(exc),"danger",)

        print("=" * 80)
        print("ROOM MEDIA DEBUG")
        print("Room ID:", room.id)
        print("Room Name:", room.name)
        print("Room media_folder_id:", room.media_folder_id)

        if room.media_folder_id:
            room_folder = db.session.get(
                MediaFolder,
                room.media_folder_id,
            )

            print("Folder:", room_folder)
            print(
                "Folder ID:",
                room_folder.id if room_folder else None,
            )
            print(
                "Folder Name:",
                room_folder.name if room_folder else None,
            )
            print(
                "Folder Active:",
                room_folder.active if room_folder else None,
            )

            assets = get_cms_media_assets(
                folder_id=room.media_folder_id,
                include_descendants=False,
                media_type=None,
                active_only=False,
            )

            print("Assets in exact folder:", len(assets))

            for asset in assets:
                print(
                    "  Asset:",
                    asset.id,
                    "|",
                    asset.title,
                    "| type:",
                    asset.media_type,
                    "| active:",
                    asset.active,
                )

        print("=" * 80)

    return render_template(
        "admin/stays/rooms/media/create.html",
        form=form,
        room=room,
        stay=room.stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Detail
# =============================================================================

@stay_room_media_bp.route(
    "/<int:media_id>",
    methods=["GET"],
)
@admin_required
def detail(media_id):
    """
    Display a single room-media assignment.
    """

    room_media = get_stay_room_media(
        media_id,
    )

    if room_media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    room = room_media.room

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
        stay=stay,
        room=room,
        room_media=room_media,
    )


# =============================================================================
# Edit
# =============================================================================

@stay_room_media_bp.route(
    "/<int:media_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(media_id):
    """
    Edit an existing room-media assignment.
    """

    room_media = get_stay_room_media(
        media_id,
    )

    if room_media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    room = room_media.room

    if room is None:
        flash(
            "The room associated with this media could not be found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay.index")
        )

    form = AdminStayRoomMediaForm(
        obj=room_media,
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
                room_media=room_media,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                caption=form.caption.data,
                active=form.active.data,
            )

            flash(
                "Room media updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_room_media.detail",
                    media_id=room_media.id,
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
        room_media=room_media,
        room=room,
        stay=room.stay,
        media_asset_preview_map=media_asset_preview_map,
    )


# =============================================================================
# Activate
# =============================================================================

@stay_room_media_bp.route(
    "/<int:media_id>/activate",
    methods=["POST"],
)
@admin_required
def activate(media_id):
    """
    Activate a room-media assignment.
    """

    room_media = get_stay_room_media(
        media_id,
    )

    if room_media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    try:
        activate_stay_room_media(
            acting_admin=current_user,
            room_media=room_media,
        )

        flash(
            "Room media activated successfully.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_room_media.detail",
            media_id=media_id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================

@stay_room_media_bp.route(
    "/<int:media_id>/deactivate",
    methods=["POST"],
)
@admin_required
def deactivate(media_id):
    """
    Deactivate a room-media assignment.
    """

    room_media = get_stay_room_media(
        media_id,
    )

    if room_media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    try:
        deactivate_stay_room_media(
            acting_admin=current_user,
            room_media=room_media,
        )

        flash(
            "Room media deactivated successfully.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_room_media.detail",
            media_id=media_id,
        )
    )


# =============================================================================
# Delete
# =============================================================================

@stay_room_media_bp.route(
    "/<int:media_id>/delete",
    methods=["POST"],
)
@admin_required
def delete(media_id):
    """
    Delete a room-media relationship.

    The underlying MediaAsset remains safely in the central Media Library.
    """

    room_media = get_stay_room_media(
        media_id,
    )

    if room_media is None:
        flash(
            "Room media not found.",
            "danger",
        )
        return redirect(
            url_for("admin_stay_room.index")
        )

    room_id = room_media.room_id

    try:
        delete_stay_room_media(
            acting_admin=current_user,
            room_media=room_media,
        )

        flash(
            "Room media assignment deleted successfully.",
            "success",
        )

    except ValueError as exc:
        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_stay_room.detail",
            room_id=room_id,
        )
    )