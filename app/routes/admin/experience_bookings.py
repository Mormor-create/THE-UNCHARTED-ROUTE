"""
The Uncharted Route
Experience Booking Administration Routes
"""

from datetime import datetime
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import current_user
from sqlalchemy import or_
from extensions import db
from app.decorators.admin import admin_required
from app.models.booking import Booking
from app.models.booking_request import BookingRequest
from app.models.experience import Experience
from app.models.experience_pricing import ExperiencePricing
from app.models.user import User
from app.forms.bookings.experience_booking_forms import (
    ExperienceBookingFilterForm,
    ExperienceBookingForm,
    ExperienceBookingAssignmentForm,
    ExperienceBookingStatusForm,
    ExperienceBookingArchiveForm,
    ExperienceBookingDeleteForm,
    ExperienceBookingCommunicationForm,
    ExperienceBookingInformationForm,)
from app.services.bookings.experience_booking_service import (
    ExperienceBookingService,
)

experience_bookings_bp = Blueprint(
    "admin_experience_bookings",
    __name__,
    url_prefix="/admin/booking/experiences",
)

def _populate_booking_choices(form, booking=None):
    """Populate experience and pricing options for the form."""

    experiences = ExperienceBookingService.get_catalogue_choices()

    form.experience_id.choices = [
        (
            experience.id,
            (
                getattr(experience, "title", None)
                or getattr(experience, "name", None)
                or f"Experience #{experience.id}"
            ),
        )
        for experience in experiences
    ]

    selected_experience_id = (
        request.form.get("experience_id", type=int)
        or getattr(
            getattr(booking, "experience_booking", None),
            "experience_id",
            None,
        )
        or (experiences[0].id if experiences else None)
    )

    pricing_options = []

    if selected_experience_id:
        pricing_options = ExperiencePricing.query.filter_by(
            experience_id=selected_experience_id
        ).all()

    form.pricing_id.choices = [
        ("", "No pricing option selected")
    ] + [
        (
            pricing.id,
            (
                getattr(pricing, "name", None)
                or getattr(pricing, "title", None)
                or f"Pricing #{pricing.id}"
            ),
        )
        for pricing in pricing_options
    ]

    if not experiences:
        form.experience_id.choices = [
            ("", "No active experiences available")
        ]

def _populate_assignment_choices(form):
    """Use existing user records; only expose accounts that look staff/admin."""
    choices = []
    for user in User.query.order_by(User.id.asc()).all():
        role = str(
            getattr(user, "role", "")
            or getattr(user, "user_type", "")
            or ""
        ).lower()
        is_active = getattr(user, "is_active", True)

        if not is_active:
            continue

        if role and not any(
            token in role for token in ("admin", "staff", "manager", "operations")
        ):
            continue

        label = (
            getattr(user, "full_name", None)
            or " ".join(
                part for part in (
                    getattr(user, "first_name", ""),
                    getattr(user, "last_name", ""),
                ) if part
            ).strip()
            or getattr(user, "email", None)
            or f"User #{user.id}"
        )
        choices.append((user.id, label))

    form.staff_id.choices = choices or [(0, "No staff accounts available")]


def _safe_rollback(message):
    db.session.rollback()
    current_app.logger.exception(message)


@experience_bookings_bp.route("/", methods=["GET"], endpoint="index")
@admin_required
def index():
    data = ExperienceBookingService.get_index_data(request.args)
    form = ExperienceBookingFilterForm()

    return render_template(
        "admin/bookings/experiences/index.html",
        bookings=data["booking"],
        stats=data["stats"],
        filters=data["filters"],
        form=form,
    )


@experience_bookings_bp.route("/archived", methods=["GET"], endpoint="archived")
@admin_required
def archived():
    bookings = ExperienceBookingService.get_archived()
    return render_template(
        "admin/bookings/experiences/archived.html",
        bookings=bookings,
    )


@experience_bookings_bp.route("/create", methods=["GET", "POST"], endpoint="create")
@admin_required
def create():
    form = ExperienceBookingForm()
    _populate_booking_choices(form)

    if not form.experience_id.choices:
        flash("Create an active experience before creating a booking.", "warning")
        return render_template(
            "admin/bookings/experiences/create.html",
            form=form,
        )

    if form.validate_on_submit():
        try:
            booking = ExperienceBookingService.create_booking(
                form,
                creator_id=current_user.id,
            )
            flash(
                f"Experience booking {booking.booking_reference} created successfully.",
                "success",
            )
            return redirect(
                url_for(
                    "admin_experience_bookings.detail",
                    booking_id=booking.id,
                )
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "warning")
        except Exception:
            _safe_rollback("Failed to create experience booking.")
            flash("The booking could not be created. Please try again.", "danger")

    return render_template("admin/bookings/experiences/create.html", form=form)


@experience_bookings_bp.route(
    "/<int:booking_id>",
    methods=["GET"],
    endpoint="detail",
)
@admin_required
def detail(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    status_form = ExperienceBookingStatusForm()
    status_form.status.data = booking.status

    return render_template(
        "admin/bookings/experiences/detail.html",
        booking=booking,
        status_form=status_form,
        assigned=ExperienceBookingService.is_assigned(booking),
        getattr=getattr,
    )

@experience_bookings_bp.route(
    "/<int:booking_id>/edit",
    methods=["GET", "POST"],
    endpoint="edit",
)
@admin_required
def edit(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingForm(obj=booking)

    if request.method == "GET" and booking.experience_booking:
        detail = booking.experience_booking
        form.experience_id.data = detail.experience_id
        form.pricing_id.data = detail.pricing_id
        form.price_basis.data = detail.price_basis
        form.unit_price.data = detail.unit_price
        form.quantity.data = detail.quantity
        form.pickup_location.data = detail.pickup_location
        form.dropoff_location.data = detail.dropoff_location
        form.customer_instructions.data = detail.customer_instructions
        form.currency.data = detail.currency

    _populate_booking_choices(form, booking)

    if form.validate_on_submit():
        try:
            ExperienceBookingService.update_booking(booking, form)
            flash("Experience booking updated successfully.", "success")
            return redirect(
                url_for("admin_experience_bookings.detail", booking_id=booking.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "warning")
        except Exception:
            _safe_rollback("Failed to update experience booking.")
            flash("The booking could not be updated.", "danger")

    return render_template(
        "admin/bookings/experiences/edit.html",
        form=form,
        booking=booking,
    )


@experience_bookings_bp.route(
    "/<int:booking_id>/assign",
    methods=["GET", "POST"],
    endpoint="assign",
)
@admin_required
def assign(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingAssignmentForm()
    _populate_assignment_choices(form)

    if form.validate_on_submit():
        try:
            if form.staff_id.data == 0:
                raise ValueError("No eligible staff account is available.")

            # Discover the assignment class through the central relationship,
            # avoiding a second, competing booking-assignment implementation.
            relationship = Booking.staff_assignments.property
            assignment_model = relationship.mapper.class_
            assignment = assignment_model()

            available_columns = {
                column.key for column in assignment_model.__table__.columns
            }
            values = {
                "booking_id": booking.id,
                "staff_id": form.staff_id.data,
                "user_id": form.staff_id.data,
                "assigned_by_user_id": current_user.id,
                "assigned_by_id": current_user.id,
                "role": form.role.data,
                "assignment_role": form.role.data,
                "notes": form.notes.data,
                "status": "active",
                "active": True,
                "created_at": datetime.utcnow(),
            }

            for field, value in values.items():
                if field in available_columns:
                    setattr(assignment, field, value)

            if "booking_id" not in available_columns:
                raise ValueError(
                    "The StaffAssignment model has no booking_id column."
                )
            if not ({"staff_id", "user_id"} & available_columns):
                raise ValueError(
                    "The StaffAssignment model has no staff/user reference column."
                )

            db.session.add(assignment)
            db.session.commit()
            flash("Staff assignment saved successfully.", "success")
            return redirect(
                url_for("admin_experience_bookings.detail", booking_id=booking.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "warning")
        except Exception:
            _safe_rollback("Failed to assign experience booking.")
            flash("The staff assignment could not be saved.", "danger")

    return render_template(
        "admin/bookings/experiences/assign.html",
        booking=booking,
        form=form,
    )


@experience_bookings_bp.route(
    "/<int:booking_id>/status",
    methods=["POST"],
    endpoint="change_status",)
@admin_required
def change_status(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingStatusForm()

    if form.validate_on_submit():
        try:
            ExperienceBookingService.change_status(
                booking,
                form.status.data,
                form.cancellation_reason.data,
            )
            flash("Booking status updated.", "success")
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "warning")
        except Exception:
            _safe_rollback("Failed to change experience booking status.")
            flash("Booking status could not be updated.", "danger")
    else:
        flash("Choose a valid booking status.", "warning")

    return redirect(
        url_for("admin_experience_bookings.detail", booking_id=booking.id))

@experience_bookings_bp.route("/<int:booking_id>/archive",methods=["GET", "POST"],endpoint="archive",)
@admin_required
def archive(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingArchiveForm()

    if form.validate_on_submit():
        try:
            ExperienceBookingService.archive(booking, form.reason.data)
            flash("Booking archived. Its history has been retained.", "success")
            return redirect(url_for("admin_experience_bookings.archived"))
        except Exception:
            _safe_rollback("Failed to archive experience booking.")
            flash("The booking could not be archived.", "danger")

    return render_template(
        "admin/bookings/experiences/archive.html",
        booking=booking,
        form=form,
    )


@experience_bookings_bp.route(
    "/<int:booking_id>/restore",
    methods=["POST"],
    endpoint="restore",
)
@admin_required
def restore(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id, archived=True)

    try:
        ExperienceBookingService.restore(booking)
        flash("Booking restored successfully.", "success")
    except Exception:
        _safe_rollback("Failed to restore experience booking.")
        flash("The booking could not be restored.", "danger")

    return redirect(
        url_for("admin_experience_bookings.detail", booking_id=booking.id)
    )


@experience_bookings_bp.route(
    "/<int:booking_id>/delete",
    methods=["GET", "POST"],
    endpoint="delete",
)
@admin_required
def delete(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id, archived=True)
    form = ExperienceBookingDeleteForm()

    if form.validate_on_submit():
        try:
            reference = booking.booking_reference
            ExperienceBookingService.safe_delete(booking)
            flash(f"Archived booking {reference} deleted.", "success")
            return redirect(url_for("admin_experience_bookings.archived"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "warning")
        except Exception:
            _safe_rollback("Failed to delete archived experience booking.")
            flash("The booking could not be deleted.", "danger")

    return render_template(
        "admin/bookings/experiences/delete.html",
        booking=booking,
        form=form,)

def _send_booking_email(booking, subject, message):
    """Send using the existing EmailService and configured booking recipient."""
    from app.services.email_service import EmailService
    from app.services.settings_service import SettingsService

    settings = SettingsService.get_settings()
    booking_email = getattr(settings, "booking_email", None)

    # Keep the existing service's configured sender/reply-to behavior.
    customer_sent = EmailService.send_email(
        recipient=booking.email,
        subject=subject,
        body=message,
        reply_to=booking_email or None,
    )

    # Notify the configured booking inbox that a customer communication was sent.
    if booking_email:
        EmailService.send_email(
            recipient=booking_email,
            subject=f"[TUR Booking {booking.booking_reference}] {subject}",
            body=(
                f"An email was sent to {booking.email} regarding booking "
                f"{booking.booking_reference}.\n\n{message}"
            ),
        )

    return bool(customer_sent)


@experience_bookings_bp.route(
    "/<int:booking_id>/communicate",
    methods=["GET", "POST"],
    endpoint="communicate",
)
@admin_required
def communicate(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingCommunicationForm()

    if form.validate_on_submit():
        try:
            sent = _send_booking_email(
                booking,
                form.subject.data.strip(),
                form.message.data.strip(),
            )
            if not sent:
                flash(
                    "The email service could not confirm delivery. "
                    "Please check the email configuration and logs.",
                    "warning",
                )
            else:
                booking.internal_notes = "\n\n".join(
                    part for part in (
                        booking.internal_notes,
                        (
                            f"[{datetime.utcnow():%Y-%m-%d %H:%M}] "
                            f"Email sent to {booking.email}: "
                            f"{form.subject.data.strip()}\n"
                            f"{form.message.data.strip()}"
                        ),
                    ) if part
                )
                db.session.commit()
                flash("Customer email sent and recorded in booking notes.", "success")

            return redirect(
                url_for("admin_experience_bookings.detail", booking_id=booking.id)
            )
        except Exception:
            _safe_rollback("Failed to send experience booking email.")
            flash("The customer email could not be sent.", "danger")

    return render_template(
        "admin/bookings/experiences/communication.html",
        booking=booking,
        form=form,
    )


@experience_bookings_bp.route(
    "/<int:booking_id>/request-information",
    methods=["GET", "POST"],
    endpoint="request_information",
)
@admin_required
def request_information(booking_id):
    booking = ExperienceBookingService.get_booking(booking_id)
    form = ExperienceBookingInformationForm()

    if form.validate_on_submit():
        try:
            subject = f"Additional information needed — {booking.booking_reference}"
            message = form.message.data.strip()
            sent = _send_booking_email(booking, subject, message)

            if not sent:
                flash("The information request email could not be confirmed.", "warning")
            else:
                booking.reviewed = True
                booking.internal_notes = "\n\n".join(
                    part for part in (
                        booking.internal_notes,
                        (
                            f"[{datetime.utcnow():%Y-%m-%d %H:%M}] "
                            f"Information requested from {booking.email}:\n{message}"
                        ),
                    ) if part
                )
                db.session.commit()
                flash("Information request sent and recorded.", "success")

            return redirect(
                url_for("admin_experience_bookings.detail", booking_id=booking.id)
            )
        except Exception:
            _safe_rollback("Failed to request booking information.")
            flash("The information request could not be sent.", "danger")

    return render_template(
        "admin/bookings/experiences/request_information.html",
        booking=booking,
        form=form,
    )


@experience_bookings_bp.route("/requests/<int:request_id>/convert",methods=["POST"],endpoint="convert_request",)
@admin_required
def convert_request(request_id):
    try:
        booking = ExperienceBookingService.convert_request(
            request_id,
            creator_id=current_user.id,
        )
        flash(
            f"Approved request converted to booking {booking.booking_reference}.",
            "success",
        )
        return redirect(
            url_for("admin_experience_bookings.detail", booking_id=booking.id)
        )
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "warning")
    except Exception:
        _safe_rollback("Failed to convert experience booking request.")
        flash("The request could not be converted.", "danger")

    return redirect(url_for("admin_experience_bookings.index"))