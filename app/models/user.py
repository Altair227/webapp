from .base import Base
from typing import TYPE_CHECKING
from app.common.types import SmallIntEnum, UserType
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

if TYPE_CHECKING:
    from .user_data import UserData


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        EmailType,
        unique=True,
        nullable=False,
        comment="",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="",
    )
    is_activated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="",
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="",
    )
    type: Mapped[UserType] = mapped_column(
        SmallIntEnum(UserType),
        nullable=False,
        default=UserType.USER,
        server_default=str(UserType.USER.value),
        comment="",
    )
    data: Mapped["UserData | None"] = relationship(
        "UserData",
        back_populates="user",
        cascade="all, delete-orphan",
    )
