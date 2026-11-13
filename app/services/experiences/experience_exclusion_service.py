"""
===============================================================================
The Uncharted Route
Experience Exclusion Service
===============================================================================

Business logic for managing exclusions belonging to experiences.

Examples:

- Park Entry Fees
- International Flights
- Travel Insurance
- Personal Purchases
- Alcoholic Drinks
- Tips & Gratuities

This service handles:

- Creating exclusions
- Retrieving exclusions
- Searching exclusions
- Updating exclusions
- Reordering exclusions
- Activating/deactivating exclusions
- Bulk creation
- Deleting exclusions
- Counting exclusions
"""

from app.models import ExperienceExclusion
from extensions import db


# =============================================================================
# Retrieval
# =============================================================================

def get_exclusion(exclusion_id):
    """
    Retrieve a single exclusion by ID.
    """

    return db.session.get(
        ExperienceExclusion,
        exclusion_id,
    )


def get_experience_exclusions(
    experience_id,
    active_only=True,
):
    """
    Retrieve exclusions belonging to an experiences.

    Results are ordered by display_order and then ID.
    """

    query = ExperienceExclusion.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceExclusion.display_order.asc(),
        ExperienceExclusion.id.asc(),
    ).all()


def get_active_experience_exclusions(
    experience_id,
):
    """
    Retrieve only active exclusions for an experiences.
    """

    return get_experience_exclusions(
        experience_id,
        active_only=True,
    )


def get_inactive_experience_exclusions(
    experience_id,
):
    """
    Retrieve inactive exclusions for an experiences.
    """

    return get_experience_exclusions(
        experience_id,
        active_only=False,
    )


def get_exclusion_count(
    experience_id,
    active_only=True,
):
    """
    Return the number of exclusions belonging to an experiences.
    """

    query = ExperienceExclusion.query.filter_by(
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

def search_exclusions(
    experience_id,
    search_term,
    active_only=True,
):
    """
    Search exclusions belonging to an experiences.

    Searches title and description.
    """

    if not search_term:
        return get_experience_exclusions(
            experience_id,
            active_only=active_only,
        )

    term = f"%{search_term.strip()}%"

    query = ExperienceExclusion.query.filter(
        ExperienceExclusion.experience_id == experience_id,
        db.or_(
            ExperienceExclusion.title.ilike(term),
            ExperienceExclusion.description.ilike(term),
        ),
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceExclusion.display_order.asc(),
        ExperienceExclusion.id.asc(),
    ).all()


# =============================================================================
# Creation
# =============================================================================

def create_exclusion(
    experience_id,
    title,
    description=None,
    icon="x-circle",
    display_order=0,
    active=True,
):
    """
    Create an exclusion for an experiences.
    """

    if not title or not title.strip():
        raise ValueError(
            "Exclusion title is required."
        )

    exclusion = ExperienceExclusion(
        experience_id=experience_id,
        title=title.strip(),
        description=description.strip()
        if description
        else None,
        icon=icon.strip()
        if icon
        else "x-circle",
        display_order=display_order,
        active=active,
    )

    db.session.add(
        exclusion
    )

    db.session.commit()

    return exclusion


# =============================================================================
# Bulk Creation
# =============================================================================

def create_exclusions(
    experience_id,
    exclusions,
):
    """
    Create multiple exclusions for an experiences.

    Example:

        [
            {
                "title": "Park Entry Fees",
                "description": "Park entrance fees are charged separately.",
                "icon": "ticket",
            },
            {
                "title": "International Flights",
                "icon": "plane",
            },
        ]

    The supplied order becomes the display order.
    """

    if not exclusions:
        return []

    created = []

    next_order = (
        ExperienceExclusion.query.filter_by(
            experience_id=experience_id
        ).count()
    )

    for exclusion_data in exclusions:

        if not exclusion_data:
            continue

        title = exclusion_data.get(
            "title"
        )

        if not title or not title.strip():
            continue

        exclusion = ExperienceExclusion(
            experience_id=experience_id,
            title=title.strip(),
            description=(
                exclusion_data.get("description").strip()
                if exclusion_data.get("description")
                else None
            ),
            icon=(
                exclusion_data.get("icon").strip()
                if exclusion_data.get("icon")
                else "x-circle"
            ),
            display_order=next_order,
            active=exclusion_data.get(
                "active",
                True,
            ),
        )

        db.session.add(
            exclusion
        )

        created.append(
            exclusion
        )

        next_order += 1

    db.session.commit()

    return created


# =============================================================================
# Update
# =============================================================================

def update_exclusion(
    exclusion_id,
    **updates,
):
    """
    Update an experiences exclusion.

    Supported fields:

    - title
    - description
    - icon
    - display_order
    - active
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
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
                    "Exclusion title is required."
                )

        if field in text_fields and isinstance(
            value,
            str,
        ):
            value = value.strip()

        setattr(
            exclusion,
            field,
            value,
        )

    db.session.commit()

    return exclusion


# =============================================================================
# Ordering
# =============================================================================

def reorder_exclusion(
    exclusion_id,
    display_order,
):
    """
    Change the display order of a single exclusion.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        return None

    exclusion.display_order = display_order

    db.session.commit()

    return exclusion


def reorder_experience_exclusions(
    experience_id,
    exclusion_ids,
):
    """
    Reorder all exclusions belonging to an experiences.

    Example:

        [7, 3, 9, 2]

    becomes:

        7 -> 0
        3 -> 1
        9 -> 2
        2 -> 3
    """

    if not exclusion_ids:
        return []

    exclusions = ExperienceExclusion.query.filter(
        ExperienceExclusion.experience_id == experience_id,
        ExperienceExclusion.id.in_(exclusion_ids),
    ).all()

    exclusions_by_id = {
        exclusion.id: exclusion
        for exclusion in exclusions
    }

    for position, exclusion_id in enumerate(
        exclusion_ids
    ):

        exclusion = exclusions_by_id.get(
            exclusion_id
        )

        if exclusion is None:
            continue

        exclusion.display_order = position

    db.session.commit()

    return get_experience_exclusions(
        experience_id,
        active_only=False,
    )


# =============================================================================
# Status Management
# =============================================================================

def activate_exclusion(
    exclusion_id,
):
    """
    Activate an exclusion.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        return None

    exclusion.active = True

    db.session.commit()

    return exclusion


def deactivate_exclusion(
    exclusion_id,
):
    """
    Deactivate an exclusion.

    The exclusion remains stored in the database.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        return None

    exclusion.active = False

    db.session.commit()

    return exclusion


# =============================================================================
# Utility
# =============================================================================

def exclusion_belongs_to_experience(
    exclusion_id,
    experience_id,
):
    """
    Determine whether an exclusion belongs to
    a particular experiences.
    """

    return ExperienceExclusion.query.filter_by(
        id=exclusion_id,
        experience_id=experience_id,
    ).first() is not None


# =============================================================================
# Deletion
# =============================================================================

def delete_exclusion(
    exclusion_id,
):
    """
    Permanently delete an exclusion.
    """

    exclusion = get_exclusion(
        exclusion_id
    )

    if exclusion is None:
        return False

    db.session.delete(
        exclusion
    )

    db.session.commit()

    return True


def delete_experience_exclusions(
    experience_id,
):
    """
    Permanently delete all exclusions belonging
    to an experiences.

    Returns the number of deleted exclusions.
    """

    exclusions = ExperienceExclusion.query.filter_by(
        experience_id=experience_id
    ).all()

    if not exclusions:
        return 0

    count = len(
        exclusions
    )

    for exclusion in exclusions:
        db.session.delete(
            exclusion
        )

    db.session.commit()

    return count


# =============================================================================
# Utility
# =============================================================================

def exclusion_exists(
    experience_id,
    title,
):
    """
    Determine whether an exclusion with the given title
    already exists for an experiences.
    """

    if not title:
        return False

    return ExperienceExclusion.query.filter(
        ExperienceExclusion.experience_id == experience_id,
        db.func.lower(
            ExperienceExclusion.title
        ) == title.strip().lower(),
    ).first() is not None