"""
===============================================================================
The Uncharted Route
Stay Media Model
===============================================================================

Associates a Stay with an existing MediaAsset from the central Media Library.

No files are uploaded through this model.

MediaAsset remains the single source of truth for uploaded files.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Stay Media Model
# =============================================================================

class StayMedia(db.Model):
    """
    Associates a media asset with a Stay.
    """

    __tablename__ = "stay_media"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stays.id"
        ),
        nullable=False,
        index=True
    )

    media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Usage
    # =========================================================================

    usage = db.Column(
        db.String(30),
        nullable=False,
        default="gallery"
    )

    # hero
    # banner
    # thumbnail
    # gallery

    display_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    caption = db.Column(
        db.Text
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    stay = db.relationship(
        "Stay",
        back_populates="media"
    )

    media_asset = db.relationship(
        "MediaAsset",
        back_populates="stay_media"
    )

    # =========================================================================
    # Audit Fields
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_image(self):
        return bool(
            self.media_asset
            and self.media_asset.is_image
        )

    @property
    def is_video(self):
        return bool(
            self.media_asset
            and self.media_asset.is_video
        )

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<StayMedia "
            f"stay={self.stay_id} "
            f"media={self.media_asset_id} "
            f"usage={self.usage}>"
        )