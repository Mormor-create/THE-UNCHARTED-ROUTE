"""
The Uncharted Route
Experience Media Service
"""

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.models import (
    Experience,
    ExperienceMedia,
    MediaAsset,
    MediaFolder,
)
from app.services.media_service import get_cms_media_assets


VALID_USAGES = {
    "hero",
    "cover",
    "gallery",
    "thumbnail",
    "banner",
    "mobile_banner",
    "seo",
    "social",
    "brochure",
    "video",
}

EXPERIENCE_MEDIA_ROOT_NAME = "Experience Media Gallery"


def get_experience_for_media(experience_id):
    """Return an Experience or None."""
    return db.session.get(Experience, experience_id)


def get_experience_media(experience_id, media_id):
    """Return an assignment belonging to the specified Experience."""
    return ExperienceMedia.query.filter_by(
        id=media_id,
        experience_id=experience_id,
    ).first()


def get_experience_media_items(experience_id):
    """Return assignments ordered for the admin interface."""
    return (
        ExperienceMedia.query
        .filter_by(experience_id=experience_id)
        .order_by(
            ExperienceMedia.display_order.asc(),
            ExperienceMedia.id.asc(),
        )
        .all()
    )


# ---------------------------------------------------------------------
# Experience Media Gallery folder resolution
# ---------------------------------------------------------------------

def get_experience_media_root_folder():
    """
    Find the root folder named 'Experience Media Gallery'.

    The lookup uses the folder name rather than assuming a particular
    root-folder slug.
    """
    return (
        MediaFolder.query
        .filter(
            func.lower(MediaFolder.name) == EXPERIENCE_MEDIA_ROOT_NAME.lower(),
            MediaFolder.parent_id.is_(None),
            MediaFolder.active.is_(True),
        )
        .order_by(MediaFolder.id.asc())
        .first()
    )


def get_experience_media_folder(experience):
    """
    Find the folder belonging to an Experience.

    Expected structure:

        Experience Media Gallery/
            experience-slug/
                child folders...

    The Experience slug must match the corresponding child folder slug.
    """
    if experience is None or not experience.slug:
        return None

    root_folder = get_experience_media_root_folder()

    if root_folder is None:
        return None

    experience_slug = experience.slug.strip().lower()

    if not experience_slug:
        return None

    return (
        MediaFolder.query
        .filter_by(
            parent_id=root_folder.id,
            slug=experience_slug,
            active=True,
        )
        .first()
    )


def get_selectable_media_assets(experience_id):
    """
    Return active assets from the Experience's folder and descendants.

    A missing root folder or Experience folder returns an empty list.
    This function never falls back to the global Media Library.
    """
    experience = get_experience_for_media(experience_id)

    if experience is None:
        return []

    experience_folder = get_experience_media_folder(experience)

    if experience_folder is None:
        return []

    return get_cms_media_assets(
        folder_id=experience_folder.id,
        include_descendants=True,
        active_only=True,
    )


def is_asset_in_experience_media_folder(experience, media_asset_id):
    """
    Check whether an asset belongs to the Experience's folder
    or one of its active descendant folders.
    """
    if experience is None or not media_asset_id:
        return False

    experience_folder = get_experience_media_folder(experience)

    if experience_folder is None:
        return False

    selectable_assets = get_cms_media_assets(
        folder_id=experience_folder.id,
        include_descendants=True,
        active_only=False,
    )

    return any(
        asset.id == media_asset_id
        for asset in selectable_assets
    )


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def _validate_usage(usage):
    """Validate an assignment usage value."""
    if usage not in VALID_USAGES:
        raise ValueError("Please select a valid media usage.")


def _validate_asset(
    experience_id,
    media_asset_id,
    allow_existing_asset_id=None,
):
    """
    Validate the selected central asset.

    New selections must belong to the Experience's folder.

    During editing, the assignment's existing asset may remain selected
    even if it has since been moved outside that folder. It must still
    exist and be active, preserving the existing inactive-asset rule.
    """
    asset = db.session.get(MediaAsset, media_asset_id)

    if asset is None:
        raise ValueError("The selected media asset does not exist.")

    if not asset.active:
        raise ValueError(
            "This media asset is inactive. Activate it in the Media Library "
            "before assigning it to an experience."
        )

    # Preserve the current assignment's asset when it is unchanged.
    if (
        allow_existing_asset_id is not None
        and asset.id == allow_existing_asset_id
    ):
        return asset

    experience = get_experience_for_media(experience_id)

    if experience is None:
        raise ValueError("Experience not found.")

    if not is_asset_in_experience_media_folder(
        experience,
        asset.id,
    ):
        raise ValueError(
            "The selected media asset does not belong to this Experience's "
            "folder in the Experience Media Gallery."
        )

    return asset


def _validate_duplicate(
    experience_id,
    media_asset_id,
    usage,
    exclude_media_id=None,
):
    """Prevent duplicate asset + usage combinations per Experience."""
    query = ExperienceMedia.query.filter_by(
        experience_id=experience_id,
        media_asset_id=media_asset_id,
        usage=usage,
    )

    if exclude_media_id is not None:
        query = query.filter(
            ExperienceMedia.id != exclude_media_id
        )

    if query.first() is not None:
        raise ValueError(
            "This media asset is already assigned to this experience "
            "for the selected usage."
        )


def _enforce_single_active_hero(
    experience_id,
    current_media=None,
):
    """
    Keep at most one active hero assignment per Experience.

    Existing hero assignments are deactivated, not deleted.
    """
    query = ExperienceMedia.query.filter_by(
        experience_id=experience_id,
        usage="hero",
        active=True,
    )

    if current_media is not None:
        query = query.filter(
            ExperienceMedia.id != current_media.id
        )

    for previous_hero in query.all():
        previous_hero.active = False


# ---------------------------------------------------------------------
# Create assignment
# ---------------------------------------------------------------------

def create_experience_media(
    experience_id,
    media_asset_id,
    usage,
    display_order=0,
    title=None,
    caption=None,
    photographer=None,
    featured=False,
    active=True,
):
    """Create a media assignment for an Experience."""
    experience = get_experience_for_media(experience_id)

    if experience is None:
        raise ValueError("Experience not found.")

    _validate_usage(usage)

    _validate_asset(
        experience_id=experience_id,
        media_asset_id=media_asset_id,
    )

    _validate_duplicate(
        experience_id=experience_id,
        media_asset_id=media_asset_id,
        usage=usage,
    )

    if usage == "hero" and active:
        _enforce_single_active_hero(experience_id)

    assignment = ExperienceMedia(
        experience_id=experience_id,
        media_asset_id=media_asset_id,
        usage=usage,
        display_order=display_order,
        title=(title or "").strip() or None,
        caption=(caption or "").strip() or None,
        photographer=(photographer or "").strip() or None,
        featured=bool(featured),
        active=bool(active),
    )

    try:
        db.session.add(assignment)
        db.session.commit()
        return assignment

    except SQLAlchemyError:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------
# Update assignment
# ---------------------------------------------------------------------

def update_experience_media(
    assignment,
    media_asset_id,
    usage,
    display_order=0,
    title=None,
    caption=None,
    photographer=None,
    featured=False,
    active=True,
):
    """Update an existing media assignment."""
    if assignment is None:
        raise ValueError("Experience media assignment not found.")

    _validate_usage(usage)

    _validate_asset(
        experience_id=assignment.experience_id,
        media_asset_id=media_asset_id,
        allow_existing_asset_id=assignment.media_asset_id,
    )

    _validate_duplicate(
        experience_id=assignment.experience_id,
        media_asset_id=media_asset_id,
        usage=usage,
        exclude_media_id=assignment.id,
    )

    if usage == "hero" and active:
        _enforce_single_active_hero(
            assignment.experience_id,
            current_media=assignment,
        )

    assignment.media_asset_id = media_asset_id
    assignment.usage = usage
    assignment.display_order = display_order
    assignment.title = (title or "").strip() or None
    assignment.caption = (caption or "").strip() or None
    assignment.photographer = (
        (photographer or "").strip() or None
    )
    assignment.featured = bool(featured)
    assignment.active = bool(active)

    try:
        db.session.commit()
        return assignment

    except SQLAlchemyError:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------
# Activate / deactivate assignment
# ---------------------------------------------------------------------

def set_experience_media_active(assignment, active):
    """Activate or deactivate an assignment without deleting it."""
    if assignment is None:
        raise ValueError("Experience media assignment not found.")

    if active:
        _validate_asset(
            experience_id=assignment.experience_id,
            media_asset_id=assignment.media_asset_id,
            allow_existing_asset_id=assignment.media_asset_id,
        )

        if assignment.usage == "hero":
            _enforce_single_active_hero(
                assignment.experience_id,
                current_media=assignment,
            )

    assignment.active = bool(active)

    try:
        db.session.commit()
        return assignment

    except SQLAlchemyError:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------
# Delete assignment only — never delete the central asset
# ---------------------------------------------------------------------
def delete_experience_media(assignment):
    """
    Delete the association only.

    The central MediaAsset and its physical file are not deleted.
    """
    if assignment is None:
        raise ValueError("Experience media assignment not found.")

    try:
        db.session.delete(assignment)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        raise