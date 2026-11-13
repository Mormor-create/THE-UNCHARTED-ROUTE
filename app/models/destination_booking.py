"""
===============================================================================
The Uncharted Route
Destination Journey Booking Detail
===============================================================================
Reservation-specific details for a central Booking of type
"destination_journey".
DestinationJourney and DestinationJourneyStop remain catalogue models.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from extensions import db

class DestinationBooking(db.Model):
    """One-to-one extension for a multi-destination journey reservation."""

    __tablename__ = "destination_bookings"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,unique=True,index=True,)

    journey_id = db.Column(db.Integer,
        db.ForeignKey("destination_journeys.id", ondelete="SET NULL"),
        nullable=True,index=True,)

    # Historical journey snapshots
    journey_name_snapshot = db.Column(db.String(255),nullable=False,)
    journey_slug_snapshot = db.Column(db.String(255),nullable=True,)
    journey_description_snapshot = db.Column(db.Text,nullable=True,)
    itinerary_snapshot = db.Column(db.JSON,nullable=True,)
    inclusions_snapshot = db.Column(db.JSON,nullable=True,)
    exclusions_snapshot = db.Column(db.JSON,nullable=True,)

    # Dates chosen by the customer
    start_date = db.Column(db.Date,nullable=False,index=True,)
    end_date = db.Column(db.Date,nullable=False,index=True,)
    duration_days = db.Column(db.Integer,nullable=False,default=1,)
    duration_nights = db.Column(db.Integer,nullable=False,default=0,)

    # Journey-specific group and preferences
    travellers_count = db.Column(db.Integer,nullable=False,default=1,)
    rooming_preferences = db.Column(db.Text,nullable=True,)
    transport_preferences = db.Column(db.Text,nullable=True,)
    preferred_stops = db.Column(db.JSON,nullable=True,)
    bespoke_requirements = db.Column(db.Text,nullable=True,)

    # Price snapshot
    pricing_basis = db.Column(db.String(50),nullable=False,default="per_person",)
    unit_price = db.Column(db.Numeric(12, 2),nullable=False,default=Decimal("0.00"),)
    currency = db.Column(db.String(3),nullable=False,default="KES",)

    # Whether this reservation uses an agreed bespoke itinerary.
    bespoke = db.Column(db.Boolean,nullable=False,default=False,)
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)
    booking = db.relationship("Booking",back_populates="destination_booking",)
    journey = db.relationship("DestinationJourney",foreign_keys=[journey_id],)

    __table_args__ = (
        CheckConstraint(
            "duration_days >= 1 AND duration_nights >= 0",
            name="ck_destination_bookings_valid_duration",),
        CheckConstraint(
            "travellers_count >= 1",
            name="ck_destination_bookings_positive_travellers",),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_destination_bookings_nonnegative_price",),)

    def __repr__(self):
        return (
            f"<DestinationBooking id={self.id} "
            f"booking_id={self.booking_id} "
            f"journey={self.journey_name_snapshot!r}>")