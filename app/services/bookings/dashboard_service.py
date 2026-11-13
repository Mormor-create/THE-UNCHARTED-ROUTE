"""
===============================================================================
The Uncharted Route
Central Booking Dashboard Service
===============================================================================
Read-only dashboard statistics for the central booking management interface.
Booking creation, allocation, payments and request conversion remain in their
existing services.
"""

from datetime import date
from sqlalchemy import func, or_
from extensions import db
from app.models import Booking

BOOKING_TYPES = {
    "experience": "Experiences",
    "safari": "Safaris",
    "stay": "Stays",
    "destination_journey": "Destination Journeys",}

BOOKING_STATUSES = (
    "pending",
    "awaiting_payment",
    "confirmed",
    "in_progress",
    "completed",
    "cancelled",
    "refunded",
    "archived",)

BOOKING_SOURCES = (
    "website",
    "staff_request",
    "admin",
    "phone",
    "other",)

def _count(query):
    """Return a count without loading every matching record."""
    return query.with_entities(func.count(Booking.id)).scalar() or 0

def _booking_type_counts():
    rows = (
        db.session.query(
            Booking.booking_type,
            func.count(Booking.id),
        )
        .group_by(Booking.booking_type)
        .all()
    )

    counts = {key: 0 for key in BOOKING_TYPES}

    for booking_type, count in rows:
        if booking_type in counts:
            counts[booking_type] = count

    return [
        {
            "key": key,
            "label": label,
            "count": counts[key],
        }
        for key, label in BOOKING_TYPES.items()
    ]


def _status_counts():
    rows = (
        db.session.query(
            Booking.status,
            func.count(Booking.id),
        )
        .group_by(Booking.status)
        .all()
    )

    return {
        status: count
        for status, count in rows
    }


def _source_counts():
    rows = (
        db.session.query(
            Booking.source,
            func.count(Booking.id),
        )
        .group_by(Booking.source)
        .all()
    )

    counts = dict(rows)
    total = sum(counts.values()) or 0

    labels = {
        "website": "Website",
        "staff_request": "Staff Request",
        "admin": "Administrator",
        "phone": "Phone",
        "other": "Other",
    }

    return [
        {
            "key": source,
            "label": labels[source],
            "count": counts.get(source, 0),
            "percentage": round(
                counts.get(source, 0) * 100 / total
            ) if total else 0,
        }
        for source in BOOKING_SOURCES
        if counts.get(source, 0) or source in {"website", "staff_request", "admin"}
    ]


def _assignment_state(booking):
    """Determine whether a booking has an assignment without assuming fields."""
    assignments = getattr(booking, "staff_assignments", None) or []

    for assignment in assignments:
        status = str(getattr(assignment, "status", "") or "").lower()

        if status not in {"cancelled", "inactive", "rejected"}:
            return True

    return False


def _booking_title(booking):
    """Return the service-specific name exposed by the central model."""
    try:
        return booking.service_name or booking.booking_type.replace("_", " ").title()
    except Exception:
        return booking.booking_type.replace("_", " ").title()


def _booking_row(booking):
    """Convert a central booking into a dashboard table row."""
    assigned = _assignment_state(booking)

    return {
        "id": booking.id,
        "reference": booking.booking_reference,
        "type": booking.booking_type,
        "type_label": BOOKING_TYPES.get(
            booking.booking_type,
            booking.booking_type.replace("_", " ").title(),
        ),
        "customer": booking.full_name or "Customer",
        "email": booking.email,
        "phone": booking.phone,
        "service_name": _booking_title(booking),
        "start_date": booking.start_date or booking.experience_date,
        "end_date": booking.end_date,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "currency": booking.currency,
        "total_amount": booking.total_amount or 0,
        "amount_paid": booking.amount_paid or 0,
        "balance_due": booking.balance_due or 0,
        "source": booking.source,
        "assigned": assigned,
        "traveller_count": booking.total_guests,
        "created_at": booking.created_at,
    }


def get_central_booking_dashboard():
    """
    Return dashboard data from the central Booking table.

    This is a read-only operation. It does not create booking, change
    payment totals, assign staff or convert booking requests.
    """
    query = Booking.query.filter(Booking.active.is_(True))
    today = date.today()

    total_bookings = _count(query)

    awaiting_assignment = sum(
        1
        for booking in query.order_by(Booking.created_at.desc()).limit(500).all()
        if not _assignment_state(booking)
        and booking.status not in {"cancelled", "refunded", "archived", "completed"}
    )

    assigned_count = sum(
        1
        for booking in query.order_by(Booking.created_at.desc()).limit(500).all()
        if _assignment_state(booking)
    )

    recent_bookings = (
        query.order_by(Booking.created_at.desc())
        .limit(10)
        .all()
    )

    upcoming_bookings = (
        query.filter(
            Booking.start_date.isnot(None),
            Booking.start_date >= today,
            Booking.status.notin_(("cancelled", "refunded", "archived", "completed")),
        )
        .order_by(Booking.start_date.asc())
        .limit(8)
        .all()
    )

    status_counts = _status_counts()
    total_for_status = sum(status_counts.values()) or 1

    status_labels = {
        "pending": "Pending",
        "awaiting_payment": "Awaiting Payment",
        "confirmed": "Confirmed",
        "in_progress": "In Progress",
        "completed": "Completed",
        "cancelled": "Cancelled",
        "refunded": "Refunded",
        "archived": "Archived",
    }

    status_overview = [
        {
            "key": status,
            "label": status_labels[status],
            "count": status_counts.get(status, 0),
            "percentage": round(
                status_counts.get(status, 0) * 100 / total_for_status
            ),
        }
        for status in BOOKING_STATUSES
        if status_counts.get(status, 0)
    ]

    # Shared-record counts use the central model's established relationships.
    # These counts represent records attached to active booking.
    payments_count = sum(len(booking.payments) for booking in query.all())
    documents_count = sum(len(booking.documents) for booking in query.all())
    travellers_count = sum(len(booking.travellers) for booking in query.all())
    notes_count = sum(len(booking.notes) for booking in query.all())
    addons_count = sum(len(booking.addons) for booking in query.all())

    return {
        "total_bookings": total_bookings,
        "awaiting_assignment": awaiting_assignment,
        "assigned_count": assigned_count,
        "open_requests": None,
        "staff_tasks": None,
        "booking_types": _booking_type_counts(),
        "status_overview": status_overview,
        "source_overview": _source_counts(),
        "recent_bookings": [
            _booking_row(booking)
            for booking in recent_bookings
        ],
        "upcoming_bookings": [
            _booking_row(booking)
            for booking in upcoming_bookings
        ],
        "shared_counts": {
            "addons": addons_count,
            "payments": payments_count,
            "documents": documents_count,
            "travellers": travellers_count,
            "notes": notes_count,
        },
    }
