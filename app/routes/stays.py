"""
===============================================================================
The Uncharted Route
Public Stay Routes
===============================================================================

Handles the public stays catalogue and accommodation details.

Routes
------
/stays/
/stays/search
/stays/<slug>
/stays/<stay_slug>/rooms/<room_slug>

Business logic is delegated to the stay service layer.
"""

from flask import (
    Blueprint,
    abort,
    render_template,
    request, url_for,
)

from app.models import Stay
from app.services.stay_service import (
    get_public_accommodation_types,
    get_public_stays,
    get_room_detail,
    get_room_by_slug,
    get_stay_by_slug,
    get_stay_detail,
    search_public_stays,
)
from app.services.page_hero_service import PageHeroService
from app.services.settings_service import SettingsService


# =============================================================================
# Blueprint
# =============================================================================

stays_bp = Blueprint(
    "stays",
    __name__,
    url_prefix="/stays",
)


# =============================================================================
# Public Stays Index
# =============================================================================

@stays_bp.route("/")
def index():
    """
    Public stays landing page.

    Supports optional filtering by:
        ?search=
        ?destination_id=
        ?accommodation_type=
        ?featured=

    The page hero is loaded from the Page Hero CMS using the
    ``stays`` page key.
    """

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    destination_id = request.args.get(
        "destination_id",
        type=int,
    )

    accommodation_type = request.args.get(
        "accommodation_type",
        "",
        type=str,
    ).strip()

    featured_param = request.args.get(
        "featured",
        "",
        type=str,
    ).strip().lower()

    featured = None

    if featured_param in {"1", "true", "yes"}:
        featured = True

    elif featured_param in {"0", "false", "no"}:
        featured = False

    stays = get_public_stays(
        search=search or None,
        destination_id=destination_id,
        accommodation_type=accommodation_type or None,
        featured=featured,
    )

    accommodation_types = get_public_accommodation_types()

    page_hero = PageHeroService.get_by_page_key("stays")

    return render_template(
        "stays/index.html",
        stays=stays,
        search=search,
        destination_id=destination_id,
        accommodation_type=accommodation_type,
        accommodation_types=accommodation_types,
        page_hero=page_hero,
        booking_enabled=SettingsService.bookings_enabled(),
    )


# =============================================================================
# Public Stay Detail
# =============================================================================
@stays_bp.route("/<string:slug>")
def detail(slug):
    """Display a single public stay and its available information."""

    stay = get_stay_by_slug(slug)

    if not stay or not stay.active:
        abort(404)

    stay_data = get_stay_detail(stay)

    if not stay_data:
        abort(404)

    return render_template(
        "stays/detail.html",
        **stay_data,
        booking_enabled=SettingsService.bookings_enabled(),)

# =============================================================================
# Public Room Detail
# =============================================================================
@stays_bp.route("/<string:stay_slug>/rooms/<string:room_slug>")
def room_detail(stay_slug, room_slug):
    """Display a room detail page with the correct booking or enquiry action."""

    stay = get_stay_by_slug(stay_slug)

    if not stay or not stay.active:
        abort(404)

    room = get_room_by_slug(stay.id, room_slug)

    if not room or not room.active:
        abort(404)

    room_data = get_room_detail(room)

    if not room_data:
        abort(404)

    settings = SettingsService.get_settings()
    booking_enabled = SettingsService.bookings_enabled()

    # Build links to the existing public forms.
    stay_booking_url = url_for(
        "public_stay_bookings.book_stay",
        slug=stay.slug,
        room_id=room.id,
    )

    stay_enquiry_url = url_for(
        "stay_inquiries.enquire",
        slug=stay.slug,
        room_id=room.id,
    )

    return render_template(
        "stays/room_detail.html",
        **room_data,
        booking_enabled=booking_enabled,
        show_booking_button=(getattr(settings, "show_booking_button", True)if settings else True),
        stay_booking_url=stay_booking_url,
        stay_enquiry_url=stay_enquiry_url,
    )
# =============================================================================
# Public Stay Search
# =============================================================================
@stays_bp.route("/search")
def search():
    """Search public accommodation properties."""

    search_term = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    stays = search_public_stays(search_term)

    accommodation_types = get_public_accommodation_types()

    return render_template(
        "stays/search.html",
        stays=stays,
        search_term=search_term,
        accommodation_types=accommodation_types,
        booking_enabled=SettingsService.bookings_enabled(),
)


# =============================================================================
# Public Stay Catalogue
# =============================================================================
@stays_bp.route("/catalogue/")
def catalogue():
    """Display the catalogue of active stays."""

    stays = (
        Stay.query
        .filter(Stay.active.is_(True))
        .order_by(Stay.property_name.asc())
        .all()
    )

    return render_template(
        "stays/catalogue.html",
        stays=stays,
        booking_enabled=SettingsService.bookings_enabled(),)

# =============================================================================
# Exports
# =============================================================================

__all__ = ["stays_bp"]
