"""
===============================================================================
The Uncharted Route
Experience Media Model
===============================================================================
Defines how media assets are associated with experiences.
One experiences can have multiple media assets.

Examples
--------

• Hero Image
• Cover Image
• Gallery Image
• Thumbnail
• Mobile Banner
• SEO Image
• Social Share Image
• Video
• PDF Brochure

The actual file is stored in MediaAsset.

This model stores how the file is used within an experiences.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Media Model
# =============================================================================
class ExperienceMedia(db.Model):
    """
    Associates media assets with experiences.
    """

    __tablename__ = "experience_media"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Foreign Keys
    # =========================================================================

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "experiences.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Usage
    # =========================================================================

    usage = db.Column(
        db.String(50),
        nullable=False,
        default="gallery"
    )

    # Supported usage values:
    #
    # hero
    # cover
    # gallery
    # thumbnail
    # banner
    # mobile_banner
    # seo
    # social
    # brochure
    # video

    # =========================================================================
    # Display
    # =========================================================================

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =========================================================================
    # Optional Information
    # =========================================================================

    title = db.Column(
        db.String(255)
    )

    caption = db.Column(
        db.Text
    )

    photographer = db.Column(
        db.String(255)
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experience = db.relationship(
        "Experience",
        back_populates="media"
    )

    media_asset = db.relationship(
        "MediaAsset",
        back_populates="experience_media"
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
    # Helper Properties
    # =========================================================================

    @property
    def is_hero(self):
        return self.usage == "hero"

    @property
    def is_cover(self):
        return self.usage == "cover"

    @property
    def is_gallery(self):
        return self.usage == "gallery"

    @property
    def is_thumbnail(self):
        return self.usage == "thumbnail"

    @property
    def is_banner(self):
        return self.usage == "banner"

    @property
    def is_mobile_banner(self):
        return self.usage == "mobile_banner"

    @property
    def is_seo(self):
        return self.usage == "seo"

    @property
    def is_social(self):
        return self.usage == "social"

    @property
    def is_brochure(self):
        return self.usage == "brochure"

    @property
    def is_video(self):
        return self.usage == "video"

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ExperienceMedia "
            f"experience_id={self.experience_id} "
            f"media_asset_id={self.media_asset_id} "
            f"usage='{self.usage}'>"
        )