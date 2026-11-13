
"""
===============================================================================
The Uncharted Route
Booking Payment Model
===============================================================================

Records payment attempts, successful payments, refunds, and financial
adjustments associated with a central booking.

Amounts are stored as positive values. The transaction type determines how
each transaction affects the booking balance.
"""

from datetime import datetime
from decimal import Decimal
from extensions import db

class BookingPayment(db.Model):
    """An auditable payment or financial transaction for a booking."""

    __tablename__ = "booking_payments"

    id = db.Column(db.Integer, primary_key=True)

    # Booking association
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction identity
    transaction_reference = db.Column(
        db.String(100), unique=True, nullable=False, index=True
    )
    idempotency_key = db.Column(
        db.String(150), unique=True, index=True
    )

    # Transaction classification
    transaction_type = db.Column(
        db.String(30), nullable=False, default="payment", index=True
    )
    status = db.Column(
        db.String(30), nullable=False, default="pending", index=True
    )
    payment_method = db.Column(db.String(40), nullable=False)
    payment_provider = db.Column(db.String(60))

    # Financial values: amount is always positive.
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="KES")

    # Optional conversion information when payment and booking currencies differ.
    booking_currency = db.Column(db.String(10))
    exchange_rate = db.Column(db.Numeric(18, 8))
    booking_currency_amount = db.Column(db.Numeric(12, 2))

    # Allocation / purpose
    payment_purpose = db.Column(
        db.String(40), nullable=False, default="balance"
    )
    description = db.Column(db.String(255))

    # Provider references
    provider_transaction_id = db.Column(db.String(255), index=True)
    provider_checkout_id = db.Column(db.String(255), index=True)
    provider_reference = db.Column(db.String(255), index=True)
    provider_response_code = db.Column(db.String(100))
    provider_response_message = db.Column(db.Text)

    # Link a refund to the original successful payment.
    original_payment_id = db.Column(
        db.Integer,
        db.ForeignKey("booking_payments.id", ondelete="SET NULL"),
        index=True,
    )

    # Optional manual transaction audit
    recorded_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    internal_notes = db.Column(db.Text)

    # Receipt
    receipt_number = db.Column(db.String(100), index=True)
    receipt_storage_key = db.Column(db.String(500))

    # Timing
    initiated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    completed_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)

    # Relationships
    booking = db.relationship(
        "Booking", back_populates="payments"
    )

    original_payment = db.relationship(
        "BookingPayment",
        remote_side=[id],
        foreign_keys=[original_payment_id],
        back_populates="refund_transactions",
    )

    refund_transactions = db.relationship(
        "BookingPayment",
        foreign_keys=[original_payment_id],
        back_populates="original_payment",
        order_by="BookingPayment.created_at",
    )

    recorded_by = db.relationship(
        "User", foreign_keys=[recorded_by_user_id]
    )

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

    @property
    def is_successful(self):
        """Whether this transaction completed successfully."""
        return self.status == "succeeded"

    @property
    def is_refund(self):
        return self.transaction_type == "refund"

    @property
    def affects_booking_balance(self):
        """
        Whether this transaction should contribute to the booking balance.

        Only successful financial transactions count. Pending and failed
        attempts must never be counted as money received or refunded.
        """
        return (
            self.status == "succeeded"
            and self.transaction_type in {
                "payment",
                "refund",
                "adjustment",
            }
        )

    @property
    def balance_effect(self):
        """
        Signed balance effect in booking currency.

        Positive payments reduce the amount owed. Refunds increase it.
        Adjustments use their explicitly stored signed amount in a future
        adjustment-specific implementation; this property currently treats
        positive adjustments as credits received.
        """
        if not self.affects_booking_balance:
            return Decimal("0.00")

        value = self.booking_currency_amount
        if value is None:
            value = self.amount

        value = Decimal(str(value))

        if self.transaction_type == "refund":
            return value

        return -value

    def __repr__(self):
        return (
            f"<BookingPayment {self.transaction_reference} "
            f"{self.transaction_type}:{self.status}>"
        )
