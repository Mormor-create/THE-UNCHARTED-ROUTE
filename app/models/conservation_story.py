"""
===============================================================================
The Uncharted Route
Conservation Story Model
===============================================================================

Reusable conservation stories that can be attached to one or more experiences.

Examples

• David Sheldrick Elephant Orphanage
• Black Rhino Conservation
• Mountain Bongo Recovery Programme
• Sea Turtle Conservation
• Grevy's Zebra Trust
• Giraffe Conservation Foundation
• Coral Reef Restoration
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Conservation Story Model
# =============================================================================

class ConservationStory(db.Model):
    """
    Represents a conservation initiative or educational story.
    """

    __tablename__ = "conservation_stories"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Basic Information
    # =========================================================================

    title = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(255),
        unique=True,
        index=True
    )

    short_description = db.Column(
        db.Text
    )

    full_story = db.Column(
        db.Text
    )

    # =========================================================================
    # Classification
    # =========================================================================

    conservation_type = db.Column(
        db.String(100),
        nullable=False
    )
    # Wildlife
    # Marine
    # Forest
    # Community
    # Climate
    # Research
    # Education

    focus_species = db.Column(
        db.String(255)
    )

    organization_name = db.Column(
        db.String(255)
    )

    organization_website = db.Column(
        db.String(255)
    )

    # =========================================================================
    # Educational Information
    # =========================================================================

    why_it_matters = db.Column(
        db.Text
    )

    visitor_impact = db.Column(
        db.Text
    )

    how_guests_help = db.Column(
        db.Text
    )

    interesting_fact = db.Column(
        db.Text
    )

    # =========================================================================
    # Display
    # =========================================================================

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

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # =========================================================================
    # Optional Hero Image
    # =========================================================================

    hero_media_id = db.Column(
        db.Integer,
        db.ForeignKey("media_assets.id")
    )

    hero_media = db.relationship(
        "MediaAsset"
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experiences = db.relationship(
        "Experience",
        back_populates="conservation_story",
        lazy="dynamic"
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
    def experience_count(self):
        return self.experiences.count()

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ConservationStory {self.title}>"
        )