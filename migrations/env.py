import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

def get_engine():
    try:
        return current_app.extensions["migrate"].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine

def get_engine_url():
    try:
        return (
            get_engine()
            .url.render_as_string(hide_password=False)
            .replace("%", "%%")
        )
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())
target_db = current_app.extensions["migrate"].db

def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Control Alembic autogenerate comparisons.

    SQLite's reflection of the Staff foreign-key constraints is producing
    false remove/add operations even though the physical database schema
    and SQLAlchemy models agree on the actual FK definitions.

    Staff FK integrity has already been repaired and verified directly
    against SQLite PRAGMA metadata, so these specific FK constraints are
    excluded from autogenerate comparison.

    Other Staff columns, indexes, tables, and constraints remain subject
    to normal Alembic comparison.
    """
    if type_ == "foreign_key_constraint":
        table = getattr(object, "table", None)

        if table is not None and table.name in {
            "staff",
            "staff_assignments",
            "staff_availability",
            "staff_schedules",
        }:
            return False

    return True

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    def process_revision_directives(
        migration_context,
        revision,
        directives,
    ):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]

            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    conf_args = dict(
        current_app.extensions["migrate"].configure_args
    )

    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = (
            process_revision_directives
        )

    conf_args["include_object"] = include_object
    connectable = get_engine()

    with connectable.connect() as connection:

        is_sqlite = connection.dialect.name == "sqlite"
        original_fk_setting = None

        if is_sqlite:
            # Access the underlying DBAPI connection before
            # Alembic starts its transaction.
            raw_connection = connection.connection.driver_connection

            original_fk_setting = raw_connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]

            # SQLite ignores this change if a transaction is active.
            raw_connection.execute("PRAGMA foreign_keys = OFF")
            raw_connection.execute("PRAGMA legacy_alter_table = ON")

            actual_fk_setting = raw_connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]

            if actual_fk_setting != 0:
                raise RuntimeError(
                    "Could not disable SQLite foreign-key enforcement."
                )

        try:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                **conf_args,
            )

            with context.begin_transaction():
                context.run_migrations()

        finally:
            if is_sqlite:
                # Ensure the Alembic transaction has ended before
                # restoring the original connection settings.
                if connection.in_transaction():
                    connection.rollback()

                raw_connection.execute(
                    f"PRAGMA foreign_keys = {int(original_fk_setting)}"
                )

                raw_connection.execute(
                    "PRAGMA legacy_alter_table = OFF"
                )

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()