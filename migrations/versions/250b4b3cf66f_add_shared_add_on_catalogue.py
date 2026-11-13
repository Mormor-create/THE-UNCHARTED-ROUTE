
"""Add shared add-on catalogue

Revision ID: 250b4b3cf66f
Revises: 9375f6f59de1
Create Date: 2026-10-29 01:05:35.321531
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "250b4b3cf66f"
down_revision = "9375f6f59de1"
branch_labels = None
depends_on = None


def upgrade():
    """Create the shared add-on catalogue and link booking add-ons to it."""

    # ------------------------------------------------------------------
    # Shared add-on catalogue
    # ------------------------------------------------------------------
    op.create_table(
        "addon_catalogue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("short_description", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("applicable_services", sa.JSON(), nullable=False),
        sa.Column("pricing_basis", sa.String(length=30), nullable=False),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("minimum_quantity", sa.Integer(), nullable=False),
        sa.Column("maximum_quantity", sa.Integer(), nullable=True),
        sa.Column("available_quantity", sa.Integer(), nullable=True),
        sa.Column("available_from", sa.Date(), nullable=True),
        sa.Column("available_until", sa.Date(), nullable=True),
        sa.Column("is_optional", sa.Boolean(), nullable=False),
        sa.Column(
            "can_be_booked_independently",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "requires_confirmation",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("experience_addon_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["experience_addon_id"],
            ["experience_addons.id"],
            name="fk_addon_catalogue_experience_addon_id_experience_addons",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_addon_catalogue_active",
        "addon_catalogue",
        ["active"],
        unique=False,
    )
    op.create_index(
        "ix_addon_catalogue_category",
        "addon_catalogue",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_addon_catalogue_code",
        "addon_catalogue",
        ["code"],
        unique=True,
    )
    op.create_index(
        "ix_addon_catalogue_experience_addon_id",
        "addon_catalogue",
        ["experience_addon_id"],
        unique=False,
    )
    op.create_index(
        "ix_addon_catalogue_name",
        "addon_catalogue",
        ["name"],
        unique=False,
    )
    op.create_index(
        "ix_addon_catalogue_slug",
        "addon_catalogue",
        ["slug"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # Link existing booking add-ons to the shared catalogue.
    # Preserve the table's existing foreign keys and constraints.
    # ------------------------------------------------------------------
    with op.batch_alter_table("booking_addons") as batch_op:
        batch_op.add_column(
            sa.Column(
                "addon_catalogue_id",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_booking_addons_addon_catalogue_id_addon_catalogue",
            "addon_catalogue",
            ["addon_catalogue_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_index(
        "ix_booking_addons_addon_catalogue_id",
        "booking_addons",
        ["addon_catalogue_id"],
        unique=False,
    )


def downgrade():
    """Remove the shared catalogue changes without altering unrelated tables."""

    op.drop_index(
        "ix_booking_addons_addon_catalogue_id",
        table_name="booking_addons",
    )

    with op.batch_alter_table("booking_addons") as batch_op:
        batch_op.drop_constraint(
            "fk_booking_addons_addon_catalogue_id_addon_catalogue",
            type_="foreignkey",
        )
        batch_op.drop_column("addon_catalogue_id")

    op.drop_index(
        "ix_addon_catalogue_slug",
        table_name="addon_catalogue",
    )
    op.drop_index(
        "ix_addon_catalogue_name",
        table_name="addon_catalogue",
    )
    op.drop_index(
        "ix_addon_catalogue_experience_addon_id",
        table_name="addon_catalogue",
    )
    op.drop_index(
        "ix_addon_catalogue_code",
        table_name="addon_catalogue",
    )
    op.drop_index(
        "ix_addon_catalogue_category",
        table_name="addon_catalogue",
    )
    op.drop_index(
        "ix_addon_catalogue_active",
        table_name="addon_catalogue",
    )

    op.drop_table("addon_catalogue")
