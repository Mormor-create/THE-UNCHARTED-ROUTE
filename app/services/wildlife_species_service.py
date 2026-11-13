"""
===============================================================================
The Uncharted Route
Wildlife Species Service
===============================================================================

Business logic and database operations for WildlifeSpecies.

Responsibilities

• Create wildlife species
• Retrieve wildlife species
• Search and filter species
• Manage featured species
• Manage active species
• Filter by conservation status
• Filter by animal class
• Identify Big Five species
• Identify endangered species
• Update species
• Delete/deactivate species
• Provide species statistics
===============================================================================
"""
from extensions import db
from app.models import WildlifeSpecies

# =============================================================================
# Wildlife Species Service
# =============================================================================


class WildlifeSpeciesService:
    """
    Service layer for WildlifeSpecies operations.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_species(
        common_name,
        animal_class,
        scientific_name=None,
        family=None,
        category=None,
        conservation_status=None,
        protected=False,
        endemic=False,
        description=None,
        interesting_fact=None,
        habitat=None,
        diet=None,
        best_viewing_time=None,
        photography_difficulty="Medium",
        featured=False,
        active=True
    ):
        """
        Create a new wildlife species.
        """

        if not common_name:
            raise ValueError(
                "Common name is required."
            )

        if not animal_class:
            raise ValueError(
                "Animal class is required."
            )

        existing_species = WildlifeSpecies.query.filter_by(
            common_name=common_name
        ).first()

        if existing_species:
            raise ValueError(
                "A wildlife species with this common name already exists."
            )

        species = WildlifeSpecies(
            common_name=common_name,
            scientific_name=scientific_name,
            family=family,
            animal_class=animal_class,
            category=category,
            conservation_status=conservation_status,
            protected=protected,
            endemic=endemic,
            description=description,
            interesting_fact=interesting_fact,
            habitat=habitat,
            diet=diet,
            best_viewing_time=best_viewing_time,
            photography_difficulty=photography_difficulty,
            featured=featured,
            active=active
        )

        db.session.add(species)
        db.session.commit()

        return species

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_by_id(species_id):
        """
        Retrieve a species by ID.
        """

        return WildlifeSpecies.query.get(species_id)

    # =========================================================================
    # Get By Common Name
    # =========================================================================

    @staticmethod
    def get_by_common_name(common_name):
        """
        Retrieve a species by common name.
        """

        if not common_name:
            return None

        return WildlifeSpecies.query.filter_by(
            common_name=common_name
        ).first()

    # =========================================================================
    # List Species
    # =========================================================================

    @staticmethod
    def get_all(
        active_only=False,
        featured_only=False,
        order_by_name=True
    ):
        """
        Return wildlife species.
        """

        query = WildlifeSpecies.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        if order_by_name:
            query = query.order_by(
                WildlifeSpecies.common_name.asc()
            )

        return query.all()

    # =========================================================================
    # Search
    # =========================================================================

    @staticmethod
    def search(
        query_text=None,
        animal_class=None,
        category=None,
        conservation_status=None,
        active_only=True,
        featured_only=False,
        protected_only=False,
        endemic_only=False
    ):
        """
        Search and filter wildlife species.
        """

        query = WildlifeSpecies.query

        if query_text:
            search_term = f"%{query_text}%"

            query = query.filter(
                db.or_(
                    WildlifeSpecies.common_name.ilike(search_term),
                    WildlifeSpecies.scientific_name.ilike(search_term),
                    WildlifeSpecies.family.ilike(search_term),
                    WildlifeSpecies.description.ilike(search_term)
                )
            )

        if animal_class:
            query = query.filter_by(
                animal_class=animal_class
            )

        if category:
            query = query.filter_by(
                category=category
            )

        if conservation_status:
            query = query.filter_by(
                conservation_status=conservation_status
            )

        if active_only:
            query = query.filter_by(
                active=True
            )

        if featured_only:
            query = query.filter_by(
                featured=True
            )

        if protected_only:
            query = query.filter_by(
                protected=True
            )

        if endemic_only:
            query = query.filter_by(
                endemic=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # Big Five
    # =========================================================================

    @staticmethod
    def get_big_five(active_only=True):
        """
        Return Big Five wildlife species.
        """

        query = WildlifeSpecies.query.filter_by(
            category="Big Five"
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # Endangered Species
    # =========================================================================

    @staticmethod
    def get_endangered(active_only=True):
        """
        Return endangered and critically endangered species.
        """

        query = WildlifeSpecies.query.filter(
            WildlifeSpecies.conservation_status.in_([
                "Endangered",
                "Critically Endangered"
            ])
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # Featured Species
    # =========================================================================

    @staticmethod
    def get_featured(active_only=True):
        """
        Return featured wildlife species.
        """

        query = WildlifeSpecies.query.filter_by(
            featured=True
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # By Animal Class
    # =========================================================================

    @staticmethod
    def get_by_animal_class(
        animal_class,
        active_only=True
    ):
        """
        Return species belonging to an animal class.
        """

        query = WildlifeSpecies.query.filter_by(
            animal_class=animal_class
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # By Conservation Status
    # =========================================================================

    @staticmethod
    def get_by_conservation_status(
        conservation_status,
        active_only=True
    ):
        """
        Return species by conservation status.
        """

        query = WildlifeSpecies.query.filter_by(
            conservation_status=conservation_status
        )

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            WildlifeSpecies.common_name.asc()
        ).all()

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_species(
        species_id,
        **updates
    ):
        """
        Update an existing wildlife species.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return None

        if "common_name" in updates:

            common_name = updates["common_name"]

            if not common_name:
                raise ValueError(
                    "Common name cannot be empty."
                )

            duplicate = WildlifeSpecies.query.filter(
                WildlifeSpecies.common_name == common_name,
                WildlifeSpecies.id != species.id
            ).first()

            if duplicate:
                raise ValueError(
                    "Another wildlife species with this common name already exists."
                )

        allowed_fields = {
            "common_name",
            "scientific_name",
            "family",
            "animal_class",
            "category",
            "conservation_status",
            "protected",
            "endemic",
            "description",
            "interesting_fact",
            "habitat",
            "diet",
            "best_viewing_time",
            "photography_difficulty",
            "featured",
            "active"
        }

        for field, value in updates.items():

            if field in allowed_fields:
                setattr(
                    species,
                    field,
                    value
                )

        db.session.commit()

        return species

    # =========================================================================
    # Activate
    # =========================================================================

    @staticmethod
    def activate(species_id):
        """
        Activate a wildlife species.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return None

        species.active = True

        db.session.commit()

        return species

    # =========================================================================
    # Deactivate
    # =========================================================================

    @staticmethod
    def deactivate(species_id):
        """
        Deactivate a wildlife species without deleting it.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return None

        species.active = False

        db.session.commit()

        return species

    # =========================================================================
    # Feature
    # =========================================================================

    @staticmethod
    def feature(species_id):
        """
        Mark a wildlife species as featured.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return None

        species.featured = True

        db.session.commit()

        return species

    # =========================================================================
    # Unfeature
    # =========================================================================

    @staticmethod
    def unfeature(species_id):
        """
        Remove featured status.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return None

        species.featured = False

        db.session.commit()

        return species

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(species_id):
        """
        Permanently delete a wildlife species.
        """

        species = WildlifeSpecies.query.get(
            species_id
        )

        if not species:
            return False

        db.session.delete(species)
        db.session.commit()

        return True

    # =========================================================================
    # Count
    # =========================================================================

    @staticmethod
    def count(active_only=False):
        """
        Return the number of wildlife species.
        """

        query = WildlifeSpecies.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.count()

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return basic wildlife catalogue statistics.
        """

        total = WildlifeSpecies.query.count()

        active = WildlifeSpecies.query.filter_by(
            active=True
        ).count()

        featured = WildlifeSpecies.query.filter_by(
            featured=True,
            active=True
        ).count()

        big_five = WildlifeSpecies.query.filter_by(
            category="Big Five",
            active=True
        ).count()

        endangered = WildlifeSpecies.query.filter(
            WildlifeSpecies.conservation_status.in_([
                "Endangered",
                "Critically Endangered"
            ]),
            WildlifeSpecies.active.is_(True)
        ).count()

        protected = WildlifeSpecies.query.filter_by(
            protected=True,
            active=True
        ).count()

        endemic = WildlifeSpecies.query.filter_by(
            endemic=True,
            active=True
        ).count()

        return {
            "total": total,
            "active": active,
            "featured": featured,
            "big_five": big_five,
            "endangered": endangered,
            "protected": protected,
            "endemic": endemic
        }