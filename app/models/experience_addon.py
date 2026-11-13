"""
===============================================================================
The Uncharted Route
Experience Add-on Model
===============================================================================

Stores optional extras that customers can purchase when booking
an experiences.

Examples

• Professional Photographer
• Bush Breakfast
• Luxury Land Cruiser Upgrade
• Airport Transfers
• Helicopter Transfer
• Champagne Picnic
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Add-on Model
# =============================================================================

class ExperienceAddon(db.Model):
    """
    Represents an optional add-on available for an experiences.
    """

    __tablename__ = "experience_addons"

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
    # Basic Information
    # -------------------------------------------------------------------------

    name = db.Column(
        db.String(255),
        nullable=False
    )

    short_description = db.Column(
        db.String(255)
    )

    description = db.Column(
        db.Text
    )

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    price = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="KES"
    )

    pricing_type = db.Column(
        db.String(50),
        nullable=False,
        default="Per Person"
    )
    # Per Person
    # Per Booking
    # Per Vehicle
    # Per Group

    # -------------------------------------------------------------------------
    # Booking Behaviour
    # -------------------------------------------------------------------------

    optional = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    available_online = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    display_order = db.Column(
        db.Integer,
        default=0
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
        back_populates="addons"
    )

    booking_addons = db.relationship(
        "BookingAddon",
        back_populates="experience_addon",
        lazy="dynamic"
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
    # Helper Properties
    # -------------------------------------------------------------------------

    @property
    def formatted_price(self):
        return f"{self.currency} {self.price:,.0f}"

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<ExperienceAddon {self.name}>"
        )