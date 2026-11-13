"""Convert stay availability to date ranges
Revision ID: 6b9ab6107ece
Revises: 250b4b3cf66f
Create Date: 2026-10-31 21:26:35.201851
"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "6b9ab6107ece"
down_revision = "250b4b3cf66f"
branch_labels = None
depends_on = None

def upgrade():
    # -------------------------------------------------------------------------
    # Add nullable date-range columns first.
    # Existing records must be populated before these become NOT NULL.
    # -------------------------------------------------------------------------
    with op.batch_alter_table("stay_availability") as batch_op:
        batch_op.add_column(
            sa.Column("start_date", sa.Date(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("end_date", sa.Date(), nullable=True)
        )

    # -------------------------------------------------------------------------
    # Preserve existing daily dates as one-day availability periods.
    # -------------------------------------------------------------------------
    op.execute(
        """
        UPDATE stay_availability
        SET
            start_date = date,
            end_date = date
        WHERE date IS NOT NULL
        """
    )

    # -------------------------------------------------------------------------
    # Convert legacy statuses to the new supported statuses.
    # -------------------------------------------------------------------------
    op.execute(
        """
        UPDATE stay_availability
        SET status = 'Unavailable'
        WHERE status IN ('Sold Out', 'Closed')
        """
    )

    # -------------------------------------------------------------------------
    # Ensure existing currency values satisfy the new NOT NULL constraint.
    # -------------------------------------------------------------------------
    op.execute(
        """
        UPDATE stay_availability
        SET currency = 'KES'
        WHERE currency IS NULL OR TRIM(currency) = ''
        """
    )

    # -------------------------------------------------------------------------
    # Verify no existing records have been left without dates.
    # -------------------------------------------------------------------------
    connection = op.get_bind()

    missing_dates = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM stay_availability
            WHERE start_date IS NULL OR end_date IS NULL
            """
        )
    ).scalar()

    if missing_dates:
        raise RuntimeError(
            "Stay availability migration stopped: "
            "some existing records could not be assigned dates."
        )

    # -------------------------------------------------------------------------
    # Enforce the new schema and remove obsolete daily inventory fields.
    # -------------------------------------------------------------------------
    with op.batch_alter_table("stay_availability") as batch_op:
        batch_op.alter_column(
            "start_date",
            existing_type=sa.Date(),
            nullable=False,
        )

        batch_op.alter_column(
            "end_date",
            existing_type=sa.Date(),
            nullable=False,
        )

        batch_op.alter_column(
            "currency",
            existing_type=sa.String(length=10),
            nullable=False,
        )

        batch_op.drop_index("ix_stay_availability_date")

        batch_op.create_index(
            "ix_stay_availability_start_date",
            ["start_date"],
            unique=False,
        )

        batch_op.create_index(
            "ix_stay_availability_end_date",
            ["end_date"],
            unique=False,
        )

        batch_op.create_index(
            "ix_stay_availability_status",
            ["status"],
            unique=False,
        )

        batch_op.drop_column("blocked_units")
        batch_op.drop_column("reserved_units")
        batch_op.drop_column("available_units")
        batch_op.drop_column("total_units")
        batch_op.drop_column("date")


def downgrade():
    # -------------------------------------------------------------------------
    # Restore the legacy columns.
    # Inventory values cannot be reconstructed after the upgrade, so they
    # are restored with zero defaults.
    # -------------------------------------------------------------------------
    with op.batch_alter_table("stay_availability") as batch_op:
        batch_op.add_column(
            sa.Column(
                "date",
                sa.Date(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "total_units",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "available_units",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "reserved_units",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

        batch_op.add_column(
            sa.Column(
                "blocked_units",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

        batch_op.drop_index("ix_stay_availability_status")
        batch_op.drop_index("ix_stay_availability_end_date")
        batch_op.drop_index("ix_stay_availability_start_date")

        batch_op.create_index(
            "ix_stay_availability_date",
            ["date"],
            unique=False,
        )

    # -------------------------------------------------------------------------
    # Restore the original date using the beginning of each range.
    # -------------------------------------------------------------------------
    op.execute(
        """
        UPDATE stay_availability
        SET date = start_date
        """
    )

    # -------------------------------------------------------------------------
    # Restore the original nullable currency definition and remove range dates.
    # -------------------------------------------------------------------------
    with op.batch_alter_table("stay_availability") as batch_op:
        batch_op.alter_column(
            "currency",
            existing_type=sa.String(length=10),
            nullable=True,
        )

        batch_op.drop_column("end_date")
        batch_op.drop_column("start_date")

    # Note: Inventory counts cannot be recovered by downgrade.
