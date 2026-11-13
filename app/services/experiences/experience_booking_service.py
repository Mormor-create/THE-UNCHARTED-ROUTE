"""
===============================================================================
The Uncharted Route
Experience Booking Domain Service
===============================================================================
Owns experience-specific booking logic.
This service is responsible for the relationship between:
    Experience
        ↓
    ExperiencePricing
        ↓
    ExperienceBooking

It does NOT own the central Booking lifecycle.
Experiences are not tied to fixed schedules. Customers may request a preferred
date, and TUR confirms feasibility separately.
"""

from decimal import Decimal, ROUND_HALF_UP
from extensions import db
from app.models import (
    Experience,
    ExperienceBooking,
    ExperienceInquiry,
    ExperiencePricing,)

CENT = Decimal("0.01")


class ExperienceBookingService:
    """Service for experience-specific booking operations."""

    # -------------------------------------------------------------------------
    # Catalogue
    # -------------------------------------------------------------------------

    @staticmethod
    def get_catalogue_choices():
        """
        Return active experiences suitable for booking selection.

        Used by admin booking forms and other internal booking workflows.
        """
        return (
            Experience.query
            .filter(Experience.active.is_(True))
            .order_by(Experience.title.asc(), Experience.id.asc())
            .all()
        )

    @staticmethod
    def get_bookable_experience(slug):
        """Return an active experience by slug."""
        if not slug:
            return None

        return (
            Experience.query
            .filter(
                Experience.slug == slug,
                Experience.active.is_(True),
            )
            .first()
        )

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    @staticmethod
    def get_pricing(experience_id, active_only=False):
        """Return pricing options for an experience."""
        query = ExperiencePricing.query.filter_by(
            experience_id=experience_id,
        )

        if active_only:
            query = query.filter(
                ExperiencePricing.active.is_(True),
            )

        return (
            query
            .order_by(
                ExperiencePricing.display_order.asc(),
                ExperiencePricing.id.asc(),
            )
            .all()
        )

    @staticmethod
    def get_active_pricing(experience_id):
        """Return active pricing options in display order."""
        return ExperienceBookingService.get_pricing(
            experience_id=experience_id,
            active_only=True,
        )

    @staticmethod
    def get_pricing_option(experience_id, pricing_id):
        """Return a pricing option belonging to the specified experience."""
        if not pricing_id:
            return None

        try:
            pricing_id = int(pricing_id)
        except (TypeError, ValueError, OverflowError):
            return None

        return (
            ExperiencePricing.query
            .filter(
                ExperiencePricing.id == pricing_id,
                ExperiencePricing.experience_id == experience_id,
            )
            .first()
        )

    @staticmethod
    def get_default_pricing(experience_id):
        """Return the first active pricing option."""
        return (
            ExperiencePricing.query
            .filter(
                ExperiencePricing.experience_id == experience_id,
                ExperiencePricing.active.is_(True),
            )
            .order_by(
                ExperiencePricing.display_order.asc(),
                ExperiencePricing.id.asc(),
            )
            .first()
        )

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_guest_counts(adults=1, children=0, infants=0):
        """Validate and normalize experience traveller counts."""

        try:
            counts = {
                "adults": int(adults),
                "children": int(children),
                "infants": int(infants),
            }
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                "Guest counts must be valid whole numbers."
            ) from exc

        for field, original_value in (
            ("adults", adults),
            ("children", children),
            ("infants", infants),
        ):
            try:
                if Decimal(str(original_value or 0)) != Decimal(
                    counts[field]
                ):
                    raise ValueError(
                        "Guest counts must be valid whole numbers."
                    )
            except (TypeError, ValueError, ArithmeticError) as exc:
                raise ValueError(
                    "Guest counts must be valid whole numbers."
                ) from exc

        if any(value < 0 for value in counts.values()):
            raise ValueError(
                "Guest counts cannot be negative."
            )

        if sum(counts.values()) < 1:
            raise ValueError(
                "At least one traveller is required."
            )

        return counts

    @staticmethod
    def validate_pricing(
        experience,
        pricing_id=None,
        guest_count=1,
    ):
        """
        Validate and return the appropriate pricing option.

        If pricing_id is omitted, the first active pricing option is used.
        """

        if experience is None or not experience.active:
            raise ValueError(
                "This experience is currently unavailable."
            )

        if pricing_id:
            try:
                pricing_id = int(pricing_id)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    "Please select a valid pricing option."
                ) from exc

            pricing = db.session.get(
                ExperiencePricing,
                pricing_id,
            )

            if (
                pricing is None
                or pricing.experience_id != experience.id
                or not pricing.active
            ):
                raise ValueError(
                    "Please select a valid pricing option for this experience."
                )
        else:
            pricing = ExperienceBookingService.get_default_pricing(
                experience.id
            )

        if pricing is None:
            raise ValueError(
                "This experience does not currently have an active "
                "pricing option."
            )

        if guest_count < pricing.minimum_people:
            raise ValueError(
                f"This pricing option requires at least "
                f"{pricing.minimum_people} traveller(s)."
            )

        if (
            pricing.maximum_people is not None
            and guest_count > pricing.maximum_people
        ):
            raise ValueError(
                f"This pricing option allows a maximum of "
                f"{pricing.maximum_people} traveller(s)."
            )

        return pricing

    # -------------------------------------------------------------------------
    # Money
    # -------------------------------------------------------------------------

    @staticmethod
    def money(value):
        """Return a monetary Decimal rounded to two decimal places."""
        return Decimal(str(value or 0)).quantize(
            CENT,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def calculate_total(pricing, adults, children, infants=0):
        """
        Calculate the experience charge.

        Infants are free. Adults and children are chargeable.
        """
        counts = ExperienceBookingService.validate_guest_counts(
            adults=adults,
            children=children,
            infants=infants,
        )

        chargeable_guests = (
            counts["adults"] +
            counts["children"]
        )

        unit_price = ExperienceBookingService.money(
            pricing.price
        )

        return ExperienceBookingService.money(
            unit_price * chargeable_guests
        )

    # -------------------------------------------------------------------------
    # ExperienceBooking detail
    # -------------------------------------------------------------------------

    @staticmethod
    def build_booking_detail(
        *,
        experience,
        pricing,
        adults=1,
        children=0,
        infants=0,
        pickup_location=None,
        dropoff_location=None,
        customer_instructions=None,
    ):
        """
        Build an ExperienceBooking detail object.

        This method does not create the central Booking.
        """

        counts = ExperienceBookingService.validate_guest_counts(
            adults=adults,
            children=children,
            infants=infants,
        )

        guest_count = sum(counts.values())

        if pricing is None:
            raise ValueError(
                "A valid experience pricing option is required."
            )

        unit_price = ExperienceBookingService.money(
            pricing.price
        )

        currency = (
            pricing.currency or "KES"
        ).upper()

        return ExperienceBooking(
            experience=experience,
            pricing=pricing,
            experience_name_snapshot=experience.title,
            experience_code_snapshot=getattr(
                experience,
                "experience_code",
                None,
            ),
            description_snapshot=getattr(
                experience,
                "description",
                None,
            ),
            meeting_point_snapshot=getattr(
                experience,
                "meeting_point",
                None,
            ),
            location_snapshot=getattr(
                experience,
                "location",
                None,
            ),
            duration_snapshot=getattr(
                experience,
                "duration",
                None,
            ),
            pricing_name_snapshot=(
                getattr(
                    pricing,
                    "experience_level",
                    None,
                )
                or getattr(
                    pricing,
                    "name",
                    None,
                )
            ),
            price_basis="per_person",
            unit_price=unit_price,
            quantity=guest_count,
            currency=currency,
            pickup_location=(
                (pickup_location or "").strip() or None
            ),
            dropoff_location=(
                (dropoff_location or "").strip() or None
            ),
            customer_instructions=(
                (customer_instructions or "").strip() or None
            ),
        )

    @staticmethod
    def update_booking_detail(
        detail,
        *,
        experience=None,
        pricing=None,
        adults=None,
        children=None,
        infants=None,
        pickup_location=None,
        dropoff_location=None,
        customer_instructions=None,
    ):
        """
        Update an existing ExperienceBooking detail.

        Only supplied values are changed.
        """

        if detail is None:
            raise ValueError(
                "Experience booking details were not found."
            )

        if experience is not None:
            if not experience.active:
                raise ValueError(
                    "The selected experience is inactive."
                )

            detail.experience = experience
            detail.experience_id = experience.id
            detail.experience_name_snapshot = experience.title
            detail.experience_code_snapshot = getattr(
                experience,
                "experience_code",
                None,
            )
            detail.description_snapshot = getattr(
                experience,
                "description",
                None,
            )
            detail.meeting_point_snapshot = getattr(
                experience,
                "meeting_point",
                None,
            )
            detail.location_snapshot = getattr(
                experience,
                "location",
                None,
            )
            detail.duration_snapshot = getattr(
                experience,
                "duration",
                None,
            )

        if pricing is not None:
            if not pricing.active:
                raise ValueError(
                    "The selected pricing option is inactive."
                )

            if detail.experience_id != pricing.experience_id:
                raise ValueError(
                    "The selected pricing option does not belong "
                    "to the selected experience."
                )

            detail.pricing = pricing
            detail.pricing_id = pricing.id
            detail.pricing_name_snapshot = (
                getattr(
                    pricing,
                    "experience_level",
                    None,
                )
                or getattr(
                    pricing,
                    "name",
                    None,
                )
            )
            detail.unit_price = (
                ExperienceBookingService.money(
                    pricing.price
                )
            )
            detail.currency = (
                pricing.currency or "KES"
            ).upper()

        if (
            adults is not None
            or children is not None
            or infants is not None
        ):
            current_adults = (
                adults
                if adults is not None
                else detail.quantity
            )
            current_children = (
                children
                if children is not None
                else 0
            )
            current_infants = (
                infants
                if infants is not None
                else 0
            )

            counts = (
                ExperienceBookingService.validate_guest_counts(
                    adults=current_adults,
                    children=current_children,
                    infants=current_infants,
                )
            )

            guest_count = sum(counts.values())

            if detail.pricing:
                if guest_count < detail.pricing.minimum_people:
                    raise ValueError(
                        f"This pricing option requires at least "
                        f"{detail.pricing.minimum_people} traveller(s)."
                    )

                if (
                    detail.pricing.maximum_people is not None
                    and guest_count > detail.pricing.maximum_people
                ):
                    raise ValueError(
                        f"This pricing option allows a maximum of "
                        f"{detail.pricing.maximum_people} traveller(s)."
                    )

            detail.quantity = guest_count

        if pickup_location is not None:
            detail.pickup_location = (
                pickup_location.strip()
                or None
            )

        if dropoff_location is not None:
            detail.dropoff_location = (
                dropoff_location.strip()
                or None
            )

        if customer_instructions is not None:
            detail.customer_instructions = (
                customer_instructions.strip()
                or None
            )

        return detail

    # -------------------------------------------------------------------------
    # Inquiry conversion
    # -------------------------------------------------------------------------

    @staticmethod
    def get_inquiry(inquiry_id):
        """Return an experience inquiry by ID."""
        if not inquiry_id:
            return None

        try:
            inquiry_id = int(inquiry_id)
        except (TypeError, ValueError, OverflowError):
            return None

        return db.session.get(
            ExperienceInquiry,
            inquiry_id,
        )

    @staticmethod
    def convert_inquiry_to_detail(
        inquiry,
        *,
        pricing=None,
        pickup_location=None,
        dropoff_location=None,
        customer_instructions=None,
    ):
        """
        Build ExperienceBooking details from an ExperienceInquiry.

        This does not create the central Booking.
        """

        if inquiry is None:
            raise ValueError(
                "Experience inquiry was not found."
            )

        experience = inquiry.experience

        if experience is None or not experience.active:
            raise ValueError(
                "The experience associated with this inquiry "
                "is no longer active."
            )

        counts = (
            ExperienceBookingService.validate_guest_counts(
                adults=inquiry.adults,
                children=inquiry.children,
                infants=inquiry.infants,
            )
        )

        guest_count = sum(counts.values())

        if pricing is None:
            pricing = (
                ExperienceBookingService.get_default_pricing(
                    experience.id
                )
            )

        pricing = ExperienceBookingService.validate_pricing(
            experience=experience,
            pricing_id=(
                pricing.id
                if pricing is not None
                else None
            ),
            guest_count=guest_count,
        )

        return ExperienceBookingService.build_booking_detail(
            experience=experience,
            pricing=pricing,
            adults=counts["adults"],
            children=counts["children"],
            infants=counts["infants"],
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            customer_instructions=(
                customer_instructions
                or inquiry.special_requests
            ),
        )

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    @staticmethod
    def save_detail(detail, commit=True):
        """Persist an ExperienceBooking detail."""
        if detail is None:
            raise ValueError(
                "Experience booking details are required."
            )

        db.session.add(detail)

        if commit:
            db.session.commit()

        return detail