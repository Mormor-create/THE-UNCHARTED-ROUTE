from __future__ import annotations
from typing import Optional
from sqlalchemy import or_
from extensions import db
from app.models.stay import Stay
from app.models.stay_room import StayRoom
from app.services.media_service import get_media_folder

# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------
def _require_admin(user):
    """
    Stay authorization is temporarily disabled during CMS setup/testing.
    """
    return None

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
def get_stay_room(room_id: int) -> Optional[StayRoom]:
    if not room_id:
        return None

    return db.session.get(StayRoom, room_id)


def get_stay_room_by_code(
    room_code: str,
    exclude_room_id: Optional[int] = None,
):
    if not room_code:
        return None

    query = StayRoom.query.filter(
        StayRoom.room_code == room_code.strip()
    )

    if exclude_room_id:
        query = query.filter(
            StayRoom.id != exclude_room_id
        )

    return query.first()


def get_stay_room_by_slug(
    slug: str,
    exclude_room_id: Optional[int] = None,
):
    if not slug:
        return None

    query = StayRoom.query.filter(
        StayRoom.slug == slug.strip()
    )

    if exclude_room_id:
        query = query.filter(
            StayRoom.id != exclude_room_id
        )

    return query.first()


def get_stay_rooms(
    stay_id: Optional[int] = None,
    search: Optional[str] = None,
    room_type: Optional[str] = None,
    availability_status: Optional[str] = None,
    active_only: bool = False,
):
    query = StayRoom.query

    if stay_id:
        query = query.filter(
            StayRoom.stay_id == stay_id
        )

    if search:
        term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                StayRoom.room_code.ilike(term),
                StayRoom.name.ilike(term),
                StayRoom.short_description.ilike(term),
            )
        )

    if room_type:
        query = query.filter(
            StayRoom.room_type == room_type
        )

    if availability_status:
        query = query.filter(
            StayRoom.availability_status == availability_status
        )

    if active_only:
        query = query.filter(
            StayRoom.active.is_(True)
        )

    return (
        query
        .order_by(
            StayRoom.display_order.asc(),
            StayRoom.name.asc(),
            StayRoom.id.asc(),
        )
        .all()
    )


def get_active_stay_rooms(stay_id: int):
    return get_stay_rooms(
        stay_id=stay_id,
        active_only=True,
    )


def get_stay_room_count(
    stay_id: Optional[int] = None,
    active_only: bool = False,
):
    query = StayRoom.query

    if stay_id:
        query = query.filter(
            StayRoom.stay_id == stay_id
        )

    if active_only:
        query = query.filter(
            StayRoom.active.is_(True)
        )

    return query.count()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_stay(stay_id: int) -> Stay:
    stay = db.session.get(Stay, stay_id)

    if stay is None:
        raise ValueError("Stay not found.")

    return stay


def _validate_media_folder(
    media_folder_id: Optional[int],
):
    """
    Validate the selected Stay Room media folder.

    The route/form layer is responsible for limiting the available choices
    to the Stays Rooms media-library branch belonging to the parent Stay.
    This service validates that the submitted folder exists and is active.
    """
    if not media_folder_id:
        return None

    folder = get_media_folder(media_folder_id)

    if folder is None:
        raise ValueError(
            "The selected room media folder does not exist."
        )

    if not folder.active:
        raise ValueError(
            "The selected room media folder is inactive."
        )

    return folder


def _validate_capacity(
    maximum_guests,
    maximum_adults,
    maximum_children,
    minimum_guests,
):
    if maximum_guests is None or maximum_guests < 1:
        raise ValueError(
            "Maximum guests must be at least 1."
        )

    if maximum_adults is None or maximum_adults < 1:
        raise ValueError(
            "Maximum adults must be at least 1."
        )

    if maximum_children is None or maximum_children < 0:
        raise ValueError(
            "Maximum children cannot be negative."
)

    if minimum_guests is None or minimum_guests < 1:
        raise ValueError("Minimum guests must be at least 1.")

    if maximum_adults > maximum_guests:
        raise ValueError("Maximum adults cannot exceed maximum guests.")

    if maximum_children > maximum_guests:
        raise ValueError("Maximum children cannot exceed maximum guests.")

    if maximum_adults + maximum_children > maximum_guests:
        raise ValueError("Maximum adults and children cannot exceed maximum guests.")

    if minimum_guests > maximum_guests:
        raise ValueError("Minimum guests cannot exceed maximum guests.")

def _validate_unique_code(
    room_code,
    exclude_room_id=None,
):
    existing = get_stay_room_by_code(
        room_code,
        exclude_room_id=exclude_room_id,
    )

    if existing:
        raise ValueError(
            "A room with this room code already exists."
        )


def _validate_unique_slug(
    slug,
    exclude_room_id=None,
):
    existing = get_stay_room_by_slug(
        slug,
        exclude_room_id=exclude_room_id,
    )

    if existing:
        raise ValueError(
            "A room with this slug already exists."
        )

# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def create_stay_room(
    acting_admin,
    *,
    stay_id,
    room_code,
    name,
    slug,
    room_type,
    short_description=None,
    description=None,
    maximum_guests=2,
    maximum_adults=2,
    maximum_children=0,
    minimum_guests=1,
    total_units=1,
    nightly_rate=0,
    currency="KES",
    meal_plan="Bed & Breakfast",
    bed_configuration=None,
    floor=None,
    size_description=None,
    availability_status="Available",
    media_folder_id=None,
    featured=False,
    active=True,
    display_order=0,
):
    _require_admin(acting_admin)

    stay = _validate_stay(stay_id)

    room_code = (room_code or "").strip()
    slug = (slug or "").strip()
    name = (name or "").strip()

    if not room_code:
        raise ValueError("Room code is required.")

    if not name:
        raise ValueError("Room name is required.")

    if not slug:
        raise ValueError("Room slug is required.")

    _validate_unique_code(room_code)
    _validate_unique_slug(slug)

    _validate_capacity(
        maximum_guests,
        maximum_adults,
        maximum_children,
        minimum_guests,
    )

    _validate_media_folder(media_folder_id)

    if total_units is None or total_units < 1:
        raise ValueError(
            "Total room units must be at least 1."
        )

    if nightly_rate is None or nightly_rate < 0:
        raise ValueError(
            "Nightly rate cannot be negative."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    room = StayRoom(
        stay_id=stay.id,
        room_code=room_code,
        name=name,
        slug=slug,
        room_type=room_type,
        short_description=short_description,
        description=description,
        maximum_guests=maximum_guests,
        maximum_adults=maximum_adults,
        maximum_children=maximum_children,
        minimum_guests=minimum_guests,
        total_units=total_units,
        nightly_rate=nightly_rate,
        currency=currency,
        meal_plan=meal_plan,
        bed_configuration=bed_configuration,
        floor=floor,
        size_description=size_description,
        availability_status=availability_status,
        media_folder_id=media_folder_id,
        featured=bool(featured),
        active=bool(active),
        display_order=display_order,
    )

    db.session.add(room)
    db.session.commit()

    return room


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_stay_room(
    acting_admin,
    *,
    room,
    stay_id,
    room_code,
    name,
    slug,
    room_type,
    short_description=None,
    description=None,
    maximum_guests=2,
    maximum_adults=2,
    maximum_children=0,
    minimum_guests=1,
    total_units=1,
    nightly_rate=0,
    currency="KES",
    meal_plan="Bed & Breakfast",
    bed_configuration=None,
    floor=None,
    size_description=None,
    availability_status="Available",
    media_folder_id=None,
    featured=False,
    active=True,
    display_order=0,
):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    stay = _validate_stay(stay_id)

    room_code = (room_code or "").strip()
    name = (name or "").strip()
    slug = (slug or "").strip()

    if not room_code:
        raise ValueError("Room code is required.")

    if not name:
        raise ValueError("Room name is required.")

    if not slug:
        raise ValueError("Room slug is required.")

    _validate_unique_code(
        room_code,
        exclude_room_id=room.id,
    )

    _validate_unique_slug(
        slug,
        exclude_room_id=room.id,
    )

    _validate_capacity(
        maximum_guests,
        maximum_adults,
        maximum_children,
        minimum_guests,
    )

    _validate_media_folder(media_folder_id)

    if total_units is None or total_units < 1:
        raise ValueError(
            "Total room units must be at least 1."
        )

    if nightly_rate is None or nightly_rate < 0:
        raise ValueError(
            "Nightly rate cannot be negative."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    room.stay_id = stay.id
    room.room_code = room_code
    room.name = name
    room.slug = slug
    room.room_type = room_type
    room.short_description = short_description
    room.description = description
    room.maximum_guests = maximum_guests
    room.maximum_adults = maximum_adults
    room.maximum_children = maximum_children
    room.minimum_guests = minimum_guests
    room.total_units = total_units
    room.nightly_rate = nightly_rate
    room.currency = currency
    room.meal_plan = meal_plan
    room.bed_configuration = bed_configuration
    room.floor = floor
    room.size_description = size_description
    room.availability_status = availability_status
    room.media_folder_id = media_folder_id
    room.featured = bool(featured)
    room.active = bool(active)
    room.display_order = display_order
    db.session.commit()
    return room

# ---------------------------------------------------------------------------
# Status / featured
# ---------------------------------------------------------------------------
def activate_stay_room(acting_admin, room):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    room.active = True
    db.session.commit()
    return room


def deactivate_stay_room(acting_admin, room):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    room.active = False
    db.session.commit()
    return room

def set_stay_room_featured(
    acting_admin,
    room,
    featured=True,):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    room.featured = bool(featured)
    db.session.commit()

    return room


def set_stay_room_display_order(
    acting_admin,
    room,
    display_order,):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    if display_order < 0:
        raise ValueError("Display order cannot be negative.")

    room.display_order = display_order
    db.session.commit()
    return room


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def delete_stay_room(acting_admin, room):
    _require_admin(acting_admin)

    if room is None:
        raise ValueError("Room not found.")

    db.session.delete(room)
    db.session.commit()
    return True