"""
===============================================================================
The Uncharted Route
Central Booking Service
===============================================================================

Coordinates central booking for experiences, safaris, stays, and destination
journeys.

The Booking model owns shared customer details, lifecycle, and financial
snapshots. Product-specific details belong to the corresponding one-to-one
booking detail model.

Experience schedules are no longer part of the booking architecture.
Customers may request preferred dates/times, while TUR handles feasibility
and confirmation separately.
===============================================================================
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.models import Booking

# =============================================================================
# Constants
# =============================================================================
SUPPORTED_BOOKING_TYPES = set(Booking.SERVICE_TYPES)
SUPPORTED_BOOKING_SOURCES = set(Booking.SOURCES)
BOOKING_STATUSES = set(Booking.STATUSES)
PAYMENT_STATUSES = set(Booking.PAYMENT_STATUSES)
MONEY_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")
TERMINAL_BOOKING_STATUSES = {
    "completed",
    "cancelled",
    "refunded",
    "archived",}
ALLOWED_STATUS_TRANSITIONS = {
    "pending": {
        "awaiting_payment",
        "confirmed",
        "cancelled",
        "archived",
    },
    "awaiting_payment": {
        "pending",
        "confirmed",
        "cancelled",
        "refunded",
        "archived",
    },
    "confirmed": {
        "in_progress",
        "completed",
        "cancelled",
        "refunded",
        "archived",
    },
    "in_progress": {
        "completed",
        "cancelled",
        "archived",
    },
    "completed": {
        "refunded",
        "archived",
    },
    "cancelled": {
        "refunded",
        "archived",
    },
    "refunded": {
        "archived",
    },
    "archived": set(),
}

# =============================================================================
# Exceptions
# =============================================================================
class BookingServiceError(Exception):
    """Base exception for booking service errors."""

class BookingValidationError(BookingServiceError):
    """Raised when booking data is invalid."""

class BookingNotFoundError(BookingServiceError):
    """Raised when a booking cannot be found."""

class BookingTransitionError(BookingServiceError):
    """Raised when a lifecycle transition is not permitted."""

class BookingAvailabilityError(BookingServiceError):
    """Raised when requested inventory is unavailable."""

# =============================================================================
# General helpers
# =============================================================================
def _money(value, field_name="amount"):
    """
    Convert a value to a non-negative, two-decimal Decimal.
    """

    try:
        amount = Decimal(
            str(
                value
                if value is not None
                else 0
            )
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"must be a valid amount."
        )

    if not amount.is_finite():
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"must be finite."
        )

    if amount < ZERO:
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"cannot be negative."
        )

    return amount.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def _count(
    value,
    field_name,
    default=0,
):
    """
    Validate a non-negative integer guest or quantity count.
    """

    if value is None:
        value = default

    try:
        number = int(value)

    except (
        TypeError,
        ValueError,
    ):
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"must be a whole number."
        )

    if (
        isinstance(value, bool)
        or str(value).strip() != str(number)
    ):
        if not isinstance(value, int):
            raise BookingValidationError(
                f"{field_name.replace('_', ' ').title()} "
                f"must be a whole number."
            )

    if number < 0:
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"cannot be negative."
        )

    return number


def _required_text(
    data,
    key,
    label=None,
):
    """
    Read and validate a required text field.
    """

    value = data.get(key)

    if value is None or not str(value).strip():
        raise BookingValidationError(
            f"{label or key.replace('_', ' ').title()} "
            f"is required."
        )

    return str(value).strip()


def _optional_text(
    data,
    key,
):
    """
    Read an optional text field without converting None to 'None'.
    """

    value = data.get(key)

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _as_date(
    value,
    field_name,
):
    """
    Accept a date or ISO-format date string.
    """

    if value in (
        None,
        "",
    ):
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError,
    ):
        raise BookingValidationError(
            f"{field_name.replace('_', ' ').title()} "
            f"must be a valid date."
        )


def _validate_dates(
    start_date=None,
    end_date=None,
):
    """
    Validate an optional booking date range.
    """

    start = _as_date(
        start_date,
        "start_date",
    )

    end = _as_date(
        end_date,
        "end_date",
    )

    if (
        start
        and end
        and end < start
    ):
        raise BookingValidationError(
            "The end date cannot be earlier than the start date."
        )

    return start, end


def _validate_currency(currency):
    """
    Validate the ISO-style three-character currency code.
    """

    currency = str(
        currency or "KES"
    ).strip().upper()

    if (
        len(currency) != 3
        or not currency.isalpha()
    ):
        raise BookingValidationError(
            "Currency must be a three-letter currency code."
        )

    return currency


def _validate_booking_type(
    booking_type,
):
    """
    Validate the requested service type.
    """

    booking_type = str(
        booking_type or ""
    ).strip().lower()

    if booking_type not in SUPPORTED_BOOKING_TYPES:
        supported = ", ".join(
            sorted(SUPPORTED_BOOKING_TYPES)
        )

        raise BookingValidationError(
            "Unsupported booking type. "
            f"Supported types: {supported}."
        )

    return booking_type


def _validate_source(source):
    """
    Validate booking provenance.
    """

    source = str(
        source or "website"
    ).strip().lower()

    if source not in SUPPORTED_BOOKING_SOURCES:
        supported = ", ".join(
            sorted(SUPPORTED_BOOKING_SOURCES)
        )

        raise BookingValidationError(
            "Unsupported booking source. "
            f"Supported sources: {supported}."
        )

    return source


def _guest_counts(data):
    """
    Return validated guest counts using the actual Booking columns.
    """

    counts = {
        "adults": _count(
            data.get("adults"),
            "adults",
            default=1,
        ),
        "children": _count(
            data.get("children"),
            "children",
        ),
        "infants": _count(
            data.get("infants"),
            "infants",
        ),
        "seniors": _count(
            data.get("seniors"),
            "seniors",
        ),
        "students": _count(
            data.get("students"),
            "students",
        ),
    }

    if sum(counts.values()) < 1:
        raise BookingValidationError(
            "A booking must include at least one guest."
        )

    return counts


def _calculate_total(
    subtotal,
    discount_amount=ZERO,
    tax_amount=ZERO,
    addon_total=ZERO,
):
    """
    Calculate the total from central financial snapshots.
    """

    subtotal = _money(
        subtotal,
        "subtotal",
    )

    discount_amount = _money(
        discount_amount,
        "discount_amount",
    )

    tax_amount = _money(
        tax_amount,
        "tax_amount",
    )

    addon_total = _money(
        addon_total,
        "addon_total",
    )

    if discount_amount > subtotal:
        raise BookingValidationError(
            "The discount cannot exceed the booking subtotal."
        )

    total = (
        subtotal
        - discount_amount
        + tax_amount
        + addon_total
    )

    if total < ZERO:
        raise BookingValidationError(
            "The calculated booking total cannot be negative."
        )

    return total.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def _refresh_financial_snapshots(
    booking,
):
    """
    Keep amount_paid, balance_due, and payment_status consistent.
    """

    total = _money(
        booking.total_amount,
        "total_amount",
    )

    paid = _money(
        booking.total_paid,
        "amount_paid",
    )

    booking.amount_paid = paid

    booking.balance_due = max(
        total - paid,
        ZERO,
    )

    if total == ZERO:

        booking.payment_status = (
            "not_required"
        )

    elif paid >= total:

        booking.payment_status = "paid"

    elif paid > ZERO:

        booking.payment_status = (
            "partially_paid"
        )

    elif booking.payment_status not in {
        "pending",
        "failed",
    }:

        booking.payment_status = "unpaid"


def _coerce_booking(
    booking_or_id,
):
    """
    Accept either a Booking instance or a database ID.
    """

    if isinstance(
        booking_or_id,
        Booking,
    ):
        return booking_or_id

    return get_booking(
        booking_or_id
    )


# =============================================================================
# Booking lookups
# =============================================================================

def get_booking(
    booking_id,
):
    """
    Retrieve a booking by database ID.
    """

    booking = db.session.get(
        Booking,
        booking_id,
    )

    if booking is None:
        raise BookingNotFoundError(
            "Booking not found."
        )

    return booking


def get_booking_by_reference(
    reference,
):
    """
    Retrieve a booking by its customer-facing reference.

    Returns None when no matching booking exists so that public routes can
    handle a missing booking cleanly.
    """

    reference = str(
        reference or ""
    ).strip()

    if not reference:
        return None

    return (
        Booking.query
        .filter_by(
            booking_reference=reference
        )
        .first()
    )


def get_booking_by_uuid(
    booking_uuid,
):
    """
    Retrieve a booking by its UUID.

    The Booking model is expected to expose the UUID through the
    `booking_uuid` column.
    """

    booking_uuid = str(
        booking_uuid or ""
    ).strip()

    if not booking_uuid:
        return None

    return (
        Booking.query
        .filter_by(
            booking_uuid=booking_uuid
        )
        .first()
    )


def list_bookings(
    booking_type=None,
    status=None,
    payment_status=None,
    source=None,
    email=None,
    active=None,
    start_date=None,
    end_date=None,
    page=None,
    per_page=20,
):
    """
    List bookings with optional filters.
    """

    query = Booking.query

    if booking_type:

        query = query.filter_by(
            booking_type=_validate_booking_type(
                booking_type
            )
        )

    if status:

        status = str(
            status
        ).strip().lower()

        if status not in BOOKING_STATUSES:
            raise BookingValidationError(
                "Invalid booking status."
            )

        query = query.filter_by(
            status=status
        )

    if payment_status:

        payment_status = str(
            payment_status
        ).strip().lower()

        if payment_status not in PAYMENT_STATUSES:
            raise BookingValidationError(
                "Invalid payment status."
            )

        query = query.filter_by(
            payment_status=payment_status
        )

    if source:

        query = query.filter_by(
            source=_validate_source(
                source
            )
        )

    if email:

        query = query.filter(
            db.func.lower(
                Booking.email
            )
            == str(email).strip().lower()
        )

    if active is not None:

        query = query.filter_by(
            active=bool(active)
        )

    start = _as_date(
        start_date,
        "start_date",
    )

    end = _as_date(
        end_date,
        "end_date",
    )

    if (
        start
        and end
        and end < start
    ):
        raise BookingValidationError(
            "The filter end date cannot be earlier than the start date."
        )

    if start:

        query = query.filter(
            db.func.coalesce(
                Booking.start_date,
                Booking.experience_date,
            ) >= start
        )

    if end:

        query = query.filter(
            db.func.coalesce(
                Booking.end_date,
                Booking.experience_date,
            ) <= end
        )

    query = query.order_by(
        Booking.created_at.desc(),
        Booking.id.desc(),
    )

    if page is not None:

        try:
            page = max(
                int(page),
                1,
            )

            per_page = min(
                max(
                    int(per_page),
                    1,
                ),
                100,
            )

        except (
            TypeError,
            ValueError,
        ):
            raise BookingValidationError(
                "Invalid pagination values."
            )

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    return query.all()


# =============================================================================
# Central booking creation
# =============================================================================

def _build_central_booking(
    data,
    booking_type,
    source="website",
):
    """
    Construct the shared Booking record.

    Only fields present on the supplied Booking model are populated here.
    Product-specific fields belong to the detail model.
    """

    if not isinstance(
        data,
        dict,
    ):
        data = dict(data)

    booking_type = _validate_booking_type(
        booking_type
    )

    source = _validate_source(
        source
    )

    start_date, end_date = _validate_dates(
        data.get("start_date"),
        data.get("end_date"),
    )

    experience_date = _as_date(
        data.get("experience_date"),
        "experience_date",
    )

    currency = _validate_currency(
        data.get(
            "currency",
            "KES",
        )
    )

    guests = _guest_counts(
        data
    )

    subtotal = _money(
        data.get(
            "subtotal",
            0,
        ),
        "subtotal",
    )

    discount = _money(
        data.get(
            "discount_amount",
            0,
        ),
        "discount_amount",
    )

    tax = _money(
        data.get(
            "tax_amount",
            0,
        ),
        "tax_amount",
    )

    addon_total = _money(
        data.get(
            "addon_total",
            0,
        ),
        "addon_total",
    )

    total = _calculate_total(
        subtotal,
        discount,
        tax,
        addon_total,
    )

    supplied_status = str(
        data.get("status")
        or "pending"
    ).strip().lower()

    if supplied_status not in BOOKING_STATUSES:
        raise BookingValidationError(
            "Invalid booking status."
        )

    supplied_payment_status = str(
        data.get("payment_status")
        or "unpaid"
    ).strip().lower()

    if supplied_payment_status not in PAYMENT_STATUSES:
        raise BookingValidationError(
            "Invalid payment status."
        )

    booking = Booking(
        booking_type=booking_type,
        source=source,

        created_by_user_id=data.get(
            "created_by_user_id"
        ),
        source_request_id=data.get(
            "source_request_id"
        ),
        user_id=data.get(
            "user_id"
        ),
        contact_id=data.get(
            "contact_id"
        ),

        first_name=_required_text(
            data,
            "first_name",
        ),
        last_name=_required_text(
            data,
            "last_name",
        ),
        email=_required_text(
            data,
            "email",
        ).lower(),

        phone=_optional_text(
            data,
            "phone",
        ),

        nationality=_optional_text(
            data,
            "nationality",
        ),

        country_of_residence=_optional_text(
            data,
            "country_of_residence",
        ),

        adults=guests["adults"],
        children=guests["children"],
        infants=guests["infants"],
        seniors=guests["seniors"],
        students=guests["students"],

        emergency_contact_name=_optional_text(
            data,
            "emergency_contact_name",
        ),

        emergency_contact_phone=_optional_text(
            data,
            "emergency_contact_phone",
        ),

        emergency_contact_relationship=_optional_text(
            data,
            "emergency_contact_relationship",
        ),

        dietary_requirements=_optional_text(
            data,
            "dietary_requirements",
        ),

        medical_information=_optional_text(
            data,
            "medical_information",
        ),

        accessibility_requirements=_optional_text(
            data,
            "accessibility_requirements",
        ),

        special_requests=_optional_text(
            data,
            "special_requests",
        ),

        status=supplied_status,
        payment_status=supplied_payment_status,

        experience_date=experience_date,
        start_date=start_date,
        end_date=end_date,

        currency=currency,

        subtotal=subtotal,
        discount_amount=discount,
        tax_amount=tax,
        addon_total=addon_total,
        total_amount=total,

        amount_paid=ZERO,
        balance_due=total,

        customer_notes=_optional_text(
            data,
            "customer_notes",
        ),

        internal_notes=_optional_text(
            data,
            "internal_notes",
        ),

        confirmation_sent=False,
        reminder_sent=False,
        reviewed=False,
        active=True,
    )

    if supplied_status == "confirmed":

        booking.confirmed_at = (
            datetime.utcnow()
        )

    if supplied_status == "cancelled":

        booking.cancelled_at = (
            datetime.utcnow()
        )

        booking.cancellation_reason = (
            _optional_text(
                data,
                "cancellation_reason",
            )
        )

    if supplied_status == "completed":

        booking.completed_at = (
            datetime.utcnow()
        )

    if total == ZERO:

        booking.payment_status = (
            "not_required"
        )

    return booking


def _commit_booking(
    booking,
):
    """
    Commit a new booking and roll back on database failure.
    """

    try:

        db.session.add(
            booking
        )

        db.session.flush()
        db.session.commit()

        return booking

    except SQLAlchemyError as exc:

        db.session.rollback()

        raise BookingServiceError(
            "The booking could not be saved. "
            "No booking changes were committed."
        ) from exc


def create_booking(
    data=None,
    booking_type=None,
    source="website",
    detail=None,
    **kwargs,
):
    """
    Create a central booking.

    Supports both calling styles:

        create_booking(
            data,
            booking_type="experience",
        )

    and the existing route-style calls:

        create_booking(
            booking_type="experience",
            experience_id=5,
            first_name="Jane",
            ...
        )

    Product-specific detail records should be supplied through `detail`
    when required.
    """

    if data is None:
        data = {}

    elif not isinstance(
        data,
        dict,
    ):
        data = dict(data)

    if kwargs:
        data.update(kwargs)

    if booking_type is None:
        booking_type = data.pop(
            "booking_type",
            None,
        )

    if source == "website":

        supplied_source = data.pop(
            "source",
            None,
        )

        if supplied_source is not None:
            source = supplied_source

    booking = _build_central_booking(
        data,
        booking_type,
        source=source,
    )

    if detail is not None:

        expected_relationship = {
            "experience": "experience_booking",
            "safari": "safari_booking",
            "stay": "stay_booking",
            "destination_journey": "destination_booking",
        }[booking.booking_type]

        if not hasattr(
            booking,
            expected_relationship,
        ):
            raise BookingValidationError(
                "The selected booking type has no "
                "compatible detail relationship."
            )

        setattr(
            detail,
            "booking",
            booking,
        )

    return _commit_booking(
        booking
    )


# =============================================================================
# Lifecycle
# =============================================================================

def update_booking_status(
    booking_or_id,
    new_status,
    reason=None,
):
    """
    Apply a permitted booking lifecycle transition.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    new_status = str(
        new_status or ""
    ).strip().lower()

    if new_status not in BOOKING_STATUSES:
        raise BookingValidationError(
            "Invalid booking status."
        )

    current_status = str(
        booking.status or "pending"
    ).lower()

    if current_status == new_status:
        return booking

    allowed = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed:
        raise BookingTransitionError(
            f"Cannot change booking status from "
            f"'{current_status}' to '{new_status}'."
        )

    now = datetime.utcnow()

    booking.status = new_status

    if new_status == "confirmed":

        booking.confirmed_at = (
            booking.confirmed_at
            or now
        )

    elif new_status == "cancelled":

        booking.cancelled_at = now

        if reason:
            booking.cancellation_reason = (
                str(reason).strip()
            )

    elif new_status == "completed":

        booking.completed_at = now

    elif new_status == "archived":

        booking.active = False

    try:

        db.session.commit()

        return booking

    except SQLAlchemyError as exc:

        db.session.rollback()

        raise BookingServiceError(
            "The booking status could not be updated."
        ) from exc


def confirm_booking(
    booking_or_id,
):
    """
    Confirm a booking.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    if booking.status == "confirmed":
        return booking

    return update_booking_status(
        booking,
        "confirmed",
    )


def cancel_booking(
    booking_or_id,
    reason=None,
):
    """
    Cancel a booking and preserve the cancellation reason.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    if booking.status == "cancelled":
        return booking

    if booking.status in {
        "completed",
        "refunded",
        "archived",
    }:
        raise BookingTransitionError(
            f"A booking in '{booking.status}' "
            f"status cannot be cancelled."
        )

    return update_booking_status(
        booking,
        "cancelled",
        reason=reason,
    )


def complete_booking(
    booking_or_id,
):
    """
    Mark a booking as completed.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    if booking.status == "completed":
        return booking

    return update_booking_status(
        booking,
        "completed",
    )


def archive_booking(
    booking_or_id,
):
    """
    Archive a booking without deleting its history.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    if booking.status == "archived":
        return booking

    return update_booking_status(
        booking,
        "archived",
    )


# =============================================================================
# Financial updates
# =============================================================================

def update_booking_financials(
    booking_or_id,
    subtotal=None,
    discount_amount=None,
    tax_amount=None,
    addon_total=None,
):
    """
    Recalculate a booking's stored financial snapshot.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    new_subtotal = _money(
        (
            booking.subtotal
            if subtotal is None
            else subtotal
        ),
        "subtotal",
    )

    new_discount = _money(
        (
            booking.discount_amount
            if discount_amount is None
            else discount_amount
        ),
        "discount_amount",
    )

    new_tax = _money(
        (
            booking.tax_amount
            if tax_amount is None
            else tax_amount
        ),
        "tax_amount",
    )

    new_addon_total = _money(
        (
            booking.addon_total
            if addon_total is None
            else addon_total
        ),
        "addon_total",
    )

    new_total = _calculate_total(
        new_subtotal,
        new_discount,
        new_tax,
        new_addon_total,
    )

    booking.subtotal = new_subtotal
    booking.discount_amount = new_discount
    booking.tax_amount = new_tax
    booking.addon_total = new_addon_total
    booking.total_amount = new_total

    _refresh_financial_snapshots(
        booking
    )

    try:

        db.session.commit()

        return booking

    except SQLAlchemyError as exc:

        db.session.rollback()

        raise BookingServiceError(
            "Booking financials could not be updated."
        ) from exc


def refresh_booking_payment_status(
    booking_or_id,
):
    """
    Refresh payment status and balance from the booking's payment records.
    """

    booking = _coerce_booking(
        booking_or_id
    )

    _refresh_financial_snapshots(
        booking
    )

    try:

        db.session.commit()

        return booking

    except SQLAlchemyError as exc:

        db.session.rollback()

        raise BookingServiceError(
            "Booking payment snapshots could not be refreshed."
        ) from exc


# =============================================================================
# Summaries and display helpers
# =============================================================================

def get_booking_primary_subject(
    booking,
):
    """
    Return the related product/detail record when one exists.
    """

    return booking.service_detail


def get_booking_summary(
    booking,
):
    """
    Return a plain summary using fields and properties on Booking.
    """

    return {
        "id": booking.id,
        "reference": booking.booking_reference,
        "type": booking.booking_type,
        "service_name": booking.service_name,
        "customer_name": booking.full_name,
        "email": booking.email,
        "phone": booking.phone,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "booking_date": booking.booking_date,
        "experience_date": booking.experience_date,
        "start_date": booking.start_date,
        "end_date": booking.end_date,
        "adults": booking.adults,
        "children": booking.children,
        "infants": booking.infants,
        "seniors": booking.seniors,
        "students": booking.students,
        "total_guests": booking.total_guests,
        "currency": booking.currency,
        "subtotal": _money(
            booking.subtotal
        ),
        "discount_amount": _money(
            booking.discount_amount
        ),
        "tax_amount": _money(
            booking.tax_amount
        ),
        "addon_total": _money(
            booking.addon_total
        ),
        "total_amount": _money(
            booking.total_amount
        ),
        "amount_paid": _money(
            booking.total_paid
        ),
        "balance_due": _money(
            booking.amount_remaining
        ),
        "source": booking.source,
        "active": booking.active,
    }


def get_booking_counts():
    """
    Return high-level counts for booking dashboards.
    """

    return {
        "total": Booking.query.count(),

        "active": (
            Booking.query
            .filter_by(active=True)
            .count()
        ),

        "pending": (
            Booking.query
            .filter_by(status="pending")
            .count()
        ),

        "awaiting_payment": (
            Booking.query
            .filter_by(
                status="awaiting_payment"
            )
            .count()
        ),

        "confirmed": (
            Booking.query
            .filter_by(status="confirmed")
            .count()
        ),

        "in_progress": (
            Booking.query
            .filter_by(status="in_progress").count()),

        "completed": (
            Booking.query
            .filter_by(status="completed")
            .count()),

        "cancelled": (
            Booking.query
            .filter_by(status="cancelled")
            .count()),

        "unpaid": (
            Booking.query
            .filter_by(payment_status="unpaid").count()),

        "partially_paid": (
            Booking.query
            .filter_by(payment_status="partially_paid").count()),

        "paid": (
            Booking.query
            .filter_by(payment_status="paid").count()),}