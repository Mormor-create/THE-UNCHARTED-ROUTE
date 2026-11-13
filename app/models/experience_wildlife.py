"""
===============================================================================
The Uncharted Route
Experience Wildlife Model
===============================================================================

Associates wildlife species with experiences.

This model stores experiences-specific wildlife information such as:

• Sighting probability
• Best viewing season
• Best viewing time
• Guide notes
• Photography opportunities

One species can belong to many experiences.
One experiences can feature many species.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Wildlife Model
# =============================================================================

class ExperienceWildlife(db.Model):
    """
    Links wildlife species to experiences.
    """

    __tablename__ = "experience_wildlife"

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

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experiences.id"),
        nullable=False
    )

    species_id = db.Column(
        db.Integer,
        db.ForeignKey("wildlife_species.id"),
        nullable=False
    )

    # =========================================================================
    # Sighting Information
    # =========================================================================

    sighting_probability = db.Column(
        db.String(50),
        default="Common",
        nullable=False
    )
    # Guaranteed
    # Very Common
    # Common
    # Occasional
    # Rare

    best_season = db.Column(
        db.String(100)
    )
    # All Year
    # Dry Season
    # Wet Season
    # July–October

    best_time_of_day = db.Column(
        db.String(100)
    )
    # Sunrise
    # Morning
    # Afternoon
    # Sunset
    # Night

    # =========================================================================
    # Guide Notes
    # =========================================================================

    guide_notes = db.Column(
        db.Text
    )

    photography_notes = db.Column(
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

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experiences = db.relationship(
        "Experience",
        back_populates="wildlife"
    )

    species = db.relationship(
        "WildlifeSpecies",
        back_populates="experiences"
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
    def is_big_five(self):
        return self.species.is_big_five

    @property
    def is_endangered(self):
        return self.species.is_endangered

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ExperienceWildlife {self.species.common_name}>"
        )