"""
===============================================================================
The Uncharted Route
Staff Assignment Model
===============================================================================

Assigns one staff member to one central booking in a specific operational role.
"""

from datetime import datetime
from extensions import db

STAFF_ASSIGNMENT_ROLES = {
    "Consultant",
    "Guide",
    "Driver",
    "Coordinator",
    "Photographer",
    "Other",}

STAFF_ASSIGNMENT_STATUSES = {
    "Assigned",
    "Accepted",
    "Declined",
    "In Progress",
    "Completed",
    "Cancelled",}

class StaffAssignment(db.Model):
    """An individual staff member's assignment to a booking."""

    __tablename__ = "staff_assignments"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)
    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,)

    role = db.Column(
        db.String(40), nullable=False, default="Other", index=True)
    status = db.Column(
        db.String(30), nullable=False, default="Assigned", index=True)

    # Assignment timing can differ from the overall booking dates.
    starts_at = db.Column(db.DateTime, index=True)
    ends_at = db.Column(db.DateTime)
    assigned_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    response_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)

    # Optional operational links
    staff_schedule_id = db.Column(
        db.Integer,
        db.ForeignKey("staff_schedules.id", ondelete="SET NULL"),
        index=True,)
    booking = db.relationship("Booking", back_populates="staff_assignments")
    staff = db.relationship("Staff", back_populates="assignments")
    assigned_by = db.relationship("User", foreign_keys=[assigned_by_user_id])
    staff_schedule = db.relationship(
        "StaffSchedule", back_populates="assignments")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,)

    @property
    def is_active(self):
        return self.status in {"Assigned", "Accepted", "In Progress"}

    def __repr__(self):
        return (
            f"<StaffAssignment booking={self.booking_id} "
            f"staff={self.staff_id} role={self.role!r}>")