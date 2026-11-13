from app import create_app
from app.models.destination import Destination
from app.models.experience import Experience

app = create_app()

with app.app_context():
    destinations = (
        Destination.query
        .order_by(Destination.id.asc())
        .all()
    )

    print("\n" + "=" * 110)
    print("THE UNCHARTED ROUTE — DESTINATION COVERAGE AUDIT")
    print("=" * 110)

    total_destinations = len(destinations)
    total_experiences = 0
    total_active_experiences = 0
    active_destinations = 0
    inactive_destinations = 0

    for destination in destinations:
        experiences = (
            Experience.query
            .filter_by(destination_id=destination.id)
            .order_by(Experience.id.asc())
            .all()
        )

        active_experiences = [
            experience for experience in experiences
            if experience.active
        ]

        status = "ACTIVE" if destination.active else "INACTIVE"

        if destination.active:
            active_destinations += 1
        else:
            inactive_destinations += 1

        total_experiences += len(experiences)
        total_active_experiences += len(active_experiences)

        print("\n" + "-" * 110)
        print(
            f"DESTINATION: {destination.name} "
            f"| ID: {destination.id} "
            f"| STATUS: {status}"
        )
        print(
            f"TOTAL EXPERIENCES: {len(experiences)} "
            f"| ACTIVE EXPERIENCES: {len(active_experiences)}"
        )

        if not experiences:
            print("  No experiences currently associated.")
            continue

        for experience in experiences:
            experience_status = (
                "ACTIVE" if experience.active else "INACTIVE"
            )

            print(
                f"  ID: {experience.id:<5} "
                f"CODE: {experience.experience_code:<18} "
                f"STATUS: {experience_status:<8} "
                f"TITLE: {experience.title}"
            )

    print("\n" + "=" * 110)
    print("OVERALL SUMMARY")
    print("=" * 110)
    print(f"Total destinations:          {total_destinations}")
    print(f"Active destinations:         {active_destinations}")
    print(f"Inactive destinations:       {inactive_destinations}")
    print(f"Total experiences:           {total_experiences}")
    print(f"Active experiences:          {total_active_experiences}")
    print("=" * 110)
    print("READ-ONLY AUDIT COMPLETE — NO DATABASE RECORDS MODIFIED.")