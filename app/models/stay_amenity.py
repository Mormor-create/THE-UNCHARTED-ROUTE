"""
===============================================================================
The Uncharted Route
Stay Amenity Model
===============================================================================

Represents an amenity or facility available at a Stay.

Amenities are stored as individual records so the public website can later
filter and search properties by facilities.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Stay Amenity Model
# =============================================================================

class StayAmenity(db.Model):
    """
    Represents an amenity belonging to a Stay.
    """

    __tablename__ = "stay_amenities"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Relationship
    # =========================================================================

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stays.id"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Amenity Information
    # =========================================================================

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.String(500)
    )

    category = db.Column(
        db.String(80),
        default="General"
    )

    # General
    # Dining
    # Wellness
    # Recreation
    # Connectivity
    # Transport
    # Family
    # Business
    # Accessibility
    # Room
    # Outdoor
    # Other

    icon = db.Column(
        db.String(100)
    )

    # =========================================================================
    # Status / Ordering
    # =========================================================================

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

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

    # =========================================================================
    # Relationship
    # =========================================================================

    stay = db.relationship(
        "Stay",
        back_populates="amenities"
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
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<StayAmenity "
            f"{self.name} - stay={self.stay_id}>"
        )