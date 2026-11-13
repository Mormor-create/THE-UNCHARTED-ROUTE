"""
===============================================================================
The Uncharted Route
Experience Inclusion Model
===============================================================================

Stores items included in an experiences.

Examples

✓ Professional Driver Guide
✓ Bottled Drinking Water
✓ Hotel Pickup & Drop-off
✓ Luxury Safari Vehicle
✓ Picnic Breakfast
✓ Park Transfers
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Inclusion Model
# =============================================================================

class ExperienceInclusion(db.Model):
    """
    Represents one inclusion for an experiences.
    """

    __tablename__ = "experience_inclusions"

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
    # Inclusion Information
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
        default="check-circle"
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
        back_populates="inclusions"
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
            f"<ExperienceInclusion {self.title}>"
        )