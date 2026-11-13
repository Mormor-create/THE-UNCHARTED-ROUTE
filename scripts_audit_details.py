from app import create_app
from app.models.destination import Destination
from app.models.experience import Experience

app = create_app()

with app.app_context():

    print("\n" + "=" * 90)
    print("DESTINATION DETAILS")
    print("=" * 90)

    for d in Destination.query.order_by(Destination.id).all():
        print(f"\n{d.id} | {d.name} | {d.slug}")
        print(f"Country: {d.country} | County: {d.county} | Region: {d.region}")
        print(f"Active: {d.active} | Featured: {d.featured} | Homepage: {d.show_on_homepage}")
        print(f"Description: {bool(d.description)}")
        print(f"Short description: {bool(d.short_description)}")
        print(f"Featured media: {d.featured_image_id}")
        print(f"Banner media: {d.banner_image_id}")

    for code in ("WNA-001", "WNA-002", "WNA-005", "LUX-001"):
        e = Experience.query.filter_by(experience_code=code).first()

        if not e:
            continue

        print("\n" + "=" * 90)
        print(f"EXPERIENCE DETAILS: {code}")
        print("=" * 90)

        print(f"Title: {e.title}")
        print(f"Short description:\n{e.short_description}")
        print(f"Description:\n{e.description}")
        print(f"Meeting point: {e.meeting_point}")
        print(f"Location: {e.location}")
        print(f"Minimum people: {e.minimum_people}")
        print(f"Maximum people: {e.maximum_people}")
        print(f"Minimum age: {e.minimum_age}")
        print(f"Difficulty: {e.difficulty}")
        print(f"Featured: {e.featured}")
        print(f"Homepage: {e.show_on_homepage}")

        for relationship in (
            "pricing", "itinerary", "inclusions", "exclusions",
            "highlights", "addons", "packing_items", "safety_rules",
            "requirements", "faqs", "wildlife", "schedules",
        ):
            items = getattr(e, relationship)
            if hasattr(items, "all"):
                items = items.all()

            print(f"\n--- {relationship.upper()} ---")
            for item in items:
                print(item.__dict__)

