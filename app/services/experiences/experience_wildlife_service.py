"""
===============================================================================
The Uncharted Route
Experience Wildlife Service
===============================================================================

Business logic for managing wildlife associated with experiences.

This service handles:

• Adding wildlife species to experiences
• Updating wildlife information
• Removing wildlife from experiences
• Retrieving wildlife for an experiences
• Filtering featured wildlife
• Filtering by sighting probability
• Reordering wildlife
• Activating/deactivating wildlife associations
• Retrieving Big Five species
• Retrieving endangered species
"""

from extensions import db

from app.models import ExperienceWildlife


# =============================================================================
# Experience Wildlife Service
# =============================================================================

class ExperienceWildlifeService:
    """
    Service layer for ExperienceWildlife operations.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def add_wildlife(
        experience_id,
        species_id,
        sighting_probability="Common",
        best_season=None,
        best_time_of_day=None,
        guide_notes=None,
        photography_notes=None,
        featured=False,
        display_order=0,
        active=True
    ):
        """
        Add a wildlife species to an experiences.
        """

        wildlife = ExperienceWildlife(
            experience_id=experience_id,
            species_id=species_id,
            sighting_probability=sighting_probability,
            best_season=best_season,
            best_time_of_day=best_time_of_day,
            guide_notes=guide_notes,
            photography_notes=photography_notes,
            featured=featured,
            display_order=display_order,
            active=active
        )

        db.session.add(wildlife)
        db.session.commit()

        return wildlife

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_by_id(wildlife_id):
        """
        Retrieve a wildlife association by ID.
        """

        return ExperienceWildlife.query.get(wildlife_id)

    # -------------------------------------------------------------------------

    @staticmethod
    def get_for_experience(
        experience_id,
        active_only=True
    ):
        """
        Retrieve wildlife associated with an experiences.
        """

        query = ExperienceWildlife.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.order_by(
            ExperienceWildlife.display_order.asc(),
            ExperienceWildlife.id.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_featured(
        experience_id,
        active_only=True
    ):
        """
        Retrieve featured wildlife for an experiences.
        """

        query = ExperienceWildlife.query.filter_by(
            experience_id=experience_id,
            featured=True
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.order_by(
            ExperienceWildlife.display_order.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_by_sighting_probability(
        experience_id,
        sighting_probability,
        active_only=True
    ):
        """
        Retrieve wildlife by sighting probability.
        """

        query = ExperienceWildlife.query.filter_by(
            experience_id=experience_id,
            sighting_probability=sighting_probability
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.order_by(
            ExperienceWildlife.display_order.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_big_five(
        experience_id,
        active_only=True
    ):
        """
        Retrieve Big Five species associated with an experiences.
        """

        wildlife = ExperienceWildlifeService.get_for_experience(
            experience_id=experience_id,
            active_only=active_only
        )

        return [
            item
            for item in wildlife
            if item.species and item.species.is_big_five
        ]

    # -------------------------------------------------------------------------

    @staticmethod
    def get_endangered(
        experience_id,
        active_only=True
    ):
        """
        Retrieve endangered species associated with an experiences.
        """

        wildlife = ExperienceWildlifeService.get_for_experience(
            experience_id=experience_id,
            active_only=active_only
        )

        return [
            item
            for item in wildlife
            if item.species and item.species.is_endangered
        ]

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update(
        wildlife_id,
        sighting_probability=None,
        best_season=None,
        best_time_of_day=None,
        guide_notes=None,
        photography_notes=None,
        featured=None,
        display_order=None,
        active=None
    ):
        """
        Update an experiences wildlife association.
        """

        wildlife = ExperienceWildlifeService.get_by_id(
            wildlife_id
        )

        if not wildlife:
            return None

        if sighting_probability is not None:
            wildlife.sighting_probability = sighting_probability

        if best_season is not None:
            wildlife.best_season = best_season

        if best_time_of_day is not None:
            wildlife.best_time_of_day = best_time_of_day

        if guide_notes is not None:
            wildlife.guide_notes = guide_notes

        if photography_notes is not None:
            wildlife.photography_notes = photography_notes

        if featured is not None:
            wildlife.featured = featured

        if display_order is not None:
            wildlife.display_order = display_order

        if active is not None:
            wildlife.active = active

        db.session.commit()

        return wildlife

    # =========================================================================
    # Featured Status
    # =========================================================================

    @staticmethod
    def set_featured(
        wildlife_id,
        featured=True
    ):
        """
        Set or remove featured status.
        """

        wildlife = ExperienceWildlifeService.get_by_id(
            wildlife_id
        )

        if not wildlife:
            return None

        wildlife.featured = featured

        db.session.commit()

        return wildlife

    # =========================================================================
    # Activation
    # =========================================================================

    @staticmethod
    def activate(wildlife_id):
        """
        Activate a wildlife association.
        """

        wildlife = ExperienceWildlifeService.get_by_id(
            wildlife_id
        )

        if not wildlife:
            return None

        wildlife.active = True

        db.session.commit()

        return wildlife

    # -------------------------------------------------------------------------

    @staticmethod
    def deactivate(wildlife_id):
        """
        Deactivate a wildlife association without deleting it.
        """

        wildlife = ExperienceWildlifeService.get_by_id(
            wildlife_id
        )

        if not wildlife:
            return None

        wildlife.active = False
        wildlife.featured = False

        db.session.commit()

        return wildlife

    # =========================================================================
    # Reordering
    # =========================================================================

    @staticmethod
    def reorder(
        experience_id,
        wildlife_ids
    ):
        """
        Reorder wildlife associations.

        wildlife_ids should be supplied in the desired order.
        """

        wildlife_items = ExperienceWildlife.query.filter(
            ExperienceWildlife.experience_id == experience_id,
            ExperienceWildlife.id.in_(wildlife_ids)
        ).all()

        wildlife_map = {
            item.id: item
            for item in wildlife_items
        }

        for position, wildlife_id in enumerate(wildlife_ids):
            wildlife = wildlife_map.get(wildlife_id)

            if wildlife:
                wildlife.display_order = position

        db.session.commit()

        return ExperienceWildlifeService.get_for_experience(
            experience_id
        )

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(wildlife_id):
        """
        Permanently remove a wildlife association.
        """

        wildlife = ExperienceWildlifeService.get_by_id(
            wildlife_id
        )

        if not wildlife:
            return False

        db.session.delete(wildlife)
        db.session.commit()

        return True

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    @staticmethod
    def delete_for_experience(experience_id):
        """
        Remove all wildlife associations for an experiences.
        """

        wildlife_items = ExperienceWildlife.query.filter_by(
            experience_id=experience_id
        ).all()

        for wildlife in wildlife_items:
            db.session.delete(wildlife)

        db.session.commit()

        return True

    # -------------------------------------------------------------------------

    @staticmethod
    def count_for_experience(
        experience_id,
        active_only=True
    ):
        """
        Count wildlife species associated with an experiences.
        """

        query = ExperienceWildlife.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.count()


# =============================================================================
# Convenience Instance
# =============================================================================

experience_wildlife_service = ExperienceWildlifeService()