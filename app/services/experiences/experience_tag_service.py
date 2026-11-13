"""
===============================================================================
The Uncharted Route
Experience Tag Service
===============================================================================

Business logic for managing searchable experiences tags.

Responsibilities
----------------

• Create tags
• Retrieve tags
• Update tags
• Delete tags
• Activate / deactivate tags
• Search tags
• Retrieve featured tags
• Assign tags to experiences
• Remove tags from experiences
• Replace experiences tags
• Retrieve an experiences's tags
• Find experiences by tag
• Count tag usage
• Reorder tags
"""

from extensions import db
from app.models import ExperienceTag, Experience

# =============================================================================
# Constants
# =============================================================================
DEFAULT_COLOR = "#10B981"

# =============================================================================
# Validation
# =============================================================================

def validate_tag_data(data):
    """
    Validate and normalize tag data.
    """

    if not data:
        raise ValueError(
            "Tag data is required."
        )

    name = data.get("name")

    if not name:
        raise ValueError(
            "Tag name is required."
        )

    name = name.strip()

    if not name:
        raise ValueError(
            "Tag name cannot be empty."
        )

    slug = data.get("slug")

    if not slug:
        raise ValueError(
            "Tag slug is required."
        )

    slug = slug.strip().lower()

    if not slug:
        raise ValueError(
            "Tag slug cannot be empty."
        )

    return {
        "name": name,
        "slug": slug,
        "description": data.get("description"),
        "color": data.get(
            "color",
            DEFAULT_COLOR
        ),
        "icon": data.get("icon"),
        "featured": data.get(
            "featured",
            False
        ),
        "meta_title": data.get("meta_title"),
        "meta_description": data.get(
            "meta_description"
        ),
        "active": data.get(
            "active",
            True
        ),
        "sort_order": data.get(
            "sort_order",
            0
        ),
    }


# =============================================================================
# Create
# =============================================================================

def create_tag(data):
    """
    Create a new experiences tag.
    """

    validated = validate_tag_data(data)

    existing_name = ExperienceTag.query.filter_by(
        name=validated["name"]
    ).first()

    if existing_name:
        raise ValueError(
            "A tag with this name already exists."
        )

    existing_slug = ExperienceTag.query.filter_by(
        slug=validated["slug"]
    ).first()

    if existing_slug:
        raise ValueError(
            "A tag with this slug already exists."
        )

    tag = ExperienceTag(
        **validated
    )

    db.session.add(tag)
    db.session.commit()

    return tag


# =============================================================================
# Retrieve
# =============================================================================

def get_tag(tag_id):
    """
    Retrieve a tag by ID.
    """

    return db.session.get(
        ExperienceTag,
        tag_id
    )


def get_tag_by_name(name):
    """
    Retrieve a tag by name.
    """

    if not name:
        return None

    return ExperienceTag.query.filter_by(
        name=name.strip()
    ).first()


def get_tag_by_slug(slug):
    """
    Retrieve a tag by slug.
    """

    if not slug:
        return None

    return ExperienceTag.query.filter_by(
        slug=slug.strip().lower()
    ).first()


# =============================================================================
# List Tags
# =============================================================================

def get_all_tags(
    active_only=False,
):
    """
    Retrieve all tags.
    """

    query = ExperienceTag.query

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceTag.sort_order.asc(),
        ExperienceTag.name.asc()
    ).all()


def get_featured_tags(
    active_only=True,
):
    """
    Retrieve featured tags.
    """

    query = ExperienceTag.query.filter_by(
        featured=True
    )

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.order_by(
        ExperienceTag.sort_order.asc(),
        ExperienceTag.name.asc()
    ).all()


# =============================================================================
# Search
# =============================================================================

def search_tags(
    search_term,
    active_only=True,
):
    """
    Search tags by name, slug, or description.
    """

    if not search_term:
        return get_all_tags(
            active_only=active_only
        )

    search_term = search_term.strip()

    query = ExperienceTag.query.filter(
        db.or_(
            ExperienceTag.name.ilike(
                f"%{search_term}%"
            ),
            ExperienceTag.slug.ilike(
                f"%{search_term}%"
            ),
            ExperienceTag.description.ilike(
                f"%{search_term}%"
            )
        )
    )

    if active_only:
        query = query.filter(
            ExperienceTag.active.is_(True)
        )

    return query.order_by(
        ExperienceTag.name.asc()
    ).all()


# =============================================================================
# Update
# =============================================================================

def update_tag(
    tag_id,
    data,
):
    """
    Update an existing tag.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    validated = validate_tag_data(data)

    duplicate_name = ExperienceTag.query.filter(
        ExperienceTag.name == validated["name"],
        ExperienceTag.id != tag.id,
    ).first()

    if duplicate_name:
        raise ValueError(
            "Another tag already uses this name."
        )

    duplicate_slug = ExperienceTag.query.filter(
        ExperienceTag.slug == validated["slug"],
        ExperienceTag.id != tag.id,
    ).first()

    if duplicate_slug:
        raise ValueError(
            "Another tag already uses this slug."
        )

    for field, value in validated.items():
        setattr(
            tag,
            field,
            value
        )

    db.session.commit()

    return tag


# =============================================================================
# Partial Update
# =============================================================================

def update_tag_fields(
    tag_id,
    **fields,
):
    """
    Update selected tag fields.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    allowed_fields = {
        "name",
        "slug",
        "description",
        "color",
        "icon",
        "featured",
        "meta_title",
        "meta_description",
        "active",
        "sort_order",
    }

    invalid_fields = (
        set(fields) - allowed_fields
    )

    if invalid_fields:
        raise ValueError(
            "Invalid fields: "
            + ", ".join(
                sorted(invalid_fields)
            )
        )

    if "name" in fields:

        if not fields["name"]:
            raise ValueError(
                "Tag name cannot be empty."
            )

        fields["name"] = (
            fields["name"].strip()
        )

        duplicate = ExperienceTag.query.filter(
            ExperienceTag.name == fields["name"],
            ExperienceTag.id != tag.id,
        ).first()

        if duplicate:
            raise ValueError(
                "Another tag already uses this name."
            )

    if "slug" in fields:

        if not fields["slug"]:
            raise ValueError(
                "Tag slug cannot be empty."
            )

        fields["slug"] = (
            fields["slug"].strip().lower()
        )

        duplicate = ExperienceTag.query.filter(
            ExperienceTag.slug == fields["slug"],
            ExperienceTag.id != tag.id,
        ).first()

        if duplicate:
            raise ValueError(
                "Another tag already uses this slug."
            )

    for field, value in fields.items():
        setattr(
            tag,
            field,
            value
        )

    db.session.commit()

    return tag


# =============================================================================
# Activation
# =============================================================================

def activate_tag(tag_id):
    """
    Activate a tag.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    tag.active = True

    db.session.commit()

    return tag


def deactivate_tag(tag_id):
    """
    Deactivate a tag without deleting it.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    tag.active = False

    db.session.commit()

    return tag


def toggle_tag(tag_id):
    """
    Toggle a tag's active state.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    tag.active = not tag.active

    db.session.commit()

    return tag


# =============================================================================
# Featured Status
# =============================================================================

def feature_tag(tag_id):
    """
    Mark a tag as featured.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    tag.featured = True

    db.session.commit()

    return tag


def unfeature_tag(tag_id):
    """
    Remove a tag from featured status.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    tag.featured = False

    db.session.commit()

    return tag


# =============================================================================
# Experience Helpers
# =============================================================================

def get_experience(experience_id):
    """
    Retrieve an experiences by ID.
    """

    return db.session.get(
        Experience,
        experience_id
    )


# =============================================================================
# Assign Tag
# =============================================================================

def add_tag_to_experience(
    experience_id,
    tag_id,
):
    """
    Assign a tag to an experiences.
    """

    experience = get_experience(
        experience_id
    )

    if not experience:
        raise ValueError(
            "Experience not found."
        )

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    if not tag.active:
        raise ValueError(
            "Cannot assign an inactive tag."
        )

    if tag in experience.tags:
        return tag

    experience.tags.append(tag)

    db.session.commit()

    return tag


# =============================================================================
# Remove Tag
# =============================================================================

def remove_tag_from_experience(
    experience_id,
    tag_id,
):
    """
    Remove a tag from an experiences.
    """

    experience = get_experience(
        experience_id
    )

    if not experience:
        raise ValueError(
            "Experience not found."
        )

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    if tag in experience.tags:
        experience.tags.remove(tag)

        db.session.commit()

    return tag


# =============================================================================
# Replace Experience Tags
# =============================================================================

def replace_experience_tags(
    experience_id,
    tag_ids,
):
    """
    Replace all tags assigned to an experiences.

    Example:

        replace_experience_tags(
            experience_id=10,
            tag_ids=[1, 4, 7, 9]
        )
    """

    experience = get_experience(
        experience_id
    )

    if not experience:
        raise ValueError(
            "Experience not found."
        )

    tag_ids = list(
        dict.fromkeys(tag_ids or [])
    )

    if not tag_ids:
        experience.tags = []

        db.session.commit()

        return []


    tags = ExperienceTag.query.filter(
        ExperienceTag.id.in_(tag_ids),
        ExperienceTag.active.is_(True),
    ).all()

    found_ids = {
        tag.id
        for tag in tags
    }

    missing_ids = (
        set(tag_ids) - found_ids
    )

    if missing_ids:
        raise ValueError(
            "Invalid or inactive tag IDs: "
            + ", ".join(
                str(tag_id)
                for tag_id in sorted(missing_ids)
            )
        )

    experience.tags = tags

    db.session.commit()

    return tags


# =============================================================================
# Experience Tags
# =============================================================================

def get_experience_tags(
    experience_id,
    active_only=True,
):
    """
    Retrieve tags assigned to an experiences.
    """

    experience = get_experience(
        experience_id
    )

    if not experience:
        raise ValueError(
            "Experience not found."
        )

    query = ExperienceTag.query.join(
        ExperienceTag,
        ExperienceTag.id == ExperienceTag.c.tag_id
    ).filter(
        ExperienceTag.c.experience_id == experience_id
    )

    if active_only:
        query = query.filter(
            ExperienceTag.active.is_(True)
        )

    return query.order_by(
        ExperienceTag.sort_order.asc(),
        ExperienceTag.name.asc()
    ).all()


# =============================================================================
# Experiences By Tag
# =============================================================================

def get_experiences_by_tag(
    tag_id,
    active_only=True,
):
    """
    Retrieve experiences associated with a tag.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    query = tag.experiences

    if active_only:
        query = query.filter(
            Experience.active.is_(True)
        )

    return query.all()


def get_experiences_by_tag_slug(
    slug,
    active_only=True,
):
    """
    Retrieve experiences using a tag slug.
    """

    tag = get_tag_by_slug(slug)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    return get_experiences_by_tag(
        tag.id,
        active_only=active_only
    )


# =============================================================================
# Tag Usage
# =============================================================================

def get_tag_usage_count(tag_id):
    """
    Return the number of experiences using a tag.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    return tag.experience_count


def get_unused_tags():
    """
    Retrieve tags that are not currently assigned
    to any experiences.
    """

    return [
        tag
        for tag in get_all_tags()
        if tag.experience_count == 0
    ]


# =============================================================================
# Popular / Used Tags
# =============================================================================

def get_most_used_tags(
    limit=10,
    active_only=True,
):
    """
    Retrieve the most frequently used tags.
    """

    tags = get_all_tags(
        active_only=active_only
    )

    return sorted(
        tags,
        key=lambda tag: tag.experience_count,
        reverse=True
    )[:limit]


# =============================================================================
# Reordering
# =============================================================================

def reorder_tag(
    tag_id,
    sort_order,
):
    """
    Change the display order of a tag.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    if sort_order < 0:
        raise ValueError(
            "Sort order cannot be negative."
        )

    tag.sort_order = sort_order

    db.session.commit()

    return tag


def reorder_tags(
    ordered_tag_ids,
):
    """
    Reorder multiple tags.

    Example:

        [5, 2, 8, 1]
    """

    tags = ExperienceTag.query.filter(
        ExperienceTag.id.in_(
            ordered_tag_ids
        )
    ).all()

    tags_by_id = {
        tag.id: tag
        for tag in tags
    }

    for position, tag_id in enumerate(
        ordered_tag_ids
    ):

        tag = tags_by_id.get(
            tag_id
        )

        if tag:
            tag.sort_order = position

    db.session.commit()

    return get_all_tags()


# =============================================================================
# Counts
# =============================================================================

def count_tags(
    active_only=False,
):
    """
    Count available tags.
    """

    query = ExperienceTag.query

    if active_only:
        query = query.filter_by(
            active=True
        )

    return query.count()


# =============================================================================
# Delete
# =============================================================================

def delete_tag(tag_id):
    """
    Permanently delete a tag.

    SQLAlchemy will remove the many-to-many association
    rows when the tag is removed from the relationship.
    """

    tag = get_tag(tag_id)

    if not tag:
        raise ValueError(
            "Tag not found."
        )

    db.session.delete(tag)
    db.session.commit()

    return True