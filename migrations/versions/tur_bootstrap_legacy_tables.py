"""Bootstrap legacy operational tables required by the historical migration chain

Revision ID: tur_bootstrap_legacy_tables
Revises: da13bb68fff4
Create Date: 2026-11-15

This migration restores five tables that existed physically in the
application database before the historical migrations that modify them,
but were never represented by an Alembic CREATE TABLE operation.

The schemas below are the pre-9375 historical schemas. They are intentionally
NOT copied from the current SQLAlchemy models because later migrations are
responsible for evolving these tables.
"""

from alembic import op
import sqlalchemy as sa


revision = "tur_bootstrap_legacy_tables"
down_revision = "da13bb68fff4"
branch_labels = None
depends_on = None


def upgrade():
    # -------------------------------------------------------------------------
    # STAFF
    # -------------------------------------------------------------------------
    op.create_table(
        "staff",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "employee_number",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "staff_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "department",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "job_title",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "employment_type",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "hire_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "emergency_contact_name",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "emergency_contact_phone",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "qualifications",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "certifications",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "languages",
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_number"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
    )

    op.create_index(
        "ix_staff_user_id",
        "staff",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_staff_employee_number",
        "staff",
        ["employee_number"],
        unique=False,
    )

    op.create_index(
        "ix_staff_staff_type",
        "staff",
        ["staff_type"],
        unique=False,
    )

    op.create_index(
        "ix_staff_status",
        "staff",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_staff_department",
        "staff",
        ["department"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # STAFF SCHEDULES
    # -------------------------------------------------------------------------
    op.create_table(
        "staff_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["staff_id"],
            ["staff.id"],
        ),
    )

    op.create_index(
        "ix_staff_schedules_staff_id",
        "staff_schedules",
        ["staff_id"],
        unique=False,
    )

    op.create_index(
        "ix_staff_schedules_status",
        "staff_schedules",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_staff_schedules_start_datetime",
        "staff_schedules",
        ["start_datetime"],
        unique=False,
    )

    op.create_index(
        "ix_staff_schedules_end_datetime",
        "staff_schedules",
        ["end_datetime"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # STAFF AVAILABILITY
    # -------------------------------------------------------------------------
    op.create_table(
        "staff_availability",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["staff_id"],
            ["staff.id"],
        ),
    )

    op.create_index(
        "ix_staff_availability_staff_id",
        "staff_availability",
        ["staff_id"],
        unique=False,
    )

    op.create_index(
        "ix_staff_availability_status",
        "staff_availability",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_staff_availability_date",
        "staff_availability",
        ["date"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # STAFF ASSIGNMENTS
    # -------------------------------------------------------------------------
    op.create_table(
        "staff_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["staff_id"],
            ["staff.id"],
        ),
    )

    op.create_index(
        "ix_staff_assignments_staff_id",
        "staff_assignments",
        ["staff_id"],
        unique=False,
    )

    op.create_index(
        "ix_staff_assignments_booking_id",
        "staff_assignments",
        ["booking_id"],
        unique=False,
    )

    op.create_index(
        "ix_staff_assignments_role",
        "staff_assignments",
        ["role"],
        unique=False,
    )

    op.create_index(
        "ix_staff_assignments_status",
        "staff_assignments",
        ["status"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # CONTACT REPLIES
    # -------------------------------------------------------------------------
    #
    # This is the schema BEFORE 73df599a7441 adds:
    #   direction
    #   email_message_id
    #   received_at
    #
    # Those columns must remain absent here because 73df is responsible for
    # adding them later in the historical chain.
    # -------------------------------------------------------------------------
    op.create_table(
        "contact_replies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("sender_name", sa.String(length=150), nullable=True),
        sa.Column("sender_email", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "delivery_method",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "delivery_status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("failed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contacts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
    )

    op.create_index(
        "ix_contact_replies_contact_id",
        "contact_replies",
        ["contact_id"],
        unique=False,
    )

    op.create_index(
        "ix_contact_replies_user_id",
        "contact_replies",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_contact_replies_delivery_status",
        "contact_replies",
        ["delivery_status"],
        unique=False,
    )

    op.create_index(
        "ix_contact_replies_sent_at",
        "contact_replies",
        ["sent_at"],
        unique=False,
    )

    op.create_index(
        "ix_contact_replies_created_at",
        "contact_replies",
        ["created_at"],
        unique=False,
    )


def downgrade():
    op.drop_table("contact_replies")
    op.drop_table("staff_assignments")
    op.drop_table("staff_availability")
    op.drop_table("staff_schedules")
    op.drop_table("staff")
