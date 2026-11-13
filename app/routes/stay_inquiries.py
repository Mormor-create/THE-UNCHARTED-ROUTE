"""
===============================================================================
The Uncharted Route
Public Stay Inquiry Routes
===============================================================================
Handles public accommodation inquiries separately from stay booking.
"""
from datetime import date
import html
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.forms.stay_inquiry import StayInquiryForm
from app.models import Stay, StayRoom
from app.models.stay_inquiry import StayInquiry
from app.services.email_service import email_service
from app.services.stay_service import get_stay_by_slug

stay_inquiries_bp = Blueprint(
    "stay_inquiries",
    __name__,
    url_prefix="/stays",)

# =============================================================================
# Email Notifications
# =============================================================================
def _send_stay_inquiry_emails(inquiry, stay):
    """Notify the customer and TUR team after a stay inquiry is saved."""

    try:
        customer_name = inquiry.full_name or "Traveller"

        # ---------------------------------------------------------------------
        # Resolve Stay name
        # ---------------------------------------------------------------------
        stay_name = (
            getattr(stay, "name", None)
            or getattr(stay, "title", None)
            or getattr(stay, "property_name", None)
            or "Selected stay"
        )

        # ---------------------------------------------------------------------
        # Resolve Room name from the saved room_id.
        #
        # room_id is the authoritative room selection stored on the inquiry.
        # ---------------------------------------------------------------------
        room = (
            db.session.get(StayRoom, inquiry.room_id)
            if inquiry.room_id
            else None
        )

        room_name = (
            getattr(room, "name", None)
            or getattr(room, "title", None)
            or "Any suitable room"
        )

        reference = f"STAY-{inquiry.id}"

        check_in = (
            inquiry.check_in.strftime("%d %B %Y")
            if inquiry.check_in
            else "Not specified"
        )

        check_out = (
            inquiry.check_out.strftime("%d %B %Y")
            if inquiry.check_out
            else "Not specified"
        )

        currency = (
            getattr(inquiry, "preferred_currency", None)
            or "KES"
        )

        phone = (
            getattr(inquiry, "phone", None)
            or "Not provided"
        )

        special_requests = (
            inquiry.special_requests
            or "None provided"
        )

        admin_recipient = (
            current_app.config.get("MAIL_ADMIN_RECIPIENT")
            or current_app.config.get("MAIL_CONTACT_RECIPIENT")
        )

        # ---------------------------------------------------------------------
        # Internal TUR notification
        # ---------------------------------------------------------------------
        internal_message = (
            "NEW STAY INQUIRY — THE UNCHARTED ROUTE\n\n"
            f"Reference: {reference}\n"
            f"Customer: {customer_name}\n"
            f"Email: {inquiry.email}\n"
            f"Phone: {phone}\n\n"
            f"Stay: {stay_name}\n"
            f"Room: {room_name}\n"
            f"Check-in: {check_in}\n"
            f"Check-out: {check_out}\n"
            f"Adults: {inquiry.adults}\n"
            f"Children: {inquiry.children}\n"
            f"Preferred currency: {currency}\n\n"
            f"Special requests:\n{special_requests}\n\n"
            f"Status: {getattr(inquiry, 'status', 'New')}\n"
            "Please follow up with the customer."
        )

        try:
            sent = email_service.send_admin_notification(
                subject=f"New Stay Inquiry — {reference}",
                message=internal_message,
                recipient=admin_recipient,
            )

            if not sent:
                current_app.logger.error(
                    "Stay inquiry team notification failed: %s",
                    reference,
                )

        except Exception:
            current_app.logger.exception(
                "Error sending stay inquiry team notification: %s",
                reference,
            )

        # ---------------------------------------------------------------------
        # Customer acknowledgement
        # ---------------------------------------------------------------------
        safe_name = html.escape(str(customer_name))
        safe_reference = html.escape(str(reference))
        safe_stay = html.escape(str(stay_name))
        safe_room = html.escape(str(room_name))
        safe_check_in = html.escape(str(check_in))
        safe_check_out = html.escape(str(check_out))
        safe_currency = html.escape(str(currency))

        customer_body = (
            f"Hello {customer_name},\n\n"
            f"Thank you for enquiring about {stay_name} with "
            "The Uncharted Route.\n"
            "We have received your inquiry and our team will review "
            "your request before getting back to you.\n\n"
            f"Inquiry reference: {reference}\n"
            f"Stay: {stay_name}\n"
            f"Room: {room_name}\n"
            f"Check-in: {check_in}\n"
            f"Check-out: {check_out}\n"
            f"Adults: {inquiry.adults}\n"
            f"Children: {inquiry.children}\n"
            f"Preferred currency: {currency}\n\n"
            "This acknowledges receipt of your inquiry; it is not a "
            "confirmed reservation or final quotation. Our team will "
            "contact you to discuss availability and details.\n\n"
            "Explore. Experience. Remember.\n"
            "The Uncharted Route"
        )

        customer_html = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.7;
                    color:#1C2822;max-width:640px;margin:0 auto;">

            <div style="background:#12372A;color:#FFFFFF;padding:24px;">
                <h2 style="margin:0;">The Uncharted Route</h2>

                <p style="margin:6px 0 0;">
                    Explore. Experience. Remember.
                </p>
            </div>

            <div style="padding:24px;background:#F7F1E5;">

                <h2>We've received your stay inquiry</h2>

                <p>Hello {safe_name},</p>

                <p>
                    Thank you for your interest. Our team has received
                    your inquiry and will review your request before
                    getting back to you.
                </p>

                <div style="background:#FFFFFF;padding:18px;border-radius:8px;">

                    <p>
                        <strong>Inquiry reference:</strong>
                        {safe_reference}
                    </p>

                    <p>
                        <strong>Stay:</strong>
                        {safe_stay}
                    </p>

                    <p>
                        <strong>Room:</strong>
                        {safe_room}
                    </p>

                    <p>
                        <strong>Check-in:</strong>
                        {safe_check_in}
                    </p>

                    <p>
                        <strong>Check-out:</strong>
                        {safe_check_out}
                    </p>

                    <p>
                        <strong>Preferred currency:</strong>
                        {safe_currency}
                    </p>

                </div>

                <p>
                    This email confirms receipt of your inquiry, not a
                    confirmed reservation. Our team will contact you to
                    discuss availability and details.
                </p>

                <p>
                    <strong>The Uncharted Route</strong><br>
                    Explore. Experience. Remember.
                </p>

            </div>
        </div>
        """

        try:
            sent = email_service.send_email(
                recipient=inquiry.email,
                subject=f"Stay Inquiry Received — {reference}",
                body=customer_body,
                html_body=customer_html,
                reply_to=current_app.config.get("MAIL_DEFAULT_SENDER"),
            )

            if not sent:
                current_app.logger.error(
                    "Stay inquiry acknowledgement failed: %s",
                    reference,
                )

        except Exception:
            current_app.logger.exception(
                "Error sending stay inquiry acknowledgement: %s",
                reference,
            )

    except Exception:
        # Email failure must never turn a successful database submission
        # into a failed inquiry.
        current_app.logger.exception(
            "Stay inquiry notification processing failed: %s",
            getattr(inquiry, "id", None),
        )


# =============================================================================
# Public Stay Inquiry
# =============================================================================

@stay_inquiries_bp.route(
    "/<string:slug>/enquire",
    methods=["GET", "POST"],
)
def enquire(slug):
    """Submit an inquiry about an accommodation property."""

    # -------------------------------------------------------------------------
    # Resolve stay
    # -------------------------------------------------------------------------
    stay = get_stay_by_slug(slug)

    if not stay or not stay.active:
        abort(404)

    form = StayInquiryForm()

    # -------------------------------------------------------------------------
    # Load active rooms for this stay.
    #
    # Room selection is always restricted to rooms belonging to this property.
    # -------------------------------------------------------------------------
    active_rooms = stay.rooms.filter_by(active=True).all()

    # -------------------------------------------------------------------------
    # Determine whether the visitor arrived from a specific room page.
    #
    # This is used on GET to populate the hidden room_id field.
    # -------------------------------------------------------------------------
    requested_room_id = request.args.get(
        "room_id",
        type=int,
    )

    selected_room = None

    if requested_room_id:
        selected_room = next(
            (
                room
                for room in active_rooms
                if room.id == requested_room_id
            ),
            None,
        )

    # -------------------------------------------------------------------------
    # GET: carry the selected room into the form.
    #
    # This means a room page such as:
    #
    # /stays/example-stay/enquire?room_id=7
    #
    # renders the form with:
    #
    # room_id = 7
    # -------------------------------------------------------------------------
    if request.method == "GET" and selected_room:
        form.room_id.data = str(selected_room.id)

    # -------------------------------------------------------------------------
    # POST: validate the submitted form.
    # -------------------------------------------------------------------------
    if form.validate_on_submit():

        # ---------------------------------------------------------------------
        # Read the room_id submitted by the browser.
        #
        # IMPORTANT:
        # We deliberately read this from the submitted WTForms field rather
        # than request.args because the room selection is carried through
        # the POST body.
        # ---------------------------------------------------------------------
        raw_room_id = (
            form.room_id.data or ""
        ).strip()

        selected_room_id = None

        # ---------------------------------------------------------------------
        # Convert room_id to an integer.
        # ---------------------------------------------------------------------
        if raw_room_id:

            try:
                selected_room_id = int(raw_room_id)

            except (TypeError, ValueError):

                form.room_id.errors.append(
                    "The selected room is invalid."
                )

                return render_template(
                    "stays/enquiry.html",
                    stay=stay,
                    form=form,
                    selected_room=None,
                )

        # ---------------------------------------------------------------------
        # Verify the selected room belongs to this stay and is active.
        #
        # This prevents somebody from submitting an arbitrary room_id.
        # ---------------------------------------------------------------------
        if selected_room_id is not None:

            selected_room = next(
                (
                    room
                    for room in active_rooms
                    if room.id == selected_room_id
                ),
                None,
            )

            if selected_room is None:

                form.room_id.errors.append(
                    "The selected room is not available for this stay."
                )

                return render_template(
                    "stays/enquiry.html",
                    stay=stay,
                    form=form,
                    selected_room=None,
                )

        # ---------------------------------------------------------------------
        # Create inquiry.
        #
        # The validated selected_room_id is now written directly to room_id.
        # ---------------------------------------------------------------------
        inquiry = StayInquiry(
            stay_id=stay.id,
            room_id=selected_room_id,
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=(
                (form.phone.data or "").strip()
                or None
            ),
            country=(
                (form.country.data or "").strip()
                or None
            ),
            check_in=form.check_in.data,
            check_out=form.check_out.data,
            adults=form.adults.data,
            children=form.children.data,
            preferred_currency=form.preferred_currency.data,
            special_requests=(
                (form.special_requests.data or "").strip()
                or None
            ),
            status="New",
            source="Website",
        )

        # ---------------------------------------------------------------------
        # Save inquiry
        # ---------------------------------------------------------------------
        try:
            db.session.add(inquiry)
            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()

            flash(
                "We couldn't submit your inquiry right now. "
                "Please try again.",
                "error",
            )

        else:

            # -----------------------------------------------------------------
            # Send notifications only after successful database save.
            # -----------------------------------------------------------------
            _send_stay_inquiry_emails(
                inquiry,
                stay,
            )

            flash(
                "Your stay inquiry has been submitted. "
                "Our team will follow up with you.",
                "success",
            )

            return redirect(
                url_for(
                    "stay_inquiries.enquire",
                    slug=stay.slug,
                )
            )

    # -------------------------------------------------------------------------
    # Render form
    # -------------------------------------------------------------------------
    return render_template(
        "stays/enquiry.html",
        stay=stay,
        form=form,
        selected_room=selected_room,
    )


__all__ = ["stay_inquiries_bp"]