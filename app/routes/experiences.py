"""
===============================================================================
The Uncharted Route
Public Experience Routes
===============================================================================

Handles the public experiences catalogue.

Routes
------
/experiences/
/experiences/category/<slug>
/experiences/search
/experiences/<slug>
/experiences/catalogue/

Business logic is delegated to the service layer.
Public experience images are resolved through the Experience Media
associations and the central Media Library.
"""

from flask import (
    Blueprint,
    abort,
    render_template,
    request,)
from app.models import Destination, Experience
from app.services.experiences.experience_service import (
    get_active_experiences,
    get_active_experience_by_slug,
    search_experiences,)
from app.services.experiences.experience_category_service import (
    get_active_categories,
    get_category_by_slug,
    get_category_experiences,)
from app.services.experiences.primary_image_service import (
    get_primary_experience_image_url,
    get_primary_experience_image_urls,)
from app.services.page_hero_service import PageHeroService

# =============================================================================
# Blueprint
# =============================================================================
experiences_bp = Blueprint(
    "experiences",
    __name__,
    url_prefix="/experiences",)

# =============================================================================
# Experience Catalogue
# =============================================================================
@experiences_bp.route("/", methods=["GET"])
def index():
    """
    Display the public Experiences catalogue.
    Only active, featured experiences appear in this catalogue.
    Homepage visibility is managed separately by show_on_homepage.
    The catalogue displays a maximum of nine experiences.
    """

    from app.models import Experience

    # Public catalogue: active and featured experiences only.
    experiences = (
        Experience.query
        .filter(
            Experience.active.is_(True),
            Experience.featured.is_(True),
            Experience.destination.has(
                Destination.active.is_(True)
            ),
        )
        .order_by(
            Experience.display_order.asc(),
            Experience.title.asc(),
            Experience.id.asc(),
        )
        .limit(9)
        .all()
    )

    # Active categories for catalogue navigation and filtering.
    categories = get_active_categories()

    # Page Hero configured in the Page Hero CMS.
    page_hero = PageHeroService.get_by_page_key("experiences")

    # Media Library-backed primary image URLs.
    image_urls = get_primary_experience_image_urls(experiences)

    return render_template(
        "experiences/index.html",
        experiences=experiences,
        categories=categories,
        page_hero=page_hero,
        image_urls=image_urls,
    )

# =============================================================================
# Experience Search
# =============================================================================
@experiences_bp.route("/search",methods=["GET"],)
def search():
    """
    Search the public experiences catalogue.

    Only active experiences are returned. Each result receives its
    primary image URL from the central Media Library.
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    experiences = []

    if query:
        experiences = search_experiences(
            query,
            active_only=True,
        )

        experiences = [
            experience
            for experience in experiences
            if (
                    experience.destination is not None
                    and experience.destination.active)]

    categories = get_active_categories()

    image_urls = get_primary_experience_image_urls(experiences)

    return render_template(
        "experiences/search.html",
        experiences=experiences,
        categories=categories,
        query=query,
        image_urls=image_urls,
    )

# =============================================================================
# Experience Category
# =============================================================================
@experiences_bp.route("/category/<slug>",methods=["GET"],)
def category(slug):
    """
    Display active experiences belonging to a category.

    The primary image for each experience is resolved through the
    Experience Media association and Media Library.
    """

    category = get_category_by_slug(slug)

    if category is None or not category.active:
        abort(404)

    experiences = get_category_experiences(
        category.id,
        active_only=True,
    )

    experiences = [
        experience
        for experience in experiences
        if (
                experience.destination is not None
                and experience.destination.active
        )
    ]

    image_urls = get_primary_experience_image_urls(experiences)
    return render_template(
        "experiences/category.html",
        category=category,
        experiences=experiences,
        image_urls=image_urls,)

@experiences_bp.route("/<slug>", methods=["GET"])
def detail(slug):
    """
    Display a single active experience.

    Public child sections only display active associations and active
    related records. The central Media Library remains responsible
    for resolving the primary image and gallery asset URLs.
    """
    experience = get_active_experience_by_slug(slug)

    if (
            experience is None
            or experience.destination is None
            or not experience.destination.active
    ):
        abort(404)

    primary_image_url = get_primary_experience_image_url(experience)
    from app.services.settings_service import SettingsService
    booking_enabled = SettingsService.bookings_enabled()

    # -------------------------------------------------------------------------
    # Active Experience Tags
    # -------------------------------------------------------------------------
    experience_tags = experience.tags.filter_by(
        active=True
    ).all()

    experience_tags = sorted(
        experience_tags,
        key=lambda tag: (
            tag.sort_order or 0,
            (tag.name or "").casefold(),
        ),
    )

    # -------------------------------------------------------------------------
    # Active Wildlife Associations + Active Wildlife Species
    # -------------------------------------------------------------------------
    wildlife_records = experience.wildlife.filter_by(
        active=True
    ).all()

    wildlife_records = [
        record
        for record in wildlife_records
        if record.species is not None and record.species.active
    ]

    wildlife_records.sort(
        key=lambda record: (
            record.display_order or 0,
            record.id,
        )
    )

    # -------------------------------------------------------------------------
    # Active Photography Associations + Active Photography Spots
    # -------------------------------------------------------------------------
    photography_records = experience.photography_spots.filter_by(
        active=True).all()

    photography_records = [
        record
        for record in photography_records
        if record.spot is not None and record.spot.active]

    photography_records.sort(
        key=lambda record: (
            record.stop_order or 0,
            record.id,))

    # -------------------------------------------------------------------------
    # Active Signature Moments
    # -------------------------------------------------------------------------
    signature_moments = experience.signature_moments.filter_by(
        active=True).all()

    signature_moments.sort(
        key=lambda moment: (
            moment.display_order or 0,
            moment.id,))

    return render_template(
        "experiences/detail.html",
        experience=experience,
        primary_image_url=primary_image_url,
        booking_enabled=booking_enabled,
        experience_tags=experience_tags,
        wildlife_records=wildlife_records,
        photography_records=photography_records,
        signature_moments=signature_moments,)
# =============================================================================
# Complete Experience Catalogue
# =============================================================================
@experiences_bp.route("/catalogue/",methods=["GET"],)
def catalogue():
    """
    Display the complete public catalogue of active experiences,
    ordered alphabetically by title.
    """
    experiences = (
        Experience.query
        .filter(
            Experience.active.is_(True),
            Experience.destination.has(
                Destination.active.is_(True)
            ),
        )
        .order_by(
            Experience.title.asc(),
        )
        .all()
    )

    categories = get_active_categories()
    image_urls = get_primary_experience_image_urls(experiences)

    return render_template(
        "experiences/catalogue.html",
        experiences=experiences,
        categories=categories,
        image_urls=image_urls,
    )

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "experiences_bp",
]