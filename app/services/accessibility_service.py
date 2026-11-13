"""
===============================================================================
The Uncharted Route — Accessibility Service
===============================================================================

Business logic for managing reusable accessibility profiles.

Responsibilities

• Create accessibility profiles
• Retrieve accessibility profiles
• Update accessibility profiles
• Delete accessibility profiles
• Search and filter profiles
• Retrieve active profiles
• Retrieve suitability-based profiles
• Generate profile summaries
• Generate CMS statistics
• Validate profile data

Accessibility profiles are reusable across multiple experiences.

===============================================================================
"""

from extensions import db
from app.models import Accessibility


# =============================================================================
# Constants
# =============================================================================

FITNESS_LEVELS = {
     "Very Low",
     "Low",
     "Low to Moderate",
     "Moderate",
     "Good",
     "High",
     "Extreme",
}

# =============================================================================
# Accessibility Service
# =============================================================================

class AccessibilityService:
    """
    Service layer for Accessibility operations.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_profile(
        name,
        slug=None,
        summary=None,
        wheelchair_accessible=False,
        stroller_friendly=False,
        walking_required=True,
        hiking_required=False,
        uneven_terrain=False,
        stairs_required=False,
        child_friendly=True,
        elderly_friendly=True,
        pregnancy_friendly=True,
        pet_friendly=False,
        minimum_fitness_level="Easy",
        maximum_altitude_meters=None,
        accessible_restrooms=False,
        changing_facilities=False,
        medical_support_available=False,
        vegetarian_available=False,
        vegan_available=False,
        halal_available=False,
        kosher_available=False,
        gluten_free_available=False,
        allergy_support=False,
        multilingual_guides=True,
        sign_language_available=False,
        braille_materials=False,
        audio_guides=False,
        notes=None,
        active=True,
    ):
        """
        Create a new accessibility profile.
        """

        name = name.strip() if name else ""

        if not name:
            raise ValueError(
                "Accessibility profile name is required."
            )

        existing = Accessibility.query.filter_by(
            name=name
        ).first()

        if existing:
            raise ValueError(
                "An accessibility profile with this name already exists."
            )

        if slug:
            slug = slug.strip()

            existing_slug = Accessibility.query.filter_by(
                slug=slug
            ).first()

            if existing_slug:
                raise ValueError(
                    "An accessibility profile with this slug already exists."
                )

        if minimum_fitness_level not in FITNESS_LEVELS:
            raise ValueError(
                "Invalid minimum fitness level."
            )

        profile = Accessibility(
            name=name,
            slug=slug,
            summary=summary,

            wheelchair_accessible=wheelchair_accessible,
            stroller_friendly=stroller_friendly,
            walking_required=walking_required,
            hiking_required=hiking_required,
            uneven_terrain=uneven_terrain,
            stairs_required=stairs_required,

            child_friendly=child_friendly,
            elderly_friendly=elderly_friendly,
            pregnancy_friendly=pregnancy_friendly,
            pet_friendly=pet_friendly,

            minimum_fitness_level=minimum_fitness_level,
            maximum_altitude_meters=maximum_altitude_meters,

            accessible_restrooms=accessible_restrooms,
            changing_facilities=changing_facilities,
            medical_support_available=medical_support_available,

            vegetarian_available=vegetarian_available,
            vegan_available=vegan_available,
            halal_available=halal_available,
            kosher_available=kosher_available,
            gluten_free_available=gluten_free_available,
            allergy_support=allergy_support,

            multilingual_guides=multilingual_guides,
            sign_language_available=sign_language_available,
            braille_materials=braille_materials,
            audio_guides=audio_guides,

            notes=notes,
            active=active,
        )

        db.session.add(profile)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return profile

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_by_id(profile_id):
        """
        Retrieve an accessibility profile by ID.
        """

        if not profile_id:
            return None

        return db.session.get(
            Accessibility,
            profile_id,
        )

    # -------------------------------------------------------------------------

    @staticmethod
    def get_by_name(name):
        """
        Retrieve an accessibility profile by name.
        """

        if not name:
            return None

        return Accessibility.query.filter_by(
            name=name
        ).first()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_by_slug(slug):
        """
        Retrieve an accessibility profile by slug.
        """

        if not slug:
            return None

        return Accessibility.query.filter_by(
            slug=slug
        ).first()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_all(active_only=False):
        """
        Retrieve all accessibility profiles.
        """

        query = Accessibility.query

        if active_only:
            query = query.filter_by(
                active=True
            )

        return query.order_by(
            Accessibility.name.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_active_profiles():
        """
        Retrieve all active accessibility profiles.
        """

        return Accessibility.query.filter_by(
            active=True
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_profile(
        profile_id,
        **kwargs,
    ):
        """
        Update an accessibility profile.

        Only attributes belonging to the Accessibility model
        may be updated.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return None

        allowed_fields = {
            "name",
            "slug",
            "summary",

            "wheelchair_accessible",
            "stroller_friendly",
            "walking_required",
            "hiking_required",
            "uneven_terrain",
            "stairs_required",

            "child_friendly",
            "elderly_friendly",
            "pregnancy_friendly",
            "pet_friendly",

            "minimum_fitness_level",
            "maximum_altitude_meters",

            "accessible_restrooms",
            "changing_facilities",
            "medical_support_available",

            "vegetarian_available",
            "vegan_available",
            "halal_available",
            "kosher_available",
            "gluten_free_available",
            "allergy_support",

            "multilingual_guides",
            "sign_language_available",
            "braille_materials",
            "audio_guides",

            "notes",
            "active",
        }

        # ---------------------------------------------------------------------
        # Normalize
        # ---------------------------------------------------------------------

        if "name" in kwargs and kwargs["name"]:
            kwargs["name"] = kwargs["name"].strip()

        if "slug" in kwargs and kwargs["slug"]:
            kwargs["slug"] = kwargs["slug"].strip()

        # ---------------------------------------------------------------------
        # Validate name uniqueness
        # ---------------------------------------------------------------------

        if "name" in kwargs:

            if not kwargs["name"]:
                raise ValueError(
                    "Accessibility profile name is required."
                )

            existing = Accessibility.query.filter(
                Accessibility.name == kwargs["name"],
                Accessibility.id != profile.id,
            ).first()

            if existing:
                raise ValueError(
                    "An accessibility profile with this name already exists."
                )

        # ---------------------------------------------------------------------
        # Validate slug uniqueness
        # ---------------------------------------------------------------------

        if "slug" in kwargs and kwargs["slug"]:

            existing_slug = Accessibility.query.filter(
                Accessibility.slug == kwargs["slug"],
                Accessibility.id != profile.id,
            ).first()

            if existing_slug:
                raise ValueError(
                    "An accessibility profile with this slug already exists."
                )

        # ---------------------------------------------------------------------
        # Validate fitness level
        # ---------------------------------------------------------------------

        if (
            "minimum_fitness_level" in kwargs
            and kwargs["minimum_fitness_level"]
            not in FITNESS_LEVELS
        ):
            raise ValueError(
                "Invalid minimum fitness level."
            )

        # ---------------------------------------------------------------------
        # Apply fields
        # ---------------------------------------------------------------------

        for field, value in kwargs.items():

            if field not in allowed_fields:
                continue

            setattr(
                profile,
                field,
                value,
            )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return profile

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete_profile(profile_id):
        """
        Delete an accessibility profile.

        Profiles currently assigned to experiences cannot be deleted.
        This protects reusable accessibility relationships.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return False

        usage_count = profile.experiences.count()

        if usage_count > 0:
            raise ValueError(
                "This accessibility profile is currently assigned to "
                f"{usage_count} experience(s) and cannot be deleted. "
                "Deactivate it instead."
            )

        db.session.delete(
            profile
        )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return True

    # =========================================================================
    # Status
    # =========================================================================

    @staticmethod
    def activate(profile_id):
        """
        Activate an accessibility profile.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return None

        profile.active = True

        db.session.commit()

        return profile

    # -------------------------------------------------------------------------

    @staticmethod
    def deactivate(profile_id):
        """
        Deactivate an accessibility profile.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return None

        profile.active = False

        db.session.commit()

        return profile

    # -------------------------------------------------------------------------

    @staticmethod
    def toggle_status(profile_id):
        """
        Toggle the active status of an accessibility profile.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return None

        profile.active = not profile.active

        db.session.commit()

        return profile

    # =========================================================================
    # Search
    # =========================================================================

    @staticmethod
    def search(
        query,
        active_only=True,
    ):
        """
        Search profiles by name, slug, summary, or notes.
        """

        if not query:
            return AccessibilityService.get_all(
                active_only=active_only
            )

        search_term = f"%{query.strip()}%"

        filters = [
            Accessibility.name.ilike(search_term),
            Accessibility.slug.ilike(search_term),
            Accessibility.summary.ilike(search_term),
            Accessibility.notes.ilike(search_term),
        ]

        search_query = Accessibility.query.filter(
            db.or_(*filters)
        )

        if active_only:
            search_query = search_query.filter(
                Accessibility.active.is_(True)
            )

        return search_query.order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Accessibility Filters
    # =========================================================================

    @staticmethod
    def get_wheelchair_accessible():
        """
        Retrieve active wheelchair-accessible profiles.
        """

        return Accessibility.query.filter_by(
            wheelchair_accessible=True,
            active=True,
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_child_friendly():
        """
        Retrieve active child-friendly profiles.
        """

        return Accessibility.query.filter_by(
            child_friendly=True,
            active=True,
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_elderly_friendly():
        """
        Retrieve active profiles suitable for elderly guests.
        """

        return Accessibility.query.filter_by(
            elderly_friendly=True,
            active=True,
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_pregnancy_friendly():
        """
        Retrieve active profiles suitable for pregnant guests.
        """

        return Accessibility.query.filter_by(
            pregnancy_friendly=True,
            active=True,
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_family_friendly():
        """
        Retrieve active family-friendly profiles.
        """

        return Accessibility.query.filter(
            Accessibility.child_friendly.is_(True),
            Accessibility.elderly_friendly.is_(True),
            Accessibility.active.is_(True),
        ).order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Fitness Filtering
    # =========================================================================

    @staticmethod
    def get_by_fitness_level(
        level,
        active_only=True,
    ):
        """
        Retrieve profiles matching a fitness level.
        """

        if not level:
            return []

        query = Accessibility.query.filter(
            db.func.lower(
                Accessibility.minimum_fitness_level
            ) == level.lower()
        )

        if active_only:
            query = query.filter(
                Accessibility.active.is_(True)
            )

        return query.order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Dietary Support
    # =========================================================================

    @staticmethod
    def get_with_dietary_support(
        vegetarian=False,
        vegan=False,
        halal=False,
        kosher=False,
        gluten_free=False,
        allergy_support=False,
    ):
        """
        Retrieve active profiles supporting requested dietary needs.
        """

        query = Accessibility.query.filter(
            Accessibility.active.is_(True)
        )

        if vegetarian:
            query = query.filter(
                Accessibility.vegetarian_available.is_(True)
            )

        if vegan:
            query = query.filter(
                Accessibility.vegan_available.is_(True)
            )

        if halal:
            query = query.filter(
                Accessibility.halal_available.is_(True)
            )

        if kosher:
            query = query.filter(
                Accessibility.kosher_available.is_(True)
            )

        if gluten_free:
            query = query.filter(
                Accessibility.gluten_free_available.is_(True)
            )

        if allergy_support:
            query = query.filter(
                Accessibility.allergy_support.is_(True)
            )

        return query.order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Communication Support
    # =========================================================================

    @staticmethod
    def get_with_communication_support(
        multilingual=False,
        sign_language=False,
        braille=False,
        audio_guides=False,
    ):
        """
        Retrieve profiles supporting requested communication options.
        """

        query = Accessibility.query.filter(
            Accessibility.active.is_(True)
        )

        if multilingual:
            query = query.filter(
                Accessibility.multilingual_guides.is_(True)
            )

        if sign_language:
            query = query.filter(
                Accessibility.sign_language_available.is_(True)
            )

        if braille:
            query = query.filter(
                Accessibility.braille_materials.is_(True)
            )

        if audio_guides:
            query = query.filter(
                Accessibility.audio_guides.is_(True)
            )

        return query.order_by(
            Accessibility.name.asc()
        ).all()

    # =========================================================================
    # Usage
    # =========================================================================

    @staticmethod
    def get_usage_count(profile_id):
        """
        Return the number of experiences using this profile.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return 0

        return profile.experiences.count()

    # =========================================================================
    # Summary
    # =========================================================================

    @staticmethod
    def get_summary(profile_id):
        """
        Return a structured accessibility summary.
        """

        profile = AccessibilityService.get_by_id(
            profile_id
        )

        if not profile:
            return None

        return {
            "id": profile.id,
            "name": profile.name,
            "slug": profile.slug,
            "summary": profile.summary,

            "wheelchair_accessible": profile.wheelchair_accessible,
            "stroller_friendly": profile.stroller_friendly,
            "walking_required": profile.walking_required,
            "hiking_required": profile.hiking_required,
            "uneven_terrain": profile.uneven_terrain,
            "stairs_required": profile.stairs_required,

            "child_friendly": profile.child_friendly,
            "elderly_friendly": profile.elderly_friendly,
            "pregnancy_friendly": profile.pregnancy_friendly,
            "pet_friendly": profile.pet_friendly,

            "minimum_fitness_level": profile.minimum_fitness_level,
            "maximum_altitude_meters": (
                profile.maximum_altitude_meters
            ),

            "accessible_restrooms": profile.accessible_restrooms,
            "changing_facilities": profile.changing_facilities,
            "medical_support_available": (
                profile.medical_support_available
            ),

            "vegetarian_available": profile.vegetarian_available,
            "vegan_available": profile.vegan_available,
            "halal_available": profile.halal_available,
            "kosher_available": profile.kosher_available,
            "gluten_free_available": profile.gluten_free_available,
            "allergy_support": profile.allergy_support,

            "multilingual_guides": profile.multilingual_guides,
            "sign_language_available": (
                profile.sign_language_available
            ),
            "braille_materials": profile.braille_materials,
            "audio_guides": profile.audio_guides,

            "family_friendly": profile.family_friendly,
            "fully_accessible": profile.fully_accessible,

            "active": profile.active,

            "usage_count": profile.experiences.count(),
        }

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return CMS statistics for accessibility profiles.
        """

        profiles = Accessibility.query.all()

        total = len(profiles)

        active = sum(
            1
            for profile in profiles
            if profile.active
        )

        inactive = total - active

        wheelchair = sum(
            1
            for profile in profiles
            if profile.wheelchair_accessible
        )

        child_friendly = sum(
            1
            for profile in profiles
            if profile.child_friendly
        )

        family_friendly = sum(
            1
            for profile in profiles
            if profile.family_friendly
        )

        fully_accessible = sum(
            1
            for profile in profiles
            if profile.fully_accessible
        )

        hiking_required = sum(
            1
            for profile in profiles
            if profile.hiking_required
        )

        dietary_support = sum(
            1
            for profile in profiles
            if any(
                [
                    profile.vegetarian_available,
                    profile.vegan_available,
                    profile.halal_available,
                    profile.kosher_available,
                    profile.gluten_free_available,
                    profile.allergy_support,
                ]
            )
        )

        communication_support = sum(
            1
            for profile in profiles
            if any(
                [
                    profile.multilingual_guides,
                    profile.sign_language_available,
                    profile.braille_materials,
                    profile.audio_guides,
                ]
            )
        )

        total_usage = sum(
            profile.experiences.count()
            for profile in profiles
        )

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "wheelchair_accessible": wheelchair,
            "child_friendly": child_friendly,
            "family_friendly": family_friendly,
            "fully_accessible": fully_accessible,
            "hiking_required": hiking_required,
            "dietary_support": dietary_support,
            "communication_support": communication_support,
            "total_usage": total_usage,
        }

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def validate_profile_data(
        name,
        slug=None,
        profile_id=None,
    ):
        """
        Validate profile uniqueness.

        profile_id may be supplied when validating an edit.
        """

        errors = []

        if not name or not name.strip():
            errors.append(
                "Accessibility profile name is required."
            )

        if name:
            query = Accessibility.query.filter(
                Accessibility.name == name.strip()
            )

            if profile_id:
                query = query.filter(
                    Accessibility.id != profile_id
                )

            if query.first():
                errors.append(
                    "An accessibility profile with this name "
                    "already exists."
                )

        if slug:
            query = Accessibility.query.filter(
                Accessibility.slug == slug.strip()
            )

            if profile_id:
                query = query.filter(
                    Accessibility.id != profile_id
                )

            if query.first():
                errors.append(
                    "An accessibility profile with this slug "
                    "already exists."
                )

        return errors