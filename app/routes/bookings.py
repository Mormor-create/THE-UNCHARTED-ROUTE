"""
===============================================================================
The Uncharted Route
Public Booking Routes
===============================================================================

Public booking flows for:
    - Experiences
    - Destination Journeys
    - Stays

Business logic belongs to Booking Service.

This route module is responsible for:
    - displaying booking forms
    - validating WTForms
    - collecting request data
    - calling Booking Service
    - redirecting customers through the success/confirmation flow

Payment gateway processing remains outside this module.
===============================================================================
"""

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,)
from app.forms.booking_form import BookingForm
from app.forms.bookings.destination_booking_forms import (
    DestinationBookingForm,)
from app.forms.bookings.stay_booking_forms import (
    StayBookingForm,)
from app.models import (
    Experience,
    ExperiencePricing,
    DestinationJourney,
    Stay,
    StayRoom,)
from extensions import db
from app.services.bookings.booking_service import (
    BOOKING_STATUSES,
    cancel_booking,
    complete_booking,
    confirm_booking,
    create_booking,
    get_booking,
    get_booking_by_reference,
    get_booking_by_uuid,
    get_booking_summary,
    update_booking_status,)

# =============================================================================
# Blueprint
# =============================================================================
bookings_bp = Blueprint(
    "booking",
    __name__,
    url_prefix="/booking",)

# =============================================================================
# Helpers
# =============================================================================
def _wants_json():
    """
    Determine whether the request expects JSON.
    """

    accept = request.headers.get(
        "Accept",
        "",
    )

    return (
        request.is_json
        or request.args.get("format") == "json"
        or "application/json" in accept
    )


def _booking_to_dict(booking):
    """
    Convert a booking summary to a JSON-safe dictionary.
    """

    summary = get_booking_summary(
        booking
    )

    if summary is None:
        return None

    result = dict(summary)

    for field in (
        "experience_date",
        "destination_start_date",
        "destination_end_date",
        "stay_check_in",
        "stay_check_out",
        "created_at",
        "updated_at",
    ):
        value = result.get(field)

        if hasattr(value, "isoformat"):
            result[field] = value.isoformat()

    for field in (
        "subtotal",
        "discount_amount",
        "tax_amount",
        "addon_total",
        "total_amount",
        "amount_paid",
        "balance_due",
    ):
        value = result.get(field)

        if value is not None:
            result[field] = str(value)

    return result


def _get_experience_choices():
    """
    Build active experience choices.
    """

    experiences = (
        Experience.query
        .filter_by(active=True)
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
        )
        .all()
    )

    return [
        (
            experience.id,
            experience.title,
        )
        for experience in experiences
    ]


def _get_pricing_choices(experience_id):
    """
    Build active pricing choices for an experience.
    """

    if not experience_id:
        return []

    pricing_options = (
        ExperiencePricing.query
        .filter_by(
            experience_id=experience_id,
            active=True,
        )
        .order_by(
            ExperiencePricing.display_order.asc(),
            ExperiencePricing.id.asc(),
        )
        .all()
    )

    choices = []

    for pricing in pricing_options:

        label = pricing.experience_level

        if pricing.minimum_people is not None:

            if pricing.maximum_people is not None:
                label += (
                    f" "
                    f"({pricing.minimum_people}–"
                    f"{pricing.maximum_people} travellers)"
                )

            else:
                label += (
                    f" "
                    f"({pricing.minimum_people}+ travellers)"
                )

        label += (
            f" — "
            f"{pricing.formatted_price}"
        )

        choices.append(
            (
                pricing.id,
                label,
            )
        )

    return choices


def _prepare_experience_form(
    form,
    selected_experience_id=None,
):
    """
    Populate Experience booking form choices.

    Experience bookings no longer use fixed schedules or departure slots.

    The customer may request an experience date/time through the booking
    flow, and TUR handles feasibility and confirmation separately.
    """

    if selected_experience_id:

        try:
            selected_experience_id = int(
                selected_experience_id
            )

        except (
            TypeError,
            ValueError,
        ):
            selected_experience_id = None

    form.experience_id.choices = (
        [
            (
                0,
                "Select an experience",
            )
        ]
        + _get_experience_choices()
    )

    if selected_experience_id:

        form.experience_id.data = (
            selected_experience_id
        )

    experience_id = (
        form.experience_id.data
        or selected_experience_id
    )

    form.pricing_id.choices = (
        [
            (
                0,
                "Select a pricing level",
            )
        ]
        + _get_pricing_choices(
            experience_id
        )
    )

    return form


def _prepare_stay_form(
    form,
    stay,
):
    """
    Populate room choices for a specific stay.
    """

    rooms = (
        StayRoom.query
        .filter_by(
            stay_id=stay.id,
            active=True,
        )
        .order_by(
            StayRoom.display_order.asc(),
            StayRoom.name.asc(),
        )
        .all()
    )

    form.room_id.choices = [
        (
            room.id,
            f"{room.name} — {room.formatted_rate}",
        )
        for room in rooms
    ]

    return form


# =============================================================================
# Experience Booking
# =============================================================================

@bookings_bp.route(
    "/create",
    methods=["GET", "POST"],
)
def create():
    """
    Public Experience booking form.

    Supports an optional experience_id query parameter:

        /booking/create?experience_id=5

    Experience bookings no longer use fixed schedules or departure slots.
    """

    form = BookingForm()

    selected_experience_id = request.args.get(
        "experience_id",
        type=int,
    )

    _prepare_experience_form(
        form,
        selected_experience_id=selected_experience_id,
    )

    if request.method == "POST":

        if form.validate_on_submit():

            try:

                booking = create_booking(
                    booking_type="experience",

                    experience_id=form.experience_id.data,

                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    nationality=form.nationality.data,
                    country_of_residence=(
                        form.country_of_residence.data
                    ),

                    adults=form.adults.data or 0,
                    children=form.children.data or 0,
                    infants=form.infants.data or 0,
                    seniors=form.seniors.data or 0,
                    students=form.students.data or 0,

                    pricing_id=(
                        form.pricing_id.data
                        or None
                    ),

                    experience_level=(
                        form.experience_level.data
                        or None
                    ),

                    emergency_contact_name=(
                        form.emergency_contact_name.data
                    ),

                    emergency_contact_phone=(
                        form.emergency_contact_phone.data
                    ),

                    emergency_contact_relationship=(
                        form.emergency_contact_relationship.data
                    ),

                    dietary_requirements=(
                        form.dietary_requirements.data
                    ),

                    medical_information=(
                        form.medical_information.data
                    ),

                    accessibility_requirements=(
                        form.accessibility_requirements.data
                    ),

                    special_requests=(
                        form.special_requests.data
                    ),

                    customer_notes=(
                        form.customer_notes.data
                    ),
                )

            except (
                ValueError,
                TypeError,
            ) as exc:

                flash(
                    str(exc),
                    "danger",
                )

            else:

                flash(
                    "Your booking request has been received.",
                    "success",
                )

                return redirect(
                    url_for(
                        "booking.success",
                        booking_reference=(
                            booking.booking_reference
                        ),
                    )
                )

    return render_template(
        "booking/create.html",
        form=form,
    )


# =============================================================================
# Destination Journey Booking
# =============================================================================

@bookings_bp.route(
    "/destination/<int:journey_id>",
    methods=["GET", "POST"],
)
def destination(journey_id):
    """
    Public Destination Journey booking page.
    """

    journey = (
        db.session.get(
            DestinationJourney,
            journey_id,
        )
    )

    if journey is None:
        return render_template(
            "errors/404.html"
        ), 404

    form = DestinationBookingForm()

    if form.validate_on_submit():

        try:

            booking = create_booking(
                booking_type="destination_journey",

                journey_id=journey.id,

                start_date=form.start_date.data,
                end_date=form.end_date.data,

                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                nationality=form.nationality.data,
                country_of_residence=(
                    form.country_of_residence.data
                ),

                adults=form.adults.data or 0,
                children=form.children.data or 0,
                infants=form.infants.data or 0,
                seniors=form.seniors.data or 0,
                students=form.students.data or 0,

                pickup_location=(
                    form.pickup_location.data
                ),

                dropoff_location=(
                    form.dropoff_location.data
                ),

                emergency_contact_name=(
                    form.emergency_contact_name.data
                ),

                emergency_contact_phone=(
                    form.emergency_contact_phone.data
                ),

                emergency_contact_relationship=(
                    form.emergency_contact_relationship.data
                ),

                dietary_requirements=(
                    form.dietary_requirements.data
                ),

                medical_information=(
                    form.medical_information.data
                ),

                accessibility_requirements=(
                    form.accessibility_requirements.data
                ),

                special_requests=(
                    form.special_requests.data
                ),

                customer_notes=(
                    form.customer_notes.data
                ),
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Your journey request has been received.",
                "success",
            )

            return redirect(
                url_for(
                    "booking.success",
                    booking_reference=(
                        booking.booking_reference
                    ),
                )
            )

    return render_template(
        "booking/destination.html",
        form=form,
        journey=journey,
    )


# =============================================================================
# Stay Booking
# =============================================================================

@bookings_bp.route(
    "/stay/<int:stay_id>",
    methods=["GET", "POST"],
)
def stay(stay_id):
    """
    Public stay booking page.
    """

    stay = db.session.get(
        Stay,
        stay_id,
    )

    if stay is None:
        return render_template(
            "errors/404.html"
        ), 404

    form = StayBookingForm()

    _prepare_stay_form(
        form,
        stay,
    )

    if form.validate_on_submit():

        try:

            booking = create_booking(
                booking_type="stay",

                stay_id=stay.id,

                room_id=form.room_id.data,

                check_in=form.check_in.data,
                check_out=form.check_out.data,

                rooms=form.rooms.data or 1,

                adults=form.adults.data or 0,
                children=form.children.data or 0,
                infants=form.infants.data or 0,

                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                nationality=form.nationality.data,
                country_of_residence=(
                    form.country_of_residence.data
                ),

                meal_plan=(
                    form.meal_plan.data
                    or None
                ),

                special_requests=(
                    form.special_requests.data
                ),

                customer_notes=(
                    form.customer_notes.data
                ),
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Your accommodation request has been received.",
                "success",
            )

            return redirect(
                url_for(
                    "booking.success",
                    booking_reference=(
                        booking.booking_reference
                    ),
                )
            )

    return render_template(
        "booking/stay.html",
        form=form,
        stay=stay,
    )


# =============================================================================
# Specific Room Booking
# =============================================================================

@bookings_bp.route(
    "/stay/<int:stay_id>/room/<int:room_id>",
    methods=["GET", "POST"],
)
def stay_room(stay_id, room_id):
    """
    Public booking page for a specific room.
    """

    stay = db.session.get(
        Stay,
        stay_id,
    )

    if stay is None:
        return render_template(
            "errors/404.html"
        ), 404

    room = db.session.get(
        StayRoom,
        room_id,
    )

    if (
        room is None
        or room.stay_id != stay.id
    ):
        return render_template(
            "errors/404.html"
        ), 404

    form = StayBookingForm()

    _prepare_stay_form(
        form,
        stay,
    )

    form.room_id.data = room.id

    if form.validate_on_submit():

        try:

            booking = create_booking(
                booking_type="stay",

                stay_id=stay.id,
                room_id=room.id,

                check_in=form.check_in.data,
                check_out=form.check_out.data,

                rooms=form.rooms.data or 1,

                adults=form.adults.data or 0,
                children=form.children.data or 0,
                infants=form.infants.data or 0,

                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                nationality=form.nationality.data,
                country_of_residence=(
                    form.country_of_residence.data
                ),

                meal_plan=(
                    form.meal_plan.data
                    or None
                ),

                special_requests=(
                    form.special_requests.data
                ),

                customer_notes=(
                    form.customer_notes.data
                ),
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            return redirect(
                url_for(
                    "booking.success",
                    booking_reference=(
                        booking.booking_reference
                    ),
                )
            )

    return render_template(
        "booking/stay.html",
        form=form,
        stay=stay,
        room=room,
    )


# =============================================================================
# Booking Success
# =============================================================================

@bookings_bp.route(
    "/success/<booking_reference>",
    methods=["GET"],
)
def success(booking_reference):
    """
    Public booking success page.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return render_template(
            "errors/404.html"
        ), 404

    return render_template(
        "booking/success.html",
        booking=booking,
    )


# =============================================================================
# Booking Confirmation
# =============================================================================

@bookings_bp.route(
    "/confirmation/<booking_reference>",
    methods=["GET"],
)
def confirmation(booking_reference):
    """
    Detailed public booking confirmation.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return render_template(
            "errors/404.html"
        ), 404

    return render_template(
        "booking/confirmation.html",
        booking=booking,
    )


# =============================================================================
# Booking Lookup
# =============================================================================

@bookings_bp.route(
    "/<booking_reference>",
    methods=["GET"],
)
def detail(booking_reference):
    """
    Backwards-compatible public booking lookup.

    The old application expected a detail endpoint. We now route that
    request into the proper confirmation experience rather than requiring
    a separate detail.html template.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:

        if _wants_json():
            return jsonify({
                "success": False,
                "error": "Booking not found.",
            }), 404

        return render_template(
            "errors/404.html"
        ), 404

    if _wants_json():

        return jsonify({
            "success": True,
            "booking": _booking_to_dict(
                booking
            ),
        })

    return redirect(
        url_for(
            "booking.confirmation",
            booking_reference=(
                booking.booking_reference
            ),
        )
    )


# =============================================================================
# Booking UUID Lookup
# =============================================================================

@bookings_bp.route(
    "/uuid/<booking_uuid>",
    methods=["GET"],
)
def by_uuid(booking_uuid):
    """
    Retrieve a booking by UUID.
    """

    booking = get_booking_by_uuid(
        booking_uuid
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking
        ),
    })


# =============================================================================
# Booking ID Lookup
# =============================================================================

@bookings_bp.route(
    "/id/<int:booking_id>",
    methods=["GET"],
)
def by_id(booking_id):
    """
    Retrieve a booking by database ID.
    """

    booking = get_booking(
        booking_id
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking
        ),
    })


# =============================================================================
# Booking Status
# =============================================================================

@bookings_bp.route(
    "/<booking_reference>/status",
    methods=["PATCH", "POST"],
)
def status(booking_reference):
    """
    Update booking status.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    data = (
        request.get_json(silent=True)
        or request.form
    )

    new_status = data.get(
        "status"
    )

    if not new_status:
        return jsonify({
            "success": False,
            "error": "Booking status is required.",
            "allowed_statuses": sorted(
                BOOKING_STATUSES
            ),
        }), 400

    try:

        booking = update_booking_status(
            booking,
            new_status,
        )

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking
        ),
    })


# =============================================================================
# Confirm
# =============================================================================

@bookings_bp.route(
    "/<booking_reference>/confirm",
    methods=["POST"],
)
def confirm(booking_reference):
    """
    Confirm a booking.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    try:

        booking = confirm_booking(
            booking
        )

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking),})

# =============================================================================
# Complete
# =============================================================================
@bookings_bp.route("/<booking_reference>/complete",methods=["POST"],)
def complete(booking_reference):
    """
    Complete a booking.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    try:

        booking = complete_booking(
            booking
        )

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking),})

# =============================================================================
# Cancel
# =============================================================================
@bookings_bp.route("/<booking_reference>/cancel",methods=["POST"],)
def cancel(booking_reference):
    """
    Cancel a booking.
    """

    booking = get_booking_by_reference(
        booking_reference
    )

    if booking is None:
        return jsonify({
            "success": False,
            "error": "Booking not found.",
        }), 404

    data = (
        request.get_json(silent=True)
        or request.form
    )

    try:

        booking = cancel_booking(
            booking,
            reason=data.get(
                "reason"
            ),
        )

    except ValueError as exc:

        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    return jsonify({
        "success": True,
        "booking": _booking_to_dict(
            booking),})