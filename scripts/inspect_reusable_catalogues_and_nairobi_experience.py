"""
===============================================================================
THE UNCHARTED ROUTE
Reusable Catalogue & Nairobi National Park Audit
===============================================================================
READ-ONLY SCRIPT.

Inspects:
    - Destinations
    - Signature Moments
    - Experience Tags
    - Accessibility Profiles
    - Conservation Stories
    - Cancellation Policies
    - Experience Categories
    - Existing Experience difficulty values
    - WNA-001 Nairobi National Park Experience
    - Its populated relationships and related records

Output:
    instance/reusable_catalogue_and_nairobi_experience_audit.json
No database records are created, updated, or deleted.
===============================================================================
"""
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project root is importable when running this script from scripts/
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect as sqlalchemy_inspect

from app import create_app
from app.models import Experience


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CATALOGUE_TABLES = {
    "destinations": ["destinations"],
    "signature_moments": ["signature_moments"],
    "experience_tags": ["tags"],
    "accessibility_profiles": ["accessibility_profiles"],
    "conservation_stories": ["conservation_stories"],
    "cancellation_policies": ["cancellation_policies"],
    "experience_categories": ["experience_categories"],
}

TARGET_EXPERIENCE_CODE = "WNA-001"
TARGET_EXPERIENCE_SLUG = "nairobi-national-park-experience"

MAX_RELATIONSHIP_DEPTH = 2


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def serialize_value(value):
    """Convert values into JSON-compatible representations."""

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def serialize_model(obj, depth=0, visited=None):
    """
    Serialize all database columns on a model instance.

    Relationships are included up to MAX_RELATIONSHIP_DEPTH so that
    related records such as MediaAsset, wildlife species and photography
    spots can also be inspected without entering infinite relationship loops.
    """

    if obj is None:
        return None

    if visited is None:
        visited = set()

    mapper = sqlalchemy_inspect(obj).mapper

    identity = sqlalchemy_inspect(obj).identity

    object_key = (
        mapper.class_.__name__,
        identity if identity is not None else id(obj),
    )

    if object_key in visited:
        return {
            "_reference": mapper.class_.__name__,
            "_identity": identity,
        }

    current_visited = visited | {object_key}

    result = {
        "_model": mapper.class_.__name__,
        "_table": mapper.local_table.name,
    }

    # All actual database columns.
    for column in mapper.column_attrs:
        result[column.key] = serialize_value(
            getattr(obj, column.key)
        )

    if depth >= MAX_RELATIONSHIP_DEPTH:
        return result

    # Related records.
    for relationship in mapper.relationships:
        relationship_name = relationship.key

        try:
            related = getattr(obj, relationship_name)

            if relationship.uselist:
                if hasattr(related, "all"):
                    related = related.all()
                else:
                    related = list(related)

                result[relationship_name] = [
                    serialize_model(
                        item,
                        depth=depth + 1,
                        visited=current_visited,
                    )
                    for item in related
                ]

            else:
                result[relationship_name] = serialize_model(
                    related,
                    depth=depth + 1,
                    visited=current_visited,
                )

        except Exception as exc:
            result[relationship_name] = {
                "_inspection_error": str(exc)
            }

    return result


# ---------------------------------------------------------------------------
# Catalogue inspection
# ---------------------------------------------------------------------------

def get_registered_models():
    """Return all registered SQLAlchemy model classes indexed by table."""

    models = {}

    for mapper in db.Model.registry.mappers:
        model_class = mapper.class_
        table_name = mapper.local_table.name

        models[table_name] = model_class

    return models


def inspect_catalogues():
    """Read all existing reusable catalogue records."""

    registered_models = get_registered_models()

    catalogue_report = {}

    for catalogue_name, candidate_tables in CATALOGUE_TABLES.items():

        model_class = None
        matched_table = None

        for table_name in candidate_tables:
            if table_name in registered_models:
                model_class = registered_models[table_name]
                matched_table = table_name
                break

        if model_class is None:
            catalogue_report[catalogue_name] = {
                "status": "MODEL_NOT_FOUND",
                "expected_tables": candidate_tables,
            }
            continue

        records = model_class.query.order_by(
            model_class.id.asc()
        ).all()

        catalogue_report[catalogue_name] = {
            "status": "FOUND",
            "model": model_class.__name__,
            "table": matched_table,
            "total_records": len(records),
            "records": [
                serialize_model(record)
                for record in records
            ],
        }

    return catalogue_report


# ---------------------------------------------------------------------------
# Difficulty inspection
# ---------------------------------------------------------------------------

def inspect_difficulty_values():
    """Read distinct difficulty values currently used by Experiences."""

    values = (
        db.session.query(Experience.difficulty)
        .distinct()
        .order_by(Experience.difficulty.asc())
        .all()
    )

    return [
        value[0]
        for value in values
    ]


# ---------------------------------------------------------------------------
# Nairobi National Park inspection
# ---------------------------------------------------------------------------

def inspect_nairobi_national_park():
    """Read WNA-001 and all its populated relationships."""

    experience = (
        Experience.query
        .filter(
            (Experience.experience_code == TARGET_EXPERIENCE_CODE)
            | (Experience.slug == TARGET_EXPERIENCE_SLUG)
        )
        .first()
    )

    if experience is None:
        return {
            "status": "NOT_FOUND",
            "experience_code": TARGET_EXPERIENCE_CODE,
            "slug": TARGET_EXPERIENCE_SLUG,
        }

    return {
        "status": "FOUND",
        "experience": serialize_model(experience),
    }


# ---------------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------------

def run_audit():

    app = create_app()

    with app.app_context():

        print("\n" + "=" * 80)
        print("THE UNCHARTED ROUTE — DATABASE AUDIT")
        print("=" * 80)

        report = {
            "audit_type": "READ_ONLY",
            "project": "The Uncharted Route",
            "catalogues": inspect_catalogues(),
            "difficulty_values": inspect_difficulty_values(),
            "nairobi_national_park": inspect_nairobi_national_park(),
        }

        output_directory = Path(app.instance_path)
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_directory
            / "reusable_catalogue_and_nairobi_experience_audit.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

        print("\nCATALOGUE SUMMARY")
        print("-" * 80)

        for name, data in report["catalogues"].items():

            if data["status"] == "FOUND":
                print(
                    f"{name}: "
                    f"{data['total_records']} records"
                )
            else:
                print(
                    f"{name}: "
                    f"{data['status']}"
                )

        print("\nDIFFICULTY VALUES")
        print("-" * 80)

        for value in report["difficulty_values"]:
            print(f"- {value}")

        print("\nNAIROBI NATIONAL PARK")
        print("-" * 80)

        experience_data = report["nairobi_national_park"]

        if experience_data["status"] == "FOUND":
            print("WNA-001 successfully inspected.")
        else:
            print("WNA-001 was not found.")

        print("\nAUDIT FILE")
        print("-" * 80)
        print(output_file)
        print("\nAudit completed. No database changes were made.")
        print("=" * 80)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from extensions import db

    run_audit()
