"""
===============================================================================
The Uncharted Route
Administrative Staff Management
===============================================================================
Administrative dashboard for managing internal staff operations.
Responsibilities
-----------------
• Staff dashboard
• Staff catalogue
• Staff profile/details
• Staff creation
• Staff editing
• Staff activation/deactivation
• Staff statistics
• Staff assignments
• Staff availability
• Staff schedules
• Staff performance

Business logic
--------------
Staff business logic is delegated to the Staff Service.

This route does not duplicate:
    • Staff validation
    • Staff status logic
    • Availability logic
    • Schedule logic
    • Assignment logic
    • Performance/statistics calculations

Customer-facing Experience Schedules are NOT part of this module.

StaffSchedule is an internal operational schedule for individual staff
members and remains intentionally separate from the removed
customer-facing ExperienceSchedule system.
"""

from datetime import datetime, time

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.decorators.admin import admin_required

from app.forms.admin_staff import (
    AdminStaffCreateForm,
    AdminStaffEditForm,
    AdminStaffFilterForm,
)
from app.models.staff import STAFF_TYPES, STAFF_STATUSES, EMPLOYMENT_TYPES

from app.services.staff_service import (
    STAFF_ROLES,
    StaffServiceError,
    activate_staff,
    create_availability,
    create_staff,
    create_staff_schedule,
    deactivate_staff,
    delete_availability,
    get_availability,
    get_staff,
    get_staff_assignments,
    get_staff_availability,
    get_staff_dashboard_data,
    get_staff_dashboard_statistics,
    get_staff_members,
    get_staff_schedules,
    get_staff_statistics,
    update_availability,
    update_staff,
    update_staff_schedule, StaffServiceError, create_staff_member,
)
from app.services.user_service import update_user
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================

staff_bp = Blueprint(
    "admin_staff",
    __name__,
    url_prefix="/admin/staff",
)


# =============================================================================
# Helpers
# =============================================================================


def _redirect_to_staff(staff):
    """
    Redirect to the Staff detail page.
    """

    return redirect(
        url_for(
            "admin_staff.detail",
            staff_id=staff.id,
        )
    )


def _get_staff_or_redirect(staff_id):
    """
    Retrieve a Staff member or redirect to the Staff catalogue.
    """

    staff = get_staff(staff_id)

    if staff is None:
        flash(
            "Staff member not found.",
            "danger",
        )

        return (
            None,
            redirect(
                url_for(
                    "admin_staff.index"
                )
            ),
        )

    return (
        staff,
        None,
    )


def _parse_date(value):
    """
    Safely parse an ISO date value.

    Returns None when no valid date is supplied.
    """

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (TypeError, ValueError):
        return None


def _parse_datetime(value):
    """
    Safely parse an HTML datetime-local value.

    Returns None when no valid value is supplied.
    """

    if not value:
        return None

    formats = (
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
    )

    for fmt in formats:
        try:
            return datetime.strptime(
                value,
                fmt,
            )
        except (TypeError, ValueError):
            continue

    return None


def _parse_time(value):
    """
    Safely parse an HTML time value.
    """

    if not value:
        return None

    formats = (
        "%H:%M",
        "%H:%M:%S",
    )

    for fmt in formats:
        try:
            return datetime.strptime(
                value,
                fmt,
            ).time()
        except (TypeError, ValueError):
            continue

    return None


# =============================================================================
# Staff Dashboard / Catalogue
# =============================================================================
@staff_bp.route("/")
@admin_required
def index():
    """
    Display the primary Staff Dashboard and catalogue.

    The Staff Index is the main Staff Management landing page.

    It contains:
        • Staff catalogue
        • Dashboard statistics
        • Staff filtering
        • Link to all-staff statistics
    """

    form = AdminStaffFilterForm(formdata=request.args)
    staff_members = get_staff_members(
        search=form.search.data,
        staff_type=form.staff_type.data,
        status=form.status.data,)

    dashboard = get_staff_dashboard_data()
    return render_template(
        "admin/staff/index.html",
        form=form,
        staff_members=staff_members,
        statistics=dashboard["statistics"],
        active_staff=dashboard["active_staff"],
        staff_roles=STAFF_ROLES,)

# =============================================================================
# Staff Detail
# =============================================================================
@staff_bp.route("/<int:staff_id>")
@admin_required
def detail(staff_id):
    """
    Display the Staff member's administrative profile hub.

    Individual operational areas are linked from this page:

        • Assignments
        • Availability
        • Schedule
        • Performance

    All-staff statistics remain on the separate Staff Statistics page.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    return render_template(
        "admin/staff/detail.html",
        staff=staff,
    )


# =============================================================================
# Staff Assignments
# =============================================================================
@staff_bp.route("/<int:staff_id>/assignments")
@admin_required
def assignments(staff_id):
    """
    Display assignments belonging to one Staff member.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    status = request.args.get(
        "status"
    ) or None

    role = request.args.get(
        "role"
    ) or None

    assignments = get_staff_assignments(
        staff,
        status=status,
        role=role,
    )

    total_assignments = len(
        assignments
    )

    active_statuses = {
        "Assigned",
        "Accepted",
        "In Progress",
    }

    active_assignments = sum(
        1
        for assignment in assignments
        if assignment.status in active_statuses
    )

    completed_assignments = sum(
        1
        for assignment in assignments
        if assignment.status == "Completed"
    )

    cancelled_assignments = sum(
        1
        for assignment in assignments
        if assignment.status == "Cancelled"
    )

    assignment_statistics = {
        "total": total_assignments,
        "active": active_assignments,
        "completed": completed_assignments,
        "cancelled": cancelled_assignments,
    }

    return render_template(
        "admin/staff/assignments.html",
        staff=staff,
        assignments=assignments,
        assignment_statistics=assignment_statistics,
        selected_status=status,
        selected_role=role,
    )


# =============================================================================
# Staff Availability
# =============================================================================
@staff_bp.route("/<int:staff_id>/availability",methods=["GET", "POST"],)
@admin_required
def availability(staff_id):
    """
    Display and create availability records for one Staff member.

    Availability is scoped to the selected Staff member.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    selected_date = _parse_date(
        request.args.get("date")
    )

    if selected_date is None:
        selected_date = datetime.utcnow().date()

    if request.method == "POST":

        date = _parse_date(
            request.form.get("date")
        )

        status = (
            request.form.get("status")
            or "Available"
        )

        start_time = _parse_time(
            request.form.get("start_time")
        )

        end_time = _parse_time(
            request.form.get("end_time")
        )

        reason = request.form.get(
            "reason"
        )

        if date is None:
            flash(
                "Please provide a valid availability date.",
                "danger",
            )

        else:

            try:

                create_availability(
                    staff=staff,
                    date=date,
                    status=status,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                )

                flash(
                    "Staff availability added successfully.",
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_staff.availability",
                        staff_id=staff.id,
                        date=date.isoformat(),
                    )
                )

            except StaffServiceError as exc:

                flash(
                    str(exc),
                    "danger",
                )

    availability_records = get_staff_availability(
        staff,
        selected_date,
    )

    availability_statuses = (
        "Available",
        "Unavailable",
        "On Leave",
        "Training",
        "Personal",
    )

    return render_template(
        "admin/staff/availability.html",
        staff=staff,
        selected_date=selected_date,
        availability_statuses=availability_statuses,
        availability_records=availability_records,
    )


# =============================================================================
# Edit Staff Availability
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/availability/<int:availability_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def availability_edit(
    staff_id,
    availability_id,
):
    """
    Edit an availability record belonging to a Staff member.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    availability_record = get_availability(
        availability_id
    )

    if (
        availability_record is None
        or availability_record.staff_id != staff.id
    ):
        flash(
            "Availability record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_staff.availability",
                staff_id=staff.id,
            )
        )

    if request.method == "POST":

        date = _parse_date(
            request.form.get("date")
        )

        start_time = _parse_time(
            request.form.get("start_time")
        )

        end_time = _parse_time(
            request.form.get("end_time")
        )

        status = (
            request.form.get("status")
            or availability_record.status
        )

        reason = request.form.get(
            "reason"
        )

        try:

            update_availability(
                availability_record,
                date=date,
                status=status,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
            )

            flash(
                "Staff availability updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_staff.availability",
                    staff_id=staff.id,
                    date=(
                        date.isoformat()
                        if date
                        else ""
                    ),
                )
            )

        except StaffServiceError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/staff/availability.html",
        staff=staff,
        selected_date=availability_record.date,
        availability_statuses=(
            "Available",
            "Unavailable",
            "On Leave",
            "Training",
            "Personal",
        ),
        availability_records=[
            availability_record
        ],
        editing_availability=availability_record,
    )


# =============================================================================
# Delete Staff Availability
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/availability/<int:availability_id>/delete",
    methods=["POST"],
)
@admin_required
def availability_delete(
    staff_id,
    availability_id,
):
    """
    Delete an availability record belonging to a Staff member.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    availability_record = get_availability(
        availability_id
    )

    if (
        availability_record is None
        or availability_record.staff_id != staff.id
    ):
        flash(
            "Availability record not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_staff.availability",
                staff_id=staff.id,
            )
        )

    try:

        delete_availability(
            availability_record
        )

        flash(
            "Staff availability deleted successfully.",
            "success",
        )

    except StaffServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_staff.availability",
            staff_id=staff.id,
        )
    )


# =============================================================================
# Staff Schedule
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/schedule"
)
@admin_required
def schedule(staff_id):
    """
    Display the internal operational schedule for one Staff member.

    This is NOT the removed customer-facing Experience Schedule system.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    start_date = _parse_date(
        request.args.get("start_date")
    )

    end_date = _parse_date(
        request.args.get("end_date")
    )

    status = request.args.get(
        "status"
    ) or None

    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.combine(
            start_date,
            time.min,
        )

    if end_date:
        end_datetime = datetime.combine(
            end_date,
            time.max,
        )

    schedules = get_staff_schedules(
        staff,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status=status,
    )

    schedule_statuses = (
        "Scheduled",
        "Completed",
        "Cancelled",
    )

    return render_template(
        "admin/staff/schedule.html",
        staff=staff,
        schedules=schedules,
        schedule_statuses=schedule_statuses,
        selected_start_date=start_date,
        selected_end_date=end_date,
        selected_status=status,
        create_schedule_url=url_for(
            "admin_staff.schedule_create",
            staff_id=staff.id,
        ),
        schedule_detail_url=lambda schedule_id: url_for(
            "admin_staff.schedule_detail",
            staff_id=staff.id,
            schedule_id=schedule_id,
        ),
        schedule_edit_url=lambda schedule_id: url_for(
            "admin_staff.schedule_edit",
            staff_id=staff.id,
            schedule_id=schedule_id,
        ),
        schedule_cancel_url=lambda schedule_id: url_for(
            "admin_staff.schedule_cancel",
            staff_id=staff.id,
            schedule_id=schedule_id,
        ),
    )


# =============================================================================
# Create Staff Schedule
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/schedule/create",
    methods=["GET", "POST"],
)
@admin_required
def schedule_create(staff_id):
    """
    Create an internal operational schedule for one Staff member.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        start_datetime = _parse_datetime(
            request.form.get(
                "start_datetime"
            )
        )

        end_datetime = _parse_datetime(
            request.form.get(
                "end_datetime"
            )
        )

        description = request.form.get(
            "description"
        )

        location = request.form.get(
            "location"
        )

        status = (
            request.form.get(
                "status"
            )
            or "Scheduled"
        )

        notes = request.form.get(
            "notes"
        )

        if start_datetime is None:
            flash(
                "Please provide a valid start date and time.",
                "danger",
            )

        else:

            try:

                create_staff_schedule(
                    staff=staff,
                    title=title,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    description=description,
                    location=location,
                    status=status,
                    notes=notes,
                )

                flash(
                    "Staff schedule created successfully.",
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_staff.schedule",
                        staff_id=staff.id,
                    )
                )

            except StaffServiceError as exc:

                flash(
                    str(exc),
                    "danger",
                )

    return render_template(
        "admin/staff/schedule.html",
        staff=staff,
        schedules=get_staff_schedules(
            staff
        ),
        schedule_statuses=(
            "Scheduled",
            "Completed",
            "Cancelled",
        ),
        create_schedule_url=url_for(
            "admin_staff.schedule_create",
            staff_id=staff.id,
        ),
    )


# =============================================================================
# Staff Schedule Detail
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/schedule/<int:schedule_id>"
)
@admin_required
def schedule_detail(
    staff_id,
    schedule_id,
):
    """
    Display one Staff schedule.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    from app.services.staff_service import get_schedule

    schedule_record = get_schedule(
        schedule_id
    )

    if (
        schedule_record is None
        or schedule_record.staff_id != staff.id
    ):
        flash(
            "Staff schedule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_staff.schedule",
                staff_id=staff.id,
            )
        )

    return render_template(
        "admin/staff/schedule.html",
        staff=staff,
        schedules=[
            schedule_record
        ],
        schedule_statuses=(
            "Scheduled",
            "Completed",
            "Cancelled",
        ),
        schedule_detail_url=lambda current_id: url_for(
            "admin_staff.schedule_detail",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
        schedule_edit_url=lambda current_id: url_for(
            "admin_staff.schedule_edit",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
        schedule_cancel_url=lambda current_id: url_for(
            "admin_staff.schedule_cancel",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
        create_schedule_url=url_for(
            "admin_staff.schedule_create",
            staff_id=staff.id,
        ),
    )


# =============================================================================
# Edit Staff Schedule
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/schedule/<int:schedule_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def schedule_edit(
    staff_id,
    schedule_id,
):
    """
    Edit an internal Staff schedule.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    from app.services.staff_service import get_schedule

    schedule_record = get_schedule(
        schedule_id
    )

    if (
        schedule_record is None
        or schedule_record.staff_id != staff.id
    ):
        flash(
            "Staff schedule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_staff.schedule",
                staff_id=staff.id,
            )
        )

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        start_datetime = _parse_datetime(
            request.form.get(
                "start_datetime"
            )
        )

        end_datetime = _parse_datetime(
            request.form.get(
                "end_datetime"
            )
        )

        status = (
            request.form.get(
                "status"
            )
            or schedule_record.status
        )

        description = request.form.get(
            "description"
        )

        location = request.form.get(
            "location"
        )

        notes = request.form.get(
            "notes"
        )

        try:

            update_staff_schedule(
                schedule_record,
                title=title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description=description,
                location=location,
                status=status,
                notes=notes,
            )

            flash(
                "Staff schedule updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_staff.schedule",
                    staff_id=staff.id,
                )
            )

        except StaffServiceError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/staff/schedule.html",
        staff=staff,
        schedules=[
            schedule_record
        ],
        schedule_statuses=(
            "Scheduled",
            "Completed",
            "Cancelled",
        ),
        create_schedule_url=url_for(
            "admin_staff.schedule_create",
            staff_id=staff.id,
        ),
        schedule_detail_url=lambda current_id: url_for(
            "admin_staff.schedule_detail",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
        schedule_edit_url=lambda current_id: url_for(
            "admin_staff.schedule_edit",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
        schedule_cancel_url=lambda current_id: url_for(
            "admin_staff.schedule_cancel",
            staff_id=staff.id,
            schedule_id=current_id,
        ),
    )


# =============================================================================
# Cancel Staff Schedule
# =============================================================================


@staff_bp.route(
    "/<int:staff_id>/schedule/<int:schedule_id>/cancel",
    methods=["POST"],
)
@admin_required
def schedule_cancel(
    staff_id,
    schedule_id,
):
    """
    Cancel an internal Staff schedule.
    """

    staff, response = _get_staff_or_redirect(
        staff_id
    )

    if response:
        return response

    from app.services.staff_service import (
        cancel_staff_schedule,
        get_schedule,
    )

    schedule_record = get_schedule(
        schedule_id
    )

    if (
        schedule_record is None
        or schedule_record.staff_id != staff.id
    ):
        flash(
            "Staff schedule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_staff.schedule",
                staff_id=staff.id,
            )
        )

    try:

        cancel_staff_schedule(
            schedule_record
        )

        flash(
            "Staff schedule cancelled successfully.",
            "success",
        )

    except StaffServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_staff.schedule",
            staff_id=staff.id,
        )
    )


# =============================================================================
# Staff Performance
# =============================================================================
@staff_bp.route("/<int:staff_id>/performance")
@admin_required
def performance(staff_id):
    """
    Display operational performance statistics for one Staff member.
    """
    staff, response = _get_staff_or_redirect(staff_id)
    if response:
        return response
    statistics = get_staff_statistics(staff)

    return render_template(
        "admin/staff/performance.html",
        staff=staff,
        statistics=statistics,)

@staff_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@admin_required
def create():
    """
    Create a new internal User account and linked Staff profile.
    """

    form = AdminStaffCreateForm()

    if form.validate_on_submit():

        try:

            staff = create_staff_member(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                phone=form.phone.data,
                is_verified=form.is_verified.data,

                employee_number=form.employee_number.data,
                staff_type=form.staff_type.data,
                department=form.department.data,
                job_title=form.job_title.data,
                employment_type=form.employment_type.data,
                hire_date=form.hire_date.data,
                status=form.status.data,

                skills=form.skills.data,
                languages=form.languages.data,
                certifications=form.certifications.data,
                qualifications=form.qualifications.data,

                emergency_contact_name=(
                    form.emergency_contact_name.data
                ),
                emergency_contact_phone=(
                    form.emergency_contact_phone.data
                ),
                emergency_contact_relationship=(
                    form.emergency_contact_relationship.data
                ),

                notes=form.notes.data,
                internal_notes=form.internal_notes.data,)

            flash(
                f"Staff member {staff.user.full_name} "
                "was created successfully.",
                "success",)

            return redirect(
                url_for(
                    "admin_staff.detail",
                    staff_id=staff.id,))

        except StaffServiceError as exc:
            flash(str(exc),"danger",)
        except ValueError as exc:
            flash(str(exc),"danger",)

    return render_template(
        "admin/staff/create.html",
        form=form,)
# =============================================================================
# Edit Staff
# =============================================================================
@staff_bp.route("/<int:staff_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(staff_id):
    """
    Edit an existing Staff profile and its linked User account.

    The Staff profile owns operational information such as:
    - employee number
    - staff type
    - department
    - job title
    - employment type
    - hire date
    - status
    - skills
    - languages
    - certifications
    - qualifications
    - emergency contact
    - notes

    The linked User account owns authentication/profile information such as:
    - first name
    - last name
    - username
    - email
    - phone
    - account status
    - verification status
    - password
    """

    staff, response = _get_staff_or_redirect(staff_id)

    if response:
        return response

    form = AdminStaffEditForm(obj=staff)

    # -------------------------------------------------------------------------
    # Populate linked User fields on GET
    # -------------------------------------------------------------------------

    if request.method == "GET" and staff.user:

        form.first_name.data = staff.user.first_name
        form.last_name.data = staff.user.last_name
        form.phone.data = staff.user.phone
        form.username.data = staff.user.username
        form.email.data = staff.user.email
        form.is_active.data = staff.user.is_active
        form.is_verified.data = staff.user.is_verified

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    if form.validate_on_submit():

        try:

            # ================================================================
            # Update linked User account
            # ================================================================

            if staff.user:

                update_user(
                    staff.user,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    email=form.email.data,
                    phone=form.phone.data,
                )

                staff.user.is_active = bool(form.is_active.data)
                staff.user.is_verified = bool(form.is_verified.data)

                if form.password.data:
                    staff.user.set_password(form.password.data)

            # ================================================================
            # Update Staff operational profile
            # ================================================================

            update_staff(
                staff,
                employee_number=form.employee_number.data,
                staff_type=form.staff_type.data,
                department=form.department.data,
                job_title=form.job_title.data,
                employment_type=form.employment_type.data,
                hire_date=form.hire_date.data,
                end_date=getattr(form, "end_date", None).data
                    if getattr(form, "end_date", None)
                    else None,
                status=form.status.data,
                skills=form.skills.data,
                languages=form.languages.data,
                certifications=form.certifications.data,
                qualifications=form.qualifications.data,
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone=form.emergency_contact_phone.data,
                emergency_contact_relationship=form.emergency_contact_relationship.data,
                notes=form.notes.data,
                internal_notes=form.internal_notes.data,
            )

            # update_user() currently commits the User transaction.
            # update_staff() commits the Staff transaction.
            # Both functions therefore complete successfully before we
            # redirect.

            flash(
                "Staff profile updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_staff.detail",
                    staff_id=staff.id,
                )
            )

        except ValueError as exc:

            db.session.rollback()

            flash(
                str(exc),
                "danger",
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update the staff profile. Please try again.",
                "danger",
            )

    return render_template(
        "admin/staff/edit.html",
        form=form,
        staff=staff,
        staff_types=STAFF_TYPES,
        staff_statuses=STAFF_STATUSES,
        employment_types=EMPLOYMENT_TYPES,)

# =============================================================================
# Deactivate Staff
# =============================================================================
@staff_bp.route("/<int:staff_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate(staff_id):
    """
    Deactivate a Staff member.
    """

    staff, response = _get_staff_or_redirect(staff_id)
    if response:
        return response
    try:

        deactivate_staff(staff)
        flash("Staff account deactivated successfully.","success",)

    except StaffServiceError as exc:
        flash(str(exc),"danger",)

    return _redirect_to_staff(staff)

# =============================================================================
# Activate Staff
# =============================================================================
@staff_bp.route("/<int:staff_id>/activate",methods=["POST"],)
@admin_required
def activate(staff_id):
    """
    Activate a Staff member.
    """
    staff, response = _get_staff_or_redirect(staff_id)
    if response:
        return response

    try:
        activate_staff(staff)
        flash("Staff account activated successfully.","success",)
    except StaffServiceError as exc:

        flash(str(exc),"danger",)
    return _redirect_to_staff(staff)

# =============================================================================
# Staff Statistics
# =============================================================================
@staff_bp.route("/statistics")
@admin_required
def statistics():
    """
    Display all-staff operational statistics.

    This page is intentionally separate from individual Staff performance.
    """

    statistics_data = get_staff_dashboard_statistics()
    return render_template(
        "admin/staff/statistics.html",
        statistics=statistics_data,)

# =============================================================================
# Public API
# =============================================================================
__all__ = ["staff_bp",]