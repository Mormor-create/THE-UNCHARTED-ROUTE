"""
===============================================================================
The Uncharted Route
Public Safari Booking Service
===============================================================================
Creates public safari booking requests using the central Booking model and
the SafariBooking detail model.

Supplier rates are authoritative. Display-currency conversions are never used
to calculate the stored booking total.

Safari booking email notifications are handled in this service:
- Customer notification goes to the email entered on the booking form.
- New booking notification goes to the TUR Gmail address.
===============================================================================
"""

import logging
import os
import smtplib
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from flask import current_app, has_app_context
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.models.booking import Booking
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPackageOption,
    SafariPackageRate,)
from app.models.safari_booking import SafariBooking

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================
DEFAULT_SENDER = "theunchartedrouteke@gmail.com"
DEFAULT_SENDER_NAME = "The Uncharted Route"
ADMIN_NOTIFICATION_EMAIL = "theunchartedrouteke@gmail.com"

def _mail_setting(name, default=None):
    """Read a mail setting from Flask config or environment variables."""
    if has_app_context():
        value = current_app.config.get(name)

        if value is not None:
            return value

    return os.getenv(name, default)


def _send_safari_email(recipient, subject, text_body, html_body=None):
    """
    Send a safari-specific email using the application's SMTP configuration.

    Email errors are logged and returned as False. They are deliberately not
    raised because email delivery must not undo a successfully saved booking.
    """
    recipient = str(recipient or "").strip()

    if not recipient:
        logger.warning("Safari email not sent: recipient address is missing.")
        return False

    mail_server = _mail_setting("MAIL_SERVER")
    mail_port = int(_mail_setting("MAIL_PORT", 587) or 587)
    mail_username = _mail_setting("MAIL_USERNAME")
    mail_password = _mail_setting("MAIL_PASSWORD")
    use_tls = str(_mail_setting("MAIL_USE_TLS", True)).lower() in {
        "true", "1", "yes", "on"
    }
    use_ssl = str(_mail_setting("MAIL_USE_SSL", False)).lower() in {
        "true", "1", "yes", "on"
    }

    sender = (
        _mail_setting("MAIL_DEFAULT_SENDER")
        or DEFAULT_SENDER
    )
    sender_name = (
        _mail_setting("MAIL_DEFAULT_SENDER_NAME")
        or DEFAULT_SENDER_NAME
    )

    if not mail_server:
        logger.error(
            "Safari email not sent: MAIL_SERVER is not configured."
        )
        return False

    if not mail_username or not mail_password:
        logger.error(
            "Safari email not sent: SMTP username or password is missing."
        )
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((sender_name, sender))
    message["To"] = recipient
    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(
                mail_server,
                mail_port,
                timeout=30,
            ) as smtp:
                smtp.login(mail_username, mail_password)
                smtp.send_message(message)

        else:
            with smtplib.SMTP(
                mail_server,
                mail_port,
                timeout=30,
            ) as smtp:
                smtp.ehlo()

                if use_tls:
                    smtp.starttls()
                    smtp.ehlo()

                smtp.login(mail_username, mail_password)
                smtp.send_message(message)

        logger.info(
            "Safari email sent successfully to %s.",
            recipient,
        )
        return True

    except Exception:
        logger.exception(
            "Failed to send safari email to %s.",
            recipient,
        )
        return False


# =============================================================================
# Safari email notification helpers
# =============================================================================

def _booking_reference(booking):
    """Return the booking's public reference, falling back to its database ID."""
    for attribute in (
        "booking_reference",
        "reference",
        "booking_number",
        "reference_number",
    ):
        value = getattr(booking, attribute, None)

        if value:
            return str(value)

    return str(getattr(booking, "id", "Pending"))


def _format_date(value):
    """Format a date for email display."""
    if not value:
        return "Not provided"

    if hasattr(value, "strftime"):
        return value.strftime("%d %B %Y")

    return str(value)


def _format_money(amount, currency):
    """Format a stored booking amount for email display."""
    try:
        value = Decimal(str(amount or 0)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return f"{currency} {value:,.2f}"
    except (TypeError, ValueError, ArithmeticError):
        return f"{currency} {amount}"


def _email_html(title, intro, rows, footer=None):
    """Build a simple branded HTML email."""
    row_html = ""

    for label, value in rows:
        safe_label = escape(str(label))
        safe_value = escape(str(value or "Not provided"))

        row_html += f"""
            <tr>
                <td style="
                    padding: 11px 14px;
                    color: #66736B;
                    font-size: 13px;
                    border-bottom: 1px solid #E9DDC8;
                    width: 38%;
                    vertical-align: top;
                ">{safe_label}</td>
                <td style="
                    padding: 11px 14px;
                    color: #1C2822;
                    font-size: 14px;
                    font-weight: 600;
                    border-bottom: 1px solid #E9DDC8;
                    vertical-align: top;
                ">{safe_value}</td>
            </tr>
        """

    safe_title = escape(title)
    safe_intro = escape(intro)
    safe_footer = escape(
        footer or "The Uncharted Route | Explore. Experience. Remember."
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="
        margin: 0;
        padding: 30px 12px;
        background-color: #F7F1E5;
        font-family: Arial, Helvetica, sans-serif;
        color: #1C2822;
    ">
        <div style="
            max-width: 640px;
            margin: 0 auto;
            background: #FFFFFF;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #E9DDC8;
        ">
            <div style="
                background: #12372A;
                padding: 28px 30px;
                color: #FFFFFF;
            ">
                <div style="
                    color: #D89B24;
                    font-size: 12px;
                    letter-spacing: 2px;
                    font-weight: bold;
                    text-transform: uppercase;
                ">THE UNCHARTED ROUTE</div>
                <h1 style="
                    margin: 12px 0 0;
                    font-size: 24px;
                    line-height: 1.3;
                ">{safe_title}</h1>
            </div>

            <div style="padding: 28px 30px;">
                <p style="
                    margin: 0 0 22px;
                    font-size: 15px;
                    line-height: 1.7;
                    color: #1C2822;
                ">{safe_intro}</p>

                <table style="
                    width: 100%;
                    border-collapse: collapse;
                    background: #FFFFFF;
                ">
                    {row_html}
                </table>

                <p style="
                    margin: 25px 0 0;
                    color: #66736B;
                    font-size: 13px;
                    line-height: 1.7;
                ">{safe_footer}</p>
            </div>

            <div style="
                padding: 17px 30px;
                background: #F7F1E5;
                color: #66736B;
                font-size: 11px;
                text-align: center;
            ">
                Explore. Experience. Remember.
            </div>
        </div>
    </body>
    </html>
    """


def _send_safari_booking_notifications(
    booking,
    safari_detail,
    customer_email,
    customer_name,
    property_obj,
    package_option,
    destination,
    rate,
    pricing,
    adults,
    children,
    infants,
    rooms_required,
    start_date,
    end_date,
    phone=None,
    nationality=None,
    country_of_residence=None,
    special_requests=None,
    dietary_requirements=None,
    accessibility_requirements=None,
    pickup_location=None,
    transfer_requirements=None,
    wildlife_preferences=None,
    rooming_preferences=None,
):
    """
    Send the customer booking notification and the internal TUR notification.

    Both messages are sent only after the booking has been committed.
    """
    reference = _booking_reference(booking)
    currency = pricing["currency"]
    amount_display = _format_money(
        booking.total_amount,
        currency,
    )

    customer_rows = [
        ("Booking reference", reference),
        ("Destination", destination.name),
        ("Property", property_obj.name),
        ("Package", package_option.name),
        ("Travel dates", (
            f"{_format_date(start_date)} to {_format_date(end_date)}"
        )),
        ("Adults", adults),
        ("Children", children),
        ("Infants", infants),
        ("Rooms required", rooms_required),
        ("Selected rate", rate.name),
        ("Estimated amount", amount_display),
        ("Booking status", "Pending review"),
    ]

    customer_text = f"""
Hello {customer_name},

Thank you for submitting your safari booking request with The Uncharted Route.

We have received your request. Our team will review the details and get in
touch with you regarding availability, the quotation where applicable, and
the next steps.

Your booking request details:

Booking reference: {reference}
Destination: {destination.name}
Property: {property_obj.name}
Package: {package_option.name}
Travel dates: {_format_date(start_date)} to {_format_date(end_date)}
Adults: {adults}
Children: {children}
Infants: {infants}
Rooms required: {rooms_required}
Selected rate: {rate.name}
Estimated amount: {amount_display}
Status: Pending review

Please keep your booking reference for future correspondence.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

    customer_html = _email_html(
        title="Your safari booking request",
        intro=(
            f"Hello {customer_name}, thank you for submitting your safari "
            "booking request. We have received your details and our team "
            "will review your request and contact you about the next steps."
        ),
        rows=customer_rows,
        footer=(
            "This is a notification that your request has been received. "
            "Your safari is not yet confirmed."
        ),
    )

    admin_rows = [
        ("Booking reference", reference),
        ("Customer", customer_name),
        ("Customer email", customer_email),
        ("Phone", phone),
        ("Nationality", nationality),
        ("Country of residence", country_of_residence),
        ("Destination", destination.name),
        ("Property", property_obj.name),
        ("Package", package_option.name),
        ("Travel start", _format_date(start_date)),
        ("Travel end", _format_date(end_date)),
        ("Adults", adults),
        ("Children", children),
        ("Infants", infants),
        ("Rooms required", rooms_required),
        ("Rate", rate.name),
        ("Pricing basis", pricing["basis"]),
        ("Unit rate", _format_money(pricing["amount"], currency)),
        ("Calculated quantity", pricing["quantity"]),
        ("Quote calculated", "Yes" if pricing["quote_calculated"] else "No"),
        ("Booking total", amount_display),
        ("Booking status", "Pending review"),
        ("Pickup location", pickup_location),
        ("Transfer requirements", transfer_requirements),
        ("Wildlife preferences", wildlife_preferences),
        ("Rooming preferences", rooming_preferences),
        ("Dietary requirements", dietary_requirements),
        ("Accessibility requirements", accessibility_requirements),
        ("Special requests", special_requests),
    ]

    admin_text = f"""
A new public safari booking request has been submitted.

BOOKING DETAILS

Booking reference: {reference}
Customer: {customer_name}
Customer email: {customer_email}
Phone: {phone or "Not provided"}
Nationality: {nationality or "Not provided"}
Country of residence: {country_of_residence or "Not provided"}

Destination: {destination.name}
Property: {property_obj.name}
Package: {package_option.name}
Travel dates: {_format_date(start_date)} to {_format_date(end_date)}

Adults: {adults}
Children: {children}
Infants: {infants}
Rooms required: {rooms_required}

Selected rate: {rate.name}
Pricing basis: {pricing["basis"]}
Unit rate: {_format_money(pricing["amount"], currency)}
Quantity: {pricing["quantity"]}
Quote calculated: {"Yes" if pricing["quote_calculated"] else "No"}
Booking total: {amount_display}

Pickup location: {pickup_location or "Not provided"}
Transfer requirements: {transfer_requirements or "Not provided"}
Wildlife preferences: {wildlife_preferences or "Not provided"}
Rooming preferences: {rooming_preferences or "Not provided"}
Dietary requirements: {dietary_requirements or "Not provided"}
Accessibility requirements: {accessibility_requirements or "Not provided"}
Special requests: {special_requests or "Not provided"}

Please review the request and verify supplier availability and pricing
before confirming the booking.
""".strip()

    admin_html = _email_html(
        title="New safari booking request",
        intro=(
            f"A new safari booking request has been submitted by "
            f"{customer_name}. Please review the booking details below."
        ),
        rows=admin_rows,
        footer=(
            "This booking is pending review. Verify supplier availability "
            "and pricing before confirming it."
        ),
    )

    # Customer receives the notification at the address they entered.
    _send_safari_email(
        recipient=customer_email,
        subject=f"Safari booking request received | {reference}",
        text_body=customer_text,
        html_body=customer_html,
    )

    # TUR receives its own notification at the shared business Gmail address.
    _send_safari_email(
        recipient=ADMIN_NOTIFICATION_EMAIL,
        subject=f"New safari booking request | {reference}",
        text_body=admin_text,
        html_body=admin_html,
    )


# =============================================================================
# Money and validation helpers
# =============================================================================

ZERO = Decimal("0.00")


class SafariBookingValidationError(ValueError):
    """Raised when a public safari booking request is invalid."""


def _money(value):
    """Convert a value to a two-decimal Decimal safely."""
    return Decimal(str(value or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def _integer(value, field_name, minimum=0):
    """Parse and validate a whole-number form value."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise SafariBookingValidationError(
            f"Please enter a valid value for {field_name}."
        )

    if isinstance(value, bool):
        raise SafariBookingValidationError(
            f"Please enter a valid value for {field_name}."
        )

    if str(value).strip() not in {str(parsed), f"+{parsed}"}:
        raise SafariBookingValidationError(
            f"{field_name} must be a whole number."
        )

    if parsed < minimum:
        raise SafariBookingValidationError(
            f"{field_name} must be at least {minimum}."
        )

    return parsed


def _parse_date(value, field_name):
    """Accept a date object or an ISO YYYY-MM-DD string."""
    if isinstance(value, date):
        return value

    if not value:
        raise SafariBookingValidationError(
            f"Please select your {field_name}."
        )

    try:
        return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError):
        raise SafariBookingValidationError(
            f"Please enter a valid {field_name}."
        )


def _get_value(data, key, default=None):
    """Read values from either a dictionary or a WTForms-like object."""
    if isinstance(data, dict):
        return data.get(key, default)

    value = getattr(data, key, default)

    if hasattr(value, "data"):
        return value.data

    return value


def _validate_email(value):
    """Perform basic required-email validation."""
    email = str(value or "").strip()

    if not email or "@" not in email or email.startswith("@"):
        raise SafariBookingValidationError(
            "Please provide a valid email address."
        )

    if email.endswith("@") or "." not in email.rsplit("@", 1)[-1]:
        raise SafariBookingValidationError(
            "Please provide a valid email address."
        )

    return email


# =============================================================================
# Public product validation
# =============================================================================

def validate_public_safari_selection(
    property_obj,
    package_option,
    rate,
    start_date,
    end_date,
):
    """
    Verify that the selected property, package and rate are currently public
    and that the rate is valid for the requested travel dates.
    """
    if not property_obj or not property_obj.active:
        raise SafariBookingValidationError(
            "This safari property is currently unavailable."
        )

    destination = property_obj.destination

    if not destination or not destination.active:
        raise SafariBookingValidationError(
            "This safari destination is currently unavailable."
        )

    if (
        not package_option
        or not package_option.active
        or package_option.property_id != property_obj.id
    ):
        raise SafariBookingValidationError(
            "Please select a valid package for this property."
        )

    if (
        not rate
        or not rate.active
        or rate.package_option_id != package_option.id
    ):
        raise SafariBookingValidationError(
            "Please select a valid rate for this package."
        )

    if start_date < date.today():
        raise SafariBookingValidationError(
            "The safari start date cannot be in the past."
        )

    if end_date <= start_date:
        raise SafariBookingValidationError(
            "The safari end date must be after the start date."
        )

    if rate.valid_from and start_date < rate.valid_from:
        raise SafariBookingValidationError(
            "The selected rate is not valid for your start date."
        )

    if rate.valid_to and start_date > rate.valid_to:
        raise SafariBookingValidationError(
            "The selected rate has expired for your travel dates."
        )

    return destination


# =============================================================================
# Rate and quote handling
# =============================================================================

def _calculate_rate_snapshot(rate, adults, children, infants):
    """
    Return a conservative quote based only on pricing rules that can be
    determined unambiguously from the selected rate.

    Unknown or ambiguous pricing remains a request for staff review. It is
    never silently presented as a confirmed or payable quotation.
    """
    amount = _money(rate.amount)
    currency = str(rate.currency or "").strip().upper()
    basis = str(rate.pricing_basis or "").strip().lower()
    category = str(rate.guest_category or "all").strip().lower()

    if amount < ZERO:
        raise SafariBookingValidationError(
            "The selected rate has an invalid amount."
        )

    if len(currency) != 3:
        raise SafariBookingValidationError(
            "The selected rate has an invalid currency."
        )

    total_guests = adults + children + infants

    if total_guests < 1:
        raise SafariBookingValidationError(
            "Your booking must include at least one traveller."
        )

    quantity = 0
    total = ZERO
    quote_calculated = False

    if category == "all" and basis in {
        "per_person",
        "per_person_sharing",
    }:
        if children == 0 and infants == 0:
            quantity = adults
            total = _money(amount * quantity)
            quote_calculated = True

    elif category == "adult" and basis in {
        "per_person",
        "per_person_sharing",
    }:
        if children == 0 and infants == 0:
            quantity = adults
            total = _money(amount * quantity)
            quote_calculated = True

    elif category == "child" and basis == "per_person":
        if adults == 0 and infants == 0 and children > 0:
            quantity = children
            total = _money(amount * quantity)
            quote_calculated = True

    return {
        "amount": amount,
        "currency": currency,
        "basis": basis,
        "category": category,
        "quantity": quantity,
        "total": total,
        "quote_calculated": quote_calculated,
    }


# =============================================================================
# Create public safari booking
# =============================================================================

def create_public_safari_booking(
    *,
    property_obj,
    package_option,
    rate,
    form_data,
):
    """
    Create a pending public safari booking request.

    Both the central Booking and SafariBooking detail are saved atomically.
    Customer and TUR email notifications are sent only after the commit.
    """
    first_name = str(
        _get_value(form_data, "first_name", "") or ""
    ).strip()

    last_name = str(
        _get_value(form_data, "last_name", "") or ""
    ).strip()

    email = _validate_email(
        _get_value(form_data, "email", "")
    )

    phone = str(
        _get_value(form_data, "phone", "") or ""
    ).strip() or None

    nationality = str(
        _get_value(form_data, "nationality", "") or ""
    ).strip() or None

    country_of_residence = str(
        _get_value(form_data, "country_of_residence", "") or ""
    ).strip() or None

    if not first_name or not last_name:
        raise SafariBookingValidationError(
            "Please enter the lead traveller's first and last name."
        )

    start_date = _parse_date(
        _get_value(form_data, "start_date"),
        "start date",
    )

    end_date = _parse_date(
        _get_value(form_data, "end_date"),
        "end date",
    )

    destination = validate_public_safari_selection(
        property_obj=property_obj,
        package_option=package_option,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )

    adults = _integer(
        _get_value(form_data, "adults", 1),
        "Adults",
        minimum=1,
    )

    children = _integer(
        _get_value(form_data, "children", 0),
        "Children",
    )

    infants = _integer(
        _get_value(form_data, "infants", 0),
        "Infants",
    )

    total_guests = adults + children + infants

    if rate.min_guests and total_guests < rate.min_guests:
        raise SafariBookingValidationError(
            f"This rate requires at least {rate.min_guests} guests."
        )

    if rate.max_guests and total_guests > rate.max_guests:
        raise SafariBookingValidationError(
            f"This rate allows a maximum of {rate.max_guests} guests."
        )

    rooms_required = _integer(
        _get_value(form_data, "rooms_required", 1),
        "Rooms required",
        minimum=1,
    )

    if rate.min_guest_age is not None or rate.max_guest_age is not None:
        children_ages = str(
            _get_value(form_data, "children_ages", "") or ""
        ).strip()

        if children and not children_ages:
            raise SafariBookingValidationError(
                "Please provide the children's ages so we can validate "
                "the selected rate."
            )

    pricing = _calculate_rate_snapshot(
        rate=rate,
        adults=adults,
        children=children,
        infants=infants,
    )

    duration_days = int(
        getattr(package_option, "duration_days", 0) or 0
    )

    duration_nights = int(
        getattr(package_option, "duration_nights", 0) or 0
    )

    nights_requested = (end_date - start_date).days

    if duration_nights and nights_requested != duration_nights:
        raise SafariBookingValidationError(
            f"This package is listed as {duration_nights} nights. "
            "Please choose dates matching the package duration."
        )

    special_requests = str(
        _get_value(form_data, "special_requests", "") or ""
    ).strip() or None

    dietary_requirements = str(
        _get_value(form_data, "dietary_requirements", "") or ""
    ).strip() or None

    accessibility_requirements = str(
        _get_value(form_data, "accessibility_requirements", "") or ""
    ).strip() or None

    pickup_location = str(
        _get_value(form_data, "pickup_location", "") or ""
    ).strip() or None

    transfer_requirements = str(
        _get_value(form_data, "transfer_requirements", "") or ""
    ).strip() or None

    wildlife_preferences = str(
        _get_value(form_data, "wildlife_preferences", "") or ""
    ).strip() or None

    rooming_preferences = str(
        _get_value(form_data, "rooming_preferences", "") or ""
    ).strip() or None

    if pricing["quote_calculated"]:
        subtotal = pricing["total"]
        total_amount = pricing["total"]
    else:
        subtotal = ZERO
        total_amount = ZERO

    booking = Booking(
        booking_type="safari",
        source="website",
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        nationality=nationality,
        country_of_residence=country_of_residence,
        adults=adults,
        children=children,
        infants=infants,
        status="pending",
        payment_status="unpaid",
        booking_date=db.func.now(),
        start_date=start_date,
        end_date=end_date,
        currency=pricing["currency"],
        subtotal=subtotal,
        discount_amount=ZERO,
        tax_amount=ZERO,
        addon_total=ZERO,
        total_amount=total_amount,
        amount_paid=ZERO,
        balance_due=total_amount,
        special_requests=special_requests,
        dietary_requirements=dietary_requirements,
        accessibility_requirements=accessibility_requirements,
        customer_notes=(
            "Public safari booking request. "
            + (
                "Price calculated from the selected supplier rate; "
                "availability and confirmation are pending."
                if pricing["quote_calculated"]
                else
                "Price requires staff review. No final quotation has "
                "been issued."
            )
        ),
        internal_notes=(
            "Public website submission. "
            + (
                "Supplier availability must be verified before confirmation."
                if pricing["quote_calculated"]
                else
                "Review the selected rate, occupancy, guest categories, "
                "and supplier pricing before issuing a quotation."
            )
        ),
    )

    # -------------------------------------------------------------------------
    # Safari-specific booking details
    # Field names below match app/models/safari_booking.py.
    # -------------------------------------------------------------------------

    safari_detail = SafariBooking(
        safari_destination_id=destination.id,
        property_id=property_obj.id,
        package_option_id=package_option.id,
        package_rate_id=rate.id,

        # Historical package snapshots
        destination_name_snapshot=destination.name,
        property_name_snapshot=property_obj.name,
        package_name_snapshot=package_option.name,
        package_description_snapshot=(
            getattr(package_option, "description", None) or ""
        ),

        # Travel dates
        start_date=start_date,
        end_date=end_date,
        duration_days=duration_days or nights_requested + 1,
        duration_nights=duration_nights or nights_requested,

        # Occupancy and rooming
        rooms_required=rooms_required,
        adults=adults,
        children=children,
        infants=infants,
        rooming_preferences=rooming_preferences,

        # Rate snapshot
        rate_name_snapshot=rate.name,
        rate_basis=pricing["basis"] or "per_person_sharing",
        unit_rate=pricing["amount"],
        quantity=max(pricing["quantity"], 1),
        currency=pricing["currency"],

        # Safari-specific requests
        pickup_location=pickup_location,
        transfer_requirements=transfer_requirements,
        wildlife_interests=wildlife_preferences,
        special_safari_requirements=special_requests,
    )

    # -------------------------------------------------------------------------
    # Persist both records atomically.
    # -------------------------------------------------------------------------

    try:
        booking.safari_booking = safari_detail

        db.session.add(booking)
        db.session.flush()

        # Preserve package itinerary as a historical snapshot.
        itinerary = []

        for day in getattr(
            package_option,
            "itinerary_days",
            [],
        ) or []:
            itinerary.append({
                "day_number": getattr(day, "day_number", None),
                "title": getattr(day, "title", None),
                "description": getattr(day, "description", None),
            })

        safari_detail.itinerary_snapshot = itinerary

        # Preserve package inclusions and exclusions.
        safari_detail.inclusions_snapshot = (
            getattr(package_option, "inclusions", None) or ""
        )

        safari_detail.exclusions_snapshot = (
            getattr(package_option, "exclusions", None) or ""
        )

        db.session.commit()

    except Exception:
        db.session.rollback()

        logger.exception("Failed to save public safari booking.")

        raise

    # -------------------------------------------------------------------------
    # Send notifications only after a successful database commit.
    # -------------------------------------------------------------------------
    customer_name = f"{first_name} {last_name}".strip()
    try:
        _send_safari_booking_notifications(
            booking=booking,
            safari_detail=safari_detail,
            customer_email=email,
            customer_name=customer_name,
            property_obj=property_obj,
            package_option=package_option,
            destination=destination,
            rate=rate,
            pricing=pricing,
            adults=adults,
            children=children,
            infants=infants,
            rooms_required=rooms_required,
            start_date=start_date,
            end_date=end_date,
            phone=phone,
            nationality=nationality,
            country_of_residence=country_of_residence,
            special_requests=special_requests,
            dietary_requirements=dietary_requirements,
            accessibility_requirements=accessibility_requirements,
            pickup_location=pickup_location,
            transfer_requirements=transfer_requirements,
            wildlife_preferences=wildlife_preferences,
            rooming_preferences=rooming_preferences,)

    except Exception:
        logger.exception(
            "Unexpected error while sending notifications for safari "
            "booking %s.",
            _booking_reference(booking),)

    return booking
