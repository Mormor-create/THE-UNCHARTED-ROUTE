"""
===============================================================================
The Uncharted Route
Conservation Story Service
===============================================================================

Business logic for reusable conservation stories.

Handles:

• Creating conservation stories
• Retrieving stories
• Updating stories
• Activating/deactivating stories
• Managing featured stories
• Managing display order
• Searching and filtering stories
• Linking stories to experiences
• Story statistics
• Deleting unused stories
"""

from extensions import db
from app.models import ConservationStory


# =============================================================================
# Conservation Story Service
# =============================================================================

class ConservationStoryService:
    """
    Service layer for managing conservation stories.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_story(
        title,
        conservation_type,
        slug=None,
        short_description=None,
        full_story=None,
        focus_species=None,
        organization_name=None,
        organization_website=None,
        why_it_matters=None,
        visitor_impact=None,
        how_guests_help=None,
        interesting_fact=None,
        featured=False,
        active=True,
        display_order=0,
        hero_media_id=None
    ):
        """
        Create and persist a new conservation story.
        """

        story = ConservationStory(
            title=title,
            slug=slug,
            short_description=short_description,
            full_story=full_story,
            conservation_type=conservation_type,
            focus_species=focus_species,
            organization_name=organization_name,
            organization_website=organization_website,
            why_it_matters=why_it_matters,
            visitor_impact=visitor_impact,
            how_guests_help=how_guests_help,
            interesting_fact=interesting_fact,
            featured=featured,
            active=active,
            display_order=display_order,
            hero_media_id=hero_media_id
        )

        db.session.add(story)
        db.session.commit()

        return story

    # =========================================================================
    # Retrieve by ID
    # =========================================================================

    @staticmethod
    def get_by_id(story_id):
        """
        Return a conservation story by ID.
        """

        return db.session.get(
            ConservationStory,
            story_id
        )

    # =========================================================================
    # Retrieve by Title
    # =========================================================================

    @staticmethod
    def get_by_title(title):
        """
        Return a conservation story by title.
        """

        return (
            ConservationStory.query
            .filter(
                ConservationStory.title == title
            )
            .first()
        )

    # =========================================================================
    # Retrieve by Slug
    # =========================================================================

    @staticmethod
    def get_by_slug(slug):
        """
        Return a conservation story by slug.
        """

        return (
            ConservationStory.query
            .filter(
                ConservationStory.slug == slug
            )
            .first()
        )

    # =========================================================================
    # Get All
    # =========================================================================

    @staticmethod
    def get_all(
        active_only=False,
        featured_only=False
    ):
        """
        Return conservation stories.
        """

        query = ConservationStory.query

        if active_only:
            query = query.filter(
                ConservationStory.active.is_(True)
            )

        if featured_only:
            query = query.filter(
                ConservationStory.featured.is_(True)
            )

        return (
            query
            .order_by(
                ConservationStory.display_order.asc(),
                ConservationStory.title.asc()
            )
            .all()
        )

    # =========================================================================
    # Get Active Stories
    # =========================================================================

    @staticmethod
    def get_active():
        """
        Return all active conservation stories.
        """

        return ConservationStoryService.get_all(
            active_only=True
        )

    # =========================================================================
    # Get Featured Stories
    # =========================================================================

    @staticmethod
    def get_featured():
        """
        Return featured active conservation stories.
        """

        return (
            ConservationStory.query
            .filter(
                ConservationStory.active.is_(True),
                ConservationStory.featured.is_(True)
            )
            .order_by(
                ConservationStory.display_order.asc(),
                ConservationStory.title.asc()
            )
            .all()
        )

    # =========================================================================
    # Filter by Conservation Type
    # =========================================================================

    @staticmethod
    def get_by_type(
        conservation_type,
        active_only=True
    ):
        """
        Return stories belonging to a conservation type.

        Examples:

        Wildlife
        Marine
        Forest
        Community
        Climate
        Research
        Education
        """

        query = ConservationStory.query.filter(
            ConservationStory.conservation_type == conservation_type
        )

        if active_only:
            query = query.filter(
                ConservationStory.active.is_(True)
            )

        return (
            query
            .order_by(
                ConservationStory.display_order.asc(),
                ConservationStory.title.asc()
            )
            .all()
        )

    # =========================================================================
    # Search
    # =========================================================================

    @staticmethod
    def search(
        keyword,
        active_only=True
    ):
        """
        Search conservation stories by title, description,
        species, organization, or story content.
        """

        if not keyword:
            return []

        search_term = f"%{keyword}%"

        query = ConservationStory.query.filter(
            db.or_(
                ConservationStory.title.ilike(search_term),
                ConservationStory.short_description.ilike(search_term),
                ConservationStory.full_story.ilike(search_term),
                ConservationStory.focus_species.ilike(search_term),
                ConservationStory.organization_name.ilike(search_term),
                ConservationStory.why_it_matters.ilike(search_term),
                ConservationStory.how_guests_help.ilike(search_term)
            )
        )

        if active_only:
            query = query.filter(
                ConservationStory.active.is_(True)
            )

        return (
            query
            .order_by(
                ConservationStory.display_order.asc(),
                ConservationStory.title.asc()
            )
            .all()
        )

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_story(story_id, **updates):
        """
        Update an existing conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        allowed_fields = {
            "title",
            "slug",
            "short_description",
            "full_story",
            "conservation_type",
            "focus_species",
            "organization_name",
            "organization_website",
            "why_it_matters",
            "visitor_impact",
            "how_guests_help",
            "interesting_fact",
            "featured",
            "active",
            "display_order",
            "hero_media_id"
        }

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(story, field, value)

        db.session.commit()

        return story

    # =========================================================================
    # Activate
    # =========================================================================

    @staticmethod
    def activate(story_id):
        """
        Activate a conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        story.active = True

        db.session.commit()

        return story

    # =========================================================================
    # Deactivate
    # =========================================================================

    @staticmethod
    def deactivate(story_id):
        """
        Deactivate a conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        story.active = False

        db.session.commit()

        return story

    # =========================================================================
    # Feature
    # =========================================================================

    @staticmethod
    def feature(story_id):
        """
        Mark a conservation story as featured.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        story.featured = True

        db.session.commit()

        return story

    # =========================================================================
    # Unfeature
    # =========================================================================

    @staticmethod
    def unfeature(story_id):
        """
        Remove the featured status from a conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        story.featured = False

        db.session.commit()

        return story

    # =========================================================================
    # Display Order
    # =========================================================================

    @staticmethod
    def set_display_order(story_id, display_order):
        """
        Set the display order of a conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return None

        story.display_order = display_order

        db.session.commit()

        return story

    # =========================================================================
    # Experience Count
    # =========================================================================

    @staticmethod
    def get_experience_count(story_id):
        """
        Return the number of experiences using a conservation story.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return 0

        return story.experience_count

    # =========================================================================
    # Stories Used by Experiences
    # =========================================================================

    @staticmethod
    def is_in_use(story_id):
        """
        Determine whether a conservation story is currently
        attached to one or more experiences.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return False

        return story.experience_count > 0

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete(story_id):
        """
        Delete a conservation story.

        A story currently attached to an experiences should be
        detached before deletion.
        """

        story = ConservationStoryService.get_by_id(story_id)

        if not story:
            return False

        if story.experience_count > 0:
            raise ValueError(
                "Cannot delete a conservation story that is "
                "currently assigned to experiences."
            )

        db.session.delete(story)
        db.session.commit()

        return True

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return conservation story statistics.
        """

        total = ConservationStory.query.count()

        active = ConservationStory.query.filter(
            ConservationStory.active.is_(True)
        ).count()

        inactive = ConservationStory.query.filter(
            ConservationStory.active.is_(False)
        ).count()

        featured = ConservationStory.query.filter(
            ConservationStory.featured.is_(True)
        ).count()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "featured": featured
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_conservation_story(**kwargs):
    return ConservationStoryService.create_story(**kwargs)


def get_conservation_story(story_id):
    return ConservationStoryService.get_by_id(story_id)


def get_conservation_story_by_slug(slug):
    return ConservationStoryService.get_by_slug(slug)


def get_active_conservation_stories():
    return ConservationStoryService.get_active()

def get_featured_conservation_stories():
    return ConservationStoryService.get_featured()

def search_conservation_stories(
    keyword,
    active_only=True
):
    return ConservationStoryService.search(
        keyword,
        active_only=active_only
    )

def update_conservation_story(
    story_id,
    **updates
):
    return ConservationStoryService.update_story(
        story_id,
        **updates
    )