"""
===============================================================================
The Uncharted Route
Signature Moment Model
===============================================================================
Represents the unforgettable moments that define an experiences.
Unlike highlights, Signature Moments are emotional, memorable moments that
guests are likely to remember long after the experiences ends.

Examples
• Watching the sunrise over the Maasai Mara
• Feeding giraffes by hand
• Elephant feeding at the orphanage
• Sundowner overlooking the savannah
• Watching flamingos take flight
• Private beach sunset dinner
"""
from datetime import datetime
from extensions import db
# =============================================================================
# Signature Moment Model
# =============================================================================
class SignatureMoment(db.Model):
    """
    Represents a memorable moment within an experiences.
    """
    __tablename__ = "signature_moments"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Relationships
    # =========================================================================
    signature_moment_experiences = db.Table(
        "signature_moment_experiences",
        db.Column(
            "signature_moment_id",
            db.Integer,
            db.ForeignKey("signature_moments.id"),
            primary_key=True,
        ),
        db.Column(
            "experience_id",
            db.Integer,
            db.ForeignKey("experiences.id"),
            primary_key=True,),)
    hero_media_id = db.Column(db.Integer,db.ForeignKey("media_assets.id"))

    # =========================================================================
    # Basic Information
    # =========================================================================
    title = db.Column(db.String(255),nullable=False)
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)

    # =========================================================================
    # Classification
    # =========================================================================
    moment_type = db.Column(db.String(100),nullable=False,default="Experience")
    # Wildlife
    # Adventure
    # Luxury
    # Cultural
    # Coastal
    # Photography
    # Dining
    # Scenic
    # Conservation

    # =========================================================================
    # Timing
    # =========================================================================
    expected_time = db.Column(db.String(100))
    # Sunrise
    # Morning
    # Afternoon
    # Sunset
    # Evening
    # Night

    estimated_duration = db.Column(db.Integer)
    # Minutes

    # =========================================================================
    # Experience Information
    # =========================================================================
    best_season = db.Column(db.String(255))
    photography_recommended = db.Column(db.Boolean,default=True,nullable=False)
    emotional_impact = db.Column(db.String(50),default="High")
    # Moderate
    # High
    # Exceptional

    # =========================================================================
    # Display
    # =========================================================================
    featured = db.Column(db.Boolean,default=True,nullable=False)
    display_order = db.Column(db.Integer,default=1,nullable=False)
    active = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    experiences = db.relationship(
        "Experience",
        secondary="signature_moment_experiences",
        back_populates="signature_moments",
        lazy="dynamic",)
    hero_media = db.relationship("MediaAsset")

    # =========================================================================
    # Audit Fields
    # =========================================================================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def has_media(self):
        return self.hero_media is not None

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<SignatureMoment {self.title}>")