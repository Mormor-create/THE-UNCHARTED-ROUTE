
"""
===============================================================================
The Uncharted Route
Task Model
===============================================================================

Generic operational tasks that may be associated with a booking or request,
or exist independently.
"""

from datetime import datetime

from extensions import db


TASK_STATUSES = {
    "Open",
    "In Progress",
    "Blocked",
    "Completed",
    "Cancelled",
}

TASK_PRIORITIES = {
    "Low",
    "Normal",
    "High",
    "Urgent",
}


class Task(db.Model):
    """A unit of operational work."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    task_reference = db.Column(
        db.String(50), unique=True, nullable=False, index=True
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    task_type = db.Column(
        db.String(50), nullable=False, default="general", index=True
    )
    status = db.Column(
        db.String(30), nullable=False, default="Open", index=True
    )
    priority = db.Column(
        db.String(20), nullable=False, default="Normal", index=True
    )

    # All links are optional: a task can exist without a booking.
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="SET NULL"),
        index=True,
    )
    booking_request_id = db.Column(
        db.Integer,
        db.ForeignKey("booking_requests.id", ondelete="SET NULL"),
        index=True,
    )

    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    owner_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    due_at = db.Column(db.DateTime, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    completion_notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    # Relationships
    booking = db.relationship("Booking", back_populates="tasks")
    booking_request = db.relationship("BookingRequest")
    created_by = db.relationship(
        "User", foreign_keys=[created_by_user_id]
    )
    owner = db.relationship(
        "User", foreign_keys=[owner_user_id]
    )

    assignments = db.relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    staff_schedules = db.relationship(
        "StaffSchedule",
        back_populates="task",
        lazy="select",
    )

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return f"<Task {self.task_reference} ({self.status})>"