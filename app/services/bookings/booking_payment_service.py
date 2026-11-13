
"""
===============================================================================
The Uncharted Route
Booking Payment Service
===============================================================================
Business logic for booking payment transactions, refunds, receipts and balances.

This service records financial transactions. Payment gateway integrations are
implemented separately.
===============================================================================
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy import or_

from app.models import Booking, BookingPayment
from extensions import db


# =============================================================================
# Constants
# =============================================================================

TRANSACTION_TYPES = {
    "payment",
    "refund",
    "adjustment",
}

PAYMENT_STATUSES = {
    "pending",
    "processing",
    "succeeded",
    "failed",
    "cancelled",
}

PAYMENT_METHODS = {
    "mpesa",
    "card",
    "bank_transfer",
    "cash",
    "paypal",
    "other",
}

PAYMENT_PURPOSES = {
    "deposit",
    "balance",
    "full_payment",
    "addon",
    "other",
}

SUPPORTED_CURRENCIES = {
    "KES", "USD", "EUR", "GBP", "UGX",
    "TZS", "ZAR", "NGN", "GHS",
}

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


# =============================================================================
# Validation and persistence helpers
# =============================================================================

def _money(value, field_name="Amount"):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid monetary amount.")

    if not amount.is_finite():
        raise ValueError(f"{field_name} must be a finite number.")

    amount = amount.quantize(CENT, rounding=ROUND_HALF_UP)

    if amount <= ZERO:
        raise ValueError(f"{field_name} must be greater than zero.")

    return amount


def _optional_decimal(value, field_name):
    if value in (None, ""):
        return None

    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if not result.is_finite() or result <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return result


def _booking_or_raise(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        raise ValueError("Booking not found.")
    return booking


def _payment_or_raise(payment_id):
    payment = db.session.get(BookingPayment, payment_id)
    if payment is None:
        raise ValueError("Payment transaction not found.")
    return payment


def _commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def generate_payment_reference():
    """Generate a unique internal transaction reference."""
    return f"PAY-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:12].upper()}"


def _normalise_reference(value, generated=False):
    value = (value or "").strip()
    if not value and generated:
        value = generate_payment_reference()
    if not value:
        raise ValueError("Transaction reference is required.")
    return value


# =============================================================================
# Create transactions
# =============================================================================

def create_booking_payment(
    booking_id,
    amount,
    payment_method,
    currency="KES",
    transaction_type="payment",
    payment_purpose="balance",
    transaction_reference=None,
    idempotency_key=None,
    payment_provider=None,
    provider_transaction_id=None,
    provider_checkout_id=None,
    provider_reference=None,
    booking_currency=None,
    exchange_rate=None,
    booking_currency_amount=None,
    description=None,
    internal_notes=None,
    recorded_by_user_id=None,
    original_payment_id=None,
    commit=True,
):
    """
    Create a payment, refund, or adjustment transaction.

    Amounts are always positive. Refunds are separate records linked to their
    original successful payment. Idempotency keys prevent duplicate creation
    when a caller retries the same operation.
    """
    booking = _booking_or_raise(booking_id)

    transaction_type = (transaction_type or "").strip().lower()
    payment_method = (payment_method or "").strip().lower()
    payment_purpose = (payment_purpose or "").strip().lower()
    currency = (currency or "").strip().upper()
    booking_currency = (
        (booking_currency or getattr(booking, "currency", None) or currency)
        .strip()
        .upper()
    )

    if transaction_type not in TRANSACTION_TYPES:
        raise ValueError("Invalid transaction type.")

    if payment_method not in PAYMENT_METHODS:
        raise ValueError("Invalid payment method.")

    if payment_purpose not in PAYMENT_PURPOSES:
        raise ValueError("Invalid payment purpose.")

    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported payment currency.")

    if booking_currency not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported booking currency.")

    amount = _money(amount)

    if idempotency_key:
        idempotency_key = idempotency_key.strip()
        existing = BookingPayment.query.filter_by(
            idempotency_key=idempotency_key
        ).first()
        if existing:
            if existing.booking_id != booking.id:
                raise ValueError(
                    "This idempotency key belongs to a different booking."
                )
            return existing

    transaction_reference = _normalise_reference(
        transaction_reference,
        generated=True,
    )

    if BookingPayment.query.filter_by(
        transaction_reference=transaction_reference
    ).first():
        raise ValueError("Transaction reference already exists.")

    rate = _optional_decimal(exchange_rate, "Exchange rate")
    converted_amount = (
        _money(booking_currency_amount, "Booking currency amount")
        if booking_currency_amount not in (None, "")
        else None
    )

    if currency == booking_currency:
        rate = Decimal("1")
        converted_amount = amount

    if converted_amount is None and rate is not None:
        converted_amount = (amount * rate).quantize(
            CENT, rounding=ROUND_HALF_UP
        )

    if transaction_type == "refund":
        if not original_payment_id:
            raise ValueError("A refund must reference its original payment.")

        original = _payment_or_raise(original_payment_id)

        if original.booking_id != booking.id:
            raise ValueError("The original payment belongs to another booking.")

        if original.transaction_type != "payment":
            raise ValueError("Refunds must link to a payment transaction.")

        if original.status != "succeeded":
            raise ValueError("Only successful payments can be refunded.")

        if currency != original.currency:
            raise ValueError("Refund currency must match the original payment.")

        already_refunded = sum(
            (
                Decimal(str(item.amount))
                for item in original.refund_transactions
                if item.status == "succeeded"
            ),
            ZERO,
        )
        if already_refunded + amount > Decimal(str(original.amount)):
            raise ValueError("Refund exceeds the remaining refundable amount.")

        if payment_purpose == "balance":
            payment_purpose = original.payment_purpose

    payment = BookingPayment(
        booking_id=booking.id,
        transaction_reference=transaction_reference,
        idempotency_key=idempotency_key or None,
        transaction_type=transaction_type,
        status="pending",
        payment_method=payment_method,
        payment_provider=(payment_provider or "").strip() or None,
        amount=amount,
        currency=currency,
        booking_currency=booking_currency,
        exchange_rate=rate,
        booking_currency_amount=converted_amount,
        payment_purpose=payment_purpose,
        description=(description or "").strip() or None,
        provider_transaction_id=(provider_transaction_id or "").strip() or None,
        provider_checkout_id=(provider_checkout_id or "").strip() or None,
        provider_reference=(provider_reference or "").strip() or None,
        original_payment_id=original_payment_id,
        recorded_by_user_id=recorded_by_user_id,
        internal_notes=(internal_notes or "").strip() or None,
        initiated_at=datetime.utcnow(),
    )

    db.session.add(payment)

    if commit:
        _commit()
        return payment

    db.session.flush()
    return payment


def record_refund(
    original_payment_id,
    amount=None,
    payment_method=None,
    payment_provider=None,
    provider_reference=None,
    description=None,
    internal_notes=None,
    recorded_by_user_id=None,
    idempotency_key=None,
    commit=True,
):
    """Create a pending refund transaction linked to a successful payment."""
    original = _payment_or_raise(original_payment_id)

    if original.transaction_type != "payment":
        raise ValueError("The selected transaction is not a payment.")

    if original.status != "succeeded":
        raise ValueError("Only successful payments can be refunded.")

    refunded = sum(
        (
            Decimal(str(item.amount))
            for item in original.refund_transactions
            if item.status in {"pending", "processing", "succeeded"}
        ),
        ZERO,
    )

    refundable = Decimal(str(original.amount)) - refunded
    if refundable <= ZERO:
        raise ValueError("No refundable balance remains.")

    refund_amount = (
        refundable if amount in (None, "") else _money(amount, "Refund amount")
    )

    if refund_amount > refundable:
        raise ValueError("Refund amount exceeds the remaining refundable amount.")

    return create_booking_payment(
        booking_id=original.booking_id,
        amount=refund_amount,
        payment_method=payment_method or original.payment_method,
        currency=original.currency,
        transaction_type="refund",
        payment_purpose=original.payment_purpose,
        payment_provider=payment_provider or original.payment_provider,
        provider_reference=provider_reference,
        booking_currency=original.booking_currency or original.currency,
        exchange_rate=original.exchange_rate,
        booking_currency_amount=(
            (refund_amount * Decimal(str(original.exchange_rate))).quantize(CENT)
            if original.exchange_rate
            else refund_amount
        ),
        description=description or f"Refund for {original.transaction_reference}",
        internal_notes=internal_notes,
        recorded_by_user_id=recorded_by_user_id,
        original_payment_id=original.id,
        idempotency_key=idempotency_key,
        commit=commit,
    )


# =============================================================================
# Retrieval
# =============================================================================

def get_booking_payment(payment_id):
    return db.session.get(BookingPayment, payment_id)


def get_payment_by_reference(transaction_reference):
    if not transaction_reference:
        return None
    return BookingPayment.query.filter_by(
        transaction_reference=transaction_reference.strip()
    ).first()


def get_payment_by_transaction_reference(transaction_reference):
    return get_payment_by_reference(transaction_reference)


def get_payment_by_provider_reference(provider_reference):
    if not provider_reference:
        return None
    return BookingPayment.query.filter(
        or_(
            BookingPayment.provider_reference == provider_reference,
            BookingPayment.provider_transaction_id == provider_reference,
            BookingPayment.provider_checkout_id == provider_reference,
        )
    ).first()


def get_booking_payments(
    booking_id,
    successful_only=False,
    transaction_type=None,
    status=None,
    limit=None,
):
    query = BookingPayment.query.filter_by(booking_id=booking_id)

    if successful_only:
        query = query.filter_by(status="succeeded")

    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type.lower())

    if status:
        query = query.filter_by(status=status.lower())

    query = query.order_by(
        BookingPayment.initiated_at.desc(),
        BookingPayment.id.desc(),
    )

    if limit:
        query = query.limit(max(1, int(limit)))

    return query.all()


def get_successful_booking_payments(booking_id):
    return get_booking_payments(booking_id, successful_only=True)


# =============================================================================
# Status updates
# =============================================================================

def update_payment_status(
    payment_id,
    status,
    provider_transaction_id=None,
    provider_checkout_id=None,
    provider_reference=None,
    provider_response_code=None,
    provider_response_message=None,
    commit=True,
):
    payment = _payment_or_raise(payment_id)
    status = (status or "").strip().lower()

    if status not in PAYMENT_STATUSES:
        raise ValueError("Invalid payment status.")

    if payment.status == "succeeded" and status != "succeeded":
        raise ValueError(
            "A successful transaction cannot be changed back to an unsuccessful status."
        )

    payment.status = status

    if provider_transaction_id is not None:
        payment.provider_transaction_id = provider_transaction_id.strip() or None
    if provider_checkout_id is not None:
        payment.provider_checkout_id = provider_checkout_id.strip() or None
    if provider_reference is not None:
        payment.provider_reference = provider_reference.strip() or None
    if provider_response_code is not None:
        payment.provider_response_code = provider_response_code.strip() or None
    if provider_response_message is not None:
        payment.provider_response_message = provider_response_message

    now = datetime.utcnow()
    if status == "succeeded":
        payment.completed_at = payment.completed_at or now
    elif status == "failed":
        payment.failed_at = payment.failed_at or now

    if commit:
        _commit()
        synchronize_booking_payment_totals(payment.booking_id)

    return payment


def complete_payment(
    payment_id,
    provider_transaction_id=None,
    provider_checkout_id=None,
    provider_reference=None,
    provider_response_code=None,
    provider_response_message=None,
    receipt_number=None,
):
    payment = _payment_or_raise(payment_id)

    if payment.status == "succeeded":
        return payment

    if payment.status not in {"pending", "processing"}:
        raise ValueError("Only pending or processing transactions can succeed.")

    payment = update_payment_status(
        payment_id=payment_id,
        status="succeeded",
        provider_transaction_id=provider_transaction_id,
        provider_checkout_id=provider_checkout_id,
        provider_reference=provider_reference,
        provider_response_code=provider_response_code,
        provider_response_message=provider_response_message,
        commit=False,
    )

    if receipt_number is not None:
        payment.receipt_number = receipt_number.strip() or None

    _commit()
    synchronize_booking_payment_totals(payment.booking_id)
    return payment


def fail_payment(payment_id, response_code=None, response_message=None):
    return update_payment_status(
        payment_id,
        "failed",
        provider_response_code=response_code,
        provider_response_message=response_message,
    )


def cancel_payment(payment_id, response_message=None):
    payment = _payment_or_raise(payment_id)

    if payment.status not in {"pending", "processing"}:
        raise ValueError("Only pending or processing transactions can be cancelled.")

    return update_payment_status(
        payment_id,
        "cancelled",
        provider_response_message=response_message,
    )


# =============================================================================
# Financial totals
# =============================================================================

def calculate_booking_payment_total(booking_id):
    """
    Net successful funds received in booking currency.

    Successful payments and positive adjustments reduce the outstanding
    balance. Successful refunds increase it. Pending and failed transactions
    never affect the balance.
    """
    payments = get_booking_payments(booking_id, successful_only=True)

    net_received = ZERO
    for payment in payments:
        if not payment.affects_booking_balance:
            continue
        net_received -= Decimal(str(payment.balance_effect))

    return max(ZERO, net_received).quantize(CENT)


def calculate_booking_refund_total(booking_id):
    refunds = get_booking_payments(
        booking_id,
        successful_only=True,
        transaction_type="refund",
    )

    total = ZERO
    for refund in refunds:
        total += Decimal(str(
            refund.booking_currency_amount
            if refund.booking_currency_amount is not None
            else refund.amount
        ))

    return total.quantize(CENT)


def synchronize_booking_payment_totals(booking_id):
    booking = _booking_or_raise(booking_id)

    total_paid = calculate_booking_payment_total(booking_id)
    total_amount = Decimal(str(booking.total_amount or 0))
    balance_due = max(ZERO, total_amount - total_paid).quantize(CENT)

    # These fields are part of the central Booking financial snapshot.
    booking.amount_paid = total_paid
    booking.balance_due = balance_due

    _commit()
    return booking


def get_booking_payment_summary(booking_id):
    booking = _booking_or_raise(booking_id)
    total_amount = Decimal(str(booking.total_amount or 0)).quantize(CENT)
    total_paid = calculate_booking_payment_total(booking_id)
    total_refunded = calculate_booking_refund_total(booking_id)
    balance_due = max(ZERO, total_amount - total_paid).quantize(CENT)

    return {
        "booking_id": booking.id,
        "currency": getattr(booking, "currency", "KES"),
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_refunded": total_refunded,
        "balance_due": balance_due,
        "payment_complete": balance_due <= ZERO,
    }


def is_booking_fully_paid(booking_id):
    return get_booking_payment_summary(booking_id)["payment_complete"]


def get_outstanding_balance(booking_id):
    return get_booking_payment_summary(booking_id)["balance_due"]


# =============================================================================
# Receipt management
# =============================================================================
def assign_receipt_number(payment_id, receipt_number):
    payment = _payment_or_raise(payment_id)

    if payment.status != "succeeded":
        raise ValueError("Receipts can only be assigned to successful transactions.")

    receipt_number = (receipt_number or "").strip()
    if not receipt_number:
        raise ValueError("Receipt number is required.")

    existing = BookingPayment.query.filter(
        BookingPayment.receipt_number == receipt_number,
        BookingPayment.id != payment.id,
    ).first()
    if existing:
        raise ValueError("Receipt number is already assigned to another transaction.")

    payment.receipt_number = receipt_number
    _commit()
    return payment
