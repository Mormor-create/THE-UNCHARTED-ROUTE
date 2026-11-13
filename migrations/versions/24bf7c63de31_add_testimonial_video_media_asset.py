"""Add testimonial video media asset.

Revision ID: 24bf7c63de31
Revises: 5ef4ef7791a1
"""

from alembic import op
import sqlalchemy as sa

revision = "24bf7c63de31"
down_revision = "5ef4ef7791a1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "testimonials",
        schema=None,
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
        },
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "video_asset_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_testimonials_video_asset_id_media_assets",
            "media_assets",
            ["video_asset_id"],
            ["id"],
            ondelete="SET NULL",
        )

        batch_op.create_index(
            "ix_testimonials_video_asset_id",
            ["video_asset_id"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table(
        "testimonials",
        schema=None,
        naming_convention={
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
        },
    ) as batch_op:
        batch_op.drop_index("ix_testimonials_video_asset_id")

        batch_op.drop_constraint(
            "fk_testimonials_video_asset_id_media_assets",
            type_="foreignkey",
        )

        batch_op.drop_column("video_asset_id")
