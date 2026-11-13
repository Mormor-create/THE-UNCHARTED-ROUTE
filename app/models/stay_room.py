"""
===============================================================================
The Uncharted Route
Stay Room Model
===============================================================================

Represents a bookable room, suite, villa, tent, cottage, or other
accommodation unit/type belonging to a Stay.

A Stay may contain multiple room types.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Stay Room Model
# =============================================================================
class StayRoom(db.Model):
    """
    Represents an accommodation room type.
    """

    __tablename__ = "stay_rooms"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # =========================================================================
    # Identity
    # =========================================================================

    room_code = db.Column(
        db.String(40),
        unique=True,
        nullable=False,
        index=True,
    )

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey("stays.id"),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
    )

    slug = db.Column(
        db.String(220),
        nullable=False,
        index=True,
    )

    room_type = db.Column(
        db.String(80),
        nullable=False,
        default="Standard Room",
    )

    # =========================================================================
    # Description
    # =========================================================================

    short_description = db.Column(
        db.String(350),
    )

    description = db.Column(
        db.Text,
    )

    # =========================================================================
    # Occupancy
    # =========================================================================

    maximum_guests = db.Column(
        db.Integer,
        nullable=False,
        default=2,
    )

    maximum_adults = db.Column(
        db.Integer,
        default=2,
    )

    # Most rooms can accommodate children by default.
    # Set this to 0 for rooms that do not accept children.

    maximum_children = db.Column(
        db.Integer,
        default=2,
    )

    minimum_guests = db.Column(
        db.Integer,
        default=1,
    )

    # =========================================================================
    # Inventory
    # =========================================================================

    total_units = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    # =========================================================================
    # Pricing
    # =========================================================================

    nightly_rate = db.Column(
        db.Float,
        nullable=False,
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="KES",
    )

    meal_plan = db.Column(
        db.String(50),
        nullable=False,
        default="Bed & Breakfast",
    )

    # Supported meal plans:
    #
    # Room Only
    # Bed & Breakfast
    # Half Board
    # Full Board
    # All Inclusive
    # Custom

    # =========================================================================
    # Room Features
    # =========================================================================

    bed_configuration = db.Column(
        db.String(150),
    )

    floor = db.Column(
        db.String(50),
    )

    size_description = db.Column(
        db.String(100),
    )

    # =========================================================================
    # Availability
    # =========================================================================

    availability_status = db.Column(
        db.String(30),
        nullable=False,
        default="Available",
    )

    # Supported statuses:
    #
    # Available
    # Limited
    # Closed
    # On Request

    # =========================================================================
    # Status
    # =========================================================================

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    # =========================================================================
    # Media Library
    # =========================================================================
    #
    # This stores the Media Library folder assigned specifically to this room.
    #
    # Example:
    #
    #     Stays Rooms
    #       └── Fairmont Mount Kenya Safari Club
    #           └── Manor Junior Suites
    #
    # Room media is managed from this folder.
    #
    # =========================================================================

    media_folder_id = db.Column(
        db.Integer,
        db.ForeignKey("media_folders.id"),
        nullable=True,
        index=True,
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    stay = db.relationship(
        "Stay",
        back_populates="rooms",
    )

    media_folder = db.relationship(
        "MediaFolder",
        foreign_keys=[media_folder_id],
    )

    # =========================================================================
    # Bookings
    # =========================================================================

    bookings = db.relationship(
        "StayBooking",
        back_populates="room",
        lazy="dynamic",
    )

    media = db.relationship(
        "StayRoomMedia",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayRoomMedia.display_order",
    )

    amenities = db.relationship(
        "StayRoomAmenity",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayRoomAmenity.display_order",
    )

    # =========================================================================
    # Audit Fields
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # =========================================================================
    # Helper Properties
    # =========================================================================

    @property
    def formatted_rate(self):
        return (
            f"{self.currency} "
            f"{self.nightly_rate:,.0f}"
        )

    @property
    def media_count(self):
        return self.media.count()

    @property
    def amenity_count(self):
        return self.amenities.count()

    @property
    def hero_media(self):
        return self.media.filter_by(
            usage="hero",
            active=True,
        ).first()

    @property
    def gallery_media(self):
        return (
            self.media
            .filter_by(
                usage="gallery",
                active=True,
            )
            .order_by(
                "StayRoomMedia.display_order"
            )
            .all()
        )

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<StayRoom "
            f"{self.room_code} - {self.name}>"
        )