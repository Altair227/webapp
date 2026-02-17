from .base import Base
from app.common.types import SmallIntEnum, UserType
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import EmailType


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment=''
    )
    email: Mapped[str] = mapped_column(
        EmailType,
        unique=True,
        nullable=False,
        comment=''
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=''
    )
    is_activated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment=''
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment=''
    )
    type: Mapped[UserType] = mapped_column(
        SmallIntEnum(UserType),
        nullable=False,
        default=UserType.USER,
        server_default=str(UserType.USER.value),
        comment=''
    )