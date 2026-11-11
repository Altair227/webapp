from collections.abc import Collection
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, event, func, inspect
from sqlalchemy.engine import Connection
from sqlalchemy.orm import (
    DeclarativeBase,
    InstrumentedAttribute,
    Mapped,
    Mapper,
    declared_attr,
    mapped_column,
)


def get_sortable_columns(
    model: type[Base],
) -> dict[str, InstrumentedAttribute[Any]]:
    return {c.key: getattr(model, c.key) for c in inspect(model).columns}


def to_dict(
    model: Base,
    exclude: Collection[str] | None = None,
) -> dict[str, Any]:
    if not exclude:
        exclude = set()
    return {
        c.key: getattr(model, c.key)
        for c in inspect(model).mapper.column_attrs
        if c.key not in exclude
    }


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="",
    )


class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            comment="",
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            comment="",
        )


class SafeDeleteMixin:
    @declared_attr
    def is_deleted(cls) -> Mapped[bool]:
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
            comment="",
        )


@event.listens_for(TimestampMixin, "before_update", propagate=True)
def before_update(
    _mapper: Mapper[Any], _connection: Connection, target: TimestampMixin
) -> None:
    target.updated_at = datetime.now(UTC)
