"""
===============================================================================
The Uncharted Route
Booking Note Model
===============================================================================

Stores customer communications and operational timeline entries for booking.
Entries can be internal or customer-visible.
"""

from datetime import datetime
from extensions import db

class BookingNote(db.Model):
    """A timeline entry associated with a central booking."""

    __tablename__ = "booking_notes"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)

    # Entry classification
    note_type = db.Column(
        db.String(40), nullable=False, default="internal_note", index=True
    )
    visibility = db.Column(
        db.String(20), nullable=False, default="internal", index=True
    )
    title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)

    # Optional communication metadata
    communication_channel = db.Column(db.String(30))
    direction = db.Column(db.String(20))
    recipient = db.Column(db.String(255))
    subject = db.Column(db.String(255))

    # Optional external reference, e.g. email or gateway message ID
    external_reference = db.Column(db.String(255), index=True)

    # Structured context for system-generated events
    event_data = db.Column(db.JSON)

    # Author / actor
    author_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    author_name_snapshot = db.Column(db.String(200))
    author_role_snapshot = db.Column(db.String(100))

    # Customer-visible delivery tracking, where applicable
    delivery_status = db.Column(db.String(30))
    delivered_at = db.Column(db.DateTime)
    delivery_error = db.Column(db.Text)

    # Relationships
    booking = db.relationship(
        "Booking", back_populates="notes"
    )
    author = db.relationship(
        "User", foreign_keys=[author_user_id]
    )

    # Timeline ordering
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    def __repr__(self):
        return (
            f"<BookingNote booking_id={self.booking_id} "
            f"type={self.note_type!r}>"
        )
