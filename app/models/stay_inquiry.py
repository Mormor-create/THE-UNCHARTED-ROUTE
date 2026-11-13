"""
===============================================================================
The Uncharted Route
Stay Inquiry Model
===============================================================================

Stores public accommodation inquiries separately from confirmed stay booking.

An inquiry does not reserve a room or reduce room availability.

The selected room, when provided, is carried through room_id. A null room_id
means the guest is inquiring about the stay generally and is open to any
suitable room.
===============================================================================
"""

from datetime import datetime
from extensions import db

class StayInquiry(db.Model):
    """Represents a guest's inquiry about accommodation."""

    __tablename__ = "stay_inquiries"

    id = db.Column(db.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    # Property and optional room selection
    # -------------------------------------------------------------------------

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey("stays.id"),
        nullable=False,
        index=True,
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("stay_rooms.id"),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Guest contact information
    # -------------------------------------------------------------------------

    full_name = db.Column(
        db.String(150),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        index=True,
    )

    phone = db.Column(
        db.String(50),
    )

    country = db.Column(
        db.String(100),
    )

    # -------------------------------------------------------------------------
    # Requested stay details
    # -------------------------------------------------------------------------

    check_in = db.Column(
        db.Date,
        nullable=False,
    )

    check_out = db.Column(
        db.Date,
        nullable=False,
    )

    adults = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    children = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    preferred_currency = db.Column(
        db.String(10),
        nullable=False,
        default="KES",
    )

    special_requests = db.Column(
        db.Text,
    )

    # -------------------------------------------------------------------------
    # Inquiry tracking
    # -------------------------------------------------------------------------

    status = db.Column(
        db.String(30),
        nullable=False,
        default="New",
        index=True,
    )

    source = db.Column(
        db.String(50),
        nullable=False,
        default="Website",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    is_archived = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
        index=True,
    )

    def __repr__(self):
        return (
            f"<StayInquiry {self.id} - "
            f"Stay {self.stay_id} - {self.status}>"
        )