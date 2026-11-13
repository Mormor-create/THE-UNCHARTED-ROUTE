"""
===============================================================================
The Uncharted Route
Experience Review Model
===============================================================================

Stores customer reviews for completed experiences.

Only guests who completed an experiences should be eligible
to leave verified reviews.

Supports:

• Overall Rating
• Guide Rating
• Transportation Rating
• Accommodation Rating
• Value Rating
• Organization Rating
• Featured Reviews
• Admin Responses
• Moderation
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Review Model
# =============================================================================

class ExperienceReview(db.Model):
    """
    Customer reviews for experiences.
    """

    __tablename__ = "experience_reviews"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experiences.id"),
        nullable=False,
        index=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        index=True
    )

    # =========================================================================
    # Reviewer Information
    # =========================================================================

    reviewer_name = db.Column(
        db.String(150),
        nullable=False
    )

    reviewer_email = db.Column(
        db.String(255)
    )

    reviewer_country = db.Column(
        db.String(100)
    )

    # =========================================================================
    # Ratings
    # =========================================================================

    overall_rating = db.Column(
        db.Integer,
        nullable=False
    )

    guide_rating = db.Column(
        db.Integer
    )

    transportation_rating = db.Column(
        db.Integer
    )

    accommodation_rating = db.Column(
        db.Integer
    )

    value_rating = db.Column(
        db.Integer
    )

    organization_rating = db.Column(
        db.Integer
    )

    # =========================================================================
    # Review Content
    # =========================================================================

    title = db.Column(
        db.String(255)
    )

    review = db.Column(
        db.Text,
        nullable=False
    )

    pros = db.Column(
        db.Text
    )

    cons = db.Column(
        db.Text
    )

    travel_date = db.Column(
        db.Date
    )

    # =========================================================================
    # Recommendation
    # =========================================================================

    would_recommend = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =========================================================================
    # Verification
    # =========================================================================

    verified_booking = db.Column(
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
    # Moderation
    # =========================================================================

    approved = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    rejected = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    rejection_reason = db.Column(
        db.Text
    )

    # =========================================================================
    # Admin Response
    # =========================================================================

    admin_response = db.Column(
        db.Text
    )

    admin_responded_by = db.Column(
        db.String(150)
    )

    admin_responded_at = db.Column(
        db.DateTime
    )

    # =========================================================================
    # Engagement
    # =========================================================================

    helpful_votes = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    report_count = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experiences = db.relationship(
        "Experience",
        back_populates="reviews"
    )

    booking = db.relationship(
        "Booking",
        back_populates="reviews"
    )

    reviewer = db.relationship(
        "User"
    )

    # =========================================================================
    # Audit
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
    # Helper Properties
    # =========================================================================

    @property
    def average_category_rating(self):
        ratings = [
            self.guide_rating,
            self.transportation_rating,
            self.accommodation_rating,
            self.value_rating,
            self.organization_rating,
        ]

        ratings = [r for r in ratings if r is not None]

        if not ratings:
            return self.overall_rating

        return round(sum(ratings) / len(ratings), 1)

    @property
    def is_public(self):
        return self.approved and not self.rejected

    @property
    def has_admin_response(self):
        return self.admin_response is not None

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ExperienceReview {self.reviewer_name}>"
        )