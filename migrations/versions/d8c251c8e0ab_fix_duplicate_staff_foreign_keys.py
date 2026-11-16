"""Fix duplicate staff foreign keys

Revision ID: d8c251c8e0ab
Revises: 068608e7ce3a
Create Date: 2026-11-12
"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d8c251c8e0ab"
down_revision = "068608e7ce3a"
branch_labels = None
depends_on = None


def _execute(sql):
    """Execute raw SQL against the current Alembic connection."""
    op.get_bind().exec_driver_sql(sql)


def _rebuild_staff_assignments():
    """
    Rebuild staff_assignments with exactly one foreign key per relationship.

    The previous database contained duplicate unnamed foreign keys on:
        booking_id
        staff_id

    This rebuild intentionally avoids SQLAlchemy reflection.
    """

    _execute(
        """
        CREATE TABLE "_staff_assignments_new" (
            id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            booking_id INTEGER NOT NULL,
            role VARCHAR(40) NOT NULL,
            status VARCHAR(30) NOT NULL,
            assigned_at DATETIME NOT NULL,
            completed_at DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            starts_at DATETIME,
            ends_at DATETIME,
            assigned_by_user_id INTEGER,
            responded_at DATETIME,
            started_at DATETIME,
            cancelled_at DATETIME,
            response_notes TEXT,
            internal_notes TEXT,
            cancellation_reason TEXT,
            staff_schedule_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(booking_id)
                REFERENCES bookings (id)
                ON DELETE CASCADE,
            FOREIGN KEY(assigned_by_user_id)
                REFERENCES users (id)
                ON DELETE SET NULL,
            FOREIGN KEY(staff_schedule_id)
                REFERENCES staff_schedules (id)
                ON DELETE SET NULL,
            FOREIGN KEY(staff_id)
                REFERENCES staff (id)
                ON DELETE RESTRICT
        )
        """
    )

    _execute(
        """
        INSERT INTO "_staff_assignments_new" (
            id,
            staff_id,
            booking_id,
            role,
            status,
            assigned_at,
            completed_at,
            created_at,
            updated_at,
            starts_at,
            ends_at,
            assigned_by_user_id,
            responded_at,
            started_at,
            cancelled_at,
            response_notes,
            internal_notes,
            cancellation_reason,
            staff_schedule_id
        )
        SELECT
            id,
            staff_id,
            booking_id,
            role,
            status,
            assigned_at,
            completed_at,
            created_at,
            updated_at,
            starts_at,
            ends_at,
            assigned_by_user_id,
            responded_at,
            started_at,
            cancelled_at,
            response_notes,
            internal_notes,
            cancellation_reason,
            staff_schedule_id
        FROM staff_assignments
        """
    )

    _execute("DROP TABLE staff_assignments")
    _execute(
        'ALTER TABLE "_staff_assignments_new" '
        'RENAME TO "staff_assignments"'
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_staff_schedule_id
        ON staff_assignments (staff_schedule_id)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_booking_id
        ON staff_assignments (booking_id)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_status
        ON staff_assignments (status)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_staff_id
        ON staff_assignments (staff_id)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_starts_at
        ON staff_assignments (starts_at)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_assignments_role
        ON staff_assignments (role)
        """
    )


def _rebuild_staff_availability():
    """
    Rebuild staff_availability with exactly one staff FK.

    The previous database contained an additional duplicate:
        staff_id -> staff.id ON DELETE NO ACTION

    The model-defined relationship is:
        staff_id -> staff.id ON DELETE CASCADE
    """

    _execute(
        """
        CREATE TABLE "_staff_availability_new" (
            id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            status VARCHAR(30) NOT NULL,
            reason VARCHAR(255),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            starts_at DATETIME NOT NULL,
            ends_at DATETIME NOT NULL,
            notes TEXT,
            all_day BOOLEAN NOT NULL,
            recurring BOOLEAN NOT NULL,
            recurrence_rule VARCHAR(255),
            created_by_user_id INTEGER,
            reviewed_by_user_id INTEGER,
            reviewed_at DATETIME,
            review_notes TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY(reviewed_by_user_id)
                REFERENCES users (id)
                ON DELETE SET NULL,
            FOREIGN KEY(created_by_user_id)
                REFERENCES users (id)
                ON DELETE SET NULL,
            FOREIGN KEY(staff_id)
                REFERENCES staff (id)
                ON DELETE CASCADE
        )
        """
    )

    _execute(
        """
        INSERT INTO "_staff_availability_new" (
            id,
            staff_id,
            status,
            reason,
            created_at,
            updated_at,
            starts_at,
            ends_at,
            notes,
            all_day,
            recurring,
            recurrence_rule,
            created_by_user_id,
            reviewed_by_user_id,
            reviewed_at,
            review_notes
        )
        SELECT
            id,
            staff_id,
            status,
            reason,
            created_at,
            updated_at,
            starts_at,
            ends_at,
            notes,
            all_day,
            recurring,
            recurrence_rule,
            created_by_user_id,
            reviewed_by_user_id,
            reviewed_at,
            review_notes
        FROM staff_availability
        """
    )

    _execute("DROP TABLE staff_availability")
    _execute(
        'ALTER TABLE "_staff_availability_new" '
        'RENAME TO "staff_availability"'
    )

    _execute(
        """
        CREATE INDEX ix_staff_availability_starts_at
        ON staff_availability (starts_at)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_availability_staff_id
        ON staff_availability (staff_id)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_availability_ends_at
        ON staff_availability (ends_at)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_availability_status
        ON staff_availability (status)
        """
    )


def _rebuild_staff_schedules():
    """
    Rebuild staff_schedules with exactly one staff FK.

    The previous database contained an additional duplicate:
        staff_id -> staff.id ON DELETE NO ACTION

    The model-defined relationship is:
        staff_id -> staff.id ON DELETE CASCADE
    """

    _execute(
        """
        CREATE TABLE "_staff_schedules_new" (
            id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            location VARCHAR(255),
            status VARCHAR(30) NOT NULL,
            notes TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            schedule_type VARCHAR(40) NOT NULL,
            starts_at DATETIME NOT NULL,
            ends_at DATETIME NOT NULL,
            timezone VARCHAR(64),
            task_id INTEGER,
            created_by_user_id INTEGER,
            confirmed_at DATETIME,
            started_at DATETIME,
            completed_at DATETIME,
            cancelled_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY(staff_id)
                REFERENCES staff (id)
                ON DELETE CASCADE,
            FOREIGN KEY(created_by_user_id)
                REFERENCES users (id)
                ON DELETE SET NULL,
            FOREIGN KEY(task_id)
                REFERENCES tasks (id)
                ON DELETE SET NULL
        )
        """
    )

    _execute(
        """
        INSERT INTO "_staff_schedules_new" (
            id,
            staff_id,
            title,
            description,
            location,
            status,
            notes,
            created_at,
            updated_at,
            schedule_type,
            starts_at,
            ends_at,
            timezone,
            task_id,
            created_by_user_id,
            confirmed_at,
            started_at,
            completed_at,
            cancelled_at
        )
        SELECT
            id,
            staff_id,
            title,
            description,
            location,
            status,
            notes,
            created_at,
            updated_at,
            schedule_type,
            starts_at,
            ends_at,
            timezone,
            task_id,
            created_by_user_id,
            confirmed_at,
            started_at,
            completed_at,
            cancelled_at
        FROM staff_schedules
        """
    )

    _execute("DROP TABLE staff_schedules")
    _execute(
        'ALTER TABLE "_staff_schedules_new" '
        'RENAME TO "staff_schedules"'
    )

    _execute(
        """
        CREATE INDEX ix_staff_schedules_status
        ON staff_schedules (status)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_schedules_starts_at
        ON staff_schedules (starts_at)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_schedules_ends_at
        ON staff_schedules (ends_at)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_schedules_task_id
        ON staff_schedules (task_id)
        """
    )

    _execute(
        """
        CREATE INDEX ix_staff_schedules_staff_id
        ON staff_schedules (staff_id)
        """
    )


def upgrade():
    """
    Replace the historically corrupted Staff FK definitions with the
    exact relationships declared by the current SQLAlchemy models.

    No SQLAlchemy reflection is used here.
    """

    bind = op.get_bind()

    # This migration repairs the historical SQLite staff FK schema only.
    # PostgreSQL does not need this SQLite-specific table rebuild.
    if bind.dialect.name != "sqlite":
        return

    # SQLite's table-rebuild workflow requires foreign-key enforcement
    # to be disabled while referenced tables are replaced.
    foreign_keys_enabled = bind.exec_driver_sql(
        "PRAGMA foreign_keys"
    ).scalar()

    if foreign_keys_enabled:
        bind.exec_driver_sql("PRAGMA foreign_keys=OFF")

    try:
        _rebuild_staff_assignments()
        _rebuild_staff_availability()
        _rebuild_staff_schedules()
    finally:
        if foreign_keys_enabled:
            bind.exec_driver_sql("PRAGMA foreign_keys=ON")


def downgrade():
    """
    Restore the exact duplicate-FK state that existed before this migration.

    This is intentionally implemented without reflection as well.
    """

    bind = op.get_bind()

    foreign_keys_enabled = bind.exec_driver_sql(
        "PRAGMA foreign_keys"
    ).scalar()

    if foreign_keys_enabled:
        bind.exec_driver_sql("PRAGMA foreign_keys=OFF")

    try:
        # --------------------------------------------------------------
        # staff_assignments
        # --------------------------------------------------------------

        _execute(
            """
            CREATE TABLE "_staff_assignments_old" (
                id INTEGER NOT NULL,
                staff_id INTEGER NOT NULL,
                booking_id INTEGER NOT NULL,
                role VARCHAR(40) NOT NULL,
                status VARCHAR(30) NOT NULL,
                assigned_at DATETIME NOT NULL,
                completed_at DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                starts_at DATETIME,
                ends_at DATETIME,
                assigned_by_user_id INTEGER,
                responded_at DATETIME,
                started_at DATETIME,
                cancelled_at DATETIME,
                response_notes TEXT,
                internal_notes TEXT,
                cancellation_reason TEXT,
                staff_schedule_id INTEGER,
                PRIMARY KEY (id),

                FOREIGN KEY(booking_id)
                    REFERENCES bookings (id)
                    ON DELETE CASCADE,

                FOREIGN KEY(assigned_by_user_id)
                    REFERENCES users (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(staff_schedule_id)
                    REFERENCES staff_schedules (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE RESTRICT,

                FOREIGN KEY(booking_id)
                    REFERENCES bookings (id)
                    ON DELETE NO ACTION,

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE NO ACTION
            )
            """
        )

        _execute(
            """
            INSERT INTO "_staff_assignments_old" (
                id,
                staff_id,
                booking_id,
                role,
                status,
                assigned_at,
                completed_at,
                created_at,
                updated_at,
                starts_at,
                ends_at,
                assigned_by_user_id,
                responded_at,
                started_at,
                cancelled_at,
                response_notes,
                internal_notes,
                cancellation_reason,
                staff_schedule_id
            )
            SELECT
                id,
                staff_id,
                booking_id,
                role,
                status,
                assigned_at,
                completed_at,
                created_at,
                updated_at,
                starts_at,
                ends_at,
                assigned_by_user_id,
                responded_at,
                started_at,
                cancelled_at,
                response_notes,
                internal_notes,
                cancellation_reason,
                staff_schedule_id
            FROM staff_assignments
            """
        )

        _execute("DROP TABLE staff_assignments")
        _execute(
            'ALTER TABLE "_staff_assignments_old" '
            'RENAME TO "staff_assignments"'
        )

        _execute(
            """
            CREATE INDEX ix_staff_assignments_staff_schedule_id
            ON staff_assignments (staff_schedule_id)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_assignments_booking_id
            ON staff_assignments (booking_id)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_assignments_status
            ON staff_assignments (status)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_assignments_staff_id
            ON staff_assignments (staff_id)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_assignments_starts_at
            ON staff_assignments (starts_at)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_assignments_role
            ON staff_assignments (role)
            """
        )

        # --------------------------------------------------------------
        # staff_availability
        # --------------------------------------------------------------

        _execute(
            """
            CREATE TABLE "_staff_availability_old" (
                id INTEGER NOT NULL,
                staff_id INTEGER NOT NULL,
                status VARCHAR(30) NOT NULL,
                reason VARCHAR(255),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                starts_at DATETIME NOT NULL,
                ends_at DATETIME NOT NULL,
                notes TEXT,
                all_day BOOLEAN NOT NULL,
                recurring BOOLEAN NOT NULL,
                recurrence_rule VARCHAR(255),
                created_by_user_id INTEGER,
                reviewed_by_user_id INTEGER,
                reviewed_at DATETIME,
                review_notes TEXT,
                PRIMARY KEY (id),

                FOREIGN KEY(reviewed_by_user_id)
                    REFERENCES users (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(created_by_user_id)
                    REFERENCES users (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE CASCADE,

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE NO ACTION
            )
            """
        )

        _execute(
            """
            INSERT INTO "_staff_availability_old" (
                id,
                staff_id,
                status,
                reason,
                created_at,
                updated_at,
                starts_at,
                ends_at,
                notes,
                all_day,
                recurring,
                recurrence_rule,
                created_by_user_id,
                reviewed_by_user_id,
                reviewed_at,
                review_notes
            )
            SELECT
                id,
                staff_id,
                status,
                reason,
                created_at,
                updated_at,
                starts_at,
                ends_at,
                notes,
                all_day,
                recurring,
                recurrence_rule,
                created_by_user_id,
                reviewed_by_user_id,
                reviewed_at,
                review_notes
            FROM staff_availability
            """
        )

        _execute("DROP TABLE staff_availability")
        _execute(
            'ALTER TABLE "_staff_availability_old" '
            'RENAME TO "staff_availability"'
        )

        _execute(
            """
            CREATE INDEX ix_staff_availability_starts_at
            ON staff_availability (starts_at)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_availability_staff_id
            ON staff_availability (staff_id)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_availability_ends_at
            ON staff_availability (ends_at)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_availability_status
            ON staff_availability (status)
            """
        )

        # --------------------------------------------------------------
        # staff_schedules
        # --------------------------------------------------------------

        _execute(
            """
            CREATE TABLE "_staff_schedules_old" (
                id INTEGER NOT NULL,
                staff_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                location VARCHAR(255),
                status VARCHAR(30) NOT NULL,
                notes TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                schedule_type VARCHAR(40) NOT NULL,
                starts_at DATETIME NOT NULL,
                ends_at DATETIME NOT NULL,
                timezone VARCHAR(64),
                task_id INTEGER,
                created_by_user_id INTEGER,
                confirmed_at DATETIME,
                started_at DATETIME,
                completed_at DATETIME,
                cancelled_at DATETIME,
                PRIMARY KEY (id),

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE CASCADE,

                FOREIGN KEY(created_by_user_id)
                    REFERENCES users (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(task_id)
                    REFERENCES tasks (id)
                    ON DELETE SET NULL,

                FOREIGN KEY(staff_id)
                    REFERENCES staff (id)
                    ON DELETE NO ACTION
            )
            """
        )

        _execute(
            """
            INSERT INTO "_staff_schedules_old" (
                id,
                staff_id,
                title,
                description,
                location,
                status,
                notes,
                created_at,
                updated_at,
                schedule_type,
                starts_at,
                ends_at,
                timezone,
                task_id,
                created_by_user_id,
                confirmed_at,
                started_at,
                completed_at,
                cancelled_at
            )
            SELECT
                id,
                staff_id,
                title,
                description,
                location,
                status,
                notes,
                created_at,
                updated_at,
                schedule_type,
                starts_at,
                ends_at,
                timezone,
                task_id,
                created_by_user_id,
                confirmed_at,
                started_at,
                completed_at,
                cancelled_at
            FROM staff_schedules
            """
        )

        _execute("DROP TABLE staff_schedules")
        _execute(
            'ALTER TABLE "_staff_schedules_old" '
            'RENAME TO "staff_schedules"'
        )

        _execute(
            """
            CREATE INDEX ix_staff_schedules_status
            ON staff_schedules (status)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_schedules_starts_at
            ON staff_schedules (starts_at)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_schedules_ends_at
            ON staff_schedules (ends_at)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_schedules_task_id
            ON staff_schedules (task_id)
            """
        )
        _execute(
            """
            CREATE INDEX ix_staff_schedules_staff_id
            ON staff_schedules (staff_id)
            """
        )

    finally:
        if foreign_keys_enabled:
            bind.exec_driver_sql("PRAGMA foreign_keys=ON")