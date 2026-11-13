"""
===============================================================================
The Uncharted Route
Cancellation Policy Model
===============================================================================
Reusable cancellation and refund policies.

Each experiences references one policy rather than storing
duplicate cancellation information.

Examples

• Flexible
• Standard
• Luxury
• Corporate
• Promotional
"""
from datetime import datetime
from extensions import db

# =============================================================================
# Cancellation Policy Model
# =============================================================================
class CancellationPolicy(db.Model):
    """
    Reusable cancellation policy.
    """

    __tablename__ = "cancellation_policies"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        index=True
    )

    short_description = db.Column(
        db.String(255)
    )

    full_policy = db.Column(
        db.Text,
        nullable=False
    )

    # =========================================================================
    # Refund Rules
    # =========================================================================

    full_refund_days = db.Column(
        db.Integer,
        default=30
    )

    partial_refund_days = db.Column(
        db.Integer,
        default=14
    )

    partial_refund_percentage = db.Column(
        db.Integer,
        default=50
    )

    no_refund_days = db.Column(
        db.Integer,
        default=7
    )

    # =========================================================================
    # Booking Changes
    # =========================================================================

    date_changes_allowed = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    name_changes_allowed = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    transferable_booking = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # =========================================================================
    # Additional Information
    # =========================================================================

    notes = db.Column(
        db.Text
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    default_policy = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experiences = db.relationship(
        "Experience",
        back_populates="cancellation_policy",
        lazy="dynamic"
    )

    stays = db.relationship(
        "Stay",
        back_populates="cancellation_policy",
        lazy="dynamic"
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
    def experience_count(self):
        return self.experiences.count()

    @property
    def has_partial_refund(self):
        return self.partial_refund_percentage > 0

    @property
    def stay_count(self):
        return self.stays.count()

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<CancellationPolicy {self.name}>")