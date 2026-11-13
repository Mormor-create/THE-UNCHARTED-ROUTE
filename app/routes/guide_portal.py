"""
===============================================================================
The Uncharted Route
Guide Portal Routes
===============================================================================
Private self-service portal for authenticated guides.
Guides can view their own operational dashboard and access their own
assignments, booking, schedules, and availability.
Administrative guide management remains in admin_guide.py.
"""

from datetime import date
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,)
from flask_login import current_user, login_required

from app.models import BookingRequest
from app.services import guide_service
from app.services.guide_service import GuideServiceError
from app.models.contact import Contact
from flask import request
from app.forms.contact import ContactReplyForm
from app.services.contact_service import ContactService
from app.services.contact_reply_service import ContactReplyService
from extensions import db

guide_portal_bp = Blueprint(
    "guide_portal",
    __name__,
    url_prefix="/guide-portal",)

# =============================================================================
# Authorization
# =============================================================================
def _get_current_guide():
    """
    Return the authenticated user's own Guide Staff profile.
    Never accept a guide ID from a URL or form to determine portal ownership.
    """
    if not current_user.is_authenticated:
        abort(401)

    # Support both normalized_role and the underlying role field.
    user_role = (
        getattr(current_user, "normalized_role", None)
        or getattr(current_user, "role", None)
    )

    if not isinstance(user_role, str) or user_role.strip().lower() != "guide":
        abort(403)

    if not getattr(current_user, "is_active", False):
        abort(403)

    # Retrieve the guide profile linked to the authenticated user.
    guide = guide_service.get_guide_by_user(current_user)

    if guide is None:
        current_app.logger.warning(
            "Guide portal access denied: no Guide Staff profile found "
            "for user ID %s.",
            current_user.id,
        )
        abort(403)

    if getattr(guide, "user_id", None) != current_user.id:
        current_app.logger.warning(
            "Guide portal access denied: guide profile ownership mismatch "
            "for user ID %s.",
            current_user.id,
        )
        abort(403)

    if getattr(guide, "staff_type", None) != "Guide":
        abort(403)

    if getattr(guide, "status", None) != "Active":
        abort(403)

    return guide


def _get_owned_assignment(guide, assignment_id):
    """
    Retrieve an assignment only if it belongs to the current guide.
    """
    assignment = guide_service.get_assignment(assignment_id)

    if assignment is None:
        abort(404)
    if assignment.staff_id != guide.id:
        abort(404)
    return assignment

# =============================================================================
# Guide-owned Contact Enquiries
# =============================================================================
def _get_owned_contact(contact_id):
    """
    Retrieve a non-archived enquiry assigned to the authenticated guide.
    Guides may only access enquiries assigned through assigned_user_id.
    The legacy assigned_to string is deliberately not used for authorization.
    """
    contact = (
        Contact.query
        .filter(
            Contact.id == contact_id,
            Contact.assigned_user_id == current_user.id,
            Contact.is_archived.is_(False),
        )
        .first())

    if contact is None:
        # Do not reveal whether another guide owns the enquiry.
        abort(404)

    return contact

# =============================================================================
# Dashboard
# =============================================================================
@guide_portal_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    """Display the current guide's personal dashboard."""
    guide = _get_current_guide()
    # Enquiries assigned directly to the authenticated guide.
    try:
        assigned_contacts = (
            Contact.query
            .filter(
                Contact.assigned_user_id == current_user.id,
                Contact.is_archived.is_(False),
            )
            .order_by(Contact.created_at.desc())
            .all()
        )
    except Exception:
        current_app.logger.exception(
            "Unable to load assigned enquiries for user ID %s.",
            current_user.id,
        )
        assigned_contacts = []

    try:
        dashboard_data = guide_service.get_guide_dashboard_for(guide)
        schedules = guide_service.get_guide_schedules(guide)
        availability = guide_service.get_guide_availability(guide,date=date.today(),)
        bookings = guide_service.get_guide_bookings(guide=guide,)

    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load guide portal dashboard for guide ID %s.",
            guide.id,)

        flash("Some dashboard information could not be loaded. Please try again.","warning",)
        dashboard_data = {
            "guide": guide,
            "statistics": {},
            "upcoming_bookings": [],
            "current_bookings": [],
            "pending_assignments": [],
            "active_assignments": [],}

        schedules = []
        availability = []
        bookings = []

    return render_template(
        "guide_portal/dashboard.html",
        guide=guide,
        statistics=dashboard_data["statistics"],
        assigned_contacts=assigned_contacts,
        upcoming_bookings=dashboard_data["upcoming_bookings"],
        current_bookings=dashboard_data["current_bookings"],
        pending_assignments=dashboard_data["pending_assignments"],
        active_assignments=dashboard_data["active_assignments"],
        schedules=schedules,
        availability=availability,
        bookings=bookings,
        today=date.today(),)

# =============================================================================
# Assignment Actions
# =============================================================================
@guide_portal_bp.route(
    "/assignments/<int:assignment_id>/accept",
    methods=["POST"],)
@login_required
def accept(assignment_id):
    """Accept an assignment belonging to the current guide."""
    guide = _get_current_guide()
    assignment = _get_owned_assignment(guide, assignment_id)

    try:
        guide_service.accept_assignment(assignment)
        flash("Assignment accepted successfully.", "success")

    except GuideServiceError as exc:
        flash(str(exc), "warning")

    return redirect(url_for("guide_portal.dashboard"))

@guide_portal_bp.route(
    "/assignments/<int:assignment_id>/decline",
    methods=["POST"],)
@login_required
def decline(assignment_id):
    """Decline an assignment belonging to the current guide."""
    guide = _get_current_guide()
    assignment = _get_owned_assignment(guide, assignment_id)

    try:
        guide_service.decline_assignment(assignment)
        flash("Assignment declined.", "success")

    except GuideServiceError as exc:
        flash(str(exc), "warning")

    return redirect(url_for("guide_portal.dashboard"))

@guide_portal_bp.route(
    "/assignments/<int:assignment_id>/start",
    methods=["POST"],)
@login_required
def start(assignment_id):
    """Start an assignment belonging to the current guide."""
    guide = _get_current_guide()
    assignment = _get_owned_assignment(guide, assignment_id)

    try:
        guide_service.start_assignment(assignment)
        flash("Assignment marked as in progress.", "success")

    except GuideServiceError as exc:
        flash(str(exc), "warning")

    return redirect(url_for("guide_portal.dashboard"))

@guide_portal_bp.route(
    "/assignments/<int:assignment_id>/complete",
    methods=["POST"],)
@login_required
def complete(assignment_id):
    """Complete an assignment belonging to the current guide."""
    guide = _get_current_guide()
    assignment = _get_owned_assignment(guide, assignment_id)

    try:
        guide_service.complete_assignment(assignment)
        flash("Assignment marked as completed.", "success")

    except GuideServiceError as exc:
        flash(str(exc), "warning")

    return redirect(url_for("guide_portal.dashboard"))

# =============================================================================
# Booking Details
# =============================================================================

# =============================================================================
# My Bookings
# =============================================================================
@guide_portal_bp.route("/booking", methods=["GET"])
@login_required
def bookings():
    """
    Display booking assigned to the authenticated guide.

    The guide can only see booking returned by the guide service
    for their own Staff profile.
    """
    guide = _get_current_guide()

    try:
        bookings_list = guide_service.get_guide_bookings(guide=guide)

    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load booking for guide ID %s.",
            guide.id,
        )
        flash(
            "Your booking could not be loaded. Please try again.",
            "warning",
        )
        bookings_list = []

    return render_template(
        "guide_portal/booking.html",
        guide=guide,
        bookings=bookings_list,
        today=date.today(),
    )

@guide_portal_bp.route("/booking/<int:booking_id>",methods=["GET"],)
@login_required
def booking_detail(booking_id):
    """
    Show a booking only when it is assigned to the current guide.
    """
    guide = _get_current_guide()
    booking = guide_service.get_guide_booking(
        guide=guide,
        booking_id=booking_id,)

    if booking is None:
        abort(404)

    assignments = guide_service.get_guide_assignments(guide)

    assignment = next(
        (
            item
            for item in assignments
            if item.booking_id == booking.id
        ),
        None,)

    return render_template(
        "guide_portal/booking_detail.html",
        guide=guide,
        booking=booking,
        assignment=assignment,)

# =============================================================================
# Ready-to-Book Handoff
# =============================================================================
@guide_portal_bp.route("/enquiries/<int:contact_id>/ready-to-book",methods=["GET", "POST"],)
@login_required
def ready_to_book(contact_id):
    """
    Submit an assigned client enquiry for administrative booking review.

    This creates a BookingRequest only. It does not create or confirm
    a Booking and does not reserve availability.
    """
    guide = _get_current_guide()
    contact = _get_owned_contact(contact_id)

    existing_request = BookingRequest.query.filter_by(
        contact_id=contact.id
    ).first()

    # Prevent accidental duplicate handoffs.
    if existing_request is not None:
        flash(
            "A booking request already exists for this enquiry. "
            "Please contact the admin team if it needs changing.",
            "info",
        )
        return redirect(
            url_for(
                "guide_portal.enquiry_detail",
                contact_id=contact.id,
            )
        )

    if request.method == "POST":
        booking_type = request.form.get("booking_type", "").strip()
        service_name = request.form.get("service_name", "").strip()
        start_date_raw = request.form.get(
            "preferred_start_date", ""
        ).strip()
        end_date_raw = request.form.get(
            "preferred_end_date", ""
        ).strip()
        details = request.form.get("request_details", "").strip()

        allowed_booking_types = {
            "experience",
            "destination_journey",
            "stay",
        }

        errors = []

        if booking_type not in allowed_booking_types:
            errors.append("Select a valid booking category.")

        if not service_name:
            errors.append("Enter the agreed service or experience.")

        if not details:
            errors.append(
                "Summarise the details discussed and agreed with the client."
            )

        def read_count(field_name, label, minimum):
            raw_value = request.form.get(field_name, "").strip()

            try:
                value = int(raw_value)
            except (TypeError, ValueError):
                errors.append(f"{label} must be a whole number.")
                return minimum

            if value < minimum:
                errors.append(f"{label} cannot be less than {minimum}.")

            return value

        adults = read_count("adults", "Adults", 1)
        children = read_count("children", "Children", 0)
        infants = read_count("infants", "Infants", 0)

        preferred_start_date = None
        preferred_end_date = None

        if start_date_raw:
            try:
                preferred_start_date = date.fromisoformat(start_date_raw)
            except ValueError:
                errors.append("Enter a valid preferred start date.")

        if end_date_raw:
            try:
                preferred_end_date = date.fromisoformat(end_date_raw)
            except ValueError:
                errors.append("Enter a valid preferred end date.")

        if (
            preferred_start_date
            and preferred_end_date
            and preferred_end_date < preferred_start_date
        ):
            errors.append(
                "The preferred end date cannot be before the start date."
            )

        if request.form.get("client_agreed") != "yes":
            errors.append(
                "Confirm that you discussed these proposed details with the client."
            )

        if errors:
            for error in errors:
                flash(error, "warning")

            return render_template(
                "guide_portal/ready_to_book.html",
                guide=guide,
                contact=contact,
                form_data=request.form,
            )

        try:
            # Re-check inside the transaction to protect against duplicate
            # submissions. The database unique constraint is the final guard.
            duplicate = BookingRequest.query.filter_by(
                contact_id=contact.id
            ).first()

            if duplicate is not None:
                flash(
                    "A booking request has already been submitted for this enquiry.",
                    "info",
                )
                return redirect(
                    url_for(
                        "guide_portal.enquiry_detail",
                        contact_id=contact.id,
                    )
                )

            booking_request = BookingRequest(
                contact_id=contact.id,
                guide_user_id=current_user.id,
                booking_type=booking_type,
                service_name=service_name,
                preferred_start_date=preferred_start_date,
                preferred_end_date=preferred_end_date,
                adults=adults,
                children=children,
                infants=infants,
                request_details=details,
                status="Pending Review",
            )

            db.session.add(booking_request)

            # Keep the original enquiry visible to the admin team as ready
            # for handoff. The request record remains the structured queue item.
            contact.status = "Ready to Book"

            db.session.commit()

            flash(
                "Booking request submitted for admin review. "
                "No reservation has been created or confirmed.",
                "success",
            )

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to submit booking request for contact %s "
                "by guide user %s.",
                contact.id,
                current_user.id,
            )
            flash(
                "The booking request could not be submitted. Please try again.",
                "danger",
            )

        return redirect(
            url_for(
                "guide_portal.enquiry_detail",
                contact_id=contact.id,
            )
        )

    return render_template(
        "guide_portal/ready_to_book.html",
        guide=guide,
        contact=contact,
        form_data={},
    )

# =============================================================================
# My Assignments
# =============================================================================
@guide_portal_bp.route("/assignments", methods=["GET"])
@login_required
def assignments():
    """Display assignments belonging to the authenticated guide."""
    guide = _get_current_guide()

    try:
        assignments_list = guide_service.get_guide_assignments(guide)
    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load assignments for guide ID %s.",
            guide.id,
        )
        flash("Your assignments could not be loaded. Please try again.", "warning")
        assignments_list = []

    return render_template(
        "guide_portal/assignments.html",
        guide=guide,
        assignments=assignments_list,)

@guide_portal_bp.route("/assignments/<int:assignment_id>",methods=["GET"],)
@login_required
def assignment_detail(assignment_id):
    """Display an individual assignment owned by the current guide."""
    guide = _get_current_guide()
    assignment = _get_owned_assignment(guide, assignment_id)

    return render_template(
        "guide_portal/assignment_detail.html",
        guide=guide,
        assignment=assignment,)

# =============================================================================
# Upcoming Tours
# =============================================================================
@guide_portal_bp.route("/tours", methods=["GET"])
@login_required
def upcoming_tours():
    """Display upcoming tours assigned to the current guide."""
    guide = _get_current_guide()

    try:
        tours = guide_service.get_upcoming_bookings(guide)

    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load upcoming tours for guide ID %s.",
            guide.id,)
        flash("Your upcoming tours could not be loaded.", "warning")
        tours = []

    return render_template(
        "guide_portal/upcoming_tours.html",
        guide=guide,
        tours=tours,
        today=date.today(),)

# =============================================================================
# My Schedule
# =============================================================================
@guide_portal_bp.route("/schedule", methods=["GET"])
@login_required
def schedule():
    """Display the authenticated guide's schedule."""

    guide = _get_current_guide()

    try:
        schedules = guide_service.get_guide_schedules(guide)

    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load schedule for guide ID %s.",
            guide.id,
        )
        flash("Your schedule could not be loaded.", "warning")
        schedules = []

    return render_template(
        "guide_portal/schedule.html",
        guide=guide,
        schedules=schedules,
        today=date.today(),)

# =============================================================================
# My Availability
# =============================================================================
@guide_portal_bp.route("/availability", methods=["GET"])
@login_required
def availability():
    """Display the authenticated guide's availability records."""

    guide = _get_current_guide()

    try:
        availability_records = guide_service.get_guide_availability(
            guide,
            date=date.today(),
        )

    except GuideServiceError:
        current_app.logger.exception(
            "Unable to load availability for guide ID %s.",
            guide.id,
        )
        flash("Your availability could not be loaded.", "warning")
        availability_records = []

    return render_template(
        "guide_portal/availability.html",
        guide=guide,
        availability=availability_records,
        today=date.today(),)

# =============================================================================
# My Client Enquiries
# =============================================================================
@guide_portal_bp.route("/enquiries", methods=["GET"])
@login_required
def enquiries():
    """List non-archived enquiries assigned to the current guide."""
    guide = _get_current_guide()
    query = Contact.query.filter(
        Contact.assigned_user_id == current_user.id,
        Contact.is_archived.is_(False),)

    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    if status:
        query = query.filter(Contact.status == status)

    if search:
        term = f"%{search}%"

        query = query.filter(
            db.or_(
                Contact.subject.ilike(term),
                Contact.first_name.ilike(term),
                Contact.last_name.ilike(term),
                Contact.email.ilike(term),))

    assigned_contacts = (
        query
        .order_by(Contact.created_at.desc())
        .all())

    return render_template(
        "guide_portal/enquiries.html",
        guide=guide,
        assigned_contacts=assigned_contacts,
        selected_status=status,
        search=search,)

# =============================================================================
# Guide Enquiry Conversation
# =============================================================================
@guide_portal_bp.route("/enquiries/<int:contact_id>",methods=["GET"],)
@login_required
def enquiry_detail(contact_id):
    """Display the conversation for an enquiry assigned to this guide."""

    guide = _get_current_guide()
    contact = _get_owned_contact(contact_id)

    try:
        conversation = ContactReplyService.get_conversation(contact.id)

    except Exception:
        current_app.logger.exception(
            "Unable to load conversation for contact ID %s.",
            contact.id,
        )
        flash("The enquiry conversation could not be loaded.", "warning")
        conversation = []

    form = ContactReplyForm()

    if not form.subject.data:
        form.subject.data = (
            f"Re: {contact.subject}"
            if contact.subject
            else "Re: Your enquiry"
        )

    booking_request = BookingRequest.query.filter_by(
        contact_id=contact.id
    ).first()

    return render_template(
        "guide_portal/enquiry_detail.html",
        guide=guide,
        contact=contact,
        booking_request=booking_request,
        conversation=conversation,
        form=form,)

# =============================================================================
# Reply to an Assigned Enquiry
# =============================================================================
@guide_portal_bp.route("/enquiries/<int:contact_id>/reply",methods=["POST"],)
@login_required
def reply_to_enquiry(contact_id):
    """Send a reply to a client for an enquiry assigned to this guide."""
    _get_current_guide()
    contact = _get_owned_contact(contact_id)
    form = ContactReplyForm()

    if not form.validate_on_submit():
        flash("Please correct the reply form and try again.", "warning")
        return redirect(
            url_for(
                "guide_portal.enquiry_detail",
                contact_id=contact.id,))

    try:
        reply = ContactReplyService.create_reply(
            contact_id=contact.id,
            user_id=current_user.id,
            sender_name=current_user.full_name,
            sender_email=current_user.email,
            subject=form.subject.data,
            message=form.message.data,
            delivery_method="Email",)

        if form.send_email.data:
            ContactReplyService.send_reply(
                reply.id,
                sender=current_user.email,
                reply_to=contact.email,)
            flash("Your reply has been submitted to the email service.","success",)

        else:
            flash("Your reply was saved without sending an email.","success",)

    except Exception:
        current_app.logger.exception(
            "Guide reply failed for contact ID %s, user ID %s.",
            contact.id,
            current_user.id,)
        flash("The reply could not be processed. Please try again.","danger",)

    return redirect(
        url_for(
            "guide_portal.enquiry_detail",
            contact_id=contact.id,))

__all__ = ["guide_portal_bp"]
