# =============================================================================
# The Uncharted Route
# Admin Destination Journey Booking Routes
# =============================================================================
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app,)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.decorators.admin import admin_required
from app.forms.bookings.destination_booking_forms import (
    DestinationBookingForm,
    DestinationBookingStatusForm,
    DestinationBookingCommunicationForm,
    DestinationBookingRequestInformationForm,)
from app.services.bookings.destination_booking_service import (
    DestinationBookingService,)
from app.services.settings_service import SettingsService
from app.services.email_service import EmailService

destination_bookings_bp = Blueprint(
    "admin_destination_bookings",
    __name__,
    url_prefix="/admin/booking/destinations",)

def _commit(success_message):
    try:
        db.session.commit()
        flash(success_message, "success")
        return True
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to save destination journey booking."
        )
        flash("The booking could not be saved. Please try again.", "error")
        return False


def _populate_form(form):
    DestinationBookingService.populate_form_choices(form)


def _load_form(form, booking):
    detail = booking.destination_booking

    values = {
        "first_name": booking.first_name,
        "last_name": booking.last_name,
        "email": booking.email,
        "phone": booking.phone,
        "nationality": booking.nationality,
        "country_of_residence": booking.country_of_residence,
        "journey_id": detail.journey_id,
        "start_date": detail.start_date,
        "end_date": detail.end_date,
        "duration_days": detail.duration_days,
        "duration_nights": detail.duration_nights,
        "travellers_count": detail.travellers_count,
        "rooming_preferences": detail.rooming_preferences,
        "transport_preferences": detail.transport_preferences,
        "preferred_stops": "\n".join(detail.preferred_stops or []),
        "bespoke_requirements": detail.bespoke_requirements,
        "bespoke": detail.bespoke,
        "pricing_basis": detail.pricing_basis,
        "unit_price": detail.unit_price,
        "currency": detail.currency,
        "booking_date": booking.booking_date,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "source": booking.source,
        "total_amount": booking.total_amount,
        "amount_paid": booking.amount_paid,
        "dietary_requirements": booking.dietary_requirements,
        "medical_information": booking.medical_information,
        "accessibility_requirements": booking.accessibility_requirements,
        "special_requests": booking.special_requests,
        "customer_notes": booking.customer_notes,
        "internal_notes": booking.internal_notes,
    }

    for field, value in values.items():
        if hasattr(form, field):
            getattr(form, field).data = value


@destination_bookings_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    bookings = DestinationBookingService.list_bookings(
        search=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
    )
    return render_template(
        "admin/bookings/destinations/index.html",
        bookings=bookings,
        search=request.args.get("q", ""),
        selected_status=request.args.get("status", ""),
    )


@destination_bookings_bp.route("/archived", methods=["GET"])
@login_required
@admin_required
def archived():
    bookings = DestinationBookingService.list_bookings(archived=True)
    return render_template(
        "admin/bookings/destinations/archived.html",
        bookings=bookings,
    )


@destination_bookings_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = DestinationBookingForm()
    _populate_form(form)

    if form.validate_on_submit():
        try:
            booking = DestinationBookingService.create_booking(
                form,
                created_by_user=current_user,
            )
            db.session.commit()
            flash("Destination journey booking created successfully.", "success")
            return redirect(
                url_for(
                    "admin_destination_bookings.detail",
                    booking_id=booking.id,
                )
            )
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception(
                "Unable to create destination journey booking."
            )
            flash(
                "The booking could not be created. Check the details and try again.",
                "error",
            )

    return render_template(
        "admin/bookings/destinations/create.html",
        form=form,)

@destination_bookings_bp.route("/<int:booking_id>", methods=["GET"])
@login_required
@admin_required
def detail(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    return render_template(
        "admin/bookings/destinations/detail.html",
        booking=booking,
    )


@destination_bookings_bp.route(
    "/<int:booking_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def edit(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    form = DestinationBookingForm()
    _populate_form(form)

    if request.method == "GET":
        _load_form(form, booking)

    if form.validate_on_submit():
        try:
            DestinationBookingService.update_booking(booking, form)
            db.session.commit()
            flash("Destination journey booking updated.", "success")
            return redirect(
                url_for(
                    "admin_destination_bookings.detail",
                    booking_id=booking.id,
                )
            )
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception(
                "Unable to update destination journey booking."
            )
            flash("The booking could not be updated.", "error")

    return render_template(
        "admin/bookings/destinations/edit.html",
        form=form,
        booking=booking,)

@destination_bookings_bp.route(
    "/<int:booking_id>/status",
    methods=["GET", "POST"],)
@login_required
@admin_required
def change_status(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    form = DestinationBookingStatusForm()

    if request.method == "GET":
        form.status.data = booking.status
        form.internal_notes.data = ""

    if form.validate_on_submit():
        try:
            DestinationBookingService.change_status(
                booking,
                form.status.data,
                form.internal_notes.data,
            )
            db.session.commit()
            flash("Booking status updated.", "success")
            return redirect(
                url_for(
                    "admin_destination_bookings.detail",
                    booking_id=booking.id,
                )
            )
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception(
                "Unable to change destination booking status."
            )
            flash("The booking status could not be updated.", "error")

    return render_template(
        "admin/bookings/destinations/status.html",
        form=form,
        booking=booking,
    )


@destination_bookings_bp.route(
    "/<int:booking_id>/archive",
    methods=["POST"],
)
@login_required
@admin_required
def archive(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    DestinationBookingService.archive(booking)
    db.session.commit()
    flash("Booking archived.", "success")
    return redirect(url_for("admin_destination_bookings.index"))


@destination_bookings_bp.route(
    "/<int:booking_id>/restore",
    methods=["POST"],
)
@login_required
@admin_required
def restore(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.archived"))

    DestinationBookingService.restore(booking)
    db.session.commit()
    flash("Booking restored.", "success")
    return redirect(url_for("admin_destination_bookings.detail", booking_id=booking.id))


@destination_bookings_bp.route(
    "/<int:booking_id>/delete",
    methods=["POST"],
)
@login_required
@admin_required
def delete(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    linked_history = any([
        bool(booking.payments),
        bool(booking.travellers),
        bool(booking.addons),
        bool(booking.notes),
        bool(booking.documents),
        bool(booking.staff_assignments),
        bool(booking.tasks),
        bool(booking.reviews),
        bool(booking.amount_paid),
    ])

    if linked_history:
        flash(
            "This booking has financial or linked history. Archive it instead.",
            "error",
        )
        return redirect(
            url_for("admin_destination_bookings.detail", booking_id=booking.id)
        )

    db.session.delete(booking)
    db.session.commit()
    flash("Booking deleted.", "success")
    return redirect(url_for("admin_destination_bookings.index"))


@destination_bookings_bp.route(
    "/<int:booking_id>/communicate",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def communicate(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    form = DestinationBookingCommunicationForm()

    if form.validate_on_submit():
        settings = SettingsService.get_settings()
        success = EmailService.send_email(
            recipient=booking.email,
            subject=form.subject.data,
            body=form.message.data,
            reply_to=getattr(settings, "booking_email", None),
        )

        if success:
            flash("Email sent to the customer.", "success")
            return redirect(
                url_for("admin_destination_bookings.detail", booking_id=booking.id)
            )

        flash("Email could not be sent. Please check your email configuration.", "error")

    return render_template(
        "admin/bookings/destinations/communication.html",
        form=form,
        booking=booking,
    )


@destination_bookings_bp.route(
    "/<int:booking_id>/request-information",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def request_information(booking_id):
    booking = DestinationBookingService.get_booking(booking_id)
    if booking is None:
        flash("Destination journey booking not found.", "error")
        return redirect(url_for("admin_destination_bookings.index"))

    form = DestinationBookingRequestInformationForm()

    if form.validate_on_submit():
        settings = SettingsService.get_settings()
        success = EmailService.send_email(
            recipient=booking.email,
            subject=form.subject.data,
            body=form.message.data,
            reply_to=getattr(settings, "booking_email", None),
        )

        if success:
            flash("Information request sent to the customer.", "success")
            return redirect(
                url_for("admin_destination_bookings.detail", booking_id=booking.id))

        flash("The information request could not be sent.", "error")

    return render_template(
        "admin/bookings/destinations/request_information.html",
        form=form,
        booking=booking,)