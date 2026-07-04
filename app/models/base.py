from datetime import datetime, UTC
from typing import Any
from sqlalchemy import Boolean, DateTime, event, func, Integer, inspect
from sqlalchemy.engine import Connection
from sqlalchemy.orm import DeclarativeBase, Mapped, Mapper, mapped_column


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
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment=""
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="",
    )


@event.listens_for(Base, "before_update", propagate=True)
def before_update(
    _mapper: Mapper[Any], _connection: Connection, target: Base
) -> None:
    target.updated_at = datetime.now(UTC)
