"""
THE UNCHARTED ROUTE — STAYS CATALOGUE AUDIT

Purpose:
    Inspect the current Stay catalogue before population.

This audit is READ-ONLY.
It does not create, update, delete, or otherwise mutate database records.

Focus:
    - Existing Stay records
    - Actual property content
    - Existing rooms/rates
    - Amenities
    - Media usage
    - Availability
    - Reviews
    - Bookings
    - SEO/contact/cancellation fields
    - Missing catalogue structure needed for the initial six-property catalogue
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from sqlalchemy import text

# --------------------------------------------------------------------------------------
# PROJECT BOOTSTRAP
# --------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("FLASK_ENV", "development")

from app import create_app
from extensions import db

from app.models.stay import Stay
from app.models.stay_room import StayRoom
from app.models.stay_amenity import StayAmenity
from app.models.stay_availability import StayAvailability
from app.models.stay_review import StayReview
from app.models.stay_booking import StayBooking
from app.models.destination import Destination

# --------------------------------------------------------------------------------------
# CONSTANTS
# --------------------------------------------------------------------------------------

LINE = "=" * 110
SUBLINE = "-" * 110


# --------------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------------

def value(field_value, fallback="—"):
    if field_value is None:
        return fallback

    if isinstance(field_value, str):
        field_value = field_value.strip()

        if not field_value:
            return fallback

        return field_value

    return str(field_value)


def yes_no(field_value):
    return "YES" if field_value else "NO"


def print_field(label, field_value, width=28):
    print(f"  {label:<{width}}: {value(field_value)}")


def print_multiline(label, field_value):
    text_value = value(field_value)

    if text_value == "—":
        print(f"  {label:<28}: —")
        return

    print(f"  {label:<28}:")
    for line in text_value.splitlines():
        print(f"    {line}")


def normalize_relationship_items(relationship):
    """
    Safely normalize SQLAlchemy relationships.

    Handles:
        - dynamic query relationships
        - normal list-like relationships
        - a single related object
        - None
    """
    if relationship is None:
        return []

    if isinstance(relationship, (list, tuple, set)):
        return list(relationship)

    if hasattr(relationship, "all") and callable(relationship.all):
        return relationship.all()

    return [relationship]


def query_property_media(stay_id):
    """
    Read property media directly from stay_media.

    This deliberately avoids the Stay.media ORM relationship because the
    current project relationship is not behaving consistently with the
    underlying table during this audit.
    """
    return db.session.execute(
        text(
            """
            SELECT
                id,
                stay_id,
                media_asset_id,
                usage,
                display_order,
                caption,
                active
            FROM stay_media
            WHERE stay_id = :stay_id
            ORDER BY display_order ASC, id ASC
            """
        ),
        {"stay_id": stay_id},
    ).mappings().all()


def query_room_media(room_id):
    """
    Read room media directly from stay_room_media.
    """
    return db.session.execute(
        text(
            """
            SELECT
                id,
                room_id,
                media_asset_id,
                usage,
                display_order,
                caption,
                active
            FROM stay_room_media
            WHERE room_id = :room_id
            ORDER BY display_order ASC, id ASC
            """
        ),
        {"room_id": room_id},
    ).mappings().all()


# --------------------------------------------------------------------------------------
# STAY AUDIT
# --------------------------------------------------------------------------------------

def audit_stay(stay):
    # ------------------------------------------------------------------
    # Relationships that are safe to inspect through the model
    # ------------------------------------------------------------------

    if hasattr(stay.rooms, "order_by"):
        rooms = stay.rooms.order_by(
            StayRoom.display_order.asc(),
            StayRoom.id.asc(),
        ).all()
    else:
        rooms = normalize_relationship_items(stay.rooms)

    if hasattr(stay.amenities, "order_by"):
        amenities = stay.amenities.order_by(
            StayAmenity.display_order.asc(),
            StayAmenity.id.asc(),
        ).all()
    else:
        amenities = normalize_relationship_items(stay.amenities)

    if hasattr(stay.availability, "order_by"):
        availability = stay.availability.order_by(
            StayAvailability.start_date.asc(),
            StayAvailability.id.asc(),
        ).all()
    else:
        availability = normalize_relationship_items(stay.availability)

    if hasattr(stay.reviews, "order_by"):
        reviews = stay.reviews.order_by(
            StayReview.id.asc(),
        ).all()
    else:
        reviews = normalize_relationship_items(stay.reviews)

    if hasattr(stay.bookings, "order_by"):
        bookings = stay.bookings.order_by(
            StayBooking.id.asc(),
        ).all()
    else:
        bookings = normalize_relationship_items(stay.bookings)

    # ------------------------------------------------------------------
    # Media is queried directly from the database tables
    # ------------------------------------------------------------------

    property_media = query_property_media(stay.id)

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------

    print()
    print(LINE)
    print(f"STAY ID {stay.id} — {value(stay.property_name)}")
    print(LINE)

    # ------------------------------------------------------------------
    # IDENTITY
    # ------------------------------------------------------------------

    print()
    print("IDENTITY")
    print(SUBLINE)

    print_field("Stay code", stay.stay_code)
    print_field("Property name", stay.property_name)
    print_field("Slug", stay.slug)
    print_field("Accommodation type", stay.accommodation_type)
    print_field("Destination ID", stay.destination_id)
    print_field("Location", stay.location)
    print_field("Address", stay.address)

    # ------------------------------------------------------------------
    # CONTENT
    # ------------------------------------------------------------------

    print()
    print("CONTENT")
    print(SUBLINE)

    print_multiline("Short description", stay.short_description)
    print_multiline("Description", stay.description)

    # ------------------------------------------------------------------
    # CAPACITY
    # ------------------------------------------------------------------

    print()
    print("CAPACITY")
    print(SUBLINE)

    print_field("Maximum guests", stay.maximum_guests)
    print_field("Maximum adults", stay.maximum_adults)
    print_field("Maximum children", stay.maximum_children)
    print_field("Total rooms", stay.total_rooms)
    print_field("Minimum nights", stay.minimum_nights)

    # ------------------------------------------------------------------
    # OPERATIONS
    # ------------------------------------------------------------------

    print()
    print("OPERATIONS")
    print(SUBLINE)

    print_field("Check-in", stay.check_in_time)
    print_field("Check-out", stay.check_out_time)
    print_field("Contact phone", stay.contact_phone)
    print_field("Contact email", stay.contact_email)
    print_field("Website", stay.website_url)
    print_field("Cancellation policy ID", stay.cancellation_policy_id)

    # ------------------------------------------------------------------
    # VISIBILITY
    # ------------------------------------------------------------------

    print()
    print("VISIBILITY")
    print(SUBLINE)

    print_field("Active", yes_no(stay.active))
    print_field("Featured", yes_no(stay.featured))
    print_field("Show on homepage", yes_no(stay.show_on_homepage))
    print_field("Display order", stay.display_order)

    # ------------------------------------------------------------------
    # SEO
    # ------------------------------------------------------------------

    print()
    print("SEO")
    print(SUBLINE)

    print_field("Meta title", stay.meta_title)
    print_field("Meta description", stay.meta_description)

    # ------------------------------------------------------------------
    # ROOMS
    # ------------------------------------------------------------------

    print()
    print("ROOMS")
    print(SUBLINE)

    if not rooms:
        print("  No rooms configured.")

    else:
        for index, room in enumerate(rooms, start=1):
            print()
            print(f"  ROOM {index}")
            print(f"  {'-' * 90}")

            print_field("Room ID", room.id)
            print_field("Room code", room.room_code)
            print_field("Name", room.name)
            print_field("Slug", room.slug)
            print_field("Room type", room.room_type)

            print_multiline(
                "Short description",
                room.short_description,
            )

            print_multiline(
                "Description",
                room.description,
            )

            print_field("Maximum guests", room.maximum_guests)
            print_field("Maximum adults", room.maximum_adults)
            print_field("Maximum children", room.maximum_children)
            print_field("Minimum guests", room.minimum_guests)
            print_field("Total units", room.total_units)

            print_field("Nightly rate", room.nightly_rate)
            print_field("Currency", room.currency)
            print_field("Meal plan", room.meal_plan)

            print_field("Bed configuration", room.bed_configuration)
            print_field("Floor", room.floor)
            print_field("Size", room.size_description)
            print_field("Availability status", room.availability_status)

            print_field("Featured", yes_no(room.featured))
            print_field("Active", yes_no(room.active))
            print_field("Display order", room.display_order)

            # ----------------------------------------------------------
            # ROOM MEDIA
            # ----------------------------------------------------------

            room_media = query_room_media(room.id)

            print()
            print(f"  Room media: {len(room_media)}")

            if not room_media:
                print("    No room media configured.")

            else:
                for media in room_media:
                    print(
                        f"    - ID={media['id']} | "
                        f"media_asset_id={media['media_asset_id']} | "
                        f"usage={value(media['usage'])} | "
                        f"active={yes_no(media['active'])} | "
                        f"order={value(media['display_order'])} | "
                        f"caption={value(media['caption'])}"
                    )

            # ----------------------------------------------------------
            # ROOM AMENITIES
            # ----------------------------------------------------------

            room_amenities = (
                db.session.execute(
                    text(
                        """
                        SELECT
                            id,
                            room_id,
                            name,
                            description,
                            category,
                            icon,
                            active,
                            featured,
                            display_order
                        FROM stay_room_amenities
                        WHERE room_id = :room_id
                        ORDER BY display_order ASC, id ASC
                        """
                    ),
                    {"room_id": room.id},
                )
                .mappings()
                .all()
            )

            print()
            print(f"  Room amenities: {len(room_amenities)}")

            if not room_amenities:
                print("    No room amenities configured.")

            else:
                for amenity in room_amenities:
                    print(
                        f"    - ID={amenity['id']} | "
                        f"name={value(amenity['name'])} | "
                        f"category={value(amenity['category'])} | "
                        f"icon={value(amenity['icon'])} | "
                        f"featured={yes_no(amenity['featured'])} | "
                        f"active={yes_no(amenity['active'])}"
                    )

                    if amenity["description"]:
                        print(
                            f"      description={value(amenity['description'])}"
                        )

    # ------------------------------------------------------------------
    # PROPERTY AMENITIES
    # ------------------------------------------------------------------

    print()
    print("PROPERTY AMENITIES")
    print(SUBLINE)

    if not amenities:
        print("  No property amenities configured.")

    else:
        for amenity in amenities:
            print(
                f"  - ID={amenity.id} | "
                f"name={value(amenity.name)} | "
                f"category={value(amenity.category)} | "
                f"icon={value(amenity.icon)} | "
                f"featured={yes_no(amenity.featured)} | "
                f"active={yes_no(amenity.active)}"
            )

            if amenity.description:
                print(
                    f"    description={value(amenity.description)}"
                )

    # ------------------------------------------------------------------
    # PROPERTY MEDIA
    # ------------------------------------------------------------------

    print()
    print("PROPERTY MEDIA")
    print(SUBLINE)

    if not property_media:
        print("  No property media configured.")

    else:
        for media in property_media:
            print(
                f"  - ID={media['id']} | "
                f"media_asset_id={media['media_asset_id']} | "
                f"usage={value(media['usage'])} | "
                f"active={yes_no(media['active'])} | "
                f"order={value(media['display_order'])} | "
                f"caption={value(media['caption'])}"
            )

    # ------------------------------------------------------------------
    # AVAILABILITY
    # ------------------------------------------------------------------

    print()
    print("AVAILABILITY")
    print(SUBLINE)

    if not availability:
        print("  No availability records configured.")

    else:
        for item in availability:
            print(
                f"  - ID={item.id} | "
                f"room_id={value(item.room_id)} | "
                f"{value(item.start_date)} → {value(item.end_date)} | "
                f"status={value(item.status)} | "
                f"rate_override={value(item.rate_override)} | "
                f"currency={value(item.currency)}"
            )

            if item.notes:
                print(
                    f"    notes={value(item.notes)}"
                )

    # ------------------------------------------------------------------
    # REVIEWS
    # ------------------------------------------------------------------

    print()
    print("REVIEWS")
    print(SUBLINE)

    if not reviews:
        print("  No reviews configured.")

    else:
        for review in reviews:
            print(
                f"  - ID={review.id} | "
                f"guest={value(review.guest_name)} | "
                f"rating={value(review.rating)} | "
                f"status={value(review.status)} | "
                f"verified={yes_no(review.verified_stay)} | "
                f"featured={yes_no(review.featured)}"
            )

    # ------------------------------------------------------------------
    # BOOKINGS
    # ------------------------------------------------------------------

    print()
    print("BOOKINGS")
    print(SUBLINE)

    if not bookings:
        print("  No StayBooking records linked to this property.")

    else:
        for booking in bookings:
            print(
                f"  - ID={booking.id} | "
                f"booking_id={value(booking.booking_id)} | "
                f"room_id={value(booking.room_id)} | "
                f"check_in={value(booking.check_in)} | "
                f"check_out={value(booking.check_out)} | "
                f"adults={value(booking.adults)} | "
                f"children={value(booking.children)} | "
                f"rooms={value(booking.rooms_count)}"
            )

    # ------------------------------------------------------------------
    # TOTALS
    # ------------------------------------------------------------------

    print()
    print("PROPERTY TOTALS")
    print(SUBLINE)

    print_field("Rooms", len(rooms))
    print_field("Property amenities", len(amenities))
    print_field("Property media", len(property_media))
    print_field("Availability records", len(availability))
    print_field("Reviews", len(reviews))
    print_field("Bookings", len(bookings))


# --------------------------------------------------------------------------------------
# CATALOGUE SUMMARY
# --------------------------------------------------------------------------------------

def main():
    app = create_app()

    with app.app_context():
        stays = (
            Stay.query
            .order_by(
                Stay.display_order.asc(),
                Stay.id.asc(),
            )
            .all()
        )

        print()
        print(LINE)
        print("THE UNCHARTED ROUTE — STAYS CATALOGUE AUDIT")
        print(LINE)

        print()
        print("MODE")
        print(SUBLINE)
        print("READ-ONLY — NO DATABASE MUTATIONS")

        # ------------------------------------------------------------------
        # DATABASE TOTALS
        # ------------------------------------------------------------------

        print()
        print("DATABASE TOTALS")
        print(SUBLINE)

        print_field("Stay records", Stay.query.count())
        print_field("Stay rooms", StayRoom.query.count())

        # Direct SQL counts for media tables.
        stay_media_count = db.session.execute(
            text("SELECT COUNT(*) FROM stay_media")
        ).scalar()

        stay_room_media_count = db.session.execute(
            text("SELECT COUNT(*) FROM stay_room_media")
        ).scalar()

        stay_room_amenities_count = db.session.execute(
            text("SELECT COUNT(*) FROM stay_room_amenities")
        ).scalar()

        print_field("Stay media", stay_media_count)
        print_field("Stay amenities", StayAmenity.query.count())
        print_field("Stay room media", stay_room_media_count)
        print_field("Stay room amenities", stay_room_amenities_count)
        print_field("Stay availability", StayAvailability.query.count())
        print_field("Stay reviews", StayReview.query.count())
        print_field("Stay bookings", StayBooking.query.count())

        # ------------------------------------------------------------------
        # EXISTING STAYS
        # ------------------------------------------------------------------

        print()
        print("EXISTING STAYS")
        print(SUBLINE)

        if not stays:
            print("  No Stay records found.")

        else:
            for stay in stays:
                print(
                    f"  - ID={stay.id} | "
                    f"{value(stay.property_name)} | "
                    f"slug={value(stay.slug)} | "
                    f"location={value(stay.location)} | "
                    f"destination_id={value(stay.destination_id)} | "
                    f"active={yes_no(stay.active)} | "
                    f"featured={yes_no(stay.featured)}"
                )

        # ------------------------------------------------------------------
        # FULL PROPERTY AUDIT
        # ------------------------------------------------------------------

        for stay in stays:
            audit_stay(stay)

        # ------------------------------------------------------------------
        # TARGET CATALOGUE
        # ------------------------------------------------------------------

        print()
        print(LINE)
        print("INITIAL SIX-PROPERTY TARGET")
        print(LINE)

        target_properties = [
            "Giraffe Manor",
            "JW Marriott Hotel Nairobi",
            "Skynest Residences by CityBlue",
            "Escada Apartments",
            "Mövenpick Hotel & Residences Nairobi",
            "Fairmont Mount Kenya Safari Club",
        ]

        existing_names = {
            stay.property_name.strip().lower()
            for stay in stays
            if stay.property_name
        }

        for name in target_properties:
            status = (
                "EXISTS"
                if name.lower() in existing_names
                else "MISSING"
            )

            print(f"  {status:<8} | {name}")

        # ------------------------------------------------------------------
        # COMPLETE
        # ------------------------------------------------------------------

        print()
        print(LINE)
        print("AUDIT COMPLETE")
        print(LINE)
        print(
            "No records were created, updated, deleted, "
            "or otherwise modified."
        )


if __name__ == "__main__":
    main()