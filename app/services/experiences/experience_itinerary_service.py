"""
===============================================================================
The Uncharted Route
Experience Itinerary Service
===============================================================================

Business logic for managing experiences itineraries.

This service handles:

- Creating itinerary items
- Retrieving itinerary items
- Filtering by day
- Updating itinerary items
- Reordering itinerary items
- Moving items between days
- Deleting itinerary items
- Building grouped itinerary data

Routes should call this service instead of manipulating
ExperienceItinerary records directly.
"""

from datetime import datetime

from app.models import ExperienceItinerary
from extensions import db


# =============================================================================
# Creation
# =============================================================================

def create_itinerary_item(
    experience_id,
    title,
    description,
    day_number=1,
    activity_time=None,
    display_order=0,
):
    """
    Create a new itinerary item for an experiences.
    """

    item = ExperienceItinerary(
        experience_id=experience_id,
        day_number=day_number,
        title=title.strip(),
        activity_time=activity_time.strip()
        if activity_time
        else None,
        description=description.strip(),
        display_order=display_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(item)
    db.session.commit()

    return item


# =============================================================================
# Retrieval
# =============================================================================

def get_itinerary_item(item_id):
    """
    Retrieve a single itinerary item by ID.
    """

    return db.session.get(
        ExperienceItinerary,
        item_id,
    )


def get_experience_itinerary(
    experience_id,
):
    """
    Retrieve all itinerary items for an experiences.

    Items are ordered by:

    1. Day number
    2. Display order
    3. ID
    """

    return ExperienceItinerary.query.filter_by(
        experience_id=experience_id
    ).order_by(
        ExperienceItinerary.day_number.asc(),
        ExperienceItinerary.display_order.asc(),
        ExperienceItinerary.id.asc(),
    ).all()


def get_day_itinerary(
    experience_id,
    day_number,
):
    """
    Retrieve itinerary items for a specific day.
    """

    return ExperienceItinerary.query.filter_by(
        experience_id=experience_id,
        day_number=day_number,
    ).order_by(
        ExperienceItinerary.display_order.asc(),
        ExperienceItinerary.id.asc(),
    ).all()


# =============================================================================
# Update
# =============================================================================

def update_itinerary_item(
    item_id,
    **updates,
):
    """
    Update an itinerary item.

    Only known editable fields are accepted.
    """

    item = get_itinerary_item(
        item_id
    )

    if item is None:
        return None

    allowed_fields = {
        "day_number",
        "title",
        "activity_time",
        "description",
        "display_order",
    }

    for field, value in updates.items():

        if field not in allowed_fields:
            continue

        if field in {
            "title",
            "description",
            "activity_time",
        }:
            if isinstance(value, str):
                value = value.strip()

        setattr(
            item,
            field,
            value,
        )

    item.updated_at = datetime.utcnow()

    db.session.commit()

    return item


# =============================================================================
# Day Management
# =============================================================================

def move_itinerary_item(
    item_id,
    day_number,
):
    """
    Move an itinerary item to another day.
    """

    item = get_itinerary_item(
        item_id
    )

    if item is None:
        return None

    item.day_number = day_number
    item.updated_at = datetime.utcnow()

    db.session.commit()

    return item


# =============================================================================
# Ordering
# =============================================================================

def reorder_itinerary_item(
    item_id,
    display_order,
):
    """
    Change the display order of an itinerary item.
    """

    item = get_itinerary_item(
        item_id
    )

    if item is None:
        return None

    item.display_order = display_order
    item.updated_at = datetime.utcnow()

    db.session.commit()

    return item


def reorder_day_itinerary(
    experience_id,
    day_number,
    item_ids,
):
    """
    Reorder all itinerary items belonging to a specific day.

    item_ids should contain the itinerary item IDs in their
    desired display order.

    Example:

        [8, 5, 7, 9]

    results in:

        item 8 -> order 0
        item 5 -> order 1
        item 7 -> order 2
        item 9 -> order 3
    """

    items = ExperienceItinerary.query.filter(
        ExperienceItinerary.experience_id == experience_id,
        ExperienceItinerary.day_number == day_number,
        ExperienceItinerary.id.in_(item_ids),
    ).all()

    items_by_id = {
        item.id: item
        for item in items
    }

    for position, item_id in enumerate(item_ids):

        item = items_by_id.get(item_id)

        if item is None:
            continue

        item.display_order = position
        item.updated_at = datetime.utcnow()

    db.session.commit()

    return get_day_itinerary(
        experience_id,
        day_number,
    )


# =============================================================================
# Bulk Operations
# =============================================================================

def update_itinerary_items(
    experience_id,
    items,
):
    """
    Bulk update itinerary items.

    Expected format:

        [
            {
                "id": 1,
                "day_number": 1,
                "display_order": 0
            },
            {
                "id": 2,
                "day_number": 1,
                "display_order": 1
            }
        ]

    Only items belonging to the supplied experiences are modified.
    """

    item_ids = [
        item_data.get("id")
        for item_data in items
        if item_data.get("id") is not None
    ]

    if not item_ids:
        return []

    existing_items = ExperienceItinerary.query.filter(
        ExperienceItinerary.experience_id == experience_id,
        ExperienceItinerary.id.in_(item_ids),
    ).all()

    items_by_id = {
        item.id: item
        for item in existing_items
    }

    for item_data in items:

        item = items_by_id.get(
            item_data.get("id")
        )

        if item is None:
            continue

        if "day_number" in item_data:
            item.day_number = item_data["day_number"]

        if "display_order" in item_data:
            item.display_order = item_data["display_order"]

        item.updated_at = datetime.utcnow()

    db.session.commit()

    return get_experience_itinerary(
        experience_id
    )


# =============================================================================
# Deletion
# =============================================================================

def delete_itinerary_item(
    item_id,
):
    """
    Permanently delete an itinerary item.
    """

    item = get_itinerary_item(
        item_id
    )

    if item is None:
        return False

    db.session.delete(item)
    db.session.commit()

    return True


def delete_experience_itinerary(
    experience_id,
):
    """
    Delete all itinerary items belonging to an experiences.
    """

    items = ExperienceItinerary.query.filter_by(
        experience_id=experience_id
    ).all()

    if not items:
        return 0

    for item in items:
        db.session.delete(item)

    db.session.commit()

    return len(items)


# =============================================================================
# Grouped Itinerary
# =============================================================================

def get_grouped_itinerary(
    experience_id,
):
    """
    Return the experiences itinerary grouped by day.

    Example result:

        {
            1: [item1, item2],
            2: [item3, item4],
            3: [item5]
        }
    """

    items = get_experience_itinerary(
        experience_id
    )

    grouped = {}

    for item in items:

        grouped.setdefault(
            item.day_number,
            []
        ).append(item)

    return grouped


# =============================================================================
# Day Summary
# =============================================================================

def get_itinerary_day_numbers(
    experience_id,
):
    """
    Return the unique day numbers used by an experiences.
    """

    items = get_experience_itinerary(
        experience_id
    )

    return sorted({
        item.day_number
        for item in items
    })


def get_itinerary_day_count(
    experience_id,
):
    """
    Return the number of distinct itinerary days.
    """

    return len(
        get_itinerary_day_numbers(
            experience_id
        )
    )


# =============================================================================
# Representation Helpers
# =============================================================================

def get_itinerary_structure(
    experience_id,
):
    """
    Return a presentation-friendly itinerary structure.

    Each day contains its itinerary items.
    """

    grouped = get_grouped_itinerary(
        experience_id
    )

    return [
        {
            "day_number": day_number,
            "items": items,
        }
        for day_number, items in grouped.items()
    ]