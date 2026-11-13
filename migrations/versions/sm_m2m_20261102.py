"""Convert Signature Moments to reusable many-to-many assignments.

Revision ID: sm_m2m_20261102
Revises: align_booking_schema_20261101

Preserves all existing Signature Moment records and their current
Experience assignments while introducing reusable many-to-many
relationships.
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision = "sm_m2m_20261102"
down_revision = "align_booking_schema_20261101"

branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ASSOCIATION_TABLE = "signature_moment_experiences"

FK_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",}

# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------
def upgrade():
    connection = op.get_bind()

    if connection.dialect.name != "sqlite":
        raise RuntimeError(
            "This migration currently supports SQLite only."
        )

    inspector = sa.inspect(connection)

    if not inspector.has_table("signature_moments"):
        raise RuntimeError(
            "Required table signature_moments does not exist."
        )

    if not inspector.has_table("experiences"):
        raise RuntimeError(
            "Required table experiences does not exist."
        )

    if inspector.has_table(ASSOCIATION_TABLE):
        raise RuntimeError(
            f"{ASSOCIATION_TABLE} already exists. "
            "Inspect the database before continuing."
        )

    columns = {
        column["name"]
        for column in inspector.get_columns("signature_moments")
    }

    if "experience_id" not in columns:
        raise RuntimeError(
            "Expected signature_moments.experience_id was not found."
        )

    # ---------------------------------------------------------------
    # 1. Validate existing assignments.
    # ---------------------------------------------------------------

    original_moment_count = connection.exec_driver_sql(
        "SELECT COUNT(*) FROM signature_moments"
    ).scalar_one()

    original_assignment_count = connection.exec_driver_sql(
        """
        SELECT COUNT(*)
        FROM signature_moments
        WHERE experience_id IS NOT NULL
        """
    ).scalar_one()

    invalid_assignments = connection.exec_driver_sql(
        """
        SELECT sm.id, sm.experience_id
        FROM signature_moments AS sm
        LEFT JOIN experiences AS e
            ON e.id = sm.experience_id
        WHERE e.id IS NULL
        """
    ).fetchall()

    if invalid_assignments:
        raise RuntimeError(
            "Invalid existing Signature Moment assignments detected: "
            f"{invalid_assignments}. Migration stopped."
        )

    # ---------------------------------------------------------------
    # 2. Create the many-to-many association table.
    # ---------------------------------------------------------------

    op.create_table(
        ASSOCIATION_TABLE,

        sa.Column(
            "signature_moment_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "experience_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["signature_moment_id"],
            ["signature_moments.id"],
        ),

        sa.ForeignKeyConstraint(
            ["experience_id"],
            ["experiences.id"],
        ),

        sa.PrimaryKeyConstraint(
            "signature_moment_id",
            "experience_id",
        ),
    )

    # ---------------------------------------------------------------
    # 3. Preserve every existing assignment.
    # ---------------------------------------------------------------

    connection.exec_driver_sql(
        """
        INSERT INTO signature_moment_experiences (
            signature_moment_id,
            experience_id
        )
        SELECT
            id,
            experience_id
        FROM signature_moments
        """
    )

    copied_assignment_count = connection.exec_driver_sql(
        """
        SELECT COUNT(*)
        FROM signature_moment_experiences
        """
    ).scalar_one()

    if copied_assignment_count != original_assignment_count:
        raise RuntimeError(
            "Signature Moment assignment count mismatch. "
            f"Original: {original_assignment_count}; "
            f"Copied: {copied_assignment_count}."
        )

    # ---------------------------------------------------------------
    # 4. Remove the obsolete one-to-many foreign key and column.
    # ---------------------------------------------------------------

    with op.batch_alter_table(
        "signature_moments",
        recreate="always",
        naming_convention=FK_NAMING_CONVENTION,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_signature_moments_experience_id_experiences",
            type_="foreignkey",
        )

        batch_op.drop_column("experience_id")

    # ---------------------------------------------------------------
    # 5. Verify record preservation.
    # ---------------------------------------------------------------

    final_moment_count = connection.exec_driver_sql(
        "SELECT COUNT(*) FROM signature_moments"
    ).scalar_one()

    final_assignment_count = connection.exec_driver_sql(
        """
        SELECT COUNT(*)
        FROM signature_moment_experiences
        """
    ).scalar_one()

    if final_moment_count != original_moment_count:
        raise RuntimeError(
            "Signature Moment record count changed during migration. "
            f"Before: {original_moment_count}; "
            f"After: {final_moment_count}."
        )

    if final_assignment_count != original_assignment_count:
        raise RuntimeError(
            "Signature Moment assignments were not preserved."
        )

    # ---------------------------------------------------------------
    # 6. Verify the old column is gone.
    # ---------------------------------------------------------------

    final_columns = {
        column["name"]
        for column in sa.inspect(connection).get_columns(
            "signature_moments"
        )
    }

    if "experience_id" in final_columns:
        raise RuntimeError(
            "Obsolete experience_id column still exists."
        )

    # ---------------------------------------------------------------
    # 7. Verify association-table foreign keys.
    # ---------------------------------------------------------------

    association_fks = sa.inspect(connection).get_foreign_keys(
        ASSOCIATION_TABLE
    )

    referenced_tables = {
        fk["referred_table"]
        for fk in association_fks
    }

    if not {
        "signature_moments",
        "experiences",
    }.issubset(referenced_tables):
        raise RuntimeError(
            "Association table is missing an expected foreign key."
        )

    violations = connection.exec_driver_sql(
        "PRAGMA foreign_key_check(signature_moment_experiences)"
    ).fetchall()

    if violations:
        raise RuntimeError(
            "Foreign-key violations detected in the new association "
            f"table: {violations}"
        )

    print("\nSignature Moments migration completed successfully.")
    print(f"  Signature Moments preserved: {final_moment_count}")
    print(f"  Existing assignments preserved: {final_assignment_count}")
    print("  Old experience_id column removed.")
    print("  New many-to-many relationship created.")

# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------
def downgrade():
    raise RuntimeError(
        "This migration is intentionally irreversible. "
        "A many-to-many relationship may contain multiple Experience "
        "assignments per Signature Moment. Restore the pre-migration "
        "database backup to roll back safely.")