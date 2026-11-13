
"""
The Uncharted Route
Booking Note Service

Business logic for booking notes and operational timeline entries.
Notes use the actual BookingNote model fields; each new interaction should
normally create a new entry rather than overwrite historical communications.
"""

from datetime import datetime

from extensions import db
from app.models import Booking, BookingNote


NOTE_TYPES = {
    "internal_note",
    "customer_message",
    "phone_call",
    "email",
    "whatsapp",
    "sms",
    "payment",
    "operations",
    "complaint",
    "resolution",
    "reminder",
    "system_event",
}

VISIBILITIES = {"internal", "customer"}
COMMUNICATION_CHANNELS = {
    "phone",
    "whatsapp",
    "email",
    "sms",
    "in_person",
    "internal",
    "system",
}
DIRECTIONS = {"inbound", "outbound", "internal"}
DELIVERY_STATUSES = {
    "pending",
    "queued",
    "sent",
    "delivered",
    "failed",
    "not_applicable",
}


def _get_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        raise ValueError("Booking not found.")
    return booking


def _get_note(note_id):
    note = db.session.get(BookingNote, note_id)
    if note is None:
        raise ValueError("Booking note not found.")
    return note


def _clean_optional(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _validate_choice(value, choices, label, allow_none=False):
    if value is None and allow_none:
        return
    if value not in choices:
        raise ValueError(f"Invalid {label}.")


def _commit(commit=True):
    if commit:
        db.session.commit()
    else:
        db.session.flush()


def create_booking_note(
    booking_id,
    content,
    title=None,
    note_type="internal_note",
    visibility="internal",
    communication_channel=None,
    direction=None,
    recipient=None,
    subject=None,
    external_reference=None,
    event_data=None,
    author_user_id=None,
    author_name_snapshot=None,
    author_role_snapshot=None,
    delivery_status=None,
    delivered_at=None,
    delivery_error=None,
    commit=True,
):
    """Create a note in the central booking timeline."""
    _get_booking(booking_id)

    content = _clean_optional(content)
    if not content:
        raise ValueError("Note content is required.")

    title = _clean_optional(title)
    _validate_choice(note_type, NOTE_TYPES, "note type")
    _validate_choice(visibility, VISIBILITIES, "visibility")
    _validate_choice(
        communication_channel,
        COMMUNICATION_CHANNELS,
        "communication channel",
        allow_none=True,
    )
    _validate_choice(direction, DIRECTIONS, "communication direction", True)
    _validate_choice(delivery_status, DELIVERY_STATUSES, "delivery status", True)

    if visibility == "internal" and delivery_status in {"sent", "delivered"}:
        raise ValueError("An internal-only note cannot be marked as customer-delivered.")

    if event_data is not None and not isinstance(event_data, dict):
        raise ValueError("Event data must be a dictionary.")

    note = BookingNote(
        booking_id=booking_id,
        content=content,
        title=title,
        note_type=note_type,
        visibility=visibility,
        communication_channel=communication_channel,
        direction=direction,
        recipient=_clean_optional(recipient),
        subject=_clean_optional(subject),
        external_reference=_clean_optional(external_reference),
        event_data=event_data,
        author_user_id=author_user_id,
        author_name_snapshot=_clean_optional(author_name_snapshot),
        author_role_snapshot=_clean_optional(author_role_snapshot),
        delivery_status=delivery_status,
        delivered_at=delivered_at,
        delivery_error=_clean_optional(delivery_error),
        created_at=datetime.utcnow(),
    )

    db.session.add(note)
    _commit(commit)
    return note


def get_booking_note(note_id):
    return db.session.get(BookingNote, note_id)


def get_booking_notes(
    booking_id,
    visibility=None,
    note_type=None,
    communication_channel=None,
    author_user_id=None,
    limit=None,
):
    """Retrieve notes for one booking, oldest first."""
    _get_booking(booking_id)
    query = BookingNote.query.filter_by(booking_id=booking_id)

    if visibility:
        _validate_choice(visibility, VISIBILITIES, "visibility")
        query = query.filter_by(visibility=visibility)
    if note_type:
        _validate_choice(note_type, NOTE_TYPES, "note type")
        query = query.filter_by(note_type=note_type)
    if communication_channel:
        _validate_choice(
            communication_channel,
            COMMUNICATION_CHANNELS,
            "communication channel",
        )
        query = query.filter_by(communication_channel=communication_channel)
    if author_user_id is not None:
        query = query.filter_by(author_user_id=author_user_id)
    if limit is not None:
        if int(limit) < 1:
            raise ValueError("Limit must be greater than zero.")
        query = query.limit(int(limit))

    return query.order_by(BookingNote.created_at.asc(), BookingNote.id.asc()).all()


def get_all_booking_notes(
    visibility=None,
    note_type=None,
    search=None,
    delivery_status=None,
    limit=None,
):
    """Retrieve notes across booking for the admin CMS."""
    query = BookingNote.query

    if visibility:
        _validate_choice(visibility, VISIBILITIES, "visibility")
        query = query.filter_by(visibility=visibility)
    if note_type:
        _validate_choice(note_type, NOTE_TYPES, "note type")
        query = query.filter_by(note_type=note_type)
    if delivery_status:
        _validate_choice(delivery_status, DELIVERY_STATUSES, "delivery status")
        query = query.filter_by(delivery_status=delivery_status)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            db.or_(
                BookingNote.title.ilike(term),
                BookingNote.content.ilike(term),
                BookingNote.recipient.ilike(term),
                BookingNote.subject.ilike(term),
                BookingNote.external_reference.ilike(term),
                BookingNote.author_name_snapshot.ilike(term),
            )
        )
    if limit is not None:
        if int(limit) < 1:
            raise ValueError("Limit must be greater than zero.")
        query = query.limit(int(limit))

    return query.order_by(BookingNote.created_at.desc(), BookingNote.id.desc()).all()


def get_booking_timeline(booking_id, visibility=None):
    return get_booking_notes(booking_id, visibility=visibility)


def get_latest_booking_notes(booking_id, limit=10, visibility=None):
    _get_booking(booking_id)
    if int(limit) < 1:
        raise ValueError("Limit must be greater than zero.")

    query = BookingNote.query.filter_by(booking_id=booking_id)
    if visibility:
        _validate_choice(visibility, VISIBILITIES, "visibility")
        query = query.filter_by(visibility=visibility)

    return query.order_by(
        BookingNote.created_at.desc(), BookingNote.id.desc()
    ).limit(int(limit)).all()


def get_customer_visible_notes(booking_id, limit=None):
    return get_booking_notes(
        booking_id,
        visibility="customer",
        limit=limit,
    )


def update_booking_note(note_id, commit=True, **updates):
    """
    Update editable note metadata/content.

    Only fields that exist on BookingNote are accepted. created_at is preserved.
    For a new communication or event, create a new note instead.
    """
    note = _get_note(note_id)
    allowed = {
        "title",
        "content",
        "note_type",
        "visibility",
        "communication_channel",
        "direction",
        "recipient",
        "subject",
        "external_reference",
        "event_data",
        "author_name_snapshot",
        "author_role_snapshot",
        "delivery_status",
        "delivered_at",
        "delivery_error",
        "verification_notes",
    }

    unknown = set(updates) - allowed
    if unknown:
        raise ValueError(
            "Unsupported note field(s): " + ", ".join(sorted(unknown))
        )

    for field, value in updates.items():
        if field in {"title", "recipient", "subject", "external_reference",
                     "author_name_snapshot", "author_role_snapshot",
                     "delivery_error"}:
            value = _clean_optional(value)

        if field == "content":
            value = _clean_optional(value)
            if not value:
                raise ValueError("Note content is required.")
        elif field == "note_type":
            _validate_choice(value, NOTE_TYPES, "note type")
        elif field == "visibility":
            _validate_choice(value, VISIBILITIES, "visibility")
        elif field == "communication_channel":
            _validate_choice(
                value, COMMUNICATION_CHANNELS, "communication channel", True
            )
        elif field == "direction":
            _validate_choice(value, DIRECTIONS, "communication direction", True)
        elif field == "delivery_status":
            _validate_choice(value, DELIVERY_STATUSES, "delivery status", True)
        elif field == "event_data" and value is not None:
            if not isinstance(value, dict):
                raise ValueError("Event data must be a dictionary.")

        setattr(note, field, value)

    if note.visibility == "internal" and note.delivery_status in {"sent", "delivered"}:
        raise ValueError("An internal-only note cannot be marked as customer-delivered.")

    _commit(commit)
    return note


def set_note_visibility(note_id, visibility, commit=True):
    _validate_choice(visibility, VISIBILITIES, "visibility")
    note = _get_note(note_id)

    if visibility == "internal" and note.delivery_status in {"sent", "delivered"}:
        raise ValueError(
            "This note is marked delivered. Review its delivery status before hiding it."
        )

    note.visibility = visibility
    _commit(commit)
    return note


def make_customer_visible(note_id, commit=True):
    return set_note_visibility(note_id, "customer", commit=commit)


def hide_from_customer(note_id, commit=True):
    return set_note_visibility(note_id, "internal", commit=commit)


def update_delivery_status(
    note_id,
    delivery_status,
    delivered_at=None,
    delivery_error=None,
    commit=True,
):
    _validate_choice(delivery_status, DELIVERY_STATUSES, "delivery status")
    note = _get_note(note_id)

    if delivery_status in {"sent", "delivered"} and note.visibility != "customer":
        raise ValueError("Only customer-visible notes can be marked sent or delivered.")

    note.delivery_status = delivery_status
    note.delivered_at = delivered_at or (
        datetime.utcnow() if delivery_status == "delivered" else None
    )
    note.delivery_error = _clean_optional(delivery_error)
    _commit(commit)
    return note


def get_notes_by_delivery_status(delivery_status, booking_id=None):
    _validate_choice(delivery_status, DELIVERY_STATUSES, "delivery status")
    query = BookingNote.query.filter_by(delivery_status=delivery_status)
    if booking_id is not None:
        _get_booking(booking_id)
        query = query.filter_by(booking_id=booking_id)
    return query.order_by(BookingNote.created_at.desc()).all()


def delete_booking_note(note_id, commit=True):
    """
    Permanently delete a note. Prefer retaining operational history.
    Restrict this operation to authorised administrators.
    """
    note = _get_note(note_id)
    db.session.delete(note)
    _commit(commit)
    return True


def get_booking_note_summary(booking_id):
    _get_booking(booking_id)
    notes = BookingNote.query.filter_by(booking_id=booking_id).all()

    return {
        "booking_id": booking_id,
        "total_notes": len(notes),
        "internal_notes": sum(n.visibility == "internal" for n in notes),
        "customer_visible_notes": sum(n.visibility == "customer" for n in notes),
        "communication_notes": sum(bool(n.communication_channel) for n in notes),
        "pending_delivery": sum(n.delivery_status == "pending" for n in notes),
        "failed_delivery": sum(n.delivery_status == "failed" for n in notes),
        "delivered": sum(n.delivery_status == "delivered" for n in notes),
    }
