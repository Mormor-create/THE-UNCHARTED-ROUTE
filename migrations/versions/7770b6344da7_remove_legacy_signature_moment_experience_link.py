"""Remove legacy signature moment experience link

Revision ID: 7f4c2e91ab63
Revises: c41d8f2a7b90
Create Date: 2026-11-16
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f4c2e91ab63"
down_revision = "c41d8f2a7b90"
branch_labels = None
depends_on = None


def upgrade():
    # The current architecture uses the reusable many-to-many
    # signature_moment_experiences association table.
    #
    # Remove the obsolete legacy direct experience relationship.
    op.drop_constraint(
        "signature_moments_experience_id_fkey",
        "signature_moments",
        type_="foreignkey",
    )

    op.drop_column(
        "signature_moments",
        "experience_id",
    )


def downgrade():
    # Restore the legacy column and relationship if this migration
    # is ever reversed.
    op.add_column(
        "signature_moments",
        sa.Column(
            "experience_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "signature_moments_experience_id_fkey",
        "signature_moments",
        "experiences",
        ["experience_id"],
        ["id"],
    )