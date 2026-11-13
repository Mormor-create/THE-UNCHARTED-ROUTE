"""
===============================================================================
The Uncharted Route
Experience Pricing Service
===============================================================================
Business logic for managing experiences pricing tiers.
The ExperiencePricing model stores individual pricing options for experiences,
including:
• Experience level
• Group size
• Price
• Currency
• Notes
• Display order
• Active status
This service provides a centralized interface for creating, updating,
retrieving, and managing experiences pricing.
Typical pricing levels:
• Explorer
• Signature
• Luxury
• Bespoke
"""
from extensions import db
# =============================================================================
# Experience Pricing Service
# =============================================================================
class ExperiencePricingService:
    """
    Service responsible for experiences pricing management.
    """
    # =========================================================================
    # Model Loader
    # =========================================================================
    @staticmethod
    def _get_model():
        """
        Lazily import the ExperiencePricing model.
        Lazy importing helps prevent circular import issues during
        application startup.
        """
        from app.models.experience_pricing import ExperiencePricing
        return ExperiencePricing

    # =========================================================================
    # Get Pricing
    # =========================================================================
    def get_by_id(self, pricing_id):
        """
        Retrieve a pricing record by ID.
        Returns
        -------
        ExperiencePricing or None
        """
        if not pricing_id:
            return None
        ExperiencePricing = self._get_model()
        return ExperiencePricing.query.get(pricing_id)

    # =========================================================================
    # Get All Pricing For Experience
    # =========================================================================
    def get_for_experience(
        self,
        experience_id,
        active_only=True,):
        """
        Return pricing options belonging to an experiences.
        Pricing is ordered by display order and then by minimum
        group size.
        """
        if not experience_id:
            return []

        ExperiencePricing = self._get_model()
        query = ExperiencePricing.query.filter_by(experience_id=experience_id)
        if active_only:
            query = query.filter_by(
                active=True)

        return query.order_by(
            ExperiencePricing.display_order.asc(),
            ExperiencePricing.minimum_people.asc(),
            ExperiencePricing.id.asc(),).all()

    # =========================================================================
    # Get By Experience Level
    # =========================================================================
    def get_by_level(
        self,
        experience_id,
        experience_level,
        active_only=True,):
        """
        Retrieve pricing options for a specific experiences level.
        Examples
        --------
        Explorer
        Signature
        Luxury
        Bespoke
        """
        if not experience_id or not experience_level:
            return []
        ExperiencePricing = self._get_model()
        query = ExperiencePricing.query.filter_by(
            experience_id=experience_id,
            experience_level=experience_level,)
        if active_only:
            query = query.filter_by(
                active=True)

        return query.order_by(ExperiencePricing.minimum_people.asc()).all()

    # =========================================================================
    # Get Pricing For Group Size
    # =========================================================================
    def get_for_group_size(
        self,
        experience_id,
        people,
        experience_level=None,):
        """
        Find the most appropriate pricing tier for a given group size.
        A pricing record matches when:
            minimum_people <= people
        and either:
            maximum_people is NULL
        or:
            people <= maximum_people
        When multiple records match, the most specific matching range
        is preferred.
        """
        if not experience_id:
            return None

        if not people or people < 1:
            raise ValueError("Number of people must be at least 1.")

        ExperiencePricing = self._get_model()
        query = ExperiencePricing.query.filter(
            ExperiencePricing.experience_id == experience_id,
            ExperiencePricing.active.is_(True),
            ExperiencePricing.minimum_people <= people,)
        if experience_level:
            query = query.filter(
                ExperiencePricing.experience_level
                == experience_level)

        matching = query.order_by(
            ExperiencePricing.minimum_people.desc(),
            ExperiencePricing.id.asc(),).all()
        for pricing in matching:
            if (
                pricing.maximum_people is None
                or people <= pricing.maximum_people
            ):
                return pricing
        return None

    # =========================================================================
    # Get Lowest Price
    # =========================================================================
    def get_lowest_price(
        self,
        experience_id,
        active_only=True,):
        """
        Return the lowest pricing option for an experiences.
        """
        if not experience_id:
            return None
        ExperiencePricing = self._get_model()
        query = ExperiencePricing.query.filter_by(experience_id=experience_id)
        if active_only:
            query = query.filter_by(active=True)
        return query.order_by(
            ExperiencePricing.price.asc()).first()

    # =========================================================================
    # Get Highest Price
    # =========================================================================
    def get_highest_price(
        self,
        experience_id,
        active_only=True,):
        """
        Return the highest pricing option for an experiences.
        """
        if not experience_id:
            return None
        ExperiencePricing = self._get_model()
        query = ExperiencePricing.query.filter_by(
            experience_id=experience_id)
        if active_only:
            query = query.filter_by(active=True)
        return query.order_by(ExperiencePricing.price.desc()).first()

    # =========================================================================
    # Create Pricing
    # =========================================================================
    def create(
        self,
        experience_id,
        experience_level,
        price,
        minimum_people=1,
        maximum_people=None,
        currency="KES",
        notes=None,
        display_order=0,
        active=True,
        commit=True,):
        """
        Create a new pricing tier.
        """

        if not experience_id:
            raise ValueError(
                "Experience ID is required."
            )

        if not experience_level:
            raise ValueError(
                "Experience level is required."
            )

        if price is None:
            raise ValueError(
                "Price is required."
            )

        if price < 0:
            raise ValueError(
                "Price cannot be negative."
            )

        if minimum_people < 1:
            raise ValueError(
                "Minimum people must be at least 1."
            )

        if (
            maximum_people is not None
            and maximum_people < minimum_people
        ):
            raise ValueError(
                "Maximum people cannot be less than minimum people."
            )

        ExperiencePricing = self._get_model()

        pricing = ExperiencePricing(
            experience_id=experience_id,
            experience_level=experience_level.strip(),
            minimum_people=minimum_people,
            maximum_people=maximum_people,
            price=price,
            currency=currency or "KES",
            notes=notes,
            display_order=display_order,
            active=active,
        )

        db.session.add(pricing)

        if commit:
            db.session.commit()

        return pricing

    # =========================================================================
    # Update Pricing
    # =========================================================================
    def update(
        self,
        pricing_id,
        experience_level=None,
        price=None,
        minimum_people=None,
        maximum_people=None,
        currency=None,
        notes=None,
        display_order=None,
        active=None,
        commit=True,):
        """
        Update an existing pricing tier.
        Only supplied values are changed.
        """

        pricing = self.get_by_id(pricing_id)
        if not pricing:
            return None
        if experience_level is not None:
            if not experience_level.strip():
                raise ValueError("Experience level cannot be empty.")
            pricing.experience_level = (
                experience_level.strip())
        if price is not None:
            if price < 0:
                raise ValueError("Price cannot be negative.")

            pricing.price = price
        if minimum_people is not None:
            if minimum_people < 1:
                raise ValueError("Minimum people must be at least 1.")

            pricing.minimum_people = minimum_people
        if maximum_people is not None:
            if maximum_people < pricing.minimum_people:
                raise ValueError("Maximum people cannot be less than minimum people.")

            pricing.maximum_people = maximum_people
        if currency is not None:
            pricing.currency = currency
        if notes is not None:
            pricing.notes = notes
        if display_order is not None:
            pricing.display_order = display_order
        if active is not None:
            pricing.active = active
        if commit:
            db.session.commit()
        return pricing

    # =========================================================================
    # Activate Pricing
    # =========================================================================
    def activate(
        self,
        pricing_id,
        commit=True,):
        """
        Activate a pricing tier.
        """
        pricing = self.get_by_id(pricing_id)
        if not pricing:
            return False
        pricing.active = True
        if commit:
            db.session.commit()
        return True

    # =========================================================================
    # Deactivate Pricing
    # =========================================================================
    def deactivate(
        self,
        pricing_id,
        commit=True,):
        """
        Deactivate a pricing tier without deleting it.
        """
        pricing = self.get_by_id(pricing_id)
        if not pricing:
            return False
        pricing.active = False
        if commit:
            db.session.commit()
        return True

    # =========================================================================
    # Delete Pricing
    # =========================================================================
    def delete(
        self,
        pricing_id,
        commit=True,):
        """
        Permanently delete a pricing tier.
        """
        pricing = self.get_by_id(pricing_id)
        if not pricing:
            return False
        db.session.delete(pricing)
        if commit:
            db.session.commit()
        return True

    # =========================================================================
    # Reorder Pricing
    # =========================================================================
    def reorder(
        self,
        pricing_id,
        display_order,
        commit=True,):
        """
        Change the display order of a pricing tier.
        """
        pricing = self.get_by_id(pricing_id)
        if not pricing:
            return False
        pricing.display_order = display_order
        if commit:
            db.session.commit()
        return True

    # =========================================================================
    # Pricing Summary
    # =========================================================================
    def get_summary(
        self,
        experience_id,):
        """
        Return a compact pricing summary for an experiences.
        Example structure:
        {
            "lowest": ExperiencePricing,
            "highest": ExperiencePricing,
            "pricing_options": [...],
            "count": 4
        }
        """
        pricing_options = self.get_for_experience(
            experience_id=experience_id,
            active_only=True,)
        if not pricing_options:
            return {
                "lowest": None,
                "highest": None,
                "pricing_options": [],
                "count": 0,}

        return {
            "lowest": min(
                pricing_options,
                key=lambda item: item.price,
            ),
            "highest": max(
                pricing_options,
                key=lambda item: item.price,
            ),
            "pricing_options": pricing_options,
            "count": len(pricing_options),}

    # =========================================================================
    # Group Pricing
    # =========================================================================
    def get_group_pricing(
        self,
        experience_id,
        experience_level=None,
        active_only=True,):
        """
        Return pricing grouped by group-size range.
        """
        pricing_options = self.get_for_experience(
            experience_id=experience_id,
            active_only=active_only,)

        if experience_level:
            pricing_options = [
                pricing
                for pricing in pricing_options
                if pricing.experience_level
                == experience_level]

        return pricing_options

# =============================================================================
# Service Instance
# =============================================================================
experience_pricing_service = ExperiencePricingService()

# =============================================================================
# Convenience Functions
# =============================================================================
def get_pricing(
    experience_id,
    active_only=True,):
    """
    Convenience wrapper for retrieving experiences pricing.
    """
    return experience_pricing_service.get_for_experience(
        experience_id=experience_id,
        active_only=active_only,)

def get_pricing_by_level(
    experience_id,
    experience_level,
    active_only=True,):
    """
    Convenience wrapper for retrieving pricing by experiences level.
    """
    return experience_pricing_service.get_by_level(
        experience_id=experience_id,
        experience_level=experience_level,
        active_only=active_only,)

def get_price_for_group(
    experience_id,
    people,
    experience_level=None,):
    """
    Convenience wrapper for finding the appropriate price for a group.
    """
    return experience_pricing_service.get_for_group_size(
        experience_id=experience_id,
        people=people,
        experience_level=experience_level,)

def create_pricing(
    experience_id,
    experience_level,
    price,
    minimum_people=1,
    maximum_people=None,
    currency="KES",
    notes=None,
    display_order=0,
    active=True,
    commit=True,):
    """
    Convenience wrapper for creating pricing.
    """
    return experience_pricing_service.create(
        experience_id=experience_id,
        experience_level=experience_level,
        price=price,
        minimum_people=minimum_people,
        maximum_people=maximum_people,
        currency=currency,
        notes=notes,
        display_order=display_order,
        active=active,
        commit=commit,)

def update_pricing(
    pricing_id,**kwargs,):
    """
    Convenience wrapper for updating pricing.
    """
    return experience_pricing_service.update(
        pricing_id,
        **kwargs,)

def delete_pricing(
    pricing_id,
    commit=True,):
    """
    Convenience wrapper for deleting pricing.
    """
    return experience_pricing_service.delete(
        pricing_id=pricing_id,
        commit=commit,)

def activate_pricing(
    pricing_id,commit=True,):
    """
    Convenience wrapper for activating pricing.
    """
    return experience_pricing_service.activate(
        pricing_id=pricing_id,
        commit=commit,)

def deactivate_pricing(
    pricing_id,commit=True,):
    """
    Convenience wrapper for deactivating pricing.
    """
    return experience_pricing_service.deactivate(
        pricing_id=pricing_id,
        commit=commit,)