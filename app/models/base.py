from datetime import datetime, UTC
from typing import Any
from sqlalchemy import Boolean, DateTime, event, func
from sqlalchemy.engine import Connection
from sqlalchemy.orm import DeclarativeBase, Mapped, Mapper,mapped_column


class Base(DeclarativeBase):
    __abstract__ = True
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment=""
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment=""
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment=""
    )


@event.listens_for(Base, "before_update", propagate=True)
def before_update(_mapper:Mapper[Any], _connection:Connection, target:Base) -> None:
    target.updated_at=datetime.now(UTC)