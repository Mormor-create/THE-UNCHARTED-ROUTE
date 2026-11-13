"""Administrative management for central TUR booking. Business logic belongs in Booking Service."""
from datetime import datetime, time
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.decorators.admin import admin_required
from extensions import db
from app.forms.admin_booking import (AdminBookingCreateForm, AdminBookingEditForm,
    AdminBookingFilterForm, AdminBookingStatusForm, AdminBookingCancellationForm)
from app.models import Booking
from app.services.bookings.booking_service import (BOOKING_STATUSES, cancel_booking,
    complete_booking, confirm_booking, create_booking, get_booking, get_booking_summary,
    update_booking_financials, update_booking_status)

bookings_bp = Blueprint('admin_bookings', __name__, url_prefix='/admin/booking')
SERVICE_TYPES = ('experience', 'safari', 'stay', 'destination_journey')

def _detail(booking):
    return redirect(url_for('admin_bookings.detail', booking_id=booking.id))

def _get_or_redirect(booking_id):
    booking = get_booking(booking_id)
    if booking is None:
        flash('Booking not found.', 'warning')
        return None, redirect(url_for('admin_bookings.index'))
    return booking, None

def _field_data(form, name, default=None):
    field = getattr(form, name, None)
    return field.data if field is not None else default


def _count(value):
    return len(value or [])


@bookings_bp.route('/')
@login_required
@admin_required
def index():
    form = AdminBookingFilterForm(formdata=request.args)
    query = Booking.query
    booking_type = (request.args.get('booking_type') or 'all').strip().lower()
    if booking_type in SERVICE_TYPES:
        query = query.filter(Booking.booking_type == booking_type)
    else:
        booking_type = 'all'
    search = (_field_data(form, 'search', '') or '').strip()
    if search:
        term = f'%{search}%'
        query = query.filter(db.or_(Booking.booking_reference.ilike(term),
            Booking.first_name.ilike(term), Booking.last_name.ilike(term),
            Booking.email.ilike(term), Booking.phone.ilike(term)))
    status = (_field_data(form, 'status', '') or '').strip().lower()
    if status in Booking.STATUSES:
        query = query.filter(Booking.status == status)
    payment_filter = (_field_data(form, 'payment_status', '') or '').strip().lower()
    if payment_filter == 'paid':
        query = query.filter(Booking.balance_due <= 0)
    elif payment_filter in {'outstanding', 'unpaid'}:
        query = query.filter(Booking.balance_due > 0)
    elif payment_filter == 'partially_paid':
        query = query.filter(Booking.amount_paid > 0, Booking.balance_due > 0)
    start = _field_data(form, 'booking_date_from')
    end = _field_data(form, 'booking_date_to')
    if start:
        query = query.filter(Booking.booking_date >= datetime.combine(start, time.min))
    if end:
        query = query.filter(Booking.booking_date <= datetime.combine(end, time.max))
    start = _field_data(form, 'experience_date_from')
    end = _field_data(form, 'experience_date_to')
    if start:
        query = query.filter(Booking.experience_date >= start)
    if end:
        query = query.filter(Booking.experience_date <= end)
    # experience_id belongs to the one-to-one detail model, not Booking itself.
    experience_id = _field_data(form, 'experience_id')
    if experience_id:
        query = query.filter(Booking.experience_booking.has(experience_id=experience_id))
    bookings = query.order_by(Booking.booking_date.desc(), Booking.id.desc()).all()
    all_bookings = Booking.query
    counts = {'all': all_bookings.count()}
    counts.update({kind: all_bookings.filter_by(booking_type=kind).count() for kind in SERVICE_TYPES})
    return render_template('admin/bookings/booking/index.html', form=form, bookings=bookings,
        booking_statuses=Booking.STATUSES, booking_types=SERVICE_TYPES,
        booking_type=booking_type, booking_counts=counts)


@bookings_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = AdminBookingCreateForm()
    if form.validate_on_submit():
        payload = {
            'booking_type': _field_data(form, 'booking_type', 'experience') or 'experience',
            'source': 'admin', 'first_name': form.first_name.data,
            'last_name': form.last_name.data, 'email': form.email.data,
            'phone': _field_data(form, 'phone'),
            'nationality': _field_data(form, 'nationality'),
            'country_of_residence': _field_data(form, 'country_of_residence'),
            'adults': _field_data(form, 'adults', 1) or 0,
            'children': _field_data(form, 'children', 0) or 0,
            'infants': _field_data(form, 'infants', 0) or 0,
            'seniors': _field_data(form, 'seniors', 0) or 0,
            'students': _field_data(form, 'students', 0) or 0,
            'emergency_contact_name': _field_data(form, 'emergency_contact_name'),
            'emergency_contact_phone': _field_data(form, 'emergency_contact_phone'),
            'emergency_contact_relationship': _field_data(form, 'emergency_contact_relationship'),
            'dietary_requirements': _field_data(form, 'dietary_requirements'),
            'medical_information': _field_data(form, 'medical_information'),
            'accessibility_requirements': _field_data(form, 'accessibility_requirements'),
            'special_requests': _field_data(form, 'special_requests'),
            'customer_notes': _field_data(form, 'customer_notes'),
            'status': (_field_data(form, 'status', 'pending') or 'pending').lower(),
        }
        for name in ('experience_id','pricing_id','experience_level','experience_date',
                     'safari_package_id','safari_id','stay_id','room_id','check_in','check_out','rooms',
                     'meal_plan','journey_id','start_date','end_date','pickup_location','dropoff_location',
                     'discount_amount','tax_amount','addon_total'):
            value = _field_data(form, name)
            if value is not None:
                payload[name] = value
        try:
            booking = create_booking(**payload)
        except (ValueError, TypeError) as exc:
            db.session.rollback()
            flash(str(exc), 'danger')
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Admin booking creation failed')
            flash('The booking could not be created. Please review the details and try again.', 'danger')
        else:
            flash(f'Booking {booking.booking_reference} created successfully.', 'success')
            return _detail(booking)
    return render_template('admin/bookings/booking/create.html', form=form, booking_types=SERVICE_TYPES)


@bookings_bp.route('/<int:booking_id>')
@login_required
@admin_required
def detail(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/detail.html', booking=booking, summary=get_booking_summary(booking))


@bookings_bp.route('/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    form = AdminBookingEditForm(obj=booking)
    if form.validate_on_submit():
        try:
            for name in ('first_name','last_name','email','phone','nationality','country_of_residence',
                         'emergency_contact_name','emergency_contact_phone','emergency_contact_relationship',
                         'dietary_requirements','medical_information','accessibility_requirements',
                         'special_requests','customer_notes','internal_notes'):
                field = getattr(form, name, None)
                if field is not None:
                    value = field.data
                    if name == 'email' and value: value = value.strip().lower()
                    if name in ('first_name','last_name') and value: value = value.strip()
                    setattr(booking, name, value)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Admin booking update failed')
            flash('The booking could not be updated. Please try again.', 'danger')
        else:
            flash('Booking updated successfully.', 'success')
            return _detail(booking)
    return render_template('admin/bookings/booking/edit.html', form=form, booking=booking)


def _action(booking_id, callback, message):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    form = AdminBookingStatusForm()
    if not form.validate_on_submit():
        flash('Invalid booking action request.', 'danger')
        return _detail(booking)
    try:
        callback(booking)
        flash(message, 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return _detail(booking)


@bookings_bp.route('/<int:booking_id>/confirm', methods=['POST'])
@login_required
@admin_required
def confirm(booking_id):
    return _action(booking_id, confirm_booking, 'Booking confirmed successfully.')


@bookings_bp.route('/<int:booking_id>/start', methods=['POST'])
@login_required
@admin_required
def start(booking_id):
    return _action(booking_id, lambda b: update_booking_status(b, 'in_progress'), 'Booking marked as in progress.')


@bookings_bp.route('/<int:booking_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete(booking_id):
    return _action(booking_id, complete_booking, 'Booking marked as completed.')


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    form = AdminBookingCancellationForm()
    if form.validate_on_submit():
        try:
            cancel_booking(booking, reason=form.reason.data)
            flash('Booking cancelled successfully.', 'success')
        except ValueError as exc:
            flash(str(exc), 'danger')
    else:
        flash('A valid cancellation reason is required.', 'danger')
    return _detail(booking)


@bookings_bp.route('/<int:booking_id>/refresh-payment-status', methods=['POST'])
@login_required
@admin_required
def refresh_payment_status(booking_id):
    return _action(booking_id, update_booking_financials, 'Booking payment totals refreshed.')


@bookings_bp.route('/<int:booking_id>/statistics')
@login_required
@admin_required
def statistics(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    stats = {'guest_count': booking.total_guests, 'traveller_count': _count(booking.travellers),
        'payment_count': _count(booking.payments), 'addon_count': _count(booking.addons),
        'note_count': _count(booking.notes), 'document_count': _count(booking.documents),
        'total_amount': booking.total_amount, 'amount_paid': booking.total_paid,
        'balance_due': booking.outstanding_balance, 'is_paid': booking.is_paid, 'status': booking.status}
    return render_template('admin/bookings/booking/statistics.html', booking=booking,
        summary=get_booking_summary(booking), statistics=stats)


@bookings_bp.route('/<int:booking_id>/travellers')
@login_required
@admin_required
def travellers(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/travellers.html', booking=booking, travellers=list(booking.travellers or []))


@bookings_bp.route('/<int:booking_id>/payments')
@login_required
@admin_required
def payments(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/payments.html', booking=booking, payments=list(booking.payments or []))


@bookings_bp.route('/<int:booking_id>/addons')
@login_required
@admin_required
def addons(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/addons.html', booking=booking, addons=list(booking.addons or []))


@bookings_bp.route('/<int:booking_id>/notes')
@login_required
@admin_required
def notes(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/notes.html', booking=booking, notes=list(booking.notes or []))


@bookings_bp.route('/<int:booking_id>/documents')
@login_required
@admin_required
def documents(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/documents.html', booking=booking, documents=list(booking.documents or []))


@bookings_bp.route('/<int:booking_id>/review')
@login_required
@admin_required
def review(booking_id):
    booking, response = _get_or_redirect(booking_id)
    if response: return response
    return render_template('admin/bookings/booking/review.html', booking=booking, reviews=list(booking.reviews or []))


__all__ = ['bookings_bp']
