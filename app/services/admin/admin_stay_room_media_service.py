"""
===============================================================================
The Uncharted Route
Admin Stay Room Media Service
===============================================================================
Service-layer operations for managing the relationship between StayRoom
records and MediaAsset records.

The service is responsible for:
• Stay room media queries
• Room and media validation
• Media-folder scoping
• Creating and updating StayRoomMedia records
• Activating/deactivating media
• Deleting StayRoomMedia relationships

The underlying MediaAsset is never deleted when a StayRoomMedia relationship
is removed.
"""

from __future__ import annotations
from typing import Optional
from extensions import db
from app.models import MediaAsset
from app.models.stay_room import StayRoom
from app.models.stay_room_media import StayRoomMedia

# ---------------------------------------------------------------------------
# Authorization
# --------------------------------------------------------------------------
def _require_admin(user):
    """
    Administrator authorization is currently handled by the route layer.

    This service-level hook is intentionally retained so existing service
    signatures and future authorization integration remain unchanged.
    """
    return None

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
def get_stay_room_media(
    media_id: int,
) -> Optional[StayRoomMedia]:
    """Return a single StayRoomMedia record by ID."""
    if not media_id:
        return None

    return db.session.get(
        StayRoomMedia,
        media_id,)

def get_room_media(
    room_id: int,
    *,
    active_only: bool = False,):
    """Return media assigned to a specific stay room."""
    query = (
        StayRoomMedia.query
        .filter_by(room_id=room_id))

    if active_only:
        query = query.filter(
            StayRoomMedia.active.is_(True))

    return (
        query
        .order_by(
            StayRoomMedia.display_order.asc(),
            StayRoomMedia.id.asc(),).all())

def get_room_media_by_stay(
    stay_id: int,
    *,
    active_only: bool = False,):
    """
    Return all room-media assignments belonging to rooms
    within a specific Stay.
    """
    query = (
        StayRoomMedia.query
        .join(StayRoom)
        .filter(
            StayRoom.stay_id == stay_id
        )
    )

    if active_only:
        query = query.filter(
            StayRoomMedia.active.is_(True)
        )

    return (
        query
        .order_by(
            StayRoomMedia.room_id.asc(),
            StayRoomMedia.display_order.asc(),
            StayRoomMedia.id.asc(),
        )
        .all()
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_room(room_id: int) -> StayRoom:
    """
    Return the StayRoom or raise a validation error.

    The room is validated through the StayRoom model before any media
    relationship is created or updated.
    """
    room = db.session.get(
        StayRoom,
        room_id,
    )

    if room is None:
        raise ValueError(
            "Stay room not found."
        )

    return room


def _validate_media_asset(
    media_asset_id: int,
    *,
    room: StayRoom,
) -> MediaAsset:
    """
    Validate a MediaAsset for use with a specific StayRoom.

    The asset must:
    • exist
    • be active
    • be an image or video
    • belong to the room's assigned media folder

    This is intentionally enforced at service level as well as form level.
    """
    media_asset = db.session.get(
        MediaAsset,
        media_asset_id,
    )

    if media_asset is None:
        raise ValueError(
            "Media asset not found."
        )

    if not media_asset.active:
        raise ValueError(
            "Selected media asset is inactive."
        )

    if not (
        media_asset.is_image
        or media_asset.is_video
    ):
        raise ValueError(
            "Selected media asset is not a supported image or video."
        )

    if not room.media_folder_id:
        raise ValueError(
            "This room does not have a media folder assigned."
        )

    # MediaAsset.folder is the legacy string organization field.
    #
    # The actual hierarchical DAM folder relationship is represented by
    # MediaAssetFolder assignments through media_asset.folder_assignments.
    #
    # A MediaAsset can belong to multiple folders, so we check whether
    # the room's assigned folder exists among those assignments.
    belongs_to_room_folder = any(
        assignment.folder is not None
        and assignment.folder.id == room.media_folder_id
        for assignment in media_asset.folder_assignments.all()
    )

    if not belongs_to_room_folder:
        raise ValueError(
            "Selected media asset does not belong to this room's media folder."
        )

    return media_asset

# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------
def create_stay_room_media(
    acting_admin,
    *,
    room_id: int,
    media_asset_id: int,
    usage: str = "gallery",
    display_order: int = 0,
    caption: Optional[str] = None,
    active: bool = True,):
    """Create a StayRoomMedia assignment."""
    _require_admin(acting_admin)

    room = _validate_room(room_id)

    media_asset = _validate_media_asset(
        media_asset_id,
        room=room,
    )

    usage = (usage or "gallery").strip().lower()

    allowed_usage = {
        "hero",
        "thumbnail",
        "gallery",
    }

    if usage not in allowed_usage:
        raise ValueError(
            "Invalid room media usage."
        )

    if display_order is None:
        display_order = 0

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    # Prevent the exact same media asset from being assigned
    # to the same room more than once.
    existing = (
        StayRoomMedia.query
        .filter_by(
            room_id=room.id,
            media_asset_id=media_asset.id,
        )
        .first()
    )

    if existing is not None:
        raise ValueError(
            "This media asset is already assigned to this room."
        )

    room_media = StayRoomMedia(
        room_id=room.id,
        media_asset_id=media_asset.id,
        usage=usage,
        display_order=display_order,
        caption=caption,
        active=bool(active),
    )

    db.session.add(room_media)
    db.session.commit()

    return room_media


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------
def update_stay_room_media(
    acting_admin,
    *,
    room_media,
    media_asset_id: int,
    usage: str = "gallery",
    display_order: int = 0,
    caption: Optional[str] = None,
    active: bool = True,):
    """Update an existing StayRoomMedia assignment."""
    _require_admin(acting_admin)

    if room_media is None:
        raise ValueError(
            "Room media record not found.")

    room = _validate_room(
        room_media.room_id)

    media_asset = _validate_media_asset(
        media_asset_id,
        room=room,)

    usage = (usage or "gallery").strip().lower()
    allowed_usage = {
        "hero",
        "thumbnail",
        "gallery",}

    if usage not in allowed_usage:
        raise ValueError("Invalid room media usage.")

    if display_order is None:
        display_order = 0

    if display_order < 0:
        raise ValueError("Display order cannot be negative.")

    duplicate = (
        StayRoomMedia.query
        .filter(
            StayRoomMedia.id != room_media.id,
            StayRoomMedia.room_id == room_media.room_id,
            StayRoomMedia.media_asset_id == media_asset.id,).first())

    if duplicate is not None:
        raise ValueError("This media asset is already assigned to this room.")

    room_media.media_asset_id = media_asset.id
    room_media.usage = usage
    room_media.display_order = display_order
    room_media.caption = caption
    room_media.active = bool(active)
    db.session.commit()
    return room_media

# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------
def activate_stay_room_media(
    acting_admin,
    *,
    room_media,):
    """Activate a room-media assignment."""
    _require_admin(acting_admin)

    if room_media is None:
        raise ValueError("Room media record not found.")

    room_media.active = True
    db.session.commit()
    return room_media

def deactivate_stay_room_media(
    acting_admin,
    *,
    room_media,):
    """Deactivate a room-media assignment."""
    _require_admin(acting_admin)

    if room_media is None:
        raise ValueError("Room media record not found.")

    room_media.active = False
    db.session.commit()

    return room_media

# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def delete_stay_room_media(
    acting_admin,
    *,
    room_media,):
    """
    Delete a StayRoomMedia relationship.
    This removes only the relationship record. It does not delete the
    underlying MediaAsset file from the Media Library.
    """
    _require_admin(acting_admin)

    if room_media is None:
        raise ValueError(
            "Room media record not found.")

    db.session.delete(room_media)
    db.session.commit()
    return True