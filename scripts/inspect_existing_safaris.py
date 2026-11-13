"""
THE UNCHARTED ROUTE
Existing Safari Catalogue Inspector

READ-ONLY INSPECTION SCRIPT.

Inspects the existing Safari catalogue and prints the relationships
between Safari destinations, properties, media, package options,
itinerary days, package rates and inquiries.

Explicitly excluded:
    - SafariBooking

Usage:
    python scripts/inspect_existing_safaris.py

This script does NOT:
    - create records
    - update records
    - delete records
    - commit transactions
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import inspect as sa_inspect


# -------------------------------------------------------------------------------------------------
# PROJECT PATH
# -------------------------------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------------------------------------
# TARGET MODELS
# -------------------------------------------------------------------------------------------------

TARGET_MODEL_NAMES = [
    "SafariDestination",
    "SafariProperty",
    "SafariPropertyMedia",
    "SafariPackageOption",
    "SafariItineraryDay",
    "SafariPackageRate",
    "SafariInquiry",
]

EXCLUDED_MODEL_NAMES = {
    "SafariBooking",
}


# -------------------------------------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------------------------------------

def separator(char: str = "=", length: int = 110) -> None:
    print(char * length)


def safe_value(value: Any) -> str:
    if value is None:
        return "None"

    if isinstance(value, str):
        return value

    return repr(value)


def load_all_model_modules() -> None:
    try:
        models_package = importlib.import_module("app.models")
    except Exception as exc:
        print()
        print("ERROR: Could not import app.models")
        print(f"       {type(exc).__name__}: {exc}")
        raise

    package_path = getattr(models_package, "__path__", None)

    if package_path is None:
        return

    failures = []

    for module_info in pkgutil.walk_packages(
        package_path,
        prefix=models_package.__name__ + ".",
    ):
        module_name = module_info.name

        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append((module_name, exc))

    if failures:
        print()
        print("WARNING: Some app.models modules could not be imported.")

        for module_name, exc in failures:
            print(
                f"  - {module_name}: "
                f"{type(exc).__name__}: {exc}"
            )

        print()


def get_model_class(model_name: str):
    from app import db

    for mapper in list(db.Model.registry.mappers):
        cls = mapper.class_

        if cls.__name__ == model_name:
            return cls

    return None


def get_primary_key_value(instance) -> Any:
    mapper = sa_inspect(instance.__class__)

    primary_keys = mapper.primary_key

    if not primary_keys:
        return None

    return getattr(
        instance,
        primary_keys[0].key,
        None,
    )


def print_record_columns(instance) -> None:
    mapper = sa_inspect(instance.__class__)

    values = []

    for column in mapper.columns:
        try:
            value = getattr(instance, column.key)
        except Exception as exc:
            value = f"<ERROR: {type(exc).__name__}: {exc}>"

        values.append((column.key, value))

    for key, value in values:
        print(f"      {key}: {safe_value(value)}")


def print_model_records(model_name: str) -> None:
    model_class = get_model_class(model_name)

    separator("-")
    print(f"{model_name}")

    if model_class is None:
        print("  MODEL NOT FOUND")
        return

    mapper = sa_inspect(model_class)

    print(f"  Table: {mapper.local_table.name}")

    try:
        records = (
            model_class.query
            .order_by(*mapper.primary_key)
            .all()
        )
    except Exception as exc:
        print(
            f"  ERROR querying model: "
            f"{type(exc).__name__}: {exc}"
        )
        return

    print(f"  Existing records: {len(records)}")

    if not records:
        print("  No records found.")
        return

    for index, instance in enumerate(records, start=1):
        pk = get_primary_key_value(instance)

        print()
        print(f"  [{index}/{len(records)}] Primary Key: {safe_value(pk)}")

        print_record_columns(instance)


def print_relationship_counts() -> None:
    """
    Provides a compact overview of how many records currently exist
    in each Safari table.
    """

    separator()
    print("SAFARI RECORD COUNTS")
    separator("-")

    for model_name in TARGET_MODEL_NAMES:
        model_class = get_model_class(model_name)

        if model_class is None:
            print(f"  {model_name:<28} MODEL NOT FOUND")
            continue

        try:
            count = model_class.query.count()
            print(f"  {model_name:<28} {count}")
        except Exception as exc:
            print(
                f"  {model_name:<28} "
                f"ERROR: {type(exc).__name__}: {exc}"
            )

    print()


def print_destination_property_tree() -> None:
    """
    Print the SafariDestination -> SafariProperty relationship if the
    models expose a normal SQLAlchemy relationship.

    This does not assume the relationship attribute name. It discovers
    relationships from SQLAlchemy mapper metadata.
    """

    destination_class = get_model_class("SafariDestination")
    property_class = get_model_class("SafariProperty")

    if destination_class is None or property_class is None:
        return

    destination_mapper = sa_inspect(destination_class)

    property_relationships = []

    for relationship in destination_mapper.relationships:
        if relationship.mapper.class_ is property_class:
            property_relationships.append(relationship)

    if not property_relationships:
        return

    separator()
    print("SAFARI DESTINATION → PROPERTY STRUCTURE")
    separator("-")

    try:
        destinations = (
            destination_class.query
            .order_by(*destination_mapper.primary_key)
            .all()
        )
    except Exception as exc:
        print(
            f"ERROR loading destinations: "
            f"{type(exc).__name__}: {exc}"
        )
        return

    if not destinations:
        print("No Safari destinations found.")
        return

    for destination in destinations:
        destination_pk = get_primary_key_value(destination)

        print()
        print(
            f"Destination "
            f"[{safe_value(destination_pk)}]"
        )

        print_record_columns(destination)

        for relationship in property_relationships:
            try:
                related = getattr(destination, relationship.key)
            except Exception as exc:
                print(
                    f"  Relationship '{relationship.key}' "
                    f"could not be loaded: "
                    f"{type(exc).__name__}: {exc}"
                )
                continue

            if related is None:
                print(f"  {relationship.key}: None")
                continue

            if not relationship.uselist:
                related = [related]

            print(
                f"  {relationship.key}: "
                f"{len(related)} record(s)"
            )

            for property_record in related:
                property_pk = get_primary_key_value(property_record)

                print(
                    f"    - Property PK: "
                    f"{safe_value(property_pk)}"
                )

                print_record_columns(property_record)


def print_package_relationship_tree() -> None:
    """
    Discover and print package option relationships to itinerary days
    and package rates without hard-coding relationship attribute names.
    """

    package_class = get_model_class("SafariPackageOption")
    itinerary_class = get_model_class("SafariItineraryDay")
    rate_class = get_model_class("SafariPackageRate")

    if package_class is None:
        return

    package_mapper = sa_inspect(package_class)

    separator()
    print("SAFARI PACKAGE STRUCTURE")
    separator("-")

    packages = (
        package_class.query
        .order_by(*package_mapper.primary_key)
        .all()
    )

    if not packages:
        print("No Safari package options found.")
        return

    for package in packages:
        package_pk = get_primary_key_value(package)

        print()
        print(
            f"Package Option "
            f"[{safe_value(package_pk)}]"
        )

        print_record_columns(package)

        for relationship in package_mapper.relationships:
            target_class = relationship.mapper.class_

            if target_class not in {
                itinerary_class,
                rate_class,
            }:
                continue

            try:
                related = getattr(package, relationship.key)
            except Exception as exc:
                print(
                    f"  Relationship '{relationship.key}' "
                    f"ERROR: {type(exc).__name__}: {exc}"
                )
                continue

            if related is None:
                print(f"  {relationship.key}: None")
                continue

            if not relationship.uselist:
                related = [related]

            print()
            print(
                f"  {relationship.key} "
                f"({target_class.__name__}): "
                f"{len(related)} record(s)"
            )

            for child in related:
                child_pk = get_primary_key_value(child)

                print(
                    f"    - "
                    f"{target_class.__name__} "
                    f"PK={safe_value(child_pk)}"
                )

                print_record_columns(child)


# -------------------------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------------------------

def main() -> int:
    separator()
    print("THE UNCHARTED ROUTE — EXISTING SAFARI INSPECTION")
    separator()

    print("Mode: READ ONLY")
    print()

    print("Included:")
    for model_name in TARGET_MODEL_NAMES:
        print(f"  - {model_name}")

    print()
    print("Explicitly excluded:")
    for model_name in sorted(EXCLUDED_MODEL_NAMES):
        print(f"  - {model_name}")

    print()
    print("Loading application...")

    try:
        from app import create_app
    except Exception as exc:
        print()
        print("ERROR: Could not import create_app from app.")
        print(f"       {type(exc).__name__}: {exc}")
        return 1

    try:
        app = create_app()
    except Exception as exc:
        print()
        print("ERROR: Application factory failed.")
        print(f"       {type(exc).__name__}: {exc}")
        return 1

    with app.app_context():
        print("Application loaded.")
        print()

        print("Loading model modules...")
        load_all_model_modules()
        print("Model modules loaded.")
        print()

        print_relationship_counts()

        separator()
        print("EXISTING SAFARI MODEL RECORDS")
        separator()

        for model_name in TARGET_MODEL_NAMES:
            print_model_records(model_name)
            print()

        print_destination_property_tree()
        print_package_relationship_tree()

    separator()
    print("EXISTING SAFARI INSPECTION COMPLETE")
    separator()

    print()
    print("No database records were created, modified, deleted, or committed.")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())