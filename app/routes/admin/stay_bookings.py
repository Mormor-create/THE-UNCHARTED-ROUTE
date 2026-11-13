"""
===============================================================================
The Uncharted Route
Stay Booking Administration
===============================================================================
"""
from datetime import datetime
from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, url_for,)
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.decorators.admin import admin_required
from app.forms.bookings.stay_booking_forms import (
    StayBookingForm,
    StayBookingStatusForm,
    StayBookingCommunicationForm,
    StayBookingRequestInformationForm,)
from app.services.bookings.stay_booking_service import StayBookingService
from app.services.settings_service import SettingsService
from app.services.email_service import EmailService

stay_bookings_bp = Blueprint(
    "admin_stay_bookings",
    __name__,
    url_prefix="/admin/booking/stays",)

def _commit(success_message, error_message):
    try:
        db.session.commit()
        flash(success_message, "success")
        return True
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Stay booking database operation failed.")
        flash(error_message, "danger")
        return False

def _populate(form):
    StayBookingService.populate_form_choices(form)


def _load_form(form, booking):
    """Load central and accommodation values into the edit form."""
    detail = booking.stay_booking

    for name in (
        "first_name", "last_name", "email", "phone", "nationality",
        "country_of_residence", "status", "payment_status", "booking_date",
        "dietary_requirements", "accessibility_requirements",
        "special_requests", "customer_notes", "internal_notes",
    ):
        if hasattr(form, name):
            getattr(form, name).data = getattr(booking, name, None)

    form.amount_paid.data = str(booking.amount_paid or 0)
    form.currency_total.data = str(booking.total_amount or 0)

    for name in (
        "stay_id", "room_id", "meal_plan", "meal_plan_snapshot",
        "check_in", "check_out", "nights", "rooms_count", "adults",
        "children", "infants", "rate_name_snapshot", "rate_basis",
        "nightly_rate", "currency", "arrival_time", "departure_time",
        "availability_reference",
    ):
        value = getattr(detail, name, None)
        if name == "room_id":
            value = value or 0
        if value is not None and hasattr(form, name):
            getattr(form, name).data = value


@stay_bookings_bp.route("/")
@admin_required
def index():
    bookings = StayBookingService.list_bookings(
        search=request.args.get("q", "").strip(),
        status=request.args.get("status", "all"),
    )
    return render_template(
        "admin/bookings/stays/index.html",
        bookings=bookings,
        search=request.args.get("q", ""),
        selected_status=request.args.get("status", "all"),)

@stay_bookings_bp.route("/archived")
@admin_required
def archived():
    return render_template(
        "admin/bookings/stays/archived.html",
        bookings=StayBookingService.list_bookings(archived=True),)

@stay_bookings_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    form = StayBookingForm()
    _populate(form)

    if form.validate_on_submit():
        try:
            booking = StayBookingService.create_booking(
                form, created_by_user=current_user
            )
            db.session.commit()
            flash("Stay booking created successfully.", "success")
            return redirect(url_for(
                "admin_stay_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not create stay booking.")
            flash(
                "Unable to create the stay booking. Check the submitted details.",
                "danger",
            )

    return render_template(
        "admin/bookings/stays/create.html", form=form, booking=None)

@stay_bookings_bp.route("/<int:booking_id>")
@admin_required
def detail(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    return render_template(
        "admin/bookings/stays/detail.html", booking=booking)

@stay_bookings_bp.route("/<int:booking_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    if not booking.stay_booking:
        flash("Accommodation-specific details are missing.", "danger")
        return redirect(url_for(
            "admin_stay_bookings.detail", booking_id=booking.id
        ))

    form = StayBookingForm()
    if request.method == "GET":
        _load_form(form, booking)

    _populate(form)

    if form.validate_on_submit():
        try:
            StayBookingService.update_booking(booking, form)
            db.session.commit()
            flash("Stay booking updated successfully.", "success")
            return redirect(url_for(
                "admin_stay_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not update stay booking.")
            flash("Unable to update the stay booking.", "danger")

    return render_template(
        "admin/bookings/stays/edit.html", form=form, booking=booking)

@stay_bookings_bp.route(
    "/<int:booking_id>/status", methods=["GET", "POST"])
@admin_required
def change_status(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    form = StayBookingStatusForm()

    if request.method == "GET":
        form.status.data = booking.status

    if form.validate_on_submit():
        try:
            StayBookingService.change_status(
                booking, form.status.data, form.internal_notes.data
            )
            db.session.commit()
            flash("Stay booking status updated.", "success")
            return redirect(url_for(
                "admin_stay_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not update stay status.")
            flash("Unable to update stay booking status.", "danger")

    return render_template(
        "admin/bookings/stays/status.html", booking=booking, form=form)

@stay_bookings_bp.route("/<int:booking_id>/archive", methods=["POST"])
@admin_required
def archive(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    StayBookingService.archive(booking)

    if _commit("Stay booking archived.", "Unable to archive stay booking."):
        return redirect(url_for("admin_stay_bookings.archived"))

    return redirect(url_for(
        "admin_stay_bookings.detail", booking_id=booking.id
    ))


@stay_bookings_bp.route("/<int:booking_id>/restore", methods=["POST"])
@admin_required
def restore(booking_id):
    booking = StayBookingService.get_booking(booking_id)

    if booking.status != "archived":
        flash("Only archived booking can be restored.", "warning")
        return redirect(url_for(
            "admin_stay_bookings.detail", booking_id=booking.id
        ))

    StayBookingService.restore(booking)
    if _commit("Stay booking restored.", "Unable to restore stay booking."):
        return redirect(url_for(
            "admin_stay_bookings.detail", booking_id=booking.id
        ))

    return redirect(url_for("admin_stay_bookings.archived"))


@stay_bookings_bp.route("/<int:booking_id>/delete", methods=["POST"])
@admin_required
def delete(booking_id):
    booking = StayBookingService.get_booking(booking_id)

    linked_history = (
        booking.payments, booking.travellers, booking.addons, booking.notes,
        booking.documents, booking.staff_assignments, booking.tasks, booking.reviews,
    )
    if any(linked_history) or (booking.amount_paid and booking.amount_paid > 0):
        flash(
            "This booking has financial or linked history. Archive it instead.",
            "warning",
        )
        return redirect(url_for(
            "admin_stay_bookings.detail", booking_id=booking.id
        ))

    try:
        db.session.delete(booking)
        db.session.commit()
        flash("Stay booking deleted.", "success")
        return redirect(url_for("admin_stay_bookings.index"))
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not delete stay booking.")
        flash("Unable to delete this booking. Archive it instead.", "danger")
        return redirect(url_for(
            "admin_stay_bookings.detail", booking_id=booking.id
        ))

@stay_bookings_bp.route(
    "/<int:booking_id>/communicate", methods=["GET", "POST"])
@admin_required
def communicate(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    form = StayBookingCommunicationForm()

    if request.method == "GET":
        form.recipient.data = booking.email

    if form.validate_on_submit():
        try:
            settings = SettingsService.get_settings()
            sent = EmailService.send_email(
                recipient=form.recipient.data.strip(),
                subject=form.subject.data.strip(),
                body=form.message.data,
                reply_to=getattr(settings, "booking_email", None),
            )
            if sent:
                flash("Message sent successfully.", "success")
            else:
                flash("The email service did not confirm delivery.", "danger")
            return redirect(url_for(
                "admin_stay_bookings.detail", booking_id=booking.id
            ))
        except Exception:
            current_app.logger.exception("Stay booking email failed.")
            flash("Unable to send the message. Check email configuration.", "danger")

    return render_template(
        "admin/bookings/stays/communication.html",
        booking=booking, form=form,
    )


@stay_bookings_bp.route(
    "/<int:booking_id>/request-information", methods=["GET", "POST"]
)
@admin_required
def request_information(booking_id):
    booking = StayBookingService.get_booking(booking_id)
    form = StayBookingRequestInformationForm()

    if form.validate_on_submit():
        try:
            settings = SettingsService.get_settings()
            sent = EmailService.send_email(
                recipient=booking.email,
                subject=f"Additional information needed — {booking.booking_reference}",
                body=form.message.data,
                reply_to=getattr(settings, "booking_email", None),
            )
            if not sent:
                flash("The email service did not confirm delivery.", "danger")
            else:
                booking.internal_notes = (
                    f"{booking.internal_notes or ''}\n\n"
                    f"Information requested {datetime.utcnow():%Y-%m-%d %H:%M}:\n"
                    f"{form.message.data}"
                ).strip()
                db.session.commit()
                flash("Information request sent.", "success")

            return redirect(url_for(
                "admin_stay_bookings.detail", booking_id=booking.id
            ))
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Stay information request failed.")
            flash("Unable to send the information request.", "danger")

    return render_template(
        "admin/bookings/stays/request_information.html",
        booking=booking, form=form,)