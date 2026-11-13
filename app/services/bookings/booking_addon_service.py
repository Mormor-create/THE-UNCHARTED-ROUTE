"""
===============================================================================
The Uncharted Route
Booking Add-on Service
===============================================================================
Business logic for booking add-ons.
This service handles:

- Adding an ExperienceAddon to a booking
- Creating a pricing snapshot
- Updating an existing booking add-on
- Cancelling an add-on
- Confirming an add-on
- Calculating add-on totals
- Synchronizing booking add-on totals
The service layer keeps booking add-on business logic out of route handlers.
"""
# =============================================================================
# The Uncharted Route
# Booking Add-on Service
# =============================================================================
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from app.models.booking import Booking
from app.models.booking_addon import BookingAddon
from app.models.experience_addon import ExperienceAddon


CENT = Decimal("0.01")


class BookingAddonService:
    """Business logic for add-ons attached to central booking."""

    @staticmethod
    def money(value):
        try:
            return Decimal(str(value if value is not None else 0)).quantize(
                CENT,
                rounding=ROUND_HALF_UP,
            )
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Enter a valid monetary amount.")

    @staticmethod
    def calculate_line_total(quantity, unit_price, discount, tax):
        quantity = int(quantity or 0)
        unit_price = BookingAddonService.money(unit_price)
        discount = BookingAddonService.money(discount)
        tax = BookingAddonService.money(tax)

        if quantity < 1:
            raise ValueError("Quantity must be at least one.")
        if unit_price < 0 or discount < 0 or tax < 0:
            raise ValueError("Prices, discounts and taxes cannot be negative.")

        gross = (unit_price * quantity).quantize(CENT)
        if discount > gross:
            raise ValueError("Discount cannot exceed the gross amount.")

        net = gross - discount
        if tax > net:
            raise ValueError("Tax cannot exceed the discounted amount.")

        return (net + tax).quantize(CENT)

    @staticmethod
    def populate_form_choices(form):
        addons = (
            ExperienceAddon.query
            .order_by(ExperienceAddon.id.desc())
            .all()
        )

        choices = [(0, "No catalogue link")]

        for addon in addons:
            label = (
                getattr(addon, "name", None)
                or getattr(addon, "title", None)
                or f"Experience add-on #{addon.id}"
            )
            choices.append((addon.id, label))

        form.experience_addon_id.choices = choices

    @staticmethod
    def list_addons(search=None, status=None, booking_id=None):
        query = BookingAddon.query.join(
            Booking,
            BookingAddon.booking_id == Booking.id,
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Booking.booking_reference.ilike(term),
                    Booking.first_name.ilike(term),
                    Booking.last_name.ilike(term),
                    Booking.email.ilike(term),
                    BookingAddon.name_snapshot.ilike(term),
                    BookingAddon.addon_code.ilike(term),
                )
            )

        if status:
            query = query.filter(BookingAddon.status == status)

        if booking_id:
            query = query.filter(BookingAddon.booking_id == booking_id)

        return query.order_by(BookingAddon.created_at.desc()).all()

    @staticmethod
    def get_addon(addon_id):
        return db.session.get(BookingAddon, addon_id)

    @staticmethod
    def get_booking(booking_id):
        return db.session.get(Booking, booking_id)

    @staticmethod
    def _find_duplicate(booking_id, addon_code, experience_addon_id,
                        exclude_id=None):
        """
        Prevent duplicate active add-ons for the same booking.

        A catalogue-linked add-on is matched by its catalogue ID. Shared
        catalogue items without that link are matched by add-on code.
        """
        query = BookingAddon.query.filter(
            BookingAddon.booking_id == booking_id,
            BookingAddon.status != "cancelled",
        )

        if exclude_id is not None:
            query = query.filter(BookingAddon.id != exclude_id)

        if experience_addon_id:
            query = query.filter(
                BookingAddon.experience_addon_id == experience_addon_id
            )
        elif addon_code:
            query = query.filter(BookingAddon.addon_code == addon_code)
        else:
            # Without a catalogue reference or code, there is no stable
            # identity with which to detect a duplicate.
            return None

        return query.first()

    @staticmethod
    def _validate_form(form, booking_id, exclude_id=None):
        booking = BookingAddonService.get_booking(booking_id)
        if booking is None:
            raise ValueError("The selected booking does not exist.")

        experience_addon_id = form.experience_addon_id.data or None
        addon_code = (form.addon_code.data or "").strip() or None

        if experience_addon_id:
            catalogue_addon = db.session.get(
                ExperienceAddon,
                experience_addon_id,
            )
            if catalogue_addon is None:
                raise ValueError("The selected catalogue add-on was not found.")

        duplicate = BookingAddonService._find_duplicate(
            booking_id=booking_id,
            addon_code=addon_code,
            experience_addon_id=experience_addon_id,
            exclude_id=exclude_id,
        )

        if duplicate:
            raise ValueError(
                "This add-on is already attached to this booking. "
                "Edit the existing line item instead."
            )

        line_total = BookingAddonService.calculate_line_total(
            form.quantity.data,
            form.unit_price.data,
            form.discount_amount.data,
            form.tax_amount.data,
        )

        return booking, experience_addon_id, addon_code, line_total

    @staticmethod
    def _apply_form(addon, form, experience_addon_id, addon_code, line_total):
        addon.addon_code = addon_code
        addon.addon_type = form.addon_type.data
        addon.experience_addon_id = experience_addon_id

        addon.name_snapshot = form.name_snapshot.data.strip()
        addon.description_snapshot = form.description_snapshot.data
        addon.pricing_basis = form.pricing_basis.data

        addon.quantity = form.quantity.data
        addon.unit_price = BookingAddonService.money(form.unit_price.data)
        addon.currency = form.currency.data
        addon.discount_amount = BookingAddonService.money(
            form.discount_amount.data
        )
        addon.tax_amount = BookingAddonService.money(form.tax_amount.data)
        addon.line_total = line_total

        addon.status = form.status.data
        addon.cancellation_reason = form.cancellation_reason.data
        addon.internal_notes = form.internal_notes.data

        if addon.status == "fulfilled" and addon.fulfilled_at is None:
            addon.fulfilled_at = datetime.utcnow()

        if addon.status == "cancelled":
            if addon.cancelled_at is None:
                addon.cancelled_at = datetime.utcnow()
        else:
            addon.cancelled_at = None
            addon.cancellation_reason = None

    @staticmethod
    def create_addon(booking_id, form, added_by_user=None):
        try:
            booking, experience_addon_id, addon_code, line_total = (
                BookingAddonService._validate_form(booking_id, form)
            )

            addon = BookingAddon(booking_id=booking.id)
            BookingAddonService._apply_form(
                addon,
                form,
                experience_addon_id,
                addon_code,
                line_total,
            )

            if added_by_user is not None:
                addon.added_by = added_by_user

            db.session.add(addon)
            db.session.flush()

            return addon

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_addon(addon, form):
        try:
            booking, experience_addon_id, addon_code, line_total = (
                BookingAddonService._validate_form(
                    addon.booking_id,
                    form,
                    exclude_id=addon.id,
                )
            )

            if addon.status in ("fulfilled", "cancelled"):
                raise ValueError(
                    "Fulfilled or cancelled add-ons cannot be edited. "
                    "Preserve the record and create a separate adjustment "
                    "workflow if a correction is required."
                )

            BookingAddonService._apply_form(
                addon,
                form,
                experience_addon_id,
                addon_code,
                line_total,
            )

            db.session.flush()
            return addon

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def change_status(addon, status, cancellation_reason=None,
                      internal_notes=None):
        allowed = {"selected", "confirmed", "fulfilled", "cancelled"}

        if status not in allowed:
            raise ValueError("Invalid add-on status.")

        if addon.status == "cancelled" and status != "cancelled":
            raise ValueError(
                "A cancelled add-on cannot be reactivated. "
                "Create a new line item if the customer repurchases it."
            )

        if addon.status == "fulfilled" and status != "fulfilled":
            raise ValueError("A fulfilled add-on cannot be reverted.")

        addon.status = status

        if status == "fulfilled" and addon.fulfilled_at is None:
            addon.fulfilled_at = datetime.utcnow()

        if status == "cancelled":
            addon.cancelled_at = datetime.utcnow()
            addon.cancellation_reason = cancellation_reason
        else:
            addon.cancelled_at = None
            addon.cancellation_reason = None

        if internal_notes:
            existing = addon.internal_notes or ""
            addon.internal_notes = (
                f"{existing}\n{internal_notes}".strip()
                if existing else internal_notes
            )

        return addon

    @staticmethod
    def sync_booking_addon_total(booking):
        """
        Recalculate the central booking add-on total from non-cancelled lines.

        Call this only if Booking.addon_total is intended to be the sum of
        these line items in your application's financial model.
        """
        total = Decimal("0.00")

        for addon in booking.addons:
            if addon.status != "cancelled":
                total += BookingAddonService.money(addon.line_total)

        booking.addon_total = total.quantize(CENT)
        return booking.addon_total