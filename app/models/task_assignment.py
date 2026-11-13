"""
===============================================================================
The Uncharted Route
Task Assignment Model
===============================================================================

Connects staff members to operational tasks independently of booking
assignments.
"""

from datetime import datetime
from extensions import db

TASK_ASSIGNMENT_STATUSES = {
    "Assigned",
    "Accepted",
    "Declined",
    "In Progress",
    "Completed",
    "Cancelled",}

class TaskAssignment(db.Model):
    """A staff member's responsibility for an operational task."""
    __tablename__ = "task_assignments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    role = db.Column(
        db.String(100), nullable=False, default="Responsible"
    )
    status = db.Column(
        db.String(30), nullable=False, default="Assigned", index=True
    )

    assigned_by_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    assigned_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    responded_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    notes = db.Column(db.Text)

    task = db.relationship("Task", back_populates="assignments")
    staff = db.relationship("Staff", back_populates="task_assignments")
    assigned_by = db.relationship(
        "User", foreign_keys=[assigned_by_user_id]
    )

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return (
            f"<TaskAssignment task={self.task_id} "
            f"staff={self.staff_id} status={self.status!r}>")