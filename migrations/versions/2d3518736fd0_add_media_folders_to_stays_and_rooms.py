"""Add media folders to stays and rooms

Revision ID: 2d3518736fd0
Revises: fe78cb827942
Create Date: 2026-11-08 12:36:49.004420

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2d3518736fd0"
down_revision = "fe78cb827942"
branch_labels = None
depends_on = None


def upgrade():
    # Add media folder reference to stays.
    with op.batch_alter_table("stays", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "media_folder_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            batch_op.f("ix_stays_media_folder_id"),
            ["media_folder_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_stays_media_folder_id_media_folders",
            "media_folders",
            ["media_folder_id"],
            ["id"],
        )

    # Add media folder reference to stay rooms.
    with op.batch_alter_table("stay_rooms", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "media_folder_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            batch_op.f("ix_stay_rooms_media_folder_id"),
            ["media_folder_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_stay_rooms_media_folder_id_media_folders",
            "media_folders",
            ["media_folder_id"],
            ["id"],
        )


def downgrade():
    # Remove media folder reference from stay rooms.
    with op.batch_alter_table("stay_rooms", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_stay_rooms_media_folder_id_media_folders",
            type_="foreignkey",
        )

        batch_op.drop_index(
            batch_op.f("ix_stay_rooms_media_folder_id")
        )

        batch_op.drop_column("media_folder_id")

    # Remove media folder reference from stays.
    with op.batch_alter_table("stays", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_stays_media_folder_id_media_folders",
            type_="foreignkey",
        )

        batch_op.drop_index(
            batch_op.f("ix_stays_media_folder_id")
        )

        batch_op.drop_column("media_folder_id")