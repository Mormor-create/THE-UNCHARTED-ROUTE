"""
===============================================================================
The Uncharted Route
Staff Service
===============================================================================

Central business-logic layer for Staff operations.

Responsibilities
----------------
• Create staff profiles
• Retrieve staff profiles
• Search and filter staff
• Update staff profiles
• Manage staff status
• Manage staff availability
• Manage staff schedules
• Assign staff to booking
• Update assignment status
• Remove staff assignments
• Calculate staff operational statistics

Architecture
------------

Routes and forms should NOT directly perform Staff business logic.

Instead:

    Admin Route
        ↓
    Staff Service
        ↓
    Staff Models
        ↓
    Database

The service also coordinates relationships between:

    • User
    • Staff
    • Booking
    • StaffAvailability
    • StaffSchedule
    • StaffAssignment

Important
---------

Staff authentication remains the responsibility of the User model and
authentication layer.

This service manages operational staff information, not passwords or
authentication credentials.
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
)

from app.models.staff import (
    STAFF_TYPES,
    STAFF_STATUSES,
    EMPLOYMENT_TYPES,
)

from app.models.staff_availability import (
    STAFF_AVAILABILITY_STATUSES,
)

from app.models.staff_schedule import (
    STAFF_SCHEDULE_STATUSES,
)

from app.models.staff_assignment import (
    STAFF_ASSIGNMENT_ROLES,
    STAFF_ASSIGNMENT_STATUSES,
)


# =============================================================================
# Exceptions
# =============================================================================
class StaffServiceError(ValueError):
    """
    Base exception raised by the Staff Service.
    """

# =============================================================================
# Validation Helpers
# =============================================================================


def _require_staff(staff):
    """
    Ensure a Staff object was supplied.
    """

    if staff is None:
        raise StaffServiceError(
            "Staff record not found."
        )

    return staff


def _require_booking(booking):
    """
    Ensure a Booking object was supplied.
    """

    if booking is None:
        raise StaffServiceError(
            "Booking not found."
        )

    return booking


def _require_user(user):
    """
    Ensure a User object was supplied.
    """

    if user is None:
        raise StaffServiceError(
            "User account not found."
        )

    return user


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


# =============================================================================
# User / Staff Validation
# =============================================================================


def get_user(user_id):
    """
    Retrieve a User by primary key.
    """

    if not user_id:
        return None

    return db.session.get(
        User,
        user_id,
    )


def get_staff_by_user(user):
    """
    Retrieve the Staff profile associated with a User.
    """

    if user is None:
        return None

    return Staff.query.filter_by(
        user_id=user.id
    ).first()


def get_staff_by_user_id(user_id):
    """
    Retrieve Staff by User ID.
    """

    if not user_id:
        return None

    return Staff.query.filter_by(
        user_id=user_id
    ).first()


def ensure_staff_user(user):
    """
    Validate that a User can be associated with a Staff profile.

    Returns the existing Staff profile when one already exists.
    """

    user = _require_user(user)

    existing = get_staff_by_user(
        user
    )

    if existing:
        return existing

    if not user.is_internal_user:
        raise StaffServiceError(
            "Only internal users can be assigned a staff profile."
        )

    return None


# =============================================================================
# Staff Retrieval
# =============================================================================


def get_staff(staff_id):
    """
    Retrieve Staff by primary key.
    """

    if not staff_id:
        return None

    return db.session.get(
        Staff,
        staff_id,
    )


def get_staff_by_employee_number(employee_number):
    """
    Retrieve Staff by employee number.
    """

    employee_number = _normalize(
        employee_number
    )

    if not employee_number:
        return None

    return Staff.query.filter_by(
        employee_number=employee_number
    ).first()


def get_staff_by_id(staff_id):
    """
    Alias for get_staff().
    """

    return get_staff(
        staff_id
    )


# =============================================================================
# Staff Catalogue
# =============================================================================


def list_staff(
    search=None,
    staff_type=None,
    department=None,
    status=None,
    employment_type=None,
    active_only=False,
):
    """
    Return Staff records using administrative filters.

    Parameters
    ----------
    search:
        Searches employee number, job title, department, and linked
        User name, username, and email.

    staff_type:
        Filter by operational staff type.

    department:
        Filter by department.

    status:
        Filter by Staff operational status.

    employment_type:
        Filter by employment type.

    active_only:
        Return only active Staff records.
    """

    query = (
        Staff.query
        .join(User)
    )

    search = _normalize(
        search
    )

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

    if staff_type:
        query = query.filter(
            Staff.staff_type == staff_type
        )

    if department:
        query = query.filter(
            Staff.department == department
        )

    if status:
        query = query.filter(
            Staff.status == status
        )

    if employment_type:
        query = query.filter(
            Staff.employment_type == employment_type
        )

    if active_only:
        query = query.filter(
            Staff.status == "Active"
        )

    return query.order_by(
        User.first_name.asc(),
        User.last_name.asc(),
    ).all()


# =============================================================================
# Staff Creation
# =============================================================================
def create_staff(
    user,
    employee_number=None,
    staff_type="Other",
    department=None,
    job_title=None,
    employment_type="Full Time",
    hire_date=None,
    end_date=None,
    status="Active",
    skills=None,
    languages=None,
    certifications=None,
    qualifications=None,
    emergency_contact_name=None,
    emergency_contact_phone=None,
    emergency_contact_relationship=None,
    notes=None,
    internal_notes=None,
):
    """
    Create a Staff profile for an existing User.

    The User account must already exist.

    Authentication credentials are intentionally not managed here.
    """

    user = _require_user(
        user
    )

    existing = get_staff_by_user(
        user
    )

    if existing:
        raise StaffServiceError(
            "This user already has a staff profile."
        )

    if not user.is_internal_user:
        raise StaffServiceError(
            "The selected user is not an internal platform user."
        )

    employee_number = _normalize(
        employee_number
    )

    if employee_number:

        duplicate = get_staff_by_employee_number(
            employee_number
        )

        if duplicate:
            raise StaffServiceError(
                "The employee number is already in use."
            )

    if staff_type not in STAFF_TYPES:
        raise StaffServiceError(
            "Invalid staff type."
        )

    if status not in STAFF_STATUSES:
        raise StaffServiceError(
            "Invalid staff status."
        )

    if employment_type not in EMPLOYMENT_TYPES:
        raise StaffServiceError(
            "Invalid employment type."
        )

    staff = Staff(
        user_id=user.id,

        employee_number=employee_number,

        staff_type=staff_type,

        department=_normalize(
            department
        ),

        job_title=_normalize(
            job_title
        ),

        employment_type=employment_type,

        hire_date=hire_date,

        end_date=end_date,

        status=status,

        skills=_normalize(
            skills
        ),

        languages=_normalize(
            languages
        ),

        certifications=_normalize(
            certifications
        ),

        qualifications=_normalize(
            qualifications
        ),

        emergency_contact_name=_normalize(
            emergency_contact_name
        ),

        emergency_contact_phone=_normalize(
            emergency_contact_phone
        ),

        emergency_contact_relationship=_normalize(
            emergency_contact_relationship
        ),

        notes=_normalize(
            notes
        ),

        internal_notes=_normalize(
            internal_notes
        ),
    )

    db.session.add(
        staff
    )

    db.session.commit()

    return staff

# =============================================================================
# Combined Staff Account + Profile Creation
# =============================================================================

def create_staff_member(
    first_name,
    last_name,
    username,
    email,
    password,
    phone=None,
    is_verified=True,
    employee_number=None,
    staff_type="Other",
    department=None,
    job_title=None,
    employment_type="Full Time",
    hire_date=None,
    end_date=None,
    status="Active",
    skills=None,
    languages=None,
    certifications=None,
    qualifications=None,
    emergency_contact_name=None,
    emergency_contact_phone=None,
    emergency_contact_relationship=None,
    notes=None,
    internal_notes=None,
):
    """
    Create a User account and linked Staff profile.

    If the supplied username or email already belongs to an internal
    User account, that account may be linked to the new Staff profile
    provided it does not already have one.

    New staff accounts are assigned an application-level User role
    according to their Staff type:

        Guide          -> guide
        Administrator  -> admin
        Everything else -> staff
    """

    from app.models import User
    from app.services.user_service import (
        create_user,
        get_user_by_username,
        get_user_by_email,
    )

    # =========================================================================
    # Validate Staff Profile Choices
    # =========================================================================

    if staff_type not in STAFF_TYPES:
        raise StaffServiceError(
            "Invalid staff type."
        )

    if status not in STAFF_STATUSES:
        raise StaffServiceError(
            "Invalid staff status."
        )

    if employment_type not in EMPLOYMENT_TYPES:
        raise StaffServiceError(
            "Invalid employment type."
        )

    # =========================================================================
    # Normalize Account Values
    # =========================================================================

    username = _normalize(username)
    email = _normalize(email)

    if not username:
        raise StaffServiceError(
            "Username is required."
        )

    if not email:
        raise StaffServiceError(
            "Email address is required."
        )

    if not password:
        raise StaffServiceError(
            "Password is required."
        )

    # =========================================================================
    # Resolve Existing User
    # =========================================================================

    existing_by_username = get_user_by_username(username)
    existing_by_email = get_user_by_email(email)

    if (
        existing_by_username
        and existing_by_email
        and existing_by_username.id != existing_by_email.id
    ):
        raise StaffServiceError(
            "The username and email belong to different user accounts."
        )

    user = existing_by_username or existing_by_email

    # =========================================================================
    # Existing User
    # =========================================================================
    if user:

        if not user.is_internal_user:
            raise StaffServiceError(
                "An existing customer account cannot be converted into "
                "a Staff profile from this screen."
            )

        existing_staff = get_staff_by_user(user)

        if existing_staff:
            raise StaffServiceError(
                "This user already has a staff profile."
            )

        # Keep the existing account credentials intact.
        # The Staff workflow is linking the existing internal account
        # to a new Staff profile rather than replacing its password.
        user.phone = phone or user.phone

        if is_verified:
            user.is_verified = True

    # =========================================================================
    # New User
    # =========================================================================

    else:

        normalized_staff_type = (
            staff_type.strip().lower()
            if staff_type
            else ""
        )

        if normalized_staff_type == "guide":
            user_role = "guide"

        elif normalized_staff_type in {
            "administrator",
            "admin",
        }:
            user_role = "admin"

        else:
            user_role = "staff"

        user = create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            role=user_role,
            phone=phone,
            is_verified=is_verified,
        )

    # =========================================================================
    # Create Staff Profile
    # =========================================================================

    try:

        staff = Staff(
            user_id=user.id,
            employee_number=_normalize(employee_number),
            staff_type=staff_type,
            department=_normalize(department),
            job_title=_normalize(job_title),
            employment_type=employment_type,
            hire_date=hire_date,
            end_date=end_date,
            status=status,
            skills=_normalize(skills),
            languages=_normalize(languages),
            certifications=_normalize(certifications),
            qualifications=_normalize(qualifications),
            emergency_contact_name=_normalize(
                emergency_contact_name
            ),
            emergency_contact_phone=_normalize(
                emergency_contact_phone
            ),
            emergency_contact_relationship=_normalize(
                emergency_contact_relationship
            ),
            notes=_normalize(notes),
            internal_notes=_normalize(internal_notes),
        )

        # Employee number uniqueness.
        if staff.employee_number:

            duplicate = get_staff_by_employee_number(
                staff.employee_number
            )

            if duplicate:
                raise StaffServiceError(
                    "The employee number is already in use."
                )

        db.session.add(staff)

        # Keep the account active when the Staff profile is Active.
        if status == "Active":
            user.is_active = True

        elif status in {
            "Inactive",
            "Suspended",
        }:
            user.is_active = False

        db.session.commit()

        return staff

    except Exception:

        db.session.rollback()

        # A newly-created User has already been committed by
        # create_user(). Remove it if Staff creation fails.
        #
        # Existing Users must never be deleted.
        if user and user.id:

            existing_staff = get_staff_by_user(user)

            if not existing_staff:
                try:
                    db.session.delete(user)
                    db.session.commit()
                except Exception:
                    db.session.rollback()

        raise
# =============================================================================
# Staff Update
# =============================================================================


def update_staff(
    staff,
    employee_number=None,
    staff_type=None,
    department=None,
    job_title=None,
    employment_type=None,
    hire_date=None,
    end_date=None,
    status=None,
    skills=None,
    languages=None,
    certifications=None,
    qualifications=None,
    emergency_contact_name=None,
    emergency_contact_phone=None,
    emergency_contact_relationship=None,
    notes=None,
    internal_notes=None,
):
    """
    Update an existing Staff profile.
    """

    staff = _require_staff(
        staff
    )

    employee_number = _normalize(
        employee_number
    )

    if employee_number:

        duplicate = (
            Staff.query
            .filter(
                Staff.employee_number == employee_number,
                Staff.id != staff.id,
            )
            .first()
        )

        if duplicate:
            raise StaffServiceError(
                "The employee number is already in use."
            )

    if staff_type is not None:

        if staff_type not in STAFF_TYPES:
            raise StaffServiceError(
                "Invalid staff type."
            )

        staff.staff_type = staff_type

    if status is not None:

        if status not in STAFF_STATUSES:
            raise StaffServiceError(
                "Invalid staff status."
            )

        staff.status = status

    if employment_type is not None:

        if employment_type not in EMPLOYMENT_TYPES:
            raise StaffServiceError(
                "Invalid employment type."
            )

        staff.employment_type = employment_type

    staff.employee_number = employee_number

    if department is not None:
        staff.department = _normalize(
            department
        )

    if job_title is not None:
        staff.job_title = _normalize(
            job_title
        )

    if hire_date is not None:
        staff.hire_date = hire_date

    if end_date is not None:
        staff.end_date = end_date

    if skills is not None:
        staff.skills = _normalize(
            skills
        )

    if languages is not None:
        staff.languages = _normalize(
            languages
        )

    if certifications is not None:
        staff.certifications = _normalize(
            certifications
        )

    if qualifications is not None:
        staff.qualifications = _normalize(
            qualifications
        )

    if emergency_contact_name is not None:
        staff.emergency_contact_name = _normalize(
            emergency_contact_name
        )

    if emergency_contact_phone is not None:
        staff.emergency_contact_phone = _normalize(
            emergency_contact_phone
        )

    if emergency_contact_relationship is not None:
        staff.emergency_contact_relationship = _normalize(
            emergency_contact_relationship
        )

    if notes is not None:
        staff.notes = _normalize(
            notes
        )

    if internal_notes is not None:
        staff.internal_notes = _normalize(
            internal_notes
        )

    staff.updated_at = datetime.utcnow()

    db.session.commit()

    return staff


# =============================================================================
# Staff Status
# =============================================================================


def update_staff_status(
    staff,
    status,
):
    """
    Change a Staff member's operational status.
    """

    staff = _require_staff(
        staff
    )

    if status not in STAFF_STATUSES:
        raise StaffServiceError(
            "Invalid staff status."
        )

    staff.status = status

    if status == "Inactive":
        staff.end_date = (
            staff.end_date
            or datetime.utcnow().date()
        )

    staff.updated_at = datetime.utcnow()

    db.session.commit()

    return staff


def activate_staff(staff):
    """
    Mark Staff as active.
    """

    return update_staff_status(
        staff,
        "Active",
    )


def deactivate_staff(staff):
    """
    Mark Staff as inactive.
    """

    return update_staff_status(
        staff,
        "Inactive",
    )

# =============================================================================
# STAFF AVAILABILITY
# =============================================================================

def get_availability(availability_id):
    """
    Retrieve a single staff availability record by ID.
    """
    return db.session.get(StaffAvailability, availability_id)


def get_staff_availability(staff, date=None):
    """
    Retrieve staff availability records.

    The StaffAvailability model stores datetime windows using starts_at
    and ends_at. When a date is supplied, records overlapping that
    calendar date are returned.

    Args:
        staff: Staff instance.
        date: Optional date object.

    Returns:
        List[StaffAvailability]
    """
    query = StaffAvailability.query.filter_by(
        staff_id=staff.id
    )

    if date is not None:
        from datetime import datetime, time

        day_start = datetime.combine(date, time.min)
        day_end = datetime.combine(date, time.max)

        query = query.filter(
            StaffAvailability.starts_at <= day_end,
            StaffAvailability.ends_at >= day_start,
        )

    return query.order_by(
        StaffAvailability.starts_at.asc()
    ).all()


def create_availability(
    staff,
    date,
    status="Available",
    start_time=None,
    end_time=None,
    reason=None,
):
    """
    Create a staff availability window.

    The public/admin form may still provide a calendar date plus optional
    start/end times. Those values are converted into the datetime fields
    required by StaffAvailability.
    """
    from datetime import datetime, time

    if not staff:
        raise StaffServiceError("Staff member is required.")

    if status not in STAFF_AVAILABILITY_STATUSES:
        raise StaffServiceError(
            f"Invalid availability status: {status}"
        )

    if date is None:
        raise StaffServiceError("Availability date is required.")

    # Default to an all-day window when times are not supplied.
    if start_time is None:
        starts_at = datetime.combine(date, time.min)
    else:
        starts_at = datetime.combine(date, start_time)

    if end_time is None:
        ends_at = datetime.combine(date, time.max)
    else:
        ends_at = datetime.combine(date, end_time)

    if ends_at <= starts_at:
        raise StaffServiceError(
            "Availability end time must be after the start time."
        )

    availability = StaffAvailability(
        staff_id=staff.id,
        status=status,
        starts_at=starts_at,
        ends_at=ends_at,
        reason=reason,
    )

    db.session.add(availability)
    db.session.commit()

    return availability


def update_availability(
    availability,
    date=None,
    status=None,
    start_time=None,
    end_time=None,
    reason=None,
):
    """
    Update a staff availability window.

    Maintains compatibility with the existing admin form API while
    storing the actual model fields as starts_at and ends_at.
    """
    from datetime import datetime, time

    if availability is None:
        raise StaffServiceError("Availability record is required.")

    if status is not None:
        if status not in STAFF_AVAILABILITY_STATUSES:
            raise StaffServiceError(
                f"Invalid availability status: {status}"
            )
        availability.status = status

    if reason is not None:
        availability.reason = reason

    current_start = availability.starts_at
    current_end = availability.ends_at

    if date is not None:
        current_start_date = date
        current_end_date = date
    else:
        current_start_date = (
            current_start.date()
            if current_start is not None
            else None
        )
        current_end_date = (
            current_end.date()
            if current_end is not None
            else current_start_date
        )

    if current_start_date is None:
        raise StaffServiceError(
            "Availability date is required."
        )

    if start_time is not None:
        new_start_time = start_time
    elif current_start is not None:
        new_start_time = current_start.time()
    else:
        new_start_time = time.min

    if end_time is not None:
        new_end_time = end_time
    elif current_end is not None:
        new_end_time = current_end.time()
    else:
        new_end_time = time.max

    starts_at = datetime.combine(
        current_start_date,
        new_start_time,
    )

    ends_at = datetime.combine(
        current_end_date,
        new_end_time,
    )

    if ends_at <= starts_at:
        raise StaffServiceError(
            "Availability end time must be after the start time."
        )

    availability.starts_at = starts_at
    availability.ends_at = ends_at

    db.session.commit()

    return availability


def delete_availability(availability):
    """
    Delete a staff availability record.
    """
    if availability is None:
        raise StaffServiceError("Availability record is required.")

    db.session.delete(availability)
    db.session.commit()


def is_staff_available(
    staff,
    date,
    start_time=None,
    end_time=None,
):
    """
    Determine whether a staff member is available during a requested
    date/time window.

    Blocked states:
        Unavailable
        On Leave
    """
    from datetime import datetime, time

    if staff is None:
        return False

    if getattr(staff, "status", None) != "Active":
        return False

    if date is None:
        return False

    if start_time is None:
        requested_start = datetime.combine(
            date,
            time.min,
        )
    else:
        requested_start = datetime.combine(
            date,
            start_time,
        )

    if end_time is None:
        requested_end = datetime.combine(
            date,
            time.max,
        )
    else:
        requested_end = datetime.combine(
            date,
            end_time,
        )

    if requested_end <= requested_start:
        return False

    blocked_statuses = {
        "Unavailable",
        "On Leave",
    }

    conflicting_record = (
        StaffAvailability.query
        .filter(
            StaffAvailability.staff_id == staff.id,
            StaffAvailability.status.in_(blocked_statuses),
            StaffAvailability.starts_at <= requested_end,
            StaffAvailability.ends_at >= requested_start,
        )
        .first()
    )

    if conflicting_record is not None:
        return False

    # If there is an explicit Available/Approved record covering
    # the requested period, treat the staff member as available.
    available_statuses = {
        "Available",
        "Approved",
    }

    available_record = (
        StaffAvailability.query
        .filter(
            StaffAvailability.staff_id == staff.id,
            StaffAvailability.status.in_(available_statuses),
            StaffAvailability.starts_at <= requested_start,
            StaffAvailability.ends_at >= requested_end,
        )
        .first()
    )

    return available_record is not None


# =============================================================================
# STAFF SCHEDULES
# =============================================================================
def get_schedule(schedule_id):
    """
    Retrieve a single staff schedule by ID.
    """
    return db.session.get(StaffSchedule, schedule_id)


def get_staff_schedules(
    staff,
    start_datetime=None,
    end_datetime=None,
    status=None,
):
    """
    Retrieve schedules for a staff member.

    StaffSchedule stores its datetime window in starts_at and ends_at.
    """
    query = StaffSchedule.query.filter_by(
        staff_id=staff.id
    )

    if start_datetime is not None:
        query = query.filter(
            StaffSchedule.ends_at >= start_datetime
        )

    if end_datetime is not None:
        query = query.filter(
            StaffSchedule.starts_at <= end_datetime
        )

    if status is not None:
        query = query.filter(
            StaffSchedule.status == status
        )

    return query.order_by(
        StaffSchedule.starts_at.asc()
    ).all()


def create_staff_schedule(
    staff,
    title,
    start_datetime,
    end_datetime=None,
    description=None,
    location=None,
    status="Scheduled",
    notes=None,
):
    """
    Create an internal staff schedule.

    This is an operational staff schedule only. It is not a customer-facing
    experience departure schedule.
    """
    if not staff:
        raise StaffServiceError("Staff member is required.")

    if not title or not title.strip():
        raise StaffServiceError("Schedule title is required.")

    if status not in STAFF_SCHEDULE_STATUSES:
        raise StaffServiceError(
            f"Invalid schedule status: {status}"
        )

    if start_datetime is None:
        raise StaffServiceError(
            "Schedule start datetime is required."
        )

    if end_datetime is None:
        raise StaffServiceError(
            "Schedule end datetime is required."
        )

    if end_datetime <= start_datetime:
        raise StaffServiceError(
            "Schedule end time must be after the start time."
        )

    schedule = StaffSchedule(
        staff_id=staff.id,
        title=title.strip(),
        description=description,
        status=status,
        starts_at=start_datetime,
        ends_at=end_datetime,
        location=location,
        notes=notes,
    )

    db.session.add(schedule)
    db.session.commit()

    return schedule


def update_staff_schedule(
    schedule,
    title=None,
    start_datetime=None,
    end_datetime=None,
    description=None,
    location=None,
    status=None,
    notes=None,
):
    """
    Update an internal staff schedule.
    """
    if schedule is None:
        raise StaffServiceError("Schedule is required.")

    if title is not None:
        title = title.strip()

        if not title:
            raise StaffServiceError(
                "Schedule title is required."
            )

        schedule.title = title

    if status is not None:
        if status not in STAFF_SCHEDULE_STATUSES:
            raise StaffServiceError(
                f"Invalid schedule status: {status}"
            )

        schedule.status = status

    if start_datetime is not None:
        schedule.starts_at = start_datetime

    if end_datetime is not None:
        schedule.ends_at = end_datetime

    if schedule.starts_at is None:
        raise StaffServiceError(
            "Schedule start datetime is required."
        )

    if schedule.ends_at is None:
        raise StaffServiceError(
            "Schedule end datetime is required."
        )

    if schedule.ends_at <= schedule.starts_at:
        raise StaffServiceError(
            "Schedule end time must be after the start time."
        )

    if description is not None:
        schedule.description = description

    if location is not None:
        schedule.location = location

    if notes is not None:
        schedule.notes = notes

    db.session.commit()

    return schedule


def cancel_staff_schedule(schedule):
    """
    Cancel an internal staff schedule.
    """
    if schedule is None:
        raise StaffServiceError("Schedule is required.")

    schedule.status = "Cancelled"
    schedule.cancelled_at = datetime.utcnow()

    db.session.commit()

    return schedule

# =============================================================================
# Staff Assignments
# =============================================================================
def get_assignment(
    assignment_id,
):
    """
    Retrieve a StaffAssignment.
    """

    if not assignment_id:
        return None

    return db.session.get(
        StaffAssignment,
        assignment_id,
    )


def get_staff_assignments(
    staff,
    status=None,
    role=None,
):
    """
    Retrieve assignments belonging to a Staff member.
    """

    staff = _require_staff(
        staff
    )

    query = StaffAssignment.query.filter_by(
        staff_id=staff.id
    )

    if status:
        query = query.filter(
            StaffAssignment.status == status
        )

    if role:
        query = query.filter(
            StaffAssignment.role == role
        )

    return query.order_by(
        StaffAssignment.created_at.desc()
    ).all()


def get_booking_assignments(
    booking,
    status=None,
):
    """
    Retrieve Staff assignments for a Booking.
    """

    booking = _require_booking(
        booking
    )

    query = StaffAssignment.query.filter_by(
        booking_id=booking.id
    )

    if status:
        query = query.filter(
            StaffAssignment.status == status
        )

    return query.order_by(
        StaffAssignment.created_at.asc()
    ).all()


def has_booking_assignment(
    staff,
    booking,
):
    """
    Determine whether Staff is already assigned to a Booking.
    """

    staff = _require_staff(
        staff
    )

    booking = _require_booking(
        booking
    )

    return (
        StaffAssignment.query
        .filter_by(
            staff_id=staff.id,
            booking_id=booking.id,
        )
        .first()
        is not None
    )


def assign_staff_to_booking(
    staff,
    booking,
    role="Other",
    is_primary=False,
    notes=None,
    check_availability=True,
):
    """
    Assign Staff to a Booking.

    This function does not modify Booking financial information or booking
    status.

    Availability validation is performed when requested.
    """

    staff = _require_staff(
        staff
    )

    booking = _require_booking(
        booking
    )

    if staff.status != "Active":
        raise StaffServiceError(
            "Inactive staff cannot be assigned to booking."
        )

    if role not in STAFF_ASSIGNMENT_ROLES:
        raise StaffServiceError(
            "Invalid staff assignment role."
        )

    if has_booking_assignment(
        staff,
        booking,
    ):
        raise StaffServiceError(
            "This staff member is already assigned to this booking."
        )

    # -------------------------------------------------------------------------
    # Availability Check
    # -------------------------------------------------------------------------

    if check_availability:

        schedule_date = booking.schedule_date

        schedule_time = booking.schedule_time

        if schedule_date:

            available = is_staff_available(
                staff,
                schedule_date,
            )

            if not available:
                raise StaffServiceError(
                    "Staff member is not available on the booking date."
                )

    assignment = StaffAssignment(
        staff_id=staff.id,

        booking_id=booking.id,

        role=role,

        status="Assigned",

        is_primary=is_primary,

        notes=_normalize(
            notes
        ),
    )

    db.session.add(
        assignment
    )

    db.session.commit()

    return assignment


def update_assignment(
    assignment,
    role=None,
    status=None,
    is_primary=None,
    notes=None,
):
    """
    Update an existing Staff assignment.
    """

    if assignment is None:
        raise StaffServiceError(
            "Staff assignment not found."
        )

    if role is not None:

        if role not in STAFF_ASSIGNMENT_ROLES:
            raise StaffServiceError(
                "Invalid staff assignment role."
            )

        assignment.role = role

    if status is not None:

        if status not in STAFF_ASSIGNMENT_STATUSES:
            raise StaffServiceError(
                "Invalid staff assignment status."
            )

        assignment.status = status

        now = datetime.utcnow()

        if status == "Accepted" and not assignment.accepted_at:
            assignment.accepted_at = now

        if status == "Completed" and not assignment.completed_at:
            assignment.completed_at = now

    if is_primary is not None:
        assignment.is_primary = bool(
            is_primary
        )

    if notes is not None:
        assignment.notes = _normalize(
            notes
        )

    assignment.updated_at = datetime.utcnow()

    db.session.commit()

    return assignment


def accept_assignment(
    assignment,
):
    """
    Mark an assignment as accepted.
    """

    return update_assignment(
        assignment,
        status="Accepted",
    )


def decline_assignment(
    assignment,
):
    """
    Mark an assignment as declined.
    """

    return update_assignment(
        assignment,
        status="Declined",
    )


def start_assignment(
    assignment,
):
    """
    Mark an assignment as in progress.
    """

    return update_assignment(
        assignment,
        status="In Progress",
    )


def complete_assignment(
    assignment,
):
    """
    Mark an assignment as completed.
    """

    return update_assignment(
        assignment,
        status="Completed",
    )


def cancel_assignment(
    assignment,
):
    """
    Cancel a Staff assignment.
    """

    return update_assignment(
        assignment,
        status="Cancelled",
    )


def remove_staff_assignment(
    assignment,
):
    """
    Remove a Staff assignment.

    This should be used for administrative correction rather than normal
    operational cancellation.
    """

    if assignment is None:
        raise StaffServiceError(
            "Staff assignment not found."
        )

    db.session.delete(
        assignment
    )

    db.session.commit()


# =============================================================================
# Staff Statistics
# =============================================================================


def get_staff_statistics(
    staff,
):
    """
    Return operational statistics for one Staff member.
    """

    staff = _require_staff(
        staff
    )

    assignments = StaffAssignment.query.filter_by(
        staff_id=staff.id
    )

    total_assignments = assignments.count()

    completed_assignments = assignments.filter_by(
        status="Completed"
    ).count()

    cancelled_assignments = assignments.filter_by(
        status="Cancelled"
    ).count()

    active_assignments = assignments.filter(
        StaffAssignment.status.in_(
            [
                "Assigned",
                "Accepted",
                "In Progress",
            ]
        )
    ).count()

    declined_assignments = assignments.filter_by(
        status="Declined"
    ).count()

    completion_rate = 0

    if total_assignments:
        completion_rate = (
            completed_assignments
            / total_assignments
        ) * 100

    return {
        "staff_id": staff.id,
        "employee_number": staff.employee_number,
        "staff_type": staff.staff_type,
        "department": staff.department,
        "status": staff.status,

        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
        "cancelled_assignments": cancelled_assignments,
        "declined_assignments": declined_assignments,

        "completion_rate": round(
            completion_rate,
            2,
        ),

        "rating": staff.rating,
    }


def get_staff_dashboard_statistics():
    """
    Return high-level Staff Dashboard statistics.
    """

    total_staff = Staff.query.count()

    active_staff = Staff.query.filter_by(
        status="Active"
    ).count()

    inactive_staff = Staff.query.filter_by(
        status="Inactive"
    ).count()

    on_leave = Staff.query.filter_by(
        status="On Leave"
    ).count()

    suspended_staff = Staff.query.filter_by(
        status="Suspended"
    ).count()

    total_assignments = StaffAssignment.query.count()

    active_assignments = StaffAssignment.query.filter(
        StaffAssignment.status.in_(
            [
                "Assigned",
                "Accepted",
                "In Progress",
            ]
        )
    ).count()

    completed_assignments = StaffAssignment.query.filter_by(
        status="Completed"
    ).count()

    return {
        "total_staff": total_staff,
        "active_staff": active_staff,
        "inactive_staff": inactive_staff,
        "on_leave": on_leave,
        "suspended_staff": suspended_staff,

        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
    }


# =============================================================================
# Staff Dashboard
# =============================================================================


def get_staff_dashboard_data():
    """
    Return the primary data required by the Staff Dashboard.
    """

    statistics = get_staff_dashboard_statistics()

    staff = list_staff(
        active_only=False
    )

    active_staff = [
        member
        for member in staff
        if member.status == "Active"
    ]

    return {
        "statistics": statistics,
        "staff": staff,
        "active_staff": active_staff,
    }


# =============================================================================
# Public API
# =============================================================================
# =============================================================================
# Staff Convenience Helpers
# =============================================================================


def get_staff_members(
    search=None,
    staff_type=None,
    department=None,
    status=None,
    employment_type=None,
    active_only=False,
):
    """
    Return Staff members for administrative and operational use.

    This is a convenience wrapper around list_staff().

    It exists as a semantic alias so routes and dashboard code can use
    get_staff_members() when the intention is specifically to retrieve
    staff members rather than perform a generic Staff catalogue query.
    """

    return list_staff(
        search=search,
        staff_type=staff_type,
        department=department,
        status=status,
        employment_type=employment_type,
        active_only=active_only,
    )


# =============================================================================
# Staff Role Constants
# =============================================================================

# STAFF_TYPES represents the operational categories of Staff.
#
# Examples may include:
#     Guide
#     Driver
#     Consultant
#     Administrator
#     Coordinator
#     Other
#
# The actual values are defined by the Staff model and therefore remain
# the single source of truth.

STAFF_ROLES = tuple(STAFF_TYPES)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # -------------------------------------------------------------------------
    # Exceptions
    # -------------------------------------------------------------------------

    "StaffServiceError",

    # -------------------------------------------------------------------------
    # Staff Role / Type Constants
    # -------------------------------------------------------------------------

    "STAFF_ROLES",

    # -------------------------------------------------------------------------
    # User / Staff
    # -------------------------------------------------------------------------

    "get_user",
    "get_staff_by_user",
    "get_staff_by_user_id",
    "ensure_staff_user",

    # -------------------------------------------------------------------------
    # Staff Retrieval
    # -------------------------------------------------------------------------

    "get_staff",
    "get_staff_by_id",
    "get_staff_by_employee_number",
    "list_staff",
    "get_staff_members",

    # -------------------------------------------------------------------------
    # Staff Management
    # -------------------------------------------------------------------------

    "create_staff",
    "update_staff",

    # -------------------------------------------------------------------------
    # Staff Status
    # -------------------------------------------------------------------------

    "update_staff_status",
    "activate_staff",
    "deactivate_staff",

    # -------------------------------------------------------------------------
    # Availability
    # -------------------------------------------------------------------------

    "get_availability",
    "get_staff_availability",
    "create_availability",
    "update_availability",
    "delete_availability",
    "is_staff_available",

    # -------------------------------------------------------------------------
    # Staff Schedules
    # -------------------------------------------------------------------------

    "get_schedule",
    "get_staff_schedules",
    "create_staff_schedule",
    "update_staff_schedule",
    "cancel_staff_schedule",

    # -------------------------------------------------------------------------
    # Staff Assignments
    # -------------------------------------------------------------------------

    "get_assignment",
    "get_staff_assignments",
    "get_booking_assignments",
    "has_booking_assignment",
    "assign_staff_to_booking",
    "update_assignment",
    "accept_assignment",
    "decline_assignment",
    "start_assignment",
    "complete_assignment",
    "cancel_assignment",
    "remove_staff_assignment",

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    "get_staff_statistics",
    "get_staff_dashboard_statistics",
    "get_staff_dashboard_data",
]
