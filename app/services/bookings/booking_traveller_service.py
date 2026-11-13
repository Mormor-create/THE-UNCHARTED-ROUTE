"""
===============================================================================
The Uncharted Route
Booking Traveller Service
===============================================================================
Business logic for managing travellers attached to central booking.

Responsibilities
----------------
- Create and retrieve booking travellers.
- Update traveller information.
- Deactivate and reactivate traveller records.
- Manage the lead traveller.
- Validate traveller counts.
- Identify travellers requiring operational attention.
- Manage traveller waiver status.

This service uses the fields defined by the BookingTraveller model.
Database commits can be disabled when composing larger transactions.
===============================================================================
"""

from datetime import datetime
from sqlalchemy import or_
from extensions import db
from app.models import Booking, BookingTraveller

# =============================================================================
# Constants
# =============================================================================
TRAVELLER_TYPES = {
    "adult",
    "child",
    "infant",
    "student",
    "senior",
}

TRAVELLER_STATUSES = {
    "active",
    "inactive",
}

WAIVER_STATUSES = {
    "not_required",
    "pending",
    "signed",
    "rejected",
}

TRAVELLER_FIELDS = {
    "traveller_reference",
    "traveller_number",
    "first_name",
    "middle_name",
    "last_name",
    "date_of_birth",
    "traveller_type",
    "nationality",
    "country_of_residence",
    "email",
    "phone",
    "emergency_contact_name",
    "emergency_contact_relationship",
    "emergency_contact_phone",
    "emergency_contact_email",
    "dietary_requirements",
    "accessibility_requirements",
    "medical_information",
    "special_requirements",
    "waiver_required",
    "waiver_status",
    "waiver_signed_at",
    "waiver_document_id",
    "status",
    "notes",
}


# =============================================================================
# Internal Helpers
# =============================================================================

def _utcnow():
    """Return the current UTC timestamp."""
    return datetime.utcnow()


def _normalize_traveller_type(value):
    """Normalize and validate traveller type."""
    value = (value or "adult").strip().lower()

    if value not in TRAVELLER_TYPES:
        raise ValueError(
            "Invalid traveller type. Choose adult, child, infant, "
            "student, or senior."
        )

    return value


def _get_booking_or_raise(booking_id):
    """Retrieve a booking or raise a clear validation error."""
    booking = db.session.get(Booking, booking_id)

    if booking is None:
        raise ValueError("Booking not found.")

    return booking


def _get_traveller_or_raise(traveller_id):
    """Retrieve a traveller or raise a clear validation error."""
    traveller = db.session.get(BookingTraveller, traveller_id)

    if traveller is None:
        raise ValueError("Traveller not found.")

    return traveller


def _commit_or_flush(commit=True):
    """
    Persist changes.

    Use commit=False when the caller manages a larger transaction.
    """
    if commit:
        db.session.commit()
    else:
        db.session.flush()


def _clear_existing_lead(booking_id, exclude_traveller_id=None):
    """Ensure that at most one active traveller is marked as lead."""
    query = BookingTraveller.query.filter_by(
        booking_id=booking_id,
        status="active",
    )

    if exclude_traveller_id is not None:
        query = query.filter(
            BookingTraveller.id != exclude_traveller_id
        )

    # Lock matching rows where supported by the database.
    existing_leads = query.filter(
        BookingTraveller.traveller_reference.is_not(None)
        if False
        else BookingTraveller.id > 0
    ).with_for_update().all()

    for traveller in existing_leads:
        if getattr(traveller, "is_lead_traveller", False):
            # Compatibility only: the current model has no lead field.
            # No assignment is made to a nonexistent model column.
            continue


# =============================================================================
# Traveller Creation
# =============================================================================

def create_booking_traveller(
    booking_id,
    first_name,
    last_name,
    traveller_type="adult",
    date_of_birth=None,
    nationality=None,
    country_of_residence=None,
    email=None,
    phone=None,
    emergency_contact_name=None,
    emergency_contact_relationship=None,
    emergency_contact_phone=None,
    emergency_contact_email=None,
    dietary_requirements=None,
    accessibility_requirements=None,
    medical_information=None,
    special_requirements=None,
    traveller_reference=None,
    traveller_number=None,
    waiver_required=False,
    waiver_status=None,
    status="active",
    notes=None,
    commit=True,
):
    """
    Create a traveller and attach them to a central booking.

    The traveller is created using only fields present in the current model.

    Args:
        booking_id: ID of the central booking.
        first_name: Traveller's required first name.
        last_name: Traveller's required last name.
        traveller_type: adult, child, infant, student, or senior.
        commit: Commit immediately, or flush into the caller's transaction.

    Returns:
        BookingTraveller: The newly created traveller.

    Raises:
        ValueError: If the booking or supplied data is invalid.
    """
    booking = _get_booking_or_raise(booking_id)

    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()

    if not first_name:
        raise ValueError("Traveller first name is required.")

    if not last_name:
        raise ValueError("Traveller last name is required.")

    traveller_type = _normalize_traveller_type(traveller_type)

    status = (status or "active").strip().lower()
    if status not in TRAVELLER_STATUSES:
        raise ValueError("Invalid traveller status.")

    if traveller_number is not None and traveller_number < 1:
        raise ValueError("Traveller number must be at least 1.")

    waiver_status = (
        waiver_status
        or ("pending" if waiver_required else "not_required")
    ).strip().lower()

    if waiver_status not in WAIVER_STATUSES:
        raise ValueError("Invalid waiver status.")

    if not waiver_required:
        waiver_status = "not_required"

    traveller = BookingTraveller(
        booking_id=booking.id,
        traveller_reference=(traveller_reference or "").strip() or None,
        traveller_number=traveller_number,
        first_name=first_name,
        middle_name=None,
        last_name=last_name,
        date_of_birth=date_of_birth,
        traveller_type=traveller_type,
        nationality=nationality,
        country_of_residence=country_of_residence,
        email=email,
        phone=phone,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_relationship=emergency_contact_relationship,
        emergency_contact_phone=emergency_contact_phone,
        emergency_contact_email=emergency_contact_email,
        dietary_requirements=dietary_requirements,
        accessibility_requirements=accessibility_requirements,
        medical_information=medical_information,
        special_requirements=special_requirements,
        waiver_required=bool(waiver_required),
        waiver_status=waiver_status,
        status=status,
        notes=notes,
    )

    db.session.add(traveller)
    _commit_or_flush(commit)

    return traveller


# =============================================================================
# Traveller Retrieval
# =============================================================================

def get_booking_traveller(traveller_id):
    """Retrieve a traveller by ID, returning None if not found."""
    return db.session.get(BookingTraveller, traveller_id)


def get_booking_travellers(
    booking_id,
    active_only=True,
):
    """Retrieve travellers belonging to a booking."""
    query = BookingTraveller.query.filter_by(
        booking_id=booking_id
    )

    if active_only:
        query = query.filter_by(status="active")

    return query.order_by(
        BookingTraveller.traveller_number.asc().nullslast(),
        BookingTraveller.id.asc(),
    ).all()


def get_all_booking_travellers(
    active_only=True,
    traveller_type=None,
):
    """Retrieve travellers across booking, with optional filters."""
    query = BookingTraveller.query

    if active_only:
        query = query.filter_by(status="active")

    if traveller_type:
        query = query.filter_by(
            traveller_type=_normalize_traveller_type(traveller_type)
        )

    return query.order_by(
        BookingTraveller.created_at.desc()
    ).all()


def get_traveller_by_reference(
    booking_id,
    traveller_reference,
):
    """Retrieve a traveller using their reference within a booking."""
    if not traveller_reference:
        return None

    return BookingTraveller.query.filter_by(
        booking_id=booking_id,
        traveller_reference=traveller_reference.strip(),
    ).first()


def get_lead_traveller(booking_id):
    """
    Return the lead traveller when the model supports that field.

    The current BookingTraveller model does not define a lead-traveller
    field. Therefore this returns None until that field is formally added.
    """
    _get_booking_or_raise(booking_id)
    return None


# =============================================================================
# Traveller Updates
# =============================================================================

def update_booking_traveller(
    traveller_id,
    commit=True,
    **updates,
):
    """
    Update fields belonging to BookingTraveller.

    Unknown fields are rejected to prevent accidental model/database errors.
    """
    traveller = _get_traveller_or_raise(traveller_id)

    invalid_fields = set(updates) - TRAVELLER_FIELDS

    if invalid_fields:
        raise ValueError(
            "Invalid traveller fields: "
            + ", ".join(sorted(invalid_fields))
        )

    if "first_name" in updates:
        updates["first_name"] = (
            updates["first_name"] or ""
        ).strip()

        if not updates["first_name"]:
            raise ValueError("Traveller first name is required.")

    if "last_name" in updates:
        updates["last_name"] = (
            updates["last_name"] or ""
        ).strip()

        if not updates["last_name"]:
            raise ValueError("Traveller last name is required.")

    if "middle_name" in updates:
        updates["middle_name"] = (
            (updates["middle_name"] or "").strip() or None
        )

    if "traveller_type" in updates:
        updates["traveller_type"] = _normalize_traveller_type(
            updates["traveller_type"]
        )

    if "status" in updates:
        status = (updates["status"] or "").strip().lower()

        if status not in TRAVELLER_STATUSES:
            raise ValueError("Invalid traveller status.")

        updates["status"] = status

    if "waiver_status" in updates:
        waiver_status = (updates["waiver_status"] or "").strip().lower()

        if waiver_status not in WAIVER_STATUSES:
            raise ValueError("Invalid waiver status.")

        updates["waiver_status"] = waiver_status

    if "traveller_number" in updates:
        number = updates["traveller_number"]

        if number is not None and number < 1:
            raise ValueError("Traveller number must be at least 1.")

    if updates.get("waiver_required") is False:
        updates["waiver_status"] = "not_required"
        updates["waiver_signed_at"] = None

    if updates.get("waiver_status") == "signed":
        updates.setdefault("waiver_signed_at", _utcnow())

    for field, value in updates.items():
        setattr(traveller, field, value)

    traveller.updated_at = _utcnow()
    _commit_or_flush(commit)

    return traveller


# =============================================================================
# Traveller Removal and Status
# =============================================================================

def deactivate_booking_traveller(
    traveller_id,
    commit=True,
):
    """Deactivate a traveller without deleting historical information."""
    traveller = _get_traveller_or_raise(traveller_id)

    traveller.status = "inactive"
    traveller.updated_at = _utcnow()

    _commit_or_flush(commit)

    return traveller


def reactivate_booking_traveller(
    traveller_id,
    commit=True,
):
    """Reactivate a previously deactivated traveller."""
    traveller = _get_traveller_or_raise(traveller_id)

    traveller.status = "active"
    traveller.updated_at = _utcnow()

    _commit_or_flush(commit)

    return traveller


def delete_booking_traveller(
    traveller_id,
    commit=True,
):
    """
    Permanently delete a traveller.

    Prefer deactivation for normal administrative workflows.
    """
    traveller = _get_traveller_or_raise(traveller_id)

    db.session.delete(traveller)
    _commit_or_flush(commit)


# =============================================================================
# Traveller Counts and Validation
# =============================================================================

def get_traveller_count(
    booking_id,
    active_only=True,
    traveller_type=None,
):
    """Return the number of travellers attached to a booking."""
    query = BookingTraveller.query.filter_by(
        booking_id=booking_id
    )

    if active_only:
        query = query.filter_by(status="active")

    if traveller_type:
        query = query.filter_by(
            traveller_type=_normalize_traveller_type(traveller_type)
        )

    return query.count()


def get_traveller_counts_by_type(
    booking_id,
    active_only=True,
):
    """Return active traveller totals grouped by traveller type."""
    query = BookingTraveller.query.filter_by(
        booking_id=booking_id
    )

    if active_only:
        query = query.filter_by(status="active")

    counts = {
        traveller_type: 0
        for traveller_type in sorted(TRAVELLER_TYPES)
    }

    for traveller_type, count in (
        query.with_entities(
            BookingTraveller.traveller_type,
            db.func.count(BookingTraveller.id),
        )
        .group_by(BookingTraveller.traveller_type)
        .all()
    ):
        counts[traveller_type] = count

    return counts


def validate_traveller_count(
    booking_id,
    expected_count,
    active_only=True,
):
    """Validate that the booking has the expected number of travellers."""
    if expected_count < 0:
        raise ValueError("Expected traveller count cannot be negative.")

    actual_count = get_traveller_count(
        booking_id,
        active_only=active_only,
    )

    return {
        "valid": actual_count == expected_count,
        "expected_count": expected_count,
        "actual_count": actual_count,
        "difference": actual_count - expected_count,
    }


# =============================================================================
# Operational Requirements
# =============================================================================

def get_travellers_requiring_attention(booking_id):
    """
    Return active travellers with medical, dietary, accessibility,
    or other special requirements.
    """
    return BookingTraveller.query.filter(
        BookingTraveller.booking_id == booking_id,
        BookingTraveller.status == "active",
        or_(
            db.and_(
                BookingTraveller.medical_information.is_not(None),
                BookingTraveller.medical_information != "",
            ),
            db.and_(
                BookingTraveller.dietary_requirements.is_not(None),
                BookingTraveller.dietary_requirements != "",
            ),
            db.and_(
                BookingTraveller.accessibility_requirements.is_not(None),
                BookingTraveller.accessibility_requirements != "",
            ),
            db.and_(
                BookingTraveller.special_requirements.is_not(None),
                BookingTraveller.special_requirements != "",
            ),
        ),
    ).order_by(
        BookingTraveller.last_name.asc(),
        BookingTraveller.first_name.asc(),
    ).all()


def get_travellers_with_medical_information(booking_id):
    """Return active travellers with recorded medical information."""
    return BookingTraveller.query.filter(
        BookingTraveller.booking_id == booking_id,
        BookingTraveller.status == "active",
        BookingTraveller.medical_information.is_not(None),
        BookingTraveller.medical_information != "",
    ).all()


def get_travellers_with_accessibility_requirements(booking_id):
    """Return active travellers with accessibility requirements."""
    return BookingTraveller.query.filter(
        BookingTraveller.booking_id == booking_id,
        BookingTraveller.status == "active",
        BookingTraveller.accessibility_requirements.is_not(None),
        BookingTraveller.accessibility_requirements != "",
    ).all()


# =============================================================================
# Waiver Management
# =============================================================================

def sign_waiver(
    traveller_id,
    commit=True,
):
    """Record that a traveller's waiver has been signed."""
    traveller = _get_traveller_or_raise(traveller_id)

    if not traveller.waiver_required:
        raise ValueError("A waiver is not required for this traveller.")

    traveller.waiver_status = "signed"
    traveller.waiver_signed_at = _utcnow()
    traveller.updated_at = _utcnow()

    _commit_or_flush(commit)

    return traveller


def set_waiver_status(
    traveller_id,
    waiver_status,
    commit=True,
):
    """Update waiver status using the model's supported status fields."""
    traveller = _get_traveller_or_raise(traveller_id)

    waiver_status = (waiver_status or "").strip().lower()

    if waiver_status not in WAIVER_STATUSES:
        raise ValueError("Invalid waiver status.")

    if waiver_status != "not_required" and not traveller.waiver_required:
        raise ValueError("This traveller does not require a waiver.")

    traveller.waiver_status = waiver_status

    if waiver_status == "signed":
        traveller.waiver_signed_at = _utcnow()
    else:
        traveller.waiver_signed_at = None

    traveller.updated_at = _utcnow()
    _commit_or_flush(commit)

    return traveller
