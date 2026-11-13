"""
===============================================================================
The Uncharted Route
Experience Service
===============================================================================
Business logic for managing travel experiences.
The Experience model is the central parent model for the experience system.
It connects to:

- Experience Category
- Destination
- Conservation Story
- Cancellation Policy
- Accessibility Profile
- Experience Media
- Experience Pricing
- Experience Itinerary
- Experience Inclusions
- Experience Exclusions
- Experience Highlights
- Experience Add-ons
- Experience Packing Items
- Experience Safety Rules
- Experience Requirements
- Experience FAQs
- Experience Wildlife
- Experience Photography
- Signature Moments
- Experience Tags
- Experience Schedules
- Experience Reviews
- Testimonials
- Bookings

This service handles operations on the parent Experience record.

Child and related records should be managed through their own services so
that the service layer remains modular, maintainable, and easy to extend.
"""

from datetime import datetime

from sqlalchemy import or_

from app.models import Experience
from app.services.media_service import get_media_folders, get_media_assets
from extensions import db


# =============================================================================
# Internal Helpers
# =============================================================================
def _clean_string(value, *, lowercase=False):
    """
    Safely clean a string value.

    Parameters
    ----------
    value : str | None
        Value to clean.

    lowercase : bool
        Whether the resulting value should be converted to lowercase.

    Returns
    -------
    str | None
        Cleaned value.
    """

    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()

    if lowercase:
        value = value.lower()
    return value

def _validate_required_fields(**fields):
    """
    Validate required Experience fields.

    Raises
    ------
    ValueError
        If one or more required fields are missing.
    """

    missing = [
        field_name
        for field_name, value in fields.items()
        if value is None
        or (
            isinstance(value, str)
            and not value.strip()
        )
    ]

    if missing:
        formatted = ", ".join(missing)

        raise ValueError(
            f"The following required fields are missing: {formatted}."
        )


# =============================================================================
# Retrieval
# =============================================================================
def get_experience_by_id(experience_id):
    """
    Retrieve an Experience by primary key.
    Parameters
    ----------
    experience_id : int

    Returns
    -------
    Experience | None
    """
    if not experience_id:
        return None
    return db.session.get(
        Experience,
        experience_id,)

def get_experience_by_slug(slug):
    """
    Retrieve an Experience by its unique slug.

    Parameters
    ----------
    slug : str
        Experience URL slug.

    Returns
    -------
    Experience | None
    """

    slug = _clean_string(
        slug,
        lowercase=True,
    )

    if not slug:
        return None

    return Experience.query.filter_by(
        slug=slug,
    ).first()


def get_experience_by_code(experience_code):
    """
    Retrieve an Experience by its unique experience code.

    Examples
    --------
    WNA-001
    COE-WEL-001
    ADV-001
    LUX-001

    Parameters
    ----------
    experience_code : str

    Returns
    -------
    Experience | None
    """

    experience_code = _clean_string(
        experience_code,)
    if not experience_code:
        return None

    return Experience.query.filter_by(
        experience_code=experience_code,).first()

def get_active_experience_by_slug(slug):
    """
    Retrieve an active Experience by slug.

    Only Experiences marked as active are returned.

    Returns
    -------
    Experience | None
    """

    experience = get_experience_by_slug(
        slug
    )

    if experience is None:
        return None

    if not experience.active:
        return None

    return experience


def get_active_experience_by_code(experience_code):
    """
    Retrieve an active Experience by experience code.

    Returns
    -------
    Experience | None
    """

    experience = get_experience_by_code(
        experience_code
    )

    if experience is None:
        return None

    if not experience.active:
        return None

    return experience


# =============================================================================
# Experience Collections
# =============================================================================
def get_all_experiences():
    """
    Retrieve all Experiences.
    Experiences are ordered by display order and then title.
    Primarily intended for administrative and CMS interfaces.
    Returns
    -------
    list[Experience]
    """

    return (
        Experience.query
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),).all())

def get_active_experiences():
    """
    Retrieve all active Experiences.
    These Experiences are eligible to appear on the public website.
    Returns
    -------
    list[Experience]
    """
    return (
        Experience.query
        .filter(
            Experience.active.is_(True))
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),)
        .all())

def get_inactive_experiences():
    """
    Retrieve all inactive Experiences.

    These Experiences remain in the database but are not publicly active.

    Returns
    -------
    list[Experience]
    """

    return (
        Experience.query
        .filter(
            Experience.active.is_(False)
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )


def get_featured_experiences():
    """
    Retrieve active Experiences marked as featured.

    These are intended for homepage and promotional sections.

    Returns
    -------
    list[Experience]
    """

    return (
        Experience.query
        .filter(
            Experience.active.is_(True),
            Experience.featured.is_(True),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )


# =============================================================================
# Filtering
# =============================================================================

def get_experiences_by_category(category_id):
    """
    Retrieve active Experiences belonging to a category.

    Parameters
    ----------
    category_id : int

    Returns
    -------
    list[Experience]
    """

    if not category_id:
        return []

    return (
        Experience.query
        .filter(
            Experience.category_id == category_id,
            Experience.active.is_(True),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )


def get_experiences_by_destination(destination_id):
    """
    Retrieve active Experiences belonging to a destination.

    Parameters
    ----------
    destination_id : int

    Returns
    -------
    list[Experience]
    """

    if not destination_id:
        return []

    return (
        Experience.query
        .filter(
            Experience.destination_id == destination_id,
            Experience.active.is_(True),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )

# =============================================================================
# Experience Media Library Retrieval
# =============================================================================

EXPERIENCE_MEDIA_FOLDER_NAME = "Experiences"


def _get_experience_media_assets():
    """
    Retrieve active images assigned to the Experiences folder
    or any of its active descendants.

    Uses the existing Media Library services without requiring
    changes to get_media_assets() or get_media_folders().
    """

    folders = get_media_folders(
        active_only=True,
    )

    # Find the root Experiences folder.
    root_folder = next(
        (
            folder
            for folder in folders
            if (
                folder.name
                and folder.name.strip().casefold()
                == EXPERIENCE_MEDIA_FOLDER_NAME.casefold()
            )
        ),
        None,
    )

    # Fail closed if the folder does not exist or is inactive.
    if root_folder is None:
        return []

    # Build the active folder hierarchy.
    folders_by_parent = {}

    for folder in folders:
        folders_by_parent.setdefault(
            folder.parent_id,
            [],
        ).append(folder)

    # Collect the root folder and all active descendants.
    folder_ids = set()

    def collect_descendants(folder):
        if folder.id in folder_ids:
            return

        folder_ids.add(folder.id)

        for child in folders_by_parent.get(
            folder.id,
            [],
        ):
            collect_descendants(child)

    collect_descendants(root_folder)

    # Retrieve images from each eligible folder.
    assets_by_id = {}

    for folder_id in folder_ids:
        assets = get_media_assets(
            folder_id=folder_id,
            media_type="image",
            active_only=True,
        )

        for asset in assets:
            assets_by_id[asset.id] = asset

    # Return a predictable order for the dropdown.
    return sorted(
        assets_by_id.values(),
        key=lambda asset: (
            (
                getattr(asset, "title", None)
                or getattr(asset, "original_filename", None)
                or getattr(asset, "filename", None)
                or ""
            ).casefold(),
            asset.id,
        ),
    )

def get_experiences_by_difficulty(difficulty):
    """
    Retrieve active Experiences by difficulty level.

    Parameters
    ----------
    difficulty : str

    Returns
    -------
    list[Experience]
    """

    difficulty = _clean_string(
        difficulty,
    )

    if not difficulty:
        return []

    return (
        Experience.query
        .filter(
            Experience.difficulty.ilike(
                difficulty
            ),
            Experience.active.is_(True),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )


# =============================================================================
# Search
# =============================================================================

def search_experiences(
    query,
    active_only=True,
):
    """
    Search Experiences.

    Searches across:

    - Experience code
    - Title
    - Short description
    - Full description
    - Location
    - Meeting point

    Parameters
    ----------
    query : str
        Search term.

    active_only : bool
        When True, only active Experiences are searched.

    Returns
    -------
    list[Experience]
    """

    query = _clean_string(
        query,
    )

    if not query:
        return []

    search_term = f"%{query}%"

    search_filters = [
        Experience.experience_code.ilike(
            search_term
        ),
        Experience.title.ilike(
            search_term
        ),
        Experience.short_description.ilike(
            search_term
        ),
        Experience.description.ilike(
            search_term
        ),
        Experience.location.ilike(
            search_term
        ),
        Experience.meeting_point.ilike(
            search_term
        ),
    ]

    query_builder = Experience.query.filter(
        or_(*search_filters)
    )

    if active_only:
        query_builder = query_builder.filter(
            Experience.active.is_(True)
        )

    return (
        query_builder
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )

# =============================================================================
# Creation
# =============================================================================
def create_experience(
    experience_code,
    title,
    slug,
    short_description,
    description,
    price_from,
    featured_image,
    category_id,
    destination_id,
    **kwargs,):
    """
    Create a new Experience.
    Homepage visibility requires featured=True. If an experience is not
    featured, it cannot be shown on the homepage.
    Raises:
        ValueError: If required fields are missing or the experience code
                    or slug already exists.
    """
    _validate_required_fields(
        experience_code=experience_code,
        title=title,
        slug=slug,
        short_description=short_description,
        description=description,
        price_from=price_from,
        featured_image=featured_image,
        category_id=category_id,
        destination_id=destination_id,
    )

    experience_code = _clean_string(experience_code)
    title = _clean_string(title)
    slug = _clean_string(slug, lowercase=True)
    short_description = _clean_string(short_description)
    description = _clean_string(description)
    featured_image = _clean_string(featured_image)

    # ------------------------------------------------------------------
    # Duplicate checks
    # ------------------------------------------------------------------
    existing_code = get_experience_by_code(experience_code)

    if existing_code is not None:
        raise ValueError(
            f"An experience with code '{experience_code}' already exists."
        )

    existing_slug = get_experience_by_slug(slug)

    if existing_slug is not None:
        raise ValueError(
            f"An experience with slug '{slug}' already exists."
        )

    # ------------------------------------------------------------------
    # Supported optional fields
    # ------------------------------------------------------------------
    allowed_fields = {
        "duration",
        "meeting_point",
        "location",
        "currency",
        "minimum_people",
        "maximum_people",
        "minimum_age",
        "difficulty",
        "banner_image",
        "meta_title",
        "meta_description",
        "conservation_story_id",
        "cancellation_policy_id",
        "accessibility_profile_id",
        "featured",
        "show_on_homepage",
        "active",
        "display_order",
    }

    experience_data = {
        field: value
        for field, value in kwargs.items()
        if field in allowed_fields
    }

    # ------------------------------------------------------------------
    # Normalize publication flags
    # ------------------------------------------------------------------
    featured = bool(experience_data.get("featured", False))
    show_on_homepage = bool(
        experience_data.get("show_on_homepage", False)
    )

    if show_on_homepage and not featured:
        raise ValueError(
            "An experience must be marked as featured before it can "
            "be shown on the homepage."
        )

    experience_data["featured"] = featured
    experience_data["show_on_homepage"] = show_on_homepage

    # ------------------------------------------------------------------
    # Clean optional string fields
    # ------------------------------------------------------------------
    string_fields = {
        "duration",
        "meeting_point",
        "location",
        "currency",
        "difficulty",
        "banner_image",
        "meta_title",
        "meta_description",
    }

    for field in string_fields:
        if field in experience_data:
            experience_data[field] = _clean_string(
                experience_data[field]
            )

    # ------------------------------------------------------------------
    # Create experience
    # ------------------------------------------------------------------
    experience = Experience(
        experience_code=experience_code,
        title=title,
        slug=slug,
        short_description=short_description,
        description=description,
        price_from=price_from,
        featured_image=featured_image,
        category_id=category_id,
        destination_id=destination_id,
        **experience_data,
    )

    try:
        db.session.add(experience)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return experience

# =============================================================================
# Updates
# =============================================================================

def update_experience(
    experience,
    **data,
):
    """
    Update an existing Experience.

    Homepage visibility requires featured=True. Turning featured off
    automatically turns show_on_homepage off as well.

    Raises:
        ValueError: If the experience is missing, required values are
                    invalid, or the experience code or slug conflicts
                    with another record.
    """
    if experience is None:
        raise ValueError("An Experience record is required.")

    # ------------------------------------------------------------------
    # Supported fields
    # ------------------------------------------------------------------
    allowed_fields = {
        "experience_code",
        "title",
        "slug",
        "short_description",
        "description",
        "duration",
        "meeting_point",
        "location",
        "price_from",
        "currency",
        "minimum_people",
        "maximum_people",
        "minimum_age",
        "difficulty",
        "featured_image",
        "banner_image",
        "meta_title",
        "meta_description",
        "featured",
        "show_on_homepage",
        "active",
        "display_order",
        "category_id",
        "destination_id",
        "conservation_story_id",
        "cancellation_policy_id",
        "accessibility_profile_id",
    }

    string_fields = {
        "experience_code",
        "title",
        "slug",
        "short_description",
        "description",
        "duration",
        "meeting_point",
        "location",
        "currency",
        "difficulty",
        "featured_image",
        "banner_image",
        "meta_title",
        "meta_description",
    }

    # ------------------------------------------------------------------
    # Filter supported fields
    # ------------------------------------------------------------------
    update_data = {
        field: value
        for field, value in data.items()
        if field in allowed_fields
    }

    # ------------------------------------------------------------------
    # Clean strings
    # ------------------------------------------------------------------
    for field in string_fields:
        if field not in update_data:
            continue

        value = update_data[field]

        if not isinstance(value, str):
            continue

        value = value.strip()

        if field == "slug":
            value = value.lower()

        update_data[field] = value

    # ------------------------------------------------------------------
    # Validate required values when supplied
    # ------------------------------------------------------------------
    required_fields = {
        "experience_code",
        "title",
        "slug",
        "short_description",
        "description",
    }

    for field in required_fields:
        if field not in update_data:
            continue

        value = update_data[field]

        if value is None or (
            isinstance(value, str) and not value
        ):
            raise ValueError(
                f"{field.replace('_', ' ').title()} cannot be empty."
            )

    # ------------------------------------------------------------------
    # Check duplicate experience code
    # ------------------------------------------------------------------
    if "experience_code" in update_data:
        existing = (
            Experience.query
            .filter(
                Experience.experience_code
                == update_data["experience_code"],
                Experience.id != experience.id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "Another experience already uses the code "
                f"'{update_data['experience_code']}'."
            )

    # ------------------------------------------------------------------
    # Check duplicate slug
    # ------------------------------------------------------------------
    if "slug" in update_data:
        existing = (
            Experience.query
            .filter(
                Experience.slug == update_data["slug"],
                Experience.id != experience.id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "Another experience already uses the slug "
                f"'{update_data['slug']}'."
            )

    # ------------------------------------------------------------------
    # Enforce homepage visibility rules
    # ------------------------------------------------------------------
    # Use the incoming featured value when supplied; otherwise preserve
    # the record's existing value.
    effective_featured = bool(
        update_data.get("featured", experience.featured)
    )

    # If featured is explicitly turned off, homepage visibility must
    # also be turned off, even if the incoming data requests otherwise.
    if not effective_featured:
        update_data["show_on_homepage"] = False

    elif "show_on_homepage" in update_data:
        update_data["show_on_homepage"] = bool(
            update_data["show_on_homepage"]
        )

    # ------------------------------------------------------------------
    # Apply updates
    # ------------------------------------------------------------------
    for field, value in update_data.items():
        setattr(experience, field, value)

    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return experience

# =============================================================================
# Activation
# =============================================================================
def activate_experience(experience):
    """
    Activate an Experience on the platform.

    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.active = True
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return experience


def deactivate_experience(experience):
    """
    Deactivate an Experience.

    The record remains in the database but is removed from active public
    Experience listings.

    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.active = False
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return experience


def toggle_experience_status(experience):
    """
    Toggle an Experience between active and inactive.

    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.active = not experience.active
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return experience


# =============================================================================
# Featured Experiences
# =============================================================================
def feature_experience(experience):
    """
    Mark an Experience as featured.
    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.featured = True
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    return experience

def unfeature_experience(experience):
    """
    Remove an Experience from featured sections.
    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.featured = False
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    return experience

def toggle_featured_status(experience):
    """
    Toggle the featured status of an Experience.
    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    experience.featured = not experience.featured
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    return experience

# =============================================================================
# Display Ordering
# =============================================================================
def update_display_order(
    experience,
    display_order,):
    """
    Update the catalogue display order of an Experience.
    Parameters
    ----------
    experience : Experience to update.
    display_order : int
        New display order.

    Returns
    -------
    Experience
        Updated Experience.
    """

    if experience is None:
        raise ValueError(
            "An Experience record is required."
        )

    if display_order is None:
        raise ValueError(
            "Display order is required."
        )

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    experience.display_order = display_order
    experience.updated_at = datetime.utcnow()

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    return experience

# =============================================================================
# Experience Statistics
# =============================================================================
def get_experience_statistics(experience):
    """Return counts for the content and records associated with an experience.

    Counts are calculated from the experience's existing SQLAlchemy
    relationships. Missing optional relationships safely return zero.
    """

    def count_related(relationship_name):
        records = getattr(experience, relationship_name, None)

        if records is None:
            return 0

        # Normal SQLAlchemy relationship collections.
        try:
            return len(records)
        except TypeError:
            pass

        # Supports query-like relationships if any are configured that way.
        count_method = getattr(records, "count", None)

        if callable(count_method):
            try:
                return count_method()
            except TypeError:
                pass

        return 0

    return {
        # Guest activity
        "booking": count_related("bookings"),
        "reviews": count_related("reviews"),
        "testimonials": count_related("testimonials"),

        # Content and pricing
        "media": count_related("media"),
        "pricing": count_related("pricing"),
        "itinerary": count_related("itinerary"),
        "inclusions": count_related("inclusions"),
        "exclusions": count_related("exclusions"),
        "highlights": count_related("highlights"),
        "addons": count_related("addons"),

        # Guest preparation and safety
        "packing_items": count_related("packing_items"),
        "safety_rules": count_related("safety_rules"),
        "requirements": count_related("requirements"),
        "faqs": count_related("faqs"),

        # Nature and experience details
        "wildlife": count_related("wildlife"),
        "photography": count_related("photography_spots"),
        "signature_moments": count_related("signature_moments"),

        # Operations and discovery
        "tags": count_related("tags"),}

# =============================================================================
# Deletion
# =============================================================================
def delete_experience(experience):
    """
    Delete an Experience.

    The Experience model is responsible for defining cascade behavior for
    related records. SQLAlchemy therefore handles child deletion according
    to the relationship configuration.

    Parameters
    ----------
    experience : Experience

    Returns
    -------
    bool
        True when deletion succeeds.
    """
    if experience is None:
        raise ValueError(
            "An Experience record is required.")

    try:
        db.session.delete(
            experience)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    return True

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Retrieval
    "get_experience_by_id",
    "get_experience_by_slug",
    "get_experience_by_code",
    "get_active_experience_by_slug",
    "get_active_experience_by_code",

    # Collections
    "get_all_experiences",
    "get_active_experiences",
    "get_inactive_experiences",
    "get_featured_experiences",

    # Filtering
    "get_experiences_by_category",
    "get_experiences_by_destination",
    "get_experiences_by_difficulty",

    # Search
    "search_experiences",

    # Creation
    "create_experience",

    # Updates
    "update_experience",

    # Activation
    "activate_experience",
    "deactivate_experience",
    "toggle_experience_status",

    # Featured
    "feature_experience",
    "unfeature_experience",
    "toggle_featured_status",

    # Ordering
    "update_display_order",

    # Statistics
    "get_experience_statistics",

    # Deletion
    "delete_experience",
]