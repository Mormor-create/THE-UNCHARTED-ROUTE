"""
===============================================================================
The Uncharted Route
Safari Booking Service
===============================================================================
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from extensions import db
from app.models.booking import Booking
from app.models.booking_request import BookingRequest
from app.models.safari_booking import SafariBooking

class SafariBookingService:
    """Business logic for safari booking using the central Booking model."""

    @staticmethod
    def _decimal(value, default="0.00"):
        try:
            result = Decimal(str(value if value not in (None, "") else default))
            if not result.is_finite():
                raise ValueError("Invalid monetary value.")
            return result
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Enter a valid monetary amount.")

    @staticmethod
    def _catalogue_choices(model, label_attributes):
        choices = [(0, "— Not selected —")]
        if model is None:
            return choices

        for item in model.query.order_by(model.id.asc()).all():
            label = next(
                (
                    getattr(item, attr, None)
                    for attr in label_attributes
                    if getattr(item, attr, None)
                ),
                f"Item #{item.id}",
            )
            choices.append((item.id, str(label)))
        return choices

    @classmethod
    def populate_form_choices(cls, form):
        """Populate catalogue selections without assuming every label field exists."""
        from app.models.safari import SafariDestination
        from app.models.safari import SafariProperty
        from app.models.safari import SafariPackageOption
        from app.models.safari import SafariPackageRate

        form.safari_destination_id.choices = cls._catalogue_choices(
            SafariDestination, ("name", "title", "destination_name", "slug")
        )
        form.property_id.choices = cls._catalogue_choices(
            SafariProperty, ("name", "title", "property_name", "slug")
        )
        form.package_option_id.choices = [
            (item.id, str(
                getattr(item, "name", None)
                or getattr(item, "title", None)
                or getattr(item, "package_name", None)
                or f"Package #{item.id}"
            ))
            for item in SafariPackageOption.query.order_by(
                SafariPackageOption.id.asc()
            ).all()
        ]
        form.package_rate_id.choices = cls._catalogue_choices(
            SafariPackageRate, ("name", "title", "rate_name")
        )

        # Optional selections use 0 as the "none" sentinel.
        for field_name in ("safari_destination_id", "property_id", "package_rate_id"):
            if getattr(form, field_name).data in ("", None):
                getattr(form, field_name).data = 0

    @staticmethod
    def list_bookings(search=None, status=None, archived=False):
        query = Booking.query.options(
            joinedload(Booking.safari_booking),
            joinedload(Booking.customer),
        ).filter(Booking.booking_type == "safari")

        if archived:
            query = query.filter(Booking.status == "archived")
        else:
            query = query.filter(Booking.status != "archived")

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
            joinedload(Booking.safari_booking),
            joinedload(Booking.customer),
            joinedload(Booking.payments),
            joinedload(Booking.travellers),
            joinedload(Booking.notes),
            joinedload(Booking.documents),
            joinedload(Booking.staff_assignments),
        ).filter_by(id=booking_id, booking_type="safari").first_or_404()

    @staticmethod
    def _snapshot(obj, names, fallback=None):
        for name in names:
            value = getattr(obj, name, None) if obj is not None else None
            if value not in (None, ""):
                return value
        return fallback

    @classmethod
    def _build_safari_detail(cls, form):
        from app.models.safari import SafariDestination
        from app.models.safari import SafariProperty
        from app.models.safari import SafariPackageOption
        from app.models.safari import SafariPackageRate

        package = SafariPackageOption.query.get(form.package_option_id.data)
        if package is None:
            raise ValueError("Select a valid safari package.")

        destination_id = form.safari_destination_id.data or None
        property_id = form.property_id.data or None
        rate_id = form.package_rate_id.data or None

        destination = (
            SafariDestination.query.get(destination_id) if destination_id else None
        )
        property_obj = SafariProperty.query.get(property_id) if property_id else None
        rate = SafariPackageRate.query.get(rate_id) if rate_id else None

        return {
            "safari_destination_id": destination_id,
            "property_id": property_id,
            "package_option_id": package.id,
            "package_rate_id": rate_id,
            "package_name_snapshot": cls._snapshot(
                package, ("name", "title", "package_name"), f"Package #{package.id}"
            ),
            "destination_name_snapshot": cls._snapshot(
                destination, ("name", "title", "destination_name")
            ),
            "property_name_snapshot": cls._snapshot(
                property_obj, ("name", "title", "property_name")
            ),
            "package_description_snapshot": cls._snapshot(
                package, ("description", "short_description")
            ),
            "itinerary_snapshot": cls._snapshot(package, ("itinerary",)),
            "inclusions_snapshot": cls._snapshot(package, ("inclusions",)),
            "exclusions_snapshot": cls._snapshot(package, ("exclusions",)),
            "start_date": form.start_date.data,
            "end_date": form.end_date.data,
            "duration_days": form.duration_days.data,
            "duration_nights": form.duration_nights.data,
            "rooms_required": form.rooms_required.data,
            "adults": form.adults.data,
            "children": form.children.data,
            "infants": form.infants.data,
            "rooming_preferences": form.rooming_preferences.data,
            "rate_name_snapshot": (
                cls._snapshot(rate, ("name", "title", "rate_name"))
                or form.rate_name_snapshot.data
            ),
            "rate_basis": form.rate_basis.data,
            "unit_rate": cls._decimal(form.unit_rate.data),
            "quantity": form.quantity.data,
            "currency": form.currency.data,
            "pickup_location": form.pickup_location.data,
            "transfer_requirements": form.transfer_requirements.data,
            "wildlife_interests": form.wildlife_interests.data,
            "special_safari_requirements": form.special_safari_requirements.data,
        }

    @classmethod
    def create_booking(cls, form, created_by_user=None, source_request=None):
        """Create a central Booking and its SafariBooking detail atomically."""
        if form.end_date.data < form.start_date.data:
            raise ValueError("Departure date cannot be before the start date.")

        total_guests = (
            form.adults.data + form.children.data + form.infants.data
        )
        if total_guests < 1:
            raise ValueError("A safari booking must include at least one traveller.")

        detail_data = cls._build_safari_detail(form)
        unit_rate = detail_data["unit_rate"]
        quantity = detail_data["quantity"]
        subtotal = unit_rate * quantity
        total = (
            cls._decimal(form.currency_total.data)
            if form.currency_total.data not in (None, "")
            else subtotal
        )
        amount_paid = cls._decimal(form.amount_paid.data)

        if amount_paid > total:
            raise ValueError("Amount paid cannot exceed the booking total.")

        booking = Booking(
            booking_type="safari",
            source=("staff_request" if source_request else form.source.data),
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
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            currency=form.currency.data,
            subtotal=subtotal,
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
        detail = SafariBooking(booking=booking, **detail_data)
        db.session.add(booking)
        db.session.add(detail)
        db.session.flush()
        return booking

    @classmethod
    def update_booking(cls, booking, form):
        if not booking.safari_booking:
            raise ValueError("Safari details are missing for this booking.")

        if form.end_date.data < form.start_date.data:
            raise ValueError("Departure date cannot be before the start date.")

        total_guests = form.adults.data + form.children.data + form.infants.data
        if total_guests < 1:
            raise ValueError("A safari booking must include at least one traveller.")

        detail_data = cls._build_safari_detail(form)
        total = (
            cls._decimal(form.currency_total.data)
            if form.currency_total.data not in (None, "")
            else detail_data["unit_rate"] * detail_data["quantity"]
        )
        paid = cls._decimal(form.amount_paid.data)
        if paid > total:
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
        booking.start_date = form.start_date.data
        booking.end_date = form.end_date.data
        booking.currency = form.currency.data
        booking.subtotal = detail_data["unit_rate"] * detail_data["quantity"]
        booking.total_amount = total
        booking.amount_paid = paid
        booking.balance_due = total - paid
        booking.dietary_requirements = form.dietary_requirements.data
        booking.accessibility_requirements = form.accessibility_requirements.data
        booking.special_requests = form.special_requests.data
        booking.customer_notes = form.customer_notes.data
        booking.internal_notes = form.internal_notes.data

        for key, value in detail_data.items():
            setattr(booking.safari_booking, key, value)

        return booking

    @staticmethod
    def change_status(booking, status, internal_notes=None):
        if status not in Booking.STATUSES:
            raise ValueError("Invalid booking status.")

        booking.status = status
        now = datetime.utcnow()

        if status == "confirmed" and not booking.confirmed_at:
            booking.confirmed_at = now
        elif status == "cancelled" and not booking.cancelled_at:
            booking.cancelled_at = now
        elif status == "completed" and not booking.completed_at:
            booking.completed_at = now

        if internal_notes:
            existing = booking.internal_notes or ""
            booking.internal_notes = (
                f"{existing}\n\n{now:%Y-%m-%d %H:%M} — {internal_notes}".strip()
            )
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

    @classmethod
    def convert_request(cls, request, created_by_user):
        """Convert an approved staff request exactly once."""
        if request.service_type != "safari":
            raise ValueError("This is not a safari booking request.")
        if request.is_converted:
            raise ValueError("This request has already been converted.")
        if request.status not in ("approved", "accepted"):
            raise ValueError("Approve the request before converting it.")

        raise ValueError(
            "Request conversion requires the complete safari form data. "
            "Use the request conversion page to confirm package, rate, and dates.")