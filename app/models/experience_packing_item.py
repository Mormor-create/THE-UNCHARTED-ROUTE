"""
===============================================================================
The Uncharted Route
Experience Packing Item Model
===============================================================================

Stores recommended packing items for an experiences.

Examples

• Hat
• Sunscreen
• Camera
• Binoculars
• Sunglasses
• Light Jacket
• Hiking Boots
• Swimwear
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Packing Item Model
# =============================================================================

class ExperiencePackingItem(db.Model):
    """
    Represents a recommended packing item for an experiences.
    """

    __tablename__ = "experience_packing_items"

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
    # Packing Item Information
    # -------------------------------------------------------------------------

    name = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    category = db.Column(
        db.String(100),
        default="General"
    )
    # Examples:
    # Clothing
    # Equipment
    # Electronics
    # Documents
    # Health
    # Personal Items

    icon = db.Column(
        db.String(100),
        default="backpack"
    )

    recommended = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    required = db.Column(
        db.Boolean,
        default=False,
        nullable=False
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
        back_populates="packing_items"
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
            f"<ExperiencePackingItem {self.name}>"
        )