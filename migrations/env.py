from typing import Any, Literal
from sqlalchemy import Table, pool, engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy_utils import EmailType
from alembic import context
from alembic.autogenerate.api import AutogenContext
from app.config import get_config
from app.models.base import Base
from app.models import (
    Admin,
    AdminData,
    EmailToken,
    News,
    SourceImage,
    User,
    UserData,
)
from app.models.relations import _r_news_source_image
from app.common.types import SmallIntEnum
from app.utils.logger import init_logger


config = context.config
app_config = get_config()
logger = init_logger(app_config.logger, name="migrations")
config.set_main_option("sqlalchemy.url", app_config.postgres.dsn)

target_metadata = Base.metadata

# comment="" is stored as NULL in Postgres; normalize so autogenerate
# doesn't emit alter_column(comment="") for every column on each run
for _table in target_metadata.tables.values():
    if _table.comment == "":
        _table.comment = None
    for _column in _table.columns:
        if _column.comment == "":
            _column.comment = None

# Only these tables are tracked by autogenerate; everything else is ignored
MIGRATED_TABLES: list[type[Base] | Table] = [
    Admin,
    AdminData,
    EmailToken,
    News,
    SourceImage,
    User,
    UserData,
    _r_news_source_image,
]
INCLUDE_TABLES: set[str] = set()
for _item in MIGRATED_TABLES:
    # association Table is used as is, ORM model -> its __tablename__
    if isinstance(_item, Table):
        INCLUDE_TABLES.add(_item.name)
    else:
        INCLUDE_TABLES.add(_item.__tablename__)


def include_object(
    obj: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object,
) -> bool:
    if type_ == "table":
        return name in INCLUDE_TABLES
    return True


def render_item(
    type_: str, obj: Any, autogen_context: AutogenContext
) -> str | Literal[False]:
    if type_ == "type" and isinstance(obj, SmallIntEnum):
        return "sa.SmallInteger()"
    if type_ == "type" and isinstance(obj, EmailType):
        length = getattr(obj.impl, "length", 255)
        return f"sa.String(length={length})"
    return False


def on_version_apply(
    ctx: object, step: Any, heads: object, run_args: object
) -> None:
    direction = "upgrade" if step.is_upgrade else "downgrade"
    source = ", ".join(step.source_revision_ids) or "<base>"
    destination = ", ".join(step.destination_revision_ids) or "<base>"
    logger.info(
        "Migration %s %s -> %s: %s",
        direction,
        source,
        destination,
        step.up_revision.doc,
    )


def run_migrations() -> None:
    try:
        with context.begin_transaction():
            context.run_migrations()
    except Exception:
        logger.exception("Migration failed")
        raise


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    print(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
        render_item=render_item,
        include_object=include_object,
        on_version_apply=on_version_apply,
    )
    run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
            include_object=include_object,
            on_version_apply=on_version_apply,
        )
        run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
