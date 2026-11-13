from __future__ import annotations

import os
import sys

# =============================================================================
# Project bootstrap
# =============================================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import inspect, select, func, and_

from app import create_app
from extensions import db


# =============================================================================
# Helpers
# =============================================================================

def print_section(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def table_exists(inspector, table_name):
    return table_name in inspector.get_table_names()


def get_sqlite_foreign_keys(connection, table_name):
    """
    Return SQLite's authoritative foreign-key metadata for a table.

    PRAGMA foreign_key_list() returns:

        0 = id
        1 = seq
        2 = referenced table
        3 = local/constrained column
        4 = referenced column
        5 = on update
        6 = on delete
        7 = match

    SQLAlchemy's SQLite inspector can sometimes omit the ON DELETE action
    even when the actual SQLite schema contains it. This helper therefore
    reads the database directly through SQLite's PRAGMA.
    """
    result = connection.exec_driver_sql(
        f"PRAGMA foreign_key_list('{table_name}')"
    )

    return [
        {
            "id": row[0],
            "seq": row[1],
            "referred_table": row[2],
            "constrained_column": row[3],
            "referred_column": row[4],
            "onupdate": row[5],
            "ondelete": row[6],
        }
        for row in result.fetchall()
    ]


def find_sqlite_fk(
    sqlite_fks,
    constrained_columns,
    referred_table,
    referred_columns,
):
    """
    Find the matching SQLite PRAGMA FK for an SQLAlchemy-inspected FK.
    """
    if len(constrained_columns) != 1:
        return None

    if len(referred_columns) != 1:
        return None

    constrained_column = constrained_columns[0]
    referred_column = referred_columns[0]

    for fk in sqlite_fks:
        if (
            fk["constrained_column"] == constrained_column
            and fk["referred_table"] == referred_table
            and fk["referred_column"] == referred_column
        ):
            return fk

    return None


# =============================================================================
# Main
# =============================================================================

def main():
    app = create_app()

    with app.app_context():

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # ---------------------------------------------------------------------
        # Open a SQLAlchemy connection for direct SQLite PRAGMA inspection.
        # ---------------------------------------------------------------------

        with db.engine.connect() as connection:

            # -----------------------------------------------------------------
            # Staff-related tables
            # -----------------------------------------------------------------

            print_section("STAFF-RELATED TABLES")

            staff_tables = sorted(
                table
                for table in tables
                if "staff" in table.lower()
            )

            if staff_tables:
                for table in staff_tables:
                    print(f"  [FOUND] {table}")
            else:
                print("  No staff-related tables found.")

            # -----------------------------------------------------------------
            # Row counts
            # -----------------------------------------------------------------

            print_section("STAFF TABLE ROW COUNTS")

            for table_name in staff_tables:
                table = db.metadata.tables.get(table_name)

                if table is None:
                    try:
                        table = db.Table(
                            table_name,
                            db.metadata,
                            autoload_with=db.engine,
                        )
                    except Exception as exc:
                        print(
                            f"  [ERROR] Could not reflect {table_name}: {exc}"
                        )
                        continue

                try:
                    count = db.session.execute(
                        select(func.count()).select_from(table)
                    ).scalar_one()

                    print(f"  {table_name}: {count}")

                except Exception as exc:
                    print(
                        f"  [ERROR] Could not count {table_name}: {exc}"
                    )

            # -----------------------------------------------------------------
            # Foreign keys
            # -----------------------------------------------------------------

            print_section("STAFF-RELATED FOREIGN KEYS")

            found_fk = False

            for table_name in staff_tables:

                foreign_keys = inspector.get_foreign_keys(table_name)

                if not foreign_keys:
                    continue

                found_fk = True

                sqlite_fks = get_sqlite_foreign_keys(
                    connection,
                    table_name,
                )

                print()
                print(f"TABLE: {table_name}")

                for fk in foreign_keys:

                    constrained_columns = (
                        fk.get("constrained_columns") or []
                    )

                    referred_table = fk.get("referred_table")

                    referred_columns = (
                        fk.get("referred_columns") or []
                    )

                    sqlite_fk = find_sqlite_fk(
                        sqlite_fks,
                        constrained_columns,
                        referred_table,
                        referred_columns,
                    )

                    print(
                        f"  {fk.get('name') or '[unnamed FK]'}"
                    )

                    print(
                        f"    columns: "
                        f"{', '.join(constrained_columns)}"
                    )

                    print(
                        f"    references: "
                        f"{referred_table}"
                        f"("
                        f"{', '.join(referred_columns)}"
                        f")"
                    )

                    if sqlite_fk:
                        print(
                            f"    ondelete: "
                            f"{sqlite_fk['ondelete']}"
                        )
                    else:
                        print(
                            "    ondelete: "
                            "[NOT FOUND IN SQLITE PRAGMA]"
                        )

            if not found_fk:
                print(
                    "  No foreign keys found on staff-related tables."
                )

            # -----------------------------------------------------------------
            # Tables elsewhere that reference Staff
            # -----------------------------------------------------------------

            print_section("OTHER TABLES REFERENCING STAFF")

            found_staff_reference = False

            for table_name in tables:

                foreign_keys = inspector.get_foreign_keys(table_name)

                for fk in foreign_keys:

                    if fk.get("referred_table") != "staff":
                        continue

                    found_staff_reference = True

                    constrained_columns = (
                        fk.get("constrained_columns") or []
                    )

                    referred_columns = (
                        fk.get("referred_columns") or []
                    )

                    sqlite_fks = get_sqlite_foreign_keys(
                        connection,
                        table_name,
                    )

                    sqlite_fk = find_sqlite_fk(
                        sqlite_fks,
                        constrained_columns,
                        "staff",
                        referred_columns,
                    )

                    print()
                    print(f"TABLE: {table_name}")

                    print(
                        f"  FK: "
                        f"{fk.get('name') or '[unnamed FK]'}"
                    )

                    print(
                        f"  columns: "
                        f"{', '.join(constrained_columns)}"
                    )

                    print(
                        f"  references: staff("
                        f"{', '.join(referred_columns)}"
                        f")"
                    )

                    if sqlite_fk:
                        print(
                            f"  ondelete: "
                            f"{sqlite_fk['ondelete']}"
                        )
                    else:
                        print(
                            "  ondelete: "
                            "[NOT FOUND IN SQLITE PRAGMA]"
                        )

            if not found_staff_reference:
                print(
                    "  No other tables currently reference staff."
                )

            # -----------------------------------------------------------------
            # Orphan checks
            #
            # Generic check for simple single-column foreign keys.
            # -----------------------------------------------------------------

            print_section("ORPHANED STAFF FOREIGN KEY CHECKS")

            orphan_found = False

            for table_name in tables:

                foreign_keys = inspector.get_foreign_keys(table_name)

                for fk in foreign_keys:

                    constrained_columns = (
                        fk.get("constrained_columns") or []
                    )

                    referred_table_name = fk.get("referred_table")

                    referred_columns = (
                        fk.get("referred_columns") or []
                    )

                    # We deliberately handle simple FKs here.
                    if len(constrained_columns) != 1:
                        continue

                    if len(referred_columns) != 1:
                        continue

                    if not referred_table_name:
                        continue

                    child_column_name = constrained_columns[0]
                    parent_column_name = referred_columns[0]

                    # Only focus on Staff-related relationships.
                    is_staff_related = (
                        "staff" in table_name.lower()
                        or "staff" in referred_table_name.lower()
                    )

                    if not is_staff_related:
                        continue

                    if (
                        table_name not in tables
                        or referred_table_name not in tables
                    ):
                        continue

                    try:
                        child_table = db.Table(
                            table_name,
                            db.metadata,
                            autoload_with=db.engine,
                        )

                        parent_table = db.Table(
                            referred_table_name,
                            db.metadata,
                            autoload_with=db.engine,
                        )

                        child_column = child_table.c[
                            child_column_name
                        ]

                        parent_column = parent_table.c[
                            parent_column_name
                        ]

                        # Ignore nullable FK values.
                        orphan_query = select(
                            func.count()
                        ).select_from(
                            child_table
                        ).where(
                            and_(
                                child_column.is_not(None),
                                ~select(parent_column)
                                .where(
                                    parent_column == child_column
                                )
                                .exists(),
                            )
                        )

                        orphan_count = db.session.execute(
                            orphan_query
                        ).scalar_one()

                        if orphan_count:
                            orphan_found = True

                            print()
                            print(
                                f"  [ORPHAN] "
                                f"{table_name}.{child_column_name}"
                            )

                            print(
                                f"           -> "
                                f"{referred_table_name}."
                                f"{parent_column_name}"
                            )

                            print(
                                f"           orphaned rows: "
                                f"{orphan_count}"
                            )

                        else:
                            print(
                                f"  [OK] "
                                f"{table_name}.{child_column_name}"
                                f" -> "
                                f"{referred_table_name}."
                                f"{parent_column_name}"
                            )

                    except Exception as exc:
                        print()
                        print(
                            f"  [ERROR] Could not check "
                            f"{table_name}.{child_column_name}"
                        )
                        print(f"          {exc}")

            if not orphan_found:
                print()
                print(
                    "  No orphaned Staff-related foreign keys detected."
                )

            # -----------------------------------------------------------------
            # Important staff tables and expected presence
            # -----------------------------------------------------------------

            print_section("EXPECTED STAFF TABLES")

            expected_tables = [
                "staff",
                "staff_availability",
                "staff_schedules",
                "staff_assignments",
            ]

            for table_name in expected_tables:
                if table_name in tables:
                    print(f"  [OK]      {table_name}")
                else:
                    print(f"  [MISSING] {table_name}")

            # -----------------------------------------------------------------
            # Database dialect
            # -----------------------------------------------------------------

            print_section("DATABASE")

            print(f"  Dialect: {db.engine.dialect.name}")
            print(f"  URL:     {db.engine.url}")

            # -----------------------------------------------------------------
            # Complete migration state
            # -----------------------------------------------------------------

            print_section("AUDIT COMPLETE")

            print(
                "This script is READ-ONLY. "
                "No database rows or schema were changed."
            )


if __name__ == "__main__":
    main()