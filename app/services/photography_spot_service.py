from app.models import PhotographySpot
from app.models.destination import Destination
from extensions import db


# =============================================================================
# Retrieval
# =============================================================================

def get_photography_spot(spot_id):
    return db.session.get(PhotographySpot, spot_id)


def get_photography_spot_by_slug(slug):
    if not slug:
        return None

    return PhotographySpot.query.filter_by(
        slug=slug.strip()
    ).first()


def get_photography_spot_by_name(name):
    if not name:
        return None

    return PhotographySpot.query.filter(
        db.func.lower(PhotographySpot.name) == name.strip().lower()
    ).first()


def get_photography_spots(active_only=True, featured_only=False):
    query = PhotographySpot.query

    if active_only:
        query = query.filter_by(active=True)

    if featured_only:
        query = query.filter_by(featured=True)

    return query.order_by(PhotographySpot.name.asc()).all()


def get_featured_photography_spots():
    return PhotographySpot.query.filter_by(
        active=True,
        featured=True,
    ).order_by(PhotographySpot.name.asc()).all()


def get_active_photography_spots():
    return get_photography_spots(active_only=True)


def get_inactive_photography_spots():
    return PhotographySpot.query.filter_by(
        active=False
    ).order_by(PhotographySpot.name.asc()).all()


# =============================================================================
# Search
# =============================================================================

def search_photography_spots(search_term, active_only=True):
    if not search_term:
        return get_photography_spots(active_only=active_only)

    term = f"%{search_term.strip()}%"

    query = PhotographySpot.query.filter(
        db.or_(
            PhotographySpot.name.ilike(term),
            PhotographySpot.slug.ilike(term),
            PhotographySpot.description.ilike(term),
            PhotographySpot.location.ilike(term),
            PhotographySpot.photography_type.ilike(term),
            PhotographySpot.best_time.ilike(term),
            PhotographySpot.best_time_to_visit.ilike(term),
            PhotographySpot.best_time_to_photograph.ilike(term),
            PhotographySpot.best_season.ilike(term),
            PhotographySpot.recommended_lens.ilike(term),
            PhotographySpot.recommended_lenses.ilike(term),
            PhotographySpot.recommended_equipment.ilike(term),
            PhotographySpot.lighting_conditions.ilike(term),
            PhotographySpot.weather_conditions.ilike(term),
            PhotographySpot.camera_settings.ilike(term),
            PhotographySpot.accessibility.ilike(term),
            PhotographySpot.photography_tips.ilike(term),
            PhotographySpot.safety_notes.ilike(term),
            PhotographySpot.destination.has(
                Destination.name.ilike(term)
            ),
        )
    )

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(PhotographySpot.name.asc()).all()


def get_photography_spots_by_type(
    photography_type,
    active_only=True,
):
    if not photography_type:
        return []

    query = PhotographySpot.query.filter(
        db.func.lower(PhotographySpot.photography_type)
        == photography_type.strip().lower()
    )

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(PhotographySpot.name.asc()).all()


def get_photography_spots_by_difficulty(
    difficulty,
    active_only=True,
):
    if not difficulty:
        return []

    query = PhotographySpot.query.filter(
        db.func.lower(PhotographySpot.difficulty)
        == difficulty.strip().lower()
    )

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(PhotographySpot.name.asc()).all()


def get_photography_spots_by_destination(
    destination_id,
    active_only=True,
):
    if not destination_id:
        return []

    query = PhotographySpot.query.filter_by(
        destination_id=destination_id
    )

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(PhotographySpot.name.asc()).all()


# =============================================================================
# Validation Helpers
# =============================================================================

def _validate_destination(destination_id):
    if not destination_id:
        raise ValueError("Please select a destination.")

    destination = db.session.get(Destination, destination_id)

    if destination is None:
        raise ValueError("The selected destination does not exist.")

    return destination


def _clean_text(value):
    if isinstance(value, str):
        return value.strip() or None

    return value


# =============================================================================
# Creation
# =============================================================================

def create_photography_spot(
    name,
    slug=None,
    description=None,
    destination_id=None,
    location=None,
    latitude=None,
    longitude=None,
    altitude=None,
    photography_type=None,
    difficulty="Easy",
    best_time=None,
    best_time_to_visit=None,
    best_time_to_photograph=None,
    best_season=None,
    recommended_lens=None,
    recommended_lenses=None,
    recommended_equipment=None,
    lighting_conditions=None,
    weather_conditions=None,
    camera_settings=None,
    accessibility=None,
    photography_tips=None,
    safety_notes=None,
    featured=False,
    active=True,
):
    if not name or not name.strip():
        raise ValueError("Photography spot name is required.")

    name = name.strip()

    if get_photography_spot_by_name(name):
        raise ValueError(
            "A photography spot with this name already exists."
        )

    _validate_destination(destination_id)

    if slug:
        slug = slug.strip()

        if get_photography_spot_by_slug(slug):
            raise ValueError(
                "A photography spot with this slug already exists."
            )

    if latitude is not None and not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if longitude is not None and not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    spot = PhotographySpot(
        name=name,
        slug=_clean_text(slug),
        description=_clean_text(description),

        destination_id=destination_id,
        location=_clean_text(location),

        latitude=latitude,
        longitude=longitude,
        altitude=altitude,

        photography_type=_clean_text(photography_type),
        difficulty=_clean_text(difficulty) or "Easy",

        # Timing
        best_time=_clean_text(best_time),
        best_time_to_visit=_clean_text(best_time_to_visit),
        best_time_to_photograph=_clean_text(
            best_time_to_photograph
        ),
        best_season=_clean_text(best_season),

        # Equipment
        recommended_lens=_clean_text(recommended_lens),
        recommended_lenses=_clean_text(recommended_lenses),
        recommended_equipment=_clean_text(
            recommended_equipment
        ),

        # Conditions
        lighting_conditions=_clean_text(lighting_conditions),
        weather_conditions=_clean_text(weather_conditions),

        # Camera and visitor guidance
        camera_settings=_clean_text(camera_settings),
        accessibility=_clean_text(accessibility),
        photography_tips=_clean_text(photography_tips),
        safety_notes=_clean_text(safety_notes),

        featured=featured,
        active=active,
    )

    db.session.add(spot)
    db.session.commit()

    return spot


# =============================================================================
# Update
# =============================================================================

def update_photography_spot(spot_id, **updates):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    allowed_fields = {
        "name",
        "slug",
        "description",
        "destination_id",
        "location",
        "latitude",
        "longitude",
        "altitude",
        "photography_type",
        "difficulty",

        # Timing
        "best_time",
        "best_time_to_visit",
        "best_time_to_photograph",
        "best_season",

        # Equipment
        "recommended_lens",
        "recommended_lenses",
        "recommended_equipment",

        # Conditions
        "lighting_conditions",
        "weather_conditions",

        # Camera and visitor guidance
        "camera_settings",
        "accessibility",
        "photography_tips",
        "safety_notes",

        "featured",
        "active",
    }

    if "name" in updates:
        new_name = _clean_text(updates["name"])

        if not new_name:
            raise ValueError("Photography spot name is required.")

        existing = get_photography_spot_by_name(new_name)

        if existing and existing.id != spot.id:
            raise ValueError(
                "A photography spot with this name already exists."
            )

        updates["name"] = new_name

    if "slug" in updates:
        new_slug = _clean_text(updates["slug"])

        if new_slug:
            existing = get_photography_spot_by_slug(new_slug)

            if existing and existing.id != spot.id:
                raise ValueError(
                    "A photography spot with this slug already exists."
                )

        updates["slug"] = new_slug

    if "destination_id" in updates:
        _validate_destination(updates["destination_id"])

    if (
        updates.get("latitude") is not None
        and not -90 <= updates["latitude"] <= 90
    ):
        raise ValueError("Latitude must be between -90 and 90.")

    if (
        updates.get("longitude") is not None
        and not -180 <= updates["longitude"] <= 180
    ):
        raise ValueError("Longitude must be between -180 and 180.")

    text_fields = {
        "description",
        "location",
        "photography_type",
        "difficulty",
        "best_time",
        "best_time_to_visit",
        "best_time_to_photograph",
        "best_season",
        "recommended_lens",
        "recommended_lenses",
        "recommended_equipment",
        "lighting_conditions",
        "weather_conditions",
        "camera_settings",
        "accessibility",
        "photography_tips",
        "safety_notes",
    }

    for field, value in updates.items():
        if field not in allowed_fields:
            continue

        if field in text_fields:
            value = _clean_text(value)

        setattr(spot, field, value)

    db.session.commit()

    return spot


# =============================================================================
# Coordinates
# =============================================================================

def update_coordinates(spot_id, latitude, longitude):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    if latitude is not None and not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if longitude is not None and not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    spot.latitude = latitude
    spot.longitude = longitude

    db.session.commit()

    return spot


def clear_coordinates(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    spot.latitude = None
    spot.longitude = None

    db.session.commit()

    return spot


# =============================================================================
# Featured and Status Management
# =============================================================================

def set_photography_spot_featured(spot_id, featured=True):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    spot.featured = featured
    db.session.commit()

    return spot


def feature_photography_spot(spot_id):
    return set_photography_spot_featured(spot_id, True)


def unfeature_photography_spot(spot_id):
    return set_photography_spot_featured(spot_id, False)


def activate_photography_spot(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    spot.active = True
    db.session.commit()

    return spot


def deactivate_photography_spot(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return None

    spot.active = False
    db.session.commit()

    return spot


# =============================================================================
# Experience Associations
# =============================================================================

def get_experience_associations(spot_id, active_only=True):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return []

    query = spot.experiences

    if active_only:
        query = query.filter_by(active=True)

    return query.order_by(
        db.text("stop_order ASC"),
        db.text("id ASC"),
    ).all()


def get_experience_count(spot_id, active_only=True):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return 0

    query = spot.experiences

    if active_only:
        query = query.filter_by(active=True)

    return query.count()


# =============================================================================
# Statistics
# =============================================================================

def get_photography_spot_count(active_only=True):
    query = PhotographySpot.query

    if active_only:
        query = query.filter_by(active=True)

    return query.count()


def get_featured_photography_spot_count():
    return PhotographySpot.query.filter_by(
        active=True,
        featured=True,
    ).count()


def photography_spot_exists(name):
    return get_photography_spot_by_name(name) is not None

# =============================================================================
# Deletion
# =============================================================================
def delete_photography_spot(spot_id):
    spot = get_photography_spot(spot_id)

    if spot is None:
        return False
    db.session.delete(spot)
    db.session.commit()

    return True