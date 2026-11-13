"""
===============================================================================
The Uncharted Route
Destination Journey Model
===============================================================================

Represents a multi-destination journey or travel package offered by
The Uncharted Route.

A DestinationJourney is the product definition.

The actual customer reservation is represented by Booking together with
DestinationBooking.
"""

from datetime import datetime

from extensions import db

class DestinationJourney(db.Model):
    """
    Sellable multi-destination journey/package.
    """
    __tablename__ = "destination_journeys"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Identity
    # =========================================================================
    name = db.Column(db.String(200),nullable=False,)
    slug = db.Column(db.String(220),unique=True,nullable=False,index=True,)
    short_description = db.Column(db.String(500),)
    description = db.Column(db.Text,)

    # =========================================================================
    # Journey Configuration
    # =========================================================================
    duration_days = db.Column(db.Integer,)
    duration_nights = db.Column(db.Integer,)
    journey_type = db.Column(db.String(50),)
    difficulty_level = db.Column( db.String(30),)

    # =========================================================================
    # Pricing
    # =========================================================================
    base_price = db.Column(db.Numeric(12, 2),)
    currency = db.Column(db.String(10),nullable=False,default="KES",)
    minimum_travellers = db.Column(db.Integer,)
    maximum_travellers = db.Column(db.Integer,)

    # =========================================================================
    # Booking Configuration
    # =========================================================================
    requires_approval = db.Column(db.Boolean,nullable=False,default=False,)

    # =========================================================================
    # Status
    # =========================================================================
    status = db.Column(db.String(30),nullable=False,default="draft",index=True,)
    is_featured = db.Column(db.Boolean,nullable=False,default=False,)
    is_bespoke = db.Column(db.Boolean,nullable=False,default=False,)

    # =========================================================================
    # SEO
    # =========================================================================
    meta_title = db.Column(db.String(255),)
    meta_description = db.Column(db.String(500),)

    # =========================================================================
    # Timestamps
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,)

    # =========================================================================
    # Relationships
    # =========================================================================
    bookings = db.relationship("DestinationBooking",back_populates="journey",lazy="dynamic",)
    stops = db.relationship("DestinationJourneyStop",back_populates="journey",cascade="all, delete-orphan",order_by="DestinationJourneyStop.sequence",)

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<DestinationJourney "f"id={self.id} "f"name='{self.name}'>")

class DestinationJourneyStop(db.Model):
    """
    A destination/stop contained within a DestinationJourney.
    """
    __tablename__ = "destination_journey_stops"

    id = db.Column(db.Integer,primary_key=True,)
    journey_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "destination_journeys.id",
            ondelete="CASCADE",),nullable=False,index=True,)
    destination_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "destinations.id",
            ondelete="SET NULL",),nullable=True,index=True,)
    sequence = db.Column(db.Integer,nullable=False,default=1,)
    days = db.Column(db.Integer,)
    nights = db.Column(db.Integer,)
    title = db.Column(db.String(200),)
    description = db.Column(db.Text,)
    arrival_notes = db.Column(db.Text,)
    departure_notes = db.Column(db.Text,)
    journey = db.relationship("DestinationJourney",back_populates="stops",)
    destination = db.relationship("Destination",)

    def __repr__(self):
        return (
            f"<DestinationJourneyStop "
            f"id={self.id} "
            f"journey_id={self.journey_id} "
            f"sequence={self.sequence}>")