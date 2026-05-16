from .base import Base
from typing import TYPE_CHECKING
from app.common.types import SmallIntEnum, AdminType
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

if TYPE_CHECKING:
    from .admin_data import AdminData


class Admin(Base):
    __tablename__ = "admins"

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
    type: Mapped[AdminType] = mapped_column(
        SmallIntEnum(AdminType),
        nullable=False,
        default=AdminType.MODERATOR,
        server_default=str(AdminType.MODERATOR.value),
        comment="",
    )
    data: Mapped["AdminData | None"] = relationship(
        "AdminData",
        back_populates="admin",
        cascade="all, delete-orphan",
    )
