"""Add media asset references to destinations

Revision ID: f724c7bf484a
Revises: b3e6849f170e
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f724c7bf484a"
down_revision = "b3e6849f170e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("destinations", schema=None) as batch_op:
        # Add the new MediaAsset reference columns.
        batch_op.add_column(
            sa.Column(
                "featured_image_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "banner_image_id",
                sa.Integer(),
                nullable=True,
            )
        )

        # Explicitly named foreign keys.
        batch_op.create_foreign_key(
            "fk_destinations_featured_image_id_media_assets",
            "media_assets",
            ["featured_image_id"],
            ["id"],
        )

        batch_op.create_foreign_key(
            "fk_destinations_banner_image_id_media_assets",
            "media_assets",
            ["banner_image_id"],
            ["id"],
        )

        # Remove the old filename/path fields.
        batch_op.drop_column("featured_image")
        batch_op.drop_column("banner_image")


def downgrade():
    with op.batch_alter_table("destinations", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "featured_image",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "banner_image",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.drop_constraint(
            "fk_destinations_banner_image_id_media_assets",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "fk_destinations_featured_image_id_media_assets",
            type_="foreignkey",
        )

        batch_op.drop_column("banner_image_id")
        batch_op.drop_column("featured_image_id")