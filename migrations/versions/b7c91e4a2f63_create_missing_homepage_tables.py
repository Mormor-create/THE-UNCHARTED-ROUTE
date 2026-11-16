
"""Create missing homepage CMS tables.

Revision ID: b7c91e4a2f63
Revises: 4e4a9ac52cc9
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "b7c91e4a2f63"
down_revision = "4e4a9ac52cc9"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # ---------------------------------------------------------
    # Homepages
    # ---------------------------------------------------------
    if not inspector.has_table("homepages"):
        op.create_table(
            "homepages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "is_published",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("meta_title", sa.String(length=255), nullable=True),
            sa.Column("meta_description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    # Refresh inspector after possible table creation.
    inspector = inspect(bind)

    # ---------------------------------------------------------
    # Homepage sections
    # ---------------------------------------------------------
    if not inspector.has_table("homepage_sections"):

        if not inspector.has_table("media_assets"):
            raise RuntimeError(
                "Cannot create homepage_sections: "
                "media_assets table does not exist."
            )

        op.create_table(
            "homepage_sections",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("homepage_id", sa.Integer(), nullable=False),
            sa.Column("section_type", sa.String(length=50), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("subtitle", sa.String(length=500), nullable=True),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("cta_text", sa.String(length=100), nullable=True),
            sa.Column("cta_url", sa.String(length=500), nullable=True),
            sa.Column("media_asset_id", sa.Integer(), nullable=True),
            sa.Column("display_order", sa.Integer(), nullable=False),
            sa.Column(
                "is_visible",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["homepage_id"],
                ["homepages.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["media_asset_id"],
                ["media_assets.id"],
                ondelete="SET NULL",
            ),
        )

    # ---------------------------------------------------------
    # Homepage section indexes
    # Create only indexes that are missing.
    # ---------------------------------------------------------
    inspector = inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("homepage_sections")
    }

    indexes = {
        "ix_homepage_sections_display_order": ["display_order"],
        "ix_homepage_sections_homepage_id": ["homepage_id"],
        "ix_homepage_sections_media_asset_id": ["media_asset_id"],
        "ix_homepage_sections_section_type": ["section_type"],
    }

    for index_name, columns in indexes.items():
        if index_name not in existing_indexes:
            op.create_index(
                index_name,
                "homepage_sections",
                columns,
                unique=False,
            )


def downgrade():
    # Intentionally preserve these tables and their data.
    pass
