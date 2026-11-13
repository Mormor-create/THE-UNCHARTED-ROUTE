"""
===============================================================================
The Uncharted Route
Destination Service
===============================================================================

Business logic for destination management.

Responsibilities
----------------
• Create destinations
• Retrieve destinations
• Search destinations
• Filter destinations
• Update destination information
• Activate/deactivate destinations
• Manage featured destinations
• Retrieve experiences belonging to destinations
• Count destination experiences
• Provide destination statistics
• Provide MediaAsset choices for destination images
"""

from datetime import datetime
from sqlalchemy import and_, or_
from app.models import (
    Destination,
    Experience,
    MediaAsset,
)
from extensions import db

# =============================================================================
# Media Asset Choices
# =============================================================================
def get_destination_image_choices():
    """Return active image assets from the central Media Library's
    Destinations folder, including its child folders.
    """
    from app.models import MediaFolder
    from app.services.media_service import get_cms_media_assets

    destinations_folder = MediaFolder.query.filter_by(
        slug="destinations",
        active=True,
    ).first()

    if destinations_folder is None:
        return []

    assets = get_cms_media_assets(
        folder_id=destinations_folder.id,
        include_descendants=True,
        media_type="image",
        active_only=True,
    )

    return [
        (
            asset.id,
            asset.title or asset.original_filename or f"Image #{asset.id}",
        )
        for asset in assets
    ]

# =============================================================================
# Destination Creation
# =============================================================================

def create_destination(
    name,
    slug,
    featured_image_id,
    country="Kenya",
    county=None,
    region=None,
    short_description=None,
    description=None,
    banner_image_id=None,
    latitude=None,
    longitude=None,
    meta_title=None,
    meta_description=None,
    featured=False,
    show_on_homepage=False,
    active=True,
):
    """Create a destination with validated media and visibility settings."""

    name = name.strip() if isinstance(name, str) else ""
    slug = slug.strip().lower() if isinstance(slug, str) else ""

    if not name:
        raise ValueError("Destination name is required.")

    if not slug:
        raise ValueError("Destination slug is required.")

    if not featured_image_id:
        raise ValueError("Featured image is required.")

    featured = bool(featured)
    active = bool(active)
    show_on_homepage = bool(show_on_homepage)

    if show_on_homepage and not featured:
        raise ValueError(
            "A destination must be featured before it can appear on the homepage."
        )

    if show_on_homepage and not active:
        raise ValueError(
            "An inactive destination cannot appear on the homepage."
        )

    existing_name = Destination.query.filter(
        Destination.name.ilike(name)
    ).first()

    if existing_name:
        raise ValueError("A destination with this name already exists.")

    existing_slug = Destination.query.filter(
        Destination.slug.ilike(slug)
    ).first()

    if existing_slug:
        raise ValueError("A destination with this slug already exists.")

    # Validate featured image.
    featured_asset = db.session.get(MediaAsset, featured_image_id)

    if featured_asset is None:
        raise ValueError("Selected featured image does not exist.")

    if not featured_asset.active:
        raise ValueError("Selected featured image is inactive.")

    if featured_asset.media_type != "image":
        raise ValueError("Selected featured asset must be an image.")

    # Validate optional banner image.
    if banner_image_id:
        banner_asset = db.session.get(MediaAsset, banner_image_id)

        if banner_asset is None:
            raise ValueError("Selected banner image does not exist.")

        if not banner_asset.active:
            raise ValueError("Selected banner image is inactive.")

        if banner_asset.media_type != "image":
            raise ValueError("Selected banner asset must be an image.")

    destination = Destination(
        name=name,
        slug=slug,
        country=(
            country.strip()
            if isinstance(country, str) and country.strip()
            else "Kenya"
        ),
        county=(
            county.strip()
            if isinstance(county, str) and county.strip()
            else None
        ),
        region=(
            region.strip()
            if isinstance(region, str) and region.strip()
            else None
        ),
        short_description=(
            short_description.strip()
            if isinstance(short_description, str)
            and short_description.strip()
            else None
        ),
        description=(
            description.strip()
            if isinstance(description, str) and description.strip()
            else None
        ),
        featured_image_id=featured_image_id,
        banner_image_id=banner_image_id or None,
        latitude=latitude,
        longitude=longitude,
        meta_title=(
            meta_title.strip()
            if isinstance(meta_title, str) and meta_title.strip()
            else None
        ),
        meta_description=(
            meta_description.strip()
            if isinstance(meta_description, str)
            and meta_description.strip()
            else None
        ),
        featured=featured,
        show_on_homepage=show_on_homepage,
        active=active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(destination)
    db.session.commit()

    return destination

# =============================================================================
# Destination Retrieval
# =============================================================================
def get_destination(destination_id):
    """
    Retrieve a destination by primary key.
    """

    if not destination_id:
        return None

    return db.session.get(
        Destination,
        destination_id,
    )


def get_destination_by_slug(slug):
    """
    Retrieve a destination by slug.
    """

    if not slug:
        return None

    normalized_slug = slug.strip().lower()

    if not normalized_slug:
        return None

    return Destination.query.filter(
        Destination.slug.ilike(normalized_slug)
    ).first()


def get_destination_by_name(name):
    """
    Retrieve a destination by name.
    """

    if not name:
        return None

    normalized_name = name.strip()

    if not normalized_name:
        return None

    return Destination.query.filter(
        Destination.name.ilike(normalized_name)
    ).first()


# =============================================================================
# Active Destination Retrieval
# =============================================================================

def get_active_destination(destination_id):
    """
    Retrieve a destination only if it is active.
    """

    destination = get_destination(destination_id)

    if destination is None:
        return None

    if not destination.active:
        return None

    return destination


def get_active_destination_by_slug(slug):
    """
    Retrieve a destination by slug only if it is active.
    """

    destination = get_destination_by_slug(slug)

    if destination is None:
        return None

    if not destination.active:
        return None

    return destination


# =============================================================================
# Destination Listing
# =============================================================================

def get_all_destinations(
    active=True,
    featured=None,
    show_on_homepage=None,
    country=None,
    county=None,
    region=None,
):
    """
    Retrieve destinations using optional filters.

    Visibility rules:
    - active=True: only active destinations.
    - featured=True: only featured destinations.
    - show_on_homepage=True: only destinations selected for the homepage.

    Optional filters can be combined.
    """

    query = Destination.query

    if active is not None:
        query = query.filter(
            Destination.active.is_(active)
        )

    if featured is not None:
        query = query.filter(
            Destination.featured.is_(featured)
        )

    if show_on_homepage is not None:
        query = query.filter(
            Destination.show_on_homepage.is_(show_on_homepage)
        )

    if country:
        query = query.filter(
            Destination.country.ilike(
                country.strip()
            )
        )

    if county:
        query = query.filter(
            Destination.county.ilike(
                county.strip()
            )
        )

    if region:
        query = query.filter(
            Destination.region.ilike(
                region.strip()
            )
        )

    return query.order_by(
        Destination.name.asc()
    ).all()

def get_active_destinations():
    """
    Retrieve all active destinations.
    """

    return get_all_destinations(
        active=True
    )

def get_inactive_destinations():
    """
    Retrieve all inactive destinations.
    """

    return get_all_destinations(
        active=False
    )

# =============================================================================
# Featured Destinations
# =============================================================================
def get_featured_destinations(
    active=True,
):
    """
    Retrieve featured destinations.
    """

    return get_all_destinations(
        active=active,
        featured=True,
    )


def set_destination_featured(
    destination,
    featured=True,
):
    """
    Set or remove featured status.
    """

    if destination is None:
        raise ValueError(
            "Destination is required."
        )

    destination.featured = bool(featured)
    destination.updated_at = datetime.utcnow()

    db.session.commit()

    return destination


def feature_destination(destination):
    """
    Mark a destination as featured.
    """

    return set_destination_featured(
        destination,
        True,
    )


def unfeature_destination(destination):
    """
    Remove a destination from featured sections.
    """

    return set_destination_featured(
        destination,
        False,
    )


# =============================================================================
# Destination Search
# =============================================================================

def search_destinations(
    query=None,
    active=True,
):
    """
    Search destinations by name, location and descriptions.
    """

    query_builder = Destination.query

    if active is not None:
        query_builder = query_builder.filter(
            Destination.active.is_(active)
        )

    if query and query.strip():

        search_term = f"%{query.strip()}%"

        query_builder = query_builder.filter(
            or_(
                Destination.name.ilike(search_term),
                Destination.slug.ilike(search_term),
                Destination.country.ilike(search_term),
                Destination.county.ilike(search_term),
                Destination.region.ilike(search_term),
                Destination.short_description.ilike(search_term),
                Destination.description.ilike(search_term),
            )
        )

    return query_builder.order_by(
        Destination.name.asc()
    ).all()


# =============================================================================
# Destination Updates
# =============================================================================
def update_destination(destination, **fields):
    """Update destination details, media, and homepage visibility."""

    if destination is None:
        raise ValueError("Destination is required.")

    allowed_fields = {
        "name",
        "slug",
        "country",
        "county",
        "region",
        "short_description",
        "description",
        "featured_image_id",
        "banner_image_id",
        "latitude",
        "longitude",
        "meta_title",
        "meta_description",
        "featured",
        "show_on_homepage",
        "active",
    }

    # Validate and normalize name.
    if "name" in fields:
        new_name = fields["name"]

        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("Destination name is required.")

        new_name = new_name.strip()

        existing = Destination.query.filter(
            and_(
                Destination.name.ilike(new_name),
                Destination.id != destination.id,
            )
        ).first()

        if existing:
            raise ValueError("A destination with this name already exists.")

        fields["name"] = new_name

    # Validate and normalize slug.
    if "slug" in fields:
        new_slug = fields["slug"]

        if not isinstance(new_slug, str) or not new_slug.strip():
            raise ValueError("Destination slug is required.")

        new_slug = new_slug.strip().lower()

        existing = Destination.query.filter(
            and_(
                Destination.slug.ilike(new_slug),
                Destination.id != destination.id,
            )
        ).first()

        if existing:
            raise ValueError("A destination with this slug already exists.")

        fields["slug"] = new_slug

    # Normalize optional text fields.
    text_fields = {
        "country",
        "county",
        "region",
        "short_description",
        "description",
        "meta_title",
        "meta_description",
    }

    for field in text_fields:
        if field not in fields:
            continue

        value = fields[field]

        if isinstance(value, str):
            value = value.strip() or None

        fields[field] = value

    # Validate featured image when provided.
    if "featured_image_id" in fields:
        image_id = fields["featured_image_id"]

        if not image_id:
            raise ValueError("Featured image is required.")

        asset = db.session.get(MediaAsset, image_id)

        if asset is None:
            raise ValueError("Selected featured image does not exist.")

        if not asset.active:
            raise ValueError("Selected featured image is inactive.")

        if asset.media_type != "image":
            raise ValueError("Selected featured asset must be an image.")

    # Validate optional banner image when provided.
    if "banner_image_id" in fields:
        banner_image_id = fields["banner_image_id"]

        if banner_image_id:
            asset = db.session.get(MediaAsset, banner_image_id)

            if asset is None:
                raise ValueError("Selected banner image does not exist.")

            if not asset.active:
                raise ValueError("Selected banner image is inactive.")

            if asset.media_type != "image":
                raise ValueError("Selected banner asset must be an image.")

        else:
            fields["banner_image_id"] = None

    # Determine the final visibility state, including unchanged values.
    final_featured = bool(fields.get("featured", destination.featured))
    final_active = bool(fields.get("active", destination.active))
    final_homepage = bool(
        fields.get("show_on_homepage", destination.show_on_homepage)
    )

    if final_homepage and not final_featured:
        raise ValueError(
            "A destination must be featured before it can appear on the homepage."
        )

    if final_homepage and not final_active:
        raise ValueError(
            "An inactive destination cannot appear on the homepage."
        )

    fields["featured"] = final_featured
    fields["active"] = final_active
    fields["show_on_homepage"] = final_homepage

    # Apply only supported fields.
    for field, value in fields.items():
        if field in allowed_fields:
            setattr(destination, field, value)

    destination.updated_at = datetime.utcnow()

    db.session.commit()

    return destination

# =============================================================================
# Destination Activation
# =============================================================================
def activate_destination(destination):
    """
    Activate a destination and restore the individual active state of each
    experience that was disabled by destination deactivation.

    Experiences that were intentionally inactive before the destination
    was deactivated remain inactive.
    """

    if destination is None:
        raise ValueError("Destination not found.")

    destination.active = True
    experiences = destination.experiences.all()
    for experience in experiences:
        if experience.destination_deactivation_previous_active is None:
            # No previous state was recorded. This normally applies to
            # experiences created while the destination was inactive.
            experience.active = True
        else:
            experience.active = (
                experience.destination_deactivation_previous_active
            )

        # The destination-level suspension has now been resolved.
        experience.destination_deactivation_previous_active = None

    db.session.commit()
    return destination

def deactivate_destination(destination):
    """
    Deactivate a destination and all of its experiences.

    Each experience's current active state is preserved so that it can be
    restored correctly when the destination is reactivated.

    Individual experience activation states are therefore not lost.
    """

    if destination is None:
        raise ValueError("Destination not found.")

    # Only capture the individual Experience state when the destination
    # is currently active. This prevents an already-deactivated destination
    # from overwriting the original states with False.
    if destination.active:
        experiences = destination.experiences.all()

        for experience in experiences:
            experience.destination_deactivation_previous_active = (
                experience.active
            )
            experience.active = False

    destination.active = False

    db.session.commit()

    return destination

def toggle_destination_status(destination):
    """
    Toggle a destination between active and inactive.
    """

    if destination is None:
        raise ValueError(
            "Destination is required."
        )

    destination.active = not destination.active
    destination.updated_at = datetime.utcnow()

    db.session.commit()

    return destination


# =============================================================================
# Destination Experience Retrieval
# =============================================================================
def get_destination_experiences(
    destination,
    active=True,):
    """
    Retrieve experiences belonging to a destination.
    """
    if isinstance(destination, int):
        destination = db.session.get(
            Destination,
            destination,)
    if destination is None:
        return []
    query = Experience.query.filter(
        Experience.destination_id == destination.id)
    if active is not None:
        query = query.filter(
            Experience.active.is_(active))

    return query.order_by(
        Experience.title.asc()
    ).all()

# =============================================================================
# Destination Experience Count
# =============================================================================

def count_destination_experiences(
    destination,
    active=True,
):
    """
    Count experiences belonging to a destination.
    """

    if isinstance(destination, int):
        destination = db.session.get(
            Destination,
            destination,
        )

    if destination is None:
        return 0

    query = Experience.query.filter(
        Experience.destination_id == destination.id
    )

    if active is not None:
        query = query.filter(
            Experience.active.is_(active)
        )

    return query.count()


# =============================================================================
# Destination Statistics
# =============================================================================

def get_destination_statistics(destination):
    """
    Return basic statistics for a destination.
    """

    if isinstance(destination, int):
        destination = db.session.get(
            Destination,
            destination,
        )

    if destination is None:
        return {
            "destination_id": None,
            "name": None,
            "active": False,
            "featured": False,
            "experience_count": 0,
        }

    return {
        "destination_id": destination.id,
        "name": destination.name,
        "active": destination.active,
        "featured": destination.featured,
        "experience_count": count_destination_experiences(
            destination
        ),
    }


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "get_destination_image_choices",
    "create_destination",
    "get_destination",
    "get_destination_by_slug",
    "get_destination_by_name",
    "get_active_destination",
    "get_active_destination_by_slug",
    "get_all_destinations",
    "get_active_destinations",
    "get_inactive_destinations",
    "get_featured_destinations",
    "set_destination_featured",
    "feature_destination",
    "unfeature_destination",
    "search_destinations",
    "update_destination",
    "activate_destination",
    "deactivate_destination",
    "toggle_destination_status",
    "get_destination_experiences",
    "count_destination_experiences",
    "get_destination_statistics",
]