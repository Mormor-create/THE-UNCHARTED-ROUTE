"""
===============================================================================
The Uncharted Route
Public Destination Journey Routes
===============================================================================

Public-facing routes for sellable multi-destination journeys.

Destination
-----------
/destinations/...
    Catalogue destinations such as Nairobi, Maasai Mara, Diani, etc.

Destination Journey
-------------------
/destination-journeys/...
    Sellable multi-destination travel products.

Booking creation remains in the central booking blueprint.
"""

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    url_for,
)

from app.services.destination_journey_service import (
    get_public_destination_journey_detail,
    get_destination_journey_by_slug,
    get_related_destination_journeys,
)


destination_journeys_bp = Blueprint(
    "destination_journeys",
    __name__,
    url_prefix="/destination-journeys",
)


# =============================================================================
# DESTINATION JOURNEY DETAIL
# =============================================================================
@destination_journeys_bp.route(
    "/<string:slug>",
    methods=["GET"],
)
def detail(slug):
    """
    Display a public Destination Journey.

    Example
    -------
    /destination-journeys/kenya-wildlife-circuit
    """

    journey = get_destination_journey_by_slug(
        slug,
        public_only=True,
    )

    if journey is None:
        abort(404)

    journey_data = (
        get_public_destination_journey_detail(
            journey
        )
    )

    if journey_data is None:
        abort(404)

    related_journeys = (
        get_related_destination_journeys(
            journey,
            limit=3,
        )
    )

    return render_template(
        "destination_journeys/detail.html",
        journey=journey_data["journey"],
        stops=journey_data["stops"],
        total_days=journey_data["total_days"],
        total_nights=journey_data["total_nights"],
        related_journeys=related_journeys,
    )