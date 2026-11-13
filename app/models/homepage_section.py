"""
===============================================================================
The Uncharted Route — Homepage Section Model
===============================================================================
Represents an individual CMS-managed section of the public homepage.
Supported section concepts include:
• Hero
• Featured Experiences
• Destination Cards
• Why Travel With Us
• Featured Journal
• Homepage Media
• Promotional / custom sections

Sections are ordered using display_order.
The model stores section configuration and presentation content but does not
duplicate Experience, Destination, BlogPost, or MediaAsset records.
Media is connected through the central MediaAsset model.
===============================================================================
"""
from datetime import datetime
from extensions import db

# =============================================================================
# Homepage Section
# =============================================================================
class HomepageSection(db.Model):
    """
    CMS-managed section appearing on the public homepage.
    """
    __tablename__ = "homepage_sections"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Homepage Relationship
    # =========================================================================
    homepage_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "homepages.id",
            ondelete="CASCADE",
        ),nullable=False,index=True,)
    homepage = db.relationship("Homepage",back_populates="sections",)

    # =========================================================================
    # Section Identity
    # =========================================================================
    section_type = db.Column(db.String(50),nullable=False,index=True,)
    title = db.Column(db.String(255),nullable=True,)
    subtitle = db.Column(db.String(500),nullable=True,)

    # =========================================================================
    # Section Content
    # =========================================================================
    content = db.Column(db.Text,nullable=True,)

    # =========================================================================
    # Call To Action
    # =========================================================================
    cta_text = db.Column(db.String(100),nullable=True,)
    cta_url = db.Column(db.String(500),nullable=True,)

    # =========================================================================
    # Media Asset
    # =========================================================================
    media_asset_id = db.Column(db.Integer,db.ForeignKey("media_assets.id",ondelete="SET NULL",),nullable=True,index=True,)
    media_asset = db.relationship("MediaAsset",lazy="joined",)

    # =========================================================================
    # Display Configuration
    # =========================================================================
    display_order = db.Column(db.Integer,nullable=False,default=0,index=True,)
    is_visible = db.Column(db.Boolean,nullable=False,default=True,server_default=db.true(),)

    # =========================================================================
    # Timestamps
    # =========================================================================
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<HomepageSection "
            f"id={self.id!r} "
            f"type={self.section_type!r} "
            f"order={self.display_order!r}>")

    # =========================================================================
    # Visibility Helpers
    # =========================================================================
    def show(self):
        """
        Make the section visible on the public homepage.
        """
        self.is_visible = True

    def hide(self):
        """
        Hide the section without deleting its configuration.
        """
        self.is_visible = False

    # =========================================================================
    # Section Type
    # =========================================================================
    @property
    def normalized_type(self):
        """
        Return the section type in normalized form.
        """
        return (
            self.section_type.strip().lower()
            if self.section_type
            else "")

    # =========================================================================
    # Section Type Helpers
    # =========================================================================
    @property
    def is_hero(self):
        return self.normalized_type == "hero"

    @property
    def is_featured_experiences(self):
        return self.normalized_type == "featured_experiences"

    @property
    def is_destinations(self):
        return self.normalized_type == "destinations"

    @property
    def is_featured_experience_card(self):
        return self.normalized_type == "featured_experience_card"

    @property
    def is_destination_card(self):
        return self.normalized_type == "destination_card"

    @property
    def is_why_travel(self):
        return self.normalized_type == "why_travel"

    @property
    def is_journal(self):
        return self.normalized_type == "journal"

    @property
    def is_media(self):
        return self.normalized_type == "media"

    @property
    def is_promotional(self):
        return self.normalized_type == "promotional"