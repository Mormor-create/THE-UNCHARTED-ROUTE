"""
===============================================================================
The Uncharted Route
Signature Moment Service
===============================================================================
Business logic for managing reusable Signature Moments.

Handles:
- Creating signature moments independently of Experiences
- Retrieving moments
- Updating moments
- Activating/deactivating moments
- Featuring/unfeaturing moments
- Managing display order
- Filtering by moment type
- Finding moments assigned to Experiences
- Managing hero media
- Deleting moments
- Statistics
"""

from extensions import db
from app.models import Experience, SignatureMoment

# =============================================================================
# Signature Moment Service
# =============================================================================
class SignatureMomentService:
    """Service layer for managing reusable Signature Moments."""

    # =========================================================================
    # Create
    # =========================================================================
    @staticmethod
    def create_moment(
        title,
        short_description=None,
        full_description=None,
        moment_type="Experience",
        expected_time=None,
        estimated_duration=None,
        best_season=None,
        photography_recommended=True,
        emotional_impact="High",
        featured=True,
        display_order=1,
        active=True,
        hero_media_id=None,
    ):
        """Create and persist a Signature Moment independently."""

        moment = SignatureMoment(
            hero_media_id=hero_media_id,
            title=title,
            short_description=short_description,
            full_description=full_description,
            moment_type=moment_type,
            expected_time=expected_time,
            estimated_duration=estimated_duration,
            best_season=best_season,
            photography_recommended=photography_recommended,
            emotional_impact=emotional_impact,
            featured=featured,
            display_order=display_order,
            active=active,
        )

        db.session.add(moment)
        db.session.commit()

        return moment

    # =========================================================================
    # Retrieve by ID
    # =========================================================================
    @staticmethod
    def get_by_id(moment_id):
        """Return a Signature Moment by ID."""
        return db.session.get(SignatureMoment, moment_id)

    # =========================================================================
    # Retrieve by Title
    # =========================================================================
    @staticmethod
    def get_by_title(title):
        """Return a Signature Moment by title."""
        return (
            SignatureMoment.query
            .filter(SignatureMoment.title == title)
            .first()
        )

    # =========================================================================
    # Get All
    # =========================================================================
    @staticmethod
    def get_all(active_only=False, featured_only=False):
        """Return Signature Moments with optional publishing filters."""

        query = SignatureMoment.query
        if active_only:
            query = query.filter(SignatureMoment.active.is_(True))

        if featured_only:
            query = query.filter(SignatureMoment.featured.is_(True))

        return (
            query
            .order_by(
                SignatureMoment.display_order.asc(),
                SignatureMoment.title.asc(),).all())

    # =========================================================================
    # Get Active
    # =========================================================================
    @staticmethod
    def get_active():
        """Return all active Signature Moments."""
        return SignatureMomentService.get_all(active_only=True)

    # =========================================================================
    # Get Featured
    # =========================================================================
    @staticmethod
    def get_featured():
        """Return featured active Signature Moments."""

        return (
            SignatureMoment.query
            .filter(
                SignatureMoment.active.is_(True),
                SignatureMoment.featured.is_(True),
            )
            .order_by(
                SignatureMoment.display_order.asc(),
                SignatureMoment.title.asc(),
            )
            .all()
        )

    # =========================================================================
    # Get by Experience
    # =========================================================================
    @staticmethod
    def get_by_experience(
        experience_id,
        active_only=True,
        featured_only=False,
    ):
        """Return Signature Moments assigned to a specific Experience."""

        query = (
            SignatureMoment.query
            .join(SignatureMoment.experiences)
            .filter(Experience.id == experience_id)
        )

        if active_only:
            query = query.filter(SignatureMoment.active.is_(True))

        if featured_only:
            query = query.filter(SignatureMoment.featured.is_(True))

        return (
            query
            .order_by(
                SignatureMoment.display_order.asc(),
                SignatureMoment.title.asc(),
            )
            .all()
        )

    # =========================================================================
    # Get by Moment Type
    # =========================================================================
    @staticmethod
    def get_by_type(moment_type, active_only=True):
        """Return Signature Moments belonging to a specific type."""

        query = SignatureMoment.query.filter(
            SignatureMoment.moment_type == moment_type
        )

        if active_only:
            query = query.filter(SignatureMoment.active.is_(True))

        return (
            query
            .order_by(
                SignatureMoment.display_order.asc(),
                SignatureMoment.title.asc(),
            )
            .all()
        )

    # =========================================================================
    # Get by Emotional Impact
    # =========================================================================
    @staticmethod
    def get_by_emotional_impact(
        emotional_impact,
        active_only=True,
    ):
        """Return moments by emotional impact level."""

        query = SignatureMoment.query.filter(
            SignatureMoment.emotional_impact == emotional_impact
        )

        if active_only:
            query = query.filter(SignatureMoment.active.is_(True))

        return (
            query
            .order_by(SignatureMoment.display_order.asc())
            .all()
        )

    # =========================================================================
    # Photography Moments
    # =========================================================================
    @staticmethod
    def get_photography_moments(active_only=True):
        """Return moments where photography is recommended."""

        query = SignatureMoment.query.filter(
            SignatureMoment.photography_recommended.is_(True)
        )

        if active_only:
            query = query.filter(SignatureMoment.active.is_(True))

        return (
            query
            .order_by(
                SignatureMoment.display_order.asc(),
                SignatureMoment.title.asc(),
            )
            .all()
        )

    # =========================================================================
    # Update
    # =========================================================================
    @staticmethod
    def update_moment(moment_id, **updates):
        """Update an existing Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        allowed_fields = {
            "hero_media_id",
            "title",
            "short_description",
            "full_description",
            "moment_type",
            "expected_time",
            "estimated_duration",
            "best_season",
            "photography_recommended",
            "emotional_impact",
            "featured",
            "display_order",
            "active",
        }

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(moment, field, value)

        db.session.commit()
        return moment

    # =========================================================================
    # Activate
    # =========================================================================
    @staticmethod
    def activate(moment_id):
        """Activate a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.active = True
        db.session.commit()

        return moment

    # =========================================================================
    # Deactivate
    # =========================================================================
    @staticmethod
    def deactivate(moment_id):
        """Deactivate a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.active = False
        db.session.commit()

        return moment

    # =========================================================================
    # Feature
    # =========================================================================
    @staticmethod
    def feature(moment_id):
        """Mark a Signature Moment as featured."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.featured = True
        db.session.commit()

        return moment

    # =========================================================================
    # Unfeature
    # =========================================================================
    @staticmethod
    def unfeature(moment_id):
        """Remove the featured status from a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.featured = False
        db.session.commit()

        return moment

    # =========================================================================
    # Display Order
    # =========================================================================
    @staticmethod
    def set_display_order(moment_id, display_order):
        """Set the display order of a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.display_order = display_order
        db.session.commit()

        return moment

    # =========================================================================
    # Hero Media
    # =========================================================================
    @staticmethod
    def set_hero_media(moment_id, hero_media_id):
        """Assign hero media to a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.hero_media_id = hero_media_id
        db.session.commit()

        return moment

    # =========================================================================
    # Remove Hero Media
    # =========================================================================
    @staticmethod
    def remove_hero_media(moment_id):
        """Remove the hero media assignment from a Signature Moment."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return None

        moment.hero_media_id = None
        db.session.commit()

        return moment

    # =========================================================================
    # Has Media
    # =========================================================================
    @staticmethod
    def has_media(moment_id):
        """Determine whether a Signature Moment has hero media."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return False

        return moment.has_media

    # =========================================================================
    # Delete
    # =========================================================================
    @staticmethod
    def delete(moment_id):
        """Delete a Signature Moment catalogue record."""

        moment = SignatureMomentService.get_by_id(moment_id)

        if not moment:
            return False

        db.session.delete(moment)
        db.session.commit()

        return True

    # =========================================================================
    # Statistics
    # =========================================================================
    @staticmethod
    def get_statistics():
        """Return Signature Moment statistics."""

        total = SignatureMoment.query.count()

        active = SignatureMoment.query.filter(
            SignatureMoment.active.is_(True)
        ).count()

        inactive = SignatureMoment.query.filter(
            SignatureMoment.active.is_(False)
        ).count()

        featured = SignatureMoment.query.filter(
            SignatureMoment.featured.is_(True)
        ).count()

        photography = SignatureMoment.query.filter(
            SignatureMoment.photography_recommended.is_(True)
        ).count()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "featured": featured,
            "photography_recommended": photography,
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_signature_moment(**kwargs):
    return SignatureMomentService.create_moment(**kwargs)


def get_signature_moment(moment_id):
    return SignatureMomentService.get_by_id(moment_id)


def get_experience_signature_moments(
    experience_id,
    active_only=True,
    featured_only=False,
):
    return SignatureMomentService.get_by_experience(
        experience_id,
        active_only=active_only,
        featured_only=featured_only,
    )


def get_featured_signature_moments():
    return SignatureMomentService.get_featured()


def update_signature_moment(moment_id, **updates):
    return SignatureMomentService.update_moment(
        moment_id,
        **updates,
    )


def delete_signature_moment(moment_id):
    return SignatureMomentService.delete(moment_id)
