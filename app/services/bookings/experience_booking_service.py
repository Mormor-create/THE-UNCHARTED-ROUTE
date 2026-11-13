"""
===============================================================================
The Uncharted Route
Experience Booking Service
===============================================================================

Central booking-domain service for experience bookings.

This service owns the lifecycle of the central Booking record and coordinates
the experience-specific detail through:

    app.services.experiences.experience_booking_service

Responsibilities here include:

    - creating the central Booking
    - updating customer/traveller booking data
    - updating booking status
    - retrieving experience bookings
    - coordinating ExperienceBooking details
    - converting experience inquiries into central bookings

Experience schedules are intentionally not supported.

Experiences use customer-requested dates rather than fixed departure schedules.
"""

from datetime import datetime
from decimal import Decimal
from extensions import db
from app.models import (
    Booking,
    ExperienceBooking,
    ExperienceInquiry,)
from app.services.experiences.experience_booking_service import (
    ExperienceBookingService as ExperienceDomainService,)

class ExperienceBookingService:
    """Central booking lifecycle service for experience bookings."""

    # -------------------------------------------------------------------------
    # Retrieval
    # -------------------------------------------------------------------------

    @staticmethod
    def get_booking(booking_id):
        """Return a central Booking by ID."""
        if not booking_id:
            return None

        try:
            booking_id = int(booking_id)
        except (TypeError, ValueError, OverflowError):
            return None

        booking = db.session.get(
            Booking,
            booking_id,
        )

        if (
            booking is None
            or booking.booking_type != "experience"
        ):
            return None

        return booking

    @staticmethod
    def get_experience_booking(booking_id):
        """Return the experience detail attached to a central booking."""
        booking = ExperienceBookingService.get_booking(
            booking_id
        )

        if booking is None:
            return None

        return booking.experience_booking

    @staticmethod
    def get_booking_by_reference(reference):
        """Return an experience booking by booking reference."""
        if not reference:
            return None

        booking = (
            Booking.query
            .filter(
                Booking.booking_reference == reference,
                Booking.booking_type == "experience",
            )
            .first()
        )

        return booking

    # -------------------------------------------------------------------------
    # Catalogue compatibility
    # -------------------------------------------------------------------------

    @staticmethod
    def get_catalogue_choices():
        """
        Return active experience choices.

        Kept here as a compatibility entry point for admin forms.
        The actual catalogue query belongs to the Experience domain service.
        """
        return ExperienceDomainService.get_catalogue_choices()

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    @staticmethod
    def create_booking(
        *,
        experience,
        first_name,
        last_name,
        email,
        phone=None,
        nationality=None,
        country_of_residence=None,
        adults=1,
        children=0,
        infants=0,
        experience_date=None,
        pricing_id=None,
        pickup_location=None,
        dropoff_location=None,
        customer_instructions=None,
        source="admin",
        status="Pending",
        payment_status="unpaid",
    ):
        """
        Create a complete central experience Booking.

        The central Booking is created here.

        The ExperienceBooking detail is created by the Experience-domain
        service.
        """

        if experience is None or not experience.active:
            raise ValueError(
                "The selected experience is unavailable."
            )

        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        email = (email or "").strip().lower()

        if not first_name or not last_name:
            raise ValueError(
                "First name and last name are required."
            )

        if not email:
            raise ValueError(
                "An email address is required."
            )

        counts = (
            ExperienceDomainService.validate_guest_counts(
                adults=adults,
                children=children,
                infants=infants,
            )
        )

        guest_count = sum(counts.values())

        pricing = ExperienceDomainService.validate_pricing(
            experience=experience,
            pricing_id=pricing_id,
            guest_count=guest_count,
        )

        unit_price = ExperienceDomainService.money(
            pricing.price
        )

        currency = (
            pricing.currency or "KES"
        ).upper()

        subtotal = ExperienceDomainService.calculate_total(
            pricing=pricing,
            adults=counts["adults"],
            children=counts["children"],
            infants=counts["infants"],
        )

        now = datetime.utcnow()

        booking = Booking(
            booking_type="experience",
            source=source,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=(phone or "").strip() or None,
            nationality=(
                (nationality or "").strip()
                or None
            ),
            country_of_residence=(
                (country_of_residence or "").strip()
                or None
            ),
            adults=counts["adults"],
            children=counts["children"],
            infants=counts["infants"],
            seniors=0,
            students=0,
            status=status,
            payment_status=payment_status,
            booking_date=now,
            experience_date=experience_date,
            currency=currency,
            subtotal=subtotal,
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            addon_total=Decimal("0.00"),
            total_amount=subtotal,
            amount_paid=Decimal("0.00"),
            balance_due=subtotal,
            customer_notes=(
                (customer_instructions or "").strip()
                or None
            ),
            created_at=now,
            updated_at=now,
        )

        detail = (
            ExperienceDomainService.build_booking_detail(
                experience=experience,
                pricing=pricing,
                adults=counts["adults"],
                children=counts["children"],
                infants=counts["infants"],
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                customer_instructions=customer_instructions,
            )
        )

        booking.experience_booking = detail

        try:
            db.session.add(booking)
            db.session.flush()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return booking

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    @staticmethod
    def update_booking(
        booking,
        *,
        experience=None,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        nationality=None,
        country_of_residence=None,
        adults=None,
        children=None,
        infants=None,
        experience_date=None,
        pricing_id=None,
        pickup_location=None,
        dropoff_location=None,
        customer_instructions=None,
        status=None,
        payment_status=None,
    ):
        """
        Update a central experience Booking and its experience detail.
        """

        if booking is None:
            raise ValueError(
                "Experience booking was not found."
            )

        if booking.booking_type != "experience":
            raise ValueError(
                "This booking is not an experience booking."
            )

        detail = booking.experience_booking

        if detail is None:
            raise ValueError(
                "Experience booking details are missing."
            )

        selected_experience = (
            experience
            if experience is not None
            else detail.experience
        )

        if selected_experience is None:
            raise ValueError(
                "A valid experience is required."
            )

        if not selected_experience.active:
            raise ValueError(
                "The selected experience is inactive."
            )

        # ---------------------------------------------------------------------
        # Customer information
        # ---------------------------------------------------------------------

        if first_name is not None:
            booking.first_name = (
                first_name.strip()
            )

        if last_name is not None:
            booking.last_name = (
                last_name.strip()
            )

        if email is not None:
            booking.email = (
                email.strip().lower()
            )

        if phone is not None:
            booking.phone = (
                phone.strip()
                or None
            )

        if nationality is not None:
            booking.nationality = (
                nationality.strip()
                or None
            )

        if country_of_residence is not None:
            booking.country_of_residence = (
                country_of_residence.strip()
                or None
            )

        # ---------------------------------------------------------------------
        # Traveller information
        # ---------------------------------------------------------------------

        current_adults = (
            adults
            if adults is not None
            else booking.adults
        )

        current_children = (
            children
            if children is not None
            else booking.children
        )

        current_infants = (
            infants
            if infants is not None
            else booking.infants
        )

        counts = (
            ExperienceDomainService.validate_guest_counts(
                adults=current_adults,
                children=current_children,
                infants=current_infants,
            )
        )

        guest_count = sum(counts.values())

        booking.adults = counts["adults"]
        booking.children = counts["children"]
        booking.infants = counts["infants"]

        # ---------------------------------------------------------------------
        # Experience / pricing
        # ---------------------------------------------------------------------

        pricing = None

        if pricing_id is not None:
            pricing = (
                ExperienceDomainService.validate_pricing(
                    experience=selected_experience,
                    pricing_id=pricing_id,
                    guest_count=guest_count,
                )
            )
        elif detail.pricing is not None:
            pricing = (
                ExperienceDomainService.validate_pricing(
                    experience=selected_experience,
                    pricing_id=detail.pricing.id,
                    guest_count=guest_count,
                )
            )
        else:
            pricing = (
                ExperienceDomainService.validate_pricing(
                    experience=selected_experience,
                    guest_count=guest_count,
                )
            )

        ExperienceDomainService.update_booking_detail(
            detail,
            experience=selected_experience,
            pricing=pricing,
            adults=counts["adults"],
            children=counts["children"],
            infants=counts["infants"],
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            customer_instructions=customer_instructions,
        )

        # ---------------------------------------------------------------------
        # Requested experience date
        # ---------------------------------------------------------------------

        if experience_date is not None:
            booking.experience_date = experience_date

        # ---------------------------------------------------------------------
        # Recalculate amount
        # ---------------------------------------------------------------------

        subtotal = (
            ExperienceDomainService.calculate_total(
                pricing=pricing,
                adults=counts["adults"],
                children=counts["children"],
                infants=counts["infants"],
            )
        )

        booking.currency = (
            pricing.currency or "KES"
        ).upper()

        booking.subtotal = subtotal
        booking.total_amount = subtotal

        discount = (
            booking.discount_amount
            or Decimal("0.00")
        )

        tax = (
            booking.tax_amount
            or Decimal("0.00")
        )

        addon_total = (
            booking.addon_total
            or Decimal("0.00")
        )

        booking.total_amount = (
            subtotal
            - discount
            + tax
            + addon_total
        )

        booking.amount_paid = (
            booking.amount_paid
            or Decimal("0.00")
        )

        booking.balance_due = (
            booking.total_amount
            - booking.amount_paid
        )

        if status is not None:
            booking.status = status

        if payment_status is not None:
            booking.payment_status = payment_status

        booking.updated_at = datetime.utcnow()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return booking

    # -------------------------------------------------------------------------
    # Inquiry conversion
    # -------------------------------------------------------------------------

    @staticmethod
    def convert_request(
        inquiry,
        *,
        pricing_id=None,
        status="Pending",
        source="admin",
    ):
        """
        Convert an ExperienceInquiry into a central Booking.

        The inquiry remains the historical request record.
        """

        if inquiry is None:
            raise ValueError(
                "Experience inquiry was not found."
            )

        if inquiry.experience is None:
            raise ValueError(
                "The inquiry has no associated experience."
            )

        if not inquiry.experience.active:
            raise ValueError(
                "The experience associated with this inquiry "
                "is inactive."
            )

        # Prevent accidental duplicate conversion when an inquiry has
        # already been linked to a booking by application-level workflows.
        existing_booking = (
            Booking.query
            .filter(
                Booking.booking_type == "experience",
                Booking.email == inquiry.email,
                Booking.experience_date == inquiry.preferred_date,
            )
            .join(
                ExperienceBooking,
                ExperienceBooking.booking_id == Booking.id,
            )
            .filter(
                ExperienceBooking.experience_id
                == inquiry.experience_id,
            )
            .first()
        )

        if existing_booking is not None:
            return existing_booking

        return ExperienceBookingService.create_booking(
            experience=inquiry.experience,
            first_name=(
                inquiry.full_name.split(" ", 1)[0]
            ),
            last_name=(
                inquiry.full_name.split(" ", 1)[1]
                if " " in inquiry.full_name
                else inquiry.full_name
            ),
            email=inquiry.email,
            phone=inquiry.phone,
            country_of_residence=inquiry.country,
            adults=inquiry.adults,
            children=inquiry.children,
            infants=inquiry.infants,
            experience_date=inquiry.preferred_date,
            pricing_id=pricing_id,
            customer_instructions=inquiry.special_requests,
            source=source,
            status=status,
            payment_status="unpaid",
        )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    @staticmethod
    def update_status(booking, status):
        """Update the central booking status."""
        if booking is None:
            raise ValueError(
                "Experience booking was not found."
            )

        if booking.booking_type != "experience":
            raise ValueError(
                "This booking is not an experience booking."
            )

        if not status:
            raise ValueError(
                "A booking status is required."
            )

        booking.status = status.strip()
        booking.updated_at = datetime.utcnow()

        db.session.commit()

        return booking

    # -------------------------------------------------------------------------
    # Archive
    # -------------------------------------------------------------------------
    @staticmethod
    def archive_booking(booking):
        """Archive an experience booking without deleting its history."""
        if booking is None:
            raise ValueError(
                "Experience booking was not found."
            )

        if hasattr(booking, "is_archived"):
            booking.is_archived = True

        booking.updated_at = datetime.utcnow()

        db.session.commit()

        return booking