"""
===============================================================================
The Uncharted Route
Experience Highlight Model
===============================================================================

Stores the key highlights of an experiences.

Examples

• Sunrise Game Drive
• Luxury Land Cruiser
• Private Guide
• Bush Breakfast
• Big Five Wildlife
• Hotel Pickup
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Highlight Model
# =============================================================================

class ExperienceHighlight(db.Model):
    """
    Represents one highlight belonging to an experiences.
    """

    __tablename__ = "experience_highlights"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------------------------
    # Experience Relationship
    # -------------------------------------------------------------------------

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experiences.id"),
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Highlight Information
    # -------------------------------------------------------------------------

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    icon = db.Column(
        db.String(100),
        default="sparkles"
    )

    # -------------------------------------------------------------------------
    # Highlight Type
    # -------------------------------------------------------------------------

    highlight_type = db.Column(
        db.String(100),
        default="General"
    )

    # Examples
    #
    # Wildlife
    # Scenic
    # Luxury
    # Food
    # Adventure
    # Photography
    # Family
    # Cultural

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------

    experiences = db.relationship(
        "Experience",
        back_populates="highlights"
    )

    # -------------------------------------------------------------------------
    # Audit Fields
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<ExperienceHighlight {self.title}>"
        )