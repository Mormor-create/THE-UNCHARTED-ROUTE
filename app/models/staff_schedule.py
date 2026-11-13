"""
===============================================================================
The Uncharted Route
Staff Schedule Model
===============================================================================
Represents planned shifts and duty periods for operational staff.
"""

from datetime import datetime
from extensions import db

STAFF_SCHEDULE_STATUSES = {
    "Scheduled",
    "Confirmed",
    "In Progress",
    "Completed",
    "Cancelled",}

class StaffSchedule(db.Model):
    """A planned shift or duty period for a staff member."""
    __tablename__ = "staff_schedules"
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    schedule_type = db.Column(
        db.String(40), nullable=False, default="shift")
    status = db.Column(
        db.String(30), nullable=False, default="Scheduled", index=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    ends_at = db.Column(db.DateTime, nullable=False, index=True)
    location = db.Column(db.String(255))
    timezone = db.Column(db.String(64), default="Africa/Nairobi")

    # Optional link to an operational task
    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id", ondelete="SET NULL"),
        index=True,)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    confirmed_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    staff = db.relationship("Staff", back_populates="schedules")
    task = db.relationship("Task", back_populates="staff_schedules")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])

    assignments = db.relationship(
        "StaffAssignment",
        back_populates="staff_schedule",
        lazy="select",)

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
            f"<StaffSchedule staff={self.staff_id} "
            f"title={self.title!r}>")