"""
===============================================================================
The Uncharted Route
Staff Availability Model
===============================================================================

Records availability windows, leave, and other unavailability periods.
"""

from datetime import datetime

from extensions import db

STAFF_AVAILABILITY_STATUSES = {
    "Available",
    "Unavailable",
    "On Leave",
    "Pending Approval",
    "Approved",
    "Rejected",}

class StaffAvailability(db.Model):
    """An availability or unavailability window for a staff member."""

    __tablename__ = "staff_availability"

    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)

    status = db.Column(db.String(30), nullable=False, default="Available", index=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    ends_at = db.Column(db.DateTime, nullable=False, index=True)

    # For leave requests or availability entered by the staff member.
    reason = db.Column(db.String(255))
    notes = db.Column(db.Text)

    all_day = db.Column(db.Boolean, nullable=False, default=False)
    recurring = db.Column(db.Boolean, nullable=False, default=False)
    recurrence_rule = db.Column(db.String(255))

    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)

    staff = db.relationship("Staff", back_populates="availability_records")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_user_id])

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,)

    @property
    def duration_seconds(self):
        if self.starts_at is None or self.ends_at is None:
            return 0
        return max(0, int((self.ends_at - self.starts_at).total_seconds()))

    def __repr__(self):
        return (
            f"<StaffAvailability staff={self.staff_id} "
            f"{self.status} {self.starts_at}>")