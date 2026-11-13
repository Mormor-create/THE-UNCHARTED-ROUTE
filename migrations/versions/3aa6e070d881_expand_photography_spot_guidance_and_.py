"""Expand photography spot guidance and conditions

Revision ID: 3aa6e070d881
Revises: bc08f88162ef
Create Date: 2026-11-03 04:59:34.283169
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3aa6e070d881"
down_revision = "bc08f88162ef"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "photography_spots",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "best_time_to_visit",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "best_time_to_photograph",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "recommended_lenses",
                sa.Text(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "lighting_conditions",
                sa.Text(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "weather_conditions",
                sa.Text(),
                nullable=True,
            )
        )

def downgrade():
    with op.batch_alter_table(
        "photography_spots",
        schema=None,
    ) as batch_op:

        batch_op.drop_column("weather_conditions")
        batch_op.drop_column("lighting_conditions")
        batch_op.drop_column("recommended_lenses")
        batch_op.drop_column("best_time_to_photograph")
        batch_op.drop_column("best_time_to_visit")