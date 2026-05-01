from typing import TYPE_CHECKING
from .base import Base
from datetime import date
from sqlalchemy import Integer, String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from .user import User


class UserData(Base):
    __tablename__ = "user_data"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="",
    )
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
