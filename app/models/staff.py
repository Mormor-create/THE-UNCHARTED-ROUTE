"""
===============================================================================
The Uncharted Route
Staff Model
===============================================================================

Employee and contractor profiles for operational staff.

Authentication and application permissions remain on User.
Existing staff information is retained while supporting the central
booking, availability, scheduling, and task-assignment architecture.
"""

from datetime import datetime
from secrets import token_hex
from sqlalchemy import event
from extensions import db

# =============================================================================
# Supported Staff Values
# =============================================================================
STAFF_TYPES = {
    "Consultant",
    "Guide",
    "Driver",
    "Operations",
    "Administrator",
    "Other",}

STAFF_STATUSES = {
    "Active",
    "Inactive",
    "On Leave",
    "Suspended",}

EMPLOYMENT_TYPES = {
    "Full-time",
    "Part-time",
    "Contract",
    "Casual",
    "Intern",
    "Volunteer",
    "Freelance",}

# =============================================================================
# Staff Model
# =============================================================================
class Staff(db.Model):
    """Operational staff profile associated with a user account."""

    __tablename__ = "staff"

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,)
    employee_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
        index=True,)

    # -------------------------------------------------------------------------
    # Employment Information
    # -------------------------------------------------------------------------
    staff_type = db.Column(
        db.String(50),
        nullable=False,
        default="Other",
        index=True,)
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(150))
    employment_type = db.Column(
        db.String(50),
        nullable=False,
        default="Full-time",)
    status = db.Column(
        db.String(50),
        nullable=False,
        default="Active",
        index=True,)
    hire_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # -------------------------------------------------------------------------
    # Contact Information
    # -------------------------------------------------------------------------
    phone = db.Column(db.String(50))
    work_email = db.Column(db.String(255))
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(50))
    emergency_contact_relationship = db.Column(db.String(100))

    # -------------------------------------------------------------------------
    # Skills, Qualifications, and Credentials
    #
    # These remain Text columns to match the existing database.
    # Do not change them to JSON until the existing stored values have been
    # inspected and a safe data conversion has been prepared.
    # -------------------------------------------------------------------------
    skills = db.Column(db.Text)
    qualifications = db.Column(db.Text)
    certifications = db.Column(db.Text)
    languages = db.Column(db.Text)
    licence_details = db.Column(db.JSON)

    # -------------------------------------------------------------------------
    # Operational Limits
    # -------------------------------------------------------------------------
    maximum_daily_assignments = db.Column(db.Integer)
    can_accept_assignments = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),)
    assignments_completed = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0",)
    assignments_cancelled = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0",)
    rating = db.Column(db.Numeric(3, 2))

    # -------------------------------------------------------------------------
    # Notes
    #
    # Both fields are retained because general notes and internal notes may
    # have different purposes in the existing application.
    # -------------------------------------------------------------------------
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)

    # -------------------------------------------------------------------------
    # Audit Timestamps
    # -------------------------------------------------------------------------
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.current_timestamp(),)

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=db.func.current_timestamp(),)

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------
    user = db.relationship(
        "User",
        back_populates="staff_profile",)

    assignments = db.relationship(
        "StaffAssignment",
        back_populates="staff",
        lazy="select",)

    availability_records = db.relationship(
        "StaffAvailability",
        back_populates="staff",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StaffAvailability.starts_at",)

    schedules = db.relationship(
        "StaffSchedule",
        back_populates="staff",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StaffSchedule.starts_at",)

    task_assignments = db.relationship(
        "TaskAssignment",
        back_populates="staff",
        lazy="select",)

    # -------------------------------------------------------------------------
    # Display Properties
    # -------------------------------------------------------------------------
    @property
    def display_name(self):
        """Return the user's name, falling back to the employee number."""

        if self.user is not None:
            name = " ".join(
                part
                for part in (
                    getattr(self.user, "first_name", None),
                    getattr(self.user, "last_name", None),
                )
                if part
            ).strip()

            if name:
                return name

        return self.employee_number

    @property
    def is_active(self):
        """Whether this staff profile is active."""

        return self.status == "Active"

    def __repr__(self):
        return (
            f"<Staff {self.employee_number or 'Unassigned'} "
            f"({self.staff_type})>"
        )

# =============================================================================
# Automatic Employee Number Generation
# =============================================================================
@event.listens_for(Staff, "before_insert")
def generate_employee_number(mapper, connection, staff):
    """
    Generate a unique employee number for new staff profiles.
    Format:
        TUR-EMP-XXXXXXXXXX
    The suffix contains 10 uppercase hexadecimal characters, matching the
    token-generation approach used by the Safari inquiry service.

    Existing employee numbers are never overwritten.
    """

    if staff.employee_number and staff.employee_number.strip():
        return

    staff.employee_number = f"TUR-EMP-{token_hex(5).upper()}"