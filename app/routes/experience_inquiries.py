
"""
===============================================================================
The Uncharted Route
Public Experience Inquiry Routes
===============================================================================
Handles public experience inquiries and post-submission email notifications.
"""

import html
import logging
from datetime import date
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError
from app.forms.experience_inquiry import ExperienceInquiryForm
from app.models import Experience, ExperienceInquiry
from app.services.email_service import email_service
from extensions import db

logger = logging.getLogger(__name__)

experience_inquiries_bp = Blueprint(
    "experience_inquiries",
    __name__,
    url_prefix="/experiences",
)


def _format_date(value):
    return value.strftime("%d %B %Y") if value else "Not specified"


def _send_experience_inquiry_emails(inquiry, experience):
    """Send customer acknowledgement and internal notification."""
    try:
        customer_name = inquiry.full_name or "Traveller"
        experience_name = (
            getattr(experience, "title", None)
            or getattr(experience, "name", None)
            or "Selected experience"
        )
        reference = (
            getattr(inquiry, "inquiry_reference", None)
            or f"EXP-{inquiry.id}"
        )
        preferred_date = _format_date(
            getattr(inquiry, "preferred_date", None)
        )
        adults = getattr(inquiry, "adults", 0) or 0
        children = getattr(inquiry, "children", 0) or 0
        infants = getattr(inquiry, "infants", 0) or 0
        currency = (
            getattr(inquiry, "preferred_currency", None)
            or getattr(inquiry, "currency", None)
            or "KES"
        )
        special_requests = (
            getattr(inquiry, "special_requests", None)
            or "None provided"
        )
        phone = getattr(inquiry, "phone", None) or "Not provided"

        admin_recipient = (
            current_app.config.get("MAIL_ADMIN_RECIPIENT")
            or current_app.config.get("MAIL_CONTACT_RECIPIENT")
        )

        internal_message = (
            "NEW EXPERIENCE INQUIRY — THE UNCHARTED ROUTE\n\n"
            f"Reference: {reference}\n"
            f"Customer: {customer_name}\n"
            f"Email: {inquiry.email}\n"
            f"Phone: {phone}\n\n"
            f"Experience: {experience_name}\n"
            f"Preferred date: {preferred_date}\n"
            f"Adults: {adults}\n"
            f"Children: {children}\n"
            f"Infants: {infants}\n"
            f"Preferred currency: {currency}\n\n"
            f"Special requests:\n{special_requests}\n\n"
            f"Status: {getattr(inquiry, 'status', 'New')}\n"
            "Please follow up with the customer."
        )

        try:
            sent = email_service.send_admin_notification(
                subject=f"New Experience Inquiry — {reference}",
                message=internal_message,
                recipient=admin_recipient,
            )
            if not sent:
                current_app.logger.error(
                    "Experience inquiry team notification failed: %s",
                    reference,
                )
        except Exception:
            current_app.logger.exception(
                "Error sending experience inquiry team notification: %s",
                reference,
            )

        safe_name = html.escape(str(customer_name))
        safe_reference = html.escape(str(reference))
        safe_experience = html.escape(str(experience_name))
        safe_date = html.escape(str(preferred_date))
        safe_currency = html.escape(str(currency))

        customer_body = (
            f"Hello {customer_name},\n\n"
            "Thank you for enquiring about an experience with "
            "The Uncharted Route.\n"
            "We have received your inquiry and our team will review "
            "your preferences before getting back to you.\n\n"
            f"Inquiry reference: {reference}\n"
            f"Experience: {experience_name}\n"
            f"Preferred date: {preferred_date}\n"
            f"Adults: {adults}\n"
            f"Children: {children}\n"
            f"Infants: {infants}\n"
            f"Preferred currency: {currency}\n\n"
            "This is an acknowledgement of receipt, not a confirmed "
            "booking or final quotation. Our team will contact you "
            "to discuss the details.\n\n"
            "Explore. Experience. Remember.\n"
            "The Uncharted Route"
        )

        customer_html = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.7;
                    color:#1C2822;max-width:640px;margin:0 auto;">
            <div style="background:#12372A;color:#FFFFFF;padding:24px;">
                <h2 style="margin:0;">The Uncharted Route</h2>
                <p style="margin:6px 0 0;">Explore. Experience. Remember.</p>
            </div>
            <div style="padding:24px;background:#F7F1E5;">
                <h2>We've received your experience inquiry</h2>
                <p>Hello {safe_name},</p>
                <p>
                    Thank you for your interest. Our team has received
                    your inquiry and will review your preferences before
                    getting back to you.
                </p>
                <div style="background:#FFFFFF;padding:18px;border-radius:8px;">
                    <p><strong>Inquiry reference:</strong> {safe_reference}</p>
                    <p><strong>Experience:</strong> {safe_experience}</p>
                    <p><strong>Preferred date:</strong> {safe_date}</p>
                    <p><strong>Preferred currency:</strong> {safe_currency}</p>
                </div>
                <p>
                    This email confirms receipt of your inquiry. It is not
                    a confirmed booking or final quotation. We'll contact
                    you to discuss the details.
                </p>
                <p><strong>The Uncharted Route</strong><br>
                Explore. Experience. Remember.</p>
            </div>
        </div>
        """

        try:
            sent = email_service.send_email(
                recipient=inquiry.email,
                subject=f"Experience Inquiry Received — {reference}",
                body=customer_body,
                html_body=customer_html,
                reply_to=current_app.config.get("MAIL_DEFAULT_SENDER"),
            )
            if not sent:
                current_app.logger.error(
                    "Experience inquiry acknowledgement failed: %s",
                    reference,
                )
        except Exception:
            current_app.logger.exception(
                "Error sending experience inquiry acknowledgement: %s",
                reference,
            )

    except Exception:
        # The inquiry is already committed. Email errors must not undo it.
        current_app.logger.exception(
            "Experience inquiry notification processing failed: %s",
            getattr(inquiry, "id", None),
        )


@experience_inquiries_bp.route("/<slug>/enquire",methods=["GET", "POST"],)
def enquire(slug):
    """Display the inquiry form and accept experience inquiries."""
    experience = Experience.query.filter_by(
        slug=slug,
        active=True,
    ).first_or_404()

    form = ExperienceInquiryForm()

    if form.validate_on_submit():
        preferred_date = form.preferred_date.data

        if preferred_date and preferred_date < date.today():
            flash("The preferred date cannot be in the past.", "danger")
            return render_template(
                "experiences/enquire.html",
                experience=experience,
                form=form,
            )

        inquiry = ExperienceInquiry(
            experience_id=experience.id,
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=(form.phone.data or "").strip() or None,
            country=(
                form.country.data.strip()
                if getattr(form, "country", None)
                and form.country.data
                else None
            ),
            preferred_date=preferred_date,
            adults=form.adults.data,
            children=form.children.data,
            infants=form.infants.data,
            preferred_currency=(
                getattr(form, "preferred_currency", None).data
                if getattr(form, "preferred_currency", None)
                else "KES"
            ),
            special_requests=(
                (form.special_requests.data or "").strip() or None
            ),
            status="New",
            source="Website",
        )

        try:
            db.session.add(inquiry)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to save experience inquiry."
            )
            flash(
                "We couldn't submit your inquiry. Please try again.",
                "danger",
            )
            return render_template(
                "experiences/enquire.html",
                experience=experience,
                form=form,
            )

        # Send notifications only after the database commit succeeds.
        _send_experience_inquiry_emails(inquiry, experience)

        reference = (
            getattr(inquiry, "inquiry_reference", None)
            or f"EXP-{inquiry.id}"
        )
        flash(
            f"Your inquiry has been submitted successfully. "
            f"Reference: {reference}",
            "success",
        )
        return redirect(url_for(
            "experience_inquiries.enquire",
            slug=experience.slug,
        ))


    return render_template(
        "experiences/enquiry.html",
        experience=experience,
        form=form,)

__all__ = ["experience_inquiries_bp"]
