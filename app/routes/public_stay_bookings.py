"""
===============================================================================
The Uncharted Route
Public Stay Booking Routes
===============================================================================
Public-facing accommodation booking and confirmation routes.
===============================================================================
"""

from datetime import date
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,)
from app.forms.public_stay_booking import PublicStayBookingForm
from app.models import Booking, Stay, StayBooking, StayRoom
from app.services.settings_service import SettingsService
from app.services.bookings.public_stay_booking import create_stay_booking


public_stay_bookings_bp = Blueprint(
    "public_stay_bookings",
    __name__,
    url_prefix="/stays",)

# =============================================================================
# Helpers
# =============================================================================
def _active_stay_or_404(slug):
    """Return an active accommodation or raise 404."""
    stay = Stay.query.filter_by(
        slug=slug,
        active=True,
    ).first()

    if stay is None:
        abort(404)

    return stay


def _active_rooms(stay):
    """Return active rooms belonging to an accommodation."""
    return (
        StayRoom.query
        .filter_by(
            stay_id=stay.id,
            active=True,
        )
        .order_by(StayRoom.id.asc())
        .all()
    )


def _get_stay_booking_page_data(stay, room):
    """Collect property and room information for the booking page."""
    rooms = _active_rooms(stay)

    media = list(getattr(stay, "media", []) or [])
    gallery = []

    for item in media:
        asset = getattr(item, "media_asset", None)

        if asset is None:
            continue

        image_url = (
            getattr(asset, "browser_url", None)
            or getattr(asset, "file_url", None)
        )

        if image_url:
            gallery.append({
                "url": image_url,
                "alt": (
                    getattr(item, "alt_text", None)
                    or getattr(stay, "property_name", None)
                    or "Accommodation"
                ),
                "usage": getattr(item, "usage", None),
            })

    hero_image = next(
        (
            item["url"]
            for item in gallery
            if item["usage"] in {"hero", "cover", "thumbnail"}
        ),
        None,
    )

    if not hero_image:
        hero_image = (
            getattr(stay, "featured_image", None)
            or (gallery[0]["url"] if gallery else None)
        )

    amenities = getattr(stay, "amenities", None) or []

    return {
        "stay": stay,
        "room": room,
        "rooms": rooms,
        "gallery": gallery,
        "hero_image": hero_image,
        "amenities": amenities,
    }


def _populate_room_choices(form, rooms):
    """Populate room choices before WTForms validates the submitted ID."""
    form.room_id.choices = [
        (
            room.id,
            getattr(room, "name", None)
            or getattr(room, "room_type", None)
            or f"Room #{room.id}",
        )
        for room in rooms
    ]


def _prefill_booking_form(form):
    """Prefill booking fields from stay-detail booking links."""
    for field_name in (
        "check_in",
        "check_out",
        "rooms",
        "adults",
        "children",
        "infants",
    ):
        value = request.args.get(field_name)

        if value is None:
            continue

        try:
            field = getattr(form, field_name)

            if field_name in {"rooms", "adults", "children", "infants"}:
                field.data = int(value)

            elif field_name in {"check_in", "check_out"}:
                field.data = date.fromisoformat(value)

        except (TypeError, ValueError):
            continue


def _render_booking_page(stay, form, selected_room):
    """
    Render the booking page without allowing cached CSRF tokens.
    This helps prevent browsers and intermediary caches from reusing
    an outdated booking form.
    """
    room_for_page = next(
        (
            room for room in _active_rooms(stay)
            if room.id == form.room_id.data
        ),
        selected_room,
    )

    page_data = _get_stay_booking_page_data(
        stay,
        room_for_page,
    )

    response = make_response(
        render_template(
            "stays/booking.html",
            form=form,
            booking_enabled=True,
            **page_data,
        )
    )

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, private, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =============================================================================
# Public Stay Booking
# =============================================================================

@public_stay_bookings_bp.route(
    "/<slug>/book",
    methods=["GET", "POST"],
)
def book_stay(slug):
    """Display a stay-specific booking page and process requests."""

    if not SettingsService.bookings_enabled():
        flash(
            "Online booking is temporarily unavailable. "
            "Please contact us to arrange your stay.",
            "info",
        )
        return redirect(
            url_for("stays.detail", slug=slug)
        )

    stay = _active_stay_or_404(slug)
    rooms = _active_rooms(stay)

    if not rooms:
        flash(
            "This accommodation has no bookable rooms at the moment.",
            "warning",
        )
        return redirect(
            url_for("stays.detail", slug=slug)
        )

    form = PublicStayBookingForm()
    _populate_room_choices(form, rooms)

    requested_room_id = request.args.get("room_id", type=int)

    selected_room = next(
        (
            room for room in rooms
            if room.id == requested_room_id
        ),
        None,
    )

    if request.method == "GET":
        if selected_room:
            form.room_id.data = selected_room.id

        _prefill_booking_form(form)

    if form.validate_on_submit():
        try:
            booking = create_stay_booking(
                stay_id=stay.id,
                room_id=form.room_id.data,
                check_in=form.check_in.data,
                check_out=form.check_out.data,
                rooms=form.rooms.data,
                adults=form.adults.data,
                children=form.children.data,
                infants=form.infants.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                nationality=form.nationality.data,
                country_of_residence=form.country_of_residence.data,
                meal_plan=form.meal_plan.data,
                special_requests=form.special_requests.data,
                customer_notes=form.customer_notes.data,
            )

            flash(
                "Your stay booking request has been received. "
                "Please check your email for confirmation of your request.",
                "success",
            )

            return redirect(
                url_for(
                    "public_stay_bookings.booking_confirmation",
                    booking_reference=booking.booking_reference,
                )
            )

        except ValueError as exc:
            flash(str(exc), "warning")

        except Exception:
            current_app.logger.exception(
                "Failed to create public stay booking for stay ID %s.",
                stay.id,
            )

            flash(
                "We couldn't process your stay request right now. "
                "Please review your details or try again shortly.",
                "danger",
            )

    return _render_booking_page(
        stay,
        form,
        selected_room,
    )


# =============================================================================
# Booking Confirmation
# =============================================================================
@public_stay_bookings_bp.route("/booking-confirmation/<booking_reference>",methods=["GET"],)
def booking_confirmation(booking_reference):
    """Display the submitted stay booking request."""
    booking = Booking.query.filter_by(
        booking_reference=booking_reference,
        booking_type="stay",
    ).first_or_404()

    stay_booking = StayBooking.query.filter_by(
        booking_id=booking.id,
    ).first_or_404()

    return render_template(
        "stays/booking_confirmation.html",
        booking=booking,
        stay_booking=stay_booking,
        stay=stay_booking.stay,
        room=stay_booking.room,)