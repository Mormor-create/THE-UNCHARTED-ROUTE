"""
THE UNCHARTED ROUTE
Safari Model Schema Inspector

READ-ONLY INSPECTION SCRIPT.

Inspects the Safari-related SQLAlchemy models without modifying the database.

Included:
    - SafariDestination
    - SafariProperty
    - SafariPropertyMedia
    - SafariPackageOption
    - SafariItineraryDay
    - SafariPackageRate
    - SafariInquiry

Explicitly excluded:
    - SafariBooking

Usage:
    python scripts/inspect_safari_models.py

This script does NOT:
    - create records
    - update records
    - delete records
    - commit transactions
    - modify the database
"""

from __future__ import annotations

import importlib
import inspect as pyinspect
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
    """
    Convert SQLAlchemy/default values into readable output without
    accidentally triggering database operations.
    """
    if value is None:
        return "None"

    if callable(value):
        try:
            name = getattr(value, "__name__", None)
            return f"<callable:{name or type(value).__name__}>"
        except Exception:
            return "<callable>"

    return repr(value)


def load_all_model_modules() -> None:
    """
    Import all modules under app.models so SQLAlchemy's model registry
    contains the project's mapped classes.

    This is read-only. Importing model modules should not modify the DB.
    """
    try:
        models_package = importlib.import_module("app.models")
    except Exception as exc:
        print()
        print("ERROR: Could not import app.models")
        print(f"       {type(exc).__name__}: {exc}")
        print()
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
            print(f"  - {module_name}: {type(exc).__name__}: {exc}")
        print()


def get_model_class(model_name: str):
    """
    Locate a mapped SQLAlchemy model by class name from the registry.
    """
    from app import db

    for mapper in list(db.Model.registry.mappers):
        cls = mapper.class_

        if cls.__name__ == model_name:
            return cls

    return None


def print_column_details(model_class) -> None:
    mapper = sa_inspect(model_class)

    print("  COLUMNS")
    print("  " + "-" * 104)

    for column in mapper.columns:
        nullable = "YES" if column.nullable else "NO"

        primary_key = "YES" if column.primary_key else "NO"

        default = safe_value(column.default.arg) if column.default is not None else "None"

        server_default = (
            safe_value(column.server_default.arg)
            if column.server_default is not None
            else "None"
        )

        print(f"    Name           : {column.name}")
        print(f"    Type           : {column.type}")
        print(f"    Nullable       : {nullable}")
        print(f"    Primary Key    : {primary_key}")
        print(f"    Default        : {default}")
        print(f"    Server Default : {server_default}")
        print()

    print("  RELATIONSHIPS")
    print("  " + "-" * 104)

    relationships = list(mapper.relationships)

    if not relationships:
        print("    None")
        return

    for relationship in relationships:
        target = relationship.mapper.class_.__name__

        local_columns = ", ".join(
            column.name for column in relationship.local_columns
        )

        remote_columns = ", ".join(
            column.name for column in relationship.remote_side
        )

        print(f"    Name           : {relationship.key}")
        print(f"    Target         : {target}")
        print(f"    Direction      : {relationship.direction}")
        print(f"    Local Columns  : {local_columns or 'None'}")
        print(f"    Remote Columns : {remote_columns or 'None'}")
        print(f"    Uselist        : {relationship.uselist}")
        print(f"    Cascade        : {relationship.cascade}")
        print()

    print("  FOREIGN KEYS")
    print("  " + "-" * 104)

    foreign_keys = []

    for column in mapper.columns:
        for fk in column.foreign_keys:
            foreign_keys.append(
                (
                    column.name,
                    fk.target_fullname,
                    getattr(fk.constraint, "name", None),
                )
            )

    if not foreign_keys:
        print("    None")
        return

    for local_column, target, constraint_name in foreign_keys:
        print(f"    {local_column} -> {target}")
        if constraint_name:
            print(f"      Constraint: {constraint_name}")


def print_table_constraints(model_class) -> None:
    """
    Print table-level constraints/indexes that are useful when designing
    duplicate protection for population scripts.
    """
    mapper = sa_inspect(model_class)
    table = mapper.local_table

    print()
    print("  TABLE CONSTRAINTS / INDEXES")
    print("  " + "-" * 104)

    primary_key = list(table.primary_key.columns.keys())
    print(f"    Primary Key: {primary_key}")

    unique_constraints = list(table.constraints)

    found_unique = False

    for constraint in unique_constraints:
        if constraint.__class__.__name__ == "UniqueConstraint":
            found_unique = True
            columns = [column.name for column in constraint.columns]
            print(
                f"    Unique Constraint: "
                f"{getattr(constraint, 'name', None) or '<unnamed>'} "
                f"-> {columns}"
            )

    if not found_unique:
        print("    Unique Constraints: None")

    indexes = list(table.indexes)

    if indexes:
        for index in indexes:
            columns = [column.name for column in index.columns]
            print(
                f"    Index: {index.name} "
                f"(unique={index.unique}) -> {columns}"
            )
    else:
        print("    Indexes: None")


def inspect_model(model_name: str) -> None:
    model_class = get_model_class(model_name)

    separator()
    print(f"MODEL: {model_name}")
    separator("-")

    if model_class is None:
        print(f"  ERROR: Model class '{model_name}' was not found.")
        return

    print(f"  Python class : {model_class}")
    print(f"  Module       : {model_class.__module__}")

    mapper = sa_inspect(model_class)
    print(f"  Table        : {mapper.local_table.name}")

    print()

    print_column_details(model_class)
    print_table_constraints(model_class)

    print()


# -------------------------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------------------------

def main() -> int:
    separator()
    print("THE UNCHARTED ROUTE — SAFARI MODEL INSPECTION")
    separator()

    print("Mode: READ ONLY")
    print()
    print("Models included:")
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

        for model_name in TARGET_MODEL_NAMES:
            inspect_model(model_name)

    separator()
    print("SAFARI MODEL INSPECTION COMPLETE")
    separator()

    print()
    print("No database records were created, modified, deleted, or committed.")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())