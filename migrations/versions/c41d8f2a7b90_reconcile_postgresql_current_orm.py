"""Reconcile PostgreSQL schema with current ORM.

Revision ID: c41d8f2a7b90
Revises: b7c91e4a2f63
Create Date: 2026-11-16
"""

from alembic import op
import sqlalchemy as sa


revision = "c41d8f2a7b90"
down_revision = "b7c91e4a2f63"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name):
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _column_exists(bind, table_name, column_name):
    if not _table_exists(bind, table_name):
        return False

    inspector = sa.inspect(bind)
    return any(
        column["name"] == column_name
        for column in inspector.get_columns(table_name)
    )


def _drop_foreign_keys_referencing_table(bind, target_table):
    """Drop all FK constraints in the public schema referencing target_table."""
    rows = bind.execute(
        sa.text(
            """
            SELECT
                tc.table_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
             AND tc.constraint_schema = ccu.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.constraint_schema = 'public'
              AND ccu.table_schema = 'public'
              AND ccu.table_name = :target_table
            """
        ),
        {"target_table": target_table},
    ).fetchall()

    for row in rows:
        op.drop_constraint(
            row.constraint_name,
            row.table_name,
            type_="foreignkey",
        )


def _drop_foreign_keys_from_table_to_table(
    bind,
    source_table,
    target_table,
):
    """Drop FK constraints on source_table that reference target_table."""
    if not _table_exists(bind, source_table):
        return

    rows = bind.execute(
        sa.text(
            """
            SELECT
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
             AND tc.constraint_schema = ccu.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.constraint_schema = 'public'
              AND tc.table_name = :source_table
              AND ccu.table_schema = 'public'
              AND ccu.table_name = :target_table
            """
        ),
        {
            "source_table": source_table,
            "target_table": target_table,
        },
    ).fetchall()

    for row in rows:
        op.drop_constraint(
            row.constraint_name,
            source_table,
            type_="foreignkey",
        )


def upgrade():
    bind = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Remove obsolete foreign keys pointing at the legacy `booking`
    #    table.
    #
    # The Render database is empty, so the historical booking table is
    # schema-only and can safely be replaced by the current `bookings`
    # model.
    # ------------------------------------------------------------------
    if _table_exists(bind, "booking"):
        _drop_foreign_keys_referencing_table(bind, "booking")

    # ------------------------------------------------------------------
    # 2. Remove obsolete booking table.
    #
    # This also removes the old ix_bookings_* indexes whose names conflict
    # with the indexes required by the current `bookings` model.
    # ------------------------------------------------------------------
    if _table_exists(bind, "booking"):
        op.drop_table("booking")

    # ------------------------------------------------------------------
    # 3. Remove obsolete Experience Schedule foreign keys/columns.
    # ------------------------------------------------------------------
    if _table_exists(bind, "experience_bookings"):
        _drop_foreign_keys_from_table_to_table(
            bind,
            "experience_bookings",
            "experience_schedules",
        )

        for column_name in (
            "schedule_id",
            "schedule_name_snapshot",
            "scheduled_start_at",
            "scheduled_end_at",
        ):
            if _column_exists(bind, "experience_bookings", column_name):
                op.drop_column("experience_bookings", column_name)

    # ------------------------------------------------------------------
    # 4. Remove obsolete Experience Availability table.
    # ------------------------------------------------------------------
    if _table_exists(bind, "experience_availability"):
        _drop_foreign_keys_referencing_table(
            bind,
            "experience_availability",
        )
        op.drop_table("experience_availability")

    # ------------------------------------------------------------------
    # 5. Remove obsolete Experience Schedules table.
    # ------------------------------------------------------------------
    if _table_exists(bind, "experience_schedules"):
        _drop_foreign_keys_referencing_table(
            bind,
            "experience_schedules",
        )
        op.drop_table("experience_schedules")

    # ------------------------------------------------------------------
    # 6. Create current `bookings` table.
    # ------------------------------------------------------------------
    if not _table_exists(bind, "bookings"):
        op.create_table(
            "bookings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "booking_reference",
                sa.String(length=30),
                nullable=False,
            ),
            sa.Column(
                "booking_uuid",
                sa.String(length=36),
                nullable=False,
            ),
            sa.Column(
                "booking_type",
                sa.String(length=50),
                nullable=False,
            ),
            sa.Column(
                "source",
                sa.String(length=30),
                nullable=False,
                server_default="website",
            ),
            sa.Column(
                "created_by_user_id",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "source_request_id",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "contact_id",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "first_name",
                sa.String(length=100),
                nullable=False,
            ),
            sa.Column(
                "last_name",
                sa.String(length=100),
                nullable=False,
            ),
            sa.Column(
                "email",
                sa.String(length=255),
                nullable=False,
            ),
            sa.Column(
                "phone",
                sa.String(length=50),
                nullable=True,
            ),
            sa.Column(
                "nationality",
                sa.String(length=100),
                nullable=True,
            ),
            sa.Column(
                "country_of_residence",
                sa.String(length=100),
                nullable=True,
            ),
            sa.Column(
                "adults",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),
            sa.Column(
                "children",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "infants",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "seniors",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "students",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "emergency_contact_name",
                sa.String(length=150),
                nullable=True,
            ),
            sa.Column(
                "emergency_contact_phone",
                sa.String(length=50),
                nullable=True,
            ),
            sa.Column(
                "emergency_contact_relationship",
                sa.String(length=100),
                nullable=True,
            ),
            sa.Column(
                "dietary_requirements",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "medical_information",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "accessibility_requirements",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "special_requests",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "status",
                sa.String(length=40),
                nullable=False,
                server_default="pending",
            ),
            sa.Column(
                "payment_status",
                sa.String(length=40),
                nullable=False,
                server_default="unpaid",
            ),
            sa.Column(
                "booking_date",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "experience_date",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "start_date",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "end_date",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "confirmed_at",
                sa.DateTime(),
                nullable=True,
            ),
            sa.Column(
                "cancelled_at",
                sa.DateTime(),
                nullable=True,
            ),
            sa.Column(
                "completed_at",
                sa.DateTime(),
                nullable=True,
            ),
            sa.Column(
                "cancellation_reason",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "currency",
                sa.String(length=3),
                nullable=False,
                server_default="KES",
            ),
            sa.Column(
                "subtotal",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "discount_amount",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "tax_amount",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "addon_total",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "total_amount",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "amount_paid",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "balance_due",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "customer_notes",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "internal_notes",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "confirmation_sent",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "reminder_sent",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "reviewed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.ForeignKeyConstraint(
                ["created_by_user_id"],
                ["users.id"],
                name="fk_bookings_created_by_user_id_users",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["source_request_id"],
                ["booking_requests.id"],
                name="fk_bookings_source_request_id_booking_requests",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_bookings_user_id_users",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["contact_id"],
                ["contacts.id"],
                name="fk_bookings_contact_id_contacts",
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "booking_reference",
                name="uq_bookings_booking_reference",
            ),
            sa.UniqueConstraint(
                "booking_uuid",
                name="uq_bookings_booking_uuid",
            ),
            sa.UniqueConstraint(
                "source_request_id",
                name="uq_bookings_source_request_id",
            ),
            sa.CheckConstraint(
                """
                adults >= 0
                AND children >= 0
                AND infants >= 0
                AND seniors >= 0
                AND students >= 0
                """,
                name="ck_bookings_nonnegative_group_counts",
            ),
            sa.CheckConstraint(
                """
                subtotal >= 0
                AND discount_amount >= 0
                AND tax_amount >= 0
                AND addon_total >= 0
                AND total_amount >= 0
                """,
                name="ck_bookings_nonnegative_financials",
            ),
        )

        # Explicit indexes matching the current ORM.
        op.create_index(
            "ix_bookings_booking_reference",
            "bookings",
            ["booking_reference"],
            unique=True,
        )
        op.create_index(
            "ix_bookings_booking_uuid",
            "bookings",
            ["booking_uuid"],
            unique=True,
        )
        op.create_index(
            "ix_bookings_booking_type",
            "bookings",
            ["booking_type"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_source",
            "bookings",
            ["source"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_created_by_user_id",
            "bookings",
            ["created_by_user_id"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_source_request_id",
            "bookings",
            ["source_request_id"],
            unique=True,
        )
        op.create_index(
            "ix_bookings_user_id",
            "bookings",
            ["user_id"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_contact_id",
            "bookings",
            ["contact_id"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_email",
            "bookings",
            ["email"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_phone",
            "bookings",
            ["phone"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_status",
            "bookings",
            ["status"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_payment_status",
            "bookings",
            ["payment_status"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_booking_date",
            "bookings",
            ["booking_date"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_experience_date",
            "bookings",
            ["experience_date"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_start_date",
            "bookings",
            ["start_date"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_end_date",
            "bookings",
            ["end_date"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_active",
            "bookings",
            ["active"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_created_at",
            "bookings",
            ["created_at"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_type_status_date",
            "bookings",
            ["booking_type", "status", "start_date"],
            unique=False,
        )
        op.create_index(
            "ix_bookings_customer_dates",
            "bookings",
            ["email", "start_date", "end_date"],
            unique=False,
        )

    # ------------------------------------------------------------------
    # 7. Create current ContactNote model.
    # ------------------------------------------------------------------
    if not _table_exists(bind, "contact_notes"):
        op.create_table(
            "contact_notes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("contact_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column(
                "author_name",
                sa.String(length=150),
                nullable=True,
            ),
            sa.Column("note", sa.Text(), nullable=False),
            sa.Column(
                "note_type",
                sa.String(length=50),
                nullable=False,
                server_default="General",
            ),
            sa.Column(
                "is_important",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.ForeignKeyConstraint(
                ["contact_id"],
                ["contacts.id"],
                name="fk_contact_notes_contact_id_contacts",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_contact_notes_user_id_users",
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

        op.create_index(
            "ix_contact_notes_contact_id",
            "contact_notes",
            ["contact_id"],
            unique=False,
        )
        op.create_index(
            "ix_contact_notes_user_id",
            "contact_notes",
            ["user_id"],
            unique=False,
        )
        op.create_index(
            "ix_contact_notes_note_type",
            "contact_notes",
            ["note_type"],
            unique=False,
        )
        op.create_index(
            "ix_contact_notes_is_important",
            "contact_notes",
            ["is_important"],
            unique=False,
        )
        op.create_index(
            "ix_contact_notes_created_at",
            "contact_notes",
            ["created_at"],
            unique=False,
        )

    # ------------------------------------------------------------------
    # 8. Create current reusable Signature Moment many-to-many table.
    # ------------------------------------------------------------------
    if not _table_exists(bind, "signature_moment_experiences"):
        op.create_table(
            "signature_moment_experiences",
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
                name="fk_signature_moment_experiences_signature_moment_id",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["experience_id"],
                ["experiences.id"],
                name="fk_signature_moment_experiences_experience_id",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "signature_moment_id",
                "experience_id",
            ),
        )

    # ------------------------------------------------------------------
    # 9. Rewire current booking child tables from legacy `booking.id`
    #    to current `bookings.id`.
    #
    # These tables already exist from the historical migration chain.
    # Their old FK constraints were removed when `booking` was dropped.
    # ------------------------------------------------------------------
    booking_child_tables = {
        "booking_addons": "booking_id",
        "booking_documents": "booking_id",
        "booking_notes": "booking_id",
        "booking_payments": "booking_id",
        "booking_travellers": "booking_id",
        "destination_bookings": "booking_id",
        "experience_bookings": "booking_id",
        "safari_bookings": "booking_id",
        "staff_assignments": "booking_id",
        "stay_bookings": "booking_id",
        "tasks": "booking_id",
        "experience_reviews": "booking_id",
    }

    for table_name, column_name in booking_child_tables.items():
        if not _table_exists(bind, table_name):
            continue

        if not _column_exists(bind, table_name, column_name):
            continue

        op.create_foreign_key(
            f"fk_{table_name}_{column_name}_bookings",
            table_name,
            "bookings",
            [column_name],
            ["id"],
            ondelete="CASCADE",
        )

    # ------------------------------------------------------------------
    # 10. BookingRequest must no longer contain booking_id.
    # ------------------------------------------------------------------
    if _column_exists(bind, "booking_requests", "booking_id"):
        _drop_foreign_keys_from_table_to_table(
            bind,
            "booking_requests",
            "bookings",
        )
        _drop_foreign_keys_from_table_to_table(
            bind,
            "booking_requests",
            "booking",
        )
        op.drop_column("booking_requests", "booking_id")


def downgrade():
    raise NotImplementedError(
        "This migration reconciles the Render schema with the current ORM "
        "and is intentionally not reversible."
    )