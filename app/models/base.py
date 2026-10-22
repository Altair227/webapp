from datetime import datetime, UTC
from typing import Any
from sqlalchemy import Boolean, DateTime, event, func, Integer, inspect
from sqlalchemy.engine import Connection
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Mapper,
    mapped_column,
    declared_attr,
)


def get_sortable_columns(model):
    return {c.key: getattr(model, c.key) for c in inspect(model).columns}


def to_dict(model, exclude=None):
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
    _mapper: Mapper[Any], _connection: Connection, target: Base
) -> None:
    target.updated_at = datetime.now(UTC)
