"""
Complete CMS and administrative modules

Revision ID: 97ca297b6f19
Revises: f72c3ff385e6
Create Date: 2026-09-06 21:29:23.703276

This migration has been manually adjusted because several CMS and
administrative tables already existed in the database before Alembic
recorded this revision.

The migration therefore:

- Does NOT recreate existing tables.
- Does NOT attempt to drop experience_availability because it is already gone.
- Completes the remaining schema changes.
- Uses SQLite-safe batch operations.
- Handles pre-existing unnamed foreign keys safely.
- Avoids duplicate foreign-key creation.
- Uses explicit foreign-key names where necessary.
- Preserves existing CMS/administrative tables during downgrade.
"""

from alembic import op
import sqlalchemy as sa

# =============================================================================
# Revision identifiers
# =============================================================================
revision = "97ca297b6f19"
down_revision = "f72c3ff385e6"
branch_labels = None
depends_on = None

# =============================================================================
# Helpers
# =============================================================================

def _inspector():
    """Return a SQLAlchemy inspector for the current database."""
    return sa.inspect(op.get_bind())


def _table_exists(table_name):
    """Return True when a table exists in the current database."""
    return table_name in _inspector().get_table_names()


def _column_exists(table_name, column_name):
    """Return True when a column exists on a table."""
    if not _table_exists(table_name):
        return False

    return any(
        column["name"] == column_name
        for column in _inspector().get_columns(table_name)
    )


def _index_exists(table_name, index_name):
    """Return True when an index exists on a table."""
    if not _table_exists(table_name):
        return False

    return any(
        index["name"] == index_name
        for index in _inspector().get_indexes(table_name)
    )


def _foreign_key_exists(
    table_name,
    constrained_columns,
    referred_table,
):
    """
    Return True when a foreign key exists for the specified columns and
    referred table.

    This deliberately checks the actual relationship rather than relying
    on the constraint name because SQLite may report legacy constraints
    as unnamed.
    """
    if not _table_exists(table_name):
        return False

    constrained_columns = list(constrained_columns)

    for foreign_key in _inspector().get_foreign_keys(table_name):
        if (
            foreign_key.get("referred_table") == referred_table
            and list(foreign_key.get("constrained_columns") or [])
            == constrained_columns
        ):
            return True

    return False


# =============================================================================
# Upgrade
# =============================================================================

def upgrade():
    """
    Complete the schema changes introduced by this revision.

    Existing CMS/admin tables are intentionally not recreated because they
    already exist in the current database.
    """

    # =========================================================================
    # 1. REMOVE ABANDONED ALEMBIC TEMP TABLE
    # =========================================================================

    # This table was created by a failed SQLite batch migration.
    #
    # It was inspected and confirmed to contain zero rows.
    #
    # It is safe to remove before the real migration proceeds.
    if _table_exists("_alembic_tmp_blog_categories"):
        op.drop_table("_alembic_tmp_blog_categories")

    # =========================================================================
    # 2. EXPERIENCE AVAILABILITY
    # =========================================================================

    # The experience_availability table is already absent from the database.
    #
    # We intentionally do NOT execute:
    #
    #     op.drop_table("experience_availability")
    #
    # because doing so would fail with:
    #
    #     no such table: experience_availability
    #
    # Nothing is required here.

    # =========================================================================
    # 3. BLOG CATEGORIES
    # =========================================================================

    if _table_exists("blog_categories"):

        # The existing table was inspected and confirmed to contain zero rows,
        # so changing color from nullable to NOT NULL is safe.
        with op.batch_alter_table(
            "blog_categories",
            schema=None,
        ) as batch_op:

            # -----------------------------------------------------------------
            # color -> NOT NULL
            # -----------------------------------------------------------------

            if _column_exists("blog_categories", "color"):
                batch_op.alter_column(
                    "color",
                    existing_type=sa.VARCHAR(length=20),
                    nullable=False,
                )

            # -----------------------------------------------------------------
            # Indexes
            # -----------------------------------------------------------------

            if not _index_exists(
                "blog_categories",
                "ix_blog_categories_active",
            ):
                batch_op.create_index(
                    "ix_blog_categories_active",
                    ["active"],
                    unique=False,
                )

            if not _index_exists(
                "blog_categories",
                "ix_blog_categories_created_at",
            ):
                batch_op.create_index(
                    "ix_blog_categories_created_at",
                    ["created_at"],
                    unique=False,
                )

            if not _index_exists(
                "blog_categories",
                "ix_blog_categories_featured",
            ):
                batch_op.create_index(
                    "ix_blog_categories_featured",
                    ["featured"],
                    unique=False,
                )

            if not _index_exists(
                "blog_categories",
                "ix_blog_categories_sort_order",
            ):
                batch_op.create_index(
                    "ix_blog_categories_sort_order",
                    ["sort_order"],
                    unique=False,
                )

    # =========================================================================
    # 4. BLOG POSTS
    # =========================================================================

    if _table_exists("blog_posts"):

        # ---------------------------------------------------------------------
        # Inspect existing foreign keys BEFORE entering batch mode.
        #
        # The current SQLite database contains unnamed foreign keys for:
        #
        #   category_id              -> blog_categories.id
        #   related_destination_id   -> destinations.id
        #   related_experience_id    -> experiences.id
        #
        # We determine whether the relationships already exist by their
        # columns/tables rather than relying on their constraint names.
        # ---------------------------------------------------------------------

        has_category_fk = _foreign_key_exists(
            "blog_posts",
            ["category_id"],
            "blog_categories",
        )

        has_destination_fk = _foreign_key_exists(
            "blog_posts",
            ["related_destination_id"],
            "destinations",
        )

        has_experience_fk = _foreign_key_exists(
            "blog_posts",
            ["related_experience_id"],
            "experiences",
        )

        with op.batch_alter_table(
            "blog_posts",
            schema=None,
            naming_convention={
                "fk": (
                    "fk_%(table_name)s_%(column_0_name)s_"
                    "%(referred_table_name)s"
                )
            },
        ) as batch_op:

            # -------------------------------------------------------------
            # reading_time -> NOT NULL
            # word_count -> NOT NULL
            #
            # We already checked the database and confirmed:
            #
            # reading_time NULL count = 0
            # word_count NULL count   = 0
            #
            # Therefore these changes require no data cleanup.
            # -------------------------------------------------------------

            if _column_exists("blog_posts", "reading_time"):
                batch_op.alter_column(
                    "reading_time",
                    existing_type=sa.INTEGER(),
                    nullable=False,
                )

            if _column_exists("blog_posts", "word_count"):
                batch_op.alter_column(
                    "word_count",
                    existing_type=sa.INTEGER(),
                    nullable=False,
                )

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_created_at",
            ):
                batch_op.create_index(
                    "ix_blog_posts_created_at",
                    ["created_at"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_featured",
            ):
                batch_op.create_index(
                    "ix_blog_posts_featured",
                    ["featured"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_pinned",
            ):
                batch_op.create_index(
                    "ix_blog_posts_pinned",
                    ["pinned"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_published_at",
            ):
                batch_op.create_index(
                    "ix_blog_posts_published_at",
                    ["published_at"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_related_destination_id",
            ):
                batch_op.create_index(
                    "ix_blog_posts_related_destination_id",
                    ["related_destination_id"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_related_experience_id",
            ):
                batch_op.create_index(
                    "ix_blog_posts_related_experience_id",
                    ["related_experience_id"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_scheduled_for",
            ):
                batch_op.create_index(
                    "ix_blog_posts_scheduled_for",
                    ["scheduled_for"],
                    unique=False,
                )

            if not _index_exists(
                "blog_posts",
                "ix_blog_posts_status",
            ):
                batch_op.create_index(
                    "ix_blog_posts_status",
                    ["status"],
                    unique=False,
                )

            # -------------------------------------------------------------
            # Foreign keys
            # -------------------------------------------------------------
            #
            # IMPORTANT:
            #
            # The original database contains these relationships already,
            # but SQLite reports their names as None.
            #
            # Because naming_convention is supplied above, Alembic can assign
            # deterministic names to reflected unnamed constraints during
            # the batch rebuild.
            #
            # We therefore only drop an existing relationship when it exists,
            # and only create the desired relationship when it does not.
            #
            # This prevents duplicate foreign keys.
            # -------------------------------------------------------------

            if has_experience_fk:
                batch_op.drop_constraint(
                    "fk_blog_posts_related_experience_id_experiences",
                    type_="foreignkey",
                )

            if has_destination_fk:
                batch_op.drop_constraint(
                    "fk_blog_posts_related_destination_id_destinations",
                    type_="foreignkey",
                )

            if has_category_fk:
                batch_op.drop_constraint(
                    "fk_blog_posts_category_id_blog_categories",
                    type_="foreignkey",
                )

            # Recreate each relationship with the desired ON DELETE action.

            batch_op.create_foreign_key(
                "fk_blog_posts_related_experience_id_experiences",
                "experiences",
                ["related_experience_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_blog_posts_related_destination_id_destinations",
                "destinations",
                ["related_destination_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_blog_posts_category_id_blog_categories",
                "blog_categories",
                ["category_id"],
                ["id"],
                ondelete="RESTRICT",
            )

    # =========================================================================
    # 5. BOOKINGS
    # =========================================================================

    if _table_exists("booking"):

        # We already inspected the database and confirmed that none of the
        # seven financial columns contain NULL values.
        #
        # Therefore no UPDATE/COALESCE cleanup is necessary.

        with op.batch_alter_table(
            "booking",
            schema=None,
        ) as batch_op:

            # -------------------------------------------------------------
            # Financial columns -> NOT NULL
            # -------------------------------------------------------------

            financial_columns = [
                "subtotal",
                "discount_amount",
                "tax_amount",
                "addon_total",
                "total_amount",
                "amount_paid",
                "balance_due",
            ]

            for column_name in financial_columns:
                if _column_exists("booking", column_name):
                    batch_op.alter_column(
                        column_name,
                        existing_type=sa.NUMERIC(
                            precision=12,
                            scale=2,
                        ),
                        nullable=False,
                    )

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            booking_indexes = {
                "ix_bookings_active": ["active"],
                "ix_bookings_booking_date": ["booking_date"],
                "ix_bookings_booking_uuid": ["booking_uuid"],
                "ix_bookings_experience_date": ["experience_date"],
                "ix_bookings_experience_id": ["experience_id"],
                "ix_bookings_pricing_id": ["pricing_id"],
                "ix_bookings_schedule_id": ["schedule_id"],
                "ix_bookings_status": ["status"],
            }

            for index_name, columns in booking_indexes.items():

                if not _index_exists(
                    "booking",
                    index_name,
                ):
                    batch_op.create_index(
                        index_name,
                        columns,
                        unique=(
                            index_name
                            == "ix_bookings_booking_uuid"
                        ),
                    )

    # =========================================================================
    # 6. CONTACTS
    # =========================================================================

    if _table_exists("contacts"):

        # Inspect the existing relationships before adding anything.
        #
        # The current contacts table has none of the new user-related
        # foreign keys, but this makes the migration safer if it is ever
        # encountered in a partially upgraded state.

        has_resolved_by_fk = _foreign_key_exists(
            "contacts",
            ["resolved_by_id"],
            "users",
        )

        has_closed_by_fk = _foreign_key_exists(
            "contacts",
            ["closed_by_id"],
            "users",
        )

        has_archived_by_fk = _foreign_key_exists(
            "contacts",
            ["archived_by_id"],
            "users",
        )

        has_user_fk = _foreign_key_exists(
            "contacts",
            ["user_id"],
            "users",
        )

        has_assigned_user_fk = _foreign_key_exists(
            "contacts",
            ["assigned_user_id"],
            "users",
        )

        with op.batch_alter_table(
            "contacts",
            schema=None,
            naming_convention={
                "fk": (
                    "fk_%(table_name)s_%(column_0_name)s_"
                    "%(referred_table_name)s"
                )
            },
        ) as batch_op:

            # -------------------------------------------------------------
            # New columns
            # -------------------------------------------------------------

            if not _column_exists("contacts", "user_id"):
                batch_op.add_column(
                    sa.Column(
                        "user_id",
                        sa.Integer(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "assigned_user_id"):
                batch_op.add_column(
                    sa.Column(
                        "assigned_user_id",
                        sa.Integer(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "is_read"):
                batch_op.add_column(
                    sa.Column(
                        "is_read",
                        sa.Boolean(),
                        server_default=sa.text("0"),
                        nullable=False,
                    )
                )

            if not _column_exists("contacts", "read_at"):
                batch_op.add_column(
                    sa.Column(
                        "read_at",
                        sa.DateTime(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "first_response_at"):
                batch_op.add_column(
                    sa.Column(
                        "first_response_at",
                        sa.DateTime(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "last_response_at"):
                batch_op.add_column(
                    sa.Column(
                        "last_response_at",
                        sa.DateTime(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "resolved_by_id"):
                batch_op.add_column(
                    sa.Column(
                        "resolved_by_id",
                        sa.Integer(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "closed_at"):
                batch_op.add_column(
                    sa.Column(
                        "closed_at",
                        sa.DateTime(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "closed_by_id"):
                batch_op.add_column(
                    sa.Column(
                        "closed_by_id",
                        sa.Integer(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "is_archived"):
                batch_op.add_column(
                    sa.Column(
                        "is_archived",
                        sa.Boolean(),
                        server_default=sa.text("0"),
                        nullable=False,
                    )
                )

            if not _column_exists("contacts", "archived_at"):
                batch_op.add_column(
                    sa.Column(
                        "archived_at",
                        sa.DateTime(),
                        nullable=True,
                    )
                )

            if not _column_exists("contacts", "archived_by_id"):
                batch_op.add_column(
                    sa.Column(
                        "archived_by_id",
                        sa.Integer(),
                        nullable=True,
                    )
                )

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            contact_indexes = {
                "ix_contacts_archived_by_id": ["archived_by_id"],
                "ix_contacts_assigned_user_id": ["assigned_user_id"],
                "ix_contacts_closed_by_id": ["closed_by_id"],
                "ix_contacts_created_at": ["created_at"],
                "ix_contacts_department": ["department"],
                "ix_contacts_enquiry_type": ["enquiry_type"],
                "ix_contacts_follow_up_date": ["follow_up_date"],
                "ix_contacts_is_archived": ["is_archived"],
                "ix_contacts_is_read": ["is_read"],
                "ix_contacts_priority": ["priority"],
                "ix_contacts_resolved_by_id": ["resolved_by_id"],
                "ix_contacts_source": ["source"],
                "ix_contacts_status": ["status"],
                "ix_contacts_user_id": ["user_id"],
            }

            for index_name, columns in contact_indexes.items():

                if not _index_exists(
                    "contacts",
                    index_name,
                ):
                    batch_op.create_index(
                        index_name,
                        columns,
                        unique=False,
                    )

            # -------------------------------------------------------------
            # Foreign keys
            # -------------------------------------------------------------
            #
            # These are deliberately created based on the pre-existing FK
            # state. The corresponding columns may have just been added above;
            # that is valid because Alembic's batch operation reconstructs the
            # table as a whole.
            # -------------------------------------------------------------

            if has_resolved_by_fk:
                batch_op.drop_constraint(
                    "fk_contacts_resolved_by_id_users",
                    type_="foreignkey",
                )

            if has_closed_by_fk:
                batch_op.drop_constraint(
                    "fk_contacts_closed_by_id_users",
                    type_="foreignkey",
                )

            if has_archived_by_fk:
                batch_op.drop_constraint(
                    "fk_contacts_archived_by_id_users",
                    type_="foreignkey",
                )

            if has_user_fk:
                batch_op.drop_constraint(
                    "fk_contacts_user_id_users",
                    type_="foreignkey",
                )

            if has_assigned_user_fk:
                batch_op.drop_constraint(
                    "fk_contacts_assigned_user_id_users",
                    type_="foreignkey",
                )

            # Create the desired relationships.

            batch_op.create_foreign_key(
                "fk_contacts_resolved_by_id_users",
                "users",
                ["resolved_by_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_contacts_closed_by_id_users",
                "users",
                ["closed_by_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_contacts_archived_by_id_users",
                "users",
                ["archived_by_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_contacts_user_id_users",
                "users",
                ["user_id"],
                ["id"],
                ondelete="SET NULL",
            )

            batch_op.create_foreign_key(
                "fk_contacts_assigned_user_id_users",
                "users",
                ["assigned_user_id"],
                ["id"],
                ondelete="SET NULL",
            )

    # =========================================================================
    # 7. EXPERIENCE SCHEDULES
    # =========================================================================

    if _table_exists("experience_schedules"):

        # We already inspected the database and confirmed:
        #
        # experience_schedules NULL currency = 0
        #
        # Therefore the NOT NULL change is safe without a data update.

        with op.batch_alter_table(
            "experience_schedules",
            schema=None,
        ) as batch_op:

            # -------------------------------------------------------------
            # currency -> NOT NULL
            # -------------------------------------------------------------

            if _column_exists(
                "experience_schedules",
                "currency",
            ):
                batch_op.alter_column(
                    "currency",
                    existing_type=sa.VARCHAR(length=10),
                    nullable=False,
                )

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            if not _index_exists(
                "experience_schedules",
                "ix_experience_schedules_active",
            ):
                batch_op.create_index(
                    "ix_experience_schedules_active",
                    ["active"],
                    unique=False,
                )

            if not _index_exists(
                "experience_schedules",
                "ix_experience_schedules_status",
            ):
                batch_op.create_index(
                    "ix_experience_schedules_status",
                    ["status"],
                    unique=False,
                )


# =============================================================================
# Downgrade
# =============================================================================

def downgrade():
    """
    Reverse the schema changes introduced by this migration.

    Existing CMS/admin tables are NOT dropped because they predated this
    migration in the physical database and are therefore not owned by this
    revision's upgrade operation.

    The downgrade only reverses the changes this reconciliation migration
    applied to those pre-existing tables.
    """

    # =========================================================================
    # 1. EXPERIENCE SCHEDULES
    # =========================================================================

    if _table_exists("experience_schedules"):

        with op.batch_alter_table(
            "experience_schedules",
            schema=None,
        ) as batch_op:

            if _index_exists(
                "experience_schedules",
                "ix_experience_schedules_status",
            ):
                batch_op.drop_index(
                    "ix_experience_schedules_status"
                )

            if _index_exists(
                "experience_schedules",
                "ix_experience_schedules_active",
            ):
                batch_op.drop_index(
                    "ix_experience_schedules_active"
                )

            if _column_exists(
                "experience_schedules",
                "currency",
            ):
                batch_op.alter_column(
                    "currency",
                    existing_type=sa.VARCHAR(length=10),
                    nullable=True,
                )

    # =========================================================================
    # 2. CONTACTS
    # =========================================================================

    if _table_exists("contacts"):

        with op.batch_alter_table(
            "contacts",
            schema=None,
            naming_convention={
                "fk": (
                    "fk_%(table_name)s_%(column_0_name)s_"
                    "%(referred_table_name)s"
                )
            },
        ) as batch_op:

            # -------------------------------------------------------------
            # Foreign keys
            # -------------------------------------------------------------

            for constraint_name in [
                "fk_contacts_assigned_user_id_users",
                "fk_contacts_user_id_users",
                "fk_contacts_archived_by_id_users",
                "fk_contacts_closed_by_id_users",
                "fk_contacts_resolved_by_id_users",
            ]:

                try:
                    batch_op.drop_constraint(
                        constraint_name,
                        type_="foreignkey",
                    )
                except Exception:
                    pass

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            contact_indexes = [
                "ix_contacts_user_id",
                "ix_contacts_status",
                "ix_contacts_source",
                "ix_contacts_resolved_by_id",
                "ix_contacts_priority",
                "ix_contacts_is_read",
                "ix_contacts_is_archived",
                "ix_contacts_follow_up_date",
                "ix_contacts_enquiry_type",
                "ix_contacts_department",
                "ix_contacts_created_at",
                "ix_contacts_closed_by_id",
                "ix_contacts_assigned_user_id",
                "ix_contacts_archived_by_id",
            ]

            for index_name in contact_indexes:

                if _index_exists(
                    "contacts",
                    index_name,
                ):
                    batch_op.drop_index(index_name)

            # -------------------------------------------------------------
            # Columns
            # -------------------------------------------------------------

            for column_name in [
                "archived_by_id",
                "archived_at",
                "is_archived",
                "closed_by_id",
                "closed_at",
                "resolved_by_id",
                "last_response_at",
                "first_response_at",
                "read_at",
                "is_read",
                "assigned_user_id",
                "user_id",
            ]:

                if _column_exists(
                    "contacts",
                    column_name,
                ):
                    batch_op.drop_column(column_name)

    # =========================================================================
    # 3. BOOKINGS
    # =========================================================================

    if _table_exists("booking"):

        with op.batch_alter_table(
            "booking",
            schema=None,
        ) as batch_op:

            booking_indexes = [
                "ix_bookings_status",
                "ix_bookings_schedule_id",
                "ix_bookings_pricing_id",
                "ix_bookings_experience_id",
                "ix_bookings_experience_date",
                "ix_bookings_booking_uuid",
                "ix_bookings_booking_date",
                "ix_bookings_active",
            ]

            for index_name in booking_indexes:

                if _index_exists(
                    "booking",
                    index_name,
                ):
                    batch_op.drop_index(index_name)

            for column_name in [
                "balance_due",
                "amount_paid",
                "total_amount",
                "addon_total",
                "tax_amount",
                "discount_amount",
                "subtotal",
            ]:

                if _column_exists(
                    "booking",
                    column_name,
                ):
                    batch_op.alter_column(
                        column_name,
                        existing_type=sa.NUMERIC(
                            precision=12,
                            scale=2,
                        ),
                        nullable=True,
                    )

    # =========================================================================
    # 4. BLOG POSTS
    # =========================================================================

    if _table_exists("blog_posts"):

        with op.batch_alter_table(
            "blog_posts",
            schema=None,
            naming_convention={
                "fk": (
                    "fk_%(table_name)s_%(column_0_name)s_"
                    "%(referred_table_name)s"
                )
            },
        ) as batch_op:

            # -------------------------------------------------------------
            # Foreign keys
            # -------------------------------------------------------------

            for constraint_name in [
                "fk_blog_posts_related_experience_id_experiences",
                "fk_blog_posts_related_destination_id_destinations",
                "fk_blog_posts_category_id_blog_categories",
            ]:

                try:
                    batch_op.drop_constraint(
                        constraint_name,
                        type_="foreignkey",
                    )
                except Exception:
                    pass

            # -------------------------------------------------------------
            # Indexes
            # -------------------------------------------------------------

            for index_name in [
                "ix_blog_posts_status",
                "ix_blog_posts_scheduled_for",
                "ix_blog_posts_related_experience_id",
                "ix_blog_posts_related_destination_id",
                "ix_blog_posts_published_at",
                "ix_blog_posts_pinned",
                "ix_blog_posts_featured",
                "ix_blog_posts_created_at",
            ]:

                if _index_exists(
                    "blog_posts",
                    index_name,
                ):
                    batch_op.drop_index(index_name)

            # -------------------------------------------------------------
            # Columns
            # -------------------------------------------------------------

            if _column_exists(
                "blog_posts",
                "word_count",
            ):
                batch_op.alter_column(
                    "word_count",
                    existing_type=sa.INTEGER(),
                    nullable=True,
                )

            if _column_exists(
                "blog_posts",
                "reading_time",
            ):
                batch_op.alter_column(
                    "reading_time",
                    existing_type=sa.INTEGER(),
                    nullable=True,
                )

    # =========================================================================
    # 5. BLOG CATEGORIES
    # =========================================================================

    if _table_exists("blog_categories"):

        with op.batch_alter_table(
            "blog_categories",
            schema=None,
        ) as batch_op:

            for index_name in [
                "ix_blog_categories_sort_order",
                "ix_blog_categories_featured",
                "ix_blog_categories_created_at",
                "ix_blog_categories_active",
            ]:

                if _index_exists(
                    "blog_categories",
                    index_name,
                ):
                    batch_op.drop_index(index_name)

            if _column_exists(
                "blog_categories",
                "color",
            ):
                batch_op.alter_column(
                    "color",
                    existing_type=sa.VARCHAR(length=20),
                    nullable=True,
                )

    # =========================================================================
    # IMPORTANT
    # =========================================================================
    #
    # We intentionally do NOT:
    #
    #   - recreate experience_availability
    #   - drop staff
    #   - drop staff_assignments
    #   - drop staff_schedules
    #   - drop staff_availability
    #   - drop contact_notes
    #   - drop contact_replies
    #   - drop homepage_sections
    #   - drop site_settings
    #   - drop homepages
    #
    # Those tables already existed physically before this migration was
    # recorded, so this revision does not own their lifecycle.