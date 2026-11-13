"""Add destination and location to photography spots

Revision ID: bc08f88162ef
Revises: sm_m2m_20261102
Create Date: 2026-11-03 04:42:20.412068
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bc08f88162ef"
down_revision = "sm_m2m_20261102"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("photography_spots", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("destination_id", sa.Integer(), nullable=True)
        )

        batch_op.add_column(
            sa.Column("location", sa.String(length=255), nullable=True)
        )

        batch_op.create_index(
            "ix_photography_spots_destination_id",
            ["destination_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_photography_spots_destination_id_destinations",
            "destinations",
            ["destination_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("photography_spots", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_photography_spots_destination_id_destinations",
            type_="foreignkey",
        )

        batch_op.drop_index("ix_photography_spots_destination_id")

        batch_op.drop_column("location")
        batch_op.drop_column("destination_id")