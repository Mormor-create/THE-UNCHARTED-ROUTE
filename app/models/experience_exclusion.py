
"""
===============================================================================
The Uncharted Route
Experience Exclusion Model
===============================================================================

Stores items NOT included in an experiences.

Examples

✗ Park Entry Fees
✗ International Flights
✗ Travel Insurance
✗ Personal Purchases
✗ Alcoholic Drinks
✗ Tips & Gratuities
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Exclusion Model
# =============================================================================

class ExperienceExclusion(db.Model):
    """
    Represents one exclusion for an experiences.
    """

    __tablename__ = "experience_exclusions"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experiences.id"),
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Exclusion Information
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
        default="x-circle"
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------

    experiences = db.relationship(
        "Experience",
        back_populates="exclusions"
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
        return f"<ExperienceExclusion {self.title}>"