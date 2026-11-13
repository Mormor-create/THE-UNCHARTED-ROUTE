"""
===============================================================================
The Uncharted Route
Booking Document Model
===============================================================================

Tracks documents associated with a booking and, optionally, a specific
traveller. Files should be stored privately, outside public static directories.
"""

from datetime import datetime

from extensions import db

class BookingDocument(db.Model):
    """A private document associated with a booking or traveller."""

    __tablename__ = "booking_documents"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    traveller_id = db.Column(
        db.Integer,
        db.ForeignKey("booking_travellers.id", ondelete="CASCADE"),
        index=True,
    )

    # Document classification
    document_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(
        db.String(30), nullable=False, default="uploaded", index=True
    )

    # Private storage metadata — never expose storage_key as a public URL.
    original_filename = db.Column(db.String(255), nullable=False)
    storage_key = db.Column(db.String(500), nullable=False, unique=True)
    mime_type = db.Column(db.String(150))
    file_size_bytes = db.Column(db.BigInteger)
    checksum_sha256 = db.Column(db.String(64))

    # Issuing / expiry information, where relevant
    issuing_country = db.Column(db.String(100))
    issued_at = db.Column(db.Date)
    expires_at = db.Column(db.Date, index=True)

    # Verification
    verification_status = db.Column(
        db.String(20), nullable=False, default="pending", index=True
    )
    verified_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    verified_at = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)

    # Upload ownership
    uploaded_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    uploaded_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    booking = db.relationship(
        "Booking", back_populates="documents"
    )
    traveller = db.relationship(
        "BookingTraveller",
        back_populates="documents",
        foreign_keys=[traveller_id],
    )
    verified_by = db.relationship(
        "User", foreign_keys=[verified_by_user_id]
    )
    uploaded_by = db.relationship(
        "User", foreign_keys=[uploaded_by_user_id])

    # Audit
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,)

    @property
    def is_verified(self):
        return self.verification_status == "verified"

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        from datetime import date
        return self.expires_at < date.today()

    def __repr__(self):
        return (
            f"<BookingDocument {self.title!r} "
            f"booking_id={self.booking_id}>"
        )