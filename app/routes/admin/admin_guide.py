"""
===============================================================================
The Uncharted Route
Admin Guide Routes
===============================================================================

Administrative routes for Guide Dashboard management.

Responsibilities
----------------
• Guide dashboard
• Guide profile viewing
• Guide schedule management
• Guide assignment management
• Guide performance
• Guide availability
• Guide booking visibility

Architecture
------------

    Admin Guide Route
            ↓
        Admin Forms
            ↓
       Guide Service
            ↓
        Guide Models
            ↓
          Database

Important
---------
Business logic must remain inside guide_service.py.

Routes are responsible for:
    • Authentication
    • Authorization
    • Form handling
    • Calling services
    • Flash messages
    • Rendering templates
    • Redirecting users
"""

from datetime import datetime
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app, )
from flask_login import current_user, login_required, login_user
from app.forms.admin_guide import (
    GuideFilterForm,
    GuideCreateForm,
    GuideEditForm,
    GuideScheduleForm,
    GuideAssignmentForm,
    GuideAvailabilityForm,)
from app.models import User
from app.services import guide_service
from app.services.guide_service import (
    GuideServiceError,)
from extensions import db
from datetime import date

# =============================================================================
# Blueprint
# =============================================================================
admin_guide_bp = Blueprint(
    "admin_guide",
    __name__,
    url_prefix="/admin/guides",)

# =============================================================================
# Authorization
# =============================================================================
def _admin_required():
    """
    Ensure the current user has administrative/staff access.
    """
    if not current_user.is_authenticated:
        return False
    return current_user.is_staff

# =============================================================================
# Helper
# =============================================================================
def _permission_required(permission):
    """
    Check whether the current user has the requested permission.
    Administrators are allowed through automatically.
    """
    if not current_user.is_authenticated:
        return False
    if current_user.is_admin:
        return True
    return current_user.has_permission(permission)

# =============================================================================
# Guide Dashboard
# =============================================================================
@admin_guide_bp.route("/")
@login_required
def index():
    """
    Guide Dashboard.
    Displays:
        • Guide statistics
        • Active guides
        • Guide workload
        • Assignment information
        • Availability overview
    """
    if not _admin_required():
        flash("You do not have permission to access the Guide Dashboard.","danger",)

        return redirect(url_for("admin.dashboard"))
    if not _permission_required("guide.view"):
        flash("You do not have permission to view guides.","danger",)
        return redirect(url_for("admin.dashboard"))
    try:
        data = guide_service.get_guide_dashboard_data()
    except GuideServiceError as exc:
        flash(str(exc),"danger",)

        data = {
            "statistics": {},
            "guides": [],
            "active_guides": [],}
    return render_template("admin/guide/index.html",**data,)

# =============================================================================
# Guide Catalogue
# =============================================================================
@admin_guide_bp.route("/list", endpoint="list_guides")
@login_required
def list_guides():
    """Display the administrative Guide catalogue."""
    if not _admin_required():
        flash("You do not have permission to access guides.","danger",)
        return redirect(url_for("admin.dashboard"))
    if not _permission_required("guide.view"):
        flash("You do not have permission to view guides.","danger",)
        return redirect(url_for("admin.dashboard"))
    form = GuideFilterForm(request.args)

    try:
        guides = guide_service.list_guides(
            search=form.search.data,
            department=form.department.data,
            status=form.status.data,
            active_only=form.active_only.data,)

        dashboard_data = guide_service.get_guide_dashboard_data()
        # Start with the dashboard context, then override its
        # guides and form values with the filtered catalogue.
        template_context = dict(dashboard_data or {})
        template_context.update({
            "guides": guides,
            "form": form,})

    except GuideServiceError as exc:
        flash(str(exc), "danger")

        template_context = {
            "guides": [],
            "form": form,
            "statistics": {},
            "active_guides": [],
            "pending_assignments": [],
            "active_assignments": [],}
    return render_template("admin/guide/index.html",**template_context,)

# =============================================================================
# Edit Guide
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/edit", methods=["GET", "POST"])
@login_required
def edit(guide_id):
    """Edit an existing Guide operational profile."""
    if not _admin_required():
        flash("You do not have permission to edit guide profiles.","danger",)
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.edit"):
        flash("You do not have permission to edit guide profiles.","danger",)
        return redirect(url_for("admin.dashboard"))
    guide = guide_service.get_guide(guide_id)
    if guide is None:
        flash("Guide record not found.", "danger")
        return redirect(url_for("admin_guide.index"))
    form = GuideEditForm(obj=guide)
    # This form edits a Guide, not a conversion to another staff type.
    form.staff_type.choices = [("Guide", "Guide")]
    if form.validate_on_submit():
        try:
            guide_service.update_guide_profile(guide,form.data,)

            flash("Guide profile updated successfully.","success",)
            return redirect(
                url_for("admin_guide.detail",guide_id=guide.id,))
        except GuideServiceError as exc:
            flash(str(exc), "danger")

    elif form.is_submitted():
        flash("Please correct the errors in the form.","danger",)

    return render_template(
        "admin/guide/edit.html",
        guide=guide,
        form=form,)
# =============================================================================
# Guide Detail
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>")
@login_required
def detail(guide_id):
    """
    Display a complete Guide profile.
    """
    if not _admin_required():
        flash(
            "You do not have permission to access guide profiles.",
            "danger",)

        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.view"):
        flash("You do not have permission to view guide profiles.","danger",)
        return redirect(url_for("admin.dashboard"))

    guide = guide_service.get_guide(guide_id)

    if guide is None:
        flash("Guide record not found.","danger",)
        return redirect(url_for("admin_guide.index"))

    try:
        statistics = guide_service.get_guide_statistics(guide)
        assignments = guide_service.get_guide_assignments(guide)
        schedules = guide_service.get_guide_schedules(guide)
        availability = guide_service.get_guide_availability(guide,date.today(),)
    except GuideServiceError as exc:
        flash(str(exc),"danger",)

        statistics = {}
        assignments = []
        schedules = []
        availability = []
    return render_template(
        "admin/guide/detail.html",
        guide=guide,
        statistics=statistics,
        assignments=assignments,
        schedules=schedules,
        availability=availability,)

# =============================================================================
# Guide Schedule
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/schedule",methods=["GET", "POST"],)
@login_required
def schedule(guide_id):
    """
    Manage a Guide's operational schedule.
    GET
        Display existing schedules.
    POST
        Create a new schedule.
    """
    if not _admin_required():
        flash("You do not have permission to manage guide schedules.","danger",)
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.schedule"):
        flash("You do not have permission to manage guide schedules.","danger",)
        return redirect(url_for("admin.dashboard"))

    guide = guide_service.get_guide(guide_id)
    if guide is None:
        flash("Guide record not found.","danger",)

        return redirect(
            url_for("admin_guide.index"))

    form = GuideScheduleForm()
    if form.validate_on_submit():
        try:
            guide_service.create_guide_schedule(
                guide=guide,
                title=form.title.data,
                start_datetime=form.start_datetime.data,
                end_datetime=form.end_datetime.data,
                description=form.description.data,
                location=form.location.data,
                status=form.status.data,
                notes=form.notes.data,)

            flash("Guide schedule created successfully.","success",)

            return redirect(
                url_for(
                    "admin_guide.schedule",
                    guide_id=guide.id,))
        except GuideServiceError as exc:
            flash(str(exc),"danger",)
    try:
        schedules = guide_service.get_guide_schedules(guide)
    except GuideServiceError as exc:
        flash(str(exc),"danger",)
        schedules = []
    return render_template(
        "admin/guide/schedule.html",
        guide=guide,
        form=form,
        schedules=schedules,)

# =============================================================================
# Edit Guide Schedule
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/schedule/<int:schedule_id>/edit",methods=["GET", "POST"],)
@login_required
def edit_schedule(
    guide_id,
    schedule_id,):
    """
    Edit an existing Guide schedule.
    """

    if not _admin_required():
        flash("You do not have permission to manage guide schedules.","danger",)
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.schedule"):
        flash("You do not have permission to manage guide schedules.","danger",)

        return redirect(url_for("admin.dashboard"))
    guide = guide_service.get_guide(guide_id)

    schedule_record = guide_service.get_schedule(schedule_id)
    if guide is None or schedule_record is None:
        flash("Guide or schedule record not found.","danger",)

        return redirect(
            url_for("admin_guide.schedule",guide_id=guide_id,))

    form = GuideScheduleForm(
        obj=schedule_record)

    if form.validate_on_submit():
        try:
            guide_service.update_guide_schedule(
                schedule=schedule_record,
                title=form.title.data,
                start_datetime=form.start_datetime.data,
                end_datetime=form.end_datetime.data,
                description=form.description.data,
                location=form.location.data,
                status=form.status.data,
                notes=form.notes.data,)

            flash("Guide schedule updated successfully.","success",)

            return redirect(
                url_for("admin_guide.schedule",guide_id=guide.id,))

        except GuideServiceError as exc:

            flash(str(exc),"danger",)

    return render_template(
        "admin/guide/schedule.html",
        guide=guide,
        form=form,
        schedules=guide_service.get_guide_schedules(guide),
        editing_schedule=schedule_record,)

# =============================================================================
# Cancel Guide Schedule
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/schedule/<int:schedule_id>/cancel",methods=["POST"],)
@login_required
def cancel_schedule(
    guide_id,
    schedule_id,
):
    """
    Cancel a Guide schedule.
    """
    if not _admin_required():
        flash("You do not have permission to cancel guide schedules.","danger",)
        return redirect(url_for("admin.dashboard"))
    if not _permission_required("guide.schedule"):
        flash("You do not have permission to cancel guide schedules.","danger",)

        return redirect(url_for("admin.dashboard"))

    schedule_record = guide_service.get_schedule(schedule_id)

    if schedule_record is None:
        flash("Schedule record not found.","danger",)

        return redirect(
            url_for(
                "admin_guide.schedule",
                guide_id=guide_id,))

    try:

        guide_service.cancel_guide_schedule(
            schedule_record)

        flash("Guide schedule cancelled successfully.","success",)

    except GuideServiceError as exc:

        flash(str(exc),"danger",)

    return redirect(
        url_for(
            "admin_guide.schedule",
            guide_id=guide_id,
        )
    )

# =============================================================================
# Guide Assignments
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/assignments",methods=["GET", "POST"],)
@login_required
def assignments(guide_id):
    """
    Manage Guide assignments.

    Assignments connect Guides to Bookings.
    """

    if not _admin_required():
        flash(
            "You do not have permission to manage guide assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not _permission_required("guide.assign"):
        flash(
            "You do not have permission to manage guide assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    guide = guide_service.get_guide(
        guide_id
    )

    if guide is None:
        flash(
            "Guide record not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    form = GuideAssignmentForm()

    if form.validate_on_submit():

        try:

            booking = guide_service.get_booking(
                form.booking_id.data
            )

            if booking is None:
                raise GuideServiceError(
                    "Booking not found."
                )

            guide_service.assign_guide_to_booking(
                guide=guide,
                booking=booking,
                role=form.role.data,
                is_primary=form.is_primary.data,
                notes=form.notes.data,
                check_availability=form.check_availability.data,
            )

            flash(
                "Guide assigned to booking successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_guide.assignments",
                    guide_id=guide.id,))

        except GuideServiceError as exc:

            flash(
                str(exc),
                "danger",
            )

    try:

        assignments_list = guide_service.get_guide_assignments(guide)
    except GuideServiceError as exc:

        flash(str(exc),"danger",)
        assignments_list = []

    return render_template(
        "admin/guide/assignments.html",
        guide=guide,
        form=form,
        assignments=assignments_list,)

# =============================================================================
# Assignment Status
# =============================================================================
@admin_guide_bp.route("/assignments/<int:assignment_id>/status/<string:status>",methods=["POST"])
@login_required
def assignment_status(
    assignment_id,
    status,):
    """
    Update the operational status of a Guide assignment.
    """

    if not _admin_required():
        flash("You do not have permission to update assignments.","danger",)
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.assign"):
        flash("You do not have permission to update assignments.","danger",)

        return redirect(url_for("admin.dashboard"))
    assignment = guide_service.get_assignment(assignment_id)
    if assignment is None:
        flash("Assignment not found.","danger",)
        return redirect(url_for("admin_guide.index"))

    try:

        guide_service.update_assignment(
            assignment,
            status=status,
        )

        flash(
            "Guide assignment status updated.",
            "success",
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("admin_guide.index")
    )

# =============================================================================
# Accept Assignment
# =============================================================================
@admin_guide_bp.route("/assignments/<int:assignment_id>/accept",methods=["POST"],)
@login_required
def accept_assignment(
    assignment_id,
):
    """
    Accept a Guide assignment.
    """

    if not _admin_required():
        flash(
            "You do not have permission to update assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(
        assignment_id
    )

    if assignment is None:
        flash(
            "Assignment not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    try:

        guide_service.accept_assignment(
            assignment
        )

        flash(
            "Assignment accepted.",
            "success",
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("admin_guide.index")
    )

# =============================================================================
# Decline Assignment
# =============================================================================
@admin_guide_bp.route(
    "/assignments/<int:assignment_id>/decline",
    methods=["POST"],)
@login_required
def decline_assignment(
    assignment_id,
):
    """
    Decline a Guide assignment.
    """

    if not _admin_required():
        flash(
            "You do not have permission to update assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(
        assignment_id
    )

    if assignment is None:
        flash("Assignment not found.", "danger")
        return redirect(
            request.referrer or url_for("admin_guide.index")
        )

    try:

        guide_service.decline_assignment(
            assignment
        )

        flash(
            "Assignment declined.",
            "success",
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("admin_guide.index")
    )


# =============================================================================
# Start Assignment
# =============================================================================
@admin_guide_bp.route(
    "/assignments/<int:assignment_id>/start",
    methods=["POST"],)
@login_required
def start_assignment(
    assignment_id,
):
    """
    Mark a Guide assignment as In Progress.
    """

    if not _admin_required():
        flash(
            "You do not have permission to update assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(
        assignment_id
    )

    if assignment is None:
        flash(
            "Assignment not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    try:

        guide_service.start_assignment(
            assignment
        )

        flash(
            "Assignment marked as in progress.",
            "success",
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("admin_guide.index"))

# =============================================================================
# Complete Assignment
# =============================================================================
@admin_guide_bp.route("/assignments/<int:assignment_id>/complete",methods=["POST"],)
@login_required
def complete_assignment(
    assignment_id,
):
    """
    Mark a Guide assignment as completed.
    """

    if not _admin_required():
        flash(
            "You do not have permission to update assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(
        assignment_id
    )

    if assignment is None:
        flash(
            "Assignment not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    try:

        guide_service.complete_assignment(
            assignment
        )

        flash(
            "Assignment completed successfully.",
            "success",
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("admin_guide.index")
    )


# =============================================================================
# Cancel Assignment
# =============================================================================
@admin_guide_bp.route("/assignments/<int:assignment_id>/cancel",methods=["POST"],)
@login_required
def cancel_assignment(
    assignment_id,
):
    """
    Cancel a Guide assignment.
    """

    if not _admin_required():
        flash(
            "You do not have permission to update assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(assignment_id)
    if assignment is None:
        flash("Assignment not found.","danger",)
        return redirect(url_for("admin_guide.index"))

    try:

        guide_service.cancel_assignment(
            assignment
        )

        flash(
            "Assignment cancelled.",
            "success",)

    except GuideServiceError as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_guide.index"))

# =============================================================================
# Guide Performance
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/performance")
@login_required
def performance(
    guide_id,
):
    """
    Display Guide performance statistics.
    """

    if not _admin_required():
        flash(
            "You do not have permission to view guide performance.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not _permission_required("guide.performance"):
        flash(
            "You do not have permission to view guide performance.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    guide = guide_service.get_guide(
        guide_id
    )

    if guide is None:
        flash(
            "Guide record not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    try:

        statistics = guide_service.get_guide_statistics(
            guide
        )

        performance_data = (
            guide_service.get_guide_performance(
                guide
            )
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

        statistics = {}
        performance_data = {}

    return render_template(
        "admin/guide/performance.html",
        guide=guide,
        statistics=statistics,
        performance=performance_data,
    )


# =============================================================================
# Guide Availability
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/availability",methods=["GET", "POST"],)
@login_required
def availability(
    guide_id,
):
    """
    Manage Guide availability.
    """

    if not _admin_required():
        flash(
            "You do not have permission to manage guide availability.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not _permission_required("guide.availability"):
        flash(
            "You do not have permission to manage guide availability.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    guide = guide_service.get_guide(
        guide_id
    )

    if guide is None:
        flash(
            "Guide record not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    form = GuideAvailabilityForm()

    if form.validate_on_submit():

        try:

            guide_service.create_availability(
                guide=guide,
                date=form.date.data,
                status=form.status.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                reason=form.reason.data,
            )

            flash(
                "Guide availability record created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_guide.availability",
                    guide_id=guide.id,
                )
            )

        except GuideServiceError as exc:

            flash(
                str(exc),
                "danger",
            )

    try:

        availability_records = (
            guide_service.get_guide_availability(
                guide,
                date=date.today(),
            )
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

        availability_records = []

    return render_template(
        "admin/guide/availability.html",
        guide=guide,
        form=form,
        availability=availability_records,
    )


# =============================================================================
# Delete Availability
# =============================================================================
@admin_guide_bp.route("/availability/<int:availability_id>/delete",methods=["POST"],)
@login_required
def delete_availability(
    availability_id,
):
    """
    Delete a Guide availability record.
    """
    if not _admin_required():
        flash(
            "You do not have permission to manage guide availability.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    availability_record = (
        guide_service.get_availability(
            availability_id))

    if availability_record is None:
        flash(
            "Availability record not found.","danger",)

        return redirect(
            url_for("admin_guide.index"))

    try:

        guide_service.delete_availability(
            availability_record
        )

        flash("Availability record deleted successfully.","success",)

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",)

    return redirect(
        request.referrer
        or url_for("admin_guide.index"))

# =============================================================================
# Guide Bookings
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/booking")
@login_required
def bookings(
    guide_id,
):
    """
    Display booking assigned to a Guide.

    This is intentionally read-oriented.

    Booking creation, payment processing, cancellation, and financial
    operations remain part of Booking Management.
    """

    if not _admin_required():
        flash(
            "You do not have permission to view guide booking.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not _permission_required("guide.view"):
        flash(
            "You do not have permission to view guide booking.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    guide = guide_service.get_guide(
        guide_id
    )

    if guide is None:
        flash(
            "Guide record not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    status = request.args.get(
        "status"
    )

    start_date = request.args.get(
        "start_date"
    )

    end_date = request.args.get(
        "end_date"
    )

    search = request.args.get(
        "search"
    )

    try:

        bookings_list = guide_service.get_guide_bookings(
            guide=guide,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search,
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

        bookings_list = []

    return render_template(
        "admin/guide/booking.html",
        guide=guide,
        bookings=bookings_list,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search,)

# =============================================================================
# Guide Booking Detail
# =============================================================================
@admin_guide_bp.route("/<int:guide_id>/booking/<int:booking_id>")
@login_required
def booking_detail(
    guide_id,
    booking_id,
):
    """
    Display a booking from the Guide's operational perspective.

    Financial and full booking administration remain under Booking
    Management.
    """

    if not _admin_required():
        flash(
            "You do not have permission to view this booking.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    guide = guide_service.get_guide(
        guide_id
    )

    if guide is None:
        flash(
            "Guide record not found.",
            "danger",
        )

        return redirect(
            url_for("admin_guide.index")
        )

    try:

        booking = guide_service.get_guide_booking(
            guide=guide,
            booking_id=booking_id,
        )

    except GuideServiceError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_guide.booking",
                guide_id=guide.id,
            )
        )

    if booking is None:
        flash(
            "Booking not found or is not assigned to this guide.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_guide.booking",
                guide_id=guide.id,
            )
        )

    return render_template(
        "admin/guide/booking.html",
        guide=guide,
        booking=booking,
        bookings=[booking],
        detail_mode=True,)

# =============================================================================
# Remove Guide Assignment
# =============================================================================
@admin_guide_bp.route("/assignments/<int:assignment_id>/remove",methods=["POST"],)
@login_required
def remove_assignment(assignment_id):
    """
    Remove a Guide assignment.

    Intended for administrative correction rather than normal operational
    cancellation.
    """

    if not _admin_required():
        flash(
            "You do not have permission to remove guide assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not _permission_required("guide.assign"):
        flash(
            "You do not have permission to remove guide assignments.",
            "danger",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    assignment = guide_service.get_assignment(
        assignment_id
    )

    if assignment is None:
        flash(
            "Assignment not found.",
            "danger",)
        return redirect(url_for("admin_guide.index"))

    try:
        guide_service.remove_guide_assignment(assignment)
        flash("Guide assignment removed successfully.","success",)
    except GuideServiceError as exc:
        flash(str(exc),"danger",)

    return redirect(
        request.referrer
        or url_for("admin_guide.index"))

from app.forms.guide_invitation_forms import (
    GuideInvitationForm,
    AcceptGuideInvitationForm,
)
from app.services.guide_invitation_service import (
    GuideInvitationError,
    create_pending_guide,
    generate_guide_invitation_token,
    verify_guide_invitation_token,
    accept_guide_invitation,
)

# This assumes app.services exports an instance named email_service.
from app.services import email_service


# =============================================================================
# Guide Invitations
# =============================================================================

@admin_guide_bp.route("/invite", methods=["GET", "POST"])
@login_required
def invite_guide():
    """Allow authorized administrators to invite a new guide."""

    if not _admin_required():
        flash(
            "You do not have permission to invite guides.",
            "danger",
        )
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.manage"):
        flash(
            "You do not have permission to manage guide invitations.",
            "danger",
        )
        return redirect(url_for("admin.dashboard"))

    form = GuideInvitationForm()

    if form.validate_on_submit():
        try:
            user = create_pending_guide(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                employee_number=form.employee_number.data,
                department=form.department.data,
                job_title=form.job_title.data,
                employment_type=form.employment_type.data,
            )

            token = generate_guide_invitation_token(user)

            invitation_url = url_for(
                "admin_guide.accept_guide_invitation",
                token=token,
                _external=True,
            )

            try:
                email_sent = email_service.send_guide_invitation_email(
                    user,
                    invitation_url,
                )
            except Exception:
                current_app.logger.exception(
                    "Guide invitation email failed for user_id=%s",
                    user.id,
                )
                email_sent = False

            if email_sent:
                flash(
                    f"Guide account created. An invitation was sent to "
                    f"{user.email}. The account remains inactive until "
                    "the guide accepts.",
                    "success",
                )
            else:
                flash(
                    f"The pending guide account for {user.email} was "
                    "created, but the invitation email could not be sent. "
                    "Please retry the invitation.",
                    "warning",
                )

            return redirect(url_for("admin_guide.list_guides"))

        except GuideInvitationError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Unable to create a guide invitation."
            )
            flash(
                "The guide invitation could not be created. "
                "Please try again.",
                "danger",
            )

    return render_template(
        "admin/guide/invite.html",
        form=form,
    )


@admin_guide_bp.route(
    "/invitation/<token>",
    methods=["GET", "POST"],
    endpoint="accept_guide_invitation",
)
def accept_guide_invitation_route(token):
    """
    Allow an invited guide to set a password and activate their account.

    A valid invitation token authorizes access to this endpoint.
    Successful acceptance signs the guide in and directs them to the
    guide portal instead of the public homepage.
    """

    user = verify_guide_invitation_token(token)

    if user is None:
        flash(
            "This invitation is invalid, expired, or already used. "
            "Please contact the administrator for a new invitation.",
            "danger",
        )

        return (
            render_template(
                "auth/accept_guide_invitation.html",
                form=AcceptGuideInvitationForm(),
                invitation_valid=False,
            ),
            400,
        )

    form = AcceptGuideInvitationForm()

    if form.validate_on_submit():
        try:
            accepted_user = accept_guide_invitation(
                token,
                form.password.data,
            )

            if accepted_user is None:
                raise GuideInvitationError(
                    "The invitation could not be completed. "
                    "Please request a new invitation."
                )

            # Confirm that the accepted account is associated with a
            # Guide staff profile before entering the guide portal.
            staff_profile = accepted_user.staff_profile

            if (
                staff_profile is None
                or staff_profile.staff_type != "Guide"
            ):
                current_app.logger.error(
                    "Accepted guide account has no valid Guide staff "
                    "profile. user_id=%s",
                    accepted_user.id,
                )

                flash(
                    "Your account was activated, but your guide profile "
                    "has not been linked correctly. Please contact the "
                    "administrator so this can be resolved.",
                    "warning",
                )

                return redirect(url_for("auth.login"))

            # The invitation token and password setup have been validated.
            # Sign in the accepted guide and send them to the portal.
            login_user(accepted_user, fresh=True)

            flash(
                "Your guide account is active. Welcome to "
                "The Uncharted Route Guide Portal.",
                "success",
            )

            return redirect(url_for("guide_portal.dashboard"))

        except GuideInvitationError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Guide invitation acceptance failed."
            )
            flash(
                "Your account could not be activated. Please try again.",
                "danger",
            )

    return render_template(
        "auth/accept_guide_invitation.html",
        form=form,
        invitation_valid=True,
    )


@admin_guide_bp.route(
    "/<int:user_id>/resend-invitation",
    methods=["POST"],
)
@login_required
def resend_guide_invitation(user_id):
    """Resend an invitation for an existing pending guide account."""

    if not _admin_required():
        flash(
            "You do not have permission to resend guide invitations.",
            "danger",
        )
        return redirect(url_for("admin.dashboard"))

    if not _permission_required("guide.manage"):
        flash(
            "You do not have permission to manage guide invitations.",
            "danger",
        )
        return redirect(url_for("admin.dashboard"))

    user = db.session.get(User, user_id)

    if (
        user is None
        or user.normalized_role != "guide"
        or user.is_active
        or user.is_verified
        or user.staff_profile is None
        or user.staff_profile.staff_type != "Guide"
    ):
        flash(
            "No eligible pending guide invitation was found.",
            "warning",
        )
        return redirect(url_for("admin_guide.list_guides"))

    try:
        token = generate_guide_invitation_token(user)

        invitation_url = url_for(
            "admin_guide.accept_guide_invitation",
            token=token,
            _external=True,
        )

        email_sent = email_service.send_guide_invitation_email(
            user,
            invitation_url,
        )

        if email_sent:
            flash(
                f"A new invitation was sent to {user.email}.",
                "success",
            )
        else:
            flash(
                f"The email could not be sent to {user.email}. "
                "Check your email configuration and try again.",
                "danger",
            )

    except Exception:
        current_app.logger.exception(
            "Unable to resend guide invitation for user_id=%s",
            user.id,
        )
        flash(
            "Unable to resend the invitation. Please try again.",
            "danger",
        )

    return redirect(url_for("admin_guide.list_guides"))

# =============================================================================
# Blueprint Export
# =============================================================================
__all__ = [
    "admin_guide_bp",
]