"""
Preserve experience active state during destination deactivation

Revision ID: fe78cb827942
Revises: 3aa6e070d881
Create Date: 2026-11-06 09:33:15.508559

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe78cb827942"
down_revision = "3aa6e070d881"
branch_labels = None
depends_on = None


def upgrade():
    """
    Add the field used to preserve an Experience's individual active state
    while its parent Destination is deactivated.
    """

    with op.batch_alter_table("experiences", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "destination_deactivation_previous_active",
                sa.Boolean(),
                nullable=True,
            )
        )


def downgrade():
    """
    Remove the Destination deactivation state field.
    """

    with op.batch_alter_table("experiences", schema=None) as batch_op:
        batch_op.drop_column(
            "destination_deactivation_previous_active"
        )