# =============================================================================
# The Uncharted Route
# Admin Booking Add-on Routes
# =============================================================================

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.decorators.admin import admin_required
from app.forms.bookings.booking_addon_forms import (
    BookingAddonForm,
    BookingAddonStatusForm,)
from app.services.bookings.booking_addon_service import BookingAddonService

booking_addons_bp = Blueprint(
    "admin_booking_addons",
    __name__,
    url_prefix="/admin/booking-addons",)

def _commit():
    try:
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to save booking add-on.")
        flash("The add-on could not be saved. Please try again.", "error")
        return False

def _prepare_form(form):
    BookingAddonService.populate_form_choices(form)


def _load_form(form, addon):
    values = {
        "addon_code": addon.addon_code,
        "addon_type": addon.addon_type,
        "experience_addon_id": addon.experience_addon_id or 0,
        "name_snapshot": addon.name_snapshot,
        "description_snapshot": addon.description_snapshot,
        "pricing_basis": addon.pricing_basis,
        "quantity": addon.quantity,
        "unit_price": addon.unit_price,
        "currency": addon.currency,
        "discount_amount": addon.discount_amount,
        "tax_amount": addon.tax_amount,
        "status": addon.status,
        "cancellation_reason": addon.cancellation_reason,
        "internal_notes": addon.internal_notes,
    }

    for name, value in values.items():
        getattr(form, name).data = value


@booking_addons_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    addons = BookingAddonService.list_addons(
        search=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
        booking_id=request.args.get("booking_id", type=int),
    )

    return render_template(
        "admin/booking/addons/index.html",
        addons=addons,
        search=request.args.get("q", ""),
        selected_status=request.args.get("status", ""),
        booking_id=request.args.get("booking_id", type=int),
    )


@booking_addons_bp.route("/booking/<int:booking_id>/create", methods=["GET", "POST"])
@login_required
@admin_required
def create(booking_id):
    booking = BookingAddonService.get_booking(booking_id)
    if booking is None:
        flash("Booking not found.", "error")
        return redirect(url_for("admin_booking_addons.index"))

    form = BookingAddonForm()
    _prepare_form(form)

    if form.validate_on_submit():
        try:
            addon = BookingAddonService.create_addon(
                booking_id,
                form,
                added_by_user=current_user,
            )
            BookingAddonService.sync_booking_addon_total(booking)
            db.session.commit()

            flash("Booking add-on added successfully.", "success")
            return redirect(
                url_for(
                    "admin_booking_addons.detail",
                    addon_id=addon.id,
                )
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to create booking add-on.")
            flash("The add-on could not be created.", "error")

    return render_template(
        "admin/booking/addons/create.html",
        form=form,
        booking=booking,
    )


@booking_addons_bp.route("/<int:addon_id>", methods=["GET"])
@login_required
@admin_required
def detail(addon_id):
    addon = BookingAddonService.get_addon(addon_id)
    if addon is None:
        flash("Booking add-on not found.", "error")
        return redirect(url_for("admin_booking_addons.index"))

    return render_template(
        "admin/booking/addons/detail.html",
        addon=addon,
    )


@booking_addons_bp.route("/<int:addon_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(addon_id):
    addon = BookingAddonService.get_addon(addon_id)
    if addon is None:
        flash("Booking add-on not found.", "error")
        return redirect(url_for("admin_booking_addons.index"))

    form = BookingAddonForm()
    _prepare_form(form)

    if request.method == "GET":
        _load_form(form, addon)

    if form.validate_on_submit():
        try:
            BookingAddonService.update_addon(addon, form)
            BookingAddonService.sync_booking_addon_total(addon.booking)
            db.session.commit()

            flash("Booking add-on updated successfully.", "success")
            return redirect(
                url_for("admin_booking_addons.detail", addon_id=addon.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update booking add-on.")
            flash("The add-on could not be updated.", "error")

    return render_template(
        "admin/booking/addons/edit.html",
        form=form,
        addon=addon,
    )


@booking_addons_bp.route("/<int:addon_id>/status", methods=["GET", "POST"])
@login_required
@admin_required
def change_status(addon_id):
    addon = BookingAddonService.get_addon(addon_id)
    if addon is None:
        flash("Booking add-on not found.", "error")
        return redirect(url_for("admin_booking_addons.index"))

    form = BookingAddonStatusForm()

    if request.method == "GET":
        form.status.data = addon.status
        form.cancellation_reason.data = addon.cancellation_reason
        form.internal_notes.data = ""

    if form.validate_on_submit():
        try:
            BookingAddonService.change_status(
                addon,
                form.status.data,
                cancellation_reason=form.cancellation_reason.data,
                internal_notes=form.internal_notes.data,
            )
            BookingAddonService.sync_booking_addon_total(addon.booking)
            db.session.commit()

            flash("Add-on status updated.", "success")
            return redirect(
                url_for("admin_booking_addons.detail", addon_id=addon.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update add-on status.")
            flash("The add-on status could not be updated.", "error")

    return render_template(
        "admin/booking/addons/status.html",
        form=form,
        addon=addon,
    )


@booking_addons_bp.route("/<int:addon_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(addon_id):
    addon = BookingAddonService.get_addon(addon_id)
    if addon is None:
        flash("Booking add-on not found.", "error")
        return redirect(url_for("admin_booking_addons.index"))

    if addon.status in {"confirmed", "fulfilled", "cancelled"}:
        flash(
            "This add-on has operational history. Change its status or retain it for audit purposes.",
            "error",
        )
        return redirect(
            url_for("admin_booking_addons.detail", addon_id=addon.id)
        )

    booking = addon.booking
    db.session.delete(addon)
    db.session.flush()
    BookingAddonService.sync_booking_addon_total(booking)

    if _commit():
        flash("Booking add-on removed.", "success")

    return redirect(
        url_for(
            "admin_booking_addons.index",
            booking_id=booking.id,
        )
    )