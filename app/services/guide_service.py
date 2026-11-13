"""
===============================================================================
The Uncharted Route
Guide Service
===============================================================================
Central business-logic layer for Guide Dashboard operations.
Guide operations are built on top of the existing Staff architecture.
Architecture
------------
    Guide Admin Route
            ↓
      Guide Service
            ↓
      Staff Service
            ↓
       Staff Models
            ↓
         Database

Guide Model Strategy
--------------------
A Guide is an internal User with an associated Staff profile.
Therefore, this service does NOT introduce a separate Guide model.
Guide-related operational records use:

    User
    Staff
    StaffAvailability
    StaffSchedule
    StaffAssignment
    Booking
    Experience
    ExperienceReview

Responsibilities
----------------
• Retrieve guide profiles
• List and search guides
• Retrieve guide dashboard data
• Retrieve guide booking
• Retrieve guide assignments
• Manage guide schedules
• Manage guide availability
• Accept / decline assignments
• Start / complete assignments
• Calculate guide performance
• Calculate guide dashboard statistics
• Retrieve upcoming guide activities
• Retrieve current guide activities
• Retrieve completed guide activities
Authentication remains the responsibility of Flask-Login/User.
Guide operational business logic belongs here rather than in routes.
"""

from datetime import datetime
from sqlalchemy import or_
from extensions import db
from app.models import (
    User,
    Staff,
    StaffAvailability,
    StaffSchedule,
    StaffAssignment,
    Booking,
    Experience,)
from app.models.staff import (
    STAFF_TYPES,
    STAFF_STATUSES,)
from app.models.staff_availability import (
    STAFF_AVAILABILITY_STATUSES,)
from app.models.staff_schedule import (
    STAFF_SCHEDULE_STATUSES,)
from app.models.staff_assignment import (
    STAFF_ASSIGNMENT_ROLES,
    STAFF_ASSIGNMENT_STATUSES,)
from app.services import staff_service

# =============================================================================
# Constants
# =============================================================================
GUIDE_STAFF_TYPE = "Guide"
ACTIVE_ASSIGNMENT_STATUSES = {
    "Assigned",
    "Accepted",
    "In Progress",}
COMPLETED_ASSIGNMENT_STATUSES = {"Completed",}
INACTIVE_ASSIGNMENT_STATUSES = {"Cancelled","Declined",}

# =============================================================================
# Exceptions
# =============================================================================
class GuideServiceError(ValueError):
    """
    Base exception raised by the Guide Service.
    """
# =============================================================================
# Internal Helpers
# =============================================================================
def _normalize(value):
    """
    Safely normalize a string value.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _require_guide(guide):
    """
    Ensure a valid Guide Staff profile was supplied.
    """
    if guide is None:
        raise GuideServiceError(
            "Guide record not found."
        )

    if guide.staff_type != GUIDE_STAFF_TYPE:
        raise GuideServiceError(
            "The selected Staff member is not a guide."
        )
    return guide

def _require_booking(booking):
    """
    Ensure a Booking exists.
    """
    if booking is None:
        raise GuideServiceError(
            "Booking not found.")
    return booking

def _require_assignment(assignment):
    """
    Ensure a StaffAssignment exists.
    """
    if assignment is None:
        raise GuideServiceError(
            "Guide assignment not found."
        )
    return assignment

def _is_guide_staff(staff):
    """Determine whether a Staff profile represents a Guide."""
    return (
        staff is not None
        and staff.staff_type == GUIDE_STAFF_TYPE)

# =============================================================================
# Guide Retrieval
# =============================================================================
def get_guide(guide_id):
    """Retrieve a Guide Staff profile by its Staff primary key."""
    if not guide_id:
        return None

    guide = db.session.get(Staff, guide_id)
    if not _is_guide_staff(guide):
        return None

    return guide


def get_guide_by_id(guide_id):
    """Retrieve a Guide Staff profile by its Staff primary key."""
    return get_guide(guide_id)


def get_guide_by_user(user):
    """Retrieve the Guide Staff profile linked to a User account."""
    if user is None or not getattr(user, "id", None):
        return None

    return Staff.query.filter_by(
        user_id=user.id,
        staff_type=GUIDE_STAFF_TYPE,
    ).first()


def get_guide_by_user_id(user_id):
    """Retrieve a Guide Staff profile by its linked User ID."""
    if not user_id:
        return None

    return Staff.query.filter_by(
        user_id=user_id,
        staff_type=GUIDE_STAFF_TYPE,
    ).first()


def get_guide_by_employee_number(employee_number):
    """Retrieve a Guide by employee number."""
    employee_number = _normalize(employee_number)

    if not employee_number:
        return None

    return Staff.query.filter(
        Staff.employee_number.ilike(employee_number),
        Staff.staff_type == GUIDE_STAFF_TYPE,
    ).first()

# =============================================================================
# Guide Catalogue
# =============================================================================
def list_guides(
    search=None,
    department=None,
    status=None,
    active_only=False,
):
    """
    Return Guide Staff records using administrative filters.

    Search covers:

        • Employee number
        • Job title
        • Department
        • First name
        • Last name
        • Username
        • Email
    """

    query = (
        Staff.query
        .join(User)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE))
    search = _normalize(search)

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Staff.employee_number.ilike(
                    search_term
                ),
                Staff.job_title.ilike(
                    search_term
                ),
                Staff.department.ilike(
                    search_term
                ),
                User.first_name.ilike(
                    search_term
                ),
                User.last_name.ilike(
                    search_term
                ),
                User.username.ilike(
                    search_term
                ),
                User.email.ilike(
                    search_term
                ),
            )
        )

    if department:
        query = query.filter(
            Staff.department == department
        )

    if status:
        query = query.filter(
            Staff.status == status
        )

    if active_only:
        query = query.filter(
            Staff.status == "Active"
        )

    return (
        query
        .order_by(
            User.first_name.asc(),
            User.last_name.asc(),
        )
        .all()
    )

# =============================================================================
# Update Guide Profile
# =============================================================================
def update_guide_profile(guide, data):
    """
    Update an existing Guide's operational profile.
    The linked User account is deliberately not modified here.
    """
    from sqlalchemy.exc import IntegrityError
    _require_guide(guide)
    employee_number = (
        (data.get("employee_number") or "").strip() or None
    )

    # A guide profile must remain a Guide profile.
    if data.get("staff_type") != GUIDE_STAFF_TYPE:
        raise GuideServiceError(
            "The staff type must remain Guide when editing a guide profile.")

    # Check for duplicate employee numbers before updating.
    if employee_number:
        duplicate = Staff.query.filter(
            Staff.employee_number == employee_number,
            Staff.id != guide.id,
        ).first()

        if duplicate:
            raise GuideServiceError(
                "That employee number is already assigned to another staff member."
            )

    guide.employee_number = employee_number
    guide.staff_type = GUIDE_STAFF_TYPE

    guide.department = (
        (data.get("department") or "").strip() or None
    )
    guide.job_title = (
        (data.get("job_title") or "").strip() or None
    )
    guide.employment_type = data.get("employment_type")
    guide.hire_date = data.get("hire_date")
    guide.end_date = data.get("end_date")
    guide.status = data.get("status")

    guide.skills = data.get("skills") or None
    guide.languages = data.get("languages") or None
    guide.certifications = data.get("certifications") or None
    guide.qualifications = data.get("qualifications") or None

    guide.emergency_contact_name = (
        (data.get("emergency_contact_name") or "").strip() or None
    )
    guide.emergency_contact_phone = (
        (data.get("emergency_contact_phone") or "").strip() or None
    )
    guide.emergency_contact_relationship = (
        (data.get("emergency_contact_relationship") or "").strip()
        or None)
    guide.notes = data.get("notes") or None
    guide.internal_notes = data.get("internal_notes") or None

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise GuideServiceError(
            "The guide could not be updated because a record conflicts "
            "with an existing database value."
        ) from exc
    except Exception:
        db.session.rollback()
        raise
    return guide

def get_guide_members():
    """
    Return all Guide Staff members.
    Convenience alias for administrative interfaces.
    """
    return list_guides()

# =============================================================================
# Guide Validation
# =============================================================================
def ensure_guide(guide):
    """
    Validate that a Staff profile is a Guide.
    """
    return _require_guide(guide)

def ensure_guide_user(user):
    """
    Validate that a User can operate as a Guide.
    """
    if user is None:
        raise GuideServiceError(
            "User account not found."
        )
    guide = get_guide_by_user(
        user)
    if guide:
        return guide
    if not user.is_guide:
        raise GuideServiceError(
            "The selected user does not have the Guide role."
        )
    return None

# =============================================================================
# Guide Status
# =============================================================================
def update_guide_status(
    guide,
    status,):
    """
    Update the operational status of a Guide.
    """
    guide = _require_guide(guide)
    if status not in STAFF_STATUSES:
        raise GuideServiceError(
            "Invalid guide status.")
    return staff_service.update_staff_status(guide,status,)

def activate_guide(guide):
    """
    Activate a Guide.
    """
    return update_guide_status(guide,"Active",)

def deactivate_guide(guide):
    """
    Deactivate a Guide.
    """
    return update_guide_status(guide,"Inactive",)

def place_guide_on_leave(guide):
    """
    Mark a Guide as being on leave.
    """

    return update_guide_status(
        guide,
        "On Leave",
    )

# =============================================================================
# Guide Assignments
# =============================================================================
def get_assignment(assignment_id):
    """
    Retrieve a StaffAssignment.
    """

    if not assignment_id:
        return None

    return db.session.get(
        StaffAssignment,
        assignment_id,
    )


def get_guide_assignments(
    guide,
    status=None,
    role=None,
):
    """
    Retrieve assignments belonging to a Guide.
    """

    guide = _require_guide(
        guide
    )

    query = StaffAssignment.query.filter_by(
        staff_id=guide.id
    )

    if status:
        query = query.filter(
            StaffAssignment.status == status
        )

    if role:
        query = query.filter(
            StaffAssignment.role == role
        )

    return (
        query
        .order_by(
            StaffAssignment.created_at.desc()
        )
        .all()
    )


def get_active_assignments(guide):
    """
    Retrieve active Guide assignments.
    """

    guide = _require_guide(
        guide
    )

    return (
        StaffAssignment.query
        .filter(
            StaffAssignment.staff_id == guide.id,
            StaffAssignment.status.in_(
                list(ACTIVE_ASSIGNMENT_STATUSES)
            ),
        )
        .order_by(
            StaffAssignment.created_at.asc()
        )
        .all()
    )


def get_completed_assignments(guide):
    """
    Retrieve completed Guide assignments.
    """

    guide = _require_guide(
        guide
    )

    return (
        StaffAssignment.query
        .filter(
            StaffAssignment.staff_id == guide.id,
            StaffAssignment.status == "Completed",
        )
        .order_by(
            StaffAssignment.completed_at.desc()
        )
        .all()
    )


def get_pending_assignments(guide):
    """
    Retrieve assignments that still require Guide action.
    """

    guide = _require_guide(
        guide
    )

    return (
        StaffAssignment.query
        .filter(
            StaffAssignment.staff_id == guide.id,
            StaffAssignment.status == "Assigned",
        )
        .order_by(
            StaffAssignment.created_at.asc()
        )
        .all()
    )


# =============================================================================
# Assignment Actions
# =============================================================================
def accept_assignment(assignment):
    """
    Accept a Guide assignment.
    """

    assignment = _require_assignment(
        assignment
    )

    guide = get_guide(
        assignment.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    return staff_service.accept_assignment(
        assignment
    )

def decline_assignment(assignment):
    """
    Decline a Guide assignment.
    """

    assignment = _require_assignment(
        assignment
    )

    guide = get_guide(
        assignment.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    return staff_service.decline_assignment(
        assignment
    )


def start_assignment(assignment):
    """
    Start a Guide assignment.
    """

    assignment = _require_assignment(
        assignment
    )

    guide = get_guide(
        assignment.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    return staff_service.start_assignment(
        assignment
    )


def complete_assignment(assignment):
    """
    Complete a Guide assignment.
    """

    assignment = _require_assignment(
        assignment
    )

    guide = get_guide(
        assignment.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    return staff_service.complete_assignment(
        assignment
    )

def update_assignment(assignment, status=None, **updates):
    """
    Update an existing Guide assignment.

    Only explicitly supported fields are updated.
    """

    assignment = _require_assignment(assignment)

    guide = get_guide(assignment.staff_id)

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    if status is not None:
        if status not in STAFF_ASSIGNMENT_STATUSES:
            raise GuideServiceError(
                "Invalid guide assignment status."
            )

        assignment.status = status

    allowed_fields = {
        "role",
        "is_primary",
        "notes",
    }

    for field, value in updates.items():
        if field not in allowed_fields:
            raise GuideServiceError(
                f"Unsupported assignment field: {field}"
            )

        if field == "role" and value is not None:
            if value not in STAFF_ASSIGNMENT_ROLES:
                raise GuideServiceError(
                    "Invalid guide assignment role."
                )

        if hasattr(assignment, field):
            setattr(assignment, field, value)
        else:
            raise GuideServiceError(
                f"The assignment model does not support '{field}'."
            )

    if hasattr(assignment, "updated_at"):
        assignment.updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return assignment

def cancel_assignment(assignment):
    """
    Cancel a Guide assignment.
    """

    assignment = _require_assignment(
        assignment
    )

    guide = get_guide(
        assignment.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    return staff_service.cancel_assignment(
        assignment
    )

def remove_guide_assignment(assignment):
    """
    Permanently remove a Guide assignment.

    This is intended for administrative correction, not
    ordinary cancellation of a booking.
    """

    assignment = _require_assignment(assignment)

    guide = get_guide(assignment.staff_id)

    if guide is None:
        raise GuideServiceError(
            "This assignment does not belong to a Guide."
        )

    try:
        db.session.delete(assignment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return True

# =============================================================================
# Guide Bookings
# =============================================================================

def get_guide_bookings(
    guide,
    status=None,
    start_date=None,
    end_date=None,
    search=None,
):
    """
    Retrieve booking assigned to a Guide through StaffAssignment.

    Supports optional status, date-range, and search filters.
    """
    guide = _require_guide(guide)

    query = (
        Booking.query
        .join(
            StaffAssignment,
            StaffAssignment.booking_id == Booking.id,
        )
        .filter(StaffAssignment.staff_id == guide.id)
    )

    if status:
        query = query.filter(Booking.status == status)

    # Apply date filters using the existing Booking.experience_date field.
    if start_date:
        try:
            start_date = datetime.strptime(
                start_date, "%Y-%m-%d"
            ).date()
            query = query.filter(
                Booking.experience_date >= start_date
            )
        except (TypeError, ValueError):
            raise GuideServiceError(
                "Invalid start date. Use YYYY-MM-DD."
            )

    if end_date:
        try:
            end_date = datetime.strptime(
                end_date, "%Y-%m-%d"
            ).date()
            query = query.filter(
                Booking.experience_date <= end_date
            )
        except (TypeError, ValueError):
            raise GuideServiceError(
                "Invalid end date. Use YYYY-MM-DD."
            )

    # Search is accepted by the route, but its searchable fields
    # depend on the actual Booking model, so don't guess them here.

    return (
        query
        .order_by(
            Booking.experience_date.asc(),
            Booking.booking_date.desc(),
        )
        .all()
    )

def get_upcoming_bookings(guide):
    """
    Retrieve upcoming booking assigned to a Guide.
    """

    guide = _require_guide(
        guide
    )

    today = datetime.utcnow().date()

    return (
        Booking.query
        .join(
            StaffAssignment,
            StaffAssignment.booking_id == Booking.id,
        )
        .filter(
            StaffAssignment.staff_id == guide.id,
            StaffAssignment.status.in_(
                list(ACTIVE_ASSIGNMENT_STATUSES)),
            Booking.experience_date >= today,)
        .order_by(Booking.experience_date.asc())
        .all())

def get_completed_bookings(guide):
    """
    Retrieve completed booking assigned to a Guide.
    """
    guide = _require_guide(guide)
    return (
        Booking.query
        .join(
            StaffAssignment,
            StaffAssignment.booking_id == Booking.id,)
        .filter(
            StaffAssignment.staff_id == guide.id,
            Booking.status.in_(
                [
                    "Completed",
                    "Reviewed",]),).order_by(
            Booking.experience_date.desc()
        ).all())

def get_booking(booking_id):
    """Retrieve a booking by its primary key."""
    if not booking_id:
        return None
    return db.session.get(Booking, booking_id)

def get_current_bookings(guide):
    """
    Retrieve booking currently in progress.
    """

    guide = _require_guide(guide)

    return (
        Booking.query
        .join(
            StaffAssignment,
            StaffAssignment.booking_id == Booking.id,
        ).filter(
            StaffAssignment.staff_id == guide.id,
            StaffAssignment.status == "In Progress",)
        .order_by(Booking.experience_date.asc()).all())

def get_guide_booking(guide, booking_id):
    """
    Retrieve a booking assigned to a specific Guide.

    Returns None when the booking does not exist or is not
    assigned to the specified Guide.
    """

    guide = _require_guide(guide)

    if not booking_id:
        return None

    return (
        Booking.query
        .join(
            StaffAssignment,
            StaffAssignment.booking_id == Booking.id,
        )
        .filter(
            Booking.id == booking_id,
            StaffAssignment.staff_id == guide.id,
        )
        .first()
    )

def assign_guide_to_booking(
    guide,
    booking,
    role=None,
    is_primary=False,
    notes=None,
    check_availability=True,
):
    """
    Assign a Guide to a booking.

    Uses the existing StaffAssignment model and validates
    the guide, booking, role, and duplicate assignment.
    """

    guide = _require_guide(guide)
    booking = _require_booking(booking)

    if role and role not in STAFF_ASSIGNMENT_ROLES:
        raise GuideServiceError(
            "Invalid guide assignment role."
        )

    existing = StaffAssignment.query.filter_by(
        staff_id=guide.id,
        booking_id=booking.id,
    ).first()

    if existing is not None:
        raise GuideServiceError(
            "This guide is already assigned to the booking."
        )

    if check_availability:
        experience_date = getattr(
            booking,
            "experience_date",
            None,
        )

        if experience_date:
            available = is_guide_available(
                guide,
                experience_date,
            )

            if not available:
                raise GuideServiceError(
                    "The guide is not available for the booking date."
                )

    assignment = StaffAssignment(
        staff_id=guide.id,
        booking_id=booking.id,
        role=role,
        is_primary=is_primary,
        notes=notes,
        status="Assigned",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),)

    try:
        db.session.add(assignment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return assignment
# =============================================================================
# Guide Availability
# =============================================================================
def get_availability(
    availability_id,
):
    """
    Retrieve a Guide availability record.
    """
    if not availability_id:
        return None
    return db.session.get(StaffAvailability,availability_id,)

def get_guide_availability(guide, date=None):
    """
    Retrieve availability records for a guide.

    If a date is supplied, retrieve availability for that date.
    If no date is supplied, retrieve all availability records
    for the guide.
    """
    guide = _require_guide(guide)
    if date is not None:
        return staff_service.get_staff_availability(guide, date)
    return staff_service.get_staff_availability(guide)

def create_availability(
    guide,
    date,
    status="Available",
    start_time=None,
    end_time=None,
    reason=None,):
    """
    Create Guide availability.
    """
    guide = _require_guide(guide)
    return staff_service.create_availability(
        guide,
        date,
        status=status,
        start_time=start_time,
        end_time=end_time,
        reason=reason,)

def update_availability(
    availability,
    date=None,
    status=None,
    start_time=None,
    end_time=None,
    reason=None,
):
    """
    Update Guide availability.
    """

    if availability is None:
        raise GuideServiceError(
            "Availability record not found."
        )

    guide = get_guide(
        availability.staff_id
    )

    if guide is None:
        raise GuideServiceError(
            "This availability record does not belong to a Guide.")

    return staff_service.update_availability(
        availability,
        date=date,
        status=status,
        start_time=start_time,
        end_time=end_time,
        reason=reason,)

def delete_availability(availability):
    """
    Delete Guide availability.
    """
    if availability is None:
        raise GuideServiceError("Availability record not found.")
    guide = get_guide(availability.staff_id)
    if guide is None:
        raise GuideServiceError(
            "This availability record does not belong to a Guide.",)
    return staff_service.delete_availability(availability)

def is_guide_available(
    guide,
    date,
    start_time=None,
    end_time=None,):
    """
    Determine whether a Guide is available.
    """
    guide = _require_guide(guide)
    return staff_service.is_staff_available(
        guide,
        date,
        start_time=start_time,
        end_time=end_time,)

# =============================================================================
# Guide Schedules
# =============================================================================
def get_schedule(schedule_id):
    """
    Retrieve a Guide StaffSchedule.
    """
    if not schedule_id:
        return None
    return db.session.get(
        StaffSchedule,
        schedule_id,)

def get_guide_schedules(
    guide,
    start_datetime=None,
    end_datetime=None,
    status=None,):
    """
    Retrieve Guide schedules.
    """

    guide = _require_guide(
        guide
    )

    return staff_service.get_staff_schedules(
        guide,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status=status,)

def create_guide_schedule(
    guide,
    title,
    start_datetime,
    end_datetime=None,
    description=None,
    location=None,
    status="Scheduled",
    notes=None,):
    """
    Create a Guide schedule.
    """
    guide = _require_guide(guide)
    return staff_service.create_staff_schedule(
        guide,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        description=description,
        location=location,
        status=status,
        notes=notes,)

def update_guide_schedule(
    schedule,
    title=None,
    start_datetime=None,
    end_datetime=None,
    description=None,
    location=None,
    status=None,
    notes=None,):
    """
    Update a Guide schedule.
    """
    if schedule is None:
        raise GuideServiceError("Guide schedule not found.")
    guide = get_guide(schedule.staff_id)

    if guide is None:
        raise GuideServiceError("This schedule does not belong to a Guide.")
    return staff_service.update_staff_schedule(
        schedule,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        description=description,
        location=location,
        status=status,
        notes=notes,)

def cancel_guide_schedule(schedule):
    """
    Cancel a Guide schedule.
    """
    if schedule is None:
        raise GuideServiceError("Guide schedule not found.")
    guide = get_guide(schedule.staff_id)
    if guide is None:
        raise GuideServiceError("This schedule does not belong to a Guide.")
    return staff_service.cancel_staff_schedule(schedule)

# =============================================================================
# Guide Performance
# =============================================================================
def get_guide_performance(guide):
    """
    Calculate operational performance statistics for a Guide.
    """
    guide = _require_guide(guide)
    assignments = StaffAssignment.query.filter_by(staff_id=guide.id)
    total_assignments = assignments.count()
    completed_assignments = assignments.filter_by(status="Completed").count()
    cancelled_assignments = assignments.filter_by(status="Cancelled").count()
    declined_assignments = assignments.filter_by(status="Declined").count()
    active_assignments = assignments.filter(
        StaffAssignment.status.in_(list(ACTIVE_ASSIGNMENT_STATUSES))).count()
    accepted_assignments = assignments.filter(
        StaffAssignment.status.in_(
            [
                "Accepted",
                "In Progress",
                "Completed",])).count()

    completion_rate = 0
    acceptance_rate = 0
    if total_assignments:
        completion_rate = (
            completed_assignments
            / total_assignments
        ) * 100

        acceptance_rate = (
            accepted_assignments
            / total_assignments
        ) * 100

    return {
        "guide_id": guide.id,
        "employee_number": guide.employee_number,
        "guide_name": (
            guide.user.full_name
            if guide.user
            else None),
        "status": guide.status,
        "staff_type": guide.staff_type,
        "department": guide.department,
        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
        "cancelled_assignments": cancelled_assignments,
        "declined_assignments": declined_assignments,
        "completion_rate": round(
            completion_rate,
            2,),
        "acceptance_rate": round(
            acceptance_rate,
            2,),
        "rating": guide.rating,}

# =============================================================================
# Guide Statistics
# =============================================================================
def get_guide_statistics(guide):
    """
    Return detailed statistics for one Guide.
    """
    guide = _require_guide(guide)
    performance = get_guide_performance(guide)
    upcoming = get_upcoming_bookings(guide)
    current = get_current_bookings(guide)
    completed = get_completed_bookings(guide)
    return {
        **performance,
        "upcoming_bookings": len(upcoming),
        "current_bookings": len(current),
        "completed_bookings": len(completed),}

def get_guide_dashboard_statistics():
    """
    Return high-level Guide Dashboard statistics.
    """
    total_guides = Staff.query.filter_by(
        staff_type=GUIDE_STAFF_TYPE
    ).count()
    active_guides = Staff.query.filter(
        Staff.staff_type == GUIDE_STAFF_TYPE,
        Staff.status == "Active",
    ).count()
    inactive_guides = Staff.query.filter(
        Staff.staff_type == GUIDE_STAFF_TYPE,
        Staff.status == "Inactive",
    ).count()

    guides_on_leave = Staff.query.filter(
        Staff.staff_type == GUIDE_STAFF_TYPE,
        Staff.status == "On Leave",
    ).count()

    suspended_guides = Staff.query.filter(
        Staff.staff_type == GUIDE_STAFF_TYPE,
        Staff.status == "Suspended",
    ).count()

    total_assignments = (
        StaffAssignment.query
        .join(
            Staff,
            Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE).count())

    active_assignments = (
        StaffAssignment.query
        .join(Staff,Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE,
            StaffAssignment.status.in_(
                list(ACTIVE_ASSIGNMENT_STATUSES)),)
        .count())

    completed_assignments = (
        StaffAssignment.query
        .join(
            Staff,
            Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE,
            StaffAssignment.status == "Completed",
        ).count())

    pending_assignments = (
        StaffAssignment.query
        .join(Staff,
            Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE,
            StaffAssignment.status == "Assigned",)
        .count())

    return {
        "total_guides": total_guides,
        "active_guides": active_guides,
        "inactive_guides": inactive_guides,
        "guides_on_leave": guides_on_leave,
        "suspended_guides": suspended_guides,
        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
        "pending_assignments": pending_assignments,}

# =============================================================================
# Dashboard Data
# =============================================================================
def get_guide_dashboard_data():
    """
    Return the primary data required by the Guide Dashboard.
    """
    statistics = (get_guide_dashboard_statistics())
    guides = list_guides()
    active_guides = [
        guide
        for guide in guides
        if guide.status == "Active"]
    pending_assignments = (
        StaffAssignment.query
        .join(Staff,
            Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE,
            StaffAssignment.status == "Assigned",)
        .order_by(
            StaffAssignment.created_at.asc()).all())

    active_assignments = (
        StaffAssignment.query
        .join(
            Staff,
            Staff.id == StaffAssignment.staff_id,)
        .filter(
            Staff.staff_type == GUIDE_STAFF_TYPE,
            StaffAssignment.status.in_(
                list(ACTIVE_ASSIGNMENT_STATUSES)),)
        .order_by(
            StaffAssignment.created_at.asc())
        .all())

    return {
        "statistics": statistics,
        "guides": guides,
        "active_guides": active_guides,
        "pending_assignments": pending_assignments,
        "active_assignments": active_assignments,}

# =============================================================================
# Guide Dashboard — Individual Guide
# =============================================================================
def get_guide_dashboard_for(guide):
    """
    Return all primary dashboard data for one Guide.
    """
    guide = _require_guide(guide)
    statistics = get_guide_statistics(guide)
    upcoming_bookings = (get_upcoming_bookings(guide))
    current_bookings = (get_current_bookings(guide))
    pending_assignments = (get_pending_assignments(guide))
    active_assignments = (get_active_assignments(guide))
    return {
        "guide": guide,
        "statistics": statistics,
        "upcoming_bookings": upcoming_bookings,
        "current_bookings": current_bookings,
        "pending_assignments": pending_assignments,
        "active_assignments": active_assignments,}

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Exceptions
    "GuideServiceError",
    # Constants
    "GUIDE_STAFF_TYPE",
    "ACTIVE_ASSIGNMENT_STATUSES",
    "COMPLETED_ASSIGNMENT_STATUSES",
    "INACTIVE_ASSIGNMENT_STATUSES",
    # Retrieval
    "get_guide",
    "get_guide_by_id",
    "get_guide_by_user",
    "get_guide_by_user_id",
    "get_guide_by_employee_number",
    # Catalogue
    "list_guides",
    "get_guide_members",
    # Validation
    "ensure_guide",
    "ensure_guide_user",
    # Status
    "update_guide_status",
    "activate_guide",
    "deactivate_guide",
    "place_guide_on_leave",
    # Assignments
    "get_assignment",
    "get_guide_assignments",
    "get_active_assignments",
    "get_completed_assignments",
    "get_pending_assignments",
    "accept_assignment",
    "decline_assignment",
    "start_assignment",
    "complete_assignment",
    "cancel_assignment",

    # Bookings
    "get_guide_bookings",
    "get_upcoming_bookings",
    "get_completed_bookings",
    "get_current_bookings",

    # Availability
    "get_availability",
    "get_guide_availability",
    "create_availability",
    "update_availability",
    "delete_availability",
    "is_guide_available",

    # Schedules
    "get_schedule",
    "get_guide_schedules",
    "create_guide_schedule",
    "update_guide_schedule",
    "cancel_guide_schedule",

    # Performance
    "get_guide_performance",
    "get_guide_statistics",

    # Dashboard
    "get_guide_dashboard_statistics",
    "get_guide_dashboard_data",
    "get_guide_dashboard_for",]