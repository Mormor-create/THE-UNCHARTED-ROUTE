"""
===============================================================================
The Uncharted Route
Experience Highlight Service
===============================================================================

Business logic for managing highlights belonging to experiences.

Examples:

- Sunrise Game Drive
- Luxury Land Cruiser
- Private Guide
- Bush Breakfast
- Big Five Wildlife
- Hotel Pickup

This service handles:

- Creating highlights
- Retrieving highlights
- Searching highlights
- Updating highlights
- Reordering highlights
- Activating/deactivating highlights
- Featuring/unfeaturing highlights
- Bulk creation
- Bulk reordering
- Deleting highlights
- Counting highlights
"""

from app.models import ExperienceHighlight
from extensions import db


# =============================================================================
# Retrieval
# =============================================================================

def get_highlight(highlight_id):
    """
    Retrieve a single highlight by ID.
    """

    return db.session.get(
        ExperienceHighlight,
        highlight_id,
    )


def get_experience_highlights(
    experience_id,
    active_only=True,
):
    """
    Retrieve highlights belonging to an experiences.

    Results are ordered by display_order and then ID.
    """

    query = ExperienceHighlight.query.filter_by(
        experience_id=experience_id
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceHighlight.display_order.asc(),
        ExperienceHighlight.id.asc(),
    ).all()


def get_active_experience_highlights(
    experience_id,
):
    """
    Retrieve only active highlights for an experiences.
    """

    return get_experience_highlights(
        experience_id,
        active_only=True,
    )


def get_inactive_experience_highlights(
    experience_id,
):
    """
    Retrieve inactive highlights for an experiences.
    """

    return ExperienceHighlight.query.filter_by(
        experience_id=experience_id,
        active=False,
    ).order_by(
        ExperienceHighlight.display_order.asc(),
        ExperienceHighlight.id.asc(),
    ).all()


def get_featured_experience_highlights(
    experience_id,
):
    """
    Retrieve featured and active highlights for an experiences.
    """

    return ExperienceHighlight.query.filter_by(
        experience_id=experience_id,
        featured=True,
        active=True,
    ).order_by(
        ExperienceHighlight.display_order.asc(),
        ExperienceHighlight.id.asc(),
    ).all()


def get_highlight_count(
    experience_id,
    active_only=True,
):
    """
    Return the number of highlights belonging to an experiences.
    """

    query = ExperienceHighlight.query.filter_by(
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

def search_highlights(
    experience_id,
    search_term,
    active_only=True,
):
    """
    Search highlights belonging to an experiences.

    Searches:

    - title
    - description
    - highlight_type
    """

    if not search_term:
        return get_experience_highlights(
            experience_id,
            active_only=active_only,
        )

    term = f"%{search_term.strip()}%"

    query = ExperienceHighlight.query.filter(
        ExperienceHighlight.experience_id == experience_id,
        db.or_(
            ExperienceHighlight.title.ilike(term),
            ExperienceHighlight.description.ilike(term),
            ExperienceHighlight.highlight_type.ilike(term),
        ),
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceHighlight.display_order.asc(),
        ExperienceHighlight.id.asc(),
    ).all()


# =============================================================================
# Filtering
# =============================================================================

def get_highlights_by_type(
    experience_id,
    highlight_type,
    active_only=True,
):
    """
    Retrieve highlights by highlight type.

    Examples:

    Wildlife
    Scenic
    Luxury
    Food
    Adventure
    Photography
    Family
    Cultural
    """

    query = ExperienceHighlight.query.filter_by(
        experience_id=experience_id,
        highlight_type=highlight_type,
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceHighlight.display_order.asc(),
        ExperienceHighlight.id.asc(),
    ).all()


# =============================================================================
# Creation
# =============================================================================

def create_highlight(
    experience_id,
    title,
    description=None,
    icon="sparkles",
    highlight_type="General",
    display_order=0,
    featured=False,
    active=True,
):
    """
    Create a highlight for an experiences.
    """

    if not title or not title.strip():
        raise ValueError(
            "Highlight title is required."
        )

    highlight = ExperienceHighlight(
        experience_id=experience_id,
        title=title.strip(),
        description=description.strip()
        if description
        else None,
        icon=icon.strip()
        if icon
        else "sparkles",
        highlight_type=highlight_type.strip()
        if highlight_type
        else "General",
        display_order=display_order,
        featured=featured,
        active=active,
    )

    db.session.add(
        highlight
    )

    db.session.commit()

    return highlight


# =============================================================================
# Bulk Creation
# =============================================================================

def create_highlights(
    experience_id,
    highlights,
):
    """
    Create multiple highlights for an experiences.

    Example:

        [
            {
                "title": "Sunrise Game Drive",
                "description": "Experience Nairobi at sunrise.",
                "icon": "sunrise",
                "highlight_type": "Wildlife",
            },
            {
                "title": "Luxury Land Cruiser",
                "icon": "car",
                "highlight_type": "Luxury",
            },
        ]

    The supplied list order becomes the display order.
    """

    if not highlights:
        return []

    created = []

    next_order = (
        ExperienceHighlight.query.filter_by(
            experience_id=experience_id
        ).count()
    )

    for highlight_data in highlights:

        if not highlight_data:
            continue

        title = highlight_data.get(
            "title"
        )

        if not title or not title.strip():
            continue

        highlight = ExperienceHighlight(
            experience_id=experience_id,
            title=title.strip(),
            description=(
                highlight_data.get("description").strip()
                if highlight_data.get("description")
                else None
            ),
            icon=(
                highlight_data.get("icon").strip()
                if highlight_data.get("icon")
                else "sparkles"
            ),
            highlight_type=(
                highlight_data.get("highlight_type").strip()
                if highlight_data.get("highlight_type")
                else "General"
            ),
            display_order=next_order,
            featured=highlight_data.get(
                "featured",
                False,
            ),
            active=highlight_data.get(
                "active",
                True,
            ),
        )

        db.session.add(
            highlight
        )

        created.append(
            highlight
        )

        next_order += 1

    db.session.commit()

    return created


# =============================================================================
# Update
# =============================================================================

def update_highlight(
    highlight_id,
    **updates,
):
    """
    Update an existing highlight.

    Supported fields:

    - title
    - description
    - icon
    - highlight_type
    - display_order
    - featured
    - active
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    allowed_fields = {
        "title",
        "description",
        "icon",
        "highlight_type",
        "display_order",
        "featured",
        "active",
    }

    text_fields = {
        "title",
        "description",
        "icon",
        "highlight_type",
    }

    for field, value in updates.items():

        if field not in allowed_fields:
            continue

        if field == "title":

            if not value or not value.strip():
                raise ValueError(
                    "Highlight title is required."
                )

        if field in text_fields and isinstance(
            value,
            str,
        ):
            value = value.strip()

        setattr(
            highlight,
            field,
            value,
        )

    db.session.commit()

    return highlight


# =============================================================================
# Ordering
# =============================================================================

def reorder_highlight(
    highlight_id,
    display_order,
):
    """
    Change the display order of a single highlight.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    highlight.display_order = display_order

    db.session.commit()

    return highlight


def reorder_experience_highlights(
    experience_id,
    highlight_ids,
):
    """
    Reorder all highlights belonging to an experiences.

    Example:

        [7, 3, 9, 2]

    becomes:

        7 -> 0
        3 -> 1
        9 -> 2
        2 -> 3
    """

    if not highlight_ids:
        return []

    highlights = ExperienceHighlight.query.filter(
        ExperienceHighlight.experience_id == experience_id,
        ExperienceHighlight.id.in_(highlight_ids),
    ).all()

    highlights_by_id = {
        highlight.id: highlight
        for highlight in highlights
    }

    for position, highlight_id in enumerate(
        highlight_ids
    ):

        highlight = highlights_by_id.get(
            highlight_id
        )

        if highlight is None:
            continue

        highlight.display_order = position

    db.session.commit()

    return get_experience_highlights(
        experience_id,
        active_only=False,
    )


# =============================================================================
# Status Management
# =============================================================================

def activate_highlight(
    highlight_id,
):
    """
    Activate a highlight.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    highlight.active = True

    db.session.commit()

    return highlight


def deactivate_highlight(
    highlight_id,
):
    """
    Deactivate a highlight without deleting it.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    highlight.active = False

    db.session.commit()

    return highlight


# =============================================================================
# Featured Management
# =============================================================================

def feature_highlight(
    highlight_id,
):
    """
    Mark a highlight as featured.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    highlight.featured = True

    db.session.commit()

    return highlight


def unfeature_highlight(
    highlight_id,
):
    """
    Remove the featured status from a highlight.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return None

    highlight.featured = False

    db.session.commit()

    return highlight


# =============================================================================
# Utility
# =============================================================================

def highlight_belongs_to_experience(
    highlight_id,
    experience_id,
):
    """
    Determine whether a highlight belongs to a
    particular experiences.
    """

    return ExperienceHighlight.query.filter_by(
        id=highlight_id,
        experience_id=experience_id,
    ).first() is not None


def highlight_exists(
    experience_id,
    title,
):
    """
    Determine whether a highlight with the given
    title already exists for an experiences.
    """

    if not title:
        return False

    return ExperienceHighlight.query.filter(
        ExperienceHighlight.experience_id == experience_id,
        db.func.lower(
            ExperienceHighlight.title
        ) == title.strip().lower(),
    ).first() is not None


# =============================================================================
# Deletion
# =============================================================================

def delete_highlight(
    highlight_id,
):
    """
    Permanently delete a highlight.
    """

    highlight = get_highlight(
        highlight_id
    )

    if highlight is None:
        return False

    db.session.delete(
        highlight
    )

    db.session.commit()

    return True


def delete_experience_highlights(
    experience_id,
):
    """
    Permanently delete all highlights belonging
    to an experiences.

    Returns the number of deleted highlights.
    """

    highlights = ExperienceHighlight.query.filter_by(
        experience_id=experience_id
    ).all()

    if not highlights:
        return 0

    count = len(
        highlights
    )

    for highlight in highlights:
        db.session.delete(
            highlight
        )

    db.session.commit()

    return count