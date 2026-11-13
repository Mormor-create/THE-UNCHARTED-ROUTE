"""
===============================================================================
The Uncharted Route
Public Safari Catalogue, Inquiry and Booking Routes
===============================================================================
Public-facing routes for:
    - Safari catalogue
    - Safari destinations
    - Safari properties and package options
    - Supplier rates and currency display
    - Safari inquiries
    - Public safari booking requests
    - Booking and inquiry confirmation pages

Safari inquiries and booking requests remain separate workflows.
A public booking request is not a confirmed reservation. Availability,
supplier confirmation and final pricing may require manual review.
"""

from datetime import date
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.forms.safari import SafariInquiryForm
from app.models.booking import Booking
from app.models.safari import SafariInquiry

from app.services.page_hero_service import PageHeroService
from app.services.settings_service import SettingsService

from app.services.safari.booking_service import (
    SafariBookingValidationError,
    create_public_safari_booking,
)

from app.services.safari.currency_service import (
    get_conversion_metadata,
)

from app.services.safari.public_service import (
    get_public_destinations,
    get_public_destination,
    get_public_properties,
    get_public_property,
    get_public_property_gallery,
    get_public_package_options,
    get_public_package_option,
    get_public_itinerary,
    get_public_rates,
    get_lowest_public_rate,
    prepare_display_rates,
    submit_safari_inquiry,
)


# =============================================================================
# Blueprint Configuration
# =============================================================================
safari_public_bp = Blueprint(
    "safaris",
    __name__,
    url_prefix="/safaris",)

SUPPORTED_CURRENCIES = {
    "KES",
    "USD",
    "EUR",
    "GBP",
    "UGX",
    "TZS",
    "ZAR",
    "NGN",
    "GHS",}

# =============================================================================
# Shared Helpers
# =============================================================================
def _parse_date(value):
    """Parse an optional ISO-formatted date."""
    if not value:
        return None

    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None

def _get_selected_option(property_obj, option_id):
    """
    Return an active package option belonging to the selected property.
    """
    if not option_id:
        return None

    try:
        option_id = int(option_id)
    except (TypeError, ValueError):
        return None

    return get_public_package_option(property_obj, option_id)


def _get_selected_rate(rates, rate_id):
    """
    Return a rate only if it is in the supplied applicable-rate collection.
    """
    if not rate_id:
        return None

    try:
        rate_id = int(rate_id)
    except (TypeError, ValueError):
        return None

    return next(
        (rate for rate in rates if rate.id == rate_id),
        None,
    )


def _get_requested_currency(form=None):
    """Resolve the requested display currency safely."""
    if request.method == "POST" and form is not None:
        requested_currency = (
            form.preferred_currency.data
            if form.preferred_currency.data
            else "KES"
        )
    else:
        requested_currency = request.args.get("currency", "KES")

    requested_currency = str(requested_currency).upper()

    if requested_currency not in SUPPORTED_CURRENCIES:
        return "KES"

    return requested_currency


def _get_conversion_info():
    """Return currency-conversion metadata without breaking catalogue pages."""
    try:
        return get_conversion_metadata()
    except Exception:
        current_app.logger.exception(
            "Unable to retrieve safari currency-conversion metadata."
        )

        return {
            "updated_at": None,
            "stale": True,
            "provider": "ExchangeRate-API",
            "provider_url": "https://www.exchangerate-api.com/",
        }


def _get_property_page_context(
    property_obj,
    form,
    option_id=None,
    rate_id=None,
):
    """
    Build shared context for property details and inquiry pages.

    Supplier rates are retrieved in their original currencies. Conversion
    is used for display only and must not be used to calculate booking totals.
    """
    packages = get_public_package_options(property_obj)

    selected_option = _get_selected_option(
        property_obj,
        option_id,
    )

    # Default to the first public package if the visitor has not selected one.
    if selected_option is None and packages:
        selected_option = packages[0]

    currency = _get_requested_currency(form)

    travel_date = None

    if form is not None and form.preferred_start_date.data:
        travel_date = form.preferred_start_date.data

    if travel_date is None:
        travel_date = _parse_date(
            request.args.get("start_date")
            or request.args.get("travel_date")
        )

    itinerary = []
    rates = []
    selected_rate = None
    starting_rate = None

    if selected_option:
        itinerary = get_public_itinerary(selected_option)

        supplier_rates = get_public_rates(
            selected_option,
            currency=None,
            travel_date=travel_date,
        )

        rates = prepare_display_rates(
            supplier_rates,
            currency,
        )

        starting_rate = get_lowest_public_rate(
            selected_option,
            currency=currency,
            travel_date=travel_date,
        )

        selected_rate = _get_selected_rate(
            rates,
            rate_id,
        )

    return {
        "property": property_obj,
        "destination": property_obj.destination,
        "gallery": get_public_property_gallery(property_obj),
        "packages": packages,
        "selected_option": selected_option,
        "itinerary": itinerary,
        "rates": rates,
        "selected_rate": selected_rate,
        "starting_rate": starting_rate,
        "form": form,
        "selected_currency": currency,
        "conversion_info": _get_conversion_info(),
    }


def _get_booking_settings():
    """Return current public booking and online-payment settings."""
    settings = SettingsService.get_settings()

    return {
        "booking_enabled": bool(settings.booking_enabled),
        "online_payment_enabled": bool(settings.online_payment_enabled),
    }


def _booking_form_redirect(
    slug,
    option_id=None,
    rate_id=None,
    start_date=None,
    end_date=None,
    currency=None,
):
    """Redirect to the dedicated booking page while preserving selections."""
    values = {
        "package_option_id": option_id,
        "rate_id": rate_id,
        "start_date": start_date.isoformat()
        if isinstance(start_date, date)
        else start_date,
        "end_date": end_date.isoformat()
        if isinstance(end_date, date)
        else end_date,
        "currency": currency,
    }

    values = {
        key: value
        for key, value in values.items()
        if value not in (None, "")
    }

    return redirect(
        url_for(
            "safaris.booking_form",
            slug=slug,
            **values,))

# =============================================================================
# Safari Catalogue
# =============================================================================
@safari_public_bp.get("/")
def index():
    """Display the public safari catalogue."""
    destinations = get_public_destinations()

    page_hero = PageHeroService.get_by_page_key("safaris")

    if page_hero and not page_hero.active:
        page_hero = None

    return render_template(
        "safaris/index.html",
        destinations=destinations,
        page_hero=page_hero,)

# =============================================================================
# Safari Destination
# =============================================================================
@safari_public_bp.get("/destinations/<slug>")
def destination_detail(slug):
    """Display a destination story and its active safari properties."""
    destination = get_public_destination(slug)

    if destination is None:
        abort(404)

    properties = get_public_properties(destination.id)

    return render_template(
        "safaris/destination.html",
        destination=destination,
        properties=properties,)

# =============================================================================
# Safari Property
# =============================================================================
@safari_public_bp.route("/properties/<slug>",methods=["GET", "POST"],)
def property_detail(slug):
    """
    Display a safari property and handle existing safari inquiries.
    Booking requests are handled by the dedicated booking routes below.
    """
    property_obj = get_public_property(slug)
    if property_obj is None:
        abort(404)

    form = SafariInquiryForm()
    settings_context = _get_booking_settings()
    def render_property_page(
        option_id=None,
        rate_id=None,
        status=200,):
        context = _get_property_page_context(
            property_obj,
            form,
            option_id=option_id,
            rate_id=rate_id,)
        context.update(settings_context)

        return (
            render_template(
                "safaris/property.html",
                **context,
            ),status,)

    # -------------------------------------------------------------------------
    # GET: Property page and visitor selections
    # -------------------------------------------------------------------------
    if request.method == "GET":
        requested_currency = request.args.get(
            "currency",
            "KES",
        ).upper()

        if requested_currency not in SUPPORTED_CURRENCIES:
            requested_currency = "KES"

        form.preferred_currency.data = requested_currency

        requested_option_id = request.args.get("package_option_id")
        requested_rate_id = request.args.get("rate_id")

        start_date = _parse_date(
            request.args.get("start_date")
        )

        end_date = _parse_date(
            request.args.get("end_date")
        )

        if start_date:
            form.preferred_start_date.data = start_date

        if end_date:
            form.preferred_end_date.data = end_date

        return render_property_page(
            option_id=requested_option_id,
            rate_id=requested_rate_id,
        )

    # -------------------------------------------------------------------------
    # POST: Existing inquiry submission
    # -------------------------------------------------------------------------
    requested_option_id = request.form.get("package_option_id")
    requested_rate_id = request.form.get("rate_id")

    selected_option = _get_selected_option(
        property_obj,
        requested_option_id,
    )

    if requested_option_id and selected_option is None:
        abort(
            400,
            description="The selected safari package is invalid.",
        )

    # -------------------------------------------------------------------------
    # Resolve the customer's preferred currency.
    # This is the authoritative currency submitted with the inquiry.
    # -------------------------------------------------------------------------
    submitted_currency = (
            request.form.get("preferred_currency")
            or "KES"
    ).strip().upper()

    if submitted_currency not in SUPPORTED_CURRENCIES:
        submitted_currency = "KES"

    form.preferred_currency.data = submitted_currency
    selected_rate = None

    if requested_rate_id:
        if selected_option is None:
            abort(
                400,
                description="Choose a safari package before selecting a rate.",
            )

        applicable_rates = get_public_rates(
            selected_option,
            currency=None,
            travel_date=form.preferred_start_date.data,
        )

        selected_rate = _get_selected_rate(
            applicable_rates,
            requested_rate_id,
        )

        if selected_rate is None:
            abort(
                400,
                description=(
                    "That rate is no longer applicable. "
                    "Please select a current rate."
                ),
            )
    requested_currency = submitted_currency

    if form.validate_on_submit():
        try:
            inquiry = submit_safari_inquiry(
                property_obj=property_obj,
                form=form,
                option=selected_option,
                rate=selected_rate,
            )

        except ValueError as exc:
            flash(str(exc), "error")

        except Exception:
            current_app.logger.exception(
                "Failed to submit safari inquiry for property %s.",
                property_obj.id,
            )

            flash(
                "We could not submit your enquiry just now. Please try again.",
                "error",
            )

        else:
            flash(
                "Your safari enquiry has been received.",
                "success",
            )

            return redirect(
                url_for(
                    "safaris.inquiry_success",
                    reference=inquiry.reference,
                )
            )

    return render_property_page(
        option_id=requested_option_id,
        rate_id=requested_rate_id,)

# =============================================================================
# Dedicated Public Safari Booking Form
# =============================================================================
@safari_public_bp.get("/properties/<slug>/book")
def booking_form(slug):
    """
    Display the standalone safari booking form.

    The visitor's package, rate, travel dates and currency selections are
    carried through the query string so the booking page can show the
    applicable package information.
    """
    property_obj = get_public_property(slug)

    if property_obj is None:
        abort(404)

    settings_context = _get_booking_settings()

    if not settings_context["booking_enabled"]:
        flash(
            "Online safari booking requests are temporarily unavailable. "
            "Please send us a safari enquiry instead.",
            "warning",
        )

        return redirect(
            url_for(
                "safaris.property_detail",
                slug=slug,
            )
        )

    form = SafariInquiryForm()

    requested_currency = request.args.get(
        "currency",
        "KES",
    ).upper()

    if requested_currency not in SUPPORTED_CURRENCIES:
        requested_currency = "KES"

    form.preferred_currency.data = requested_currency

    start_date = _parse_date(
        request.args.get("start_date")
    )

    end_date = _parse_date(
        request.args.get("end_date")
    )

    if start_date:
        form.preferred_start_date.data = start_date

    if end_date:
        form.preferred_end_date.data = end_date

    context = _get_property_page_context(
        property_obj,
        form,
        option_id=request.args.get("package_option_id"),
        rate_id=request.args.get("rate_id"),
    )

    context.update(settings_context)

    return render_template(
        "safaris/booking.html",
        **context,)

# =============================================================================
# Dedicated Public Safari Booking Submission
# =============================================================================
@safari_public_bp.post("/properties/<slug>/book/submit")
def submit_public_booking(slug):
    """
    Validate and save a public safari booking request.

    This workflow is deliberately separate from SafariInquiry. It saves
    a central Booking and its SafariBooking detail through the existing
    booking service. The resulting booking remains pending review.
    """
    property_obj = get_public_property(slug)

    if property_obj is None:
        abort(404)

    settings_context = _get_booking_settings()

    if not settings_context["booking_enabled"]:
        flash(
            "Online safari booking requests are temporarily unavailable. "
            "Please send us a safari enquiry instead.",
            "warning",
        )

        return redirect(
            url_for(
                "safaris.property_detail",
                slug=slug,
            )
        )

    option_id = request.form.get("package_option_id")
    rate_id = request.form.get("rate_id")

    submitted_currency = request.form.get(
        "currency",
        "KES",
    ).upper()

    if submitted_currency not in SUPPORTED_CURRENCIES:
        submitted_currency = "KES"

    selected_option = _get_selected_option(
        property_obj,
        option_id,
    )

    if selected_option is None:
        flash(
            "Please select a valid safari package.",
            "error",
        )

        return _booking_form_redirect(
            slug,
            currency=submitted_currency,
        )

    start_date = _parse_date(
        request.form.get("start_date")
    )

    end_date = _parse_date(
        request.form.get("end_date")
    )

    if start_date is None or end_date is None:
        flash(
            "Please select valid safari start and end dates.",
            "error",
        )

        return _booking_form_redirect(
            slug,
            option_id=option_id,
            rate_id=rate_id,
            start_date=request.form.get("start_date"),
            end_date=request.form.get("end_date"),
            currency=submitted_currency,
        )

    # Retrieve the current supplier rates in their original currencies.
    # Never use a converted display amount to calculate a booking total.
    applicable_rates = get_public_rates(
        selected_option,
        currency=None,
        travel_date=start_date,
    )

    selected_rate = _get_selected_rate(
        applicable_rates,
        rate_id,
    )

    if selected_rate is None:
        flash(
            "The selected rate is no longer available for those dates. "
            "Please select a current rate and try again.",
            "error",
        )

        return _booking_form_redirect(
            slug,
            option_id=option_id,
            start_date=start_date,
            end_date=end_date,
            currency=submitted_currency,
        )

    # Only customer-submitted information is passed into the service.
    # Property, package, rate and price are resolved server-side.
    form_data = {
        "first_name": request.form.get("first_name", ""),
        "last_name": request.form.get("last_name", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
        "nationality": request.form.get("nationality", ""),
        "country_of_residence": request.form.get(
            "country_of_residence",
            "",
        ),
        "start_date": start_date,
        "end_date": end_date,
        "adults": request.form.get("adults", 1),
        "children": request.form.get("children", 0),
        "infants": request.form.get("infants", 0),
        "rooms_required": request.form.get("rooms_required", 1),
        "children_ages": request.form.get("children_ages", ""),
        "rooming_preferences": request.form.get(
            "rooming_preferences",
            "",
        ),
        "pickup_location": request.form.get("pickup_location", ""),
        "transfer_requirements": request.form.get(
            "transfer_requirements",
            "",
        ),
        "wildlife_preferences": request.form.get(
            "wildlife_preferences",
            "",
        ),
        "dietary_requirements": request.form.get(
            "dietary_requirements",
            "",
        ),
        "accessibility_requirements": request.form.get(
            "accessibility_requirements",
            "",
        ),
        "special_requests": request.form.get(
            "special_requests",
            "",
        ),
    }

    try:
        booking = create_public_safari_booking(
            property_obj=property_obj,
            package_option=selected_option,
            rate=selected_rate,
            form_data=form_data,
        )

    except SafariBookingValidationError as exc:
        flash(str(exc), "error")

        return _booking_form_redirect(
            slug,
            option_id=option_id,
            rate_id=rate_id,
            start_date=start_date,
            end_date=end_date,
            currency=submitted_currency,
        )

    except Exception:
        current_app.logger.exception(
            "Failed to create public safari booking for property %s.",
            property_obj.id,
        )

        flash(
            "We could not submit your safari booking request. "
            "Please try again or contact our team.",
            "error",
        )

        return _booking_form_redirect(
            slug,
            option_id=option_id,
            rate_id=rate_id,
            start_date=start_date,
            end_date=end_date,
            currency=submitted_currency,
        )

    current_app.logger.info(
        "Public safari booking request %s created.",
        booking.booking_reference,
    )

    return redirect(
        url_for(
            "safaris.booking_received",
            reference=booking.booking_reference,))

# =============================================================================
# Public Safari Booking Confirmation
# =============================================================================
@safari_public_bp.get("/booking/<reference>/received")
def booking_received(reference):
    """Display confirmation for a submitted safari booking request."""
    booking = Booking.query.filter_by(
        booking_reference=reference,
        booking_type="safari",
        source="website",
    ).first_or_404()

    if not booking.safari_booking:
        abort(404)

    return render_template(
        "safaris/booking_success.html",
        booking=booking,
        safari_booking=booking.safari_booking,)

# =============================================================================
# Public Safari Inquiry Confirmation
# =============================================================================
@safari_public_bp.get("/inquiry/<reference>/received")
def inquiry_success(reference):
    """Display confirmation after a successfully submitted safari inquiry."""
    inquiry = SafariInquiry.query.filter_by(
        reference=reference,
    ).first_or_404()

    return render_template(
        "safaris/inquiry_success.html",
        inquiry=inquiry,)