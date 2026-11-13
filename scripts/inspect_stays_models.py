"""
===============================================================================
THE UNCHARTED ROUTE
STAYS MODEL INSPECTOR
===============================================================================

Purpose
-------
Inspect the current Stay-related SQLAlchemy models before catalogue population.

This script DOES NOT:
    - create records
    - update records
    - delete records
    - modify migrations
    - modify media
    - modify bookings

It reports:
    - Stay-related model classes
    - database tables
    - columns
    - nullability
    - defaults
    - foreign keys
    - relationships
    - existing database row counts

Run:
    python scripts/inspect_stays_models.py
===============================================================================
"""

from __future__ import annotations
import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect as sqlalchemy_inspect
from app import create_app
from extensions import db

# =============================================================================
# Stay-related model modules/classes
# =============================================================================

MODEL_IMPORTS = [
    ("app.models.stay", "Stay"),
    ("app.models.stay_room", "StayRoom"),
    ("app.models.stay_media", "StayMedia"),
    ("app.models.stay_amenity", "StayAmenity"),
    ("app.models.stay_room_media", "StayRoomMedia"),
    ("app.models.stay_room_amenity", "StayRoomAmenity"),
    ("app.models.stay_availability", "StayAvailability"),
    ("app.models.stay_review", "StayReview"),
    ("app.models.stay_booking", "StayBooking"),
]


def import_model(module_name, class_name):
    module = __import__(
        module_name,
        fromlist=[class_name],
    )
    return getattr(module, class_name)


def print_separator(char="-", width=110):
    print(char * width)


def print_model(model):
    mapper = sqlalchemy_inspect(model)
    table = mapper.local_table

    print()
    print("=" * 110)
    print(f"MODEL: {model.__name__}")
    print(f"TABLE: {table.name}")
    print("=" * 110)

    print()
    print("COLUMNS")
    print("-" * 110)

    for column in table.columns:
        nullable = "NULL" if column.nullable else "NOT NULL"

        default = column.default
        server_default = column.server_default

        if default is not None:
            default_text = str(default.arg)
        elif server_default is not None:
            default_text = str(server_default.arg)
        else:
            default_text = "-"

        foreign_keys = []

        for fk in column.foreign_keys:
            foreign_keys.append(
                f"{fk.target_fullname}"
            )

        fk_text = ", ".join(foreign_keys) if foreign_keys else "-"

        print(
            f"{column.name:<35}"
            f"{str(column.type):<30}"
            f"{nullable:<10}"
            f"default={default_text:<25}"
            f"FK={fk_text}"
        )

    print()
    print("RELATIONSHIPS")
    print("-" * 110)

    relationships = mapper.relationships

    if not relationships:
        print("  None")
    else:
        for relationship in relationships:
            target = relationship.mapper.class_.__name__

            print(
                f"  {relationship.key:<30}"
                f"-> {target:<30}"
                f"uselist={relationship.uselist}"
                f"  lazy={relationship.lazy}"
            )

    print()
    print("DATABASE COUNT")

    try:
        count = model.query.count()
        print(f"  Existing rows: {count}")
    except Exception as exc:
        print(f"  COUNT FAILED: {exc}")

    print()


def print_db_tables():
    inspector = sqlalchemy_inspect(db.engine)

    print()
    print("=" * 110)
    print("DATABASE TABLES RELEVANT TO STAYS")
    print("=" * 110)

    tables = inspector.get_table_names()

    stay_tables = [
        table
        for table in tables
        if "stay" in table.lower()
    ]

    if not stay_tables:
        print("No tables containing 'stay' were found.")
        return

    for table in sorted(stay_tables):
        print(f"  {table}")


def main():
    app = create_app()

    with app.app_context():
        print()
        print("=" * 110)
        print("THE UNCHARTED ROUTE — STAYS MODEL INSPECTION")
        print("=" * 110)
        print("Mode: READ ONLY")
        print("Database changes: NONE")
        print("=" * 110)

        print_db_tables()

        print()
        print("=" * 110)
        print("MODEL DEFINITIONS")
        print("=" * 110)

        imported_models = []

        for module_name, class_name in MODEL_IMPORTS:
            try:
                model = import_model(
                    module_name,
                    class_name,
                )

                imported_models.append(model)

                print(
                    f"\n[OK] {module_name}.{class_name}"
                )

            except Exception as exc:
                print(
                    f"\n[ERROR] Could not import "
                    f"{module_name}.{class_name}"
                )
                print(f"        {type(exc).__name__}: {exc}")

        for model in imported_models:
            print_model(model)

        print()
        print("=" * 110)
        print("STAYS MODEL INSPECTION COMPLETE")
        print("=" * 110)
        print("No database changes were made.")
        print()


if __name__ == "__main__":
    main()