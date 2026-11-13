"""
===============================================================================
The Uncharted Route
Admin Booking Payments
===============================================================================
"""
from decimal import Decimal
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from app.decorators.admin import admin_required
from app.models import Booking, BookingPayment
from app.forms.bookings.booking_payment_forms import (
    BookingPaymentForm,
    BookingPaymentFilterForm,
    BookingRefundForm,)
from app.services.bookings.booking_payment_service import (
    create_booking_payment,
    record_refund,
    get_booking_payment,
    get_booking_payment_summary,
    get_booking_payments,
    update_payment_status,)

booking_payments_bp = Blueprint(
    "booking_payments",
    __name__,
    url_prefix="/admin/booking-payments",
)


def _populate_booking_choices(form, include_all=False):
    choices = [
        (
            booking.id,
            f"Booking #{booking.id} — "
            f"{getattr(booking, 'booking_reference', None) or 'No reference'}",
        )
        for booking in Booking.query.order_by(Booking.id.desc()).limit(1000).all()
    ]

    if include_all:
        form.booking_id.choices = [(0, "All booking")] + choices
    else:
        form.booking_id.choices = choices


def _get_payment_or_404(payment_id):
    payment = get_booking_payment(payment_id)
    if payment is None:
        abort(404)
    return payment


@booking_payments_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    form = BookingPaymentFilterForm(request.args)
    _populate_booking_choices(form, include_all=True)

    query = BookingPayment.query

    booking_id = request.args.get("booking_id", type=int)
    transaction_type = request.args.get("transaction_type", "").strip().lower()
    status = request.args.get("status", "").strip().lower()
    search = request.args.get("q", "").strip()

    if booking_id:
        query = query.filter_by(booking_id=booking_id)

    if transaction_type in {"payment", "refund", "adjustment"}:
        query = query.filter_by(transaction_type=transaction_type)

    if status in {"pending", "processing", "succeeded", "failed", "cancelled"}:
        query = query.filter_by(status=status)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                BookingPayment.transaction_reference.ilike(term),
                BookingPayment.provider_reference.ilike(term),
                BookingPayment.provider_transaction_id.ilike(term),
                BookingPayment.receipt_number.ilike(term),
            )
        )

    payments = query.order_by(
        BookingPayment.initiated_at.desc(),
        BookingPayment.id.desc(),
    ).all()

    return render_template(
        "admin/bookings/booking_payments/index.html",
        payments=payments,
        form=form,
        selected_booking_id=booking_id or 0,
        selected_type=transaction_type,
        selected_status=status,
        search=search,)

@booking_payments_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = BookingPaymentForm()
    _populate_booking_choices(form)

    if not form.booking_id.choices:
        flash("Create a booking before recording a transaction.", "warning")
        return redirect(url_for("booking_payments.index"))

    if form.validate_on_submit():
        try:
            payment = create_booking_payment(
                booking_id=form.booking_id.data,
                amount=form.amount.data,
                payment_method=form.payment_method.data,
                currency=form.currency.data,
                transaction_type=form.transaction_type.data,
                payment_purpose=form.payment_purpose.data,
                transaction_reference=form.transaction_reference.data,
                payment_provider=form.payment_provider.data,
                provider_reference=form.provider_reference.data,
                description=form.description.data,
                internal_notes=form.internal_notes.data,
                recorded_by_user_id=current_user.id,
            )
            flash("Transaction recorded successfully.", "success")
            return redirect(
                url_for("booking_payments.detail", payment_id=payment.id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("The transaction could not be recorded.", "danger")

    return render_template(
        "admin/bookings/booking_payments/create.html",
        form=form,)

@booking_payments_bp.route("/<int:payment_id>", methods=["GET"])
@login_required
@admin_required
def detail(payment_id):
    payment = _get_payment_or_404(payment_id)
    summary = get_booking_payment_summary(payment.booking_id)
    refund_form = BookingRefundForm()

    refundable_amount = None
    if payment.transaction_type == "payment" and payment.status == "succeeded":
        refunded = sum(
            (
                Decimal(str(refund.amount))
                for refund in payment.refund_transactions
                if refund.status in {"pending", "processing", "succeeded"}
            ),
            Decimal("0.00"),
        )
        refundable_amount = max(
            Decimal("0.00"),
            Decimal(str(payment.amount)) - refunded,)

    return render_template(
        "admin/bookings/booking_payments/detail.html",
        payment=payment,
        summary=summary,
        refund_form=refund_form,
        refundable_amount=refundable_amount,)

@booking_payments_bp.route("/<int:payment_id>/refund",methods=["POST"],)
@login_required
@admin_required
def refund(payment_id):
    payment = _get_payment_or_404(payment_id)
    form = BookingRefundForm()

    if not form.validate_on_submit():
        flash("Please check the refund details and try again.", "danger")
        return redirect(
            url_for("booking_payments.detail", payment_id=payment.id)
        )

    try:
        refund_payment = record_refund(
            original_payment_id=payment.id,
            amount=form.amount.data,
            payment_method=form.payment_method.data or payment.payment_method,
            payment_provider=form.payment_provider.data,
            provider_reference=form.provider_reference.data,
            description=form.description.data,
            internal_notes=form.internal_notes.data,
            recorded_by_user_id=current_user.id,
        )
        flash(
            "Refund transaction created. It remains pending until confirmed.",
            "success",
        )
        return redirect(
            url_for(
                "booking_payments.detail",
                payment_id=refund_payment.id,
            )
        )
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
        return redirect(
            url_for("booking_payments.detail", payment_id=payment.id)
        )


@booking_payments_bp.route(
    "/<int:payment_id>/status",
    methods=["POST"],
)
@login_required
@admin_required
def update_status(payment_id):
    payment = _get_payment_or_404(payment_id)
    new_status = (request.form.get("status") or "").strip().lower()

    # The admin interface may update a pending/processing transaction to a
    # terminal status. Success should only be used after verification.
    if new_status == "succeeded":
        flash(
            "Use the verified payment completion workflow to confirm success.",
            "warning",
        )
        return redirect(
            url_for("booking_payments.detail", payment_id=payment.id)
        )

    try:
        update_payment_status(
            payment_id=payment.id,
            status=new_status,
            provider_response_message=(
                request.form.get("provider_response_message") or None
            ),
        )
        flash("Transaction status updated.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")

    return redirect(
        url_for("booking_payments.detail", payment_id=payment.id))