"""
===============================================================================
The Uncharted Route
Booking Request Model
===============================================================================
Stores booking requests and enquiries before, or independently of, a confirmed
booking. Supports website customers, staff submissions, and administrator
review across all supported booking types.
"""
from datetime import datetime
from extensions import db

class BookingRequest(db.Model):
    """A request that may eventually be converted into a central Booking."""
    __tablename__ = "booking_requests"
    # Identity
    id = db.Column(db.Integer, primary_key=True)
    request_reference = db.Column(
        db.String(40), unique=True, nullable=False, index=True
    )

    # Request classification
    service_type = db.Column(db.String(40), nullable=False, index=True)
    source = db.Column(db.String(30), nullable=False, default="website", index=True)
    status = db.Column(
        db.String(30), nullable=False, default="submitted", index=True
    )
    priority = db.Column(db.String(20), nullable=False, default="normal")

    # Customer / requester
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    contact_id = db.Column(
        db.Integer, db.ForeignKey("contacts.id", ondelete="SET NULL"), index=True
    )

    customer_first_name = db.Column(db.String(100), nullable=False)
    customer_last_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(255), nullable=False, index=True)
    customer_phone = db.Column(db.String(50))
    customer_country = db.Column(db.String(100))

    # Staff-submitted requests may identify the staff member who submitted them.
    submitted_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    # Requested service / product
    experience_id = db.Column(
        db.Integer, db.ForeignKey("experiences.id", ondelete="SET NULL")
    )
    safari_package_option_id = db.Column(
        db.Integer, db.ForeignKey("safari_package_options.id", ondelete="SET NULL")
    )
    stay_id = db.Column(
        db.Integer, db.ForeignKey("stays.id", ondelete="SET NULL")
    )
    destination_journey_id = db.Column(
        db.Integer, db.ForeignKey("destination_journeys.id", ondelete="SET NULL")
    )

    # Product and request snapshots
    requested_service_name = db.Column(db.String(255))
    requested_service_reference = db.Column(db.String(100))
    request_title = db.Column(db.String(255))
    request_message = db.Column(db.Text)

    # Requested dates and group details
    preferred_start_date = db.Column(db.Date)
    preferred_end_date = db.Column(db.Date)
    alternative_start_date = db.Column(db.Date)

    adults = db.Column(db.Integer, nullable=False, default=1)
    children = db.Column(db.Integer, nullable=False, default=0)
    infants = db.Column(db.Integer, nullable=False, default=0)
    seniors = db.Column(db.Integer, nullable=False, default=0)
    students = db.Column(db.Integer, nullable=False, default=0)

    # Budget / pricing indication. These do not constitute a confirmed quote.
    preferred_currency = db.Column(db.String(10), default="KES")
    budget_minimum = db.Column(db.Numeric(12, 2))
    budget_maximum = db.Column(db.Numeric(12, 2))

    # Flexible service-specific information
    request_details = db.Column(db.JSON)
    special_requirements = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    # Review workflow
    reviewed_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)

    information_requested_at = db.Column(db.DateTime)
    information_request_message = db.Column(db.Text)
    customer_response = db.Column(db.Text)
    customer_responded_at = db.Column(db.DateTime)

    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)

    # A request can be converted into at most one booking.
    # The corresponding Booking.source_request_id is the authoritative link.
    converted_booking = db.relationship(
        "Booking",
        back_populates="source_request",
        uselist=False,
        foreign_keys="Booking.source_request_id",
    )

    # Relationships
    customer = db.relationship(
        "User", foreign_keys=[user_id]
    )
    submitted_by = db.relationship(
        "User", foreign_keys=[submitted_by_user_id]
    )
    reviewed_by = db.relationship(
        "User", foreign_keys=[reviewed_by_user_id]
    )
    contact = db.relationship("Contact")

    experience = db.relationship("Experience")
    safari_package_option = db.relationship("SafariPackageOption")
    stay = db.relationship("Stay")
    destination_journey = db.relationship("DestinationJourney")

    # Audit
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    closed_at = db.Column(db.DateTime)

    @property
    def customer_name(self):
        """Return the requester's display name."""
        return " ".join(
            part for part in (self.customer_first_name, self.customer_last_name)
            if part
        ).strip()

    @property
    def total_travellers(self):
        """Return the total number of requested travellers."""
        return sum(
            value or 0
            for value in (
                self.adults,
                self.children,
                self.infants,
                self.seniors,
                self.students,
            )
        )

    @property
    def is_converted(self):
        return self.converted_booking is not None

    def __repr__(self):
        return (
            f"<BookingRequest {self.request_reference} "
            f"({self.status})>")