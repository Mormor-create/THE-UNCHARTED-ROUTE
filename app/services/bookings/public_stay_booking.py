# =============================================================================
# Public Stay Booking
# =============================================================================
import logging
import os
import smtplib
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from flask import current_app, has_app_context
from app.models import Booking, StayBooking
from app.models.stay import Stay
from app.models.stay_room import StayRoom
from extensions import db

logger = logging.getLogger(__name__)

STAY_ADMIN_EMAIL = "theunchartedrouteke@gmail.com"
STAY_DEFAULT_SENDER = "theunchartedrouteke@gmail.com"
STAY_SENDER_NAME = "The Uncharted Route"

def _public_stay_value(data, key, default=None):
    """Read a value from a dictionary or WTForms form."""
    if isinstance(data, dict):
        return data.get(key, default)

    value = getattr(data, key, default)
    return value.data if hasattr(value, "data") else value

def _public_stay_decimal(value):
    """Convert a monetary value to a safe two-decimal Decimal."""
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError
        return amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("The selected room has an invalid rate.")


def _public_stay_mail_setting(name, default=None):
    """Read SMTP configuration from Flask or environment settings."""
    if has_app_context():
        value = current_app.config.get(name)
        if value is not None:
            return value

    return os.getenv(name, default)


def _send_public_stay_email(recipient, subject, text_body, html_body=None):
    """Send a stay notification without affecting the saved booking."""
    recipient = str(recipient or "").strip()

    if not recipient:
        return False

    server = _public_stay_mail_setting("MAIL_SERVER")
    port = int(_public_stay_mail_setting("MAIL_PORT", 587) or 587)
    username = _public_stay_mail_setting("MAIL_USERNAME")
    password = _public_stay_mail_setting("MAIL_PASSWORD")

    use_tls = str(
        _public_stay_mail_setting("MAIL_USE_TLS", True)
    ).lower() in {"true", "1", "yes", "on"}

    use_ssl = str(
        _public_stay_mail_setting("MAIL_USE_SSL", False)
    ).lower() in {"true", "1", "yes", "on"}

    sender = (
        _public_stay_mail_setting("MAIL_DEFAULT_SENDER")
        or STAY_DEFAULT_SENDER
    )

    sender_name = (
        _public_stay_mail_setting("MAIL_DEFAULT_SENDER_NAME")
        or STAY_SENDER_NAME
    )

    if not server or not username or not password:
        logger.error("Stay email not sent: SMTP configuration is incomplete.")
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
            with smtplib.SMTP_SSL(server, port, timeout=30) as smtp:
                smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(server, port, timeout=30) as smtp:
                smtp.ehlo()
                if use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(username, password)
                smtp.send_message(message)

        logger.info("Stay email sent to %s.", recipient)
        return True

    except Exception:
        logger.exception("Failed to send stay email to %s.", recipient)
        return False


def _send_stay_booking_notifications(booking, stay_booking, stay, room):
    """Send customer and internal notifications after database commit."""
    reference = booking.booking_reference
    customer_name = f"{booking.first_name} {booking.last_name}".strip()

    currency = stay_booking.currency
    amount = Decimal(str(booking.total_amount or 0))

    amount_display = (
        f"{currency} "
        f"{amount.quantize(Decimal('0.01')):,.2f}"
    )

    check_in = stay_booking.check_in.strftime("%d %B %Y")
    check_out = stay_booking.check_out.strftime("%d %B %Y")

    rows = [
        ("Booking reference", reference),
        ("Customer", customer_name),
        ("Accommodation", stay_booking.stay_name_snapshot),
        ("Room", stay_booking.room_name_snapshot),
        ("Check-in", check_in),
        ("Check-out", check_out),
        ("Nights", stay_booking.nights),
        ("Rooms", stay_booking.rooms_count),
        ("Adults", booking.adults),
        ("Children", booking.children),
        ("Infants", booking.infants),
        ("Meal plan", stay_booking.meal_plan_snapshot),
        ("Estimated amount", amount_display),
        ("Status", "Pending review"),
    ]

    customer_text = f"""
Hello {customer_name},

Thank you for submitting your accommodation booking request
with The Uncharted Route.

We have received your request. Our team will review the details
and contact you regarding availability and the next steps.

Booking reference: {reference}
Accommodation: {stay_booking.stay_name_snapshot}
Room: {stay_booking.room_name_snapshot}
Check-in: {check_in}
Check-out: {check_out}
Nights: {stay_booking.nights}
Rooms: {stay_booking.rooms_count}
Guests: {booking.total_guests}
Meal plan: {stay_booking.meal_plan_snapshot or "Standard"}
Estimated amount: {amount_display}

Status: Pending review.

Your accommodation is not yet confirmed.

The Uncharted Route
Explore. Experience. Remember.
""".strip()

    admin_text = f"""
A new public stay booking request has been submitted.

Reference: {reference}
Customer: {customer_name}
Email: {booking.email}
Phone: {booking.phone or "Not provided"}

Accommodation: {stay_booking.stay_name_snapshot}
Location: {stay_booking.property_location_snapshot or "Not provided"}
Room: {stay_booking.room_name_snapshot}

Check-in: {check_in}
Check-out: {check_out}
Nights: {stay_booking.nights}
Rooms: {stay_booking.rooms_count}

Adults: {booking.adults}
Children: {booking.children}
Infants: {booking.infants}

Meal plan: {stay_booking.meal_plan_snapshot or "Standard"}
Nightly rate: {currency} {stay_booking.nightly_rate}
Estimated total: {amount_display}

Special requests: {booking.special_requests or "Not provided"}

Status: Pending review.

Please verify availability and pricing before confirming this booking.
""".strip()

    html_rows = "".join(
        f"""
        <tr>
            <td style="padding:11px 14px;color:#66736B;
                border-bottom:1px solid #E9DDC8;">
                {escape(str(label))}
            </td>
            <td style="padding:11px 14px;color:#1C2822;
                font-weight:600;border-bottom:1px solid #E9DDC8;">
                {escape(str(value if value not in (None, "") else "Not provided"))}
            </td>
        </tr>
        """
        for label, value in rows
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:30px 12px;background:#F7F1E5;
        font-family:Arial,sans-serif;color:#1C2822;">
        <div style="max-width:640px;margin:auto;background:white;
            border:1px solid #E9DDC8;border-radius:12px;overflow:hidden;">
            <div style="background:#12372A;padding:28px 30px;color:white;">
                <div style="color:#D89B24;font-size:12px;
                    letter-spacing:2px;font-weight:bold;">
                    THE UNCHARTED ROUTE
                </div>
                <h2>Stay booking request received</h2>
            </div>
            <div style="padding:28px 30px;">
                <p>Hello {escape(customer_name)},</p>
                <p>Thank you for submitting your accommodation booking
                request. Our team will review it and contact you.</p>
                <table style="width:100%;border-collapse:collapse;">
                    {html_rows}
                </table>
                <p style="color:#66736B;font-size:13px;margin-top:25px;">
                    Your accommodation is not yet confirmed.
                </p>
            </div>
            <div style="padding:17px;background:#F7F1E5;
                text-align:center;color:#66736B;font-size:12px;">
                Explore. Experience. Remember.
            </div>
        </div>
    </body>
    </html>
    """

    _send_public_stay_email(
        booking.email,
        f"Stay booking request received | {reference}",
        customer_text,
        html_body,
    )

    _send_public_stay_email(
        STAY_ADMIN_EMAIL,
        f"New stay booking request | {reference}",
        admin_text,
        html_body,
    )


def create_stay_booking(
    *,
    stay_id,
    room_id,
    check_in,
    check_out,
    rooms=1,
    adults=1,
    children=0,
    infants=0,
    first_name,
    last_name,
    email,
    phone=None,
    nationality=None,
    country_of_residence=None,
    meal_plan=None,
    special_requests=None,
    customer_notes=None,
    status=None,
):
    """
    Create a public stay booking request.

    This function is separate from the admin StayBookingService methods.
    Both booking records are committed atomically.

    This creates an accommodation request only. Hotel availability and final
    pricing are verified manually by the TUR team before confirmation.
    No room inventory is reserved or deducted during public submission.
    """
    stay = Stay.query.filter_by(
        id=stay_id,
        active=True,
    ).first()

    if not stay:
        raise ValueError("This accommodation is currently unavailable.")

    room = StayRoom.query.filter_by(
        id=room_id,
        stay_id=stay.id,
        active=True,
    ).first()

    if not room:
        raise ValueError("Please select a valid room.")

    # Validate and normalize submitted values.
    check_in = check_in if isinstance(check_in, date) else date.fromisoformat(str(check_in))
    check_out = check_out if isinstance(check_out, date) else date.fromisoformat(str(check_out))

    rooms = int(rooms or 1)
    adults = int(adults or 0)
    children = int(children or 0)
    infants = int(infants or 0)

    if check_in < date.today():
        raise ValueError("Check-in cannot be in the past.")

    if check_out <= check_in:
        raise ValueError("Check-out must be after check-in.")

    if rooms < 1:
        raise ValueError("At least one room must be selected.")

    if adults + children + infants < 1:
        raise ValueError("Your booking must include at least one guest.")

    # Occupancy limits apply across the number of rooms requested.
    maximum_guests = int(room.maximum_guests or 0) * rooms
    maximum_adults = int(room.maximum_adults or 0) * rooms
    maximum_children = int(room.maximum_children or 0) * rooms

    if adults + children > maximum_guests:
        raise ValueError(
            f"The selected room arrangement accommodates a maximum of "
            f"{maximum_guests} adults and children across {rooms} room(s)."
        )

    if adults > maximum_adults:
        raise ValueError(
            f"The selected room arrangement accommodates a maximum of "
            f"{maximum_adults} adults across {rooms} room(s)."
        )

    if children > maximum_children:
        raise ValueError(
            f"The selected room arrangement accommodates a maximum of "
            f"{maximum_children} children across {rooms} room(s)."
        )

    email = str(email or "").strip()

    if (
        not email
        or "@" not in email
        or "." not in email.rsplit("@", 1)[-1]
    ):
        raise ValueError("Please provide a valid email address.")

    first_name = str(first_name or "").strip()
    last_name = str(last_name or "").strip()

    if not first_name or not last_name:
        raise ValueError("Please provide your first and last name.")

    nights = (check_out - check_in).days

    if nights < (stay.minimum_nights or 1):
        raise ValueError(
            f"This accommodation requires a minimum stay of "
            f"{stay.minimum_nights} night(s)."
        )

    nightly_rate = _public_stay_decimal(room.nightly_rate)
    currency = str(room.currency or "KES").upper()

    if len(currency) != 3:
        raise ValueError("The selected room has an invalid currency.")

    total = (
        nightly_rate * nights * rooms
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    selected_meal_plan = (
        str(meal_plan or "").strip()
        or room.meal_plan
        or "Bed & Breakfast"
    )

    stay_name = (
        getattr(stay, "property_name", None)
        or f"Stay #{stay.id}"
    )

    room_name = (
        getattr(room, "name", None)
        or getattr(room, "room_type", None)
        or f"Room #{room.id}"
    )

    booking = Booking(
        booking_type="stay",
        source="website",
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=str(phone or "").strip() or None,
        nationality=nationality,
        country_of_residence=country_of_residence,
        adults=adults,
        children=children,
        infants=infants,
        status="pending",
        payment_status="unpaid",
        booking_date=datetime.utcnow(),
        start_date=check_in,
        end_date=check_out,
        currency=currency,
        subtotal=total,
        discount_amount=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        addon_total=Decimal("0.00"),
        total_amount=total,
        amount_paid=Decimal("0.00"),
        balance_due=total,
        special_requests=special_requests,
        customer_notes=customer_notes or (
            "Public website stay booking request. "
            "Availability and final confirmation are pending."
        ),
        internal_notes=(
            "Public website accommodation request. No hotel inventory has "
            "been checked or reserved. Contact the property to verify "
            "availability and final pricing before confirming."
        ),
    )

    stay_detail = StayBooking(
        stay_id=stay.id,
        room_id=room.id,
        stay_name_snapshot=stay_name,
        property_location_snapshot=(
            getattr(stay, "location", None)
            or getattr(stay, "address", None)
        ),
        room_name_snapshot=room_name,
        room_description_snapshot=(
            getattr(room, "description", None)
            or getattr(room, "short_description", None)
        ),
        meal_plan=selected_meal_plan,
        meal_plan_snapshot=selected_meal_plan,
        check_in=check_in,
        check_out=check_out,
        nights=nights,
        rooms_count=rooms,
        adults=adults,
        children=children,
        infants=infants,
        occupancy_snapshot={
            "adults": adults,
            "children": children,
            "infants": infants,
            "rooms": rooms,
        },
        rate_name_snapshot=f"{room_name} — Standard Room Rate",
        rate_basis="per_room_per_night",
        nightly_rate=nightly_rate,
        currency=currency,
        special_requests=special_requests,
    )

    try:
        booking.stay_booking = stay_detail
        db.session.add(booking)
        db.session.flush()
        db.session.commit()

    except Exception:
        db.session.rollback()
        logger.exception("Failed to save public stay booking.")
        raise

    try:
        _send_stay_booking_notifications(
            booking=booking,
            stay_booking=stay_detail,
            stay=stay,
            room=room,)
    except Exception:
        logger.exception(
            "Unexpected notification error for stay booking %s.",
            booking.booking_reference,)
    return booking