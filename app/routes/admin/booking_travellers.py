"""
===============================================================================
The Uncharted Route
Admin Booking Traveller Routes
===============================================================================
"""

from datetime import datetime
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import login_required
from sqlalchemy import or_
from app.decorators.admin import admin_required
from extensions import db
from app.forms.bookings.booking_traveller_forms import BookingTravellerForm
from app.models import Booking, BookingTraveller

booking_travellers_bp = Blueprint(
    "admin_booking_travellers",
    __name__,
    url_prefix="/admin/booking-travellers",)

def _populate_booking_choices(form):
    """Populate the booking selector with central booking."""
    bookings = Booking.query.order_by(Booking.id.desc()).limit(500).all()

    form.booking_id.choices = [
        (
            booking.id,
            f"Booking #{booking.id}"
            + (
                f" — {getattr(booking, 'booking_reference', '')}"
                if getattr(booking, "booking_reference", None)
                else ""
            ),
        )
        for booking in bookings
    ]


def _get_traveller_or_404(traveller_id):
    traveller = db.session.get(BookingTraveller, traveller_id)

    if traveller is None:
        abort(404)

    return traveller


@booking_travellers_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    """List and search booking travellers."""
    query = BookingTraveller.query

    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    booking_id = request.args.get("booking_id", type=int)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                BookingTraveller.first_name.ilike(term),
                BookingTraveller.middle_name.ilike(term),
                BookingTraveller.last_name.ilike(term),
                BookingTraveller.email.ilike(term),
                BookingTraveller.phone.ilike(term),
                BookingTraveller.traveller_reference.ilike(term),
            )
        )

    if status in {"active", "inactive"}:
        query = query.filter(BookingTraveller.status == status)

    if booking_id:
        query = query.filter(
            BookingTraveller.booking_id == booking_id
        )

    travellers = query.order_by(
        BookingTraveller.created_at.desc()
    ).all()

    bookings = Booking.query.order_by(Booking.id.desc()).limit(500).all()

    return render_template(
        "admin/bookings/booking_travellers/index.html",
        travellers=travellers,
        bookings=bookings,
        search=search,
        selected_status=status,
        selected_booking_id=booking_id,
    )


@booking_travellers_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    """Create a traveller for a central booking."""
    form = BookingTravellerForm()
    _populate_booking_choices(form)

    if not form.booking_id.choices:
        flash(
            "Create a central booking before adding travellers.",
            "warning",
        )
        return redirect(url_for("admin_booking_travellers.index"))

    if form.validate_on_submit():
        booking = db.session.get(Booking, form.booking_id.data)

        if booking is None:
            form.booking_id.errors.append("The selected booking does not exist.")
        else:
            traveller = BookingTraveller(
                booking_id=booking.id,
                traveller_reference=form.traveller_reference.data or None,
                traveller_number=form.traveller_number.data,
                first_name=form.first_name.data.strip(),
                middle_name=(form.middle_name.data or "").strip() or None,
                last_name=form.last_name.data.strip(),
                date_of_birth=form.date_of_birth.data,
                traveller_type=form.traveller_type.data,
                nationality=form.nationality.data or None,
                country_of_residence=form.country_of_residence.data or None,
                email=form.email.data or None,
                phone=form.phone.data or None,
                emergency_contact_name=form.emergency_contact_name.data or None,
                emergency_contact_relationship=(
                    form.emergency_contact_relationship.data or None
                ),
                emergency_contact_phone=form.emergency_contact_phone.data or None,
                emergency_contact_email=form.emergency_contact_email.data or None,
                dietary_requirements=form.dietary_requirements.data or None,
                accessibility_requirements=(
                    form.accessibility_requirements.data or None
                ),
                medical_information=form.medical_information.data or None,
                special_requirements=form.special_requirements.data or None,
                waiver_required=bool(form.waiver_required.data),
                waiver_status=form.waiver_status.data,
                status=form.status.data,
                notes=form.notes.data or None,
            )

            db.session.add(traveller)
            db.session.commit()

            flash("Traveller added successfully.", "success")
            return redirect(
                url_for(
                    "admin_booking_travellers.detail",
                    traveller_id=traveller.id,
                )
            )

    return render_template(
        "admin/bookings/booking_travellers/create.html",
        form=form,
    )


@booking_travellers_bp.route("/<int:traveller_id>")
@login_required
@admin_required
def detail(traveller_id):
    """View a traveller record."""
    traveller = _get_traveller_or_404(traveller_id)

    return render_template(
        "admin/bookings/booking_travellers/detail.html",
        traveller=traveller,)

@booking_travellers_bp.route("/<int:traveller_id>/edit",methods=["GET", "POST"],)
@login_required
@admin_required
def edit(traveller_id):
    """Edit an existing traveller record."""
    traveller = _get_traveller_or_404(traveller_id)

    form = BookingTravellerForm(obj=traveller)
    _populate_booking_choices(form)

    if form.validate_on_submit():
        booking = db.session.get(Booking, form.booking_id.data)

        if booking is None:
            form.booking_id.errors.append("The selected booking does not exist.")
        else:
            traveller.booking_id = booking.id

            fields = [
                "traveller_reference",
                "traveller_number",
                "first_name",
                "middle_name",
                "last_name",
                "date_of_birth",
                "traveller_type",
                "nationality",
                "country_of_residence",
                "email",
                "phone",
                "emergency_contact_name",
                "emergency_contact_relationship",
                "emergency_contact_phone",
                "emergency_contact_email",
                "dietary_requirements",
                "accessibility_requirements",
                "medical_information",
                "special_requirements",
                "waiver_required",
                "waiver_status",
                "status",
                "notes",
            ]

            for field in fields:
                value = getattr(form, field).data

                if field in {"first_name", "last_name"}:
                    value = value.strip()

                elif field == "middle_name":
                    value = (value or "").strip() or None

                elif isinstance(value, str) and not value.strip():
                    value = None

                setattr(traveller, field, value)

            traveller.updated_at = datetime.utcnow()
            db.session.commit()

            flash("Traveller updated successfully.", "success")
            return redirect(
                url_for(
                    "admin_booking_travellers.detail",
                    traveller_id=traveller.id,
                )
            )

    return render_template(
        "admin/bookings/booking_travellers/edit.html",
        form=form,
        traveller=traveller,)

@booking_travellers_bp.route("/<int:traveller_id>/toggle",methods=["POST"],)
@login_required
@admin_required
def toggle(traveller_id):
    """Activate or deactivate a traveller without deleting history."""
    traveller = _get_traveller_or_404(traveller_id)

    traveller.status = (
        "inactive" if traveller.status == "active" else "active")
    traveller.updated_at = datetime.utcnow()

    db.session.commit()

    flash(
        "Traveller record "
        + ("deactivated." if traveller.status == "inactive" else "reactivated."),
        "success",)

    return redirect(
        request.referrer
        or url_for("admin_booking_travellers.index"))