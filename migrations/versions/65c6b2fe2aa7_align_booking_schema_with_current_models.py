"""
Align booking schema with current SQLAlchemy models.
Revision ID: align_booking_schema_20261101
Revises: e3ffac21080c
Rebuilds the booking-related SQLite tables using current model metadata.
Preserves existing records, model-defined indexes, unique constraints,
check constraints and foreign-key relationships.
The migration intentionally removes obsolete duplicate foreign keys
and the redundant bookings.booking_uuid unique constraint.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.sql import quoted_name

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision = "align_booking_schema_20261101"
down_revision = "e3ffac21080c"

branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Tables to rebuild
# ---------------------------------------------------------------------------
TARGET_TABLES = (
    "booking_requests",
    "bookings",
    "booking_documents",
    "booking_notes",
    "booking_payments",
    "booking_travellers",
    "staff",
    "destination_bookings",
    "safari_bookings",
    "stay_bookings",
    "booking_addons",)
SHADOW_PREFIX = "__tur_schema_fix_"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _quote(connection, identifier):
    """Safely quote a SQLite identifier."""
    return connection.dialect.identifier_preparer.quote(identifier)

def _get_model_metadata():
    """
    Obtain the metadata supplied to Alembic by Flask-Migrate.

    This is the authoritative source for the replacement schemas.
    """
    metadata = op.get_context().opts.get("target_metadata")

    if metadata is None:
        raise RuntimeError(
            "Alembic target_metadata is unavailable. "
            "Check migrations/env.py.")
    return metadata

def _get_tables(metadata):
    """Resolve all target SQLAlchemy tables."""
    tables = {}

    for name in TARGET_TABLES:
        table = metadata.tables.get(name)

        if table is None:
            raise RuntimeError(
                f"SQLAlchemy metadata does not contain table: {name}")
        tables[name] = table
    return tables

def _validate_environment(connection):
    """Ensure the migration runs under the required SQLite settings."""
    if connection.dialect.name != "sqlite":
        raise RuntimeError(
            "This migration is designed specifically for SQLite.")

    foreign_keys = connection.exec_driver_sql(
        "PRAGMA foreign_keys"
    ).scalar()

    if foreign_keys != 0:
        raise RuntimeError(
            "SQLite foreign-key enforcement must be disabled before "
            "the migration transaction begins. Check migrations/env.py."
        )

    legacy_alter_table = connection.exec_driver_sql(
        "PRAGMA legacy_alter_table"
    ).scalar()

    if legacy_alter_table != 1:
        raise RuntimeError(
            "PRAGMA legacy_alter_table must be ON during this migration."
        )


def _validate_existing_tables(connection, tables):
    """
    Check that the existing database has exactly the model columns.

    This prevents accidental data loss if the database has drifted
    beyond the differences already investigated.
    """
    inspector = sa.inspect(connection)

    for name, model_table in tables.items():

        if not inspector.has_table(name):
            raise RuntimeError(
                f"Required existing table is missing: {name}"
            )

        database_columns = {
            column["name"]
            for column in inspector.get_columns(name)
        }

        model_columns = {
            column.name
            for column in model_table.columns
        }

        if database_columns != model_columns:
            missing = sorted(model_columns - database_columns)
            extra = sorted(database_columns - model_columns)

            raise RuntimeError(
                f"Column mismatch in {name}. "
                f"Missing from database: {missing}. "
                f"Extra in database: {extra}. "
                "Migration stopped to protect existing data."
            )


def _get_record_counts(connection):
    """Capture record counts before rebuilding."""
    counts = {}

    for name in TARGET_TABLES:
        counts[name] = connection.exec_driver_sql(
            f"SELECT COUNT(*) FROM {_quote(connection, name)}"
        ).scalar_one()

    return counts



def _create_shadow_tables(connection, tables):
    """
    Create replacement tables using current SQLAlchemy metadata.

    Correct self-referencing foreign keys so they point to the
    final table name rather than the temporary shadow name.
    """
    shadow_tables = {}
    metadata = _get_model_metadata()

    for name, model_table in tables.items():
        shadow_name = f"{SHADOW_PREFIX}{name}"

        shadow_table = model_table.to_metadata(
            metadata,
            name=shadow_name,
        )

        # -----------------------------------------------------------
        # Correct self-referencing foreign keys.
        # -----------------------------------------------------------
        for constraint in list(shadow_table.foreign_key_constraints):

            elements = list(constraint.elements)

            if not elements:
                continue

            # Identify foreign keys that incorrectly point to
            # this temporary shadow table.
            self_referencing = [
                element
                for element in elements
                if element.column.table.name == shadow_name
            ]

            if not self_referencing:
                continue

            # Preserve the original constraint configuration.
            local_columns = [
                element.parent.name
                for element in elements
            ]

            remote_columns = [
                (
                    f"{name}.{element.column.name}"
                    if element.column.table.name == shadow_name
                    else element.target_fullname
                )
                for element in elements
            ]

            replacement = sa.ForeignKeyConstraint(
                local_columns,
                remote_columns,
                name=constraint.name,
                onupdate=constraint.onupdate,
                ondelete=constraint.ondelete,
                deferrable=constraint.deferrable,
                initially=constraint.initially,
                match=constraint.match,
                use_alter=constraint.use_alter,
            )

            # Replace the incorrectly redirected constraint.
            shadow_table.constraints.remove(constraint)
            shadow_table.append_constraint(replacement)

        shadow_tables[name] = shadow_table

    # Create all replacement tables after correcting their FKs.
    for name, shadow_table in shadow_tables.items():

        ddl = CreateTable(shadow_table).compile(
            dialect=connection.dialect)
        connection.exec_driver_sql(str(ddl))

    return shadow_tables

def _copy_existing_records(connection, tables, shadow_tables):
    """Copy every existing column and record into its replacement table."""

    for name, model_table in tables.items():
        shadow_name = shadow_tables[name].name
        columns = [
            column.name
            for column in model_table.columns]

        column_list = ", ".join(
            _quote(connection, column)
            for column in columns
        )

        original_name = _quote(connection, name)
        shadow_name_quoted = _quote(connection, shadow_name)

        connection.exec_driver_sql(
            f"""
            INSERT INTO {shadow_name_quoted} ({column_list})
            SELECT {column_list}
            FROM {original_name}
            """)

def _replace_original_tables(connection, shadow_tables):
    """
    Replace original tables with their metadata-based equivalents.

    All records have already been copied before this operation begins.
    """
    for name in TARGET_TABLES:
        connection.exec_driver_sql(
            f"DROP TABLE {_quote(connection, name)}")

    for name in TARGET_TABLES:
        shadow_name = shadow_tables[name].name
        connection.exec_driver_sql(
            f"""
            ALTER TABLE {_quote(connection, shadow_name)}
            RENAME TO {_quote(connection, name)}
            """)

def _recreate_model_indexes(connection, tables):
    """
    Recreate explicit indexes defined by current SQLAlchemy models.

    Unique constraints and check constraints are already included
    in the replacement CREATE TABLE statements.
    """
    for name, model_table in tables.items():

        for index in sorted(
            model_table.indexes,
            key=lambda item: item.name or "",
        ):

            if not index.name:
                raise RuntimeError(
                    f"Unnamed index found on model table {name}."
                )

            ddl = CreateIndex(index).compile(
                dialect=connection.dialect
            )

            connection.exec_driver_sql(str(ddl))


def _verify_record_counts(connection, before):
    """Ensure every target table retains its original record count."""

    after = _get_record_counts(connection)

    for name in TARGET_TABLES:

        if before[name] != after[name]:
            raise RuntimeError(
                f"Record count mismatch in {name}: "
                f"before={before[name]}, after={after[name]}.")
    return after

def _verify_foreign_keys(connection):
    """
    Check SQLite foreign-key consistency after rebuilding.

    This checks all tables, including external dependent tables.
    """
    violations = connection.exec_driver_sql(
        "PRAGMA foreign_key_check"
    ).fetchall()
    if violations:
        raise RuntimeError(
            "Foreign-key violations detected after rebuilding: "
            f"{violations}")


def _verify_foreign_key_targets(connection):
    """
    Ensure no foreign key references a temporary shadow table.
    """
    for name in TARGET_TABLES:

        rows = connection.exec_driver_sql(
            f"PRAGMA foreign_key_list({_quote(connection, name)})"
        ).mappings().all()

        for row in rows:
            referenced_table = row["table"]

            if referenced_table.startswith(SHADOW_PREFIX):
                raise RuntimeError(
                    f"Invalid foreign-key target in {name}: "
                    f"{row['from']} references {referenced_table}."
                )

            if referenced_table == name:
                print(
                    f"Verified self-reference: "
                    f"{name}.{row['from']} -> "
                    f"{referenced_table}.{row['to']}"
                )


def _verify_indexes(connection, tables):
    """Verify all model-defined indexes exist after rebuilding."""
    inspector = sa.inspect(connection)
    for name, model_table in tables.items():
        existing_indexes = {
            index["name"]
            for index in inspector.get_indexes(name)}

        for model_index in model_table.indexes:
            if model_index.name not in existing_indexes:
                raise RuntimeError(
                    f"Expected index {model_index.name} "
                    f"is missing from {name}.")

# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------
def upgrade():

    connection = op.get_bind()
    _validate_environment(connection)
    metadata = _get_model_metadata()
    tables = _get_tables(metadata)

    # Verify that no unexpected column changes have occurred.
    _validate_existing_tables(connection, tables)

    # Prevent overwriting leftovers from an earlier failed attempt.
    for name in TARGET_TABLES:

        shadow_name = f"{SHADOW_PREFIX}{name}"
        result = connection.exec_driver_sql(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (shadow_name,),
        ).first()

        if result:
            raise RuntimeError(
                f"Temporary table {shadow_name} already exists. "
                "Inspect the database before continuing."
            )

    # Capture existing records before any schema changes.
    original_counts = _get_record_counts(connection)

    # ---------------------------------------------------------------
    # 1. Create all replacement tables.
    # ---------------------------------------------------------------
    shadow_tables = _create_shadow_tables(
        connection,
        tables,)

    # ---------------------------------------------------------------
    # 2. Copy all existing records.
    # ---------------------------------------------------------------
    _copy_existing_records(
        connection,
        tables,
        shadow_tables,)

    # ---------------------------------------------------------------
    # 3. Replace original tables.
    # ---------------------------------------------------------------
    _replace_original_tables(
        connection,
        shadow_tables,)

    # ---------------------------------------------------------------
    # 4. Restore model-defined indexes.
    # ---------------------------------------------------------------
    _recreate_model_indexes(
        connection,
        tables,)

    # ---------------------------------------------------------------
    # 5. Verify record preservation.
    # ---------------------------------------------------------------
    final_counts = _verify_record_counts(
        connection,
        original_counts,)

    # ---------------------------------------------------------------
    # 6. Verify indexes and foreign-key consistency.
    # ---------------------------------------------------------------
    _verify_indexes(
        connection,
        tables,)

    _verify_foreign_keys(connection)
    _verify_foreign_key_targets(connection)

    print("\nBooking schema alignment completed.")
    for name in TARGET_TABLES:
        print(
            f"  {name}: "
            f"{original_counts[name]} -> {final_counts[name]}")

# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------
def downgrade():
    raise RuntimeError(
        "This schema-alignment migration is intentionally irreversible. "
        "To roll back, restore the database backup created before "
        "the migration.")