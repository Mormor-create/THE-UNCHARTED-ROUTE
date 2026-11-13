"""
===============================================================================
The Uncharted Route
Experience Add-on Service
===============================================================================

Business logic for managing optional add-ons associated with experiences.

Examples

• Professional Photographer
• Bush Breakfast
• Luxury Land Cruiser Upgrade
• Airport Transfers
• Helicopter Transfer
• Champagne Picnic

The service layer keeps add-on management separate from routes and models.

Responsibilities

• Create add-ons
• Retrieve add-ons
• Update add-ons
• Activate / deactivate add-ons
• Delete add-ons
• Reorder add-ons
• Calculate add-on pricing
• Validate add-on availability
"""

from extensions import db
from app.models import ExperienceAddon


# =============================================================================
# Experience Add-on Service
# =============================================================================


class ExperienceAddonService:
    """
    Service layer for ExperienceAddon operations.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_addon(
        experience_id,
        name,
        price,
        short_description=None,
        description=None,
        currency="KES",
        pricing_type="Per Person",
        optional=True,
        available_online=True,
        display_order=0,
        active=True,
    ):
        """
        Create a new experiences add-on.
        """

        if not experience_id:
            raise ValueError(
                "Experience ID is required."
            )

        if not name or not name.strip():
            raise ValueError(
                "Add-on name is required."
            )

        if price is None:
            raise ValueError(
                "Add-on price is required."
            )

        if price < 0:
            raise ValueError(
                "Add-on price cannot be negative."
            )

        valid_pricing_types = {
            "Per Person",
            "Per Booking",
            "Per Vehicle",
            "Per Group",
        }

        if pricing_type not in valid_pricing_types:
            raise ValueError(
                "Invalid pricing type."
            )

        addon = ExperienceAddon(
            experience_id=experience_id,
            name=name.strip(),
            short_description=short_description,
            description=description,
            price=price,
            currency=currency,
            pricing_type=pricing_type,
            optional=optional,
            available_online=available_online,
            display_order=display_order,
            active=active,
        )

        db.session.add(addon)
        db.session.commit()

        return addon

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_addon(addon_id):
        """
        Retrieve an add-on by ID.
        """

        return db.session.get(
            ExperienceAddon,
            addon_id
        )

    # =========================================================================
    # Retrieve All
    # =========================================================================

    @staticmethod
    def get_all_addons(
        experience_id=None,
        active_only=False,
        online_only=False,
    ):
        """
        Retrieve add-ons.

        Optional filters:

        experience_id
        active_only
        online_only
        """

        query = ExperienceAddon.query

        if experience_id is not None:
            query = query.filter_by(
                experience_id=experience_id
            )

        if active_only:
            query = query.filter_by(
                active=True
            )

        if online_only:
            query = query.filter_by(
                available_online=True
            )

        return query.order_by(
            ExperienceAddon.display_order.asc(),
            ExperienceAddon.id.asc()
        ).all()

    # =========================================================================
    # Retrieve Online Add-ons
    # =========================================================================

    @staticmethod
    def get_online_addons(experience_id):
        """
        Retrieve add-ons currently available for online booking.
        """

        return ExperienceAddonService.get_all_addons(
            experience_id=experience_id,
            active_only=True,
            online_only=True,
        )

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_addon(
        addon_id,
        name=None,
        price=None,
        short_description=None,
        description=None,
        currency=None,
        pricing_type=None,
        optional=None,
        available_online=None,
        display_order=None,
    ):
        """
        Update an existing add-on.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        if name is not None:

            if not name.strip():
                raise ValueError(
                    "Add-on name cannot be empty."
                )

            addon.name = name.strip()

        if price is not None:

            if price < 0:
                raise ValueError(
                    "Add-on price cannot be negative."
                )

            addon.price = price

        if short_description is not None:
            addon.short_description = short_description

        if description is not None:
            addon.description = description

        if currency is not None:
            addon.currency = currency

        if pricing_type is not None:

            valid_pricing_types = {
                "Per Person",
                "Per Booking",
                "Per Vehicle",
                "Per Group",
            }

            if pricing_type not in valid_pricing_types:
                raise ValueError(
                    "Invalid pricing type."
                )

            addon.pricing_type = pricing_type

        if optional is not None:
            addon.optional = optional

        if available_online is not None:
            addon.available_online = available_online

        if display_order is not None:
            addon.display_order = display_order

        db.session.commit()

        return addon

    # =========================================================================
    # Activate
    # =========================================================================

    @staticmethod
    def activate_addon(addon_id):
        """
        Activate an add-on.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        addon.active = True

        db.session.commit()

        return addon

    # =========================================================================
    # Deactivate
    # =========================================================================

    @staticmethod
    def deactivate_addon(addon_id):
        """
        Deactivate an add-on.

        Existing booking records are not modified.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        addon.active = False
        addon.available_online = False

        db.session.commit()

        return addon

    # =========================================================================
    # Toggle Online Availability
    # =========================================================================

    @staticmethod
    def set_online_availability(
        addon_id,
        available=True,
    ):
        """
        Enable or disable online availability.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        if available and not addon.active:
            raise ValueError(
                "Cannot make an inactive add-on available online."
            )

        addon.available_online = available

        db.session.commit()

        return addon

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete_addon(addon_id):
        """
        Delete an add-on.

        This should generally be used only when the add-on has
        never been used in a booking.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        if addon.booking_addons.count() > 0:
            raise ValueError(
                "Cannot delete an add-on that has been used in a booking. "
                "Deactivate it instead."
            )

        db.session.delete(addon)
        db.session.commit()

        return True

    # =========================================================================
    # Reorder
    # =========================================================================

    @staticmethod
    def reorder_addons(
        experience_id,
        addon_ids,
    ):
        """
        Reorder add-ons for an experiences.

        addon_ids should be supplied in the desired display order.
        """

        if not isinstance(addon_ids, (list, tuple)):
            raise ValueError(
                "addon_ids must be a list or tuple."
            )

        addons = ExperienceAddon.query.filter(
            ExperienceAddon.experience_id == experience_id,
            ExperienceAddon.id.in_(addon_ids),
        ).all()

        addon_map = {
            addon.id: addon
            for addon in addons
        }

        for position, addon_id in enumerate(addon_ids):
            addon = addon_map.get(addon_id)

            if addon:
                addon.display_order = position

        db.session.commit()

        return ExperienceAddonService.get_all_addons(
            experience_id=experience_id
        )

    # =========================================================================
    # Pricing
    # =========================================================================

    @staticmethod
    def calculate_price(
        addon_id,
        quantity=1,
        guests=1,
    ):
        """
        Calculate the total price for an add-on.

        Pricing behaviour depends on pricing_type:

        Per Person
            price × guests × quantity

        Per Booking
            price × quantity

        Per Vehicle
            price × quantity

        Per Group
            price × quantity
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            raise ValueError(
                "Experience add-on not found."
            )

        if quantity < 1:
            raise ValueError(
                "Quantity must be at least 1."
            )

        if guests < 1:
            raise ValueError(
                "Guest count must be at least 1."
            )

        if addon.pricing_type == "Per Person":
            return addon.price * guests * quantity

        return addon.price * quantity

    # =========================================================================
    # Availability
    # =========================================================================

    @staticmethod
    def is_available_online(addon_id):
        """
        Determine whether an add-on can currently be selected online.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            return False

        return (
            addon.active
            and addon.available_online
        )

    # =========================================================================
    # Bulk Deactivation
    # =========================================================================

    @staticmethod
    def deactivate_experience_addons(experience_id):
        """
        Deactivate all add-ons belonging to an experiences.
        """

        addons = ExperienceAddon.query.filter_by(
            experience_id=experience_id
        ).all()

        for addon in addons:
            addon.active = False
            addon.available_online = False

        db.session.commit()

        return addons

    # =========================================================================
    # Representation Helper
    # =========================================================================

    @staticmethod
    def get_addon_summary(addon_id):
        """
        Return a simple operational summary for an add-on.
        """

        addon = ExperienceAddonService.get_addon(
            addon_id
        )

        if not addon:
            return None

        return {
            "id": addon.id,
            "experience_id": addon.experience_id,
            "name": addon.name,
            "price": addon.price,
            "currency": addon.currency,
            "pricing_type": addon.pricing_type,
            "optional": addon.optional,
            "available_online": addon.available_online,
            "active": addon.active,
            "formatted_price": addon.formatted_price,
        }