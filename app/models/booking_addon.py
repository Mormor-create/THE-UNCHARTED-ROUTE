"""
===============================================================================
The Uncharted Route
Booking Add-on Model
===============================================================================
Records add-ons purchased as part of a central booking.
The line item stores historical price and description snapshots. Catalogue
records remain separate, and the same add-on must not be charged twice for
the same booking.
"""

from datetime import datetime
from decimal import Decimal
from extensions import db

class BookingAddon(db.Model):
    """A purchased add-on associated with a central booking."""

    __tablename__ = "booking_addons"

    id = db.Column(db.Integer, primary_key=True)

    # Booking association
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional shared add-on catalogue reference.
    # This is intentionally a separate catalogue from ExperienceAddon.
    addon_code = db.Column(db.String(60), index=True)
    addon_type = db.Column(
        db.String(40), nullable=False, default="other", index=True
    )

    # Optional link to an existing experience-specific catalogue item.
    # Keep nullable because other service types may use other catalogues.
    experience_addon_id = db.Column(
        db.Integer,
        db.ForeignKey("experience_addons.id", ondelete="SET NULL"),
        index=True,
    )

    # Historical item snapshot
    name_snapshot = db.Column(db.String(255), nullable=False)
    description_snapshot = db.Column(db.Text)
    pricing_basis = db.Column(
        db.String(30), nullable=False, default="per_booking"
    )

    # Price snapshot
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(
        db.Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    currency = db.Column(db.String(10), nullable=False, default="KES")
    discount_amount = db.Column(
        db.Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    tax_amount = db.Column(
        db.Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    line_total = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    # Operational state
    status = db.Column(
        db.String(30), nullable=False, default="selected", index=True
    )
    fulfilled_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)

    # Prevent duplicate additions when a request is retried.
    idempotency_key = db.Column(db.String(150), unique=True, index=True)

    # Staff audit
    added_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    internal_notes = db.Column(db.Text)

    # Relationships
    booking = db.relationship(
        "Booking", back_populates="addons"
    )
    experience_addon = db.relationship("ExperienceAddon")
    added_by = db.relationship(
        "User", foreign_keys=[added_by_user_id]
    )

    addon_catalogue_id = db.Column(
        db.Integer,
        db.ForeignKey("addon_catalogue.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    addon_catalogue = db.relationship(
        "AddonCatalogue",
        foreign_keys=[addon_catalogue_id],
    )

    # Audit
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @property
    def calculated_line_total(self):
        """Calculate the line total without mutating the stored snapshot."""
        quantity = self.quantity or 0
        unit_price = Decimal(str(self.unit_price or 0))
        discount = Decimal(str(self.discount_amount or 0))
        tax = Decimal(str(self.tax_amount or 0))

        return (unit_price * quantity) - discount + tax

    def __repr__(self):
        return (
            f"<BookingAddon {self.name_snapshot!r} "
            f"booking_id={self.booking_id}>"
        )
