"""
===============================================================================
The Uncharted Route
Experience Photography Service
===============================================================================

Business logic for managing photography spots associated with experiences.

This service handles the relationship between:

    Experience
        |
        └── ExperiencePhotography
                |
                └── PhotographySpot

An experiences may contain multiple photography spots, while a photography
spot may be used by multiple experiences.

This service manages:

- Adding photography spots to experiences
- Retrieving photography spots for an experiences
- Retrieving experiences associations for a photography spot
- Updating experiences-specific photography information
- Reordering photography stops
- Featuring/unfeaturing photography stops
- Activating/deactivating photography stops
- Removing photography spots from experiences
"""

from datetime import datetime

from app.models import ExperiencePhotography
from extensions import db


# =============================================================================
# Retrieval
# =============================================================================

def get_experience_photography(
    experience_id,
    active_only=True,
):
    """
    Retrieve photography spots associated with an experiences.

    Results are ordered by stop_order.
    """

    query = ExperiencePhotography.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperiencePhotography.stop_order.asc(),
        ExperiencePhotography.id.asc(),
    ).all()


def get_photography_association(
    association_id,
):
    """
    Retrieve a single ExperiencePhotography association.
    """

    return db.session.get(
        ExperiencePhotography,
        association_id,
    )


def get_experience_photography_association(
    experience_id,
    photography_spot_id,
):
    """
    Retrieve the association between an experiences and a photography spot.
    """

    return ExperiencePhotography.query.filter_by(
        experience_id=experience_id,
        photography_spot_id=photography_spot_id,
    ).first()


def get_photography_spot_experiences(
    photography_spot_id,
    active_only=True,
):
    """
    Retrieve all experiences using a photography spot.
    """

    query = ExperiencePhotography.query.filter_by(
        photography_spot_id=photography_spot_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperiencePhotography.stop_order.asc(),
        ExperiencePhotography.id.asc(),
    ).all()


# =============================================================================
# Creation
# =============================================================================

def add_photography_spot(
    experience_id,
    photography_spot_id,
    stop_order=0,
    featured=False,
    active=True,
    notes=None,
):
    """
    Associate a photography spot with an experiences.

    Duplicate associations are prevented.
    """

    existing = get_experience_photography_association(
        experience_id,
        photography_spot_id,
    )

    if existing:
        raise ValueError(
            "This photography spot is already associated "
            "with this experiences."
        )

    association = ExperiencePhotography(
        experience_id=experience_id,
        photography_spot_id=photography_spot_id,
        stop_order=stop_order,
        featured=featured,
        active=active,
        notes=notes.strip() if notes else None,
    )

    db.session.add(
        association
    )

    db.session.commit()

    return association


# =============================================================================
# Bulk Creation
# =============================================================================

def add_photography_spots(
    experience_id,
    photography_spot_ids,
):
    """
    Associate multiple photography spots with an experiences.

    Existing associations are skipped.

    The supplied order becomes the stop order.
    """

    if not photography_spot_ids:
        return []

    existing = ExperiencePhotography.query.filter(
        ExperiencePhotography.experience_id == experience_id,
        ExperiencePhotography.photography_spot_id.in_(
            photography_spot_ids
        ),
    ).all()

    existing_ids = {
        item.photography_spot_id
        for item in existing
    }

    next_order = (
        ExperiencePhotography.query.filter_by(
            experience_id=experience_id
        ).count()
    )

    created = []

    for photography_spot_id in photography_spot_ids:

        if photography_spot_id in existing_ids:
            continue

        association = ExperiencePhotography(
            experience_id=experience_id,
            photography_spot_id=photography_spot_id,
            stop_order=next_order,
            featured=False,
            active=True,
        )

        db.session.add(
            association
        )

        created.append(
            association
        )

        next_order += 1

    db.session.commit()

    return created


# =============================================================================
# Update
# =============================================================================

def update_photography_association(
    association_id,
    **updates,
):
    """
    Update experiences-specific photography information.

    Supported fields:

    - stop_order
    - featured
    - active
    - notes
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    allowed_fields = {
        "stop_order",
        "featured",
        "active",
        "notes",
    }

    for field, value in updates.items():

        if field not in allowed_fields:
            continue

        if field == "notes" and isinstance(
            value,
            str,
        ):
            value = value.strip()

        setattr(
            association,
            field,
            value,
        )

    db.session.commit()

    return association


# =============================================================================
# Ordering
# =============================================================================

def reorder_photography_spot(
    association_id,
    stop_order,
):
    """
    Change the order of a photography stop.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    association.stop_order = stop_order

    db.session.commit()

    return association


def reorder_experience_photography(
    experience_id,
    association_ids,
):
    """
    Reorder photography spots belonging to an experiences.

    Example:

        [7, 3, 9, 2]

    produces:

        association 7 -> 0
        association 3 -> 1
        association 9 -> 2
        association 2 -> 3
    """

    if not association_ids:
        return []

    associations = ExperiencePhotography.query.filter(
        ExperiencePhotography.experience_id == experience_id,
        ExperiencePhotography.id.in_(association_ids),
    ).all()

    associations_by_id = {
        association.id: association
        for association in associations
    }

    for position, association_id in enumerate(
        association_ids
    ):

        association = associations_by_id.get(
            association_id
        )

        if association is None:
            continue

        association.stop_order = position

    db.session.commit()

    return get_experience_photography(
        experience_id,
        active_only=False,
    )


# =============================================================================
# Featured Management
# =============================================================================

def set_photography_spot_featured(
    association_id,
    featured=True,
):
    """
    Mark or unmark a photography spot as featured
    within an experiences.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    association.featured = featured

    db.session.commit()

    return association


def feature_photography_spot(
    association_id,
):
    """
    Mark a photography stop as featured.
    """

    return set_photography_spot_featured(
        association_id,
        True,
    )


def unfeature_photography_spot(
    association_id,
):
    """
    Remove a photography stop from featured status.
    """

    return set_photography_spot_featured(
        association_id,
        False,
    )


def get_featured_photography_spots(
    experience_id,
):
    """
    Retrieve featured photography spots for an experiences.
    """

    return ExperiencePhotography.query.filter_by(
        experience_id=experience_id,
        featured=True,
        active=True,
    ).order_by(
        ExperiencePhotography.stop_order.asc(),
        ExperiencePhotography.id.asc(),
    ).all()


# =============================================================================
# Status Management
# =============================================================================

def activate_photography_spot(
    association_id,
):
    """
    Activate a photography spot association.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    association.active = True

    db.session.commit()

    return association


def deactivate_photography_spot(
    association_id,
):
    """
    Deactivate a photography spot association.

    The relationship is preserved in the database.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    association.active = False

    db.session.commit()

    return association


# =============================================================================
# Notes
# =============================================================================

def update_photography_notes(
    association_id,
    notes,
):
    """
    Update experiences-specific notes for a photography stop.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return None

    association.notes = (
        notes.strip()
        if notes
        else None
    )

    db.session.commit()

    return association


# =============================================================================
# Deletion
# =============================================================================

def remove_photography_spot(
    association_id,
):
    """
    Remove a photography spot from an experiences.
    """

    association = get_photography_association(
        association_id
    )

    if association is None:
        return False

    db.session.delete(
        association
    )

    db.session.commit()

    return True


def remove_photography_spot_from_experience(
    experience_id,
    photography_spot_id,
):
    """
    Remove a specific photography spot from an experiences.
    """

    association = get_experience_photography_association(
        experience_id,
        photography_spot_id,
    )

    if association is None:
        return False

    db.session.delete(
        association
    )

    db.session.commit()

    return True


def remove_all_experience_photography(
    experience_id,
):
    """
    Remove all photography spot associations from an experiences.
    """

    associations = ExperiencePhotography.query.filter_by(
        experience_id=experience_id
    ).all()

    if not associations:
        return 0

    count = len(
        associations
    )

    for association in associations:
        db.session.delete(
            association
        )

    db.session.commit()

    return count


# =============================================================================
# Statistics
# =============================================================================

def get_experience_photography_count(
    experience_id,
    active_only=True,
):
    """
    Return the number of photography spots associated
    with an experiences.
    """

    query = ExperiencePhotography.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.count()


# =============================================================================
# Utility
# =============================================================================

def photography_spot_is_associated(
    experience_id,
    photography_spot_id,
):
    """
    Determine whether a photography spot is already associated
    with an experiences.
    """

    return (
        get_experience_photography_association(
            experience_id,
            photography_spot_id,
        )
        is not None
    )