"""
===============================================================================
The Uncharted Route
Email Service
===============================================================================
Centralized email delivery service for transactional and marketing emails.
Supported email types:
- Account verification
- Password reset
- Booking confirmation
- Booking cancellation
- Contact enquiry notification
- Newsletter emails
- Administrative notifications
- Guide invitations
Configuration is loaded from environment variables:

MAIL_SERVER
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
MAIL_USE_TLS
MAIL_USE_SSL
MAIL_DEFAULT_SENDER
MAIL_DEFAULT_SENDER_NAME
"""
import os
import smtplib
import logging
from email.message import EmailMessage
from email.utils import formataddr
import re
import secrets
from datetime import datetime
from html import escape
from urllib.parse import urlparse
from flask import current_app, url_for
from itsdangerous import URLSafeSerializer

# =============================================================================
# Logging
# =============================================================================
logger = logging.getLogger(__name__)

# =============================================================================
# Email Service
# =============================================================================
class EmailService:
    """Centralized email delivery service."""

    # =========================================================================
    # Initialization
    # =========================================================================
    def __init__(self):
        """Initialize email configuration from environment variables."""

        self.mail_server = os.getenv(
            "MAIL_SERVER",
            "localhost",
        )

        self.mail_port = int(
            os.getenv(
                "MAIL_PORT",
                "587",
            )
        )

        self.mail_username = os.getenv("MAIL_USERNAME")
        self.mail_password = os.getenv("MAIL_PASSWORD")

        self.use_tls = self._get_bool(
            "MAIL_USE_TLS",
            True,
        )

        self.use_ssl = self._get_bool(
            "MAIL_USE_SSL",
            False,
        )

        self.default_sender = os.getenv(
            "MAIL_DEFAULT_SENDER",
        "theunchartedrouteke@gmail.com",)

        self.default_sender_name = os.getenv(
            "MAIL_DEFAULT_SENDER_NAME",
            "The Uncharted Route",
        )

        if self.use_tls and self.use_ssl:
            logger.warning(
                "MAIL_USE_TLS and MAIL_USE_SSL are both enabled. "
                "SSL delivery will take precedence."
            )

    # =========================================================================
    # Configuration Helpers
    # =========================================================================
    @staticmethod
    def _get_bool(
        name: str,
        default: bool = False,
    ) -> bool:
        """Convert an environment variable into a boolean."""

        value = os.getenv(name)

        if value is None:
            return default

        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    # =========================================================================
    # Sender
    # =========================================================================
    @property
    def sender(self) -> str:
        """Return the formatted default sender."""
        return formataddr(
            (
                self.default_sender_name,
                self.default_sender,))

    # =========================================================================
    # Recipient Helpers
    # =========================================================================
    @staticmethod
    def _normalize_recipients(recipients) -> list:
        """Normalize a single recipient or a collection of recipients."""

        if not recipients:
            return []

        if isinstance(recipients, str):
            recipient = recipients.strip()
            return [recipient] if recipient else []

        return [
            str(email).strip()
            for email in recipients
            if email and str(email).strip()
        ]

    # =========================================================================
    # Core Email Method
    # =========================================================================
    def send_email(
        self,
        recipient,
        subject: str,
        body: str,
        html_body: str = None,
        sender: str = None,
        reply_to: str = None,
        cc=None,
        bcc=None,
        message_id :str=None) -> bool:
        """
        Send a plain-text email, optionally with an HTML alternative.
        Returns True if the SMTP server accepts the message; otherwise False.
        """
        try:
            recipients = self._normalize_recipients(recipient)

            if not recipients:
                logger.warning(
                    "Email not sent: no recipient supplied.")
                return False

            cc_recipients = self._normalize_recipients(cc)
            bcc_recipients = self._normalize_recipients(bcc)

            all_recipients = (
                recipients
                + cc_recipients
                + bcc_recipients)

            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = sender or self.sender
            message["To"] = ", ".join(recipients)

            if message_id:
                message["Message-ID"] = message_id

            if reply_to:
                message["Reply-To"] = reply_to

            if cc_recipients:
                message["Cc"] = ", ".join(cc_recipients)

            message.set_content(body or "")

            if html_body:
                message.add_alternative(
                    html_body,
                    subtype="html",
                )

            self._deliver(
                message,
                all_recipients,
            )

            logger.info(
                "Email successfully sent to %s",
                ", ".join(recipients),
            )

            return True

        except Exception:
            logger.exception(
                "Failed to send email to %s",
                recipient,
            )
            return False

    # =========================================================================
    # SMTP Delivery
    # =========================================================================
    def _deliver(
        self,
        message: EmailMessage,
        recipients: list,
    ) -> None:
        """Deliver an email using SMTP."""

        if self.use_ssl:
            with smtplib.SMTP_SSL(
                self.mail_server,
                self.mail_port,
                timeout=30,
            ) as smtp:
                self._authenticate(smtp)
                smtp.send_message(
                    message,
                    to_addrs=recipients,
                )
            return

        with smtplib.SMTP(
            self.mail_server,
            self.mail_port,
            timeout=30,
        ) as smtp:
            if self.use_tls:
                smtp.starttls()

            self._authenticate(smtp)

            smtp.send_message(
                message,
                to_addrs=recipients,
            )

    # =========================================================================
    # SMTP Authentication
    # =========================================================================
    def _authenticate(self, smtp) -> None:
        """Authenticate when SMTP credentials are configured."""

        if self.mail_username and self.mail_password:
            smtp.login(
                self.mail_username,
                self.mail_password,
            )

    # =========================================================================
    # Guide Invitation
    # =========================================================================
    def send_guide_invitation_email(
        self,
        user,
        invitation_url: str,
    ) -> bool:
        """Invite a guide to activate their TUR account."""

        name = (
            getattr(user, "first_name", None)
            or getattr(user, "username", None)
            or "Guide"
        )

        safe_name = escape(str(name))
        safe_url = escape(str(invitation_url), quote=True)

        subject = "Your Guide Invitation | The Uncharted Route"

        body = f"""
Hello {name},

You have been invited to join The Uncharted Route as a guide.

To accept your invitation and set your password, open the link below:

{invitation_url}

For your security, this invitation link is time-limited and should
not be shared with anyone.

If you were not expecting this invitation, please contact
The Uncharted Route administration team.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Guide Invitation</title>
</head>
<body style="margin:0; padding:24px; background:#F7F1E5;
             color:#1C2822; font-family:Arial,sans-serif;">
    <div style="max-width:600px; margin:0 auto; padding:32px;
                background:#FFFFFF; border-radius:12px;">
        <p style="color:#5C6B32; font-weight:bold;">
            THE UNCHARTED ROUTE
        </p>

        <h1 style="color:#12372A;">Welcome to the guide team</h1>

        <p>Hello {safe_name},</p>

        <p>
            You have been invited to join The Uncharted Route
            as a guide.
        </p>

        <p>
            Accept your invitation to set your password and
            complete your account setup.
        </p>

        <p style="margin:28px 0;">
            <a href="{safe_url}"
               style="display:inline-block; padding:14px 22px;
                      background:#12372A; color:#FFFFFF;
                      text-decoration:none; border-radius:6px;">
                Accept Guide Invitation
            </a>
        </p>

        <p>
            For your security, this link is time-limited and
            should not be shared.
        </p>

        <p>
            If you were not expecting this invitation, contact
            The Uncharted Route administration team.
        </p>

        <p style="margin-top:32px;">
            <strong>The Uncharted Route</strong><br>
            Explore. Experience. Remember.
        </p>
    </div>
</body>
</html>
"""
        return self.send_email(
            recipient=getattr(user, "email", None),
            subject=subject,
            body=body,
            html_body=html_body,)

    # =========================================================================
    # Account Verification
    # =========================================================================
    def send_verification_email(
        self,
        user,
        verification_url: str,
    ) -> bool:
        """Send an account verification email."""

        name = (
            getattr(user, "first_name", None)
            or getattr(user, "username", None)
            or "Traveler"
        )

        safe_name = escape(str(name))
        safe_url = escape(str(verification_url), quote=True)

        subject = "Verify Your Account | The Uncharted Route"

        body = f"""
Hello {name},

Welcome to The Uncharted Route.

Please verify your account using the link below:

{verification_url}

If you did not create this account, you can safely ignore this email.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verify Your Account</title>
</head>
<body style="font-family:Arial,sans-serif; color:#1C2822;">
    <h2>Welcome to The Uncharted Route</h2>
    <p>Hello {safe_name},</p>
    <p>
        Thank you for creating an account with
        <strong>The Uncharted Route</strong>.
    </p>
    <p>Please verify your account to continue:</p>
    <p>
        <a href="{safe_url}">Verify My Account</a>
    </p>
    <p>
        If you did not create this account, you can safely ignore
        this email.
    </p>
    <p>
        <strong>The Uncharted Route</strong><br>
        Explore. Experience. Remember.
    </p>
</body>
</html>
"""
        return self.send_email(
            recipient=getattr(user, "email", None),
            subject=subject,
            body=body,
            html_body=html_body,)

    # =========================================================================
    # Password Reset
    # =========================================================================
    def send_password_reset_email(
        self,
        user,
        reset_url: str,
    ) -> bool:
        """Send a password reset email."""

        name = (
            getattr(user, "first_name", None)
            or getattr(user, "username", None)
            or "Traveler"
        )

        safe_name = escape(str(name))
        safe_url = escape(str(reset_url), quote=True)

        subject = "Reset Your Password | The Uncharted Route"

        body = f"""
Hello {name},

We received a request to reset your password.

Use the link below to reset it:

{reset_url}

If you did not request a password reset, you can safely ignore this email.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Password Reset</title>
</head>
<body style="font-family:Arial,sans-serif; color:#1C2822;">
    <h2>Password Reset</h2>
    <p>Hello {safe_name},</p>
    <p>We received a request to reset your password.</p>
    <p><a href="{safe_url}">Reset My Password</a></p>
    <p>
        If you did not request this, you can safely ignore this email.
    </p>
    <p><strong>The Uncharted Route</strong></p>
</body>
</html>
"""
        return self.send_email(
            recipient=getattr(user, "email", None),
            subject=subject,
            body=body,
            html_body=html_body,)

    # =========================================================================
    # Booking Confirmation
    # =========================================================================
    def send_booking_confirmation(self, booking) -> bool:
        """Send a booking confirmation email."""
        customer_email = getattr(booking, "email", None)
        if not customer_email:
            customer = getattr(booking, "customer", None)
            customer_email = getattr(customer, "email", None)

        if not customer_email:
            logger.warning(
                "Booking confirmation failed: booking has no customer email."
            )
            return False

        booking_reference = (
            getattr(booking, "booking_reference", None)
            or getattr(booking, "reference", None)
            or str(getattr(booking, "id", ""))
        )

        customer_name = (
            getattr(booking, "customer_name", None)
            or getattr(booking, "first_name", None)
            or "Traveler"
        )

        safe_name = escape(str(customer_name))
        safe_reference = escape(str(booking_reference))

        subject = (
            f"Booking Confirmation #{booking_reference} | "
            "The Uncharted Route"
        )

        body = f"""
Hello {customer_name},

Thank you for booking with The Uncharted Route.

Your booking has been received.

Booking Reference:
{booking_reference}

We look forward to helping you explore, experience, and remember Kenya.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Booking Confirmation</title>
</head>
<body style="font-family:Arial,sans-serif; color:#1C2822;">
    <h2>Booking Confirmation</h2>
    <p>Hello {safe_name},</p>
    <p>
        Thank you for booking with
        <strong>The Uncharted Route</strong>.
    </p>
    <p>
        <strong>Booking Reference:</strong> {safe_reference}
    </p>
    <p>
        We look forward to helping you explore, experience,
        and remember Kenya.
    </p>
    <p><strong>The Uncharted Route</strong></p>
</body>
</html>
"""
        return self.send_email(
            recipient=customer_email,
            subject=subject,
            body=body,
            html_body=html_body,)

    # =========================================================================
    # Booking Cancellation
    # =========================================================================
    def send_booking_cancellation(self, booking) -> bool:
        """Notify a customer that a booking has been cancelled."""

        customer_email = getattr(booking, "email", None)
        if not customer_email:
            customer = getattr(booking, "customer", None)
            customer_email = getattr(customer, "email", None)

        if not customer_email:
            logger.warning(
                "Booking cancellation email skipped: no customer email."
            )
            return False

        booking_reference = (
            getattr(booking, "booking_reference", None)
            or getattr(booking, "reference", None)
            or str(getattr(booking, "id", "")))

        customer_name = (
            getattr(booking, "customer_name", None)
            or "Traveler")

        safe_name = escape(str(customer_name))
        safe_reference = escape(str(booking_reference))

        subject = f"Booking Cancellation #{booking_reference}"

        body = f"""
Hello {customer_name},

Your booking with The Uncharted Route has been cancelled.

Booking Reference:
{booking_reference}

If you believe this cancellation was made in error,
please contact our team.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Booking Cancellation</title>
</head>
<body style="font-family:Arial,sans-serif; color:#1C2822;">
    <h2>Booking Cancellation</h2>
    <p>Hello {safe_name},</p>
    <p>Your booking with The Uncharted Route has been cancelled.</p>
    <p>
        <strong>Booking Reference:</strong> {safe_reference}
    </p>
    <p>
        If you believe this cancellation was made in error,
        please contact our team.
    </p>
    <p><strong>The Uncharted Route</strong></p>
</body>
</html>
"""

        return self.send_email(
            recipient=customer_email,
            subject=subject,
            body=body,
            html_body=html_body,)

    # =========================================================================
    # Contact Enquiry Notification
    # =========================================================================
    def send_contact_notification(
        self,
        contact,
        recipient: str = None,
    ) -> bool:
        """Notify the company about a new website enquiry."""

        recipient = (
            recipient
            or os.getenv(
                "MAIL_CONTACT_RECIPIENT",
                self.default_sender,
            )
        )

        name = (
            getattr(contact, "full_name", None)
            or getattr(contact, "first_name", None)
            or "Website Visitor"
        )

        email = getattr(contact, "email", None) or "Not provided"
        subject_text = (
            getattr(contact, "subject", None)
            or "New Website Enquiry"
        )
        enquiry_type = (
            getattr(contact, "enquiry_type", None)
            or "General"
        )
        message_text = getattr(contact, "message", None) or ""

        subject = f"New Contact Enquiry: {subject_text}"

        body = f"""
New website enquiry received.

Name:
{name}

Email:
{email}

Enquiry Type:
{enquiry_type}

Subject:
{subject_text}

Message:
{message_text}
""".strip()

        reply_to = (
            email
            if email != "Not provided" and "@" in email
            else None)

        return self.send_email(
            recipient=recipient,
            subject=subject,
            body=body,
            reply_to=reply_to,)

    # =========================================================================
    # Customer Testimonial Confirmation
    # =========================================================================
    def send_testimonial_received_email(
            self,
            testimonial,
            customer_email=None,
    ) -> bool:
        """
        Confirm receipt of a customer testimonial.
        The review is still pending moderation.
        """
        customer_name = (
                getattr(testimonial, "customer_name", None)
                or "Traveler"
        )

        customer_email = (
                customer_email
                or getattr(testimonial, "customer_email", None)
        )

        if isinstance(customer_email, (tuple, list)):
            customer_email = (
                customer_email[0] if customer_email else None
            )

        customer_email = (
            customer_email.strip()
            if isinstance(customer_email, str)
            else None
        )

        if not customer_email:
            logger.warning(
                "Testimonial confirmation skipped: "
                "no customer email for testimonial ID %s.",
                getattr(testimonial, "id", None),
            )
            return False

        rating = getattr(testimonial, "rating", None) or 0
        review_text = (
                getattr(testimonial, "testimonial", None) or ""
        )

        safe_name = escape(str(customer_name))
        safe_rating = max(0, min(5, int(rating)))
        stars = "★" * safe_rating + "☆" * (5 - safe_rating)
        safe_stars = escape(stars)
        safe_review = escape(str(review_text))

        subject = (
            "Thank You for Sharing Your Experience | "
            "The Uncharted Route"
        )

        body = f"""
    Hello {customer_name},

    Thank you for taking the time to share your experience with
    The Uncharted Route.

    We have received your review and appreciate you helping other
    travelers discover meaningful experiences.

    Your review is awaiting our team's review before it can appear
    on our website.

    Your rating: {stars}

    Your review:
    {review_text}

    Explore. Experience. Remember.

    The Uncharted Route
    """.strip()

        html_body = f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You for Your Review</title>
    </head>
    <body style="margin:0;padding:24px;background:#F7F1E5;
                 color:#1C2822;font-family:Arial,sans-serif;">
        <div style="max-width:600px;margin:0 auto;padding:32px;
                    background:#FFFFFF;border:1px solid #E9DDC8;
                    border-radius:14px;">
            <p style="color:#5C6B32;font-weight:bold;letter-spacing:1px;">
                THE UNCHARTED ROUTE
            </p>

            <h1 style="color:#12372A;font-size:26px;">
                Thank you for sharing your experience!
            </h1>

            <p>Hello {safe_name},</p>

            <p>
                Thank you for taking the time to leave a review.
                Your feedback means a great deal to us and helps other
                travelers plan their own journeys.
            </p>

            <div style="margin:24px 0;padding:20px;
                        background:#F7F1E5;border-radius:10px;">
                <p style="margin-top:0;color:#66736B;font-size:13px;">
                    YOUR RATING
                </p>
                <p style="margin:0;color:#D89B24;font-size:24px;">
                    {safe_stars}
                </p>
                <p style="margin-bottom:0;line-height:1.7;">
                    {safe_review}
                </p>
            </div>

            <p>
                Your review has been received and is awaiting our team's
                review before publication.
            </p>

            <p>
                Thank you for being part of our journey.
            </p>

            <p style="margin-top:28px;">
                <strong style="color:#12372A;">The Uncharted Route</strong><br>
                <span style="color:#66736B;">
                    Explore. Experience. Remember.
                </span>
            </p>
        </div>
    </body>
    </html>
    """

        return self.send_email(
            recipient=customer_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )

    # =========================================================================
    # New Testimonial Administrative Notification
    # =========================================================================
    def send_testimonial_admin_notification(
            self,
            testimonial,
            review_url: str = None,
    ) -> bool:
        """
        Notify the team when a customer submits a new testimonial.
        """
        recipient = (
                os.getenv("MAIL_TESTIMONIAL_RECIPIENT")
                or os.getenv("MAIL_ADMIN_RECIPIENT")
                or self.default_sender
        )

        customer_name = (
                getattr(testimonial, "customer_name", None)
                or "Not provided"
        )
        customer_email = (
                getattr(testimonial, "customer_email", None)
                or "Not provided"
        )
        rating = getattr(testimonial, "rating", None) or 0
        review_text = (
                getattr(testimonial, "testimonial", None) or ""
        )

        experience = getattr(testimonial, "experience", None)
        stay = getattr(testimonial, "stay", None)
        safari_option = getattr(
            testimonial,
            "safari_package_option",
            None,
        )

        listing = (
                      getattr(experience, "title", None)
                      if experience else None
                  ) or (
                      getattr(stay, "name", None)
                      if stay else None
                  ) or (
                      getattr(safari_option, "name", None)
                      if safari_option else None
                  ) or "General feedback"

        testimonial_id = getattr(testimonial, "id", None)

        subject = (
            f"New Customer Testimonial — {customer_name}"
        )

        body = f"""
    A new customer testimonial has been submitted.

    Review ID: {testimonial_id or "Not available"}
    Customer: {customer_name}
    Customer Email: {customer_email}
    Rating: {rating}/5
    Related Listing: {listing}

    Review:
    {review_text}

    Moderation status: Awaiting review.

    {"Manage this review: " + review_url if review_url else "Open the testimonial management section in your admin dashboard."}

    The Uncharted Route
    """.strip()

        safe_name = escape(str(customer_name))
        safe_email = escape(str(customer_email))
        safe_listing = escape(str(listing))
        safe_rating = escape(str(rating))
        safe_review = escape(str(review_text))
        safe_id = escape(str(testimonial_id or "Not available"))

        review_link = ""

        if review_url:
            safe_url = escape(str(review_url), quote=True)
            review_link = f"""
                <p style="margin:24px 0;">
                    <a href="{safe_url}"
                       style="display:inline-block;padding:13px 20px;
                              background:#12372A;color:#FFFFFF;
                              text-decoration:none;border-radius:7px;
                              font-weight:bold;">
                        Review Submission
                    </a>
                </p>
                """

        html_body = f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Customer Testimonial</title>
    </head>
    <body style="margin:0;padding:24px;background:#F7F1E5;
                 color:#1C2822;font-family:Arial,sans-serif;">
        <div style="max-width:650px;margin:0 auto;padding:30px;
                    background:#FFFFFF;border:1px solid #E9DDC8;
                    border-radius:12px;">
            <p style="color:#5C6B32;font-weight:bold;">
                THE UNCHARTED ROUTE · ADMIN NOTIFICATION
            </p>

            <h1 style="color:#12372A;font-size:24px;">
                New testimonial received
            </h1>

            <p>A customer has submitted a review that requires moderation.</p>

            <table style="width:100%;border-collapse:collapse;
                          margin:20px 0;font-size:14px;">
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        Review ID
                    </td>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        {safe_id}
                    </td>
                </tr>
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        Customer
                    </td>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        {safe_name}
                    </td>
                </tr>
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        Email
                    </td>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        {safe_email}
                    </td>
                </tr>
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        Rating
                    </td>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        {safe_rating}/5
                    </td>
                </tr>
                <tr>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        Related listing
                    </td>
                    <td style="padding:10px;border-bottom:1px solid #E9DDC8;">
                        {safe_listing}
                    </td>
                </tr>
            </table>

            <h2 style="font-size:16px;color:#12372A;">Customer Review</h2>

            <div style="padding:18px;background:#F7F1E5;
                        border-radius:8px;line-height:1.7;
                        white-space:pre-wrap;">{safe_review}</div>

            <p style="margin-top:22px;">
                <strong>Moderation:</strong>
                Awaiting review
            </p>

            {review_link}

            <p style="margin-top:28px;color:#66736B;font-size:13px;">
                The Uncharted Route · Explore. Experience. Remember.
            </p>
        </div>
    </body>
    </html>
    """

        return self.send_email(
            recipient=recipient,
            subject=subject,
            body=body,
            html_body=html_body,
            reply_to=(
                customer_email
                if customer_email != "Not provided"
                   and "@" in customer_email
                else None
            ),
        )

    # =========================================================================
    # Newsletter Tracking Helpers
    # =========================================================================
    @staticmethod
    def _newsletter_serializer(salt):
        """Create a signed serializer for newsletter links."""
        secret_key = current_app.secret_key

        if not secret_key:
            raise RuntimeError(
                "A Flask SECRET_KEY is required for newsletter tracking."
            )

        return URLSafeSerializer(secret_key, salt=salt)

    @staticmethod
    def _trackable_newsletter_url(url):
        """Only track normal HTTP and HTTPS links."""
        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() in {"http", "https"} and bool(
                parsed.netloc
            )
        except (TypeError, ValueError):
            return False

    def _track_newsletter_links(self, html_body, subscriber, nonce):
        """Rewrite HTML links to record newsletter clicks."""
        if not html_body:
            return html_body

        serializer = self._newsletter_serializer(
            "tur-newsletter-tracking-v1"
        )

        def replace_link(match):
            original_url = match.group(2)
            quote_char = match.group(1)

            if not self._trackable_newsletter_url(original_url):
                return match.group(0)

            # Do not wrap an existing unsubscribe link.
            parsed = urlparse(original_url)
            if (
                parsed.path.rstrip("/").endswith("/newsletter/unsubscribe")
                or "/newsletter/track/" in parsed.path
            ):
                return match.group(0)

            token = serializer.dumps({
                "subscriber_id": subscriber.id,
                "nonce": nonce,
                "url": original_url,
            })

            tracked_url = url_for(
                "public_newsletter.track_click",
                token=token,
                _external=True,
            )

            return (
                f"href={quote_char}"
                f"{escape(tracked_url, quote=True)}"
                f"{quote_char}"
            )

        return re.sub(
            r"""href\s*=\s*(["'])(.*?)\1""",
            replace_link,
            html_body,
            flags=re.IGNORECASE,
        )

    # =========================================================================
    # Newsletter
    # =========================================================================
    def send_newsletter(
        self,
        subscriber,
        subject: str,
        body: str,
        html_body: str = None,
    ) -> bool:
        """Send a consented newsletter with unsubscribe and tracking links."""

        if not subscriber:
            return False

        if not getattr(subscriber, "subscribed", False):
            return False

        if not getattr(subscriber, "verified", False):
            return False

        if not getattr(subscriber, "marketing_consent", False):
            return False

        if not getattr(subscriber, "email", None):
            return False

        try:
            from extensions import db
            from app.models import NewsletterSubscriber

            # Refresh the recipient before sending, where possible, so a
            # recently unsubscribed subscriber is not emailed from stale data.
            current_subscriber = db.session.get(
                NewsletterSubscriber,
                subscriber.id,
            )

            if (
                current_subscriber is None
                or not current_subscriber.subscribed
                or not current_subscriber.verified
                or not current_subscriber.marketing_consent
            ):
                return False

            subscriber = current_subscriber

            nonce = secrets.token_urlsafe(16)

            unsubscribe_token = self._newsletter_serializer(
                "tur-newsletter-unsubscribe-v1"
            ).dumps({
                "subscriber_id": subscriber.id,
            })

            unsubscribe_url = url_for(
                "public_newsletter.unsubscribe",
                token=unsubscribe_token,
                _external=True,
            )

            tracking_token = self._newsletter_serializer(
                "tur-newsletter-tracking-v1"
            ).dumps({
                "subscriber_id": subscriber.id,
                "nonce": nonce,
            })

            pixel_url = url_for(
                "public_newsletter.track_open",
                token=tracking_token,
                _external=True,
            )

            plain_body = (body or "").rstrip()
            plain_body += (
                "\n\n---\n"
                "You are receiving this email because you subscribed "
                "to The Uncharted Route newsletter.\n"
                f"Unsubscribe: {unsubscribe_url}\n"
            )

            if html_body:
                tracked_html = self._track_newsletter_links(
                    html_body,
                    subscriber,
                    nonce,
                )

                tracking_pixel = (
                    f'<img src="{escape(pixel_url, quote=True)}" '
                    'width="1" height="1" alt="" '
                    'style="display:none!important;width:1px;height:1px;'
                    'border:0;" />'
                )

                unsubscribe_footer = f"""
                <hr style="border:0;border-top:1px solid #E9DDC8;
                           margin:28px 0;">
                <p style="font-size:12px;line-height:1.6;color:#66736B;">
                    You are receiving this email because you subscribed
                    to The Uncharted Route newsletter.
                    <br>
                    <a href="{escape(unsubscribe_url, quote=True)}"
                       style="color:#12372A;">
                        Unsubscribe from marketing emails
                    </a>
                </p>
                {tracking_pixel}
                """

                if re.search(r"</body\s*>", tracked_html, re.IGNORECASE):
                    tracked_html = re.sub(
                        r"</body\s*>",
                        unsubscribe_footer + "\n</body>",
                        tracked_html,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                else:
                    tracked_html += unsubscribe_footer

                html_body = tracked_html

            else:
                html_body = None

            sent = self.send_email(
                recipient=subscriber.email,
                subject=subject,
                body=plain_body,
                html_body=html_body,
            )

            if not sent:
                return False

            # Count the email only after the SMTP server accepts it.
            subscriber.total_emails_sent = (
                subscriber.total_emails_sent or 0
            ) + 1
            subscriber.last_email_sent = datetime.utcnow()

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                logger.exception(
                    "Newsletter was sent to subscriber ID %s, "
                    "but its send statistics could not be saved.",
                    subscriber.id,
                )

            return True

        except Exception:
            logger.exception(
                "Newsletter processing failed for subscriber ID %s.",
                getattr(subscriber, "id", None),
            )
            return False
    # =========================================================================
    # Administrative Notification
    # =========================================================================
    def send_admin_notification(
        self,
        subject: str,
        message: str,
        recipient: str = None,) -> bool:
        """Send an internal administrative notification."""
        recipient = (
            recipient
            or os.getenv(
                "MAIL_ADMIN_RECIPIENT",
                self.default_sender,))

        return self.send_email(
            recipient=recipient,
            subject=subject,
            body=message,)

# =============================================================================
# Shared Service Instance
# =============================================================================
email_service = EmailService()

# =============================================================================
# Convenience Functions
# =============================================================================
def send_email(
    recipient,
    subject: str,
    body: str,
    html_body: str = None,
    sender: str = None,
    reply_to: str = None,
    cc=None,
    bcc=None,
    message_id: str = None,
) -> bool:
    """Convenience wrapper around EmailService.send_email()."""
    return email_service.send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        html_body=html_body,
        sender=sender,
        reply_to=reply_to,
        cc=cc,
        bcc=bcc,
        message_id=message_id,
    )

def send_guide_invitation_email(
    user,
    invitation_url: str,) -> bool:
    """Convenience wrapper for guide invitation emails."""
    return email_service.send_guide_invitation_email(
        user,
        invitation_url,)

def send_verification_email(
    user,
    verification_url: str,
) -> bool:
    """Convenience wrapper for account verification."""

    return email_service.send_verification_email(
        user,
        verification_url,
    )

def send_password_reset_email(
    user,
    reset_url: str,) -> bool:
    """Convenience wrapper for password reset."""
    return email_service.send_password_reset_email(user,reset_url,)

def send_booking_confirmation(booking) -> bool:
    """Convenience wrapper for booking confirmation."""
    return email_service.send_booking_confirmation(booking)

def send_booking_cancellation(booking) -> bool:
    """Convenience wrapper for booking cancellation."""
    return email_service.send_booking_cancellation(booking)

def send_contact_notification(
    contact,
    recipient: str = None,) -> bool:
    """Convenience wrapper for contact notifications."""
    return email_service.send_contact_notification(
        contact,
        recipient,)

def send_newsletter(
    subscriber,
    subject: str,
    body: str,
    html_body: str = None,
) -> bool:
    """Convenience wrapper for newsletter delivery."""
    return email_service.send_newsletter(
        subscriber,
        subject,
        body,
        html_body,)

def send_admin_notification(
    subject: str,
    message: str,
    recipient: str = None,
) -> bool:
    """Convenience wrapper for administrative notifications."""
    return email_service.send_admin_notification(
        subject,
        message,
        recipient,)