
"""Admin CMS routes for central booking notes."""

from datetime import datetime

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required

from app.decorators.admin import admin_required
from extensions import db
from app.forms.bookings.booking_note_forms import BookingNoteForm
from app.models import Booking, BookingNote
from app.services.bookings.booking_note_service import (
    create_booking_note,
    delete_booking_note,
    get_all_booking_notes,
    get_booking_note,
    update_booking_note,
)

booking_notes_bp = Blueprint(
    "admin_booking_notes",
    __name__,
    url_prefix="/admin/booking-notes",
)


def _booking_choices():
    bookings = Booking.query.order_by(Booking.id.desc()).limit(500).all()
    return [
        (booking.id, f"Booking #{booking.id}")
        for booking in bookings
    ]


def _populate_form(form):
    form.booking_id.choices = _booking_choices()


def _author_snapshot():
    user = current_user
    name = (
        getattr(user, "full_name", None)
        or getattr(user, "name", None)
        or getattr(user, "email", None)
        or "Admin"
    )
    role = getattr(user, "role", None)
    if role is not None and not isinstance(role, str):
        role = getattr(role, "name", str(role))
    return str(name)[:200], (str(role)[:100] if role else None)


@booking_notes_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    search = request.args.get("q", "").strip()
    visibility = request.args.get("visibility", "").strip() or None
    note_type = request.args.get("note_type", "").strip() or None
    delivery_status = request.args.get("delivery_status", "").strip() or None

    try:
        notes = get_all_booking_notes(
            visibility=visibility,
            note_type=note_type,
            delivery_status=delivery_status,
            search=search,
            limit=500,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        notes = get_all_booking_notes(limit=500)

    return render_template(
        "admin/booking/booking_notes/index.html",
        notes=notes,
        search=search,
        visibility=visibility or "",
        note_type=note_type or "",
        delivery_status=delivery_status or "",)

@booking_notes_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = BookingNoteForm()
    _populate_form(form)

    if form.validate_on_submit():
        author_name, author_role = _author_snapshot()
        try:
            note = create_booking_note(
                booking_id=form.booking_id.data,
                title=form.title.data,
                content=form.content.data,
                note_type=form.note_type.data,
                visibility=form.visibility.data,
                communication_channel=form.communication_channel.data or None,
                direction=form.direction.data or None,
                recipient=form.recipient.data,
                subject=form.subject.data,
                external_reference=form.external_reference.data,
                author_user_id=current_user.id,
                author_name_snapshot=form.author_name_snapshot.data or author_name,
                author_role_snapshot=form.author_role_snapshot.data or author_role,
                delivery_status=form.delivery_status.data or None,
                delivery_error=form.delivery_error.data,
            )
            flash("Booking note created successfully.", "success")
            return redirect(url_for("admin_booking_notes.detail", note_id=note.id))
        except ValueError as exc:
            flash(str(exc), "error")

    return render_template("admin/booking/booking_notes/create.html", form=form)


@booking_notes_bp.route("/<int:note_id>")
@login_required
@admin_required
def detail(note_id):
    note = get_booking_note(note_id)
    if note is None:
        abort(404)
    return render_template("admin/booking/booking_notes/detail.html", note=note)


@booking_notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(note_id):
    note = get_booking_note(note_id)
    if note is None:
        abort(404)

    form = BookingNoteForm(obj=note)
    _populate_form(form)

    if request.method == "GET":
        form.booking_id.data = note.booking_id
        form.communication_channel.data = note.communication_channel or ""
        form.direction.data = note.direction or ""
        form.delivery_status.data = note.delivery_status or ""

    if form.validate_on_submit():
        try:
            # Booking ownership and original creation time are not editable here.
            note.title = (form.title.data or "").strip() or None
            note.content = form.content.data.strip()
            note.note_type = form.note_type.data
            note.visibility = form.visibility.data
            note.communication_channel = form.communication_channel.data or None
            note.direction = form.direction.data or None
            note.recipient = (form.recipient.data or "").strip() or None
            note.subject = (form.subject.data or "").strip() or None
            note.external_reference = (
                (form.external_reference.data or "").strip() or None
            )
            note.delivery_status = form.delivery_status.data or None
            note.delivery_error = (form.delivery_error.data or "").strip() or None
            note.author_name_snapshot = (
                (form.author_name_snapshot.data or "").strip() or None
            )
            note.author_role_snapshot = (
                (form.author_role_snapshot.data or "").strip() or None
            )

            if note.visibility == "internal" and note.delivery_status in {
                "sent", "delivered"
            }:
                raise ValueError(
                    "A note marked sent or delivered cannot be internal-only."
                )

            if note.delivery_status == "delivered" and note.delivered_at is None:
                note.delivered_at = datetime.utcnow()
            elif note.delivery_status not in {"delivered"}:
                note.delivered_at = None

            db.session.commit()
            flash("Booking note updated successfully.", "success")
            return redirect(url_for("admin_booking_notes.detail", note_id=note.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")

    return render_template("admin/booking/booking_notes/edit.html", form=form, note=note)


@booking_notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(note_id):
    note = get_booking_note(note_id)
    if note is None:
        abort(404)

    try:
        delete_booking_note(note_id)
        flash("Booking note deleted.", "success")
    except ValueError as exc:
        flash(str(exc), "error")

    return redirect(url_for("admin_booking_notes.index"))