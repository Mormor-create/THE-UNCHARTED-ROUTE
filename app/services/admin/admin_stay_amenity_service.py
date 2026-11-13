from __future__ import annotations

from typing import Optional

from sqlalchemy import or_

from extensions import db
from app.models.stay import Stay
from app.models.stay_amenity import StayAmenity

def _require_admin(user):
    return None


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_stay_amenity(amenity_id: int) -> Optional[StayAmenity]:
    if not amenity_id:
        return None

    return db.session.get(
        StayAmenity,
        amenity_id,
    )


def get_stay_amenities(
    stay_id: Optional[int] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
    featured_only: bool = False,
):
    query = StayAmenity.query

    if stay_id:
        query = query.filter(
            StayAmenity.stay_id == stay_id
        )

    if search:
        term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                StayAmenity.name.ilike(term),
                StayAmenity.description.ilike(term),
            )
        )

    if category:
        query = query.filter(
            StayAmenity.category == category
        )

    if active_only:
        query = query.filter(
            StayAmenity.active.is_(True)
        )

    if featured_only:
        query = query.filter(
            StayAmenity.featured.is_(True)
        )

    return (
        query
        .order_by(
            StayAmenity.display_order.asc(),
            StayAmenity.name.asc(),
            StayAmenity.id.asc(),
        )
        .all()
    )


def get_active_stay_amenities(stay_id: int):
    return get_stay_amenities(
        stay_id=stay_id,
        active_only=True,
    )


def get_featured_stay_amenities(stay_id: int):
    return get_stay_amenities(
        stay_id=stay_id,
        active_only=True,
        featured_only=True,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_stay_amenity(
    acting_admin,
    *,
    stay_id,
    name,
    description=None,
    category="General",
    icon=None,
    active=True,
    featured=False,
    display_order=0,
):
    _require_admin(acting_admin)

    stay = db.session.get(Stay, stay_id)

    if stay is None:
        raise ValueError("Stay not found.")

    name = (name or "").strip()

    if not name:
        raise ValueError(
            "Amenity name is required."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    amenity = StayAmenity(
        stay_id=stay.id,
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

def update_stay_amenity(
    acting_admin,
    *,
    amenity,
    stay_id,
    name,
    description=None,
    category="General",
    icon=None,
    active=True,
    featured=False,
    display_order=0,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError(
            "Amenity not found."
        )

    stay = db.session.get(Stay, stay_id)

    if stay is None:
        raise ValueError("Stay not found.")

    name = (name or "").strip()

    if not name:
        raise ValueError(
            "Amenity name is required."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    amenity.stay_id = stay.id
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
# Status / featured
# ---------------------------------------------------------------------------

def activate_stay_amenity(acting_admin, amenity):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError("Amenity not found.")

    amenity.active = True
    db.session.commit()

    return amenity


def deactivate_stay_amenity(acting_admin, amenity):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError("Amenity not found.")

    amenity.active = False
    db.session.commit()

    return amenity


def set_stay_amenity_featured(
    acting_admin,
    amenity,
    featured=True,
):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError("Amenity not found.")

    amenity.featured = bool(featured)
    db.session.commit()

    return amenity


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_stay_amenity(acting_admin, amenity):
    _require_admin(acting_admin)

    if amenity is None:
        raise ValueError("Amenity not found.")

    db.session.delete(amenity)
    db.session.commit()

    return True