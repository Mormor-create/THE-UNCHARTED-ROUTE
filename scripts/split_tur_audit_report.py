"""
===============================================================================
THE UNCHARTED ROUTE
Audit Report Splitter — Detailed Catalogue Reports
===============================================================================

Reads the existing audit JSON.

Creates:
    01_destinations.json
    02_signature_moments.json
    03_experience_tags.json
    04_accessibility_profiles.json
    05_conservation_stories.json
    06_cancellation_policies.json
    07_experience_categories.json
    08_difficulty_values.json
    09_nairobi_experience_core.json
    10_nairobi_experience_operations.json
    11_nairobi_experience_media_and_associations.json

READ-ONLY:
No database connection.
No database changes.
No modification of the original audit report.
===============================================================================
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    PROJECT_ROOT
    / "instance"
    / "reusable_catalogue_and_nairobi_experience_audit.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "instance"
    / "tur_audit_reports"
)

# ---------------------------------------------------------------------------
# Catalogue definitions
# ---------------------------------------------------------------------------
CATALOGUE_REPORTS = {
    "01_destinations.json": "destinations",
    "02_signature_moments.json": "signature_moments",
    "03_experience_tags.json": "experience_tags",
    "04_accessibility_profiles.json": "accessibility_profiles",
    "05_conservation_stories.json": "conservation_stories",
    "06_cancellation_policies.json": "cancellation_policies",
    "07_experience_categories.json": "experience_categories",}

OPERATIONAL_RELATIONSHIPS = {
    "pricing",
    "itinerary",
    "inclusions",
    "exclusions",
    "highlights",
    "addons",
    "packing_items",
    "safety_rules",
    "requirements",
    "faqs",
    "schedules",
    "reviews",
    "testimonials",
    "bookings",}

MEDIA_AND_ASSOCIATION_RELATIONSHIPS = {
    "media",
    "hero_media",
    "gallery_media",
    "thumbnail_media",
    "tags",
    "signature_moments",
    "wildlife",
    "photography_spots",
    "conservation_story",
    "cancellation_policy",
    "accessibility_profile",
    "category",
    "destination",}

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(filename, data):
    output_file = OUTPUT_DIR / filename

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    size_kb = output_file.stat().st_size / 1024

    print(
        f"Created: {filename} "
        f"({size_kb:.2f} KB)"
    )


def extract_direct_fields(record):
    """
    Keep the catalogue record's own fields.

    Exclude nested relationships so that one catalogue report
    does not unnecessarily contain records from other catalogues.
    """

    if not isinstance(record, dict):
        return record

    return {
        key: value
        for key, value in record.items()
        if not isinstance(value, (dict, list))
    }


# ---------------------------------------------------------------------------
# 01–07. Separate reusable catalogue reports
# ---------------------------------------------------------------------------

def split_catalogues(report):

    catalogues = report.get("catalogues", {})

    print("\nREUSABLE CATALOGUES")
    print("-" * 75)

    for filename, catalogue_key in CATALOGUE_REPORTS.items():

        catalogue = catalogues.get(catalogue_key, {})

        if catalogue.get("status") != "FOUND":
            output = {
                "catalogue": catalogue_key,
                "status": catalogue.get(
                    "status",
                    "NOT_PRESENT_IN_SOURCE_REPORT",
                ),
                "details": catalogue,
            }

        else:
            records = catalogue.get("records", [])

            output = {
                "catalogue": catalogue_key,
                "status": "FOUND",
                "model": catalogue.get("model"),
                "table": catalogue.get("table"),
                "total_records": catalogue.get(
                    "total_records",
                    len(records),
                ),
                "records": [
                    extract_direct_fields(record)
                    for record in records
                ],
            }

        write_json(filename, output)


# ---------------------------------------------------------------------------
# 08. Difficulty values
# ---------------------------------------------------------------------------

def split_difficulty_values(report):

    values = report.get("difficulty_values", [])

    write_json(
        "08_difficulty_values.json",
        {
            "catalogue": "experience_difficulty",
            "total_values": len(values),
            "values": values,
        },
    )


# ---------------------------------------------------------------------------
# 09–11. Nairobi National Park reports
# ---------------------------------------------------------------------------

def split_nairobi_experience(report):

    nairobi_data = report.get(
        "nairobi_national_park",
        {},
    )

    experience = nairobi_data.get("experience", {})

    if nairobi_data.get("status") != "FOUND":
        experience = {}

    relationship_keys = (
        OPERATIONAL_RELATIONSHIPS
        | MEDIA_AND_ASSOCIATION_RELATIONSHIPS
    )

    # 09. Core experience details.
    core_details = {
        key: value
        for key, value in experience.items()
        if key not in relationship_keys
    }

    write_json(
        "09_nairobi_experience_core.json",
        {
            "status": nairobi_data.get("status"),
            "experience": core_details,
        },
    )

    # 10. Operational details.
    operational_details = {
        key: value
        for key, value in experience.items()
        if key in OPERATIONAL_RELATIONSHIPS
    }

    write_json(
        "10_nairobi_experience_operations.json",
        {
            "experience_code": experience.get("experience_code"),
            "experience_title": experience.get("title"),
            "relationships": operational_details,
        },
    )

    # 11. Media and reusable associations.
    association_details = {
        key: value
        for key, value in experience.items()
        if key in MEDIA_AND_ASSOCIATION_RELATIONSHIPS
    }

    write_json(
        "11_nairobi_experience_media_and_associations.json",
        {
            "experience_code": experience.get("experience_code"),
            "experience_title": experience.get("title"),
            "relationships": association_details,
        },
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"\nOriginal audit report not found:\n{SOURCE_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = read_json(SOURCE_FILE)

    print("\n" + "=" * 75)
    print("THE UNCHARTED ROUTE — AUDIT REPORT SPLITTER")
    print("=" * 75)

    split_catalogues(report)
    split_difficulty_values(report)
    split_nairobi_experience(report)

    print("\n" + "=" * 75)
    print("ALL 11 REPORTS GENERATED")
    print("=" * 75)

    print(f"\nOutput directory:\n{OUTPUT_DIR}")

    print("\nOriginal audit JSON remains unchanged.")
    print("No database records were modified.")

    print("=" * 75)


if __name__ == "__main__":
    main()
