from sqlalchemy import or_
from extensions import db
from app.models.stay import Stay
from app.models.stay_room import StayRoom
from app.models.stay_media import StayMedia
from app.models.stay_amenity import StayAmenity
from app.models.stay_room_media import StayRoomMedia
from app.models.stay_room_amenity import StayRoomAmenity
from app.models.stay_review import StayReview

# ============================================================
# PUBLIC STAY LISTING
# ============================================================
def get_public_stays(
    search=None,
    destination_id=None,
    accommodation_type=None,
    featured=None,
    limit=None,
):
    """
    Return active stays suitable for public display.

    Optional filters:
        search
        destination_id
        accommodation_type
        featured
        limit
    """
    query = Stay.query.filter_by(active=True)

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Stay.property_name.ilike(search_term),
                Stay.short_description.ilike(search_term),
                Stay.description.ilike(search_term),
                Stay.location.ilike(search_term),
            )
        )

    if destination_id:
        query = query.filter(
            Stay.destination_id == destination_id
        )

    if accommodation_type:
        query = query.filter(
            Stay.accommodation_type == accommodation_type
        )

    if featured is not None:
        query = query.filter(
            Stay.featured == featured
        )

    query = query.order_by(
        Stay.display_order.asc(),
        Stay.property_name.asc(),
        Stay.id.asc(),
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_featured_stays(limit=6):
    """
    Return active featured stays for the public homepage
    or public stays landing page.
    """
    return get_public_stays(
        featured=True,
        limit=limit,
    )


def get_stay_by_slug(slug):
    """
    Return a single active stay by slug.
    """
    if not slug:
        return None

    return Stay.query.filter(
        Stay.slug == slug,
        Stay.active.is_(True),
    ).first()


def get_stay_by_id(stay_id):
    """
    Return a single active stay by ID.
    """
    return Stay.query.filter(
        Stay.id == stay_id,
        Stay.active.is_(True),
    ).first()


# ============================================================
# PUBLIC STAY ROOMS
# ============================================================

def get_public_rooms(stay_id):
    """
    Return active rooms belonging to an active stay.
    """
    stay = get_stay_by_id(stay_id)

    if not stay:
        return []

    return StayRoom.query.filter(
        StayRoom.stay_id == stay.id,
        StayRoom.active.is_(True),
    ).order_by(
        StayRoom.display_order.asc(),
        StayRoom.name.asc(),
        StayRoom.id.asc(),
    ).all()


def get_room_by_slug(stay_id, slug):
    """
    Return an active room belonging to an active stay.
    """
    stay = get_stay_by_id(stay_id)

    if not stay or not slug:
        return None

    return StayRoom.query.filter(
        StayRoom.stay_id == stay.id,
        StayRoom.slug == slug,
        StayRoom.active.is_(True),
    ).first()


def get_room_by_id(room_id):
    """
    Return an active room whose parent stay is also active.
    """
    room = StayRoom.query.filter(
        StayRoom.id == room_id,
        StayRoom.active.is_(True),
    ).first()

    if not room:
        return None

    stay = get_stay_by_id(room.stay_id)

    if not stay:
        return None

    return room


# ============================================================
# STAY MEDIA
# ============================================================

def get_stay_media(stay_id, usage=None):
    """
    Return active media assigned to a public stay.
    """
    stay = get_stay_by_id(stay_id)

    if not stay:
        return []

    query = StayMedia.query.filter(
        StayMedia.stay_id == stay.id,
        StayMedia.active.is_(True),
    )

    if usage:
        query = query.filter(
            StayMedia.usage == usage
        )

    return query.order_by(
        StayMedia.display_order.asc(),
        StayMedia.id.asc(),
    ).all()


def get_stay_hero_media(stay_id):
    """
    Return the first active hero image/media for a stay.
    """
    media = get_stay_media(
        stay_id,
        usage="hero",
    )

    if media:
        return media[0]

    media = get_stay_media(
        stay_id,
        usage="banner",
    )

    if media:
        return media[0]

    media = get_stay_media(
        stay_id,
        usage="thumbnail",
    )

    if media:
        return media[0]

    gallery = get_stay_media(
        stay_id,
        usage="gallery",
    )

    return gallery[0] if gallery else None


def get_stay_gallery(stay_id):
    """
    Return public gallery media for a stay.
    """
    media = get_stay_media(stay_id)

    return [
        item
        for item in media
        if item.usage in {
            "hero",
            "banner",
            "thumbnail",
            "gallery",
        }
    ]


# ============================================================
# STAY AMENITIES
# ============================================================

def get_stay_amenities(stay_id, featured_only=False):
    """
    Return active amenities belonging to a public stay.
    """
    stay = get_stay_by_id(stay_id)

    if not stay:
        return []

    query = StayAmenity.query.filter(
        StayAmenity.stay_id == stay.id,
        StayAmenity.active.is_(True),
    )

    if featured_only:
        query = query.filter(
            StayAmenity.featured.is_(True)
        )

    return query.order_by(
        StayAmenity.display_order.asc(),
        StayAmenity.name.asc(),
        StayAmenity.id.asc(),
    ).all()


def get_room_amenities(room_id):
    """
    Return active amenities assigned to a public room.
    """
    room = get_room_by_id(room_id)

    if not room:
        return []

    return StayRoomAmenity.query.filter(
        StayRoomAmenity.room_id == room.id,
        StayRoomAmenity.active.is_(True),
    ).order_by(
        StayRoomAmenity.display_order.asc(),
        StayRoomAmenity.name.asc(),
        StayRoomAmenity.id.asc(),
    ).all()


# ============================================================
# ROOM MEDIA
# ============================================================

def get_room_media(room_id, usage=None):
    """
    Return active media assigned to a public room.
    """
    room = get_room_by_id(room_id)

    if not room:
        return []

    query = StayRoomMedia.query.filter(
        StayRoomMedia.room_id == room.id,
        StayRoomMedia.active.is_(True),
    )

    if usage:
        query = query.filter(
            StayRoomMedia.usage == usage
        )

    return query.order_by(
        StayRoomMedia.display_order.asc(),
        StayRoomMedia.id.asc(),
    ).all()


def get_room_hero_media(room_id):
    """
    Return the preferred hero/thumbnail/gallery image for a room.
    """
    media = get_room_media(
        room_id,
        usage="hero",
    )

    if media:
        return media[0]

    media = get_room_media(
        room_id,
        usage="thumbnail",
    )

    if media:
        return media[0]

    media = get_room_media(
        room_id,
        usage="gallery",
    )

    return media[0] if media else None


def get_room_gallery(room_id):
    """
    Return all active public media for a room.
    """
    return get_room_media(room_id)


# ============================================================
# STAY REVIEWS
# ============================================================

def get_stay_reviews(
    stay_id,
    featured_only=False,
    limit=None,
):
    """
    Return approved and visible reviews for a public stay.
    """
    stay = get_stay_by_id(stay_id)

    if not stay:
        return []

    query = StayReview.query.filter(
        StayReview.stay_id == stay.id,
        StayReview.status == "approved",
    )

    if featured_only:
        query = query.filter(
            StayReview.featured.is_(True)
        )

    query = query.order_by(
        StayReview.stay_date.desc(),
        StayReview.id.desc(),
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_stay_average_rating(stay_id):
    """
    Calculate the average approved public review rating.
    """
    reviews = get_stay_reviews(stay_id)

    if not reviews:
        return None

    total = sum(
        review.rating
        for review in reviews
        if review.rating is not None
    )

    rated_reviews = [
        review
        for review in reviews
        if review.rating is not None
    ]

    if not rated_reviews:
        return None

    return round(
        total / len(rated_reviews),
        1,
    )


def get_stay_review_count(stay_id):
    """
    Return the number of approved public reviews.
    """
    return len(get_stay_reviews(stay_id))


# ============================================================
# PUBLIC STAY DETAIL DATA
# ============================================================

def get_stay_detail(stay):
    """
    Build the public detail data required by the Stay detail
    page.

    This keeps the public route thin and gives templates a
    predictable data structure.
    """
    if not stay or not stay.active:
        return None

    rooms = get_public_rooms(stay.id)
    media = get_stay_media(stay.id)
    gallery = get_stay_gallery(stay.id)
    amenities = get_stay_amenities(stay.id)
    featured_amenities = get_stay_amenities(
        stay.id,
        featured_only=True,
    )
    reviews = get_stay_reviews(stay.id)
    featured_reviews = get_stay_reviews(
        stay.id,
        featured_only=True,
        limit=3,
    )

    return {
        "stay": stay,
        "rooms": rooms,
        "media": media,
        "gallery": gallery,
        "hero_media": get_stay_hero_media(stay.id),
        "amenities": amenities,
        "featured_amenities": featured_amenities,
        "reviews": reviews,
        "featured_reviews": featured_reviews,
        "average_rating": get_stay_average_rating(stay.id),
        "review_count": len(reviews),
    }


def get_room_detail(room):
    """
    Build the public detail data required by the Room detail page.
    """
    if not room or not room.active:
        return None

    stay = get_stay_by_id(room.stay_id)

    if not stay:
        return None

    media = get_room_media(room.id)
    amenities = get_room_amenities(room.id)

    return {
        "stay": stay,
        "room": room,
        "media": media,
        "gallery": get_room_gallery(room.id),
        "hero_media": get_room_hero_media(room.id),
        "amenities": amenities,
    }


# ============================================================
# SEARCH HELPERS
# ============================================================

def search_public_stays(search_term):
    """
    Search active public stays by property name, location,
    accommodation type, and description.
    """
    if not search_term:
        return get_public_stays()

    search_term = search_term.strip()

    if not search_term:
        return get_public_stays()

    pattern = f"%{search_term}%"

    return Stay.query.filter(
        Stay.active.is_(True),
        or_(
            Stay.property_name.ilike(pattern),
            Stay.location.ilike(pattern),
            Stay.accommodation_type.ilike(pattern),
            Stay.short_description.ilike(pattern),
            Stay.description.ilike(pattern),
        ),
    ).order_by(
        Stay.display_order.asc(),
        Stay.property_name.asc(),
        Stay.id.asc(),
    ).all()


def get_public_accommodation_types():
    """
    Return accommodation types currently represented by active
    public stays.
    """
    rows = (
        db.session.query(Stay.accommodation_type)
        .filter(
            Stay.active.is_(True),
            Stay.accommodation_type.isnot(None),
        )
        .distinct()
        .order_by(
            Stay.accommodation_type.asc()
        )
        .all()
    )

    return [
        row[0]
        for row in rows
        if row[0]
    ]


# ============================================================
# STAY SUMMARY
# ============================================================

def get_stay_summary(stay_id):
    """
    Return useful summary information for a public stay card
    or detail page.
    """
    stay = get_stay_by_id(stay_id)

    if not stay:
        return None

    rooms = get_public_rooms(stay.id)
    amenities = get_stay_amenities(stay.id)
    reviews = get_stay_reviews(stay.id)

    return {
        "stay": stay,
        "room_count": len(rooms),
        "amenity_count": len(amenities),
        "review_count": len(reviews),
        "average_rating": get_stay_average_rating(stay.id),
        "hero_media": get_stay_hero_media(stay.id),
    }