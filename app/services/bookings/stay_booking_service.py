"""
===============================================================================
The Uncharted Route
Stay Booking Service
===============================================================================
Stay-specific booking operations.
The central Booking record remains the master operational record.
Stay bookings use customer-requested dates and are confirmed manually
after the property availability is checked outside the application.
===============================================================================
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from extensions import db
from app.models.booking import Booking
from app.models.stay_booking import StayBooking

class StayBookingService:
    """Business logic for stay reservations backed by the central Booking."""

    @staticmethod
    def decimal_value(value, default="0.00"):
        try:
            amount = Decimal(str(value if value not in (None, "") else default))
            if not amount.is_finite() or amount < 0:
                raise ValueError("Amounts must be non-negative.")
            return amount
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Enter a valid monetary amount.")

    @staticmethod
    def _label(item, fields):
        for field in fields:
            value = getattr(item, field, None)
            if value:
                return str(value)
        return f"Item #{item.id}"

    @classmethod
    def populate_form_choices(cls, form):
        # Keep these imports aligned with the existing Stay catalogue model files.
        from app.models.stay import Stay
        from app.models.stay_room import StayRoom

        form.stay_id.choices = [
            (item.id, cls._label(item, ("name", "title", "stay_name", "slug")))
            for item in Stay.query.order_by(Stay.id.asc()).all()
        ]
        form.room_id.choices = [(0, "— No specific room selected —")] + [
            (item.id, cls._label(item, ("name", "title", "room_name", "room_type")))
            for item in StayRoom.query.order_by(StayRoom.id.asc()).all()
        ]

        if form.room_id.data in (None, ""):
            form.room_id.data = 0

    @staticmethod
    def list_bookings(search=None, status=None, archived=False):
        query = Booking.query.options(
            joinedload(Booking.stay_booking),
            joinedload(Booking.customer),
        ).filter(Booking.booking_type == "stay")

        query = (
            query.filter(Booking.status == "archived")
            if archived else query.filter(Booking.status != "archived")
        )

        if status and status != "all":
            query = query.filter(Booking.status == status)

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(or_(
                Booking.booking_reference.ilike(term),
                Booking.first_name.ilike(term),
                Booking.last_name.ilike(term),
                Booking.email.ilike(term),
                Booking.phone.ilike(term),
            ))

        return query.order_by(Booking.created_at.desc()).all()

    @staticmethod
    def get_booking(booking_id):
        return Booking.query.options(
            joinedload(Booking.stay_booking),
            joinedload(Booking.customer),
            joinedload(Booking.payments),
            joinedload(Booking.travellers),
            joinedload(Booking.addons),
            joinedload(Booking.notes),
            joinedload(Booking.documents),
            joinedload(Booking.staff_assignments),
            joinedload(Booking.tasks),
            joinedload(Booking.reviews),
        ).filter_by(id=booking_id, booking_type="stay").first_or_404()

    @staticmethod
    def _snapshot(item, fields, fallback=None):
        for field in fields:
            value = getattr(item, field, None) if item is not None else None
            if value not in (None, ""):
                return value
        return fallback

    @classmethod
    def build_stay_detail(cls, form):
        from app.models.stay import Stay
        from app.models.stay_room import StayRoom

        stay = Stay.query.get(form.stay_id.data)
        if stay is None:
            raise ValueError("Select a valid accommodation.")

        room_id = form.room_id.data or None
        room = StayRoom.query.get(room_id) if room_id else None

        if room is not None:
            # If rooms belong to a stay, prevent selecting a room from another stay.
            room_stay_id = getattr(room, "stay_id", None)
            if room_stay_id is not None and room_stay_id != stay.id:
                raise ValueError("The selected room does not belong to this accommodation.")

        check_in = form.check_in.data
        check_out = form.check_out.data
        if check_out <= check_in:
            raise ValueError("Check-out must be after check-in.")

        expected_nights = (check_out - check_in).days
        if form.nights.data != expected_nights:
            raise ValueError(
                f"The selected dates represent {expected_nights} night(s)."
            )

        guests = form.adults.data + form.children.data + form.infants.data
        if guests < 1:
            raise ValueError("A stay booking must include at least one guest.")

        occupancy = {
            "adults": form.adults.data,
            "children": form.children.data,
            "infants": form.infants.data,
            "rooms": form.rooms_count.data,
        }

        return {
            "stay_id": stay.id,
            "room_id": room.id if room else None,
            "stay_name_snapshot": cls._snapshot(
                stay, ("name", "title", "stay_name"), f"Stay #{stay.id}"
            ),
            "property_location_snapshot": cls._snapshot(
                stay, ("location", "address", "property_location", "city")
            ),
            "room_name_snapshot": cls._snapshot(
                room, ("name", "title", "room_name", "room_type")
            ),
            "room_description_snapshot": cls._snapshot(
                room, ("description", "short_description")
            ),
            "meal_plan": form.meal_plan.data or None,
            "meal_plan_snapshot": form.meal_plan_snapshot.data or form.meal_plan.data or None,
            "check_in": check_in,
            "check_out": check_out,
            "nights": expected_nights,
            "rooms_count": form.rooms_count.data,
            "adults": form.adults.data,
            "children": form.children.data,
            "infants": form.infants.data,
            "occupancy_snapshot": occupancy,
            "rate_name_snapshot": form.rate_name_snapshot.data,
            "rate_basis": form.rate_basis.data,
            "nightly_rate": cls.decimal_value(form.nightly_rate.data),
            "currency": form.currency.data,
            "arrival_time": form.arrival_time.data,
            "departure_time": form.departure_time.data,
            "special_requests": form.special_requests.data,
            "accessibility_requirements": form.accessibility_requirements.data,
            "availability_reference": form.availability_reference.data,
        }

    @classmethod
    def create_booking(cls, form, created_by_user=None, source_request=None):
        detail_data = cls.build_stay_detail(form)
        nightly_rate = detail_data["nightly_rate"]

        if detail_data["rate_basis"] == "per_person_per_night":
            billable_units = (
                form.adults.data + form.children.data
            ) * form.nights.data
        elif detail_data["rate_basis"] == "per_person":
            billable_units = form.adults.data + form.children.data
        elif detail_data["rate_basis"] == "per_room":
            billable_units = form.rooms_count.data
        elif detail_data["rate_basis"] == "per_stay":
            billable_units = 1
        else:
            billable_units = form.rooms_count.data * form.nights.data

        calculated_total = nightly_rate * billable_units
        total = (
            cls.decimal_value(form.currency_total.data)
            if form.currency_total.data not in (None, "")
            else calculated_total
        )
        amount_paid = cls.decimal_value(form.amount_paid.data)
        if amount_paid > total:
            raise ValueError("Amount paid cannot exceed the booking total.")

        booking = Booking(
            booking_type="stay",
            source="staff_request" if source_request else form.source.data,
            created_by_user=created_by_user,
            source_request=source_request,
            user_id=source_request.user_id if source_request else None,
            contact_id=source_request.contact_id if source_request else None,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            nationality=form.nationality.data,
            country_of_residence=form.country_of_residence.data,
            adults=form.adults.data,
            children=form.children.data,
            infants=form.infants.data,
            status=form.status.data,
            payment_status=form.payment_status.data,
            booking_date=form.booking_date.data,
            start_date=form.check_in.data,
            end_date=form.check_out.data,
            currency=form.currency.data,
            subtotal=calculated_total,
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            addon_total=Decimal("0.00"),
            total_amount=total,
            amount_paid=amount_paid,
            balance_due=total - amount_paid,
            dietary_requirements=form.dietary_requirements.data,
            accessibility_requirements=form.accessibility_requirements.data,
            special_requests=form.special_requests.data,
            customer_notes=form.customer_notes.data,
            internal_notes=form.internal_notes.data,
        )

        db.session.add(booking)
        booking.stay_booking = StayBooking(**detail_data)
        db.session.flush()
        return booking

    @classmethod
    def update_booking(cls, booking, form):
        if not booking.stay_booking:
            raise ValueError("Accommodation details are missing from this booking.")

        detail_data = cls.build_stay_detail(form)
        nightly_rate = detail_data["nightly_rate"]

        if detail_data["rate_basis"] == "per_person_per_night":
            units = (form.adults.data + form.children.data) * form.nights.data
        elif detail_data["rate_basis"] == "per_person":
            units = form.adults.data + form.children.data
        elif detail_data["rate_basis"] == "per_room":
            units = form.rooms_count.data
        elif detail_data["rate_basis"] == "per_stay":
            units = 1
        else:
            units = form.rooms_count.data * form.nights.data

        calculated_total = nightly_rate * units
        total = (
            cls.decimal_value(form.currency_total.data)
            if form.currency_total.data not in (None, "")
            else calculated_total
        )
        amount_paid = cls.decimal_value(form.amount_paid.data)
        if amount_paid > total:
            raise ValueError("Amount paid cannot exceed the booking total.")

        booking.first_name = form.first_name.data.strip()
        booking.last_name = form.last_name.data.strip()
        booking.email = form.email.data.strip()
        booking.phone = form.phone.data.strip() if form.phone.data else None
        booking.nationality = form.nationality.data
        booking.country_of_residence = form.country_of_residence.data
        booking.adults = form.adults.data
        booking.children = form.children.data
        booking.infants = form.infants.data
        booking.status = form.status.data
        booking.payment_status = form.payment_status.data
        booking.booking_date = form.booking_date.data
        booking.start_date = form.check_in.data
        booking.end_date = form.check_out.data
        booking.currency = form.currency.data
        booking.subtotal = calculated_total
        booking.total_amount = total
        booking.amount_paid = amount_paid
        booking.balance_due = total - amount_paid
        booking.dietary_requirements = form.dietary_requirements.data
        booking.accessibility_requirements = form.accessibility_requirements.data
        booking.special_requests = form.special_requests.data
        booking.customer_notes = form.customer_notes.data
        booking.internal_notes = form.internal_notes.data

        for key, value in detail_data.items():
            setattr(booking.stay_booking, key, value)

        return booking

    @staticmethod
    def change_status(booking, status, internal_notes=None):
        if status not in Booking.STATUSES:
            raise ValueError("Invalid booking status.")

        now = datetime.utcnow()
        booking.status = status

        if status == "confirmed" and not booking.confirmed_at:
            booking.confirmed_at = now
        elif status == "cancelled" and not booking.cancelled_at:
            booking.cancelled_at = now
        elif status == "completed" and not booking.completed_at:
            booking.completed_at = now

        if internal_notes:
            booking.internal_notes = (
                f"{booking.internal_notes or ''}\n\n"
                f"{now:%Y-%m-%d %H:%M} — {internal_notes}"
            ).strip()
        return booking

    @staticmethod
    def archive(booking):
        booking.status = "archived"
        booking.active = False
        return booking

    @staticmethod
    def restore(booking):
        booking.status = "pending"
        booking.active = True
        return booking
