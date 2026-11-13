"""
===============================================================================
The Uncharted Route
Experience Booking Detail
===============================================================================
Product-specific extension for a central Booking of type "experience".
Shared customer, lifecycle, payment, traveller and operations data belongs
to Booking, not this model.
Experience bookings are not tied to fixed schedules. The customer may request
a preferred experience date/time separately, and TUR confirms feasibility
manually.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from extensions import db

class ExperienceBooking(db.Model):
    """One-to-one experience-specific booking details."""

    __tablename__ = "experience_bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,unique=True,index=True,)

    # =========================================================================
    # Catalogue references
    # =========================================================================
    experience_id = db.Column(db.Integer,
        db.ForeignKey("experiences.id", ondelete="SET NULL"),
        nullable=True,index=True,)

    pricing_id = db.Column(db.Integer,
        db.ForeignKey("experience_pricing.id", ondelete="SET NULL"),
        nullable=True,index=True,)

    # =========================================================================
    # Historical product snapshots
    # =========================================================================
    experience_name_snapshot = db.Column(db.String(255),nullable=False,)
    experience_code_snapshot = db.Column(db.String(100),nullable=True,)
    description_snapshot = db.Column(db.Text,nullable=True,)
    meeting_point_snapshot = db.Column(db.String(255),nullable=True,)
    location_snapshot = db.Column(db.String(255),nullable=True,)
    duration_snapshot = db.Column(db.String(100),nullable=True,)

    # =========================================================================
    # Pricing snapshot
    # =========================================================================
    pricing_name_snapshot = db.Column(db.String(150),nullable=True,)
    price_basis = db.Column(db.String(40),nullable=False,default="per_person",)
    unit_price = db.Column(db.Numeric(12, 2),nullable=False,default=Decimal("0.00"),)
    quantity = db.Column(db.Integer,nullable=False,default=1,)
    currency = db.Column(db.String(3),nullable=False,default="KES",)

    # =========================================================================
    # Optional operational specifics
    # =========================================================================
    pickup_location = db.Column(db.String(255),nullable=True,)
    dropoff_location = db.Column(db.String(255),nullable=True,)
    customer_instructions = db.Column(db.Text,nullable=True,)

    # =========================================================================
    # Audit fields
    # =========================================================================
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)

    # =========================================================================
    # Relationships
    # =========================================================================
    booking = db.relationship("Booking",back_populates="experience_booking",)
    experience = db.relationship("Experience",back_populates="bookings",foreign_keys=[experience_id],)
    pricing = db.relationship("ExperiencePricing",back_populates="bookings",foreign_keys=[pricing_id],)

    # =========================================================================
    # Constraints
    # =========================================================================
    __table_args__ = (
        CheckConstraint("quantity >= 1",
            name="ck_experience_bookings_quantity_positive",),
        CheckConstraint("unit_price >= 0",
            name="ck_experience_bookings_unit_price_nonnegative",),)

    def __repr__(self):
        return (
            f"<ExperienceBooking id={self.id} "
            f"booking_id={self.booking_id} "
            f"experience_id={self.experience_id}>")