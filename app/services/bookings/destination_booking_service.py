# =============================================================================
# The Uncharted Route
# Destination Journey Booking Service
# =============================================================================

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from app.models.booking import Booking
from app.models.destination_booking import DestinationBooking
from app.models.destination_journey import DestinationJourney

class DestinationBookingService:
    """Business logic for destination journey booking."""

    @staticmethod
    def populate_form_choices(form):
        """Populate journey choices before form validation."""
        journeys = (
            DestinationJourney.query
            .filter(DestinationJourney.status == "published")
            .order_by(DestinationJourney.name.asc())
            .all())

        # Keep an existing selected journey available for editing historical
        # booking even if it is no longer published.
        selected_id = None
        try:
            selected_id = int(form.journey_id.data)
        except (TypeError, ValueError):
            pass

        if selected_id and not any(j.id == selected_id for j in journeys):
            selected = db.session.get(DestinationJourney, selected_id)
            if selected:
                journeys.append(selected)

        form.journey_id.choices = [
            (journey.id, journey.name)
            for journey in journeys
        ]

    @staticmethod
    def list_bookings(search=None, status=None, archived=False):
        query = (
            Booking.query
            .join(
                DestinationBooking,
                DestinationBooking.booking_id == Booking.id,
            )
            .filter(Booking.booking_type == "destination_journey")
        )

        if archived:
            query = query.filter(
                or_(
                    Booking.status == "archived",
                    Booking.active.is_(False),
                )
            )
        else:
            query = query.filter(
                Booking.status != "archived",
                Booking.active.is_(True),
            )

        if status:
            query = query.filter(Booking.status == status)

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Booking.booking_reference.ilike(term),
                    Booking.first_name.ilike(term),
                    Booking.last_name.ilike(term),
                    Booking.email.ilike(term),
                    DestinationBooking.journey_name_snapshot.ilike(term),
                )
            )

        return query.order_by(Booking.created_at.desc()).all()

    @staticmethod
    def get_booking(booking_id):
        return (
            Booking.query
            .join(
                DestinationBooking,
                DestinationBooking.booking_id == Booking.id,
            )
            .filter(
                Booking.id == booking_id,
                Booking.booking_type == "destination_journey",
            )
            .first()
        )

    @staticmethod
    def _parse_preferred_stops(value):
        if not value:
            return None

        if isinstance(value, list):
            return value

        lines = [
            line.strip()
            for line in str(value).splitlines()
            if line.strip()
        ]
        return lines or None

    @staticmethod
    def _decimal(value, default="0.00"):
        try:
            return Decimal(str(value if value is not None else default))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal(default)

    @staticmethod
    def _snapshot_journey(journey):
        stops = []

        for stop in journey.stops:
            destination = stop.destination
            stops.append({
                "sequence": stop.sequence,
                "title": stop.title,
                "destination_id": stop.destination_id,
                "destination_name": (
                    getattr(destination, "name", None)
                    if destination else None
                ),
                "days": stop.days,
                "nights": stop.nights,
                "description": stop.description,
                "arrival_notes": stop.arrival_notes,
                "departure_notes": stop.departure_notes,
            })

        return {
            "itinerary": stops,
            "inclusions": [],
            "exclusions": [],
        }

    @staticmethod
    def _apply_shared_fields(booking, form, created_by_user=None):
        booking.booking_type = "destination_journey"
        booking.source = form.source.data or "admin"

        booking.first_name = form.first_name.data.strip()
        booking.last_name = form.last_name.data.strip()
        booking.email = form.email.data.strip()
        booking.phone = form.phone.data
        booking.nationality = form.nationality.data
        booking.country_of_residence = form.country_of_residence.data

        booking.adults = form.travellers_count.data
        booking.children = 0
        booking.infants = 0
        booking.seniors = 0
        booking.students = 0

        booking.booking_date = form.booking_date.data
        booking.start_date = form.start_date.data
        booking.end_date = form.end_date.data
        booking.experience_date = form.start_date.data

        booking.status = form.status.data
        booking.payment_status = form.payment_status.data
        booking.currency = form.currency.data

        booking.total_amount = DestinationBookingService._decimal(
            form.total_amount.data
        )
        booking.subtotal = booking.total_amount
        booking.discount_amount = Decimal("0.00")
        booking.tax_amount = Decimal("0.00")
        booking.addon_total = Decimal("0.00")
        booking.amount_paid = DestinationBookingService._decimal(
            form.amount_paid.data
        )
        booking.balance_due = max(
            Decimal("0.00"),
            booking.total_amount - booking.amount_paid,
        )

        booking.dietary_requirements = form.dietary_requirements.data
        booking.medical_information = form.medical_information.data
        booking.accessibility_requirements = (
            form.accessibility_requirements.data
        )
        booking.special_requests = form.special_requests.data
        booking.customer_notes = form.customer_notes.data
        booking.internal_notes = form.internal_notes.data

        if created_by_user is not None:
            booking.created_by_user = created_by_user

        if booking.status == "archived":
            booking.active = False
        elif booking.status != "archived":
            booking.active = True

    @staticmethod
    def _apply_detail_fields(detail, journey, form):
        snapshot = DestinationBookingService._snapshot_journey(journey)

        detail.journey_id = journey.id
        detail.journey_name_snapshot = journey.name
        detail.journey_slug_snapshot = journey.slug
        detail.journey_description_snapshot = (
            journey.description or journey.short_description
        )
        detail.itinerary_snapshot = snapshot["itinerary"]
        detail.inclusions_snapshot = snapshot["inclusions"]
        detail.exclusions_snapshot = snapshot["exclusions"]

        detail.start_date = form.start_date.data
        detail.end_date = form.end_date.data
        detail.duration_days = form.duration_days.data
        detail.duration_nights = form.duration_nights.data
        detail.travellers_count = form.travellers_count.data

        detail.rooming_preferences = form.rooming_preferences.data
        detail.transport_preferences = form.transport_preferences.data
        detail.preferred_stops = (
            DestinationBookingService._parse_preferred_stops(
                form.preferred_stops.data
            )
        )
        detail.bespoke_requirements = form.bespoke_requirements.data
        detail.bespoke = bool(form.bespoke.data or journey.is_bespoke)

        detail.pricing_basis = form.pricing_basis.data
        detail.unit_price = DestinationBookingService._decimal(
            form.unit_price.data
        )
        detail.currency = form.currency.data

    @staticmethod
    def create_booking(form, created_by_user=None):
        """Create Booking and DestinationBooking together."""
        try:
            journey = db.session.get(
                DestinationJourney,
                form.journey_id.data,
            )
            if journey is None:
                raise ValueError("The selected destination journey no longer exists.")

            if journey.status != "published":
                raise ValueError(
                    "Only published destination journeys can be booked."
                )

            if (
                journey.minimum_travellers
                and form.travellers_count.data < journey.minimum_travellers
            ):
                raise ValueError(
                    f"This journey requires at least "
                    f"{journey.minimum_travellers} travellers."
                )

            if (
                journey.maximum_travellers
                and form.travellers_count.data > journey.maximum_travellers
            ):
                raise ValueError(
                    f"This journey allows a maximum of "
                    f"{journey.maximum_travellers} travellers."
                )

            booking = Booking()
            DestinationBookingService._apply_shared_fields(
                booking,
                form,
                created_by_user=created_by_user,
            )
            db.session.add(booking)
            db.session.flush()

            detail = DestinationBooking(booking_id=booking.id)
            DestinationBookingService._apply_detail_fields(
                detail,
                journey,
                form,
            )
            db.session.add(detail)
            db.session.flush()

            return booking

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_booking(booking, form):
        """Update a booking without replacing its historical identity."""
        try:
            if booking.booking_type != "destination_journey":
                raise ValueError("This is not a destination journey booking.")

            journey = db.session.get(
                DestinationJourney,
                form.journey_id.data,
            )
            if journey is None:
                raise ValueError("The selected destination journey was not found.")

            if (
                journey.minimum_travellers
                and form.travellers_count.data < journey.minimum_travellers
            ):
                raise ValueError(
                    f"This journey requires at least "
                    f"{journey.minimum_travellers} travellers."
                )

            if (
                journey.maximum_travellers
                and form.travellers_count.data > journey.maximum_travellers
            ):
                raise ValueError(
                    f"This journey allows a maximum of "
                    f"{journey.maximum_travellers} travellers."
                )

            detail = booking.destination_booking
            if detail is None:
                detail = DestinationBooking(booking_id=booking.id)
                db.session.add(detail)

            DestinationBookingService._apply_shared_fields(booking, form)
            DestinationBookingService._apply_detail_fields(
                detail,
                journey,
                form,
            )

            db.session.flush()
            return booking

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def change_status(booking, status, internal_notes=None):
        if status not in Booking.STATUSES:
            raise ValueError("Invalid booking status.")

        booking.status = status
        booking.active = status != "archived"

        if internal_notes:
            existing = booking.internal_notes or ""
            booking.internal_notes = (
                f"{existing}\n{internal_notes}".strip()
                if existing else internal_notes
            )

        if status == "confirmed" and not booking.confirmed_at:
            from datetime import datetime
            booking.confirmed_at = datetime.utcnow()

        if status == "cancelled" and not booking.cancelled_at:
            from datetime import datetime
            booking.cancelled_at = datetime.utcnow()

        if status == "completed" and not booking.completed_at:
            from datetime import datetime
            booking.completed_at = datetime.utcnow()

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