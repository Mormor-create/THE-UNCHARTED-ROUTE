"""
===============================================================================
The Uncharted Route
Public Destination Routes
===============================================================================
Handles the public destination catalogue.

Routes
------
/destinations/
/destinations/search
/destinations/<slug>

Business logic is delegated to the destination service layer.
"""

from flask import (
    Blueprint,
    abort,
    render_template,
    request,)
from app.services.destination_service import (
    get_all_destinations,
    get_active_destination_by_slug,
    get_destination_experiences,
    search_destinations, get_active_destinations,)
from app.services.page_hero_service import (
    PageHeroService,)

# =============================================================================
# Blueprint
# =============================================================================
destinations_bp = Blueprint(
    "destinations",
    __name__,
    url_prefix="/destinations",)

# =============================================================================
# Destination Catalogue
# =============================================================================
@destinations_bp.route("/", methods=["GET"])
def index():
    """Display the public destinations catalogue."""

    destinations = get_all_destinations(
        active=True,
        featured=True,)

    featured_destinations = get_all_destinations(
        active=True,
        featured=True,
        show_on_homepage=True,)

    page_hero = PageHeroService.get_by_page_key(
        "destinations")

    return render_template(
        "destinations/index.html",
        destinations=destinations,
        featured_destinations=featured_destinations,
        page_hero=page_hero,)

# =============================================================================
# Destination Search
# =============================================================================
@destinations_bp.route(
    "/search",
    methods=["GET"],)
def search():
    """
    Search the public destination catalogue.

    Only active destinations are returned.
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    destinations = []

    if query:
        destinations = search_destinations(
            query=query,
            active=True,
        )

    return render_template(
        "destinations/search.html",
        destinations=destinations,
        query=query,
    )

# =============================================================================
# Destination Detail
# =============================================================================
@destinations_bp.route(
    "/<slug>",
    methods=["GET"],)
def detail(slug):
    """
    Display a single active destination.

    The destination's active experiences are retrieved through the
    destination service layer and passed to the template.
    """

    destination = get_active_destination_by_slug(
        slug,
    )

    if destination is None:
        abort(404)

    experiences = get_destination_experiences(
        destination,
        active=True,
    )

    return render_template(
        "destinations/detail.html",
        destination=destination,
        experiences=experiences,
    )

@destinations_bp.route("/catalogue/")
def catalogue():
    """ Display the complete public catalogue of active destinations. """
    destinations = get_active_destinations()

    return render_template( "destinations/catalogue.html",
                            destinations=destinations, )

__all__ = [
    "destinations_bp",
]