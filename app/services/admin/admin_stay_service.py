from __future__ import annotations
from typing import Optional
from sqlalchemy import or_
from extensions import db
from app.models.destination import Destination
from app.models.stay import Stay
from app.services.media_service import get_media_folder

# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------
def _require_admin(user):
    """
    Stay authorization is temporarily disabled during CMS setup and testing.
    Route-level authorization can be enabled later without changing the
    service logic.
    """
    return None

# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------
def get_stay(stay_id: int) -> Optional[Stay]:
    """Return a single stay by primary key."""
    if not stay_id:
        return None

    return db.session.get(Stay, stay_id)

def get_stay_by_code(stay_code: str) -> Optional[Stay]:
    """Return a stay by its unique stay code."""
    if not stay_code:
        return None

    return (
        Stay.query
        .filter(Stay.stay_code == stay_code.strip())
        .first())

def get_stay_by_slug(slug: str) -> Optional[Stay]:
    """Return a stay by slug."""
    if not slug:
        return None

    return (
        Stay.query
        .filter(Stay.slug == slug.strip())
        .first())

def get_stays(
    search: Optional[str] = None,
    destination_id: Optional[int] = None,
    accommodation_type: Optional[str] = None,
    status: Optional[str] = None,
    featured: Optional[bool] = None,
    active_only: bool = False,
):
    """
    Return stays using optional administration filters.
    """
    query = Stay.query

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Stay.property_name.ilike(search_term),
                Stay.stay_code.ilike(search_term),
                Stay.location.ilike(search_term),
                Stay.short_description.ilike(search_term),
            )
        )

    if destination_id:
        query = query.filter(
            Stay.destination_id == destination_id
        )

    if accommodation_type:
        query = query.filter(
            Stay.accommodation_type == accommodation_type
        )

    if status:
        normalized_status = status.strip().lower()

        if normalized_status == "active":
            query = query.filter(
                Stay.active.is_(True)
            )

        elif normalized_status == "inactive":
            query = query.filter(
                Stay.active.is_(False)
            )

    if featured is not None:
        query = query.filter(
            Stay.featured.is_(featured)
        )

    if active_only:
        query = query.filter(
            Stay.active.is_(True)
        )

    return (
        query
        .order_by(
            Stay.display_order.asc(),
            Stay.property_name.asc(),
            Stay.id.asc(),
        )
        .all()
    )


def get_featured_stays(limit: Optional[int] = None):
    """Return active featured stays."""
    query = (
        Stay.query
        .filter(
            Stay.active.is_(True),
            Stay.featured.is_(True),
        )
        .order_by(
            Stay.display_order.asc(),
            Stay.property_name.asc(),
            Stay.id.asc(),
        )
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_active_stays():
    """Return all active stays."""
    return get_stays(active_only=True)


def get_stays_by_destination(destination_id: int):
    """Return active stays belonging to a destination."""
    if not destination_id:
        return []

    return (
        Stay.query
        .filter(
            Stay.destination_id == destination_id,
            Stay.active.is_(True),
        )
        .order_by(
            Stay.display_order.asc(),
            Stay.property_name.asc(),
            Stay.id.asc(),
        )
        .all()
    )


def get_stay_count(active_only: bool = False) -> int:
    """Return the number of stays."""
    query = Stay.query

    if active_only:
        query = query.filter(
            Stay.active.is_(True)
        )

    return query.count()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_destination(destination_id: int) -> Destination:
    if not destination_id:
        raise ValueError("A destination is required.")

    destination = db.session.get(
        Destination,
        destination_id,
    )

    if destination is None:
        raise ValueError(
            "The selected destination does not exist."
        )

    if not destination.active:
        raise ValueError(
            "The selected destination is inactive."
        )

    return destination


def _validate_media_folder(
    media_folder_id: Optional[int],
):
    """
    Validate the selected Stay property media folder.

    The route/form layer is responsible for restricting the available
    choices to the Stays media-library tree. This service validation only
    confirms that the submitted folder actually exists and is active.
    """
    if not media_folder_id:
        return None

    folder = get_media_folder(media_folder_id)

    if folder is None:
        raise ValueError(
            "The selected media folder does not exist."
        )

    if not folder.active:
        raise ValueError(
            "The selected media folder is inactive."
        )

    return folder


def _validate_unique_code(
    stay_code: str,
    exclude_stay_id: Optional[int] = None,
):
    existing = get_stay_by_code(stay_code)

    if existing and existing.id != exclude_stay_id:
        raise ValueError(
            "A stay with this stay code already exists."
        )


def _validate_unique_slug(
    slug: str,
    exclude_stay_id: Optional[int] = None,
):
    existing = get_stay_by_slug(slug)

    if existing and existing.id != exclude_stay_id:
        raise ValueError(
            "A stay with this slug already exists."
        )


def _validate_capacity(
    maximum_guests,
    maximum_adults,
    maximum_children,
):
    if (
        maximum_guests is not None
        and maximum_guests < 1
    ):
        raise ValueError(
            "Maximum guests must be at least 1."
        )

    if (
        maximum_adults is not None
        and maximum_adults < 1
    ):
        raise ValueError(
            "Maximum adults must be at least 1."
        )

    if (
        maximum_children is not None
        and maximum_children < 0
    ):
        raise ValueError(
            "Maximum children cannot be negative."
        )

    if (
        maximum_guests is not None
        and maximum_adults is not None
        and maximum_adults > maximum_guests
    ):
        raise ValueError(
            "Maximum adults cannot exceed maximum guests."
        )

    if (
        maximum_guests is not None
        and maximum_children is not None
        and maximum_children > maximum_guests
    ):
        raise ValueError(
            "Maximum children cannot exceed maximum guests."
        )

    if (
        maximum_guests is not None
        and maximum_adults is not None
        and maximum_children is not None
        and maximum_adults + maximum_children > maximum_guests
    ):
        raise ValueError(
            "Maximum adults and children cannot exceed maximum guests."
        )

# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def create_stay(
    acting_admin,
    *,
    stay_code,
    property_name,
    slug,
    accommodation_type,
    short_description,
    description,
    location,
    address=None,
    destination_id,
    media_folder_id=None,
    latitude=None,
    longitude=None,
    maximum_guests=None,
    maximum_adults=None,
    maximum_children=None,
    total_rooms=None,
    minimum_nights=1,
    check_in_time=None,
    check_out_time=None,
    contact_phone=None,
    contact_email=None,
    website_url=None,
    meta_title=None,
    meta_description=None,
    featured=False,
    active=True,
    display_order=0,
):
    _require_admin(acting_admin)

    stay_code = (stay_code or "").strip()
    property_name = (property_name or "").strip()
    slug = (slug or "").strip()

    if not stay_code:
        raise ValueError("Stay code is required.")

    if not property_name:
        raise ValueError("Property name is required.")

    if not slug:
        raise ValueError("Slug is required.")

    _validate_unique_code(stay_code)
    _validate_unique_slug(slug)

    _validate_destination(destination_id)
    _validate_media_folder(media_folder_id)

    _validate_capacity(
        maximum_guests,
        maximum_adults,
        maximum_children,
    )

    if minimum_nights is None or minimum_nights < 1:
        raise ValueError(
            "Minimum nights must be at least 1."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    stay = Stay(
        stay_code=stay_code,
        property_name=property_name,
        slug=slug,
        accommodation_type=accommodation_type,
        short_description=short_description,
        description=description,
        location=location,
        address=address,
        destination_id=destination_id,
        media_folder_id=media_folder_id,
        latitude=latitude,
        longitude=longitude,
        maximum_guests=maximum_guests,
        maximum_adults=maximum_adults,
        maximum_children=maximum_children,
        total_rooms=total_rooms,
        minimum_nights=minimum_nights,
        check_in_time=check_in_time,
        check_out_time=check_out_time,
        contact_phone=contact_phone,
        contact_email=contact_email,
        website_url=website_url,
        meta_title=meta_title,
        meta_description=meta_description,
        featured=bool(featured),
        active=bool(active),
        display_order=display_order,)

    db.session.add(stay)
    db.session.commit()

    return stay


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_stay(
    acting_admin,
    *,
    stay,
    stay_code,
    property_name,
    slug,
    accommodation_type,
    short_description,
    description,
    location,
    address=None,
    destination_id,
    media_folder_id=None,
    latitude=None,
    longitude=None,
    maximum_guests=None,
    maximum_adults=None,
    maximum_children=None,
    total_rooms=None,
    minimum_nights=1,
    check_in_time=None,
    check_out_time=None,
    contact_phone=None,
    contact_email=None,
    website_url=None,
    meta_title=None,
    meta_description=None,
    featured=False,
    active=True,
    display_order=0,
):
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    stay_code = (stay_code or "").strip()
    property_name = (property_name or "").strip()
    slug = (slug or "").strip()

    if not stay_code:
        raise ValueError("Stay code is required.")

    if not property_name:
        raise ValueError("Property name is required.")

    if not slug:
        raise ValueError("Slug is required.")

    _validate_unique_code(
        stay_code,
        exclude_stay_id=stay.id,
    )

    _validate_unique_slug(
        slug,
        exclude_stay_id=stay.id,
    )

    _validate_destination(destination_id)
    _validate_media_folder(media_folder_id)

    _validate_capacity(
        maximum_guests,
        maximum_adults,
        maximum_children,
    )

    if minimum_nights is None or minimum_nights < 1:
        raise ValueError(
            "Minimum nights must be at least 1."
        )

    if display_order is None or display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    stay.stay_code = stay_code
    stay.property_name = property_name
    stay.slug = slug
    stay.accommodation_type = accommodation_type
    stay.short_description = short_description
    stay.description = description
    stay.location = location
    stay.address = address
    stay.destination_id = destination_id
    stay.media_folder_id = media_folder_id
    stay.latitude = latitude
    stay.longitude = longitude
    stay.maximum_guests = maximum_guests
    stay.maximum_adults = maximum_adults
    stay.maximum_children = maximum_children
    stay.total_rooms = total_rooms
    stay.minimum_nights = minimum_nights
    stay.check_in_time = check_in_time
    stay.check_out_time = check_out_time
    stay.contact_phone = contact_phone
    stay.contact_email = contact_email
    stay.website_url = website_url
    stay.meta_title = meta_title
    stay.meta_description = meta_description
    stay.featured = bool(featured)
    stay.active = bool(active)
    stay.display_order = display_order

    db.session.commit()

    return stay

# ---------------------------------------------------------------------------
# Status / featured
# ---------------------------------------------------------------------------
def activate_stay(acting_admin, stay):
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    stay.active = True
    db.session.commit()

    return stay

def deactivate_stay(acting_admin, stay):
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    stay.active = False
    db.session.commit()

    return stay

def set_stay_featured(
    acting_admin,
    stay,
    featured: bool = True,
):
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    stay.featured = bool(featured)
    db.session.commit()

    return stay

def set_stay_display_order(
    acting_admin,
    stay,
    display_order: int,
):
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    stay.display_order = display_order

    db.session.commit()
    return stay

# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def delete_stay(acting_admin, stay):
    """
    Permanently delete a stay.

    This should generally only be used during CMS setup/testing.
    Once booking or operational records exist, deactivation should
    normally be preferred.
    """
    _require_admin(acting_admin)

    if stay is None:
        raise ValueError("Stay not found.")

    db.session.delete(stay)
    db.session.commit()

    return True