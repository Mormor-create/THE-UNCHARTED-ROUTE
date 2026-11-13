
"""
Add promotion inquiries

Revision ID: e3ffac21080c
Revises: 6b9ab6107ece
Create Date: 2026-11-01 01:05:34.932249

"""

from alembic import op
import sqlalchemy as sa


# =============================================================================
# Revision identifiers
# =============================================================================

revision = "e3ffac21080c"
down_revision = "6b9ab6107ece"
branch_labels = None
depends_on = None


# =============================================================================
# Upgrade
# =============================================================================

def upgrade():

    # -------------------------------------------------------------------------
    # Create Promotion Inquiries Table
    # -------------------------------------------------------------------------

    op.create_table(
        "promotion_inquiries",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "promotion_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "promotion_title",
            sa.String(length=200),
            nullable=False,
        ),

        sa.Column(
            "customer_name",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "phone",
            sa.String(length=40),
            nullable=False,
        ),

        sa.Column(
            "country",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "contact_method",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "admin_notes",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "submitted_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # Promotion Inquiry Indexes
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "promotion_inquiries",
        schema=None,
    ) as batch_op:

        batch_op.create_index(
            batch_op.f("ix_promotion_inquiries_email"),
            ["email"],
            unique=False,
        )

        batch_op.create_index(
            batch_op.f("ix_promotion_inquiries_promotion_id"),
            ["promotion_id"],
            unique=False,
        )

        batch_op.create_index(
            batch_op.f("ix_promotion_inquiries_status"),
            ["status"],
            unique=False,
        )

        batch_op.create_index(
            batch_op.f("ix_promotion_inquiries_submitted_at"),
            ["submitted_at"],
            unique=False,
        )

    # -------------------------------------------------------------------------
    # Remove Obsolete Promotion Booking URL
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "promotions",
        schema=None,
    ) as batch_op:

        batch_op.drop_column("booking_url")


# =============================================================================
# Downgrade
# =============================================================================

def downgrade():

    # -------------------------------------------------------------------------
    # Restore Obsolete Promotion Booking URL
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "promotions",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "booking_url",
                sa.VARCHAR(length=500),
                nullable=True,
            )
        )

    # -------------------------------------------------------------------------
    # Remove Promotion Inquiry Indexes
    # -------------------------------------------------------------------------

    with op.batch_alter_table(
        "promotion_inquiries",
        schema=None,
    ) as batch_op:

        batch_op.drop_index(
            batch_op.f("ix_promotion_inquiries_submitted_at")
        )

        batch_op.drop_index(
            batch_op.f("ix_promotion_inquiries_status")
        )

        batch_op.drop_index(
            batch_op.f("ix_promotion_inquiries_promotion_id")
        )

        batch_op.drop_index(
            batch_op.f("ix_promotion_inquiries_email")
        )

    # -------------------------------------------------------------------------
    # Drop Promotion Inquiries Table
    # -------------------------------------------------------------------------

    op.drop_table("promotion_inquiries")
