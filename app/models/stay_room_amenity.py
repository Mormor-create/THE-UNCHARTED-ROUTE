"""
===============================================================================
The Uncharted Route
Stay Room Amenity Model
===============================================================================

Represents an amenity belonging specifically to an accommodation room type.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Stay Room Amenity Model
# =============================================================================

class StayRoomAmenity(db.Model):
    """
    Represents an amenity belonging to a StayRoom.
    """

    __tablename__ = "stay_room_amenities"

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

    room_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stay_rooms.id"
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
        default="Room"
    )

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

    room = db.relationship(
        "StayRoom",
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
            f"<StayRoomAmenity "
            f"{self.name} - room={self.room_id}>"
        )