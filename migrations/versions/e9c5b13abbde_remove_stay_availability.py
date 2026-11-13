"""Remove stay availability

Revision ID: e9c5b13abbde
Revises: 9237113b43ea
Create Date: 2026-11-10 09:51:30.191932

This migration intentionally removes only the obsolete
date-range StayAvailability architecture.

The following remain untouched:
- stays
- stay_rooms
- stay_bookings
- bookings
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e9c5b13abbde'
down_revision = '9237113b43ea'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table("stay_availability")


def downgrade():
    raise RuntimeError(
        "The obsolete stay_availability architecture was intentionally "
        "removed and is not automatically restorable."
    )