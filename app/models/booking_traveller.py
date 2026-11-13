"""
===============================================================================
The Uncharted Route
Booking Traveller Model
===============================================================================
Stores individual traveller details for any central booking.
"""
from datetime import datetime
from extensions import db

class BookingTraveller(db.Model):
    """An individual traveller associated with a booking."""

    __tablename__ = "booking_travellers"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)

    # Optional traveller reference within the booking
    traveller_reference = db.Column(db.String(40), index=True)
    traveller_number = db.Column(db.Integer)

    # Traveller identity
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    traveller_type = db.Column(db.String(20), nullable=False, default="adult")
    nationality = db.Column(db.String(100))
    country_of_residence = db.Column(db.String(100))

    # Contact details, where applicable
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))

    # Emergency contact
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_relationship = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(50))
    emergency_contact_email = db.Column(db.String(255))

    # Operational requirements
    dietary_requirements = db.Column(db.Text)
    accessibility_requirements = db.Column(db.Text)
    medical_information = db.Column(db.Text)
    special_requirements = db.Column(db.Text)

    # Waiver / acknowledgement tracking
    waiver_required = db.Column(db.Boolean, nullable=False, default=False)
    waiver_status = db.Column(
        db.String(20), nullable=False, default="not_required")
    waiver_signed_at = db.Column(db.DateTime)
    waiver_document_id = db.Column(
        db.Integer,
        db.ForeignKey("booking_documents.id", ondelete="SET NULL"),)

    # Operational status
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    notes = db.Column(db.Text)

    # Relationships
    booking = db.relationship("Booking", back_populates="travellers")
    documents = db.relationship(
        "BookingDocument",
        back_populates="traveller",
        foreign_keys="BookingDocument.traveller_id",
        lazy="select",)

    waiver_document = db.relationship(
        "BookingDocument",
        foreign_keys=[waiver_document_id],
        post_update=True,)

    # Audit
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,)

    @property
    def full_name(self):
        return " ".join(
            part
            for part in (self.first_name, self.middle_name, self.last_name)
            if part).strip()

    def __repr__(self):
        return (
            f"<BookingTraveller {self.full_name!r} "
            f"booking_id={self.booking_id}>")