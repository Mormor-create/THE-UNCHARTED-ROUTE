from __future__ import annotations

from typing import Optional

from sqlalchemy import or_

from extensions import db
from app.models.stay_room import StayRoom
from app.models.stay_room_amenity import StayRoomAmenity

def _require_admin(user):
    return None


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_stay_room_amenity(
    amenity_id: int,
) -> Optional[StayRoomAmenity]:
    if not amenity_id:
        return None

    return db.session.get(
        StayRoomAmenity,
        amenity_id,
    )


def get_stay_room_amenities(
    room_id: Optional[int] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
    featured_only: bool = False,
):
    query = StayRoomAmenity.query

    if room_id:
        query = query.filter(
            StayRoomAmenity.room_id == room_id
        )

    if search:
        term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                StayRoomAmenity.name.ilike(term),
                StayRoomAmenity.description.ilike(term),
            )
        )

    if category:
        query = query.filter(
            StayRoomAmenity.category == category
        )

    if active_only:
        query = query.filter(
            StayRoomAmenity.active.is_(True)
        )

    if featured_only:
        query = query.filter(
            StayRoomAmenity.featured.is_(True)
        )

    return (
        query
        .order_by(
            StayRoomAmenity.display_order.asc(),
            StayRoomAmenity.name.asc(),
            StayRoomAmenity.id.asc(),
        )
        .all()
    )


def get_active_stay_room_amenities(room_id: int):
    return get_stay_room_amenities(
        room_id=room_id,
        active_only=True,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_stay_room_amenity(
    acting_admin,
    *,
    room_id,
    name,
    description=None,
    category="Room",
    icon=None,
    active=True,
    featured=False,
    display_order=0,
):
    _require_admin(acting_admin)

    room = db.session.get(
        StayRoom,
        room_id,
    )

    if room is None:
        raise ValueError("Room not found.")

    name = (name or "").strip()

    if not name:
        raise ValueError(
            "Room amenity name is required."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    amenity = StayRoomAmenity(
        room_id=room.id,
        name=name,
        description=description,
        category=category,
        icon=icon,
        active=bool(active),
        featured=bool(featured),
        display_order=display_order,
    )

    db.session.add(amenity)
    db.session.commit()

    return amenity


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_stay_room_amenity(
    acting_admin,
    *,
    amenity,
    room_id,
    name,
    description=None,
    category="Room",
    icon=None,
    active=True,
    featured=False,
    display_order=0,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Room amenity not found."
        )

    room = db.session.get(
        StayRoom,
        room_id,
    )

    if room is None:
        raise ValueError("Room not found.")

    name = (name or "").strip()

    if not name:
        raise ValueError(
            "Room amenity name is required."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    amenity.room_id = room.id
    amenity.name = name
    amenity.description = description
    amenity.category = category
    amenity.icon = icon
    amenity.active = bool(active)
    amenity.featured = bool(featured)
    amenity.display_order = display_order

    db.session.commit()

    return amenity


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def activate_stay_room_amenity(
    acting_admin,
    amenity,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Room amenity not found."
        )

    amenity.active = True
    db.session.commit()

    return amenity


def deactivate_stay_room_amenity(
    acting_admin,
    amenity,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Room amenity not found."
        )

    amenity.active = False
    db.session.commit()

    return amenity


def set_stay_room_amenity_featured(
    acting_admin,
    amenity,
    featured=True,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Room amenity not found."
        )

    amenity.featured = bool(featured)
    db.session.commit()

    return amenity


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_stay_room_amenity(
    acting_admin,
    amenity,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Room amenity not found."
        )

    db.session.delete(amenity)
    db.session.commit()

    return True