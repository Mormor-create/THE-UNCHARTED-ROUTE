from app import create_app
from app.models.destination import Destination
from app.models.experience import Experience
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPackageOption,
    SafariPackageRate,
)

app = create_app()

with app.app_context():

    print("\n" + "=" * 100)
    print("REGULAR DESTINATIONS")
    print("=" * 100)

    for d in Destination.query.order_by(Destination.country, Destination.name).all():
        print(
            f"{d.id} | {d.name} | {d.country} | "
            f"County={d.county} | Region={d.region} | "
            f"Active={d.active} | Experiences={d.experiences.count()} | "
            f"Stays={d.stays.count()}"
        )

    print("\n" + "=" * 100)
    print("EXPERIENCE CONTENT COMPLETENESS")
    print("=" * 100)

    for e in Experience.query.order_by(Experience.id).all():
        print(f"\n{e.experience_code} | {e.title}")
        print(f"Destination: {e.destination.name if e.destination else 'MISSING'}")
        print(f"Category: {e.category.name if e.category else 'MISSING'}")
        print(f"Price: {e.price_from} {e.currency}")
        print(f"Duration: {e.duration}")
        print(f"Description: {bool(e.description)}")
        print(f"Cancellation policy: {bool(e.cancellation_policy_id)}")
        print(f"Conservation story: {bool(e.conservation_story_id)}")

        for relationship in (
            "pricing", "itinerary", "inclusions", "exclusions",
            "highlights", "addons", "packing_items", "safety_rules",
            "requirements", "faqs", "wildlife", "photography_spots",
            "signature_moments", "schedules", "reviews", "media",
        ):
            try:
                value = getattr(e, relationship)
                count = value.count() if hasattr(value, "count") else len(value)
                print(f"  {relationship}: {count}")
            except Exception as exc:
                print(f"  {relationship}: ERROR - {exc}")

    print("\n" + "=" * 100)
    print("SAFARI DESTINATIONS")
    print("=" * 100)

    for d in SafariDestination.query.order_by(SafariDestination.display_order, SafariDestination.name).all():
        print(
            f"{d.id} | {d.name} | {d.slug} | "
            f"Active={d.active} | Properties={len(d.properties)}"
        )

    print("\n" + "=" * 100)
    print("SAFARI PROPERTIES AND PACKAGES")
    print("=" * 100)

    for p in SafariProperty.query.order_by(SafariProperty.destination_id, SafariProperty.display_order).all():
        print(
            f"\nPROPERTY: {p.id} | {p.name} | {p.slug} | "
            f"Destination={p.destination.name if p.destination else 'MISSING'} | "
            f"Active={p.active}"
        )
        print(f"  Overview: {bool(p.overview)}")
        print(f"  Property story: {bool(p.property_story)}")
        print(f"  Accommodation: {bool(p.accommodation_details)}")
        print(f"  Dining: {bool(p.dining_information)}")
        print(f"  Booking conditions: {bool(p.booking_conditions)}")

        for option in p.package_options:
            print(
                f"  PACKAGE: {option.name} | {option.slug} | "
                f"{option.duration_days}D/{option.duration_nights}N | "
                f"Active={option.active}"
            )
            print(f"    Itinerary days: {len(option.itinerary_days)}")
            print(f"    Rates: {len(option.rates)}")

            for rate in option.rates:
                print(
                    f"      {rate.name} | {rate.pricing_basis} | "
                    f"{rate.amount} {rate.currency} | "
                    f"Season={rate.season_name} | "
                    f"Active={rate.active}"
                )
