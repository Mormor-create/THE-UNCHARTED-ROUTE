
"""
Shared Add-on Catalogue Service
"""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import or_

from extensions import db
from app.models.addon_catalogue import AddonCatalogue


class AddonCatalogueService:
    @staticmethod
    def slugify(value):
        value = (value or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @staticmethod
    def populate_form_choices(form):
        # Choices are declared on the form; retained as a common hook
        # for future Media Library and related-record choices.
        return form

    @staticmethod
    def list_addons(
        search=None,
        category=None,
        service_type=None,
        active=None,
        page=1,
        per_page=20,
    ):
        query = AddonCatalogue.query

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AddonCatalogue.name.ilike(term),
                    AddonCatalogue.code.ilike(term),
                    AddonCatalogue.slug.ilike(term),
                    AddonCatalogue.short_description.ilike(term),
                )
            )

        if category:
            query = query.filter(AddonCatalogue.category == category)

        if service_type:
            # JSON membership syntax differs between database engines.
            # This expression is supported by SQLite JSON and PostgreSQL
            # JSONB-compatible deployments; verify for your DB dialect.
            query = query.filter(
                AddonCatalogue.applicable_services.contains([service_type])
            )

        if active in (True, False):
            query = query.filter(AddonCatalogue.active.is_(active))

        return query.order_by(
            AddonCatalogue.display_order.asc(),
            AddonCatalogue.name.asc(),
        ).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_addon(addon_id):
        return db.session.get(AddonCatalogue, addon_id)

    @staticmethod
    def get_by_code(code):
        return AddonCatalogue.query.filter_by(
            code=(code or "").strip()
        ).first()

    @staticmethod
    def validate_catalogue_data(data, addon_id=None):
        code = (data.get("code") or "").strip()
        slug = (data.get("slug") or "").strip().lower()

        if not code:
            raise ValueError("An add-on code is required.")

        duplicate_code = AddonCatalogue.query.filter(
            AddonCatalogue.code == code
        )
        duplicate_slug = AddonCatalogue.query.filter(
            AddonCatalogue.slug == slug
        )

        if addon_id is not None:
            duplicate_code = duplicate_code.filter(
                AddonCatalogue.id != addon_id
            )
            duplicate_slug = duplicate_slug.filter(
                AddonCatalogue.id != addon_id
            )

        if duplicate_code.first():
            raise ValueError("That add-on code is already in use.")

        if duplicate_slug.first():
            raise ValueError("That slug is already in use.")

        services = data.get("applicable_services") or []
        invalid = set(services) - set(AddonCatalogue.SERVICE_TYPES)
        if invalid:
            raise ValueError("One or more selected services are invalid.")

        if not services:
            raise ValueError("Select at least one applicable service.")

        if data.get("category") not in AddonCatalogue.CATEGORIES:
            raise ValueError("Select a valid add-on category.")

        if data.get("pricing_basis") not in AddonCatalogue.PRICING_BASES:
            raise ValueError("Select a valid pricing basis.")

        if data.get("currency") not in AddonCatalogue.CURRENCIES:
            raise ValueError("Select a supported currency.")

        price = Decimal(str(data.get("unit_price", 0)))
        if not price.is_finite() or price < 0:
            raise ValueError("Price must be a valid non-negative amount.")

        minimum = data.get("minimum_quantity") or 1
        maximum = data.get("maximum_quantity")
        inventory = data.get("available_quantity")

        if minimum < 1:
            raise ValueError("Minimum quantity must be at least one.")
        if maximum is not None and maximum < minimum:
            raise ValueError(
                "Maximum quantity cannot be less than minimum quantity."
            )
        if inventory is not None and inventory < 0:
            raise ValueError("Inventory cannot be negative.")

        start = data.get("available_from")
        end = data.get("available_until")
        if start and end and end < start:
            raise ValueError("Availability end date precedes start date.")

        return True

    @staticmethod
    def _apply(addon, data):
        addon.code = data["code"].strip()
        addon.name = data["name"].strip()
        addon.slug = (
            data.get("slug") or AddonCatalogueService.slugify(data["name"])
        ).strip().lower()
        addon.short_description = data.get("short_description") or None
        addon.description = data.get("description") or None
        addon.category = data["category"]
        addon.applicable_services = list(data["applicable_services"] or [])
        addon.pricing_basis = data["pricing_basis"]
        addon.unit_price = Decimal(str(data["unit_price"])).quantize(
            Decimal("0.01")
        )
        addon.currency = data["currency"]
        addon.minimum_quantity = data.get("minimum_quantity") or 1
        addon.maximum_quantity = data.get("maximum_quantity")
        addon.available_quantity = data.get("available_quantity")
        addon.available_from = data.get("available_from")
        addon.available_until = data.get("available_until")
        addon.image_url = data.get("image_url") or None
        addon.is_optional = bool(data.get("is_optional"))
        addon.can_be_booked_independently = bool(
            data.get("can_be_booked_independently")
        )
        addon.requires_confirmation = bool(
            data.get("requires_confirmation")
        )
        addon.featured = bool(data.get("featured"))
        addon.active = bool(data.get("active"))
        addon.display_order = data.get("display_order") or 0

    @classmethod
    def create_addon(cls, data):
        cls.validate_catalogue_data(data)
        addon = AddonCatalogue()
        cls._apply(addon, data)
        db.session.add(addon)
        db.session.flush()
        return addon

    @classmethod
    def update_addon(cls, addon, data):
        cls.validate_catalogue_data(data, addon_id=addon.id)
        cls._apply(addon, data)
        db.session.flush()
        return addon

    @staticmethod
    def set_active(addon, active):
        addon.active = bool(active)
        db.session.flush()
        return addon

    @staticmethod
    def is_available(addon, service_type, quantity=1, on_date=None):
        if not addon or not addon.active:
            return False
        if service_type not in (addon.applicable_services or []):
            return False
        if quantity < addon.minimum_quantity:
            return False
        if (
            addon.maximum_quantity is not None
            and quantity > addon.maximum_quantity
        ):
            return False
        if (
            addon.available_quantity is not None
            and quantity > addon.available_quantity
        ):
            return False

        on_date = on_date or date.today()
        if addon.available_from and on_date < addon.available_from:
            return False
        if addon.available_until and on_date > addon.available_until:
            return False

        return True
