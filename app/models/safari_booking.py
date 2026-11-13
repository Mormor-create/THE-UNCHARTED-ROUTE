"""
===============================================================================
The Uncharted Route
Safari Booking Detail
===============================================================================
Safari-specific details for a central Booking of type "safari".
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from extensions import db

class SafariBooking(db.Model):
    """One-to-one safari-specific booking details."""

    __tablename__ = "safari_bookings"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id", ondelete="CASCADE"),nullable=False,unique=True,index=True,)
    # Catalogue references
    safari_destination_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_destinations.id", ondelete="SET NULL"),nullable=True,index=True,)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_properties.id", ondelete="SET NULL"),nullable=True,index=True,)

    package_option_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_package_options.id", ondelete="SET NULL"),nullable=True,index=True,)

    package_rate_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_package_rates.id", ondelete="SET NULL"),nullable=True,index=True,)

    # Historical package snapshots
    package_name_snapshot = db.Column(db.String(255),nullable=False,)
    destination_name_snapshot = db.Column(db.String(255),nullable=True,)
    property_name_snapshot = db.Column(db.String(255),nullable=True,)
    package_description_snapshot = db.Column(db.Text,nullable=True,)
    itinerary_snapshot = db.Column(db.JSON,nullable=True,)
    inclusions_snapshot = db.Column(db.JSON,nullable=True,)
    exclusions_snapshot = db.Column(db.JSON,nullable=True,)

    # Travel dates
    start_date = db.Column(db.Date,nullable=False,index=True,)
    end_date = db.Column(db.Date,nullable=False,index=True,)
    duration_days = db.Column(db.Integer,nullable=False,default=1,)
    duration_nights = db.Column(db.Integer,nullable=False,default=0,)

    # Occupancy and rooming
    rooms_required = db.Column(db.Integer,nullable=False,default=1,)
    adults = db.Column(db.Integer,nullable=False,default=1,)
    children = db.Column(db.Integer,nullable=False,default=0,)
    infants = db.Column(db.Integer,nullable=False,default=0,)
    rooming_preferences = db.Column(db.Text,nullable=True,)

    # Rate snapshot
    rate_name_snapshot = db.Column(db.String(150),nullable=True,)
    rate_basis = db.Column(db.String(50),nullable=False,default="per_person_sharing",)
    unit_rate = db.Column(db.Numeric(12, 2),nullable=False,default=Decimal("0.00"),)
    quantity = db.Column(db.Integer,nullable=False,default=1,)
    currency = db.Column(db.String(3),nullable=False,default="USD",)

    # Safari-specific requests
    pickup_location = db.Column(db.String(255),nullable=True,)
    transfer_requirements = db.Column(db.Text,nullable=True,)
    wildlife_interests = db.Column(db.Text,nullable=True,)
    special_safari_requirements = db.Column(db.Text,nullable=True,)
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)
    booking = db.relationship("Booking",back_populates="safari_booking",)
    safari_destination = db.relationship("SafariDestination",foreign_keys=[safari_destination_id],)
    property = db.relationship("SafariProperty",foreign_keys=[property_id],)
    package_option = db.relationship("SafariPackageOption",foreign_keys=[package_option_id],)
    package_rate = db.relationship("SafariPackageRate",foreign_keys=[package_rate_id],)

    __table_args__ = (
        CheckConstraint(
            "duration_days >= 1 AND duration_nights >= 0",
            name="ck_safari_bookings_valid_duration",),
        CheckConstraint(
            "rooms_required >= 1 AND quantity >= 1",
            name="ck_safari_bookings_positive_quantities",),
        CheckConstraint(
            "adults >= 0 AND children >= 0 AND infants >= 0",
            name="ck_safari_bookings_nonnegative_occupancy",),
        CheckConstraint(
            "unit_rate >= 0",
            name="ck_safari_bookings_nonnegative_rate",),)

    def __repr__(self):
        return (
            f"<SafariBooking id={self.id} "
            f"booking_id={self.booking_id} "
            f"package={self.package_name_snapshot!r}>")