from app import create_app
from extensions import db
from app.models.destination import Destination


DESTINATIONS_TO_DELETE = {
    "aberdare national park",
    "hell's gate national park",
    "nanyuki",
    "ol pejeta conservancy",
}

app = create_app()

with app.app_context():

    print("\n" + "=" * 90)
    print("DESTINATION CLEANUP — FINAL FOUR")
    print("=" * 90)

    all_destinations = Destination.query.all()

    targets = [
        destination
        for destination in all_destinations
        if destination.name.strip().lower() in DESTINATIONS_TO_DELETE
    ]

    found_names = {destination.name.strip().lower() for destination in targets}
    missing = DESTINATIONS_TO_DELETE - found_names

    if missing:
        print("\nWARNING: These destinations were not found:")
        for name in sorted(missing):
            print(f"  - {name}")

    if not targets:
        print("\nNo matching destinations found.")
    else:
        blocked = []

        print("\nDESTINATIONS SELECTED FOR DELETION")

        for destination in targets:
            experiences = destination.experiences.all()
            stays_count = destination.stays.count()

            print("\n" + "-" * 70)
            print(f"Destination: {destination.name}")
            print(f"Status: {'ACTIVE' if destination.active else 'INACTIVE'}")
            print(f"Attached Experiences: {len(experiences)}")
            print(f"Attached Stays: {stays_count}")

            if experiences or stays_count:
                blocked.append(destination.name)
                print("PROTECTED: Attached records detected. Will not delete.")

        if blocked:
            print("\n" + "=" * 90)
            print("DELETION CANCELLED")
            print("=" * 90)
            print("Some destinations have attached Experiences or Stays.")
            print("No destinations have been deleted.")
            print("\nPlease review these destinations:")
            for name in blocked:
                print(f"  - {name}")

        else:
            try:
                for destination in targets:
                    db.session.delete(destination)

                db.session.commit()

                print("\n" + "=" * 90)
                print("DELETION COMMITTED SUCCESSFULLY")
                print("=" * 90)

                for destination in targets:
                    print(f"REMOVED: {destination.name}")

            except Exception as error:
                db.session.rollback()
                print("\nERROR: Deletion failed. All changes rolled back.")
                print(error)

    # FINAL INVENTORY
    print("\n" + "=" * 90)
    print("FINAL DESTINATION INVENTORY")
    print("=" * 90)

    remaining = Destination.query.order_by(Destination.name.asc()).all()

    for destination in remaining:
        status = "ACTIVE" if destination.active else "INACTIVE"
        print(f"{destination.name:<45} | {status}")

    active_count = sum(1 for d in remaining if d.active)
    inactive_count = len(remaining) - active_count

    print("\n" + "=" * 90)
    print("FINAL SUMMARY")
    print("=" * 90)

    print(f"Total remaining destinations: {len(remaining)}")
    print(f"Active destinations: {active_count}")
    print(f"Inactive destinations: {inactive_count}")

    remaining_names = {
        destination.name.strip().lower()
        for destination in remaining
    }

    print("\nDELETION VERIFICATION")

    for name in sorted(DESTINATIONS_TO_DELETE):
        if name in remaining_names:
            print(f"STILL PRESENT: {name}")
        else:
            print(f"REMOVED: {name}")

    print("\nPHUKET VERIFICATION")

    phuket = next(
        (d for d in remaining if d.name.strip().lower() == "phuket"),
        None
    )

    if phuket:
        print(f"Phuket preserved — Status: {'ACTIVE' if phuket.active else 'INACTIVE'}")
    else:
        print("WARNING: Phuket was not found!")

    print("\nInventory complete.")
