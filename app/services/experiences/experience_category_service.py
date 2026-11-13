"""
===============================================================================
The Uncharted Route
Experience Category Service
===============================================================================

Business logic for managing experiences categories.

This service handles:

- Creating categories
- Retrieving categories
- Finding categories by slug
- Updating categories
- Activating/deactivating categories
- Featuring/unfeaturing categories
- Reordering categories
- Retrieving experiences within a category
- Deleting categories

Routes should call this service instead of manipulating
ExperienceCategory records directly.
"""

import re
from datetime import datetime
from app.models import ExperienceCategory
from extensions import db


# =============================================================================
# Slug Helpers
# =============================================================================

def generate_category_slug(name):
    """
    Generate a URL-friendly slug from a category name.

    Example:

        "Wildlife & Conservation"

    becomes:

        "wildlife-conservation"
    """

    slug = name.strip().lower()

    slug = re.sub(
        r"[^a-z0-9\s-]",
        "",
        slug,
    )

    slug = re.sub(
        r"[\s_-]+",
        "-",
        slug,
    )

    return slug.strip("-")


def generate_unique_category_slug(
    name,
    category_id=None,
):
    """
    Generate a unique category slug.

    If the generated slug already exists, a numeric suffix is added.

    Example:

        wildlife-conservation
        wildlife-conservation-2
        wildlife-conservation-3
    """

    base_slug = generate_category_slug(
        name
    )

    slug = base_slug
    counter = 2

    query = ExperienceCategory.query.filter(
        ExperienceCategory.slug == slug
    )

    if category_id is not None:
        query = query.filter(
            ExperienceCategory.id != category_id
        )

    while query.first() is not None:

        slug = f"{base_slug}-{counter}"

        query = ExperienceCategory.query.filter(
            ExperienceCategory.slug == slug
        )

        if category_id is not None:
            query = query.filter(
                ExperienceCategory.id != category_id
            )

        counter += 1

    return slug


# =============================================================================
# Creation
# =============================================================================

def create_category(
    name,
    short_description=None,
    description=None,
    icon=None,
    color="#0F766E",
    featured_image=None,
    banner_image=None,
    display_order=0,
    featured=False,
    active=True,
):
    """
    Create a new experiences category.
    """

    name = name.strip()

    existing = ExperienceCategory.query.filter(
        db.func.lower(
            ExperienceCategory.name
        ) == name.lower()
    ).first()

    if existing:
        raise ValueError(
            "An experiences category with this name already exists."
        )

    slug = generate_unique_category_slug(
        name
    )

    category = ExperienceCategory(
        name=name,
        slug=slug,
        icon=icon.strip() if icon else None,
        color=color,
        short_description=(
            short_description.strip()
            if short_description
            else None
        ),
        description=(
            description.strip()
            if description
            else None
        ),
        featured_image=featured_image,
        banner_image=banner_image,
        display_order=display_order,
        featured=featured,
        active=active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(category)
    db.session.commit()

    return category


# =============================================================================
# Retrieval
# =============================================================================

def get_category(category_id):
    """
    Retrieve a category by ID.
    """

    return db.session.get(
        ExperienceCategory,
        category_id,
    )


def get_category_by_slug(slug):
    """
    Retrieve a category by its URL slug.
    """

    if not slug:
        return None

    return ExperienceCategory.query.filter(
        db.func.lower(
            ExperienceCategory.slug
        ) == slug.strip().lower()
    ).first()


def get_category_by_name(name):
    """
    Retrieve a category by name.
    """

    if not name:
        return None

    return ExperienceCategory.query.filter(
        db.func.lower(
            ExperienceCategory.name
        ) == name.strip().lower()
    ).first()


def get_all_categories(
    active_only=False,
):
    """
    Retrieve all experiences categories.

    Categories are ordered by display order and then name.
    """

    query = ExperienceCategory.query

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceCategory.display_order.asc(),
        ExperienceCategory.name.asc(),
    ).all()


def get_active_categories():
    """
    Retrieve active experiences categories.
    """

    return get_all_categories(
        active_only=True
    )


def get_featured_categories(
    active_only=True,
):
    """
    Retrieve featured categories.
    """

    query = ExperienceCategory.query.filter_by(
        featured=True
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceCategory.display_order.asc(),
        ExperienceCategory.name.asc(),
    ).all()


# =============================================================================
# Category Experiences
# =============================================================================

def get_category_experiences(
    category_id,
    active_only=True,
):
    """
    Retrieve experiences belonging to a category.

    Uses the relationship defined on ExperienceCategory.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return []

    query = category.experiences

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.all()


def get_category_experience_count(
    category_id,
    active_only=True,
):
    """
    Return the number of experiences in a category.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return 0

    query = category.experiences

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.count()


# =============================================================================
# Update
# =============================================================================

def update_category(
    category_id,
    **updates,
):
    """
    Update an experiences category.

    Supported fields:

    - name
    - short_description
    - description
    - icon
    - color
    - featured_image
    - banner_image
    - display_order
    - featured
    - active

    Slug is regenerated automatically if the name changes.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return None

    allowed_fields = {
        "name",
        "short_description",
        "description",
        "icon",
        "color",
        "featured_image",
        "banner_image",
        "display_order",
        "featured",
        "active",
    }

    if "name" in updates:

        new_name = updates["name"]

        if not new_name or not new_name.strip():
            raise ValueError(
                "Category name cannot be empty."
            )

        new_name = new_name.strip()

        existing = ExperienceCategory.query.filter(
            db.func.lower(
                ExperienceCategory.name
            ) == new_name.lower(),
            ExperienceCategory.id != category.id,
        ).first()

        if existing:
            raise ValueError(
                "An experiences category with this name already exists."
            )

        category.name = new_name

        category.slug = generate_unique_category_slug(
            new_name,
            category_id=category.id,
        )

    for field, value in updates.items():

        if field not in allowed_fields:
            continue

        if field == "name":
            continue

        if field in {
            "short_description",
            "description",
            "icon",
            "color",
        }:
            if isinstance(value, str):
                value = value.strip()

        setattr(
            category,
            field,
            value,
        )

    category.updated_at = datetime.utcnow()

    db.session.commit()

    return category


# =============================================================================
# Status Management
# =============================================================================

def activate_category(
    category_id,
):
    """
    Activate a category.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return None

    category.active = True
    category.updated_at = datetime.utcnow()

    db.session.commit()

    return category


def deactivate_category(
    category_id,
):
    """
    Deactivate a category.

    The category remains in the database but will no longer
    appear in active category listings.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return None

    category.active = False
    category.updated_at = datetime.utcnow()

    db.session.commit()

    return category


def set_category_featured(
    category_id,
    featured=True,
):
    """
    Mark or unmark a category as featured.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return None

    category.featured = featured
    category.updated_at = datetime.utcnow()

    db.session.commit()

    return category


def feature_category(
    category_id,
):
    """
    Mark a category as featured.
    """

    return set_category_featured(
        category_id,
        True,
    )


def unfeature_category(
    category_id,
):
    """
    Remove a category from featured categories.
    """

    return set_category_featured(
        category_id,
        False,
    )


# =============================================================================
# Ordering
# =============================================================================

def reorder_category(
    category_id,
    display_order,
):
    """
    Change the display order of a category.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return None

    category.display_order = display_order
    category.updated_at = datetime.utcnow()

    db.session.commit()

    return category


def reorder_categories(
    category_ids,
):
    """
    Reorder multiple categories.

    Example:

        [5, 2, 8, 1]

    produces:

        category 5 -> 0
        category 2 -> 1
        category 8 -> 2
        category 1 -> 3
    """

    if not category_ids:
        return []

    categories = ExperienceCategory.query.filter(
        ExperienceCategory.id.in_(category_ids)
    ).all()

    categories_by_id = {
        category.id: category
        for category in categories
    }

    for position, category_id in enumerate(
        category_ids
    ):

        category = categories_by_id.get(
            category_id
        )

        if category is None:
            continue

        category.display_order = position
        category.updated_at = datetime.utcnow()

    db.session.commit()

    return get_all_categories()


# =============================================================================
# Search
# =============================================================================

def search_categories(
    query,
    active_only=True,
):
    """
    Search categories by name or description.
    """

    if not query:
        return []

    search_term = f"%{query.strip()}%"

    filters = [
        ExperienceCategory.name.ilike(
            search_term
        ),
        ExperienceCategory.short_description.ilike(
            search_term
        ),
        ExperienceCategory.description.ilike(
            search_term
        ),
    ]

    category_query = ExperienceCategory.query.filter(
        db.or_(
            *filters
        )
    )

    if active_only:
        category_query = category_query.filter_by(
            active=True
        )

    return category_query.order_by(
        ExperienceCategory.display_order.asc(),
        ExperienceCategory.name.asc(),
    ).all()


# =============================================================================
# Deletion
# =============================================================================

def delete_category(
    category_id,
):
    """
    Delete an experiences category.

    Because the model relationship uses:

        cascade="all, delete-orphan"

    deleting the category will also delete its
    associated experiences.

    This should therefore normally be used only from
    an administrative workflow.
    """

    category = get_category(
        category_id
    )

    if category is None:
        return False

    db.session.delete(
        category
    )

    db.session.commit()

    return True