"""
THE UNCHARTED ROUTE
Photography Spots Population

34 retained records enriched
9 excluded records deleted
76 new records created

Dry-run is the default.
Use --apply only after a successful dry run.
"""

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "photography_spots_population.json"
)

EXPECTED_STARTING_COUNT = 43
EXPECTED_RETAINED_COUNT = 34
EXPECTED_DELETE_COUNT = 9
EXPECTED_CREATE_COUNT = 76
EXPECTED_FINAL_COUNT = 110

EXPECTED_DELETE_IDS = {
    8, 9, 27, 28, 29, 31, 32, 42, 43
}

EXPECTED_INACTIVE_DESTINATIONS = {
    12, 17, 20, 22
}

EXPECTED_NEW_DESTINATIONS = {
    7, 9, 12, 17, 20, 22, 25, 28, 30,
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42
}


def slugify(value):
    return re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower()
    ).strip("-")


def validate_population_data(data):

    required_sections = {
        "metadata",
        "updates",
        "delete_ids",
        "creates"
    }

    missing = required_sections - set(data.keys())

    if missing:
        raise ValueError(
            f"Population JSON is missing sections: {sorted(missing)}"
        )

    updates = data["updates"]
    delete_ids = data["delete_ids"]
    creates = data["creates"]

    if len(updates) != EXPECTED_RETAINED_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_RETAINED_COUNT} updates, "
            f"found {len(updates)}"
        )

    if len(delete_ids) != EXPECTED_DELETE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_DELETE_COUNT} delete IDs, "
            f"found {len(delete_ids)}"
        )

    if set(delete_ids) != EXPECTED_DELETE_IDS:
        raise ValueError(
            "Delete IDs do not match the approved deletion list."
        )

    if len(creates) != EXPECTED_CREATE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_CREATE_COUNT} new records, "
            f"found {len(creates)}"
        )

    update_ids = [item["id"] for item in updates]

    if len(set(update_ids)) != EXPECTED_RETAINED_COUNT:
        raise ValueError("Duplicate retained record IDs detected.")

    if set(update_ids) & set(delete_ids):
        raise ValueError(
            "A record cannot be both retained and deleted."
        )

    names = [item["name"].casefold() for item in creates]
    slugs = [item["slug"] for item in creates]

    if len(set(names)) != EXPECTED_CREATE_COUNT:
        raise ValueError("Duplicate new photography spot names.")

    if len(set(slugs)) != EXPECTED_CREATE_COUNT:
        raise ValueError("Duplicate new photography spot slugs.")

    destination_counts = {}

    for item in creates:

        required_fields = [
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
            "active",
            "featured"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in item
        ]

        if missing_fields:
            raise ValueError(
                f"{item.get('name', 'Unnamed record')} "
                f"is missing fields: {missing_fields}"
            )

        if not item["name"].strip():
            raise ValueError("A new record has an empty name.")

        if not item["description"].strip():
            raise ValueError(
                f"{item['name']} has an empty description."
            )

        if not item["location"].strip():
            raise ValueError(
                f"{item['name']} has an empty location."
            )

        if item["slug"] != slugify(item["name"]):
            raise ValueError(
                f"Invalid slug for {item['name']}: {item['slug']}"
            )

        if item["active"] is not False:
            raise ValueError(
                f"New record must be inactive: {item['name']}"
            )

        if item["featured"] is not False:
            raise ValueError(
                f"New record must not be featured: {item['name']}"
            )

        latitude = item["latitude"]
        longitude = item["longitude"]

        if not -90 <= latitude <= 90:
            raise ValueError(
                f"Invalid latitude for {item['name']}"
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                f"Invalid longitude for {item['name']}"
            )

        destination_id = item["destination_id"]

        destination_counts[destination_id] = (
            destination_counts.get(destination_id, 0) + 1
        )

    if set(destination_counts) != EXPECTED_NEW_DESTINATIONS:
        raise ValueError(
            "New records do not cover the approved destination list."
        )

    incorrect_counts = {
        destination_id: count
        for destination_id, count in destination_counts.items()
        if count != 4
    }

    if incorrect_counts:
        raise ValueError(
            f"Expected four new spots per destination: {incorrect_counts}"
        )

    return updates, delete_ids, creates


def main():

    parser = argparse.ArgumentParser(
        description="Populate TUR photography spots."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit changes. Without this flag, changes are rolled back."
    )

    args = parser.parse_args()

    print("\n" + "=" * 85)
    print("THE UNCHARTED ROUTE - PHOTOGRAPHY SPOTS POPULATION")
    print("=" * 85)

    print(f"Data file: {DATA_FILE}")

    print(
        "Execution mode:",
        "APPLY" if args.apply else "DRY RUN"
    )

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Population JSON not found: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    updates, delete_ids, creates = validate_population_data(data)

    sys.path.insert(0, str(PROJECT_ROOT))

    from app import create_app, db
    from app.models.photography_spot import PhotographySpot
    from app.models.destination import Destination

    app = create_app()

    with app.app_context():

        try:

            existing = PhotographySpot.query.order_by(
                PhotographySpot.id
            ).all()

            existing_ids = {
                spot.id for spot in existing
            }

            update_ids = {
                item["id"] for item in updates
            }

            delete_id_set = set(delete_ids)

            print("\nVALIDATING EXISTING DATABASE")
            print("-" * 85)

            if len(existing) != EXPECTED_STARTING_COUNT:
                raise ValueError(
                    f"Expected {EXPECTED_STARTING_COUNT} existing spots, "
                    f"found {len(existing)}."
                )

            if update_ids | delete_id_set != existing_ids:
                raise ValueError(
                    "Existing database IDs do not match the approved "
                    "34 retained + 9 excluded records."
                )

            if update_ids & delete_id_set:
                raise ValueError(
                    "Retained and deleted IDs overlap."
                )

            print("Existing photography spots: 43")
            print("Retained records: 34")
            print("Records marked for deletion: 9")
            print("New records: 76")

            destinations = {
                destination.id: destination
                for destination in Destination.query.all()
            }

            missing_destinations = (
                EXPECTED_NEW_DESTINATIONS
                - set(destinations)
            )

            if missing_destinations:
                raise ValueError(
                    f"Missing destination records: "
                    f"{sorted(missing_destinations)}"
                )

            print("\nVALIDATING DESTINATIONS")
            print("-" * 85)

            for destination_id in EXPECTED_INACTIVE_DESTINATIONS:

                destination = destinations.get(destination_id)

                if destination is None:
                    raise ValueError(
                        f"Destination {destination_id} does not exist."
                    )

                if destination.active:
                    raise ValueError(
                        f"Destination {destination_id} is expected "
                        "to remain inactive."
                    )

            print(
                "Inactive destinations preserved:",
                sorted(EXPECTED_INACTIVE_DESTINATIONS)
            )

            existing_names = {
                spot.name.casefold()
                for spot in existing
            }

            existing_slugs = {
                spot.slug
                for spot in existing
                if spot.slug
            }

            new_names = {
                item["name"].casefold()
                for item in creates
            }

            new_slugs = {
                item["slug"]
                for item in creates
            }

            if existing_names & new_names:
                raise ValueError(
                    "One or more new photography spot names "
                    "already exist."
                )

            if existing_slugs & new_slugs:
                raise ValueError(
                    "One or more new photography spot slugs "
                    "already exist."
                )

            retained = {
                spot.id: spot
                for spot in existing
                if spot.id in update_ids
            }

            # Preserve the active and featured flags of retained records.
            original_flags = {
                spot_id: (
                    spot.active,
                    spot.featured
                )
                for spot_id, spot in retained.items()
            }

            # Preserve the known ExperiencePhotography association.
            spot_two = retained.get(2)

            if spot_two is None:
                raise ValueError(
                    "Photography spot ID 2 is missing from retained records."
                )

            if not any(
                link.experience_id == 1
                for link in spot_two.experiences.all()
            ):
                raise ValueError(
                    "Required association spot ID 2 → experience ID 1 "
                    "was not found."
                )

            print("\nVALIDATING EXPERIENCE ASSOCIATIONS")
            print("-" * 85)

            print(
                "Preserved: Photography spot 2 → Experience 1"
            )

            excluded = [
                spot
                for spot in existing
                if spot.id in delete_id_set
            ]

            for spot in excluded:

                if spot.experiences.count():
                    raise RuntimeError(
                        f"Refusing to delete photography spot "
                        f"{spot.id} ({spot.name}): "
                        "it has ExperiencePhotography associations."
                    )

            print(
                "All nine excluded records are safe to delete."
            )

            print("\nAPPLYING POPULATION OPERATIONS")
            print("-" * 85)

            # Enrich retained records.
            for item in updates:

                spot = retained[item["id"]]

                for field, value in item["fields"].items():

                    if field in {
                        "id",
                        "name",
                        "slug",
                        "active",
                        "featured"
                    }:
                        raise ValueError(
                            f"Forbidden update field '{field}' "
                            f"for photography spot {spot.id}."
                        )

                    if not hasattr(spot, field):
                        raise ValueError(
                            f"Unknown PhotographySpot field: {field}"
                        )

                    setattr(spot, field, value)

            # Delete only the approved excluded records.
            for spot in excluded:
                db.session.delete(spot)

            # Create all 76 new inactive records.
            for item in creates:

                if item["destination_id"] not in destinations:
                    raise ValueError(
                        f"Unknown destination ID "
                        f"{item['destination_id']}."
                    )

                db.session.add(
                    PhotographySpot(**item)
                )

            db.session.flush()

            final_count = PhotographySpot.query.count()

            if final_count != EXPECTED_FINAL_COUNT:
                raise ValueError(
                    f"Expected {EXPECTED_FINAL_COUNT} final records, "
                    f"found {final_count}."
                )

            # Check retained flags have not changed.
            for spot_id, original in original_flags.items():

                spot = db.session.get(
                    PhotographySpot,
                    spot_id
                )

                current = (
                    spot.active,
                    spot.featured
                )

                if current != original:
                    raise ValueError(
                        f"Active/featured flags changed for "
                        f"retained spot {spot_id}."
                    )

            # Verify the required experience association again.
            spot_two_after = db.session.get(
                PhotographySpot,
                2
            )

            if not any(
                link.experience_id == 1
                for link in spot_two_after.experiences.all()
            ):
                raise ValueError(
                    "Spot 2 → Experience 1 association was not preserved."
                )

            # Verify all newly created records remain inactive.
            for item in creates:

                spot = PhotographySpot.query.filter_by(
                    slug=item["slug"]
                ).first()

                if spot is None:
                    raise ValueError(
                        f"New record missing after flush: {item['name']}"
                    )

                if spot.active or spot.featured:
                    raise ValueError(
                        f"New record unexpectedly active or featured: "
                        f"{item['name']}"
                    )

            if args.apply:

                db.session.commit()

                print("\n" + "=" * 85)
                print("POPULATION COMMITTED SUCCESSFULLY")
                print("=" * 85)

                print("Retained and enriched: 34")
                print("Deleted: 9")
                print("Created: 76")
                print("Final photography spots: 110")

            else:

                db.session.rollback()

                print("\n" + "=" * 85)
                print("DRY RUN PASSED")
                print("=" * 85)

                print("All validation checks passed.")
                print("34 retained records validated.")
                print("9 approved deletions validated.")
                print("76 new records validated.")
                print("Final projected count: 110.")
                print("No database changes were committed.")
                print("\nRun with --apply to commit the changes.")

        except Exception:

            db.session.rollback()

            print("\n" + "=" * 85)
            print("POPULATION FAILED")
            print("=" * 85)

            print("[WARNING] Database transaction rolled back.")

            raise


if __name__ == "__main__":
    main()