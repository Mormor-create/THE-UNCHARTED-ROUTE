"""
===============================================================================
The Uncharted Route
Public Promotion Routes
===============================================================================

Public-facing promotion pages and customer promotion inquiries.

Customers can:
    - Browse current published promotions.
    - View individual promotion details.
    - Submit inquiries about active promotions.

Promotion inquiries do not create bookings or reservations.
===============================================================================
"""

import html
import logging
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,)
from app.forms.promotion_forms import PromotionInquiryForm
from app.models.promotion import Promotion
from app.services.email_service import (
    send_admin_notification,
    send_email,)
from app.services.promotion_service import PromotionService

logger = logging.getLogger(__name__)

promotions_bp = Blueprint(
    "promotions",
    __name__,
    url_prefix="/offers",)

# =============================================================================
# PUBLIC PROMOTION LISTING
# =============================================================================
@promotions_bp.route("/")
def index():
    """Display current published offers."""

    promotions = (
        PromotionService.get_public_query()
        .order_by(
            Promotion.show_on_homepage.desc(),
            Promotion.created_at.desc(),
            Promotion.id.desc(),).all())

    return render_template(
        "promotions/index.html",
        promotions=promotions,)

# =============================================================================
# PUBLIC PROMOTION DETAIL
# =============================================================================
@promotions_bp.route("/<slug>", methods=["GET"])
def detail(slug):
    """Display one current published offer and its inquiry form."""

    promotion = (
        PromotionService.get_public_query()
        .filter_by(slug=slug)
        .first())

    if promotion is None:
        abort(404)
    form = PromotionInquiryForm()

    return render_template(
        "promotions/detail.html",
        promotion=promotion,
        form=form,)

# =============================================================================
# PROMOTION INQUIRY EMAILS
# =============================================================================
def _send_promotion_inquiry_emails(inquiry):
    """
    Send an internal notification and customer acknowledgement.
    Email failures are logged independently. They must never undo an
    inquiry that has already been saved successfully.
    """

    customer_name = inquiry.customer_name
    customer_email = inquiry.email
    customer_phone = inquiry.phone or "Not provided"
    customer_country = inquiry.country or "Not provided"
    contact_method = inquiry.preferred_contact_method
    promotion_title = inquiry.promotion_title
    message = inquiry.message

    # -------------------------------------------------------------------------
    # Internal notification
    # -------------------------------------------------------------------------

    internal_subject = (
        f"New Promotion Inquiry: {promotion_title}")

    internal_message = f"""
A new promotion inquiry has been submitted through The Uncharted Route.

INQUIRY DETAILS
---------------
Inquiry Reference: #{inquiry.id}
Promotion: {promotion_title}

CUSTOMER DETAILS
----------------
Name: {customer_name}
Email: {customer_email}
Phone: {customer_phone}
Country: {customer_country}
Preferred Contact Method: {contact_method}

CUSTOMER MESSAGE
----------------
{message}

Please log in to the administration dashboard to review this inquiry,
update its status and record any follow-up notes.

Promotion Inquiry Management:
{url_for('admin_promotions.inquiries', _external=True)}
"""

    try:
        internal_sent = send_admin_notification(
            subject=internal_subject,
            message=internal_message,
        )

        if not internal_sent:
            logger.warning(
                "Internal email notification was not delivered "
                "for promotion inquiry #%s.",
                inquiry.id,
            )

    except Exception:
        logger.exception(
            "Failed to send internal notification for promotion inquiry #%s.",
            inquiry.id,
        )

    # -------------------------------------------------------------------------
    # Customer acknowledgement
    # -------------------------------------------------------------------------

    customer_subject = (
        f"We've received your inquiry | {promotion_title}"
    )

    safe_name = html.escape(customer_name)
    safe_title = html.escape(promotion_title)
    safe_message = html.escape(message).replace("\n", "<br>")

    customer_text = f"""
Hello {customer_name},

Thank you for your interest in The Uncharted Route.

We have successfully received your inquiry about:

{promotion_title}

Your inquiry reference is #{inquiry.id}.

Our team will review your message and get back to you using your
preferred contact method: {contact_method}.

Your message:
{message}

Thank you for considering The Uncharted Route.

Explore. Experience. Remember.

The Uncharted Route
"""

    customer_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Promotion Inquiry Received</title>
</head>

<body style="margin:0;padding:0;background-color:#F7F1E5;
             font-family:Arial,Helvetica,sans-serif;color:#1C2822;">

    <div style="max-width:620px;margin:35px auto;background:#FFFFFF;
                border-radius:16px;overflow:hidden;
                border:1px solid #E9DDC8;">

        <div style="padding:32px;background-color:#12372A;text-align:center;">
            <p style="margin:0;color:#D89B24;font-size:12px;
                      font-weight:bold;letter-spacing:3px;">
                THE UNCHARTED ROUTE
            </p>

            <h1 style="margin:18px 0 0;color:#FFFFFF;
                       font-size:25px;line-height:1.4;">
                We've received your inquiry!
            </h1>
        </div>

        <div style="padding:32px;">

            <p style="font-size:15px;line-height:1.8;">
                Hello <strong>{safe_name}</strong>,
            </p>

            <p style="font-size:15px;line-height:1.8;">
                Thank you for your interest in The Uncharted Route.
                Your promotion inquiry has been received successfully.
            </p>

            <div style="margin:25px 0;padding:22px;
                        background-color:#F7F1E5;border-radius:12px;">

                <p style="margin:0;color:#66736B;font-size:11px;
                          font-weight:bold;letter-spacing:1px;">
                    YOUR INQUIRY
                </p>

                <h2 style="margin:10px 0;color:#12372A;font-size:19px;">
                    {safe_title}
                </h2>

                <p style="margin:0;color:#66736B;font-size:13px;">
                    Reference: #{inquiry.id}
                </p>
            </div>

            <p style="font-size:14px;line-height:1.8;">
                <strong>Your message:</strong><br>
                {safe_message}
            </p>

            <p style="font-size:14px;line-height:1.8;">
                Our team will review your inquiry and get back to you
                using your preferred contact method:
                <strong>{html.escape(contact_method)}</strong>.
            </p>

            <p style="font-size:14px;line-height:1.8;">
                Thank you for considering us. We look forward to helping
                you plan something memorable.
            </p>

            <div style="margin-top:30px;padding-top:22px;
                        border-top:1px solid #E9DDC8;">

                <p style="margin:0;color:#12372A;font-weight:bold;">
                    The Uncharted Route
                </p>

                <p style="margin:7px 0 0;color:#66736B;font-size:12px;">
                    Explore. Experience. Remember.
                </p>
            </div>

        </div>
    </div>

</body>
</html>
"""

    try:
        customer_sent = send_email(
            recipient=customer_email,
            subject=customer_subject,
            body=customer_text,
            html_body=customer_html,)

        if not customer_sent:
            logger.warning(
                "Customer acknowledgement was not delivered "
                "for promotion inquiry #%s.",
                inquiry.id,
            )

    except Exception:
        logger.exception(
            "Failed to send customer acknowledgement "
            "for promotion inquiry #%s.",
            inquiry.id,)

# =============================================================================
# SUBMIT PROMOTION INQUIRY
# =============================================================================
@promotions_bp.route("/<slug>/inquire",methods=["POST"],)
def submit_inquiry(slug):
    """
    Save a customer inquiry for an active promotion.
    This endpoint does not create a booking, reservation or payment.
    """
    promotion = (
        PromotionService.get_public_query()
        .filter_by(slug=slug)
        .first())

    if promotion is None:
        abort(404)

    form = PromotionInquiryForm()

    if not form.validate_on_submit():
        flash(
            "Please review the form and correct the highlighted fields.",
            "error",)

        return render_template(
            "promotions/detail.html",
            promotion=promotion,
            form=form,), 400

    try:
        inquiry = PromotionService.create_promotion_inquiry(
            promotion=promotion,
            form=form,)

        if inquiry is None:
            flash("We could not submit your inquiry. Please try again.","error",)

            return redirect(
                url_for(
                    "promotions.detail",
                    slug=promotion.slug,))

    except Exception:
        logger.exception(
            "Could not save promotion inquiry for promotion #%s.",
            promotion.id,)

        flash(
            "Something went wrong while submitting your inquiry. "
            "Please try again.",
            "error",)

        return redirect(
            url_for(
                "promotions.detail",
                slug=promotion.slug,))

    # The service is expected to commit the inquiry before returning it.
    # Email failures must not undo the saved inquiry.
    _send_promotion_inquiry_emails(inquiry)
    flash(
        "Thank you! Your inquiry has been received. "
        "We've sent a confirmation to your email address.",
        "success",)

    return redirect(
        url_for(
            "promotions.detail",
            slug=promotion.slug,)
        + "#promotion-inquiry")