"""
===============================================================================
The Uncharted Route
Experience Inclusion Service
===============================================================================

Business logic for managing inclusions belonging to experiences.

Examples:

- Professional Driver Guide
- Bottled Drinking Water
- Hotel Pickup & Drop-off
- Luxury Safari Vehicle
- Picnic Breakfast
- Park Transfers

This service handles:

- Creating inclusions
- Retrieving inclusions
- Updating inclusions
- Reordering inclusions
- Activating/deactivating inclusions
- Bulk creation
- Removing inclusions
- Counting inclusions
"""

from app.models import ExperienceInclusion
from extensions import db


# =============================================================================
# Retrieval
# =============================================================================

def get_inclusion(inclusion_id):
    """
    Retrieve a single inclusion by ID.
    """

    return db.session.get(
        ExperienceInclusion,
        inclusion_id,
    )


def get_experience_inclusions(
    experience_id,
    active_only=True,
):
    """
    Retrieve inclusions belonging to an experiences.

    Results are ordered by display_order and then ID.
    """

    query = ExperienceInclusion.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceInclusion.display_order.asc(),
        ExperienceInclusion.id.asc(),
    ).all()


def get_active_experience_inclusions(
    experience_id,
):
    """
    Retrieve only active inclusions for an experiences.
    """

    return get_experience_inclusions(
        experience_id,
        active_only=True,
    )


def get_inactive_experience_inclusions(
    experience_id,
):
    """
    Retrieve inactive inclusions for an experiences.
    """

    return ExperienceInclusion.query.filter_by(
        experience_id=experience_id,
        active=False,
    ).order_by(
        ExperienceInclusion.display_order.asc(),
        ExperienceInclusion.id.asc(),
    ).all()


def get_inclusion_count(
    experience_id,
    active_only=True,
):
    """
    Return the number of inclusions belonging to an experiences.
    """

    query = ExperienceInclusion.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.count()


# =============================================================================
# Search
# =============================================================================

def search_inclusions(
    experience_id,
    search_term,
    active_only=True,
):
    """
    Search inclusions belonging to an experiences.

    Searches title and description.
    """

    if not search_term:
        return get_experience_inclusions(
            experience_id,
            active_only=active_only,
        )

    term = f"%{search_term.strip()}%"

    query = ExperienceInclusion.query.filter(
        ExperienceInclusion.experience_id == experience_id,
        db.or_(
            ExperienceInclusion.title.ilike(term),
            ExperienceInclusion.description.ilike(term),
        ),
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceInclusion.display_order.asc(),
        ExperienceInclusion.id.asc(),
    ).all()


# =============================================================================
# Creation
# =============================================================================

def create_inclusion(
    experience_id,
    title,
    description=None,
    icon="check-circle",
    display_order=0,
    active=True,
):
    """
    Create an inclusion for an experiences.
    """

    if not title or not title.strip():
        raise ValueError(
            "Inclusion title is required."
        )

    title = title.strip()

    inclusion = ExperienceInclusion(
        experience_id=experience_id,
        title=title,
        description=description.strip()
        if description
        else None,
        icon=icon.strip()
        if icon
        else "check-circle",
        display_order=display_order,
        active=active,
    )

    db.session.add(
        inclusion
    )

    db.session.commit()

    return inclusion


# =============================================================================
# Bulk Creation
# =============================================================================

def create_inclusions(
    experience_id,
    inclusions,
):
    """
    Create multiple inclusions for an experiences.

    Each item should be a dictionary.

    Example:

        [
            {
                "title": "Professional Driver Guide",
                "description": "Experienced safari guide",
                "icon": "user-check",
            },
            {
                "title": "Bottled Drinking Water",
                "icon": "droplets",
            },
        ]

    The supplied order becomes the display order.
    """

    if not inclusions:
        return []

    created = []

    next_order = (
        ExperienceInclusion.query.filter_by(
            experience_id=experience_id
        ).count()
    )

    for inclusion_data in inclusions:

        if not inclusion_data:
            continue

        title = inclusion_data.get(
            "title"
        )

        if not title or not title.strip():
            continue

        inclusion = ExperienceInclusion(
            experience_id=experience_id,
            title=title.strip(),
            description=(
                inclusion_data.get("description").strip()
                if inclusion_data.get("description")
                else None
            ),
            icon=(
                inclusion_data.get("icon").strip()
                if inclusion_data.get("icon")
                else "check-circle"
            ),
            display_order=next_order,
            active=inclusion_data.get(
                "active",
                True,
            ),
        )

        db.session.add(
            inclusion
        )

        created.append(
            inclusion
        )

        next_order += 1

    db.session.commit()

    return created


# =============================================================================
# Update
# =============================================================================

def update_inclusion(
    inclusion_id,
    **updates,
):
    """
    Update an experiences inclusion.

    Supported fields:

    - title
    - description
    - icon
    - display_order
    - active
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        return None

    allowed_fields = {
        "title",
        "description",
        "icon",
        "display_order",
        "active",
    }

    text_fields = {
        "title",
        "description",
        "icon",
    }

    for field, value in updates.items():

        if field not in allowed_fields:
            continue

        if field == "title":

            if not value or not value.strip():
                raise ValueError(
                    "Inclusion title is required."
                )

        if field in text_fields and isinstance(
            value,
            str,
        ):
            value = value.strip()

        setattr(
            inclusion,
            field,
            value,
        )

    db.session.commit()

    return inclusion


# =============================================================================
# Ordering
# =============================================================================

def reorder_inclusion(
    inclusion_id,
    display_order,
):
    """
    Change the display order of a single inclusion.
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        return None

    inclusion.display_order = display_order

    db.session.commit()

    return inclusion


def reorder_experience_inclusions(
    experience_id,
    inclusion_ids,
):
    """
    Reorder all inclusions belonging to an experiences.

    Example:

        [7, 3, 9, 2]

    becomes:

        7 -> 0
        3 -> 1
        9 -> 2
        2 -> 3
    """

    if not inclusion_ids:
        return []

    inclusions = ExperienceInclusion.query.filter(
        ExperienceInclusion.experience_id == experience_id,
        ExperienceInclusion.id.in_(inclusion_ids),
    ).all()

    inclusions_by_id = {
        inclusion.id: inclusion
        for inclusion in inclusions
    }

    for position, inclusion_id in enumerate(
        inclusion_ids
    ):

        inclusion = inclusions_by_id.get(
            inclusion_id
        )

        if inclusion is None:
            continue

        inclusion.display_order = position

    db.session.commit()

    return get_experience_inclusions(
        experience_id,
        active_only=False,
    )


# =============================================================================
# Status Management
# =============================================================================

def activate_inclusion(
    inclusion_id,
):
    """
    Activate an inclusion.
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        return None

    inclusion.active = True

    db.session.commit()

    return inclusion


def deactivate_inclusion(
    inclusion_id,
):
    """
    Deactivate an inclusion.

    The inclusion remains stored in the database.
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        return None

    inclusion.active = False

    db.session.commit()

    return inclusion


# =============================================================================
# Deletion
# =============================================================================

def delete_inclusion(
    inclusion_id,
):
    """
    Permanently delete an inclusion.
    """

    inclusion = get_inclusion(
        inclusion_id
    )

    if inclusion is None:
        return False

    db.session.delete(
        inclusion
    )

    db.session.commit()

    return True


def delete_experience_inclusions(
    experience_id,
):
    """
    Permanently delete all inclusions belonging
    to an experiences.

    Returns the number of deleted inclusions.
    """

    inclusions = ExperienceInclusion.query.filter_by(
        experience_id=experience_id
    ).all()

    if not inclusions:
        return 0

    count = len(
        inclusions
    )

    for inclusion in inclusions:
        db.session.delete(
            inclusion
        )

    db.session.commit()

    return count


# =============================================================================
# Utility
# =============================================================================

def inclusion_belongs_to_experience(
    inclusion_id,
    experience_id,
):
    """
    Determine whether an inclusion belongs to
    a particular experiences.
    """

    return ExperienceInclusion.query.filter_by(
        id=inclusion_id,
        experience_id=experience_id,
    ).first() is not None