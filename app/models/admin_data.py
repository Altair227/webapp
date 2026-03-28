from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from .admin import Admin


class AdminData(Base):
    __tablename__ = "admin_data"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="",
    )
    admin_id: Mapped[int] = mapped_column(
        ForeignKey(
            "admins.id",
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
    admin: Mapped["Admin"] = relationship(
        "Admin",
        back_populates="admin_data",
    )
