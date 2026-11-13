"""
===============================================================================
The Uncharted Route
Reusable Page Hero Model
===============================================================================

Reusable page-level hero content for the public website.

A PageHero is associated with a public website page through `page_key`
rather than being directly attached to Experience, Destination, Stay,
Testimonial, Contact, etc.

Hero media is selected from the centralized MediaAsset / DAM system.
"""
from datetime import datetime
from extensions import db

# =============================================================================
# Page Hero Model
# =============================================================================
class PageHero(db.Model):
    """
    Reusable page-level hero configuration.

    Each public CMS page can have one reusable hero configuration identified
    by a unique page_key.

    Examples:

        experiences
        destinations
        stays
        about
        contact
        conservation
        journal

    The actual page determines which PageHero it wants to load.
    """

    __tablename__ = "page_heroes"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Page Identity
    # =========================================================================

    page_key = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True
    )

    page_name = db.Column(
        db.String(150),
        nullable=False
    )

    # =========================================================================
    # Hero Content
    # =========================================================================

    eyebrow = db.Column(
        db.String(150)
    )

    heading = db.Column(
        db.String(255),
        nullable=False
    )

    subheading = db.Column(
        db.Text
    )

    # =========================================================================
    # Desktop Hero Media
    # =========================================================================

    desktop_media_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    desktop_media = db.relationship(
        "MediaAsset",
        foreign_keys=[desktop_media_id]
    )

    # =========================================================================
    # Mobile Hero Media
    # =========================================================================

    mobile_media_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_assets.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    mobile_media = db.relationship(
        "MediaAsset",
        foreign_keys=[mobile_media_id]
    )

    # =========================================================================
    # Hero Presentation
    # =========================================================================

    overlay_style = db.Column(
        db.String(50),
        nullable=False,
        default="dark"
    )
    # Examples:
    #
    # dark
    # light
    # none

    image_position = db.Column(
        db.String(50),
        nullable=False,
        default="center"
    )
    # Examples:
    #
    # center
    # center top
    # center center
    # center bottom
    # left center
    # right center

    # =========================================================================
    # Primary Call To Action
    # =========================================================================

    primary_cta_text = db.Column(
        db.String(100)
    )

    primary_cta_url = db.Column(
        db.String(500)
    )

    # =========================================================================
    # Secondary Call To Action
    # =========================================================================

    secondary_cta_text = db.Column(
        db.String(100)
    )

    secondary_cta_url = db.Column(
        db.String(500)
    )

    # =========================================================================
    # Status / Display
    # =========================================================================

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # =========================================================================
    # Internal Notes
    # =========================================================================
    notes = db.Column(db.Text)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Properties
    # =========================================================================
    @property
    def desktop_image_url(self):
        """
        Returns the desktop hero media URL when available.
        """

        if self.desktop_media:
            return (
                self.desktop_media.file_url
                or self.desktop_media.file_path
            )

        return None

    @property
    def mobile_image_url(self):
        """
        Returns the mobile hero media URL when available.

        Falls back to the desktop media when a dedicated mobile asset
        has not been selected.
        """

        if self.mobile_media:
            return (
                self.mobile_media.file_url
                or self.mobile_media.file_path
            )

        return self.desktop_image_url

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<PageHero {self.page_key}>"
        )