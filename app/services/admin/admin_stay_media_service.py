"""
===============================================================================
The Uncharted Route
Admin Stay Media Service
===============================================================================

Service-layer operations for managing the relationship between Stay records
and MediaAsset records.

The service is responsible for:
• Stay media queries
• Stay and media validation
• Media-folder scoping
• Creating and updating StayMedia records
• Activating/deactivating media
• Display ordering
• Deleting StayMedia relationships

The underlying MediaAsset is never deleted when a StayMedia relationship
is removed.
"""

from __future__ import annotations

from typing import Optional

from extensions import db
from app.models.media_asset import MediaAsset
from app.models.stay import Stay
from app.models.stay_media import StayMedia


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

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

def get_stay_media(media_id: int) -> Optional[StayMedia]:
    """Return a single StayMedia record by ID."""

    if not media_id:
        return None

    return db.session.get(
        StayMedia,
        media_id,
    )


def get_stay_media_items(
    stay_id: int,
    usage: Optional[str] = None,
    active_only: bool = False,
):
    """Return media assigned to a specific Stay."""

    query = StayMedia.query.filter(
        StayMedia.stay_id == stay_id
    )

    if usage:
        query = query.filter(
            StayMedia.usage == usage
        )

    if active_only:
        query = query.filter(
            StayMedia.active.is_(True)
        )

    return (
        query
        .order_by(
            StayMedia.display_order.asc(),
            StayMedia.id.asc(),
        )
        .all()
    )


def get_stay_hero_media(stay_id: int):
    """Return the first active hero media item for a Stay."""

    return (
        StayMedia.query
        .filter(
            StayMedia.stay_id == stay_id,
            StayMedia.usage == "hero",
            StayMedia.active.is_(True),
        )
        .order_by(
            StayMedia.display_order.asc(),
            StayMedia.id.asc(),
        )
        .first()
    )


def get_stay_banner_media(stay_id: int):
    """Return the first active banner media item for a Stay."""

    return (
        StayMedia.query
        .filter(
            StayMedia.stay_id == stay_id,
            StayMedia.usage == "banner",
            StayMedia.active.is_(True),
        )
        .order_by(
            StayMedia.display_order.asc(),
            StayMedia.id.asc(),
        )
        .first()
    )


def get_stay_thumbnail_media(stay_id: int):
    """Return the first active thumbnail media item for a Stay."""

    return (
        StayMedia.query
        .filter(
            StayMedia.stay_id == stay_id,
            StayMedia.usage == "thumbnail",
            StayMedia.active.is_(True),
        )
        .order_by(
            StayMedia.display_order.asc(),
            StayMedia.id.asc(),
        )
        .first()
    )


def get_stay_gallery_media(stay_id: int):
    """Return active gallery media for a Stay."""

    return get_stay_media_items(
        stay_id=stay_id,
        usage="gallery",
        active_only=True,
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_stay(stay_id: int) -> Stay:
    """Return the Stay or raise a validation error."""

    stay = db.session.get(
        Stay,
        stay_id,
    )

    if stay is None:
        raise ValueError(
            "Stay not found."
        )

    return stay


def _validate_media_asset(
    media_asset_id: int,
    *,
    stay: Stay,
) -> MediaAsset:
    """
    Validate a MediaAsset for use with a specific Stay.

    The asset must:
    • exist
    • be active
    • be an image or video
    • belong to the Stay's assigned media folder

    MediaAsset uses the hierarchical MediaAssetFolder relationship for
    DAM organization. The legacy MediaAsset.folder string is not used
    for folder scoping.

    A MediaAsset may belong to multiple DAM folders, so the validation
    succeeds when at least one folder assignment matches the Stay's
    assigned media folder.
    """

    media = db.session.get(
        MediaAsset,
        media_asset_id,
    )

    if media is None:
        raise ValueError(
            "Media asset not found."
        )

    if not media.active:
        raise ValueError(
            "The selected media asset is inactive."
        )

    if not (
        media.is_image
        or media.is_video
    ):
        raise ValueError(
            "Only image and video media can be attached to a stay."
        )

    if not stay.media_folder_id:
        raise ValueError(
            "This stay does not have a media folder assigned."
        )

    belongs_to_stay_folder = any(
        assignment.folder is not None
        and assignment.folder.id == stay.media_folder_id
        for assignment in media.folder_assignments.all()
    )

    if not belongs_to_stay_folder:
        raise ValueError(
            "The selected media asset does not belong to this stay's media folder."
        )

    return media


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_stay_media(
    acting_admin,
    *,
    stay_id,
    media_asset_id,
    usage="gallery",
    display_order=0,
    caption=None,
    active=True,
):
    """Create a StayMedia relationship."""

    _require_admin(acting_admin)

    stay = _validate_stay(stay_id)

    media = _validate_media_asset(
        media_asset_id,
        stay=stay,
    )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    item = StayMedia(
        stay_id=stay.id,
        media_asset_id=media.id,
        usage=usage,
        display_order=display_order,
        caption=caption,
        active=bool(active),
    )

    db.session.add(item)
    db.session.commit()

    return item


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_stay_media(
    acting_admin,
    *,
    media,
    stay_id,
    media_asset_id,
    usage="gallery",
    display_order=0,
    caption=None,
    active=True,
):
    """Update an existing StayMedia relationship."""

    _require_admin(acting_admin)

    if media is None:
        raise ValueError(
            "Stay media record not found."
        )

    stay = _validate_stay(stay_id)

    asset = _validate_media_asset(
        media_asset_id,
        stay=stay,
    )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    media.stay_id = stay.id
    media.media_asset_id = asset.id
    media.usage = usage
    media.display_order = display_order
    media.caption = caption
    media.active = bool(active)

    db.session.commit()

    return media


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def activate_stay_media(acting_admin, media):
    """Activate a StayMedia relationship."""

    _require_admin(acting_admin)

    if media is None:
        raise ValueError(
            "Stay media record not found."
        )

    media.active = True
    db.session.commit()

    return media


def deactivate_stay_media(acting_admin, media):
    """Deactivate a StayMedia relationship."""

    _require_admin(acting_admin)

    if media is None:
        raise ValueError(
            "Stay media record not found."
        )

    media.active = False
    db.session.commit()

    return media


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

def set_stay_media_display_order(
    acting_admin,
    media,
    display_order,
):
    """Update the display order of a StayMedia relationship."""

    _require_admin(acting_admin)

    if media is None:
        raise ValueError(
            "Stay media record not found."
        )

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    media.display_order = display_order

    db.session.commit()

    return media


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def delete_stay_media(acting_admin, media):
    """
    Delete a StayMedia relationship.

    This removes only the relationship record. It does not delete the
    underlying MediaAsset from the Media Library.
    """

    _require_admin(acting_admin)

    if media is None:
        raise ValueError(
            "Stay media record not found."
        )

    db.session.delete(media)
    db.session.commit()

    return True