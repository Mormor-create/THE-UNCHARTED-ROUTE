"""
===============================================================================
The Uncharted Route
Public Experience Booking Routes
===============================================================================
"""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from app.models import Booking
from app.services.settings_service import SettingsService
from app.services.bookings.booking_service import (
    BookingServiceError,
    BookingValidationError,
    create_booking,)
from app.services.experiences.experience_booking_service import (
    ExperienceBookingService,)

experience_bookings_bp = Blueprint(
    "experience_bookings",
    __name__,)

# =============================================================================
# Create Experience Booking
# =============================================================================
@experience_bookings_bp.route("/experiences/<slug>/book",methods=["GET", "POST"],)
def create(slug):
    """
    Public Experience booking request.
    Experiences no longer use fixed schedules or departure slots.
    The customer selects:
        - Experience
        - Pricing option
        - Traveller counts
        - Customer/contact details
        - Pickup/drop-off preferences
        - Customer instructions

    The request is saved as a central Booking with an
    ExperienceBooking product-specific detail record.
    """

    experience = (
        ExperienceBookingService.get_bookable_experience(slug)
    )

    if experience is None:
        abort(404)

    if not SettingsService.bookings_enabled():
        flash(
            "Online bookings are temporarily unavailable. "
            "Please contact us to enquire about this experience.",
            "info",)

        return redirect(
            url_for(
                "experiences.detail",
                slug=slug,))

    pricing_options = (
        ExperienceBookingService.get_active_pricing(
            experience.id))

    selected_pricing_id = request.values.get(
        "pricing_id",
        type=int,)

    selected_pricing = None

    if selected_pricing_id:
        selected_pricing = next(
            (
                pricing
                for pricing in pricing_options
                if pricing.id == selected_pricing_id
            ),None,)

    print(
        "[DEBUG] Experience booking:",
        slug,
        "booking_enabled =",
        SettingsService.bookings_enabled(),)

    # =========================================================================
    # POST
    # =========================================================================
    if request.method == "POST":
        try:
            adults = request.form.get(
                "adults",1,)

            children = request.form.get(
                "children",0,)

            infants = request.form.get(
                "infants",0,)

            pricing_id = request.form.get(
                "pricing_id") or None

            # -----------------------------------------------------------------
            # Validate traveller counts
            # -----------------------------------------------------------------
            guest_counts = (
                ExperienceBookingService.validate_guest_counts(
                    adults=adults,
                    children=children,
                    infants=infants,))

            total_guests = sum(guest_counts.values())

            # -----------------------------------------------------------------
            # Validate pricing
            # -----------------------------------------------------------------
            pricing = (
                ExperienceBookingService.validate_pricing(
                    experience,
                    pricing_id=pricing_id,
                    guest_count=total_guests,))

            # -----------------------------------------------------------------
            # Calculate the experience total
            # -----------------------------------------------------------------
            experience_total = (
                ExperienceBookingService.calculate_total(
                    pricing,
                    adults=guest_counts["adults"],
                    children=guest_counts["children"],
                    infants=guest_counts["infants"],))

            # -----------------------------------------------------------------
            # Build product-specific ExperienceBooking detail
            # -----------------------------------------------------------------
            experience_booking = (
                ExperienceBookingService.build_booking_detail(
                    experience=experience,
                    pricing=pricing,
                    adults=guest_counts["adults"],
                    children=guest_counts["children"],
                    infants=guest_counts["infants"],
                    pickup_location=request.form.get("pickup_location"),
                    dropoff_location=request.form.get("dropoff_location"),
                    customer_instructions=request.form.get("customer_instructions"),))

            # -----------------------------------------------------------------
            # Build central Booking data
            #
            # Shared customer/lifecycle/financial data belongs to Booking.
            # Product-specific data belongs to ExperienceBooking.
            # -----------------------------------------------------------------
            booking_data = {
                "first_name": request.form.get(
                    "first_name",
                    "",),

                "last_name": request.form.get(
                    "last_name",
                    "",),

                "email": request.form.get(
                    "email",
                    "",),

                "phone": request.form.get(
                    "phone"),
                "nationality": request.form.get(
                    "nationality"),
                "country_of_residence": request.form.get(
                    "country_of_residence"),
                "adults": guest_counts["adults"],
                "children": guest_counts["children"],
                "infants": guest_counts["infants"],
                "customer_notes": request.form.get(
                    "customer_notes"),
                "experience_date": request.form.get(
                    "experience_date"),

                "subtotal": experience_total,
                "discount_amount": 0,
                "tax_amount": 0,
                "addon_total": 0,
                "currency": pricing.currency,
                "status": "pending",
                "payment_status": "unpaid",
                "source": "website",}

            # -----------------------------------------------------------------
            # Create central Booking + ExperienceBooking detail
            # -----------------------------------------------------------------
            booking = create_booking(
                data=booking_data,
                booking_type="experience",
                source="website",
                detail=experience_booking,)

            # -----------------------------------------------------------------
            # Confirmation
            # -----------------------------------------------------------------
            return redirect(
                url_for(
                    "experience_bookings.confirmation",
                    reference=booking.booking_reference,))

        except (
            BookingValidationError,
            BookingServiceError,
            ValueError,
            TypeError,) as exc:

            flash(str(exc),"error",)

            # Preserve the submitted pricing selection
            selected_pricing = next(
                (
                    pricing
                    for pricing in pricing_options
                    if pricing.id == selected_pricing_id),None,)

    # =========================================================================
    # GET / failed POST
    # =========================================================================
    return render_template(
        "experience_bookings/create.html",
        experience=experience,
        pricing_options=pricing_options,
        selected_pricing=selected_pricing,)

# =============================================================================
# Confirmation
# =============================================================================
@experience_bookings_bp.route("/experience-bookings/<reference>/confirmation",methods=["GET"],)
def confirmation(reference):
    """
    Display confirmation for a website Experience booking.
    """
    booking = (
        Booking.query
        .filter_by(
            booking_reference=reference,
            booking_type="experience",
            source="website",
        ).first_or_404())

    return render_template(
        "experience_bookings/confirmation.html",
        booking=booking,
        experience_booking=booking.experience_booking,)