"""
Remove experience schedules

Revision ID: 9237113b43ea
Revises: 2d3518736fd0
Create Date: 2026-11-10 07:04:00.672074

This migration intentionally removes only the obsolete Experience Schedule
architecture.

The database is currently in a partially migrated state where:
    - experience_schedules has already been dropped
    - experience_bookings still contains the old schedule columns
    - experience_bookings still contains the old schedule foreign key
    - the old schedule indexes still exist

This migration rebuilds experience_bookings without those obsolete fields.

It does NOT modify:
    - staff_schedules
    - staff_availability
    - staff_assignments
    - bookings
    - experience_pricing
    - any other booking architecture
"""

from alembic import op
import sqlalchemy as sa


revision = "9237113b43ea"
down_revision = "2d3518736fd0"
branch_labels = None
depends_on = None


def upgrade():
    """
    Rebuild experience_bookings without the obsolete Experience Schedule
    architecture.

    SQLite requires a table rebuild for this structural change.

    The existing experience_bookings records are copied into the replacement
    table. The obsolete schedule fields and foreign key are intentionally
    excluded.
    """

    # SQLite cannot drop the existing table while foreign-key enforcement
    # is active because the old table still references the already-removed
    # experience_schedules table.
    #
    # Use an Alembic autocommit block so the SQLite PRAGMA is actually applied.
    with op.get_context().autocommit_block():
        if op.get_bind().dialect.name == "sqlite":
            op.execute("PRAGMA foreign_keys=OFF")
        # ------------------------------------------------------------------
        # Create replacement table.
        # ------------------------------------------------------------------
        op.create_table(
            "_experience_bookings_new",

            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
            ),

            sa.Column(
                "booking_id",
                sa.Integer(),
                sa.ForeignKey(
                    "booking.id",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),

            sa.Column(
                "experience_id",
                sa.Integer(),
                sa.ForeignKey(
                    "experiences.id",
                    ondelete="SET NULL",
                ),
                nullable=True,
            ),

            sa.Column(
                "pricing_id",
                sa.Integer(),
                sa.ForeignKey(
                    "experience_pricing.id",
                    ondelete="SET NULL",
                ),
                nullable=True,
            ),

            sa.Column(
                "experience_name_snapshot",
                sa.String(255),
                nullable=False,
            ),

            sa.Column(
                "experience_code_snapshot",
                sa.String(100),
                nullable=True,
            ),

            sa.Column(
                "description_snapshot",
                sa.Text(),
                nullable=True,
            ),

            sa.Column(
                "meeting_point_snapshot",
                sa.String(255),
                nullable=True,
            ),

            sa.Column(
                "location_snapshot",
                sa.String(255),
                nullable=True,
            ),

            sa.Column(
                "duration_snapshot",
                sa.String(100),
                nullable=True,
            ),

            sa.Column(
                "pricing_name_snapshot",
                sa.String(150),
                nullable=True,
            ),

            sa.Column(
                "price_basis",
                sa.String(40),
                nullable=False,
                server_default="per_person",
            ),

            sa.Column(
                "unit_price",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0.00",
            ),

            sa.Column(
                "quantity",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),

            sa.Column(
                "currency",
                sa.String(3),
                nullable=False,
                server_default="KES",
            ),

            sa.Column(
                "pickup_location",
                sa.String(255),
                nullable=True,
            ),

            sa.Column(
                "dropoff_location",
                sa.String(255),
                nullable=True,
            ),

            sa.Column(
                "customer_instructions",
                sa.Text(),
                nullable=True,
            ),

            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
            ),

            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
            ),

            sa.CheckConstraint(
                "quantity >= 1",
                name="ck_experience_bookings_quantity_positive",
            ),

            sa.CheckConstraint(
                "unit_price >= 0",
                name="ck_experience_bookings_unit_price_nonnegative",
            ),
        )

        # ------------------------------------------------------------------
        # Copy existing ExperienceBooking data.
        #
        # The obsolete schedule fields are deliberately excluded.
        # Existing booking/detail data is preserved.
        # ------------------------------------------------------------------
        op.execute(
            """
            INSERT INTO _experience_bookings_new (
                id,
                booking_id,
                experience_id,
                pricing_id,
                experience_name_snapshot,
                experience_code_snapshot,
                description_snapshot,
                meeting_point_snapshot,
                location_snapshot,
                duration_snapshot,
                pricing_name_snapshot,
                price_basis,
                unit_price,
                quantity,
                currency,
                pickup_location,
                dropoff_location,
                customer_instructions,
                created_at,
                updated_at
            )
            SELECT
                id,
                booking_id,
                experience_id,
                pricing_id,
                experience_name_snapshot,
                experience_code_snapshot,
                description_snapshot,
                meeting_point_snapshot,
                location_snapshot,
                duration_snapshot,
                pricing_name_snapshot,
                price_basis,
                unit_price,
                quantity,
                currency,
                pickup_location,
                dropoff_location,
                customer_instructions,
                created_at,
                updated_at
            FROM experience_bookings
            """
        )

        # ------------------------------------------------------------------
        # Remove the old table.
        #
        # This also removes:
        #   - schedule_id
        #   - schedule_name_snapshot
        #   - scheduled_start_at
        #   - scheduled_end_at
        #   - old schedule foreign key
        #   - old schedule indexes
        # ------------------------------------------------------------------
        op.drop_table("experience_bookings")

        # ------------------------------------------------------------------
        # Rename replacement table.
        # ------------------------------------------------------------------
        op.rename_table(
            "_experience_bookings_new",
            "experience_bookings",
        )

        # ------------------------------------------------------------------
        # Restore indexes belonging to the current ExperienceBooking model.
        # ------------------------------------------------------------------
        op.create_index(
            "ix_experience_bookings_booking_id",
            "experience_bookings",
            ["booking_id"],
            unique=True,
        )

        op.create_index(
            "ix_experience_bookings_experience_id",
            "experience_bookings",
            ["experience_id"],
            unique=False,
        )

        op.create_index(
            "ix_experience_bookings_pricing_id",
            "experience_bookings",
            ["pricing_id"],
            unique=False,
        )

        # ------------------------------------------------------------------
        # Restore SQLite foreign-key enforcement.
        # ------------------------------------------------------------------
        if op.get_bind().dialect.name == "sqlite":
            op.execute("PRAGMA foreign_keys=ON")
def downgrade():
    raise RuntimeError(
        "The Experience Schedule architecture was intentionally removed. "
        "Restore the pre-migration database backup to roll back this change."
    )
