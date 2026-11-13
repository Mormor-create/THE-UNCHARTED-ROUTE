"""Public catalogue and inquiry logic for safari experiences."""
import html
from datetime import date
from secrets import token_hex
from flask import current_app
from sqlalchemy.orm import joinedload
from app.services.email_service import email_service
from extensions import db
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPropertyMedia,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
    SafariInquiry,)
from app.services.safari.currency_service import (
    convert_amount,
    get_conversion_metadata,
    CurrencyConversionError,)

# -----------------------------------------------------------------------------
# Public destination pages
# -----------------------------------------------------------------------------
def get_public_destinations():
    return (
        SafariDestination.query
        .filter_by(active=True)
        .order_by(
            SafariDestination.display_order,
            SafariDestination.name,
        )
        .all()
    )

def get_public_destination(slug):
    return (
        SafariDestination.query
        .filter_by(slug=slug, active=True)
        .options(
            joinedload(SafariDestination.properties)
        )
        .first()
    )

# -----------------------------------------------------------------------------
# Public accommodation pages
# -----------------------------------------------------------------------------
def get_public_properties(destination_id):
    return (
        SafariProperty.query
        .filter_by(destination_id=destination_id, active=True)
        .order_by(
            SafariProperty.display_order,
            SafariProperty.name,
        )
        .all()
    )

def get_public_property(slug):
    return (
        SafariProperty.query
        .filter_by(slug=slug, active=True)
        .options(
            joinedload(SafariProperty.destination),
            joinedload(SafariProperty.media).joinedload(
                SafariPropertyMedia.media_asset
            ),
            joinedload(SafariProperty.package_options),
        )
        .first()
    )

def get_public_property_gallery(property_obj):
    """Return active gallery associations in display order."""
    return (
        SafariPropertyMedia.query
        .filter_by(property_id=property_obj.id, active=True)
        .order_by(
            SafariPropertyMedia.display_order,
            SafariPropertyMedia.id,
        )
        .all()
    )

# -----------------------------------------------------------------------------
# Public duration options and itineraries
# -----------------------------------------------------------------------------
def get_public_package_options(property_obj):
    return (
        SafariPackageOption.query
        .filter_by(property_id=property_obj.id, active=True)
        .order_by(
            SafariPackageOption.display_order,
            SafariPackageOption.duration_days,
        )
        .all()
    )

def get_public_package_option(property_obj, option_id):
    return (
        SafariPackageOption.query
        .filter_by(
            id=option_id,
            property_id=property_obj.id,
            active=True,
        )
        .first()
    )

def get_public_itinerary(option):
    return (
        SafariItineraryDay.query
        .filter_by(
            package_option_id=option.id,
            active=True,
        )
        .order_by(SafariItineraryDay.day_number.asc())
        .all()
    )

# -----------------------------------------------------------------------------
# Public pricing
# -----------------------------------------------------------------------------
def get_public_rates(option, currency=None, travel_date=None):
    """Return active rates valid for the requested travel date.

    Pass currency=None to retrieve supplier rates in all original currencies.
    """
    travel_date = travel_date or date.today()

    query = SafariPackageRate.query.filter_by(
        package_option_id=option.id,
        active=True,
    )

    # Optional legacy filter. Currency conversion pages should omit this.
    if currency:
        query = query.filter_by(currency=currency.upper())

    query = query.filter(
        db.or_(
            SafariPackageRate.valid_from.is_(None),
            SafariPackageRate.valid_from <= travel_date,
        ),
        db.or_(
            SafariPackageRate.valid_to.is_(None),
            SafariPackageRate.valid_to >= travel_date,
        ),
    )

    return query.order_by(
        SafariPackageRate.display_order,
        SafariPackageRate.amount,
    ).all()

def prepare_display_rates(rates, display_currency):
    """Attach display-only prices without changing stored supplier prices."""
    prepared = []
    target = (display_currency or "KES").upper()

    for rate in rates:
        original_currency = (rate.currency or "").upper()

        # These are transient display attributes; amount and currency stay intact.
        rate.original_amount = rate.amount
        rate.original_currency = original_currency
        rate.display_currency = original_currency
        rate.display_amount = rate.amount
        rate.conversion_available = False

        try:
            converted = convert_amount(
                rate.amount,
                original_currency,
                target,
            )
        except CurrencyConversionError:
            # Keep the actual source currency visible if conversion fails.
            pass
        else:
            rate.display_amount = converted
            rate.display_currency = target
            rate.conversion_available = True

        prepared.append(rate)

    return prepared

def get_lowest_public_rate(option, currency="KES", travel_date=None):
    """Return the lowest comparable public rate in the requested currency."""
    rates = get_public_rates(
        option,
        currency=None,
        travel_date=travel_date,
    )

    if not rates:
        return None

    display_rates = prepare_display_rates(rates, currency)

    # Never compare amounts in different currencies as if they were equivalent.
    if not all(rate.conversion_available for rate in display_rates):
        return None

    return min(
        display_rates,
        key=lambda rate: float(rate.display_amount),
    )

def submit_safari_inquiry(property_obj, form, option=None, rate=None):
    """Save a public safari inquiry and notify the traveller and TUR team."""

    if not property_obj or not property_obj.active:
        raise ValueError("This safari property is not currently available.")

    if not property_obj.destination or not property_obj.destination.active:
        raise ValueError("This safari destination is not currently available.")

    if option is not None:
        if option.property_id != property_obj.id or not option.active:
            raise ValueError(
                "The selected duration does not belong to this property."
            )

    if rate is not None:
        if option is None or rate.package_option_id != option.id or not rate.active:
            raise ValueError(
                "The selected rate does not belong to this duration."
            )

    inquiry = SafariInquiry(
        reference=f"TUR-SAF-{token_hex(5).upper()}",
        destination_id=property_obj.destination_id,
        property_id=property_obj.id,
        package_option_id=option.id if option else None,
        rate_id=rate.id if rate else None,
    )

    for field_name in (
        "full_name",
        "email",
        "phone",
        "preferred_start_date",
        "preferred_end_date",
        "adults",
        "children",
        "infants",
        "children_ages",
        "preferred_currency",
        "special_requests",
    ):
        if hasattr(form, field_name):
            setattr(inquiry, field_name, form[field_name].data)

    # Save first. Email failures must never undo a valid inquiry.
    try:
        db.session.add(inquiry)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    def display_value(obj, *attributes, default="Not specified"):
        """Safely get a display value without assuming one model field name."""
        if obj is None:
            return default

        for attribute in attributes:
            value = getattr(obj, attribute, None)
            if value is not None and str(value).strip():
                return str(value)

        return default

    def format_date(value):
        return value.strftime("%d %B %Y") if value else "Not specified"

    try:
        traveller_name = inquiry.full_name or "Traveller"
        destination_name = display_value(
            inquiry.destination, "name", "title", "destination_name"
        )
        property_name = display_value(
            inquiry.property, "name", "title", "property_name", "display_name"
        )
        option_name = display_value(
            inquiry.package_option,
            "name",
            "title",
            "duration_label",
            default="No duration selected",
        )
        rate_name = display_value(
            inquiry.rate,
            "name",
            "title",
            "label",
            default="No specific rate selected",
        )

        start_date = format_date(inquiry.preferred_start_date)
        end_date = format_date(inquiry.preferred_end_date)

        party_details = (
            f"Adults: {inquiry.adults}\n"
            f"Children: {inquiry.children}\n"
            f"Infants: {inquiry.infants}\n"
            f"Children's ages: {inquiry.children_ages or 'Not specified'}"
        )

        special_requests = inquiry.special_requests or "None provided"

        internal_message = (
            "NEW SAFARI INQUIRY — THE UNCHARTED ROUTE\n\n"
            f"Reference: {inquiry.reference}\n"
            f"Traveller: {traveller_name}\n"
            f"Email: {inquiry.email}\n"
            f"Phone: {inquiry.phone or 'Not provided'}\n\n"
            f"Destination: {destination_name}\n"
            f"Property: {property_name}\n"
            f"Duration/package: {option_name}\n"
            f"Selected rate: {rate_name}\n"
            f"Preferred currency: {inquiry.preferred_currency}\n"
            f"Arrival: {start_date}\n"
            f"Departure: {end_date}\n\n"
            f"Travellers:\n{party_details}\n\n"
            f"Special requests:\n{special_requests}\n\n"
            f"Status: {inquiry.status}\n"
            "Please follow up with the traveller."
        )

        admin_recipient = (
            current_app.config.get("MAIL_ADMIN_RECIPIENT")
            or current_app.config.get("MAIL_CONTACT_RECIPIENT")
        )

        # Notify the TUR team.
        try:
            sent = email_service.send_admin_notification(
                subject=f"New Safari Inquiry — {inquiry.reference}",
                message=internal_message,
                recipient=admin_recipient,
            )
            if not sent:
                current_app.logger.error(
                    "Safari inquiry team notification failed: %s",
                    inquiry.reference,
                )
        except Exception:
            current_app.logger.exception(
                "Error sending safari inquiry team notification: %s",
                inquiry.reference,
            )

        # Acknowledge receipt to the traveller.
        safe_name = html.escape(traveller_name)
        safe_reference = html.escape(inquiry.reference)
        safe_destination = html.escape(destination_name)
        safe_property = html.escape(property_name)
        safe_option = html.escape(option_name)
        safe_rate = html.escape(rate_name)
        safe_start = html.escape(start_date)
        safe_end = html.escape(end_date)
        safe_currency = html.escape(inquiry.preferred_currency or "KES")

        customer_body = (
            f"Hello {traveller_name},\n\n"
            "Thank you for contacting The Uncharted Route about your safari.\n"
            "We have received your inquiry and our team will review your "
            "preferences before getting back to you.\n\n"
            f"Your inquiry reference: {inquiry.reference}\n"
            f"Destination: {destination_name}\n"
            f"Property: {property_name}\n"
            f"Package/duration: {option_name}\n"
            f"Selected rate: {rate_name}\n"
            f"Preferred currency: {inquiry.preferred_currency}\n"
            f"Arrival: {start_date}\n"
            f"Departure: {end_date}\n\n"
            "This is an acknowledgement of receipt, not a confirmed booking "
            "or final quotation. We will contact you to discuss the details.\n\n"
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
                <h2>We've received your safari inquiry</h2>
                <p>Hello {safe_name},</p>
                <p>
                    Thank you for your interest in exploring with us.
                    Our team has received your inquiry and will review
                    your preferences before getting back to you.
                </p>
                <div style="background:#FFFFFF;padding:18px;border-radius:8px;">
                    <p><strong>Inquiry reference:</strong> {safe_reference}</p>
                    <p><strong>Destination:</strong> {safe_destination}</p>
                    <p><strong>Property:</strong> {safe_property}</p>
                    <p><strong>Package/duration:</strong> {safe_option}</p>
                    <p><strong>Selected rate:</strong> {safe_rate}</p>
                    <p><strong>Preferred currency:</strong> {safe_currency}</p>
                    <p><strong>Arrival:</strong> {safe_start}</p>
                    <p><strong>Departure:</strong> {safe_end}</p>
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
                subject=f"Safari Inquiry Received — {inquiry.reference}",
                body=customer_body,
                html_body=customer_html,
                reply_to=(
                    current_app.config.get("MAIL_DEFAULT_SENDER")
                ),
            )
            if not sent:
                current_app.logger.error(
                    "Safari inquiry acknowledgement failed: %s",
                    inquiry.reference,
                )
        except Exception:
            current_app.logger.exception(
                "Error sending safari inquiry acknowledgement: %s",
                inquiry.reference,
            )

    except Exception:
        # The inquiry is already committed. Never turn an email or
        # notification problem into a failed inquiry submission.
        current_app.logger.exception(
            "Safari inquiry notification processing failed: %s",
            inquiry.reference,
        )

    return inquiry