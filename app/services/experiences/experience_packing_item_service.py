"""
===============================================================================
The Uncharted Route
Experience Packing Item Service
===============================================================================

Business logic for managing recommended packing items associated with
experiences.

Responsibilities
-----------------

• Create packing items
• Retrieve packing items
• Update packing items
• Delete packing items
• Activate / deactivate packing items
• Mark items as required or recommended
• Reorder packing items
• Retrieve items by category
• Retrieve required items
• Retrieve recommended items
• Retrieve active packing items
"""

from app.models import ExperiencePackingItem
from extensions import db


# =============================================================================
# Experience Packing Item Service
# =============================================================================

class ExperiencePackingItemService:
    """
    Service layer for ExperiencePackingItem operations.
    """

    # =========================================================================
    # CREATE
    # =========================================================================

    @staticmethod
    def create_packing_item(
        experience_id,
        name,
        description=None,
        category="General",
        icon="backpack",
        recommended=True,
        required=False,
        display_order=0,
        active=True
    ):
        """
        Create a new packing item for an experiences.
        """

        if not name or not name.strip():
            raise ValueError("Packing item name is required.")

        if required:
            recommended = True

        packing_item = ExperiencePackingItem(
            experience_id=experience_id,
            name=name.strip(),
            description=description,
            category=category,
            icon=icon,
            recommended=recommended,
            required=required,
            display_order=display_order,
            active=active
        )

        db.session.add(packing_item)
        db.session.commit()

        return packing_item

    # =========================================================================
    # GET BY ID
    # =========================================================================

    @staticmethod
    def get_packing_item(packing_item_id):
        """
        Retrieve a packing item by ID.
        """

        return (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

    # =========================================================================
    # GET BY EXPERIENCE
    # =========================================================================

    @staticmethod
    def get_experience_packing_items(
        experience_id,
        active_only=True
    ):
        """
        Retrieve packing items belonging to an experiences.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(experience_id=experience_id)
        )

        if active_only:
            query = query.filter_by(active=True)

        return (
            query
            .order_by(
                ExperiencePackingItem.display_order.asc(),
                ExperiencePackingItem.id.asc()
            )
            .all()
        )

    # =========================================================================
    # GET BY CATEGORY
    # =========================================================================

    @staticmethod
    def get_by_category(
        experience_id,
        category,
        active_only=True
    ):
        """
        Retrieve packing items belonging to a specific category.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(
                experience_id=experience_id,
                category=category
            )
        )

        if active_only:
            query = query.filter_by(active=True)

        return (
            query
            .order_by(
                ExperiencePackingItem.display_order.asc(),
                ExperiencePackingItem.id.asc()
            )
            .all()
        )

    # =========================================================================
    # REQUIRED ITEMS
    # =========================================================================

    @staticmethod
    def get_required_items(
        experience_id,
        active_only=True
    ):
        """
        Retrieve required packing items for an experiences.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(
                experience_id=experience_id,
                required=True
            )
        )

        if active_only:
            query = query.filter_by(active=True)

        return (
            query
            .order_by(
                ExperiencePackingItem.display_order.asc(),
                ExperiencePackingItem.id.asc()
            )
            .all()
        )

    # =========================================================================
    # RECOMMENDED ITEMS
    # =========================================================================

    @staticmethod
    def get_recommended_items(
        experience_id,
        active_only=True
    ):
        """
        Retrieve recommended packing items for an experiences.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(
                experience_id=experience_id,
                recommended=True
            )
        )

        if active_only:
            query = query.filter_by(active=True)

        return (
            query
            .order_by(
                ExperiencePackingItem.display_order.asc(),
                ExperiencePackingItem.id.asc()
            )
            .all()
        )

    # =========================================================================
    # UPDATE
    # =========================================================================

    @staticmethod
    def update_packing_item(
        packing_item_id,
        **kwargs
    ):
        """
        Update an existing packing item.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return None

        allowed_fields = {
            "name",
            "description",
            "category",
            "icon",
            "recommended",
            "required",
            "display_order",
            "active"
        }

        for field, value in kwargs.items():

            if field not in allowed_fields:
                continue

            if field == "name" and value:
                value = value.strip()

            setattr(
                packing_item,
                field,
                value
            )

        if packing_item.required:
            packing_item.recommended = True

        db.session.commit()

        return packing_item

    # =========================================================================
    # ACTIVATE
    # =========================================================================

    @staticmethod
    def activate(packing_item_id):
        """
        Activate a packing item.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return None

        packing_item.active = True

        db.session.commit()

        return packing_item

    # =========================================================================
    # DEACTIVATE
    # =========================================================================

    @staticmethod
    def deactivate(packing_item_id):
        """
        Deactivate a packing item without deleting it.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return None

        packing_item.active = False

        db.session.commit()

        return packing_item

    # =========================================================================
    # MARK REQUIRED
    # =========================================================================

    @staticmethod
    def mark_required(packing_item_id):
        """
        Mark a packing item as required.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return None

        packing_item.required = True
        packing_item.recommended = True

        db.session.commit()

        return packing_item

    # =========================================================================
    # MARK OPTIONAL
    # =========================================================================

    @staticmethod
    def mark_optional(packing_item_id):
        """
        Mark a packing item as optional.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return None

        packing_item.required = False

        db.session.commit()

        return packing_item

    # =========================================================================
    # DELETE
    # =========================================================================

    @staticmethod
    def delete_packing_item(packing_item_id):
        """
        Permanently delete a packing item.
        """

        packing_item = (
            ExperiencePackingItem.query
            .filter_by(id=packing_item_id)
            .first()
        )

        if not packing_item:
            return False

        db.session.delete(packing_item)
        db.session.commit()

        return True

    # =========================================================================
    # REORDER
    # =========================================================================

    @staticmethod
    def reorder_items(
        experience_id,
        item_order
    ):
        """
        Reorder packing items.

        Parameters
        ----------
        experience_id : int
            Experience whose items are being reordered.

        item_order : list[int]
            List of packing item IDs in the desired order.

        Example
        -------
        [5, 2, 8, 1]
        """

        items = (
            ExperiencePackingItem.query
            .filter(
                ExperiencePackingItem.experience_id == experience_id,
                ExperiencePackingItem.id.in_(item_order)
            )
            .all()
        )

        item_map = {
            item.id: item
            for item in items
        }

        for position, item_id in enumerate(item_order):
            item = item_map.get(item_id)

            if item:
                item.display_order = position

        db.session.commit()

        return (
            ExperiencePackingItem.query
            .filter_by(experience_id=experience_id)
            .order_by(
                ExperiencePackingItem.display_order.asc(),
                ExperiencePackingItem.id.asc()
            )
            .all()
        )

    # =========================================================================
    # COUNT
    # =========================================================================

    @staticmethod
    def count_items(
        experience_id,
        active_only=True
    ):
        """
        Return the number of packing items for an experiences.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(experience_id=experience_id)
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.count()

    # =========================================================================
    # COUNT REQUIRED
    # =========================================================================

    @staticmethod
    def count_required_items(
        experience_id,
        active_only=True
    ):
        """
        Return the number of required packing items.
        """

        query = (
            ExperiencePackingItem.query
            .filter_by(
                experience_id=experience_id,
                required=True
            )
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.count()