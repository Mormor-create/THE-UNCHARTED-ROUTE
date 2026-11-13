"""
===============================================================================
The Uncharted Route
Stay Booking Detail
===============================================================================
Accommodation-specific details for a central Booking of type "stay".
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from extensions import db

class StayBooking(db.Model):
    """One-to-one accommodation-specific booking details."""
    __tablename__ = "stay_bookings"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id", ondelete="CASCADE"),nullable=False,unique=True,index=True,)

    # Catalogue references
    stay_id = db.Column(db.Integer,db.ForeignKey("stays.id", ondelete="SET NULL"),nullable=True,index=True,)
    room_id = db.Column(db.Integer,db.ForeignKey("stay_rooms.id", ondelete="SET NULL"),nullable=True,index=True,)

    # Historical accommodation snapshots
    stay_name_snapshot = db.Column(db.String(255),nullable=False,)
    property_location_snapshot = db.Column(db.String(255),nullable=True,)
    room_name_snapshot = db.Column(db.String(255),nullable=True,)
    room_description_snapshot = db.Column(db.Text,nullable=True,)
    meal_plan = db.Column(db.String(80),nullable=True,)
    meal_plan_snapshot = db.Column(db.String(150),nullable=True,)

    # Reservation dates
    check_in = db.Column(db.Date,nullable=False,index=True,)
    check_out = db.Column(db.Date,nullable=False,index=True,)
    nights = db.Column(db.Integer,nullable=False,default=1,)
    rooms_count = db.Column(db.Integer,nullable=False,default=1,)

    # Occupancy
    adults = db.Column(db.Integer,nullable=False,default=1,)
    children = db.Column(db.Integer,nullable=False,default=0,)
    infants = db.Column(db.Integer,nullable=False,default=0,)
    occupancy_snapshot = db.Column(db.JSON,nullable=True,)

    # Rate and price snapshots
    rate_name_snapshot = db.Column(db.String(150),nullable=True,)
    rate_basis = db.Column(db.String(50),nullable=False,default="per_room_per_night",)
    nightly_rate = db.Column(db.Numeric(12, 2),nullable=False,default=Decimal("0.00"),)
    currency = db.Column(db.String(3),nullable=False,default="KES",)

    # Guest preferences and operational requirements
    arrival_time = db.Column(db.String(30),nullable=True,)
    departure_time = db.Column(db.String(30),nullable=True,)
    special_requests = db.Column(db.Text,nullable=True,)
    accessibility_requirements = db.Column(db.Text,nullable=True,)

    # Optional reservation-specific inventory reference.
    # as a separate booking lifecycle.
    availability_reference = db.Column(db.String(100),nullable=True,)
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)
    booking = db.relationship("Booking",back_populates="stay_booking",)
    stay = db.relationship("Stay",foreign_keys=[stay_id],)
    room = db.relationship("StayRoom",foreign_keys=[room_id],)

    __table_args__ = (
        CheckConstraint(
            "nights >= 1 AND rooms_count >= 1",
            name="ck_stay_bookings_positive_nights_rooms",),
        CheckConstraint(
            "adults >= 0 AND children >= 0 AND infants >= 0",
            name="ck_stay_bookings_nonnegative_occupancy",),
        CheckConstraint(
            "nightly_rate >= 0",
            name="ck_stay_bookings_nonnegative_nightly_rate",),)

    def __repr__(self):
        return (
            f"<StayBooking id={self.id} "
            f"booking_id={self.booking_id} "
            f"stay={self.stay_name_snapshot!r}>")