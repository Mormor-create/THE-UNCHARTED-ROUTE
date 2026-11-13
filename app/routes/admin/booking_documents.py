"""
The Uncharted Route
Admin Booking Documents
"""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import current_user, login_required
from app.decorators.admin import admin_required
from extensions import db
from app.forms.bookings.booking_document_forms import BookingDocumentForm
from app.models import Booking, BookingDocument, BookingTraveller
from app.services.bookings import booking_document_service as document_service

booking_documents_bp = Blueprint(
    "booking_documents",
    __name__,
    url_prefix="/admin/booking-documents",)

def _populate_choices(form, selected_booking_id=None, selected_traveller_id=None):
    bookings = Booking.query.order_by(Booking.id.desc()).limit(1000).all()
    form.booking_id.choices = [
        (booking.id, f"Booking #{booking.id}")
        for booking in bookings
    ]

    travellers_query = BookingTraveller.query
    if selected_booking_id:
        travellers_query = travellers_query.filter_by(
            booking_id=selected_booking_id
        )

    travellers = travellers_query.order_by(
        BookingTraveller.booking_id.asc(),
        BookingTraveller.id.asc(),
    ).limit(2000).all()

    form.traveller_id.choices = [(0, "Booking-level document")] + [
        (traveller.id, f"{traveller.full_name} — Booking #{traveller.booking_id}")
        for traveller in travellers
    ]

    if selected_booking_id and not any(
        booking.id == selected_booking_id for booking in bookings
    ):
        form.booking_id.choices.insert(
            0, (selected_booking_id, f"Booking #{selected_booking_id}")
        )

    if selected_traveller_id and not any(
        traveller.id == selected_traveller_id for traveller in travellers
    ):
        traveller = db.session.get(BookingTraveller, selected_traveller_id)
        if traveller:
            form.traveller_id.choices.append(
                (
                    traveller.id,
                    f"{traveller.full_name} — Booking #{traveller.booking_id}",
                )
            )


def _form_data(form):
    return {
        "booking_id": form.booking_id.data,
        "traveller_id": form.traveller_id.data or None,
        "title": form.title.data,
        "document_type": form.document_type.data,
        "description": form.description.data,
        "original_filename": form.original_filename.data,
        "storage_key": form.storage_key.data,
        "mime_type": form.mime_type.data,
        "file_size_bytes": form.file_size_bytes.data,
        "checksum_sha256": form.checksum_sha256.data,
        "issuing_country": form.issuing_country.data,
        "issued_at": form.issued_at.data,
        "expires_at": form.expires_at.data,
        "status": form.status.data,
        "verification_status": form.verification_status.data,
        "verification_notes": form.verification_notes.data,
        "rejection_reason": form.rejection_reason.data,}

def _populate_form_from_document(form, document):
    form.booking_id.data = document.booking_id
    form.traveller_id.data = document.traveller_id or 0
    form.title.data = document.title
    form.document_type.data = document.document_type
    form.description.data = document.description
    form.original_filename.data = document.original_filename
    form.storage_key.data = document.storage_key
    form.mime_type.data = document.mime_type
    form.file_size_bytes.data = document.file_size_bytes
    form.checksum_sha256.data = document.checksum_sha256
    form.issuing_country.data = document.issuing_country
    form.issued_at.data = document.issued_at
    form.expires_at.data = document.expires_at
    form.status.data = document.status
    form.verification_status.data = document.verification_status
    form.verification_notes.data = document.verification_notes
    form.rejection_reason.data = document.rejection_reason


@booking_documents_bp.route("/")
@login_required
@admin_required
def index():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    verification_status = request.args.get("verification_status", "").strip()
    document_type = request.args.get("document_type", "").strip()
    booking_id_raw = request.args.get("booking_id", "").strip()

    try:
        booking_id = int(booking_id_raw) if booking_id_raw else None
    except ValueError:
        booking_id = None

    documents = document_service.get_all_booking_documents(
        booking_id=booking_id,
        status=status or None,
        document_type=document_type or None,
        verification_status=verification_status or None,
        search=search or None,
    )

    return render_template(
        "admin/bookings/booking_documents/index.html",
        documents=documents,
        search=search,
        status=status,
        verification_status=verification_status,
        document_type=document_type,
        booking_id=booking_id_raw,)

@booking_documents_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = BookingDocumentForm()
    selected_booking_id = request.args.get("booking_id", type=int)
    _populate_choices(form, selected_booking_id=selected_booking_id)

    if selected_booking_id and request.method == "GET":
        form.booking_id.data = selected_booking_id

    if form.validate_on_submit():
        data = _form_data(form)
        if data["traveller_id"] == 0:
            data["traveller_id"] = None

        try:
            document = document_service.create_booking_document(
                **data,
                uploaded_by_user_id=current_user.id,
            )
            flash("Booking document record created.", "success")
            return redirect(
                url_for("booking_documents.detail", document_id=document.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")

    return render_template(
        "admin/bookings/booking_documents/create.html",
        form=form,)

@booking_documents_bp.route("/<int:document_id>")
@login_required
@admin_required
def detail(document_id):
    document = document_service.get_booking_document(document_id)
    if document is None:
        abort(404)

    return render_template(
        "admin/bookings/booking_documents/detail.html",
        document=document,)

@booking_documents_bp.route("/<int:document_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(document_id):
    document = document_service.get_booking_document(document_id)
    if document is None:
        abort(404)

    form = BookingDocumentForm()
    _populate_choices(
        form,
        selected_booking_id=document.booking_id,
        selected_traveller_id=document.traveller_id,
    )

    if request.method == "GET":
        _populate_form_from_document(form, document)
    else:
        # Keep the immutable private storage key available for validation.
        form.storage_key.data = document.storage_key

    if form.validate_on_submit():
        data = _form_data(form)
        if data["traveller_id"] == 0:
            data["traveller_id"] = None

        # The private storage key is immutable from the edit screen.
        data.pop("storage_key", None)

        try:
            document_service.update_booking_document(
                document_id,
                **data,
            )
            flash("Booking document updated.", "success")
            return redirect(
                url_for("booking_documents.detail", document_id=document_id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")

    return render_template(
        "admin/bookings/booking_documents/edit.html",
        form=form,
        document=document,)

@booking_documents_bp.route("/<int:document_id>/verify",methods=["POST"],)
@login_required
@admin_required
def verify(document_id):
    document = document_service.get_booking_document(document_id)
    if document is None:
        abort(404)

    try:
        document_service.verify_booking_document(
            document_id,
            verified_by_user_id=current_user.id,
            notes=request.form.get("verification_notes"),
        )
        flash("Document marked as verified.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for("booking_documents.detail", document_id=document_id))

@booking_documents_bp.route("/<int:document_id>/reject",methods=["POST"],)
@login_required
@admin_required
def reject(document_id):
    document = document_service.get_booking_document(document_id)
    if document is None:
        abort(404)

    try:
        document_service.reject_booking_document(
            document_id,
            verified_by_user_id=current_user.id,
            reason=request.form.get("rejection_reason", ""),
        )
        flash("Document rejected.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for("booking_documents.detail", document_id=document_id))

@booking_documents_bp.route("/<int:document_id>/toggle",methods=["POST"],)
@login_required
@admin_required
def toggle(document_id):
    document = document_service.get_booking_document(document_id)
    if document is None:
        abort(404)

    try:
        if document.status == "archived":
            document_service.reactivate_booking_document(document_id)
            flash("Document record reactivated.", "success")
        else:
            document_service.deactivate_booking_document(document_id)
            flash("Document record archived.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for("booking_documents.detail", document_id=document_id))