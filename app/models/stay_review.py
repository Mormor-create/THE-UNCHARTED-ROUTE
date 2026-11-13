"""
===============================================================================
The Uncharted Route
Stay Review Model
===============================================================================

Represents a guest review of a Stay.

Stay reviews are intentionally separate from Experience reviews because the
accommodation experience and the travel experience are different products.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Stay Review Model
# =============================================================================

class StayReview(db.Model):
    """
    Represents a review of an accommodation property.
    """

    __tablename__ = "stay_reviews"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Relationship
    # =========================================================================

    stay_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stays.id"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Guest Information
    # =========================================================================

    guest_name = db.Column(
        db.String(150),
        nullable=False
    )

    guest_email = db.Column(
        db.String(255)
    )

    # =========================================================================
    # Review
    # =========================================================================

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(200)
    )

    review = db.Column(
        db.Text,
        nullable=False
    )

    # =========================================================================
    # Stay Details
    # =========================================================================

    room_name = db.Column(
        db.String(200)
    )

    stay_date = db.Column(
        db.Date
    )

    # =========================================================================
    # Moderation
    # =========================================================================

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    # pending
    # approved
    # rejected
    # hidden

    verified_stay = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # =========================================================================
    # Management Notes
    # =========================================================================

    admin_response = db.Column(
        db.Text
    )

    # =========================================================================
    # Relationship
    # =========================================================================

    stay = db.relationship(
        "Stay",
        back_populates="reviews"
    )

    # =========================================================================
    # Audit Fields
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_approved(self):
        return self.status == "approved"

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<StayReview "
            f"stay={self.stay_id} "
            f"rating={self.rating}>"
        )