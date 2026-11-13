"""
===============================================================================
The Uncharted Route
Experience Itinerary Model
===============================================================================

Stores itinerary items for an experiences.

Each experiences can have multiple itinerary entries.

Examples

08:00 - Hotel Pickup
09:00 - Arrive at Nairobi National Park
09:15 - Morning Game Drive
12:00 - Picnic Breakfast
14:00 - Return to Hotel
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Itinerary Model
# =============================================================================

class ExperienceItinerary(db.Model):
    """
    Represents a single itinerary item belonging
    to an experiences.
    """

    __tablename__ = "experience_itineraries"

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
    # Itinerary Information
    # -------------------------------------------------------------------------

    day_number = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    activity_time = db.Column(
        db.String(50)
    )

    description = db.Column(
        db.Text,
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

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------

    experiences = db.relationship(
        "Experience",
        back_populates="itinerary"
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
            f"<ExperienceItinerary "
            f"Day {self.day_number}: {self.title}>"
        )