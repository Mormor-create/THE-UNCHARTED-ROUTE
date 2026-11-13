"""
===============================================================================
The Uncharted Route
Central Booking Model
===============================================================================
The central Booking record represents a customer's reservation across any of
the four supported service types:
    - experience
    - safari
    - stay
    - destination_journey
Product-specific information belongs to the corresponding one-to-one detail
model. This model owns shared customer information, lifecycle, financial
snapshots, provenance, and operational relationships.
Booking creation and staff allocation are independent operations.
"""
from datetime import datetime
from decimal import Decimal
from secrets import token_hex
from uuid import uuid4
from sqlalchemy import CheckConstraint, Index
from extensions import db
# =============================================================================
# Reference Generation
# =============================================================================
def generate_booking_reference():
    """
    Generate a customer-facing booking reference.
    Format:
        TUR-BKG-YYYYMMDD-XXXXXXXX
    The random suffix makes accidental collisions unlikely. The database's
    unique constraint remains the final protection against duplicate references.
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = token_hex(4).upper()
    return f"TUR-BKG-{date_part}-{random_part}"

# =============================================================================
# Booking
# =============================================================================
class Booking(db.Model):
    """Central reservation record shared by all service types."""
    __tablename__ = "bookings"
    SERVICE_TYPES = (
        "experience",
        "safari",
        "stay",
        "destination_journey",)

    SOURCES = (
        "website",
        "staff_request",
        "admin",
        "phone",
        "other",)

    STATUSES = (
        "pending",
        "awaiting_payment",
        "confirmed",
        "in_progress",
        "completed",
        "cancelled",
        "refunded",
        "archived",
    )

    PAYMENT_STATUSES = (
        "unpaid",
        "pending",
        "partially_paid",
        "paid",
        "partially_refunded",
        "refunded",
        "failed",
        "not_required",
    )

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    booking_reference = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True,
        default=generate_booking_reference,
    )

    booking_uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
        index=True,
    )

    booking_type = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    source = db.Column(
        db.String(30),
        nullable=False,
        default="website",
        index=True,
    )

    # -------------------------------------------------------------------------
    # Origin and creator
    # -------------------------------------------------------------------------

    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_request_id = db.Column(
        db.Integer,
        db.ForeignKey("booking_requests.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    created_by_user = db.relationship(
        "User",
        foreign_keys=[created_by_user_id],
        backref=db.backref("created_bookings", lazy="dynamic"),
    )

    source_request = db.relationship(
        "BookingRequest",
        foreign_keys=[source_request_id],
        back_populates="converted_booking",
        uselist=False,
    )

    # -------------------------------------------------------------------------
    # Customer account and CRM link
    # -------------------------------------------------------------------------

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    contact_id = db.Column(
        db.Integer,
        db.ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    customer = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref=db.backref("customer_bookings", lazy="dynamic"),
    )

    contact = db.relationship(
        "Contact",
        foreign_keys=[contact_id],
        backref=db.backref("booking", lazy="dynamic"),
    )

    # -------------------------------------------------------------------------
    # Lead traveller / customer snapshot
    # -------------------------------------------------------------------------

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        index=True,
    )

    phone = db.Column(
        db.String(50),
        nullable=True,
        index=True,
    )

    nationality = db.Column(
        db.String(100),
        nullable=True,
    )

    country_of_residence = db.Column(
        db.String(100),
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Group composition
    # -------------------------------------------------------------------------

    adults = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    children = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    infants = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    seniors = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    students = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    # -------------------------------------------------------------------------
    # Emergency contact
    # -------------------------------------------------------------------------

    emergency_contact_name = db.Column(
        db.String(150),
        nullable=True,
    )

    emergency_contact_phone = db.Column(
        db.String(50),
        nullable=True,
    )

    emergency_contact_relationship = db.Column(
        db.String(100),
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Requirements
    # -------------------------------------------------------------------------

    dietary_requirements = db.Column(
        db.Text,
        nullable=True,
    )

    medical_information = db.Column(
        db.Text,
        nullable=True,
    )

    accessibility_requirements = db.Column(
        db.Text,
        nullable=True,
    )

    special_requests = db.Column(
        db.Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Booking lifecycle
    # -------------------------------------------------------------------------

    status = db.Column(
        db.String(40),
        nullable=False,
        default="pending",
        index=True,
    )

    payment_status = db.Column(
        db.String(40),
        nullable=False,
        default="unpaid",
        index=True,
    )

    booking_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    experience_date = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    start_date = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    end_date = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    confirmed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    cancelled_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    cancellation_reason = db.Column(
        db.Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Financial snapshots
    # -------------------------------------------------------------------------

    currency = db.Column(
        db.String(3),
        nullable=False,
        default="KES",
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    discount_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    tax_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    addon_total = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    amount_paid = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    balance_due = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # -------------------------------------------------------------------------
    # Customer-facing and internal notes
    # -------------------------------------------------------------------------

    customer_notes = db.Column(
        db.Text,
        nullable=True,
    )

    internal_notes = db.Column(
        db.Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Communications and operational flags
    # -------------------------------------------------------------------------

    confirmation_sent = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    reminder_sent = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    reviewed = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Audit timestamps
    # -------------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # -------------------------------------------------------------------------
    # Service-specific one-to-one details
    # -------------------------------------------------------------------------

    experience_booking = db.relationship(
        "ExperienceBooking",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    safari_booking = db.relationship(
        "SafariBooking",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    stay_booking = db.relationship(
        "StayBooking",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    destination_booking = db.relationship(
        "DestinationBooking",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # -------------------------------------------------------------------------
    # Shared booking records
    # -------------------------------------------------------------------------

    travellers = db.relationship(
        "BookingTraveller",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BookingTraveller.id",
    )

    payments = db.relationship(
        "BookingPayment",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BookingPayment.created_at",
    )

    addons = db.relationship(
        "BookingAddon",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BookingAddon.created_at",
    )

    notes = db.relationship(
        "BookingNote",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BookingNote.created_at",
    )

    documents = db.relationship(
        "BookingDocument",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BookingDocument.created_at",
    )

    staff_assignments = db.relationship(
        "StaffAssignment",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StaffAssignment.created_at",
    )

    tasks = db.relationship(
        "Task",
        back_populates="booking",
        lazy="select",
    )

    reviews = db.relationship(
        "ExperienceReview",
        back_populates="booking",
        lazy="select",
    )

    # -------------------------------------------------------------------------
    # Database constraints and indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        CheckConstraint(
            "adults >= 0 AND children >= 0 AND infants >= 0 "
            "AND seniors >= 0 AND students >= 0",
            name="ck_bookings_nonnegative_group_counts",
        ),
        CheckConstraint(
            "subtotal >= 0 AND discount_amount >= 0 "
            "AND tax_amount >= 0 AND addon_total >= 0 "
            "AND total_amount >= 0",
            name="ck_bookings_nonnegative_financials",
        ),
        Index(
            "ix_bookings_type_status_date",
            "booking_type",
            "status",
            "start_date",
        ),
        Index(
            "ix_bookings_customer_dates",
            "email",
            "start_date",
            "end_date",
        ),
    )

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    @property
    def full_name(self):
        """Return the lead traveller's display name."""
        return " ".join(
            part.strip()
            for part in (self.first_name or "", self.last_name or "")
            if part and part.strip())

    @property
    def lead_traveller(self):
        """Compatibility alias for the lead customer's name."""
        return self.full_name

    @property
    def total_guests(self):
        """Return the total number of people in the booking group."""
        return sum(
            int(value or 0)
            for value in (
                self.adults,
                self.children,
                self.infants,
                self.seniors,
                self.students,))

    @property
    def total_paid(self):
        """
        Sum balance-affecting payment transactions.
        Fall back to the stored amount_paid snapshot when no qualifying
        transaction records are available.
        """
        successful = [
            payment
            for payment in self.payments
            if getattr(payment, "affects_booking_balance", False)]
        if not successful:
            return Decimal(str(self.amount_paid or 0))
        return sum(
            (
                Decimal(
                    str(getattr(payment, "balance_effect", 0) or 0)
                )
                for payment in successful
            ),Decimal("0.00"),)

    @property
    def amount_remaining(self):
        """Return the remaining amount owed, never below zero."""

        total = Decimal(str(self.total_amount or 0))
        paid = Decimal(str(self.total_paid or 0))

        return max(total - paid, Decimal("0.00"))

    @property
    def outstanding_balance(self):
        """Compatibility alias for the calculated remaining balance."""

        return self.amount_remaining

    @property
    def is_paid(self):
        """Whether the current amount due has been covered."""

        return self.amount_remaining <= Decimal("0.00")

    @property
    def payment_complete(self):
        """Compatibility alias for is_paid."""

        return self.is_paid

    @property
    def successful_payment_count(self):
        """Count successful payments, excluding refunds and reversals."""

        return sum(
            1
            for payment in self.payments
            if str(getattr(payment, "status", "")).lower()
            in {"succeeded", "successful", "completed"}
            and str(
                getattr(payment, "transaction_type", "payment")
            ).lower()
            not in {"refund", "reversal"}
        )

    @property
    def addons_total(self):
        """Calculate the total value of active add-on snapshots."""

        return sum(
            (
                Decimal(str(getattr(addon, "line_total", 0) or 0))
                for addon in self.addons
                if getattr(addon, "active", True)
            ),
            Decimal("0.00"),)

    @property
    def service_detail(self):
        """Return the detail record matching this booking's service type."""

        details = {
            "experience": self.experience_booking,
            "safari": self.safari_booking,
            "stay": self.stay_booking,
            "destination_journey": self.destination_booking,}
        return details.get(self.booking_type)

    @property
    def service_name(self):
        """Return a human-readable product name where available."""
        detail = self.service_detail
        if detail is None:
            return self.booking_type.replace("_", " ").title()
        for field in (
            "experience_name_snapshot",
            "package_name_snapshot",
            "stay_name_snapshot",
            "journey_name_snapshot",
            "name_snapshot",
            "title_snapshot",
        ):
            value = getattr(detail, field, None)

            if value:
                return value

        for relation_name in (
            "experience",
            "package",
            "stay",
            "journey",):
            related = getattr(detail, relation_name, None)

            if related is not None:
                return (
                    getattr(related, "title", None)
                    or getattr(related, "name", None)
                    or getattr(related, "package_name", None))

        return self.booking_type.replace("_", " ").title()

    def __repr__(self):
        return (
            f"<Booking {self.booking_reference!r} "
            f"type={self.booking_type!r} status={self.status!r}>")