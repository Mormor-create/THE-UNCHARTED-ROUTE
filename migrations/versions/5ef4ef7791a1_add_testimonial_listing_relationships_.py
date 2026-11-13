"""Add testimonial listing relationships and taxonomy and safari booking.

Revision ID: 5ef4ef7791a1
Revises: 5a6470af7062
Create Date: 2026-10-25 02:43:31.429007

This migration is intentionally idempotent because some tables and columns
may already exist when the application has created its SQLAlchemy metadata
before Alembic has advanced its revision.
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "5ef4ef7791a1"
down_revision = "5a6470af7062"
branch_labels = None
depends_on = None


def _inspector():
    """Return a fresh inspector reflecting the current database schema."""
    return sa.inspect(op.get_bind())


def _table_exists(table_name):
    return _inspector().has_table(table_name)


def _column_exists(table_name, column_name):
    if not _table_exists(table_name):
        return False

    return any(
        column["name"] == column_name
        for column in _inspector().get_columns(table_name)
    )


def _index_exists(table_name, index_name):
    if not _table_exists(table_name):
        return False

    return any(
        index["name"] == index_name
        for index in _inspector().get_indexes(table_name)
    )


def _foreign_key_exists(table_name, columns, referred_table):
    """Check by columns and target table, including unnamed SQLite FKs."""
    if not _table_exists(table_name):
        return False

    expected_columns = list(columns)

    for foreign_key in _inspector().get_foreign_keys(table_name):
        if (
            foreign_key.get("constrained_columns") == expected_columns
            and foreign_key.get("referred_table") == referred_table
        ):
            return True

    return False


def _create_index_if_missing(table_name, index_name, columns, unique=False):
    if not _index_exists(table_name, index_name):
        op.create_index(
            index_name,
            table_name,
            columns,
            unique=unique,
        )


def _create_taxonomy_tables():
    """Create taxonomy tables only when they do not already exist."""

    if not _table_exists("testimonial_categories"):
        op.create_table(
            "testimonial_categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.Column("display_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )

    if not _table_exists("testimonial_tags"):
        op.create_table(
            "testimonial_tags",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("slug", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=300), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )

    _create_index_if_missing(
        "testimonial_categories",
        "ix_testimonial_categories_active",
        ["active"],
    )
    _create_index_if_missing(
        "testimonial_categories",
        "ix_testimonial_categories_slug",
        ["slug"],
        unique=True,
    )
    _create_index_if_missing(
        "testimonial_tags",
        "ix_testimonial_tags_active",
        ["active"],
    )
    _create_index_if_missing(
        "testimonial_tags",
        "ix_testimonial_tags_slug",
        ["slug"],
        unique=True,
    )


def _create_assignment_tables():
    """Create many-to-many tables only if absent."""

    if not _table_exists("testimonial_category_assignments"):
        op.create_table(
            "testimonial_category_assignments",
            sa.Column("testimonial_id", sa.Integer(), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["category_id"],
                ["testimonial_categories.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["testimonial_id"],
                ["testimonials.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("testimonial_id", "category_id"),
        )

    if not _table_exists("testimonial_tag_assignments"):
        op.create_table(
            "testimonial_tag_assignments",
            sa.Column("testimonial_id", sa.Integer(), nullable=False),
            sa.Column("tag_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["tag_id"],
                ["testimonial_tags.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["testimonial_id"],
                ["testimonials.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("testimonial_id", "tag_id"),
        )


def _create_safari_bookings_table():
    """Create safari booking records only when the table is absent."""

    if _table_exists("safari_bookings"):
        return

    op.create_table(
        "safari_bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("destination_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("package_option_id", sa.Integer(), nullable=True),
        sa.Column("rate_id", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("duration_nights", sa.Integer(), nullable=False),
        sa.Column("destination_name", sa.String(length=150), nullable=False),
        sa.Column("property_name", sa.String(length=200), nullable=False),
        sa.Column("package_name", sa.String(length=200), nullable=False),
        sa.Column("rate_name", sa.String(length=180), nullable=True),
        sa.Column("pricing_basis", sa.String(length=40), nullable=True),
        sa.Column("season_name", sa.String(length=100), nullable=True),
        sa.Column("occupancy_type", sa.String(length=20), nullable=True),
        sa.Column("rate_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("rate_currency", sa.String(length=3), nullable=True),
        sa.Column("board_basis", sa.String(length=60), nullable=True),
        sa.Column("children_ages", sa.String(length=200), nullable=True),
        sa.Column("special_requests", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "duration_days >= 1",
            name="ck_safari_booking_duration_days",
        ),
        sa.CheckConstraint(
            "duration_nights >= 0",
            name="ck_safari_booking_duration_nights",
        ),
        sa.CheckConstraint(
            "end_date >= start_date",
            name="ck_safari_booking_dates",
        ),
        sa.CheckConstraint(
            "rate_amount IS NULL OR rate_amount >= 0",
            name="ck_safari_booking_rate_amount",
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["booking.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["destination_id"],
            ["safari_destinations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["package_option_id"],
            ["safari_package_options.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["safari_properties.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["rate_id"],
            ["safari_package_rates.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def _ensure_safari_booking_indexes():
    indexes = [
        ("ix_safari_bookings_booking_id", ["booking_id"], True),
        ("ix_safari_bookings_destination_id", ["destination_id"], False),
        ("ix_safari_bookings_end_date", ["end_date"], False),
        ("ix_safari_bookings_package_option_id", ["package_option_id"], False),
        ("ix_safari_bookings_property_id", ["property_id"], False),
        ("ix_safari_bookings_rate_id", ["rate_id"], False),
        ("ix_safari_bookings_start_date", ["start_date"], False),
    ]

    for index_name, columns, unique in indexes:
        _create_index_if_missing(
            "safari_bookings",
            index_name,
            columns,
            unique=unique,
        )


def _ensure_testimonial_columns():
    """Add missing testimonial listing/media columns without duplicating them."""

    if not _table_exists("testimonials"):
        raise RuntimeError(
            "The testimonials table does not exist. "
            "Check the earlier database migrations before proceeding."
        )

    new_columns = [
        ("stay_id", sa.Integer()),
        ("safari_package_option_id", sa.Integer()),
        ("profile_photo_asset_id", sa.Integer()),
        ("customer_photo_asset_id", sa.Integer()),
    ]

    missing_columns = [
        (name, column_type)
        for name, column_type in new_columns
        if not _column_exists("testimonials", name)
    ]

    if missing_columns:
        with op.batch_alter_table("testimonials") as batch_op:
            for name, column_type in missing_columns:
                batch_op.add_column(
                    sa.Column(name, column_type, nullable=True)
                )

    # Create each foreign key only if it does not already exist.
    foreign_keys = [
        (
            "fk_testimonials_stay",
            ["stay_id"],
            "stays",
            "id",
        ),
        (
            "fk_testimonials_safari_package_option",
            ["safari_package_option_id"],
            "safari_package_options",
            "id",
        ),
        (
            "fk_testimonials_profile_photo_asset",
            ["profile_photo_asset_id"],
            "media_assets",
            "id",
        ),
        (
            "fk_testimonials_customer_photo_asset",
            ["customer_photo_asset_id"],
            "media_assets",
            "id",
        ),
    ]

    missing_foreign_keys = [
        (name, columns, referred_table, referred_column)
        for name, columns, referred_table, referred_column in foreign_keys
        if not _foreign_key_exists(
            "testimonials",
            columns,
            referred_table,
        )
    ]

    if missing_foreign_keys:
        with op.batch_alter_table("testimonials") as batch_op:
            for name, columns, referred_table, referred_column in (
                missing_foreign_keys
            ):
                batch_op.create_foreign_key(
                    name,
                    referred_table,
                    columns,
                    [referred_column],
                    ondelete="SET NULL",
                )


def upgrade():
    # Ensure prerequisite taxonomy and assignment tables exist.
    _create_taxonomy_tables()
    _create_assignment_tables()

    # Ensure safari booking storage and its indexes exist.
    _create_safari_bookings_table()
    _ensure_safari_booking_indexes()

    # Add only missing testimonial columns and foreign keys.
    _ensure_testimonial_columns()


def downgrade():
    """
    Intentionally non-destructive.

    Some objects covered by this revision already existed while Alembic
    still reported the previous revision. Dropping them here could destroy
    pre-existing taxonomy, safari-booking, or testimonial data.

    If a rollback is genuinely required, first back up the database and
    inspect which objects were introduced by this revision before removing
    them manually.
    """
    pass
