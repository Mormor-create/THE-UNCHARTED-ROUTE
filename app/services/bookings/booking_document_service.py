"""
The Uncharted Route
Booking Document Service
Business logic for private documents attached to central booking and,
optionally, individual travellers.
Storage keys are private identifiers, never public URLs.
"""

from datetime import date, datetime
from extensions import db
from app.models import Booking, BookingDocument, BookingTraveller

DOCUMENT_STATUSES = {
    "uploaded",
    "under_review",
    "approved",
    "rejected",
    "archived",}

VERIFICATION_STATUSES = {
    "pending",
    "verified",
    "rejected",}

DOCUMENT_TYPES = {
    "passport",
    "national_id",
    "visa",
    "insurance",
    "waiver",
    "payment_receipt",
    "booking_confirmation",
    "itinerary",
    "medical",
    "consent",
    "other",}

EDITABLE_FIELDS = {
    "title",
    "document_type",
    "description",
    "status",
    "original_filename",
    "mime_type",
    "file_size_bytes",
    "checksum_sha256",
    "issuing_country",
    "issued_at",
    "expires_at",
    "verification_status",
    "verification_notes",
    "rejection_reason",
    "traveller_id",
    "uploaded_by_user_id",}

def _commit(commit=True):
    if commit:
        db.session.commit()
    else:
        db.session.flush()


def _normalise_text(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _get_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        raise ValueError("The selected booking does not exist.")
    return booking


def _get_document(document_id):
    return db.session.get(BookingDocument, document_id)


def _validate_document_data(
    booking_id,
    title,
    document_type,
    original_filename,
    storage_key,
    traveller_id=None,
    file_size_bytes=None,
    issued_at=None,
    expires_at=None,
    verification_status="pending",
    status="uploaded",
):
    _get_booking(booking_id)

    if not _normalise_text(title):
        raise ValueError("Document title is required.")

    if not _normalise_text(document_type):
        raise ValueError("Document type is required.")

    if not _normalise_text(original_filename):
        raise ValueError("Original filename is required.")

    if not _normalise_text(storage_key):
        raise ValueError("A private storage key is required.")

    if status not in DOCUMENT_STATUSES:
        raise ValueError("Invalid document status.")

    if verification_status not in VERIFICATION_STATUSES:
        raise ValueError("Invalid verification status.")

    if file_size_bytes is not None and int(file_size_bytes) < 0:
        raise ValueError("File size cannot be negative.")

    if issued_at and expires_at and expires_at < issued_at:
        raise ValueError("Expiry date cannot be earlier than issue date.")

    if traveller_id is not None:
        traveller = db.session.get(BookingTraveller, traveller_id)
        if traveller is None:
            raise ValueError("The selected traveller does not exist.")
        if traveller.booking_id != booking_id:
            raise ValueError(
                "The selected traveller does not belong to this booking."
            )


def create_booking_document(
    booking_id,
    title,
    document_type,
    original_filename,
    storage_key,
    description=None,
    traveller_id=None,
    mime_type=None,
    file_size_bytes=None,
    checksum_sha256=None,
    issuing_country=None,
    issued_at=None,
    expires_at=None,
    status="uploaded",
    verification_status="pending",
    verification_notes=None,
    rejection_reason=None,
    uploaded_by_user_id=None,
    commit=True,
):
    """Create document metadata for a file already stored privately."""

    title = _normalise_text(title)
    document_type = _normalise_text(document_type)
    original_filename = _normalise_text(original_filename)
    storage_key = _normalise_text(storage_key)

    _validate_document_data(
        booking_id=booking_id,
        title=title,
        document_type=document_type,
        original_filename=original_filename,
        storage_key=storage_key,
        traveller_id=traveller_id,
        file_size_bytes=file_size_bytes,
        issued_at=issued_at,
        expires_at=expires_at,
        verification_status=verification_status,
        status=status,
    )

    document = BookingDocument(
        booking_id=booking_id,
        traveller_id=traveller_id,
        title=title,
        document_type=document_type,
        description=_normalise_text(description),
        status=status,
        original_filename=original_filename,
        storage_key=storage_key,
        mime_type=_normalise_text(mime_type),
        file_size_bytes=file_size_bytes,
        checksum_sha256=_normalise_text(checksum_sha256),
        issuing_country=_normalise_text(issuing_country),
        issued_at=issued_at,
        expires_at=expires_at,
        verification_status=verification_status,
        verification_notes=_normalise_text(verification_notes),
        rejection_reason=_normalise_text(rejection_reason),
        uploaded_by_user_id=uploaded_by_user_id,
        uploaded_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(document)
    _commit(commit)
    return document


def get_booking_document(document_id):
    return _get_document(document_id)


def get_booking_documents(booking_id, active_only=True):
    """
    Retrieve documents for a booking.

    The model has no active flag. For backwards compatibility, active_only
    excludes documents whose status is archived.
    """
    query = BookingDocument.query.filter_by(booking_id=booking_id)

    if active_only:
        query = query.filter(BookingDocument.status != "archived")

    return query.order_by(
        BookingDocument.created_at.desc(),
        BookingDocument.id.desc(),
    ).all()


def get_all_booking_documents(
    booking_id=None,
    status=None,
    document_type=None,
    verification_status=None,
    search=None,
):
    query = BookingDocument.query

    if booking_id is not None:
        query = query.filter_by(booking_id=booking_id)

    if status:
        query = query.filter_by(status=status)

    if document_type:
        query = query.filter_by(document_type=document_type)

    if verification_status:
        query = query.filter_by(
            verification_status=verification_status
        )

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            db.or_(
                BookingDocument.title.ilike(term),
                BookingDocument.original_filename.ilike(term),
                BookingDocument.document_type.ilike(term),
            )
        )

    return query.order_by(
        BookingDocument.created_at.desc(),
        BookingDocument.id.desc(),
    ).all()


def get_documents_by_type(booking_id, document_type, active_only=True):
    query = BookingDocument.query.filter_by(
        booking_id=booking_id,
        document_type=document_type,
    )

    if active_only:
        query = query.filter(BookingDocument.status != "archived")

    return query.order_by(BookingDocument.created_at.desc()).all()


def get_required_documents(booking_id, active_only=True):
    """
    The current model has no required flag.
    This function therefore returns no records until a required-document
    requirement is represented explicitly in the model.
    """
    return []


def get_customer_visible_documents(booking_id):
    """
    Customer visibility is not represented by the current model.
    Do not expose documents through this function until a visibility policy
    is added and enforced by an authenticated customer-facing route.
    """
    return []


def update_booking_document(document_id, commit=True, **updates):
    document = _get_document(document_id)
    if document is None:
        return None

    unknown = set(updates) - EDITABLE_FIELDS
    if unknown:
        raise ValueError(
            "Unsupported document fields: " + ", ".join(sorted(unknown))
        )

    merged = {
        "booking_id": document.booking_id,
        "title": updates.get("title", document.title),
        "document_type": updates.get(
            "document_type", document.document_type
        ),
        "original_filename": updates.get(
            "original_filename", document.original_filename
        ),
        "storage_key": document.storage_key,
        "traveller_id": updates.get(
            "traveller_id", document.traveller_id
        ),
        "file_size_bytes": updates.get(
            "file_size_bytes", document.file_size_bytes
        ),
        "issued_at": updates.get("issued_at", document.issued_at),
        "expires_at": updates.get("expires_at", document.expires_at),
        "verification_status": updates.get(
            "verification_status", document.verification_status
        ),
        "status": updates.get("status", document.status),
    }

    _validate_document_data(**merged)

    for field, value in updates.items():
        if field in {
            "title",
            "document_type",
            "original_filename",
            "description",
            "mime_type",
            "checksum_sha256",
            "issuing_country",
            "verification_notes",
            "rejection_reason",
        }:
            value = _normalise_text(value)

        if field == "file_size_bytes" and value is not None:
            value = int(value)

        setattr(document, field, value)

    document.updated_at = datetime.utcnow()
    _commit(commit)
    return document


def verify_booking_document(
    document_id,
    verified_by_user_id,
    notes=None,
    commit=True,
):
    document = _get_document(document_id)
    if document is None:
        return None

    document.verification_status = "verified"
    document.verified_by_user_id = verified_by_user_id
    document.verified_at = datetime.utcnow()
    document.verification_notes = _normalise_text(notes)
    document.rejection_reason = None
    document.status = "approved"
    document.updated_at = datetime.utcnow()

    _commit(commit)
    return document


def reject_booking_document(
    document_id,
    verified_by_user_id,
    reason,
    commit=True,
):
    document = _get_document(document_id)
    if document is None:
        return None

    reason = _normalise_text(reason)
    if not reason:
        raise ValueError("A rejection reason is required.")

    document.verification_status = "rejected"
    document.verified_by_user_id = verified_by_user_id
    document.verified_at = datetime.utcnow()
    document.rejection_reason = reason
    document.status = "rejected"
    document.updated_at = datetime.utcnow()

    _commit(commit)
    return document


def unverify_booking_document(document_id, commit=True):
    document = _get_document(document_id)
    if document is None:
        return None

    document.verification_status = "pending"
    document.verified_by_user_id = None
    document.verified_at = None
    document.verification_notes = None
    document.rejection_reason = None
    document.status = "under_review"
    document.updated_at = datetime.utcnow()

    _commit(commit)
    return document


def mark_document_required(document_id):
    raise NotImplementedError(
        "The current BookingDocument model has no required field."
    )


def mark_document_optional(document_id):
    raise NotImplementedError(
        "The current BookingDocument model has no required field."
    )


def set_customer_visibility(document_id, visible):
    raise NotImplementedError(
        "The current BookingDocument model has no customer visibility field."
    )


def get_expired_documents(booking_id=None):
    today = date.today()
    query = BookingDocument.query.filter(
        BookingDocument.expires_at.isnot(None),
        BookingDocument.expires_at < today,
        BookingDocument.status != "archived",
    )

    if booking_id is not None:
        query = query.filter_by(booking_id=booking_id)

    return query.order_by(BookingDocument.expires_at.asc()).all()


def get_documents_needing_attention(booking_id=None):
    query = BookingDocument.query.filter(
        BookingDocument.status != "archived",
        db.or_(
            BookingDocument.verification_status.in_(["pending", "rejected"]),
            db.and_(
                BookingDocument.expires_at.isnot(None),
                BookingDocument.expires_at < date.today(),
            ),
        ),
    )

    if booking_id is not None:
        query = query.filter_by(booking_id=booking_id)

    return query.order_by(BookingDocument.created_at.desc()).all()


def deactivate_booking_document(document_id, commit=True):
    """Soft-deactivate by archiving; the model has no active flag."""
    document = _get_document(document_id)
    if document is None:
        return None

    document.status = "archived"
    document.updated_at = datetime.utcnow()
    _commit(commit)
    return document


def reactivate_booking_document(document_id, commit=True):
    document = _get_document(document_id)
    if document is None:
        return None

    if document.status != "archived":
        return document

    document.status = (
        "approved"
        if document.verification_status == "verified"
        else "uploaded"
    )
    document.updated_at = datetime.utcnow()
    _commit(commit)
    return document


def delete_booking_document(document_id, commit=True):
    """
    Delete database metadata only.

    This function deliberately does not delete the underlying private file.
    The storage provider should handle file deletion separately.
    """
    document = _get_document(document_id)
    if document is None:
        return False

    db.session.delete(document)
    _commit(commit)
    return True


def get_document_status_summary(booking_id):
    documents = get_booking_documents(booking_id, active_only=True)
    total = len(documents)
    verified = sum(
        1 for document in documents
        if document.verification_status == "verified"
    )
    rejected = sum(
        1 for document in documents
        if document.verification_status == "rejected"
    )
    expired = sum(1 for document in documents if document.is_expired)
    needing_attention = sum(
        1 for document in documents
        if (
            document.verification_status in {"pending", "rejected"}
            or document.is_expired
        )
    )

    return {
        "total": total,
        "verified": verified,
        "unverified": total - verified,
        "rejected": rejected,
        "expired": expired,
        "needing_attention": needing_attention,
        "archived": BookingDocument.query.filter_by(
            booking_id=booking_id,
            status="archived",
        ).count(),
    }