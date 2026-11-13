"""
THE UNCHARTED ROUTE — STAYS CATALOGUE POPULATION
================================================

Initial six-property Stay catalogue.

Scope
-----
1. Giraffe Manor
2. JW Marriott Hotel Nairobi
3. Skynest Residences by CityBlue
4. Escada Apartments
5. Mövenpick Hotel & Residences Nairobi
6. Fairmont Mount Kenya Safari Club

This script is intentionally conservative.

It:
- creates missing Stay records
- updates/enhances the two existing catalogue records
- preserves existing StayRoom records
- adds missing StayRoom records
- adds missing property amenities
- adds missing room amenities
- uses StayRoom.nightly_rate for base catalogue pricing
- reuses existing Destination records
- creates Mount Kenya Destination only when --apply is used
- creates NO media
- creates NO reviews
- creates NO bookings
- creates NO inquiries
- does not create a StayRate model
- does not modify existing operational/customer bookings

Dry run is genuinely read-only:
- no db.session.add()
- no db.session.flush()
- no database UPDATE
- no database INSERT
- no database DELETE
- no commit

Pricing
-------
Rates below are indicative TUR catalogue/planning benchmarks, not supplier
confirmation. They should be commercially reviewed before being presented
as final bookable supplier rates.

Usage
-----
Dry run:
    python scripts/populate_stays_catalogue.py

Apply:
    python scripts/populate_stays_catalogue.py --apply
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import text

# =============================================================================
# PROJECT BOOTSTRAP
# =============================================================================
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("FLASK_ENV", "development")

from app import create_app
from extensions import db

from app.models import Destination
from app.models.stay import Stay
from app.models.stay_room import StayRoom
from app.models.stay_amenity import StayAmenity
from app.models.stay_room_amenity import StayRoomAmenity


# =============================================================================
# CONFIGURATION
# =============================================================================

RATE_MODE = "INDICATIVE_PLANNING_BENCHMARK"

TARGET_STAYS = [
    "Giraffe Manor",
    "JW Marriott Hotel Nairobi",
    "Skynest Residences by CityBlue",
    "Escada Apartments",
    "Mövenpick Hotel & Residences Nairobi",
    "Fairmont Mount Kenya Safari Club",
]


# =============================================================================
# HELPERS
# =============================================================================

def slugify(value: str) -> str:
    """Create a stable URL slug without introducing a dependency."""

    value = value.strip().lower()
    value = value.replace("ö", "o")
    value = value.replace("é", "e")
    value = value.replace("’", "'")
    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-")


def money(value: float | int | Decimal) -> float:
    """Convert a numeric planning rate into a float."""

    return float(Decimal(str(value)))


def print_header(title: str) -> None:
    print()
    print("=" * 110)
    print(title)
    print("=" * 110)


def print_section(title: str) -> None:
    print()
    print("-" * 110)
    print(title)
    print("-" * 110)


# =============================================================================
# DESTINATIONS
# =============================================================================

def destination_id_for(
    *,
    preferred_slugs: list[str],
    preferred_names: list[str],
) -> int | None:
    """
    Resolve an existing destination.

    This helper NEVER creates or modifies destinations.
    """

    rows = db.session.execute(
        text(
            """
            SELECT id, name, slug
            FROM destinations
            ORDER BY id ASC
            """
        )
    ).mappings().all()

    normalized_slugs = {
        slug.strip().lower()
        for slug in preferred_slugs
    }

    normalized_names = {
        name.strip().lower()
        for name in preferred_names
    }

    for row in rows:
        if (row["slug"] or "").strip().lower() in normalized_slugs:
            return int(row["id"])

    for row in rows:
        if (row["name"] or "").strip().lower() in normalized_names:
            return int(row["id"])

    return None


def create_mount_kenya_destination() -> int:
    """
    Create the Mount Kenya destination.

    IMPORTANT:
    This function is only called during --apply.

    The destination is created in the same transaction as the Fairmont
    Mount Kenya Safari Club Stay.
    """

    existing = destination_id_for(
        preferred_slugs=["mount-kenya"],
        preferred_names=["Mount Kenya"],
    )

    if existing is not None:
        return existing

    print("  CREATE DESTINATION | Mount Kenya")

    destination = Destination(
        name="Mount Kenya",
        slug="mount-kenya",
        country="Kenya",
        county="Laikipia",
        region="Mount Kenya",
        short_description=(
            "A spectacular highland destination centred around Mount Kenya, "
            "with mountain landscapes, wildlife, conservation, adventure "
            "and distinctive luxury retreats."
        ),
        description=(
            "Mount Kenya is one of Kenya's defining highland destinations, "
            "combining dramatic mountain landscapes with wildlife, "
            "conservation, outdoor adventure and distinctive luxury stays.\n\n"
            "The wider Mount Kenya and Laikipia landscape provides access to "
            "nature experiences, conservation initiatives, ranches, wildlife "
            "areas and premium retreats around Nanyuki and the mountain's "
            "foothills.\n\n"
            "For The Uncharted Route, Mount Kenya provides a natural base "
            "for destination-led stays and experiences centred on nature, "
            "conservation, heritage and outdoor adventure."
        ),
        latitude=-0.1521,
        longitude=37.3084,
        meta_title="Mount Kenya | The Uncharted Route",
        meta_description=(
            "Discover Mount Kenya, a highland destination combining "
            "spectacular mountain landscapes, wildlife, conservation, "
            "adventure and luxury stays."
        ),
        featured=True,
        show_on_homepage=False,
        active=True,
    )

    db.session.add(destination)
    db.session.flush()

    return destination.id


def resolve_destinations(
    population: "StayPopulation",
) -> dict[str, int]:
    """
    Resolve destinations required by the initial Stay catalogue.

    Nairobi:
        Must already exist.

    Mount Kenya:
        Reused when already present.
        Created only during --apply.
        Reported as planned during dry-run.

    Dry-run never creates a Destination.
    """

    destinations: dict[str, int] = {}

    # -------------------------------------------------------------------------
    # Nairobi
    # -------------------------------------------------------------------------

    nairobi_id = destination_id_for(
        preferred_slugs=[
            "nairobi",
            "nairobi-city",
        ],
        preferred_names=[
            "Nairobi",
            "Nairobi City",
        ],
    )

    if nairobi_id is None:
        raise RuntimeError(
            "Required Nairobi destination does not exist. "
            "The Stay population will not create Nairobi automatically."
        )

    destinations["nairobi"] = nairobi_id

    print(
        f"  Nairobi destination       : EXISTING — ID={nairobi_id}"
    )

    # -------------------------------------------------------------------------
    # Mount Kenya
    # -------------------------------------------------------------------------

    mount_kenya_id = destination_id_for(
        preferred_slugs=[
            "mount-kenya",
        ],
        preferred_names=[
            "Mount Kenya",
        ],
    )

    if mount_kenya_id is not None:
        destinations["mount-kenya"] = mount_kenya_id

        print(
            f"  Mount Kenya destination   : EXISTING — ID={mount_kenya_id}"
        )

        return destinations

    if population.apply_changes:
        mount_kenya_id = create_mount_kenya_destination()

        print(
            f"  Mount Kenya destination   : CREATED — ID={mount_kenya_id}"
        )

        destinations["mount-kenya"] = mount_kenya_id

        return destinations

    print(
        "  Mount Kenya destination   : "
        "MISSING — WOULD BE CREATED ON APPLY"
    )

    # Sentinel is used ONLY for dry-run planning.
    # It is never written to the database.
    destinations["mount-kenya"] = -1

    return destinations


# =============================================================================
# LOOKUPS
# =============================================================================

def find_stay(slug: str) -> Stay | None:
    return Stay.query.filter_by(slug=slug).first()


def find_room(
    stay_id: int,
    slug: str,
) -> StayRoom | None:
    return StayRoom.query.filter_by(
        stay_id=stay_id,
        slug=slug,
    ).first()


def find_property_amenity(
    stay_id: int,
    name: str,
) -> StayAmenity | None:
    return StayAmenity.query.filter(
        StayAmenity.stay_id == stay_id,
        db.func.lower(StayAmenity.name) == name.lower(),
    ).first()


def find_room_amenity(
    room_id: int,
    name: str,
) -> StayRoomAmenity | None:
    return StayRoomAmenity.query.filter(
        StayRoomAmenity.room_id == room_id,
        db.func.lower(StayRoomAmenity.name) == name.lower(),
    ).first()


def update_if_changed(
    obj: Any,
    field: str,
    value: Any,
    *,
    force: bool = False,
) -> bool:
    """
    Update a field if required.

    force=False:
        only fills blank values.

    force=True:
        explicitly updates catalogue corrections.

    This helper is only used during --apply.
    """

    current = getattr(obj, field, None)

    if force:
        if current != value:
            setattr(obj, field, value)
            return True

        return False

    if current in (None, "", 0) and value not in (None, ""):
        setattr(obj, field, value)
        return True

    return False


def make_room_code(
    stay: Stay,
    slug: str,
) -> str:
    """
    Generate a deterministic room code under VARCHAR(40).
    """

    stay_code = (
        (stay.stay_code or "TUR-STAY")
        .upper()
    )

    short_slug = (
        re.sub(
            r"[^A-Z0-9]+",
            "-",
            slug.upper(),
        )
        .strip("-")
    )

    code = f"{stay_code}-{short_slug}"

    if len(code) <= 40:
        return code

    return code[:40]


# =============================================================================
# STAY DEFINITIONS
# =============================================================================

STAY_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "Giraffe Manor",
        "slug": "giraffe-manor",
        "stay_code": "STY-001",
        "accommodation_type": "Boutique Hotel",
        "destination_key": "nairobi",
        "location": "Karen, Nairobi",
        "address": "Karen, Nairobi, Kenya",
        "short_description": (
            "An iconic Nairobi wildlife stay where elegant accommodation, "
            "resident Rothschild's giraffes and conservation come together "
            "in a remarkable manor setting."
        ),
        "description": (
            "Giraffe Manor is one of Nairobi's most distinctive luxury stays, "
            "combining an elegant heritage setting with an unforgettable "
            "wildlife experience.\n\n"
            "Set within a leafy Karen estate, the property is known for its "
            "resident Rothschild's giraffes and the extraordinary opportunity "
            "to experience them as part of the rhythm of a stay. Breakfast "
            "and other moments at the manor can become wildlife encounters, "
            "turning accommodation itself into part of the journey.\n\n"
            "The property offers an intimate, characterful atmosphere with "
            "heritage architecture, gardens, refined dining and access to "
            "the wider Giraffe Centre experience. Guests can also access "
            "The Retreat at Giraffe Manor for additional wellness and "
            "leisure facilities.\n\n"
            "For travellers combining Nairobi with a wildlife-led escape, "
            "Giraffe Manor offers a rare stay where conservation, hospitality "
            "and the city's wildlife story meet."
        ),
        "maximum_guests": 20,
        "maximum_adults": 20,
        "maximum_children": 6,
        "total_rooms": 12,
        "minimum_nights": 1,
        "check_in_time": "12:00",
        "check_out_time": "10:00",
        "contact_phone": "+254 111 033 900",
        "contact_email": "stay@thesafaricollection.com",
        "website_url": (
            "https://www.thesafaricollection.com/properties/giraffe-manor/"
        ),
        "meta_title": "Giraffe Manor Nairobi | The Uncharted Route",
        "meta_description": (
            "Discover Giraffe Manor in Nairobi, an iconic luxury wildlife "
            "stay combining elegant accommodation, resident giraffes and "
            "conservation."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 1,
        "rooms": [
            {
                "name": "Superior Room",
                "slug": "superior-room",
                "room_type": "Superior Room",
                "short_description": (
                    "An elegant manor accommodation option combining "
                    "heritage character, refined interiors and access to "
                    "the property's distinctive wildlife experience."
                ),
                "description": (
                    "The Superior Room provides an intimate stay within the "
                    "heritage character of Giraffe Manor. Guests enjoy an "
                    "elegant private space while remaining immersed in the "
                    "property's gardens, hospitality and wildlife setting."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 10,
                "nightly_rate": 1413,
                "currency": "USD",
                "meal_plan": "Fully Inclusive",
                "bed_configuration": "Double or King Bed",
                "size_description": "Property-specific room size",
                "featured": True,
                "display_order": 1,
            },
            {
                "name": "Superior Family Suite",
                "slug": "superior-family-suite",
                "room_type": "Family Suite",
                "short_description": (
                    "A spacious family suite designed for a distinctive "
                    "Giraffe Manor stay with additional sleeping capacity."
                ),
                "description": (
                    "The Superior Family Suite provides a more spacious "
                    "family-oriented accommodation configuration with "
                    "private en-suite sleeping areas and access to the "
                    "same signature wildlife experience."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 2,
                "nightly_rate": 4832,
                "currency": "USD",
                "meal_plan": "Fully Inclusive",
                "bed_configuration": "Multiple Beds",
                "size_description": "Property-specific suite size",
                "display_order": 2,
            },
        ],
        "amenities": [
            {
                "name": "Resident Rothschild's Giraffes",
                "category": "Wildlife",
                "icon": "bird",
                "description": (
                    "A signature wildlife experience centred around the "
                    "property's resident giraffes."
                ),
                "featured": True,
            },
            {
                "name": "Giraffe Breakfast Experience",
                "category": "Experience",
                "icon": "coffee",
                "description": (
                    "A distinctive dining experience where resident giraffes "
                    "may visit during breakfast."
                ),
                "featured": True,
            },
            {
                "name": "The Retreat",
                "category": "Wellness",
                "icon": "sparkles",
                "description": (
                    "Access to additional wellness and leisure facilities "
                    "at The Retreat."
                ),
            },
            {
                "name": "21 Metre Infinity Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "A 21-metre infinity pool at The Retreat overlooking "
                    "the giraffe sanctuary."
                ),
            },
            {
                "name": "Spa and Wellness",
                "category": "Wellness",
                "icon": "heart",
                "description": (
                    "Wellness facilities including spa treatments, sauna, "
                    "steam room, gym and hot tub."
                ),
            },
            {
                "name": "Garden and Outdoor Spaces",
                "category": "Property",
                "icon": "trees",
                "description": (
                    "Leafy landscaped grounds providing a tranquil setting "
                    "around the manor."
                ),
            },
            {
                "name": "Conservation Experience",
                "category": "Conservation",
                "icon": "leaf",
                "description": (
                    "A stay connected to giraffe conservation and the work "
                    "of the African Fund for Endangered Wildlife."
                ),
                "featured": True,
            },
        ],
    },
    {
        "name": "JW Marriott Hotel Nairobi",
        "slug": "jw-marriott-hotel-nairobi",
        "stay_code": "TUR-STAY-002",
        "accommodation_type": "Hotel",
        "destination_key": "nairobi",
        "location": "Westlands, Nairobi",
        "address": "Chiromo Lane, Westlands, Nairobi, Kenya",
        "short_description": (
            "A five-star city hotel in Westlands offering contemporary "
            "accommodation, skyline views, curated dining, wellness "
            "facilities and serviced residences."
        ),
        "description": (
            "JW Marriott Hotel Nairobi is a contemporary luxury city retreat "
            "in Westlands, combining refined accommodation, panoramic views "
            "and a broad collection of dining, wellness and business "
            "facilities.\n\n"
            "The hotel provides a choice of guest rooms and suites alongside "
            "JW Marriott Residences, including furnished one-, two- and "
            "three-bedroom residential layouts for guests seeking additional "
            "space and a longer-stay feel.\n\n"
            "Guests can unwind at the heated infinity pool, visit Spa by JW, "
            "use the fitness centre or explore the hotel's dining venues. "
            "The property also provides dedicated meeting and event spaces "
            "for corporate gatherings, conferences, celebrations and "
            "weddings.\n\n"
            "Its Westlands location makes it well suited to both business "
            "and leisure travellers seeking a polished Nairobi base with "
            "easy access to the city's commercial and cultural districts."
        ),
        "maximum_guests": 4,
        "maximum_adults": 4,
        "maximum_children": 2,
        "total_rooms": 315,
        "minimum_nights": 1,
        "check_in_time": "15:00",
        "check_out_time": "12:00",
        "contact_phone": "0719 010888",
        "contact_email": "customer.care@marriott.com",
        "website_url": (
            "https://www.marriott.com/en-us/hotels/nbojw-jw-marriott-hotel-nairobi/"
        ),
        "meta_title": "JW Marriott Hotel Nairobi | Luxury Stay in Westlands",
        "meta_description": (
            "Explore JW Marriott Hotel Nairobi in Westlands, with luxury "
            "guest rooms, serviced residences, curated dining, wellness "
            "facilities and panoramic city views."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 2,
        "rooms": [
            {
                "name": "Junior Suite",
                "slug": "junior-suite",
                "room_type": "Junior Suite",
                "short_description": (
                    "A spacious 69 m² junior suite featuring a king bedroom, "
                    "separate living area and Nairobi views."
                ),
                "description": (
                    "The Junior Suite offers a residential-style setting "
                    "with a king bedroom and separate living area. Its "
                    "69 m² layout provides additional space to relax, work "
                    "or enjoy the Nairobi skyline."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 0,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 450,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "size_description": "69 m²",
                "display_order": 1,
                "preserve_existing": True,
            },
            {
                "name": "Deluxe King Room",
                "slug": "deluxe-king-room",
                "room_type": "Deluxe Room",
                "short_description": (
                    "A contemporary king room designed for a comfortable "
                    "luxury city stay in Westlands."
                ),
                "description": (
                    "The Deluxe King Room provides a polished base for "
                    "business and leisure travellers, combining a king bed, "
                    "contemporary interiors and access to the hotel's wider "
                    "dining, wellness and hospitality facilities."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 325,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "display_order": 2,
            },
            {
                "name": "One Bedroom Residence",
                "slug": "one-bedroom-residence",
                "room_type": "Serviced Residence",
                "short_description": (
                    "A furnished one-bedroom residence with separate "
                    "living and dining areas and a fully equipped kitchen."
                ),
                "description": (
                    "The One Bedroom Residence is designed for guests who "
                    "want the space and flexibility of a private residence "
                    "within a five-star hotel environment. The layout "
                    "includes separate living and dining areas and a "
                    "fully equipped kitchen."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 525,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "display_order": 3,
            },
            {
                "name": "Two Bedroom Residence",
                "slug": "two-bedroom-residence",
                "room_type": "Serviced Residence",
                "short_description": (
                    "A spacious furnished residence designed for families, "
                    "groups and longer luxury stays."
                ),
                "description": (
                    "The Two Bedroom Residence offers additional privacy "
                    "and living space for families or small groups, with "
                    "separate living and dining areas and a fully equipped "
                    "kitchen."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 750,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Beds",
                "display_order": 4,
            },
            {
                "name": "Three Bedroom Residence",
                "slug": "three-bedroom-residence",
                "room_type": "Serviced Residence",
                "short_description": (
                    "A premium multi-bedroom residence offering generous "
                    "space for families and extended stays."
                ),
                "description": (
                    "The Three Bedroom Residence provides a larger "
                    "residential layout for families or groups seeking "
                    "privacy, living space and hotel services in Westlands."
                ),
                "maximum_guests": 6,
                "maximum_adults": 6,
                "maximum_children": 3,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 1050,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Beds",
                "display_order": 5,
            },
        ],
        "amenities": [
            {
                "name": "Heated Infinity Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "A heated infinity pool with elevated Nairobi skyline views."
                ),
                "featured": True,
            },
            {
                "name": "Spa by JW",
                "category": "Wellness",
                "icon": "sparkles",
                "description": (
                    "A dedicated hotel spa offering massages, facials and "
                    "body treatments."
                ),
                "featured": True,
            },
            {
                "name": "Fitness Centre",
                "category": "Wellness",
                "icon": "dumbbells",
                "description": (
                    "A fully equipped fitness centre for cardio and strength "
                    "training."
                ),
            },
            {
                "name": "Executive Lounge",
                "category": "Business",
                "icon": "briefcase",
                "description": (
                    "A dedicated executive hospitality space for eligible guests."
                ),
            },
            {
                "name": "Multiple Dining Venues",
                "category": "Dining",
                "icon": "utensils",
                "description": (
                    "A collection of restaurants, cafés, bars and lounges "
                    "across the property."
                ),
                "featured": True,
            },
            {
                "name": "Meeting and Event Facilities",
                "category": "Business",
                "icon": "presentation",
                "description": (
                    "Ballroom, boardrooms and meeting spaces for corporate "
                    "events, celebrations and weddings."
                ),
            },
        ],
    },
    {
        "name": "Skynest Residences by CityBlue",
        "slug": "skynest-residences-by-cityblue",
        "stay_code": "TUR-STAY-003",
        "accommodation_type": "Serviced Residence",
        "destination_key": "nairobi",
        "location": "Westlands, Nairobi",
        "address": "Mkungu Close, Westlands, Nairobi, Kenya",
        "short_description": (
            "Premium furnished residences in Westlands with spacious "
            "apartment layouts, rooftop leisure facilities and city living."
        ),
        "description": (
            "Skynest Residences by CityBlue is a premium serviced residence "
            "in Westlands designed around the flexibility of a private "
            "apartment combined with hotel-style services and amenities.\n\n"
            "The residence offers furnished one-, one-and-a-half-, two-, "
            "three- and four-bedroom layouts with living spaces, kitchens "
            "or kitchenettes and private residential comforts suited to "
            "short stays, business travel, families and longer visits.\n\n"
            "Residents can make use of the rooftop heated infinity pool, "
            "fitness and wellness facilities, squash court, games areas and "
            "social spaces. Slate Kitchen & Bar provides an on-site dining "
            "option.\n\n"
            "The Westlands location places guests close to major shopping, "
            "business and entertainment destinations while retaining the "
            "privacy and flexibility of a residential stay."
        ),
        "maximum_guests": 8,
        "maximum_adults": 8,
        "maximum_children": 4,
        "total_rooms": 249,
        "minimum_nights": 1,
        "check_in_time": "14:00",
        "check_out_time": "11:00",
        "contact_phone": None,
        "contact_email": None,
        "website_url": (
            "https://www.citybluehotels.com/skynest-residences-by-cityblue-nairobi"
        ),
        "meta_title": "Skynest Residences Nairobi | The Uncharted Route",
        "meta_description": (
            "Stay at Skynest Residences by CityBlue in Westlands, with "
            "furnished apartments, rooftop leisure facilities, wellness "
            "amenities and flexible residential living."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 3,
        "rooms": [
            {
                "name": "One Bedroom Residence",
                "slug": "one-bedroom-residence",
                "room_type": "One Bedroom Residence",
                "short_description": (
                    "A fully furnished one-bedroom residence with a "
                    "comfortable private living space."
                ),
                "description": (
                    "The One Bedroom Residence is suited to couples, "
                    "business travellers and longer-stay guests seeking "
                    "the privacy and flexibility of a furnished apartment."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 130,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "1 King Bed",
                "display_order": 1,
            },
            {
                "name": "One and a Half Bedroom Residence",
                "slug": "one-and-a-half-bedroom-residence",
                "room_type": "1.5 Bedroom Residence",
                "short_description": (
                    "A flexible furnished residence offering additional "
                    "space beyond a conventional one-bedroom apartment."
                ),
                "description": (
                    "The One and a Half Bedroom Residence provides additional "
                    "flexibility for guests who want more space while retaining "
                    "the convenience of a serviced residential property."
                ),
                "maximum_guests": 3,
                "maximum_adults": 3,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 155,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "King Bed",
                "display_order": 2,
            },
            {
                "name": "Two Bedroom Residence",
                "slug": "two-bedroom-residence",
                "room_type": "Two Bedroom Residence",
                "short_description": (
                    "A spacious furnished two-bedroom apartment suited "
                    "to families and small groups."
                ),
                "description": (
                    "The Two Bedroom Residence provides separate sleeping "
                    "spaces and generous shared living areas for families, "
                    "friends or business groups travelling together."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 190,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "King Beds",
                "display_order": 3,
            },
            {
                "name": "Three Bedroom Residence",
                "slug": "three-bedroom-residence",
                "room_type": "Three Bedroom Residence",
                "short_description": (
                    "A large furnished residence offering privacy and "
                    "shared living space for families and groups."
                ),
                "description": (
                    "The Three Bedroom Residence is designed for guests "
                    "who need substantial residential space, making it "
                    "particularly suitable for families and longer stays."
                ),
                "maximum_guests": 6,
                "maximum_adults": 6,
                "maximum_children": 3,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 250,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "King Beds",
                "display_order": 4,
            },
            {
                "name": "Four Bedroom Residence",
                "slug": "four-bedroom-residence",
                "room_type": "Four Bedroom Residence",
                "short_description": (
                    "The largest residential configuration, suited to "
                    "families and groups seeking extensive private space."
                ),
                "description": (
                    "The Four Bedroom Residence provides a spacious private "
                    "base for larger families and groups, combining multiple "
                    "bedrooms with shared residential living areas."
                ),
                "maximum_guests": 8,
                "maximum_adults": 8,
                "maximum_children": 4,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 325,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "King Beds",
                "display_order": 5,
            },
        ],
        "amenities": [
            {
                "name": "Rooftop Heated Infinity Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "A rooftop heated infinity pool overlooking the Westlands skyline."
                ),
                "featured": True,
            },
            {
                "name": "Fitness Centre",
                "category": "Wellness",
                "icon": "dumbbells",
                "description": (
                    "A resident fitness facility supporting everyday workouts."
                ),
            },
            {
                "name": "Sauna and Steam Room",
                "category": "Wellness",
                "icon": "sparkles",
                "description": (
                    "Wellness facilities designed for post-workout relaxation."
                ),
            },
            {
                "name": "Squash Court",
                "category": "Recreation",
                "icon": "circle",
                "description": (
                    "An on-site squash facility for active guests."
                ),
            },
            {
                "name": "Games Room",
                "category": "Recreation",
                "icon": "gamepad",
                "description": (
                    "Indoor recreational facilities including social games."
                ),
            },
            {
                "name": "Slate Kitchen & Bar",
                "category": "Dining",
                "icon": "utensils",
                "description": (
                    "An on-site restaurant and bar providing a convenient "
                    "dining option for residents and guests."
                ),
                "featured": True,
            },
            {
                "name": "Secure Parking",
                "category": "Services",
                "icon": "car",
                "description": (
                    "On-site parking for residents and visiting guests."
                ),
            },
            {
                "name": "24-Hour Reception",
                "category": "Services",
                "icon": "clock",
                "description": (
                    "Round-the-clock reception and guest support."
                ),
            },
        ],
    },
    {
        "name": "Escada Apartments",
        "slug": "escada-apartments",
        "stay_code": "TUR-STAY-004",
        "accommodation_type": "Serviced Apartments",
        "destination_key": "nairobi",
        "location": "Westlands, Nairobi",
        "address": "Lantana Road, Westlands, Nairobi, Kenya",
        "short_description": (
            "High-end furnished apartments in Westlands with a rooftop "
            "pool, 270 rooftop restaurant, secure parking and residential privacy."
        ),
        "description": (
            "Escada Apartments is a premium serviced-apartment property "
            "in Westlands, offering furnished accommodation for business, "
            "leisure and extended stays.\n\n"
            "The property provides Mini One Bedroom, One Bedroom and Two "
            "Bedroom apartment configurations, giving guests the flexibility "
            "of private living and dining areas alongside fully equipped "
            "kitchens.\n\n"
            "Guests can enjoy the rooftop swimming pool and rooftop leisure "
            "spaces, dine at 270 Rooftop Restaurant and make use of the "
            "property's gym and secure parking facilities.\n\n"
            "With 24-hour security, CCTV and backup power, Escada provides "
            "a practical premium base in Westlands, close to the area's "
            "business, shopping and dining destinations."
        ),
        "maximum_guests": 4,
        "maximum_adults": 4,
        "maximum_children": 2,
        "total_rooms": None,
        "minimum_nights": 1,
        "check_in_time": "14:00",
        "check_out_time": "11:00",
        "contact_phone": None,
        "contact_email": None,
        "website_url": (
            "https://wonderissproperties.com/residences/escada-residence/"
        ),
        "meta_title": "Escada Apartments Westlands | The Uncharted Route",
        "meta_description": (
            "Stay at Escada Apartments in Westlands, Nairobi, with furnished "
            "apartments, rooftop pool, 270 Rooftop Restaurant, gym and secure parking."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 4,
        "rooms": [
            {
                "name": "Mini One Bedroom Apartment",
                "slug": "mini-one-bedroom-apartment",
                "room_type": "Mini One Bedroom",
                "short_description": (
                    "A compact premium furnished apartment designed for "
                    "couples and business travellers."
                ),
                "description": (
                    "The Mini One Bedroom Apartment provides a private "
                    "residential setting with the convenience of a serviced "
                    "apartment in Westlands."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 100,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "1 King Bed",
                "display_order": 1,
            },
            {
                "name": "One Bedroom Apartment",
                "slug": "one-bedroom-apartment",
                "room_type": "One Bedroom",
                "short_description": (
                    "A fully furnished one-bedroom apartment with private "
                    "living space and kitchen facilities."
                ),
                "description": (
                    "The One Bedroom Apartment offers the privacy and "
                    "flexibility of a furnished home while retaining the "
                    "services and security expected from a premium "
                    "serviced-apartment property."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 125,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "1 King Bed",
                "display_order": 2,
            },
            {
                "name": "Two Bedroom Apartment",
                "slug": "two-bedroom-apartment",
                "room_type": "Two Bedroom",
                "short_description": (
                    "A spacious furnished two-bedroom apartment suited "
                    "to families, couples and small groups."
                ),
                "description": (
                    "The Two Bedroom Apartment provides multiple private "
                    "sleeping spaces alongside shared living and dining areas, "
                    "making it suitable for families and small groups."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 175,
                "currency": "USD",
                "meal_plan": "Room Only",
                "bed_configuration": "King Beds",
                "display_order": 3,
            },
        ],
        "amenities": [
            {
                "name": "Rooftop Swimming Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "A rooftop swimming pool with elevated views across Westlands."
                ),
                "featured": True,
            },
            {
                "name": "270 Rooftop Restaurant",
                "category": "Dining",
                "icon": "utensils",
                "description": (
                    "The property's rooftop restaurant and dining venue."
                ),
                "featured": True,
            },
            {
                "name": "Gym",
                "category": "Wellness",
                "icon": "dumbbells",
                "description": (
                    "An on-site fitness facility for resident guests."
                ),
            },
            {
                "name": "Secure Parking",
                "category": "Services",
                "icon": "car",
                "description": (
                    "Secure on-site parking for guests and residents."
                ),
            },
            {
                "name": "24-Hour Security",
                "category": "Security",
                "icon": "shield",
                "description": (
                    "Round-the-clock security supported by CCTV and "
                    "controlled property access."
                ),
                "featured": True,
            },
            {
                "name": "Backup Power",
                "category": "Services",
                "icon": "zap",
                "description": (
                    "Backup power provision supporting continuity during "
                    "power interruptions."
                ),
            },
        ],
    },
    {
        "name": "Mövenpick Hotel & Residences Nairobi",
        "slug": "movenpick-hotel-residences-nairobi",
        "stay_code": "TUR-STAY-005",
        "accommodation_type": "Hotel & Residences",
        "destination_key": "nairobi",
        "location": "Westlands, Nairobi",
        "address": "Mkungu Close, Westlands, Nairobi, Kenya",
        "short_description": (
            "A luxury Westlands hotel and residence combining contemporary "
            "accommodation, panoramic city views, wellness facilities and "
            "distinctive dining."
        ),
        "description": (
            "Mövenpick Hotel & Residences Nairobi combines luxury hotel "
            "accommodation with residential options in the heart of Westlands.\n\n"
            "The property provides contemporary rooms, suites and residence "
            "layouts alongside leisure facilities including an outdoor "
            "swimming pool, fitness centre and spa-oriented wellness offering.\n\n"
            "Dining is a central part of the experience. The View provides "
            "a distinctive 360-degree revolving restaurant experience, while "
            "Baluba offers all-day dining and Kijani Bar provides a relaxed "
            "social setting.\n\n"
            "The property also caters to business and events with extensive "
            "meeting and conference facilities, making it suitable for "
            "corporate travel, leisure stays, celebrations and longer "
            "residential visits."
        ),
        "maximum_guests": 4,
        "maximum_adults": 4,
        "maximum_children": 2,
        "total_rooms": 276,
        "minimum_nights": 1,
        "check_in_time": "14:00",
        "check_out_time": "12:00",
        "contact_phone": None,
        "contact_email": None,
        "website_url": (
            "https://all.accor.com/hotel/B4Q7/index.en.shtml"
        ),
        "meta_title": (
            "Mövenpick Hotel & Residences Nairobi | The Uncharted Route"
        ),
        "meta_description": (
            "Discover Mövenpick Hotel & Residences Nairobi in Westlands, "
            "with luxury accommodation, The View revolving restaurant, "
            "wellness facilities and event spaces."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 5,
        "rooms": [
            {
                "name": "Classic King Room",
                "slug": "classic-king-room",
                "room_type": "Classic Room",
                "short_description": (
                    "A contemporary king room designed for a comfortable "
                    "luxury stay in Westlands."
                ),
                "description": (
                    "The Classic King Room provides a refined base for "
                    "business and leisure guests, with contemporary "
                    "interiors and access to the hotel's full hospitality "
                    "and dining offering."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 250,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "display_order": 1,
            },
            {
                "name": "Deluxe King Room",
                "slug": "deluxe-king-room",
                "room_type": "Deluxe Room",
                "short_description": (
                    "An upgraded king accommodation option with additional "
                    "space and refined city-hotel comforts."
                ),
                "description": (
                    "The Deluxe King Room offers a more spacious luxury "
                    "setting for guests seeking comfort, city access and "
                    "the hotel's dining, leisure and wellness facilities."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 295,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "display_order": 2,
            },
            {
                "name": "One Bedroom Residence",
                "slug": "one-bedroom-residence",
                "room_type": "Residence",
                "short_description": (
                    "A residential accommodation option designed for "
                    "guests seeking additional living flexibility."
                ),
                "description": (
                    "The One Bedroom Residence combines private bedroom "
                    "accommodation with residential living space, making "
                    "it suitable for longer stays and guests who prefer "
                    "a more apartment-style environment."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 350,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "1 King Bed",
                "display_order": 3,
            },
            {
                "name": "Two Bedroom Residence",
                "slug": "two-bedroom-residence",
                "room_type": "Residence",
                "short_description": (
                    "A spacious residence suited to families, small groups "
                    "and extended luxury stays."
                ),
                "description": (
                    "The Two Bedroom Residence offers additional privacy "
                    "and shared living space for families or small groups "
                    "looking for a residential-style stay within the hotel."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 500,
                "currency": "USD",
                "bed_configuration": "King Beds",
                "meal_plan": "Bed & Breakfast",
                "display_order": 4,
            },
        ],
        "amenities": [
            {
                "name": "The View Revolving Restaurant",
                "category": "Dining",
                "icon": "utensils",
                "description": (
                    "A distinctive 360-degree revolving restaurant offering "
                    "panoramic Nairobi views."
                ),
                "featured": True,
            },
            {
                "name": "Baluba",
                "category": "Dining",
                "icon": "utensils",
                "description": (
                    "An all-day dining venue serving guests throughout the day."
                ),
            },
            {
                "name": "Kijani Bar",
                "category": "Dining",
                "icon": "glass-water",
                "description": (
                    "A relaxed hotel bar and social dining space."
                ),
            },
            {
                "name": "Outdoor Swimming Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "An outdoor pool providing a leisure space within the hotel."
                ),
                "featured": True,
            },
            {
                "name": "Fitness Centre",
                "category": "Wellness",
                "icon": "dumbbells",
                "description": (
                    "A dedicated fitness facility for resident guests."
                ),
            },
            {
                "name": "Spa and Wellness",
                "category": "Wellness",
                "icon": "sparkles",
                "description": (
                    "Wellness facilities supporting relaxation and treatments."
                ),
            },
            {
                "name": "Conference and Event Facilities",
                "category": "Business",
                "icon": "presentation",
                "description": (
                    "Extensive meeting and event spaces suitable for "
                    "corporate functions, conferences and celebrations."
                ),
                "featured": True,
            },
        ],
    },
    {
        "name": "Fairmont Mount Kenya Safari Club",
        "slug": "fairmont-mount-kenya-safari-club",
        "stay_code": "TUR-STAY-006",
        "accommodation_type": "Luxury Safari Club",
        "destination_key": "mount-kenya",
        "location": "Nanyuki, Laikipia",
        "address": "Mount Kenya, Nanyuki, Laikipia, Kenya",
        "short_description": (
            "A legendary Mount Kenya retreat combining heritage, refined "
            "accommodation, conservation, nature and mountain views."
        ),
        "description": (
            "Fairmont Mount Kenya Safari Club is a distinctive luxury retreat "
            "in Nanyuki, set against the dramatic backdrop of Mount Kenya and "
            "the landscapes of Laikipia.\n\n"
            "The property combines heritage character with refined rooms, "
            "suites, cottages and villas, creating a destination stay rather "
            "than simply an overnight base. Guests can enjoy expansive "
            "grounds, mountain views and a slower rhythm shaped by the "
            "surrounding landscape.\n\n"
            "Experiences include golf, horse riding, nature walks, wildlife "
            "and conservation activities, with the Mount Kenya Wildlife "
            "Conservancy and Wildlife Rescue Centre forming an important "
            "part of the property's conservation story.\n\n"
            "Wellness, swimming, dining, events and family activities make "
            "the property suitable for romantic escapes, family holidays, "
            "celebrations, corporate retreats and multi-day Mount Kenya "
            "adventures."
        ),
        "maximum_guests": 4,
        "maximum_adults": 4,
        "maximum_children": 3,
        "total_rooms": None,
        "minimum_nights": 1,
        "check_in_time": "14:00",
        "check_out_time": "11:00",
        "contact_phone": None,
        "contact_email": None,
        "website_url": (
            "https://www.fairmont.com/en/hotels/nanyuki/"
            "fairmont-mount-kenya-safari-club.html"
        ),
        "meta_title": (
            "Fairmont Mount Kenya Safari Club | The Uncharted Route"
        ),
        "meta_description": (
            "Stay at Fairmont Mount Kenya Safari Club in Nanyuki, a luxury "
            "retreat combining Mount Kenya views, heritage, conservation, "
            "nature and refined hospitality."
        ),
        "featured": True,
        "show_on_homepage": True,
        "display_order": 6,
        "rooms": [
            {
                "name": "Manor Junior Suite",
                "slug": "manor-junior-suite",
                "room_type": "Junior Suite",
                "short_description": (
                    "A refined heritage-style suite offering a distinctive "
                    "Mount Kenya Safari Club stay."
                ),
                "description": (
                    "The Manor Junior Suite provides an elegant retreat "
                    "within the property's heritage setting, combining "
                    "comfortable private accommodation with access to the "
                    "club's extensive grounds and experiences."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 450,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Bed",
                "display_order": 1,
            },
            {
                "name": "Manor Equatorial Suite",
                "slug": "manor-equatorial-suite",
                "room_type": "Suite",
                "short_description": (
                    "A premium heritage suite designed for a more spacious "
                    "Mount Kenya retreat."
                ),
                "description": (
                    "The Manor Equatorial Suite offers a more expansive "
                    "accommodation experience within the club's distinctive "
                    "heritage environment."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 575,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Bed",
                "display_order": 2,
            },
            {
                "name": "Batian Villa",
                "slug": "batian-villa",
                "room_type": "Villa",
                "short_description": (
                    "A premium private villa suited to guests seeking "
                    "additional space and privacy."
                ),
                "description": (
                    "Batian Villa provides a more private accommodation "
                    "experience for guests who want additional space, "
                    "comfort and a stronger sense of retreat."
                ),
                "maximum_guests": 4,
                "maximum_adults": 4,
                "maximum_children": 2,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 900,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Beds",
                "display_order": 3,
            },
            {
                "name": "Riverside Accommodation",
                "slug": "riverside-accommodation",
                "room_type": "Riverside Room",
                "short_description": (
                    "A tranquil accommodation option positioned within "
                    "the property's riverside environment."
                ),
                "description": (
                    "Riverside accommodation offers a quieter retreat "
                    "within the extensive grounds, complementing the "
                    "property's wider nature and conservation experience."
                ),
                "maximum_guests": 2,
                "maximum_adults": 2,
                "maximum_children": 1,
                "minimum_guests": 1,
                "total_units": 1,
                "nightly_rate": 425,
                "currency": "USD",
                "meal_plan": "Bed & Breakfast",
                "bed_configuration": "King Bed",
                "display_order": 4,
            },
        ],
        "amenities": [
            {
                "name": "Mount Kenya Views",
                "category": "Property",
                "icon": "mountain",
                "description": (
                    "A dramatic setting with views towards Mount Kenya."
                ),
                "featured": True,
            },
            {
                "name": "Heated Outdoor Swimming Pool",
                "category": "Recreation",
                "icon": "waves",
                "description": (
                    "A heated outdoor pool within the club's landscaped grounds."
                ),
            },
            {
                "name": "Riuki Spa",
                "category": "Wellness",
                "icon": "sparkles",
                "description": (
                    "An on-site spa and wellness offering for relaxation "
                    "and restorative treatments."
                ),
                "featured": True,
            },
            {
                "name": "Golf Course",
                "category": "Recreation",
                "icon": "flag",
                "description": (
                    "Golf facilities within the historic Mount Kenya Safari "
                    "Club grounds."
                ),
            },
            {
                "name": "Horse Riding",
                "category": "Activities",
                "icon": "horse",
                "description": (
                    "Horse-riding experiences across the surrounding grounds."
                ),
            },
            {
                "name": "Wildlife Rescue Centre",
                "category": "Conservation",
                "icon": "paw-print",
                "description": (
                    "Access to the property's wildlife rescue and conservation "
                    "experience."
                ),
                "featured": True,
            },
            {
                "name": "Conservation Experiences",
                "category": "Conservation",
                "icon": "leaf",
                "description": (
                    "Nature and conservation activities connected to the "
                    "Mount Kenya Wildlife Conservancy."
                ),
            },
            {
                "name": "Family Activities",
                "category": "Family",
                "icon": "users",
                "description": (
                    "A range of activities and experiences suitable for "
                    "families and younger travellers."
                ),
            },
        ],
    },
]


# =============================================================================
# ROOM AMENITIES
# =============================================================================

ROOM_AMENITIES_BY_STAY: dict[str, list[dict[str, Any]]] = {
    "giraffe-manor": [
        {
            "name": "Private Bathroom",
            "category": "Bathroom",
            "icon": "bath",
            "description": "Private en-suite bathroom facilities.",
            "featured": True,
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
        {
            "name": "Tea and Coffee Facilities",
            "category": "In-Room",
            "icon": "coffee",
            "description": "In-room tea and coffee facilities.",
        },
    ],
    "jw-marriott-hotel-nairobi": [
        {
            "name": "King Bed",
            "category": "Bedroom",
            "icon": "bed-double",
            "description": "King-size sleeping configuration.",
        },
        {
            "name": "Separate Living Area",
            "category": "Living",
            "icon": "sofa",
            "description": (
                "Dedicated living space in applicable suites and residences."
            ),
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
        {
            "name": "Air Conditioning",
            "category": "In-Room",
            "icon": "snowflake",
            "description": "Climate-controlled accommodation.",
        },
        {
            "name": "Kitchen Facilities",
            "category": "Residence",
            "icon": "chef-hat",
            "description": (
                "Kitchen facilities in applicable residence categories."
            ),
        },
    ],
    "skynest-residences-by-cityblue": [
        {
            "name": "Fully Furnished",
            "category": "In-Room",
            "icon": "sofa",
            "description": "Fully furnished residential accommodation.",
            "featured": True,
        },
        {
            "name": "Kitchen Facilities",
            "category": "Kitchen",
            "icon": "chef-hat",
            "description": (
                "Kitchen or kitchenette facilities depending on residence type."
            ),
        },
        {
            "name": "Living Area",
            "category": "Living",
            "icon": "sofa",
            "description": "Dedicated residential living space.",
        },
        {
            "name": "Private Balcony",
            "category": "Outdoor",
            "icon": "building",
            "description": (
                "Balcony facilities on applicable apartment layouts."
            ),
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
    ],
    "escada-apartments": [
        {
            "name": "Fully Equipped Kitchen",
            "category": "Kitchen",
            "icon": "chef-hat",
            "description": (
                "Kitchen facilities for independent residential living."
            ),
            "featured": True,
        },
        {
            "name": "Living and Dining Area",
            "category": "Living",
            "icon": "sofa",
            "description": (
                "Dedicated residential living and dining space."
            ),
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
        {
            "name": "Air Conditioning",
            "category": "In-Room",
            "icon": "snowflake",
            "description": "Climate-controlled accommodation.",
        },
    ],
    "movenpick-hotel-residences-nairobi": [
        {
            "name": "King Bed",
            "category": "Bedroom",
            "icon": "bed-double",
            "description": "King-size sleeping configuration.",
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
        {
            "name": "Air Conditioning",
            "category": "In-Room",
            "icon": "snowflake",
            "description": "Climate-controlled accommodation.",
        },
        {
            "name": "Residential Living Space",
            "category": "Residence",
            "icon": "sofa",
            "description": (
                "Additional living space in residence categories."
            ),
        },
    ],
    "fairmont-mount-kenya-safari-club": [
        {
            "name": "Private Bathroom",
            "category": "Bathroom",
            "icon": "bath",
            "description": "Private en-suite bathroom facilities.",
        },
        {
            "name": "Wi-Fi",
            "category": "Connectivity",
            "icon": "wifi",
            "description": "Guest Wi-Fi access.",
        },
        {
            "name": "Tea and Coffee Facilities",
            "category": "In-Room",
            "icon": "coffee",
            "description": "In-room tea and coffee facilities.",
        },
        {
            "name": "Mount Kenya Setting",
            "category": "View",
            "icon": "mountain",
            "description": (
                "Accommodation within the Mount Kenya landscape."
            ),
            "featured": True,
        },
    ],
}


# =============================================================================
# POPULATION ENGINE
# =============================================================================

class StayPopulation:

    def __init__(
        self,
        apply_changes: bool,
    ):
        self.apply_changes = apply_changes

        self.created_stays = 0
        self.reused_stays = 0
        self.updated_stays = 0

        self.created_rooms = 0
        self.reused_rooms = 0
        self.updated_rooms = 0

        self.created_amenities = 0
        self.reused_amenities = 0

        self.created_room_amenities = 0
        self.reused_room_amenities = 0

        self.planned_stays = 0
        self.planned_rooms = 0
        self.planned_amenities = 0
        self.planned_room_amenities = 0

        self.destination_map: dict[str, int] = {}

    # -------------------------------------------------------------------------
    # Stay — APPLY
    # -------------------------------------------------------------------------

    def populate_stay(
        self,
        definition: dict[str, Any],
    ) -> Stay:

        slug = definition["slug"]

        stay = find_stay(slug)

        if stay is None:

            stay = Stay(
                stay_code=definition["stay_code"],
                property_name=definition["name"],
                slug=slug,
                accommodation_type=definition["accommodation_type"],
                short_description=definition["short_description"],
                description=definition["description"],
                location=definition["location"],
                address=definition["address"],
                destination_id=self.destination_map[
                    definition["destination_key"]
                ],
                maximum_guests=definition["maximum_guests"],
                maximum_adults=definition["maximum_adults"],
                maximum_children=definition["maximum_children"],
                total_rooms=definition["total_rooms"],
                minimum_nights=definition["minimum_nights"],
                check_in_time=definition["check_in_time"],
                check_out_time=definition["check_out_time"],
                contact_phone=definition["contact_phone"],
                contact_email=definition["contact_email"],
                website_url=definition["website_url"],
                meta_title=definition["meta_title"],
                meta_description=definition["meta_description"],
                featured=definition["featured"],
                show_on_homepage=definition["show_on_homepage"],
                active=True,
                display_order=definition["display_order"],
            )

            db.session.add(stay)
            db.session.flush()

            self.created_stays += 1

            print(
                f"  CREATE STAY | {stay.property_name} | "
                f"destination_id={stay.destination_id}"
            )

            return stay

        self.reused_stays += 1

        changed = False

        explicit_updates = {
            "property_name": definition["name"],
            "accommodation_type": definition["accommodation_type"],
            "short_description": definition["short_description"],
            "description": definition["description"],
            "location": definition["location"],
            "address": definition["address"],
            "destination_id": self.destination_map[
                definition["destination_key"]
            ],
            "maximum_guests": definition["maximum_guests"],
            "maximum_adults": definition["maximum_adults"],
            "maximum_children": definition["maximum_children"],
            "total_rooms": definition["total_rooms"],
            "minimum_nights": definition["minimum_nights"],
            "check_in_time": definition["check_in_time"],
            "check_out_time": definition["check_out_time"],
            "website_url": definition["website_url"],
            "meta_title": definition["meta_title"],
            "meta_description": definition["meta_description"],
            "featured": definition["featured"],
            "show_on_homepage": definition["show_on_homepage"],
            "active": True,
            "display_order": definition["display_order"],
        }

        for field, value in explicit_updates.items():

            if field in {
                "maximum_adults",
                "maximum_children",
                "total_rooms",
            } and value is None:
                continue

            if update_if_changed(
                stay,
                field,
                value,
                force=True,
            ):
                changed = True

        for field in (
            "contact_phone",
            "contact_email",
        ):
            value = definition[field]

            if value and update_if_changed(
                stay,
                field,
                value,
                force=False,
            ):
                changed = True

        if changed:
            self.updated_stays += 1

            print(
                f"  UPDATE STAY | {stay.property_name}"
            )
        else:
            print(
                f"  REUSE STAY | {stay.property_name}"
            )

        return stay

    # -------------------------------------------------------------------------
    # Room — APPLY
    # -------------------------------------------------------------------------

    def populate_room(
        self,
        stay: Stay,
        room_definition: dict[str, Any],
    ) -> StayRoom:

        slug = room_definition["slug"]

        room = find_room(
            stay.id,
            slug,
        )

        if room is None:

            room = StayRoom(
                room_code=make_room_code(
                    stay,
                    slug,
                ),
                stay_id=stay.id,
                name=room_definition["name"],
                slug=slug,
                room_type=room_definition["room_type"],
                short_description=room_definition["short_description"],
                description=room_definition["description"],
                maximum_guests=room_definition["maximum_guests"],
                maximum_adults=room_definition["maximum_adults"],
                maximum_children=room_definition["maximum_children"],
                minimum_guests=room_definition["minimum_guests"],
                total_units=room_definition["total_units"],
                nightly_rate=money(
                    room_definition["nightly_rate"]
                ),
                currency=room_definition["currency"],
                meal_plan=room_definition["meal_plan"],
                bed_configuration=room_definition["bed_configuration"],
                size_description=room_definition.get(
                    "size_description"
                ),
                availability_status="Available",
                featured=room_definition.get(
                    "featured",
                    False,
                ),
                active=True,
                display_order=room_definition["display_order"],
            )

            db.session.add(room)
            db.session.flush()

            self.created_rooms += 1

            print(
                f"    CREATE ROOM | {room.name} | "
                f"{room.nightly_rate:.2f} "
                f"{room.currency}/night"
            )

            return room

        self.reused_rooms += 1

        changed = False

        fillable_fields = {
            "name": room_definition["name"],
            "room_type": room_definition["room_type"],
            "short_description": room_definition["short_description"],
            "description": room_definition["description"],
            "maximum_guests": room_definition["maximum_guests"],
            "maximum_adults": room_definition["maximum_adults"],
            "maximum_children": room_definition["maximum_children"],
            "minimum_guests": room_definition["minimum_guests"],
            "total_units": room_definition["total_units"],
            "meal_plan": room_definition["meal_plan"],
            "bed_configuration": room_definition["bed_configuration"],
            "size_description": room_definition.get(
                "size_description"
            ),
        }

        # Existing operational/catalogue rates are preserved.
        #
        # This specifically protects the existing JW Marriott Junior Suite
        # rate from being overwritten.
        if not room_definition.get(
            "preserve_existing",
            False,
        ):
            fillable_fields["nightly_rate"] = money(
                room_definition["nightly_rate"]
            )
            fillable_fields["currency"] = room_definition["currency"]

        for field, value in fillable_fields.items():

            if value is None:
                continue

            if update_if_changed(
                room,
                field,
                value,
                force=False,
            ):
                changed = True

        if changed:
            self.updated_rooms += 1

            print(
                f"    UPDATE ROOM | {room.name}"
            )
        else:
            print(
                f"    REUSE ROOM | {room.name}"
            )

        return room

    # -------------------------------------------------------------------------
    # Property amenities — APPLY
    # -------------------------------------------------------------------------

    def populate_property_amenities(
        self,
        stay: Stay,
        amenities: list[dict[str, Any]],
    ) -> None:

        for definition in amenities:

            existing = find_property_amenity(
                stay.id,
                definition["name"],
            )

            if existing:
                self.reused_amenities += 1
                continue

            amenity = StayAmenity(
                stay_id=stay.id,
                name=definition["name"],
                description=definition["description"],
                category=definition.get(
                    "category",
                    "General",
                ),
                icon=definition.get("icon"),
                active=True,
                featured=definition.get(
                    "featured",
                    False,
                ),
                display_order=definition.get(
                    "display_order",
                    0,
                ),
            )

            db.session.add(amenity)

            self.created_amenities += 1

            print(
                f"    CREATE AMENITY | {definition['name']}"
            )

    # -------------------------------------------------------------------------
    # Room amenities — APPLY
    # -------------------------------------------------------------------------

    def populate_room_amenities(
        self,
        stay: Stay,
        rooms: list[StayRoom],
    ) -> None:

        definitions = ROOM_AMENITIES_BY_STAY.get(
            stay.slug,
            [],
        )

        if not definitions:
            return

        for room in rooms:

            for definition in definitions:

                existing = find_room_amenity(
                    room.id,
                    definition["name"],
                )

                if existing:
                    self.reused_room_amenities += 1
                    continue

                amenity = StayRoomAmenity(
                    room_id=room.id,
                    name=definition["name"],
                    description=definition["description"],
                    category=definition.get(
                        "category",
                        "Room",
                    ),
                    icon=definition.get("icon"),
                    active=True,
                    featured=definition.get(
                        "featured",
                        False,
                    ),
                    display_order=definition.get(
                        "display_order",
                        0,
                    ),
                )

                db.session.add(amenity)

                self.created_room_amenities += 1

                print(
                    f"      CREATE ROOM AMENITY | "
                    f"{room.name} → {definition['name']}"
                )

    # -------------------------------------------------------------------------
    # DRY-RUN PLANNING
    # -------------------------------------------------------------------------

    def plan_stay(
        self,
        definition: dict[str, Any],
    ) -> None:
        """
        Read-only planning pass.

        This method deliberately does not instantiate ORM records for
        persistence and does not call db.session.add(), flush(), commit(),
        update or delete operations.
        """

        slug = definition["slug"]

        stay = find_stay(slug)

        if stay is None:

            self.planned_stays += 1

            print(
                f"  WOULD CREATE STAY | "
                f"{definition['name']} | "
                f"destination={definition['destination_key']}"
            )

            for room_definition in definition["rooms"]:

                self.planned_rooms += 1

                print(
                    f"    WOULD CREATE ROOM | "
                    f"{room_definition['name']} | "
                    f"{room_definition['nightly_rate']:.2f} "
                    f"{room_definition['currency']}/night"
                )

            for amenity in definition["amenities"]:

                self.planned_amenities += 1

                print(
                    f"    WOULD CREATE AMENITY | "
                    f"{amenity['name']}"
                )

            room_amenity_definitions = ROOM_AMENITIES_BY_STAY.get(
                slug,
                [],
            )

            room_count = len(
                definition["rooms"]
            )

            for room_definition in definition["rooms"]:

                for room_amenity in room_amenity_definitions:

                    self.planned_room_amenities += 1

                    print(
                        f"      WOULD CREATE ROOM AMENITY | "
                        f"{room_definition['name']} → "
                        f"{room_amenity['name']}"
                    )

            return

        print(
            f"  WOULD REUSE/UPDATE STAY | "
            f"{stay.property_name} | ID={stay.id}"
        )

        for room_definition in definition["rooms"]:

            existing_room = find_room(
                stay.id,
                room_definition["slug"],
            )

            if existing_room is None:

                self.planned_rooms += 1

                print(
                    f"    WOULD CREATE ROOM | "
                    f"{room_definition['name']} | "
                    f"{room_definition['nightly_rate']:.2f} "
                    f"{room_definition['currency']}/night"
                )

            else:

                print(
                    f"    WOULD REUSE ROOM | "
                    f"{existing_room.name} | ID={existing_room.id}"
                )

        for amenity in definition["amenities"]:

            existing_amenity = find_property_amenity(
                stay.id,
                amenity["name"],
            )

            if existing_amenity is None:

                self.planned_amenities += 1

                print(
                    f"    WOULD CREATE AMENITY | "
                    f"{amenity['name']}"
                )

            else:

                print(
                    f"    REUSE EXISTING AMENITY | "
                    f"{amenity['name']}"
                )

        room_amenity_definitions = ROOM_AMENITIES_BY_STAY.get(
            slug,
            [],
        )

        for room_definition in definition["rooms"]:

            existing_room = find_room(
                stay.id,
                room_definition["slug"],
            )

            if existing_room is None:
                continue

            for room_amenity in room_amenity_definitions:

                existing_room_amenity = find_room_amenity(
                    existing_room.id,
                    room_amenity["name"],
                )

                if existing_room_amenity is None:

                    self.planned_room_amenities += 1

                    print(
                        f"      WOULD CREATE ROOM AMENITY | "
                        f"{room_definition['name']} → "
                        f"{room_amenity['name']}"
                    )

                else:

                    print(
                        f"      REUSE EXISTING ROOM AMENITY | "
                        f"{room_definition['name']} → "
                        f"{room_amenity['name']}"
                    )

    # -------------------------------------------------------------------------
    # APPLY PASS
    # -------------------------------------------------------------------------

    def apply_stay_definition(
        self,
        definition: dict[str, Any],
    ) -> None:

        stay = self.populate_stay(
            definition
        )

        rooms: list[StayRoom] = []

        for room_definition in definition["rooms"]:

            room = self.populate_room(
                stay,
                room_definition,
            )

            rooms.append(room)

        self.populate_property_amenities(
            stay,
            definition["amenities"],
        )

        self.populate_room_amenities(
            stay,
            rooms,
        )

    # -------------------------------------------------------------------------
    # FULL POPULATION
    # -------------------------------------------------------------------------

    def run(self) -> None:

        print_header(
            "THE UNCHARTED ROUTE — INITIAL STAYS CATALOGUE POPULATION"
        )

        print_section("MODE")

        if self.apply_changes:
            print(
                "  APPLY — DATABASE MUTATIONS ENABLED"
            )
        else:
            print(
                "  DRY RUN — GENUINELY READ-ONLY"
            )

        print()
        print(
            f"  Rate mode: {RATE_MODE}"
        )
        print(
            "  Media: PRESERVED / NO NEW MEDIA"
        )
        print(
            "  Reviews: NO NEW REVIEWS"
        )
        print(
            "  Bookings: PRESERVED / NO NEW BOOKINGS"
        )
        print(
            "  Inquiries: NO NEW INQUIRIES"
        )

        print_section(
            "RESOLVING STAY DESTINATIONS"
        )

        self.destination_map = resolve_destinations(
            self
        )

        print(
            f"  Nairobi destination       : "
            f"ID={self.destination_map['nairobi']}"
        )

        mount_kenya_id = self.destination_map[
            "mount-kenya"
        ]

        if mount_kenya_id == -1:
            print(
                "  Mount Kenya destination   : "
                "PLANNED FOR APPLY"
            )
        else:
            print(
                f"  Mount Kenya destination   : "
                f"ID={mount_kenya_id}"
            )

        print_section(
            "TARGET PROPERTIES"
        )

        for name in TARGET_STAYS:
            print(
                f"  - {name}"
            )

        print_section(
            "POPULATING"
        )

        if self.apply_changes:

            for definition in STAY_DEFINITIONS:

                self.apply_stay_definition(
                    definition
                )

        else:

            for definition in STAY_DEFINITIONS:

                self.plan_stay(
                    definition
                )

        print_section(
            "SUMMARY"
        )

        if self.apply_changes:

            print(
                f"  Stays created                 : "
                f"{self.created_stays}"
            )
            print(
                f"  Stays reused                  : "
                f"{self.reused_stays}"
            )
            print(
                f"  Stays updated                 : "
                f"{self.updated_stays}"
            )
            print(
                f"  Rooms created                 : "
                f"{self.created_rooms}"
            )
            print(
                f"  Rooms reused                  : "
                f"{self.reused_rooms}"
            )
            print(
                f"  Rooms updated                 : "
                f"{self.updated_rooms}"
            )
            print(
                f"  Property amenities created    : "
                f"{self.created_amenities}"
            )
            print(
                f"  Property amenities reused     : "
                f"{self.reused_amenities}"
            )
            print(
                f"  Room amenities created        : "
                f"{self.created_room_amenities}"
            )
            print(
                f"  Room amenities reused         : "
                f"{self.reused_room_amenities}"
            )

        else:

            print(
                f"  Stays that would be created   : "
                f"{self.planned_stays}"
            )
            print(
                f"  Rooms that would be created   : "
                f"{self.planned_rooms}"
            )
            print(
                f"  Amenities that would be created: "
                f"{self.planned_amenities}"
            )
            print(
                f"  Room amenities that would be created: "
                f"{self.planned_room_amenities}"
            )

        print()
        print(
            "  Existing operational records:"
        )
        print(
            "    Stay bookings                : PRESERVED"
        )
        print(
            "    Stay reviews                 : PRESERVED"
        )
        print(
            "    Stay inquiries               : PRESERVED"
        )
        print(
            "    Stay media                   : PRESERVED"
        )
        print(
            "    Stay room media              : PRESERVED"
        )
        print(
            "    Stay availability            : PRESERVED"
        )

        print()
        print(
            "  Catalogue rates are indicative TUR planning benchmarks."
        )
        print(
            "  Supplier confirmation is required before final commercial use."
        )

        if not self.apply_changes:

            print()
            print(
                "  DRY RUN COMPLETE."
            )
            print(
                "  NO DATABASE RECORDS WERE CREATED, UPDATED, DELETED, "
                "FLUSHED OR COMMITTED."
            )


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description="Populate the initial TUR Stay catalogue."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Commit database changes. Without this flag the script is "
            "strictly read-only."
        ),
    )

    args = parser.parse_args()

    app = create_app()

    with app.app_context():

        population = StayPopulation(
            apply_changes=args.apply
        )

        try:

            population.run()

            if args.apply:

                db.session.commit()

                print_header(
                    "BATCH 1 COMMITTED SUCCESSFULLY"
                )

                print(
                    "  Initial six-property Stay catalogue populated successfully."
                )
                print(
                    "  Existing operational/customer records were preserved."
                )
                print(
                    "  No media, reviews, bookings or inquiries were created."
                )
                print(
                    "  Mount Kenya destination was created/reused as required."
                )

            return 0

        except Exception as exc:

            db.session.rollback()

            print_header(
                "STAYS CATALOGUE POPULATION FAILED"
            )

            print(
                f"  Error: {exc}"
            )

            print()
            print(
                "  Database transaction rolled back."
            )
            print(
                "  No partial changes were committed."
            )

            raise


if __name__ == "__main__":
    raise SystemExit(
        main()
    )