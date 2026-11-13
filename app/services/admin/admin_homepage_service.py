"""
===============================================================================
The Uncharted Route — Administrative Homepage Service
===============================================================================

Business logic for the administrative homepage CMS.

Responsibilities
----------------
• Retrieve the current homepage
• Create the initial homepage configuration when necessary
• Retrieve homepage sections
• Create homepage sections
• Update homepage sections
• Delete homepage sections
• Control section visibility
• Control section ordering
• Update homepage metadata
• Publish / unpublish the homepage
• Validate homepage media assets
• Enforce administrator authorization

Architecture
------------
Routes handle HTTP concerns.

    Route → Form → Service → Model

Forms handle input validation.

Models handle persistence and model behavior.

This service handles homepage-specific business rules.

The homepage does not duplicate:

• Experience
• Destination
• BlogPost
• Booking
• Testimonial
• MediaAsset

Those systems remain responsible for their own records.

Homepage structure:

    Homepage
        │
        └── HomepageSection
                │
                └── MediaAsset

Homepage section types
----------------------
hero
featured_experiences
featured_experience_card
destinations
destination_card
why_travel
journal
media
promotional

Authorization
-------------
All homepage mutation operations require an active administrator.

During the current CMS setup/testing phase, _require_admin()
remains intentionally disabled. Route-level authorization can be
restored once CMS configuration/testing is complete.

===============================================================================
"""

from datetime import datetime

from app.models import (
    Homepage,
    HomepageSection,
    MediaAsset,
)

from extensions import db


# =============================================================================
# Constants
# =============================================================================
ALLOWED_SECTION_TYPES = {
    # -------------------------------------------------------------------------
    # Hero
    # -------------------------------------------------------------------------
    "hero",
    # -------------------------------------------------------------------------
    # Experiences
    # -------------------------------------------------------------------------
    # Section heading / introductory content
    "featured_experiences",

    # Individual experience card
    "featured_experience_card",

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------
    # Section heading / introductory content
    "destinations",

    # Individual destination card
    "destination_card",

    # -------------------------------------------------------------------------
    # Other homepage sections
    # -------------------------------------------------------------------------
    "why_travel",
    "journal",
    "media",
    "promotional",
}


ALLOWED_HOMEPAGE_MEDIA_TYPES = {
    "image",
    "video",
}


# =============================================================================
# Authorization
# =============================================================================

def can_manage_homepage(user):
    """
    Determine whether a user may manage the homepage CMS.

    Parameters
    ----------
    user : User
        User attempting to access homepage management.

    Returns
    -------
    bool
        True when the user is an active administrator.
    """

    if user is None:
        return False

    return bool(
        user.is_active
        and user.is_admin
    )


def _require_admin(user):
    """
    Homepage authorization is temporarily disabled during CMS setup
    and testing.

    Route-level administrator protection can be restored after the
    homepage CMS has been configured and tested.
    """

    return None


# =============================================================================
# Current Homepage
# =============================================================================

def get_current_homepage():
    """
    Return the current homepage configuration.

    If no homepage configuration exists yet,
    Homepage.get_current() creates the initial record.

    Returns
    -------
    Homepage
        Current homepage configuration.
    """

    return Homepage.get_current()


# =============================================================================
# Homepage Retrieval
# =============================================================================

def get_homepage(homepage_id):
    """
    Retrieve a homepage by primary key.

    Parameters
    ----------
    homepage_id : int
        Homepage primary key.

    Returns
    -------
    Homepage | None
        Matching homepage or None when it does not exist.
    """

    if not homepage_id:
        return None

    return db.session.get(
        Homepage,
        homepage_id,
    )


# =============================================================================
# Homepage Update
# =============================================================================

def update_homepage(
    acting_admin,
    homepage,
    title=None,
    description=None,
    meta_title=None,
    meta_description=None,
    is_published=None,
):
    """
    Update homepage configuration.
    """

    _require_admin(acting_admin)

    if homepage is None:
        raise ValueError(
            "A valid homepage is required."
        )

    homepage.title = (
        title.strip()
        if title and title.strip()
        else None
    )

    homepage.description = (
        description.strip()
        if description and description.strip()
        else None
    )

    homepage.meta_title = (
        meta_title.strip()
        if meta_title and meta_title.strip()
        else None
    )

    homepage.meta_description = (
        meta_description.strip()
        if meta_description and meta_description.strip()
        else None
    )

    if is_published is not None:
        homepage.is_published = bool(
            is_published
        )

    homepage.updated_at = datetime.utcnow()

    db.session.commit()

    return homepage


# =============================================================================
# Publish Homepage
# =============================================================================

def publish_homepage(
    acting_admin,
    homepage,
):
    """
    Publish the homepage.
    """

    _require_admin(acting_admin)

    if homepage is None:
        raise ValueError(
            "A valid homepage is required."
        )

    homepage.publish()
    homepage.updated_at = datetime.utcnow()

    db.session.commit()

    return homepage


# =============================================================================
# Unpublish Homepage
# =============================================================================

def unpublish_homepage(
    acting_admin,
    homepage,
):
    """
    Unpublish the homepage.
    """

    _require_admin(acting_admin)

    if homepage is None:
        raise ValueError(
            "A valid homepage is required."
        )

    homepage.unpublish()
    homepage.updated_at = datetime.utcnow()

    db.session.commit()

    return homepage


# =============================================================================
# Homepage Sections
# =============================================================================

def get_homepage_sections(
    homepage,
    visible_only=False,
):
    """
    Retrieve homepage sections in display order.
    """

    if homepage is None:
        return []

    query = HomepageSection.query.filter(
        HomepageSection.homepage_id == homepage.id
    )

    if visible_only:
        query = query.filter(
            HomepageSection.is_visible.is_(True)
        )

    return query.order_by(
        HomepageSection.display_order.asc(),
        HomepageSection.id.asc(),
    ).all()


# =============================================================================
# Homepage Section Retrieval
# =============================================================================

def get_homepage_section(section_id):
    """
    Retrieve a homepage section by primary key.
    """

    if not section_id:
        return None

    return db.session.get(
        HomepageSection,
        section_id,
    )


# =============================================================================
# Section Type Validation
# =============================================================================

def _normalize_section_type(section_type):
    """
    Normalize and validate a homepage section type.

    Returns
    -------
    str
        Normalized section type.

    Raises
    ------
    ValueError
        When the section type is invalid.
    """

    normalized_type = (
        section_type.strip().lower()
        if isinstance(section_type, str)
        else ""
    )

    if normalized_type not in ALLOWED_SECTION_TYPES:
        raise ValueError(
            "Invalid homepage section type."
        )

    return normalized_type


# =============================================================================
# Media Asset Validation
# =============================================================================

def get_homepage_media_asset(
    media_asset_id,
):
    """
    Retrieve and validate a media asset for homepage use.

    Only active image and video assets are accepted.

    Parameters
    ----------
    media_asset_id : int
        MediaAsset primary key.

    Returns
    -------
    MediaAsset | None
        Valid media asset or None when no asset is selected.
    """

    if not media_asset_id:
        return None

    asset = db.session.get(
        MediaAsset,
        media_asset_id,
    )

    if asset is None:
        raise ValueError(
            "The selected media asset does not exist."
        )

    if not asset.active:
        raise ValueError(
            "The selected media asset is inactive."
        )

    if asset.media_type not in ALLOWED_HOMEPAGE_MEDIA_TYPES:
        raise ValueError(
            "The selected media asset cannot be used on the homepage."
        )

    return asset


# =============================================================================
# Create Homepage Section
# =============================================================================

def create_homepage_section(
    acting_admin,
    homepage,
    section_type,
    title=None,
    subtitle=None,
    content=None,
    cta_text=None,
    cta_url=None,
    media_asset_id=None,
    display_order=0,
    is_visible=True,
):
    """
    Create a new homepage section.
    """

    _require_admin(acting_admin)

    if homepage is None:
        raise ValueError(
            "A valid homepage is required."
        )

    normalized_type = _normalize_section_type(
        section_type
    )

    # -------------------------------------------------------------------------
    # Display order
    # -------------------------------------------------------------------------

    if display_order is None:
        display_order = 0

    try:
        display_order = int(display_order)
    except (TypeError, ValueError):
        raise ValueError(
            "Display order must be a valid number."
        )

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    # -------------------------------------------------------------------------
    # Media
    # -------------------------------------------------------------------------

    media_asset = get_homepage_media_asset(
        media_asset_id
    )

    # -------------------------------------------------------------------------
    # Create section
    # -------------------------------------------------------------------------

    section = HomepageSection(
        homepage_id=homepage.id,

        section_type=normalized_type,

        title=(
            title.strip()
            if isinstance(title, str) and title.strip()
            else None
        ),

        subtitle=(
            subtitle.strip()
            if isinstance(subtitle, str) and subtitle.strip()
            else None
        ),

        content=(
            content.strip()
            if isinstance(content, str) and content.strip()
            else None
        ),

        cta_text=(
            cta_text.strip()
            if isinstance(cta_text, str) and cta_text.strip()
            else None
        ),

        cta_url=(
            cta_url.strip()
            if isinstance(cta_url, str) and cta_url.strip()
            else None
        ),

        media_asset=media_asset,

        display_order=display_order,

        is_visible=bool(is_visible),
    )

    db.session.add(section)
    db.session.commit()

    return section


# =============================================================================
# Update Homepage Section
# =============================================================================

def update_homepage_section(
    acting_admin,
    section,
    section_type=None,
    title=None,
    subtitle=None,
    content=None,
    cta_text=None,
    cta_url=None,
    media_asset_id=None,
    display_order=None,
    is_visible=None,
):
    """
    Update an existing homepage section.

    Media behavior
    --------------
    media_asset_id = None
        Leave the existing media unchanged.

    media_asset_id = 0
        Explicitly remove the existing media.

    media_asset_id = valid ID
        Replace the existing media with that asset.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    # -------------------------------------------------------------------------
    # Section type
    # -------------------------------------------------------------------------

    if section_type is not None:
        section.section_type = _normalize_section_type(
            section_type
        )

    # -------------------------------------------------------------------------
    # Text fields
    # -------------------------------------------------------------------------

    if title is not None:
        section.title = (
            title.strip()
            if isinstance(title, str) and title.strip()
            else None
        )

    if subtitle is not None:
        section.subtitle = (
            subtitle.strip()
            if isinstance(subtitle, str) and subtitle.strip()
            else None
        )

    if content is not None:
        section.content = (
            content.strip()
            if isinstance(content, str) and content.strip()
            else None
        )

    if cta_text is not None:
        section.cta_text = (
            cta_text.strip()
            if isinstance(cta_text, str) and cta_text.strip()
            else None
        )

    if cta_url is not None:
        section.cta_url = (
            cta_url.strip()
            if isinstance(cta_url, str) and cta_url.strip()
            else None
        )

    # -------------------------------------------------------------------------
    # Media
    #
    # None = do not change existing media
    # 0    = explicitly remove existing media
    # ID   = use selected MediaAsset
    # -------------------------------------------------------------------------

    if media_asset_id is not None:

        if media_asset_id == 0:
            section.media_asset = None

        else:
            section.media_asset = get_homepage_media_asset(
                media_asset_id
            )

    # -------------------------------------------------------------------------
    # Display order
    # -------------------------------------------------------------------------

    if display_order is not None:

        try:
            display_order = int(display_order)
        except (TypeError, ValueError):
            raise ValueError(
                "Display order must be a valid number."
            )

        if display_order < 0:
            raise ValueError(
                "Display order cannot be negative."
            )

        section.display_order = display_order

    # -------------------------------------------------------------------------
    # Visibility
    # -------------------------------------------------------------------------

    if is_visible is not None:
        section.is_visible = bool(
            is_visible
        )

    section.updated_at = datetime.utcnow()

    db.session.commit()

    return section


# =============================================================================
# Delete Homepage Section
# =============================================================================

def delete_homepage_section(
    acting_admin,
    section,
):
    """
    Delete a homepage section.

    The associated MediaAsset is NOT deleted.

    MediaAssets belong to the central Media Library and may be
    referenced by other parts of the website.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    db.session.delete(section)
    db.session.commit()

    return True


# =============================================================================
# Show Homepage Section
# =============================================================================

def show_homepage_section(
    acting_admin,
    section,
):
    """
    Make a homepage section visible.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    section.show()
    section.updated_at = datetime.utcnow()

    db.session.commit()

    return section


# =============================================================================
# Hide Homepage Section
# =============================================================================

def hide_homepage_section(
    acting_admin,
    section,
):
    """
    Hide a homepage section without deleting it.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    section.hide()
    section.updated_at = datetime.utcnow()

    db.session.commit()

    return section


# =============================================================================
# Set Homepage Section Visibility
# =============================================================================

def set_homepage_section_visibility(
    acting_admin,
    section,
    is_visible,
):
    """
    Explicitly set homepage section visibility.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    section.is_visible = bool(
        is_visible
    )

    section.updated_at = datetime.utcnow()

    db.session.commit()

    return section


# =============================================================================
# Reorder Homepage Section
# =============================================================================

def reorder_homepage_section(
    acting_admin,
    section,
    display_order,
):
    """
    Change the display order of a homepage section.
    """

    _require_admin(acting_admin)

    if section is None:
        raise ValueError(
            "A valid homepage section is required."
        )

    if display_order is None:
        raise ValueError(
            "A display order is required."
        )

    try:
        display_order = int(display_order)
    except (TypeError, ValueError):
        raise ValueError(
            "Display order must be a valid number."
        )

    if display_order < 0:
        raise ValueError(
            "Display order cannot be negative."
        )

    section.display_order = display_order
    section.updated_at = datetime.utcnow()

    db.session.commit()

    return section


# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "can_manage_homepage",
    "get_current_homepage",
    "get_homepage",
    "get_homepage_sections",
    "get_homepage_section",
    "get_homepage_media_asset",
    "update_homepage",
    "publish_homepage",
    "unpublish_homepage",
    "create_homepage_section",
    "update_homepage_section",
    "delete_homepage_section",
    "show_homepage_section",
    "hide_homepage_section",
    "set_homepage_section_visibility",
    "reorder_homepage_section",
]