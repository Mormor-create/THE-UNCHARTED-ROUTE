"""Primary image assignment and resolution for TUR experiences."""

from flask import has_request_context, url_for

from extensions import db
from app.models import ExperienceMedia
from app.models.media_asset import MediaAsset

PRIMARY_IMAGE_USAGES = ("hero", "cover", "thumbnail")

def set_primary_experience_image(experience, asset_id):
    """
    Associate a Media Library image with an experience.

    An empty asset ID leaves the existing image unchanged.
    Returns the selected MediaAsset, or None if no image was selected.
    """
    if asset_id in (None, "", 0, "0"):
        return None

    try:
        asset_id = int(asset_id)
    except (TypeError, ValueError):
        raise ValueError("Select a valid image from the Media Library.")

    asset = MediaAsset.query.filter_by(
        id=asset_id,
        active=True,
    ).first()

    if asset is None:
        raise ValueError(
            "The selected image does not exist or is inactive."
        )

    if asset.media_type != "image":
        raise ValueError("The primary image must be an image asset.")

    if not asset.browser_url:
        raise ValueError(
            "The selected image has no browser-accessible URL."
        )

    # Ensure the experience has a database ID before querying associations.
    db.session.flush()

    # Reuse the existing primary association when possible.
    primary_media = (
        ExperienceMedia.query
        .filter(
            ExperienceMedia.experience_id == experience.id,
            ExperienceMedia.usage.in_(PRIMARY_IMAGE_USAGES),
        )
        .order_by(
            ExperienceMedia.display_order.asc(),
            ExperienceMedia.id.asc(),
        )
        .first()
    )

    if primary_media is None:
        primary_media = ExperienceMedia(
            experience_id=experience.id,
            media_asset_id=asset.id,
            usage="hero",
            display_order=0,
            featured=True,
            active=True,
        )
        db.session.add(primary_media)
    else:
        primary_media.media_asset = asset
        primary_media.usage = "hero"
        primary_media.display_order = 0
        primary_media.featured = True
        primary_media.active = True

    # Flush before comparing association IDs.
    db.session.flush()

    # Deactivate other primary-image associations without Query.update().
    # This avoids SQLAlchemy's order_by()/bulk-update conflict.
    other_primary_media = (
        ExperienceMedia.query
        .filter(
            ExperienceMedia.experience_id == experience.id,
            ExperienceMedia.id != primary_media.id,
            ExperienceMedia.usage.in_(PRIMARY_IMAGE_USAGES),
            ExperienceMedia.active.is_(True),
        )
        .all()
    )

    for association in other_primary_media:
        association.active = False

    # Retain a legacy value for existing code, but use browser_url for display.
    experience.featured_image = (
        asset.file_path or asset.filename or asset.file_url
    )

    return asset

def get_primary_experience_image_url(experience):
    """
    Return the image URL explicitly associated with this experience.

    An experience without a valid image association has no image URL.
    Legacy featured_image values are intentionally not used as fallbacks.
    """
    associations = (
        ExperienceMedia.query
        .filter(
            ExperienceMedia.experience_id == experience.id,
            ExperienceMedia.active.is_(True),
            ExperienceMedia.usage.in_(PRIMARY_IMAGE_USAGES),
        )
        .order_by(
            ExperienceMedia.featured.desc(),
            ExperienceMedia.display_order.asc(),
            ExperienceMedia.id.asc(),
        )
        .all()
    )

    for association in associations:
        asset = association.media_asset

        if (
            asset is not None
            and asset.active
            and asset.media_type == "image"
            and asset.browser_url
        ):
            return asset.browser_url

    return None

def get_primary_experience_image_urls(experiences):
    """Return {experience_id: browser_url} for an experience collection."""
    image_urls = {}

    for experience in experiences:
        image_url = get_primary_experience_image_url(experience)

        if image_url:
            image_urls[experience.id] = image_url

    return image_urls