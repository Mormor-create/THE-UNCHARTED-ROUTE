import re
import unicodedata
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from sqlalchemy.exc import IntegrityError
from app.decorators.admin import admin_required
from app.forms.admin_photography_spots import AdminPhotographySpotForm
from app.models import Destination
from app.services.photography_spot_service import (
    create_photography_spot,
    delete_photography_spot,
    get_photography_spot,
    get_photography_spots,
    search_photography_spots,
    update_photography_spot,)

photography_spots_bp = Blueprint(
    "admin_photography_spots",
    __name__,
    url_prefix="/admin/photography-spots",)

def _slugify(value):
    """Convert a name into a URL-friendly slug."""

    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()

    return re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    ).strip("-")


def _form_data(form):
    """Return fields accepted by the photography spot service."""

    return {
        "name": form.name.data.strip(),
        "slug": (
            form.slug.data.strip()
            if form.slug.data and form.slug.data.strip()
            else _slugify(form.name.data)
        ),
        "description": form.description.data,

        # Destination and location
        "destination_id": form.destination_id.data,
        "location": form.location.data,

        # Coordinates
        "latitude": form.latitude.data,
        "longitude": form.longitude.data,
        "altitude": form.altitude.data,

        # Photography classification
        "photography_type": form.photography_type.data,
        "difficulty": form.difficulty.data,

        # Photography timing
        "best_time": form.best_time.data,
        "best_time_to_visit": form.best_time_to_visit.data,
        "best_time_to_photograph": (
            form.best_time_to_photograph.data
        ),
        "best_season": form.best_season.data,

        # Photography equipment
        "recommended_lens": form.recommended_lens.data,
        "recommended_lenses": form.recommended_lenses.data,
        "recommended_equipment": (
            form.recommended_equipment.data
        ),

        # Photography conditions
        "lighting_conditions": form.lighting_conditions.data,
        "weather_conditions": form.weather_conditions.data,

        # Camera and visitor guidance
        "camera_settings": form.camera_settings.data,
        "accessibility": form.accessibility.data,
        "photography_tips": form.photography_tips.data,
        "safety_notes": form.safety_notes.data,

        # Display
        "featured": form.featured.data,
        "active": form.active.data,
    }


# =============================================================================
# Photography Spots Index
# =============================================================================

@photography_spots_bp.route("/")
@admin_required
def index():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "all")
    featured = request.args.get("featured", "all")

    # -------------------------------------------------------------------------
    # Overall statistics
    # These counts are independent of the filters applied to the table.
    # -------------------------------------------------------------------------

    all_spots = get_photography_spots(
        active_only=False,
    )

    total_spots = len(all_spots)

    active_spots = sum(
        1 for spot in all_spots
        if spot.active
    )

    inactive_spots = sum(
        1 for spot in all_spots
        if not spot.active
    )

    featured_spots = sum(
        1 for spot in all_spots
        if spot.featured
    )

    # -------------------------------------------------------------------------
    # Table records
    # -------------------------------------------------------------------------

    if search:
        spots = search_photography_spots(
            search,
            active_only=False,
        )
    else:
        spots = all_spots

    if status == "active":
        spots = [
            spot for spot in spots
            if spot.active
        ]

    elif status == "inactive":
        spots = [
            spot for spot in spots
            if not spot.active
        ]

    if featured == "yes":
        spots = [
            spot for spot in spots
            if spot.featured
        ]

    elif featured == "no":
        spots = [
            spot for spot in spots
            if not spot.featured
        ]

    destination_filter = request.args.get(
        "destination",
        "all",
    )

    if destination_filter != "all":
        try:
            destination_id = int(destination_filter)

            spots = [
                spot for spot in spots
                if spot.destination_id == destination_id
            ]

        except (ValueError, TypeError):
            destination_filter = "all"

    destinations = Destination.query.order_by(
        Destination.name.asc()
    ).all()

    return render_template(
        "admin/experiences/photography_spots/index.html",
        spots=spots,
        search=search,
        destinations=destinations,
        destination_filter=destination_filter,
        status=status,
        featured=featured,

        # Overall statistics
        total_spots=total_spots,
        active_spots=active_spots,
        inactive_spots=inactive_spots,
        featured_spots=featured_spots,
    )


# =============================================================================
# Create Photography Spot
# =============================================================================

@photography_spots_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@admin_required
def create():
    form = AdminPhotographySpotForm()

    if form.validate_on_submit():
        try:
            spot = create_photography_spot(
                **_form_data(form)
            )

        except ValueError as exc:
            flash(str(exc), "danger")

        except IntegrityError:
            from extensions import db
            db.session.rollback()

            flash(
                "A photography spot with that name or slug already exists.",
                "danger",
            )

        else:
            flash(
                "Photography spot created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_photography_spots.edit",
                    spot_id=spot.id,
                )
            )

    return render_template(
        "admin/experiences/photography_spots/form.html",
        form=form,
        spot=None,
        page_title="Create Photography Spot",
    )


# =============================================================================
# Edit Photography Spot
# =============================================================================

@photography_spots_bp.route(
    "/<int:spot_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        flash(
            "Photography spot not found.",
            "danger",
        )

        return redirect(
            url_for("admin_photography_spots.index")
        )

    form = AdminPhotographySpotForm(obj=spot)

    if form.validate_on_submit():
        try:
            update_photography_spot(
                spot_id,
                **_form_data(form),
            )

        except ValueError as exc:
            flash(str(exc), "danger")

        except IntegrityError:
            from extensions import db
            db.session.rollback()

            flash(
                "A photography spot with that name or slug already exists.",
                "danger",
            )

        else:
            flash(
                "Photography spot updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_photography_spots.edit",
                    spot_id=spot.id,
                )
            )

    return render_template(
        "admin/experiences/photography_spots/form.html",
        form=form,
        spot=spot,
        page_title=f"Edit {spot.name}",
    )


# =============================================================================
# Photography Spot Details
# =============================================================================

@photography_spots_bp.route("/<int:spot_id>/")
@admin_required
def detail(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        flash(
            "Photography spot not found.",
            "danger",
        )

        return redirect(
            url_for("admin_photography_spots.index")
        )

    experience_links = spot.experiences.all()

    return render_template(
        "admin/experiences/photography_spots/detail.html",
        spot=spot,
        experience_links=experience_links,
    )


# =============================================================================
# Delete Photography Spot
# =============================================================================
@photography_spots_bp.route(
    "/<int:spot_id>/delete",
    methods=["POST"],)
@admin_required
def delete(spot_id):
    deleted = delete_photography_spot(spot_id)

    if deleted:
        flash(
            "Photography spot deleted successfully.",
            "success",
        )
    else:
        flash(
            "Photography spot not found.",
            "danger",
        )

    return redirect(
        url_for("admin_photography_spots.index")
    )