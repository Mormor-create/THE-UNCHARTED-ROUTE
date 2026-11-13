"""
===============================================================================
The Uncharted Route
Safari Booking Administration
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
from app.forms.bookings.safari_booking_forms import (
    SafariBookingForm,
    SafariBookingCommunicationForm,
    SafariBookingRequestInformationForm,
    SafariBookingStatusForm,)
from app.services.bookings.safari_booking_service import SafariBookingService
from app.services.settings_service import SettingsService
from app.services.email_service import EmailService

safari_bookings_bp = Blueprint(
    "admin_safari_bookings",
    __name__,
    url_prefix="/admin/booking/safaris",)

def _save_or_rollback(success_message, error_message):
    try:
        db.session.commit()
        flash(success_message, "success")
        return True
    except (SQLAlchemyError, ValueError):
        db.session.rollback()
        current_app.logger.exception("Safari booking operation failed.")
        flash(error_message, "danger")
        return False


def _populate(form):
    SafariBookingService.populate_form_choices(form)

@safari_bookings_bp.route("/")
@admin_required
def index():
    bookings = SafariBookingService.list_bookings(
        search=request.args.get("q", "").strip(),
        status=request.args.get("status", "all"),
    )
    return render_template(
        "admin/bookings/safaris/index.html",
        bookings=bookings,
        search=request.args.get("q", ""),
        selected_status=request.args.get("status", "all"),)

@safari_bookings_bp.route("/archived")
@admin_required
def archived():
    bookings = SafariBookingService.list_bookings(archived=True)
    return render_template(
        "admin/bookings/safaris/archived.html", bookings=bookings)

@safari_bookings_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    form = SafariBookingForm()
    _populate(form)

    if form.validate_on_submit():
        try:
            booking = SafariBookingService.create_booking(
                form, created_by_user=current_user
            )
            db.session.commit()
            flash("Safari booking created successfully.", "success")
            return redirect(url_for(
                "admin_safari_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not create safari booking.")
            flash("Unable to create the safari booking. Check the details and try again.", "danger")

    return render_template(
        "admin/bookings/safaris/create.html", form=form, booking=None)

@safari_bookings_bp.route("/<int:booking_id>")
@admin_required
def detail(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    return render_template(
        "admin/bookings/safaris/detail.html", booking=booking)

@safari_bookings_bp.route("/<int:booking_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    if not booking.safari_booking:
        flash("Safari-specific details are missing for this booking.", "danger")
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id
        ))

    form = SafariBookingForm(obj=booking.safari_booking)
    if request.method == "GET":
        form.first_name.data = booking.first_name
        form.last_name.data = booking.last_name
        form.email.data = booking.email
        form.phone.data = booking.phone
        form.nationality.data = booking.nationality
        form.country_of_residence.data = booking.country_of_residence
        form.status.data = booking.status
        form.payment_status.data = booking.payment_status
        form.booking_date.data = booking.booking_date
        form.adults.data = booking.adults
        form.children.data = booking.children
        form.infants.data = booking.infants
        form.currency_total.data = str(booking.total_amount or 0)
        form.amount_paid.data = str(booking.amount_paid or 0)
        form.dietary_requirements.data = booking.dietary_requirements
        form.accessibility_requirements.data = booking.accessibility_requirements
        form.special_requests.data = booking.special_requests
        form.customer_notes.data = booking.customer_notes
        form.internal_notes.data = booking.internal_notes

    _populate(form)

    if request.method == "GET":
        detail = booking.safari_booking
        for name in (
            "safari_destination_id", "property_id", "package_option_id",
            "package_rate_id", "start_date", "end_date", "duration_days",
            "duration_nights", "rooms_required", "rooming_preferences",
            "rate_name_snapshot", "rate_basis", "unit_rate", "quantity",
            "currency", "pickup_location", "transfer_requirements",
            "wildlife_interests", "special_safari_requirements",
        ):
            value = getattr(detail, name, None)
            if name in ("safari_destination_id", "property_id", "package_rate_id"):
                value = value or 0
            if value is not None:
                getattr(form, name).data = value

    if form.validate_on_submit():
        try:
            SafariBookingService.update_booking(booking, form)
            db.session.commit()
            flash("Safari booking updated successfully.", "success")
            return redirect(url_for(
                "admin_safari_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not update safari booking.")
            flash("Unable to update the safari booking.", "danger")

    return render_template(
        "admin/bookings/safaris/edit.html", form=form, booking=booking)

@safari_bookings_bp.route("/<int:booking_id>/status", methods=["GET", "POST"])
@admin_required
def change_status(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    form = SafariBookingStatusForm()

    if request.method == "GET":
        form.status.data = booking.status

    if form.validate_on_submit():
        try:
            SafariBookingService.change_status(
                booking, form.status.data, form.internal_notes.data
            )
            db.session.commit()
            flash("Safari booking status updated.", "success")
            return redirect(url_for(
                "admin_safari_bookings.detail", booking_id=booking.id
            ))
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            current_app.logger.exception("Could not change safari status.")
            flash("Unable to update the booking status.", "danger")

    return render_template(
        "admin/bookings/safaris/status.html",
        form=form, booking=booking,)

@safari_bookings_bp.route("/<int:booking_id>/archive", methods=["POST"])
@admin_required
def archive(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    SafariBookingService.archive(booking)
    if _save_or_rollback("Safari booking archived.", "Could not archive booking."):
        return redirect(url_for("admin_safari_bookings.archived"))
    return redirect(url_for(
        "admin_safari_bookings.detail", booking_id=booking.id))


@safari_bookings_bp.route("/<int:booking_id>/restore", methods=["POST"])
@admin_required
def restore(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    if booking.status != "archived":
        flash("Only archived booking can be restored.", "warning")
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id
        ))

    SafariBookingService.restore(booking)
    if _save_or_rollback("Safari booking restored.", "Could not restore booking."):
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id
        ))
    return redirect(url_for("admin_safari_bookings.archived"))


@safari_bookings_bp.route("/<int:booking_id>/delete", methods=["POST"])
@admin_required
def delete(booking_id):
    booking = SafariBookingService.get_booking(booking_id)

    # Historical and financial records must never be silently deleted.
    protected_relations = (
        booking.payments, booking.travellers, booking.documents,
        booking.notes, booking.staff_assignments, booking.tasks, booking.reviews,
    )
    if any(protected_relations):
        flash(
            "This booking has linked history. Archive it instead of deleting it.",
            "warning",
        )
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id
        ))

    if booking.amount_paid and booking.amount_paid > 0:
        flash("A booking with payments cannot be deleted. Archive it instead.", "warning")
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id
        ))

    try:
        db.session.delete(booking)
        db.session.commit()
        flash("Safari booking deleted.", "success")
        return redirect(url_for("admin_safari_bookings.index"))
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Could not delete safari booking.")
        flash("Unable to delete this booking. Archive it instead.", "danger")
        return redirect(url_for(
            "admin_safari_bookings.detail", booking_id=booking.id))


@safari_bookings_bp.route("/<int:booking_id>/communicate", methods=["GET", "POST"])
@admin_required
def communicate(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    form = SafariBookingCommunicationForm()

    if request.method == "GET":
        form.recipient.data = booking.email

    if form.validate_on_submit():
        try:
            sent = EmailService.send_email(
                recipient=form.recipient.data.strip(),
                subject=form.subject.data.strip(),
                body=form.message.data,
                reply_to=SettingsService.get_settings().booking_email,
            )
            if not sent:
                flash("The email service did not confirm delivery.", "danger")
            else:
                flash("Message sent successfully.", "success")
            return redirect(url_for(
                "admin_safari_bookings.detail", booking_id=booking.id
            ))
        except Exception:
            current_app.logger.exception("Safari booking email failed.")
            flash("Unable to send the message. Check the email configuration.", "danger")

    return render_template(
        "admin/bookings/safaris/communication.html",
        booking=booking, form=form,)

@safari_bookings_bp.route("/<int:booking_id>/request-information", methods=["GET", "POST"])
@admin_required
def request_information(booking_id):
    booking = SafariBookingService.get_booking(booking_id)
    form = SafariBookingRequestInformationForm()

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
                flash("Email delivery was not confirmed.", "danger")
            else:
                booking.internal_notes = (
                    (booking.internal_notes or "")
                    + f"\n\nInformation requested {datetime.utcnow():%Y-%m-%d %H:%M}:\n"
                    + form.message.data
                ).strip()
                db.session.commit()
                flash("Information request sent.", "success")
            return redirect(url_for(
                "admin_safari_bookings.detail", booking_id=booking.id
            ))
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Safari information request failed.")
            flash("Unable to send the information request.", "danger")

    return render_template(
        "admin/bookings/safaris/request_information.html",
        booking=booking, form=form,)