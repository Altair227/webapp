from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SafeDeleteMixin, TimestampMixin


if TYPE_CHECKING:
    from .user import User


class UserData(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "user_data"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        comment="",
    )
    firstname: Mapped[str | None] = mapped_column(
        String(100),
        comment="",
        nullable=True,
    )
    lastname: Mapped[str | None] = mapped_column(
        String(100),
        comment="",
        nullable=True,
    )
    photo_url: Mapped[str | None] = mapped_column(
        String(500),
        comment="",
        nullable=True,
    )
    birthdate: Mapped[date | None] = mapped_column(
        Date,
        comment="",
        nullable=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="data",
    )
