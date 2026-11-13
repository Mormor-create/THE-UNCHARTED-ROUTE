"""
===============================================================================
The Uncharted Route
Destination Journey Service
===============================================================================

Public and catalogue-level business logic for Destination Journeys.

A DestinationJourney is a sellable multi-destination travel product.

Responsibilities
----------------
• Retrieve active/public journeys
• Retrieve a journey by slug
• Retrieve featured journeys
• Retrieve journeys by status
• Search journeys
• Retrieve journey stops
• Prepare public journey detail data
• Validate public journey availability/status

Booking creation and booking calculations do NOT belong here.
Those remain in the central booking service / booking routes.
"""

from sqlalchemy import or_

from extensions import db

from app.models.destination_journey import (
    DestinationJourney,
    DestinationJourneyStop,
)


# =============================================================================
# PUBLIC STATUS
# =============================================================================

PUBLIC_JOURNEY_STATUS = "published"


# =============================================================================
# NORMALISATION HELPERS
# =============================================================================

def _normalise(value):
    """
    Return a trimmed string or None.
    """

    if value is None:
        return None

    value = str(value).strip()

    return value or None


# =============================================================================
# GET JOURNEY
# =============================================================================

def get_destination_journey_by_id(journey_id):
    """
    Retrieve a DestinationJourney by primary key.

    Returns
    -------
    DestinationJourney | None
    """

    if not journey_id:
        return None

    return db.session.get(
        DestinationJourney,
        journey_id,
    )


def get_destination_journey_by_slug(
    slug,
    public_only=True,
):
    """
    Retrieve a DestinationJourney by slug.

    Parameters
    ----------
    slug : str
        Journey slug.

    public_only : bool
        When True, only published journeys are returned.
    """

    slug = _normalise(slug)

    if not slug:
        return None

    query = DestinationJourney.query.filter(
        DestinationJourney.slug == slug
    )

    if public_only:
        query = query.filter(
            DestinationJourney.status == PUBLIC_JOURNEY_STATUS
        )

    return query.first()


# =============================================================================
# PUBLIC JOURNEY CATALOGUE
# =============================================================================

def get_public_destination_journeys(
    featured=None,
    journey_type=None,
    difficulty_level=None,
    bespoke=None,
):
    """
    Return published Destination Journeys for the public website.

    Optional filters:
        featured
        journey_type
        difficulty_level
        bespoke
    """

    query = DestinationJourney.query.filter(
        DestinationJourney.status == PUBLIC_JOURNEY_STATUS
    )

    if featured is not None:
        query = query.filter(
            DestinationJourney.is_featured == featured
        )

    if journey_type:
        query = query.filter(
            DestinationJourney.journey_type == journey_type
        )

    if difficulty_level:
        query = query.filter(
            DestinationJourney.difficulty_level
            == difficulty_level
        )

    if bespoke is not None:
        query = query.filter(
            DestinationJourney.is_bespoke == bespoke
        )

    return (
        query
        .order_by(
            DestinationJourney.is_featured.desc(),
            DestinationJourney.name.asc(),
        )
        .all()
    )


def get_featured_destination_journeys():
    """
    Return published featured Destination Journeys.
    """

    return get_public_destination_journeys(
        featured=True,
    )


# =============================================================================
# SEARCH
# =============================================================================

def search_destination_journeys(
    query_text,
    public_only=True,
):
    """
    Search Destination Journeys by:

    • name
    • short description
    • full description
    • journey type
    • difficulty level
    """

    query_text = _normalise(query_text)

    if not query_text:
        return []

    search_term = f"%{query_text}%"

    query = DestinationJourney.query

    if public_only:
        query = query.filter(
            DestinationJourney.status
            == PUBLIC_JOURNEY_STATUS
        )

    query = query.filter(
        or_(
            DestinationJourney.name.ilike(
                search_term
            ),
            DestinationJourney.short_description.ilike(
                search_term
            ),
            DestinationJourney.description.ilike(
                search_term
            ),
            DestinationJourney.journey_type.ilike(
                search_term
            ),
            DestinationJourney.difficulty_level.ilike(
                search_term
            ),
        )
    )

    return (
        query
        .order_by(
            DestinationJourney.is_featured.desc(),
            DestinationJourney.name.asc(),
        )
        .all()
    )


# =============================================================================
# JOURNEY STOPS
# =============================================================================

def get_destination_journey_stops(
    journey_id,
):
    """
    Return ordered stops belonging to a journey.
    """

    if not journey_id:
        return []

    return (
        DestinationJourneyStop.query
        .filter_by(
            journey_id=journey_id
        )
        .order_by(
            DestinationJourneyStop.sequence.asc(),
            DestinationJourneyStop.id.asc(),
        )
        .all()
    )


# =============================================================================
# JOURNEY TYPES / FILTER VALUES
# =============================================================================

def get_public_journey_types():
    """
    Return unique journey types used by published journeys.
    """

    journeys = (
        DestinationJourney.query
        .filter(
            DestinationJourney.status
            == PUBLIC_JOURNEY_STATUS,
            DestinationJourney.journey_type.isnot(None),
        )
        .order_by(
            DestinationJourney.journey_type.asc()
        )
        .all()
    )

    values = []

    for journey in journeys:

        value = _normalise(
            journey.journey_type
        )

        if value and value not in values:
            values.append(value)

    return values


def get_public_difficulty_levels():
    """
    Return unique difficulty levels used by published journeys.
    """

    journeys = (
        DestinationJourney.query
        .filter(
            DestinationJourney.status
            == PUBLIC_JOURNEY_STATUS,
            DestinationJourney.difficulty_level.isnot(None),
        )
        .order_by(
            DestinationJourney.difficulty_level.asc()
        )
        .all()
    )

    values = []

    for journey in journeys:

        value = _normalise(
            journey.difficulty_level
        )

        if value and value not in values:
            values.append(value)

    return values


# =============================================================================
# PUBLIC DETAIL DATA
# =============================================================================

def get_public_destination_journey_detail(
    journey,
):
    """
    Prepare the data required by the public
    Destination Journey detail page.

    This function deliberately returns the actual model
    plus its ordered stops rather than manufacturing
    fields that do not exist on the model.
    """

    if journey is None:
        return None

    if journey.status != PUBLIC_JOURNEY_STATUS:
        return None

    stops = get_destination_journey_stops(
        journey.id
    )

    total_days = journey.duration_days or 0
    total_nights = journey.duration_nights or 0

    return {
        "journey": journey,
        "stops": stops,
        "total_days": total_days,
        "total_nights": total_nights,
    }


# =============================================================================
# RELATED JOURNEYS
# =============================================================================

def get_related_destination_journeys(
    journey,
    limit=3,
):
    """
    Return published journeys related to the supplied journey.

    Matching is based on journey type first and then
    falls back to other published journeys.
    """

    if journey is None:
        return []

    query = DestinationJourney.query.filter(
        DestinationJourney.status
        == PUBLIC_JOURNEY_STATUS,
        DestinationJourney.id != journey.id,
    )

    if journey.journey_type:

        related = (
            query
            .filter(
                DestinationJourney.journey_type
                == journey.journey_type
            )
            .order_by(
                DestinationJourney.is_featured.desc(),
                DestinationJourney.name.asc(),
            )
            .limit(limit)
            .all()
        )

        if len(related) >= limit:
            return related

        existing_ids = [
            item.id
            for item in related
        ]

        fallback_query = query

        if existing_ids:
            fallback_query = fallback_query.filter(
                ~DestinationJourney.id.in_(
                    existing_ids
                )
            )

        remaining = (
            fallback_query
            .order_by(
                DestinationJourney.is_featured.desc(),
                DestinationJourney.name.asc(),
            )
            .limit(
                limit - len(related)
            )
            .all()
        )

        return related + remaining

    return (
        query
        .order_by(
            DestinationJourney.is_featured.desc(),
            DestinationJourney.name.asc(),
        )
        .limit(limit)
        .all()
    )


# =============================================================================
# BOOKING ELIGIBILITY
# =============================================================================

def journey_accepts_public_booking(
    journey,
):
    """
    Determine whether a journey can currently be
    presented as bookable on the public website.

    The actual booking service remains responsible for
    validating the booking itself.
    """

    if journey is None:
        return False

    if journey.status != PUBLIC_JOURNEY_STATUS:
        return False

    return True