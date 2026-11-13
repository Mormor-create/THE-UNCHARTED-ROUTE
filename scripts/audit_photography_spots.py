"""
THE UNCHARTED ROUTE
PHOTOGRAPHY SPOTS — READ-ONLY AUDIT

Exports:
    instance/tur_audit_reports/12_photography_spots.json
    instance/tur_audit_reports/12_photography_spots.csv

This script does not modify the database.
"""

import csv
import importlib
import json
import pkgutil
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import inspect as sqlalchemy_inspect

# ============================================================
# PROJECT PATH
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))

sys.path.insert(0, str(PROJECT_ROOT))

LOCAL_APP_PACKAGE = PROJECT_ROOT / "app" / "__init__.py"

if not LOCAL_APP_PACKAGE.exists():
    raise FileNotFoundError(
        f"Local Flask application not found: {LOCAL_APP_PACKAGE}"
    )

print("=" * 85)
print("THE UNCHARTED ROUTE — PHOTOGRAPHY SPOTS AUDIT")
print("=" * 85)
print(f"Project root: {PROJECT_ROOT}")
print(f"Application:  {LOCAL_APP_PACKAGE}")


# ============================================================
# APPLICATION
# ============================================================

from app import create_app

app = create_app()


# ============================================================
# MODEL DISCOVERY
# ============================================================

def discover_model(class_name):
    """
    Find a model class by name inside the local app.models package.
    This avoids assuming the exact module filename.
    """

    models_package = importlib.import_module("app.models")

    # Check classes already exposed by app.models.
    model = getattr(models_package, class_name, None)

    if model is not None:
        return model

    package_path = getattr(models_package, "__path__", None)

    if package_path:
        for module_info in pkgutil.walk_packages(
            package_path,
            prefix="app.models."
        ):
            try:
                module = importlib.import_module(module_info.name)
            except Exception as exc:
                print(
                    f"WARNING: Could not import {module_info.name}: {exc}"
                )
                continue

            model = getattr(module, class_name, None)

            if model is not None:
                return model

    raise ImportError(
        f"Could not locate model class '{class_name}' "
        "inside the local app.models package."
    )


PhotographySpot = discover_model("PhotographySpot")

print(f"\nPhotographySpot model: {PhotographySpot.__module__}")


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return str(value)


def serialize_model(instance):
    """
    Export every mapped database column on a model.
    This ensures that no PhotographySpot fields are silently omitted.
    """

    if instance is None:
        return None

    mapper = sqlalchemy_inspect(instance).mapper
    result = {}

    for column_property in mapper.column_attrs:
        key = column_property.key

        try:
            result[key] = serialize_value(getattr(instance, key))
        except Exception as exc:
            result[key] = f"[READ ERROR: {exc}]"

    return result


def get_relationship_value(instance, relationship_name):
    """
    Read a SQLAlchemy relationship without assuming whether it is
    dynamic, scalar, or a normal collection.
    """

    if instance is None:
        return None

    try:
        value = getattr(instance, relationship_name)
    except Exception:
        return None

    if value is None:
        return None

    if hasattr(value, "all") and callable(value.all):
        return value.all()

    if isinstance(value, (list, tuple, set)):
        return list(value)

    return value


def get_destination_records(experience):
    """
    Find Destination relationships on an Experience.

    PhotographySpot has no direct destination_id in the current
    model structure, so destination information is obtained through
    the linked experience.
    """

    if experience is None:
        return []

    mapper = sqlalchemy_inspect(experience).mapper
    destinations = []

    for relationship in mapper.relationships:
        target_class = relationship.mapper.class_
        target_name = target_class.__name__.lower()
        relationship_name = relationship.key.lower()

        if (
            target_name == "destination"
            or relationship_name in {"destination", "destinations"}
        ):
            related = get_relationship_value(
                experience,
                relationship.key
            )

            if related is None:
                continue

            if not isinstance(related, list):
                related = [related]

            for destination in related:
                if destination is not None:
                    destinations.append(destination)

    return destinations


def serialize_experience_link(association):
    """
    Serialize one ExperiencePhotography association and its
    linked Experience and Destination records.
    """

    association_data = serialize_model(association)

    experience = getattr(association, "experience", None)

    experience_data = serialize_model(experience)

    destinations = get_destination_records(experience)

    destination_data = [
        serialize_model(destination)
        for destination in destinations
    ]

    return {
        "association": association_data,
        "experience": experience_data,
        "destinations": destination_data,
    }


def get_spot_experience_associations(spot):
    """
    PhotographySpot.experiences is expected to return
    ExperiencePhotography association records.
    """

    related = get_relationship_value(spot, "experiences")

    if related is None:
        return []

    if not isinstance(related, list):
        related = [related]

    return related


# ============================================================
# AUDIT
# ============================================================

def run_audit():
    output_directory = (
        PROJECT_ROOT
        / "instance"
        / "tur_audit_reports"
    )

    output_directory.mkdir(parents=True, exist_ok=True)

    json_path = output_directory / "12_photography_spots.json"
    csv_path = output_directory / "12_photography_spots.csv"

    print("\n" + "=" * 85)
    print("READING PHOTOGRAPHY SPOTS")
    print("=" * 85)

    with app.app_context():

        spots = (
            PhotographySpot.query
            .order_by(PhotographySpot.id.asc())
            .all()
        )

        audit_records = []

        for index, spot in enumerate(spots, start=1):

            spot_data = serialize_model(spot)

            associations = get_spot_experience_associations(spot)

            linked_experiences = [
                serialize_experience_link(association)
                for association in associations
            ]

            destination_map = {}

            for linked in linked_experiences:
                for destination in linked["destinations"]:
                    if destination is None:
                        continue

                    destination_id = destination.get("id")

                    destination_key = (
                        str(destination_id)
                        if destination_id is not None
                        else json.dumps(
                            destination,
                            sort_keys=True,
                            default=str
                        )
                    )

                    destination_map[destination_key] = destination

            destinations = list(destination_map.values())

            record = {
                "spot": spot_data,
                "experience_association_count": len(associations),
                "linked_experiences": linked_experiences,
                "destinations_via_linked_experiences": destinations,
                "destination_linkage_note": (
                    "Destinations are derived from linked experiences. "
                    "PhotographySpot has no direct destination_id field."
                ),
            }

            audit_records.append(record)

            print(
                f"[{index:02d}/{len(spots):02d}] "
                f"{spot_data.get('name', 'Unnamed spot')} "
                f"| ID: {spot_data.get('id')} "
                f"| Active: {spot_data.get('active')} "
                f"| Experiences: {len(associations)} "
                f"| Destinations: {len(destinations)}"
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        active_count = sum(
            1 for record in audit_records
            if record["spot"].get("active") is True
        )

        inactive_count = sum(
            1 for record in audit_records
            if record["spot"].get("active") is False
        )

        featured_count = sum(
            1 for record in audit_records
            if record["spot"].get("featured") is True
        )

        with_coordinates = sum(
            1 for record in audit_records
            if (
                record["spot"].get("latitude") is not None
                and record["spot"].get("longitude") is not None
            )
        )

        without_coordinates = len(audit_records) - with_coordinates

        linked_count = sum(
            1 for record in audit_records
            if record["experience_association_count"] > 0
        )

        unlinked_count = len(audit_records) - linked_count

        with_destination = sum(
            1 for record in audit_records
            if record["destinations_via_linked_experiences"]
        )

        without_destination = len(audit_records) - with_destination

        names = [
            (record["spot"].get("name") or "").strip().casefold()
            for record in audit_records
        ]

        slugs = [
            (record["spot"].get("slug") or "").strip().casefold()
            for record in audit_records
        ]

        duplicate_names = {
            name: count
            for name, count in Counter(names).items()
            if name and count > 1
        }

        duplicate_slugs = {
            slug: count
            for slug, count in Counter(slugs).items()
            if slug and count > 1
        }

        summary = {
            "total_photography_spots": len(audit_records),
            "active": active_count,
            "inactive": inactive_count,
            "featured": featured_count,
            "with_coordinates": with_coordinates,
            "without_coordinates": without_coordinates,
            "linked_to_experiences": linked_count,
            "not_linked_to_experiences": unlinked_count,
            "with_destination_established_through_experience": with_destination,
            "without_destination_established_through_experience": without_destination,
            "duplicate_names": duplicate_names,
            "duplicate_slugs": duplicate_slugs,
            "destination_relationship_note": (
                "PhotographySpot has no direct destination_id. "
                "Destination associations in this report are derived "
                "from ExperiencePhotography -> Experience -> Destination."
            ),
        }

        report = {
            "project": "The Uncharted Route",
            "report": "Photography Spots CMS Audit",
            "read_only": True,
            "summary": summary,
            "photography_spots": audit_records,
        }

        # ----------------------------------------------------
        # WRITE JSON
        # ----------------------------------------------------

        with json_path.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
                default=str
            )

        # ----------------------------------------------------
        # WRITE CSV
        # ----------------------------------------------------

        csv_columns = [
            "id",
            "name",
            "slug",
            "description",
            "latitude",
            "longitude",
            "altitude",
            "photography_type",
            "difficulty",
            "best_time",
            "best_season",
            "recommended_lens",
            "recommended_equipment",
            "camera_settings",
            "accessibility",
            "photography_tips",
            "safety_notes",
            "featured",
            "active",
            "created_at",
            "updated_at",
            "experience_association_count",
            "linked_experiences",
            "destinations_via_linked_experiences",
        ]

        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=csv_columns,
                extrasaction="ignore"
            )

            writer.writeheader()

            for record in audit_records:

                row = dict(record["spot"])

                row["experience_association_count"] = (
                    record["experience_association_count"]
                )

                row["linked_experiences"] = json.dumps(
                    [
                        {
                            "experience": item["experience"],
                            "destinations": item["destinations"],
                            "association": item["association"],
                        }
                        for item in record["linked_experiences"]
                    ],
                    ensure_ascii=False,
                    default=str
                )

                row["destinations_via_linked_experiences"] = json.dumps(
                    record["destinations_via_linked_experiences"],
                    ensure_ascii=False,
                    default=str
                )

                writer.writerow(row)

        # ----------------------------------------------------
        # PRINT SUMMARY
        # ----------------------------------------------------

        print("\n" + "=" * 85)
        print("PHOTOGRAPHY SPOTS AUDIT SUMMARY")
        print("=" * 85)

        print(f"Total spots:                       {summary['total_photography_spots']}")
        print(f"Active:                            {summary['active']}")
        print(f"Inactive:                          {summary['inactive']}")
        print(f"Featured:                          {summary['featured']}")
        print(f"With coordinates:                  {summary['with_coordinates']}")
        print(f"Without coordinates:               {summary['without_coordinates']}")
        print(f"Linked to experiences:             {summary['linked_to_experiences']}")
        print(f"Not linked to experiences:         {summary['not_linked_to_experiences']}")
        print(f"With destination established:      {summary['with_destination_established_through_experience']}")
        print(f"Without destination established:   {summary['without_destination_established_through_experience']}")

        print("\nDUPLICATE CHECKS")
        print("-" * 85)
        print(f"Duplicate names: {duplicate_names or 'None detected'}")
        print(f"Duplicate slugs: {duplicate_slugs or 'None detected'}")

        print("\nEXPORTS")
        print("-" * 85)
        print(f"JSON: {json_path}")
        print(f"CSV:  {csv_path}")

        print("\nAudit completed. No database records were modified.")
        print("=" * 85)


if __name__ == "__main__":
    run_audit()